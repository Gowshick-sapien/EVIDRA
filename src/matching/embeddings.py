from __future__ import annotations

import logging
import uuid
from typing import Any, Optional
import numpy as np

# pyrefly: ignore [missing-import]
from src.db.ledger import FactGroupRecord

import re

logger = logging.getLogger(__name__)


def normalize_entity_name(entity: str) -> str:
    """Standardize corporate entity names for blocking."""
    raw = str(entity or "").strip().lower()
    if not raw or raw in ("reporting entity", "the company", "company", "management"):
        return "reporting entity"
    # Strip punctuation
    raw = re.sub(r"[^\w\s]", " ", raw)
    # Strip legal entity suffixes
    raw = re.sub(r"\b(limited|ltd|inc|incorporated|corp|corporation|company|co|llc|holdings|group)\b", "", raw)
    raw = " ".join(raw.split())
    return raw or "reporting entity"


class FactGroupEngine:
    """Two-tier candidate fact grouping engine combining hard blocking and soft embedding similarity."""

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
    ) -> list[tuple[FactGroupRecord, list[str]]]:
        """Group normalized fact candidates into dispute clusters.
        
        Returns:
            List of tuples: (FactGroupRecord, [fact_id_1, fact_id_2, ...])
        """
        if not candidates:
            return []

        # 1. Tier 1: Hard Blocking on normalized entity and temporal interval
        partitions: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        for c in candidates:
            entity_norm = normalize_entity_name(c.get("entity", ""))
            p_start = str(c.get("period_start", ""))
            p_end = str(c.get("period_end", ""))
            key = (entity_norm, p_start, p_end)
            partitions.setdefault(key, []).append(c)

        grouped_results: list[tuple[FactGroupRecord, list[str]]] = []

        # 2. Tier 2: Soft Semantic Matching within each hard block
        for (entity_key, p_start, p_end), partition in partitions.items():
            if len(partition) == 1:
                cand = partition[0]
                group_id = f"GRP-{uuid.uuid4().hex[:8]}"
                period_id = f"{p_start}_{p_end}" if p_start != "1970-01-01" else "Undated"
                group_record = FactGroupRecord(
                    group_id=group_id,
                    entity=cand.get("entity", "Reporting Entity"),
                    attribute=cand.get("attribute", "General Metric"),
                    period_id=period_id,
                    member_count=1,
                )
                grouped_results.append((group_record, [cand["fact_id"]]))
                continue

            # Multi-candidate partition: Compute attribute embeddings
            attributes = [c.get("attribute", "") for c in partition]
            try:
                embeddings = self.model.encode(attributes, convert_to_numpy=True)
            except Exception as e:
                logger.warning(f"Embedding generation failed: {e}. Falling back to single groups.")
                for cand in partition:
                    group_id = f"GRP-{uuid.uuid4().hex[:8]}"
                    period_id = f"{p_start}_{p_end}" if p_start != "1970-01-01" else "Undated"
                    group_record = FactGroupRecord(
                        group_id=group_id,
                        entity=cand.get("entity", "Reporting Entity"),
                        attribute=cand.get("attribute", "General Metric"),
                        period_id=period_id,
                        member_count=1,
                    )
                    grouped_results.append((group_record, [cand["fact_id"]]))
                continue

            # Build adjacency graph where similarity >= threshold
            num_items = len(partition)
            visited = [False] * num_items

            for i in range(num_items):
                if visited[i]:
                    continue

                cluster_indices = [i]
                visited[i] = True

                for j in range(i + 1, num_items):
                    if not visited[j]:
                        sim = self._cosine_similarity(embeddings[i], embeddings[j])
                        if sim >= self.similarity_threshold:
                            cluster_indices.append(j)
                            visited[j] = True

                cluster_facts = [partition[idx] for idx in cluster_indices]
                fact_ids = [c["fact_id"] for c in cluster_facts]
                primary_cand = cluster_facts[0]

                group_id = f"GRP-{uuid.uuid4().hex[:8]}"
                period_id = f"{p_start}_{p_end}" if p_start != "1970-01-01" else "Undated"
                group_record = FactGroupRecord(
                    group_id=group_id,
                    entity=primary_cand.get("entity", "Reporting Entity"),
                    attribute=primary_cand.get("attribute", "General Metric"),
                    period_id=period_id,
                    member_count=len(fact_ids),
                )
                grouped_results.append((group_record, fact_ids))

        return grouped_results
