"""
4-Gate Contextual Fact Resolution Engine for EVIDRA 2.0 (Phase P1, Gate 1-4).

Replaces unconstrained single-pass cosine clustering with a disciplined 4-gate
verification sequence:
  Gate 1: Canonical Entity Grounding
  Gate 2: Temporal Comparability Classification
  Gate 3: Metric Family & Measurement Semantics Compatibility
  Gate 4: Context Compatibility (Scope & Accounting Basis)
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Optional
import numpy as np

# pyrefly: ignore [missing-import]
from src.db.ledger import FactGroupRecord
# pyrefly: ignore [missing-import]
from src.matching.identity import (
    FactIdentityBuilder,
    FactIdentitySignature,
    MeasurementClassifier,
    MeasurementType,
    normalize_canonical_entity,
)
# pyrefly: ignore [missing-import]
from src.matching.temporal import (
    ComparabilityAction,
    TemporalComparabilityClassifier,
    TemporalRelation,
)

logger = logging.getLogger(__name__)


def normalize_entity_name(entity: str) -> str:
    """Standardize corporate entity names for blocking."""
    return normalize_canonical_entity(entity)


class ContextualFactGroupEngine:
    """
    4-Gate candidate fact grouping engine combining structural signatures
    with semantic embedding fallback.
    """

    def __init__(
        self,
        embedding_model_name: str = "BAAI/bge-small-en-v1.5",
        similarity_threshold: float = 0.82,
    ):
        self.model_name = embedding_model_name
        self.similarity_threshold = similarity_threshold
        self._model = None

    @property
    def model(self):
        """Lazy load local sentence transformer embedding model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model

    @staticmethod
    def _cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(v1, v2) / (norm1 * norm2))

    def group_candidates(
        self,
        candidates: list[dict[str, Any]],
        signatures: Optional[dict[str, FactIdentitySignature]] = None,
    ) -> list[tuple[FactGroupRecord, list[str]]]:
        """
        Group normalized fact candidates into dispute clusters using 4 disciplined gates.
        
        Returns:
            List of tuples: (FactGroupRecord, [fact_id_1, fact_id_2, ...])
        """
        if not candidates:
            return []

        # Ensure signatures are available for every candidate
        active_sigs: dict[str, FactIdentitySignature] = {}
        if signatures:
            active_sigs.update(signatures)

        for c in candidates:
            fid = c["fact_id"]
            if fid not in active_sigs:
                obs_proxy = {
                    "entity": c.get("entity", ""),
                    "attribute": c.get("attribute", ""),
                    "raw_value": c.get("raw_value", ""),
                    "unit": c.get("normalized_unit", ""),
                    "statement": c.get("statement", ""),
                }
                active_sigs[fid] = FactIdentityBuilder.build(
                    fact_id=fid,
                    observation=obs_proxy,
                    period_start=str(c.get("period_start", "1970-01-01")),
                    period_end=str(c.get("period_end", "1970-01-01")),
                )

        # ---------------------------------------------------------------------
        # GATE 1: Canonical Entity Grounding
        # ---------------------------------------------------------------------
        entity_partitions: dict[str, list[dict[str, Any]]] = {}
        for c in candidates:
            sig = active_sigs[c["fact_id"]]
            e_key = sig.entity_canonical.lower().strip()
            entity_partitions.setdefault(e_key, []).append(c)

        grouped_results: list[tuple[FactGroupRecord, list[str]]] = []

        for entity_canonical, entity_members in entity_partitions.items():
            # -----------------------------------------------------------------
            # GATE 3A: Measurement Semantics & Metric Family Blocking
            # Block mixing ABSOLUTE_VALUE with RATE_OF_CHANGE or PERCENTAGE
            # -----------------------------------------------------------------
            family_partitions: dict[tuple[str, str], list[dict[str, Any]]] = {}
            for m in entity_members:
                sig = active_sigs[m["fact_id"]]
                m_type = sig.measurement_type.value
                m_fam = sig.metric_family
                family_partitions.setdefault((m_type, m_fam), []).append(m)

            for (m_type, m_fam), fam_members in family_partitions.items():
                # -------------------------------------------------------------
                # GATE 2: Temporal Comparability Clustering
                # Separate DIRECTLY_COMPARABLE from CONTEXTUALLY_RELATED/NON_COMP
                # -------------------------------------------------------------
                temporal_partitions: dict[tuple[str, str], list[dict[str, Any]]] = {}
                for m in fam_members:
                    sig = active_sigs[m["fact_id"]]
                    p_start = sig.period_start
                    p_end = sig.period_end
                    temporal_partitions.setdefault((p_start, p_end), []).append(m)

                # Process each exact temporal interval
                for (p_start, p_end), temp_members in temporal_partitions.items():
                    period_id = f"{p_start}_{p_end}" if p_start != "1970-01-01" else "Undated"

                    if len(temp_members) == 1:
                        cand = temp_members[0]
                        sig = active_sigs[cand["fact_id"]]
                        group_id = f"GRP-{uuid.uuid4().hex[:8]}"
                        group_record = FactGroupRecord(
                            group_id=group_id,
                            entity=sig.entity_canonical,
                            attribute=sig.metric_subtype or cand.get("attribute", "General Metric"),
                            period_id=period_id,
                            member_count=1,
                            metric_family=m_fam,
                            metric_subtype=sig.metric_subtype,
                            measurement_type=m_type,
                            group_type="DIRECT_COMPARISON",
                        )
                        grouped_results.append((group_record, [cand["fact_id"]]))
                        continue

                    # ---------------------------------------------------------
                    # GATE 3B: Metric Subtype & Surface Semantic Embedding Matching
                    # ---------------------------------------------------------
                    num_items = len(temp_members)
                    visited = [False] * num_items

                    attributes = [
                        active_sigs[m["fact_id"]].surface_metric or m.get("attribute", "")
                        for m in temp_members
                    ]
                    embeddings = None
                    try:
                        embeddings = self.model.encode(attributes, convert_to_numpy=True)
                    except Exception as e:
                        logger.warning(f"Embedding encoding failed: {e}")

                    for i in range(num_items):
                        if visited[i]:
                            continue

                        cluster_indices = [i]
                        visited[i] = True
                        sig_i = active_sigs[temp_members[i]["fact_id"]]

                        for j in range(i + 1, num_items):
                            if not visited[j]:
                                sig_j = active_sigs[temp_members[j]["fact_id"]]
                                # 1. Exact subtype key match
                                if (
                                    sig_i.metric_subtype
                                    and sig_j.metric_subtype
                                    and sig_i.metric_subtype == sig_j.metric_subtype
                                ):
                                    cluster_indices.append(j)
                                    visited[j] = True
                                # 2. Semantic embedding fallback ONLY when subtype is unassigned or generic
                                elif (
                                    (not sig_i.metric_subtype or sig_i.metric_subtype == "GENERAL_METRIC"
                                     or not sig_j.metric_subtype or sig_j.metric_subtype == "GENERAL_METRIC")
                                    and embeddings is not None
                                ):
                                    sim = self._cosine_similarity(embeddings[i], embeddings[j])
                                    if sim >= self.similarity_threshold:
                                        cluster_indices.append(j)
                                        visited[j] = True

                        sub_members = [temp_members[idx] for idx in cluster_indices]
                        primary_sig = active_sigs[sub_members[0]["fact_id"]]
                        subtype_key = primary_sig.metric_subtype or "GENERAL_METRIC"

                        # -----------------------------------------------------
                        # GATE 4: Context Compatibility Check (Scope & Basis)
                        # -----------------------------------------------------
                        scopes = {active_sigs[m["fact_id"]].scope for m in sub_members}
                        bases = {active_sigs[m["fact_id"]].basis for m in sub_members}

                        has_scope_divergence = len(scopes - {"UNKNOWN"}) > 1
                        has_basis_divergence = len(bases - {"UNKNOWN"}) > 1

                        group_type = (
                            "CONTEXTUAL_COMPARISON"
                            if (has_scope_divergence or has_basis_divergence)
                            else "DIRECT_COMPARISON"
                        )

                        fact_ids = [m["fact_id"] for m in sub_members]

                        group_id = f"GRP-{uuid.uuid4().hex[:8]}"
                        group_record = FactGroupRecord(
                            group_id=group_id,
                            entity=primary_sig.entity_canonical,
                            attribute=subtype_key,
                            period_id=period_id,
                            member_count=len(fact_ids),
                            metric_family=m_fam,
                            metric_subtype=subtype_key,
                            measurement_type=m_type,
                            group_type=group_type,
                        )
                        grouped_results.append((group_record, fact_ids))

        return grouped_results


# Aliased for 100% backwards compatibility with existing pipeline references
FactGroupEngine = ContextualFactGroupEngine
