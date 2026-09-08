from __future__ import annotations

import logging
from typing import Any, Optional

# pyrefly: ignore [missing-import]
from src.decision.schemas import (
    CandidateFactView,
    EvidenceSufficiencyResult,
    SufficiencyAction,
    SufficiencyStatus,
)

logger = logging.getLogger(__name__)

GENERIC_ENTITIES = {
    "reporting entity",
    "the company",
    "company",
    "management",
    "total",
    "consolidated",
    "standalone",
    "unknown",
    "none",
    "",
}


class EvidenceSufficiencyGate:
    """Deterministic categorical rule gate evaluating evidence readiness before tournament dispatch.
    
    Eliminates arbitrary decimal scoring formulas and routes fact groups categorically to:
    - ADJUDICATE (Standard pairwise tournament)
    - RECONCILE_CONTEXT (Path B contextual reconciliation)
    - DEFER (Evidence Gap Engine / second source pending)
    - SKIP (Fast-path UNRESOLVED)
    """

    @classmethod
    def evaluate(
        cls,
        candidates: list[CandidateFactView],
        group_metadata: Optional[dict[str, Any]] = None,
        identities: Optional[dict[str, Any]] = None,
    ) -> EvidenceSufficiencyResult:
        """Categorically evaluate evidence sufficiency across candidates and identity signatures."""
        meta = dict(group_metadata) if group_metadata is not None else {}
        num_candidates = len(candidates)

        # Stage 1: Candidate Count & Multiplicity Check
        if num_candidates == 0:
            return EvidenceSufficiencyResult(
                status=SufficiencyStatus.INSUFFICIENT_IDENTITY,
                action=SufficiencyAction.SKIP,
                reason="No candidate facts provided for fact group adjudication.",
                missing_dimensions=["candidates"],
                details={"candidate_count": 0},
            )

        if num_candidates == 1:
            c = candidates[0]
            val_display = f"{c.normalized_value} {c.normalized_unit}".strip()
            return EvidenceSufficiencyResult(
                status=SufficiencyStatus.SINGLE_SOURCE_PENDING,
                action=SufficiencyAction.DEFER,
                reason=(
                    f"Single source claim ({val_display}) observed; "
                    "awaiting independent second source for corroboration."
                ),
                missing_dimensions=["second_source"],
                details={"candidate_count": 1, "fact_id": c.fact_id, "document_id": c.document_id},
            )

        # Stage 2: Identity Completeness Check
        missing_dims: list[str] = []
        for c in candidates:
            # Check for generic or missing entity
            ent = (meta.get("entity") or c.document_id or "").strip().lower()
            if ent in GENERIC_ENTITIES:
                if "entity" not in missing_dims:
                    missing_dims.append("entity")

            # Check for missing attribute / metric family
            attr = (meta.get("attribute") or meta.get("metric_family") or "").strip()
            if not attr:
                if "metric" not in missing_dims:
                    missing_dims.append("metric")

            # Check for missing value
            if not c.normalized_value and not c.raw_value:
                if "value" not in missing_dims:
                    missing_dims.append("value")

            # Check for temporal boundaries
            start = c.period_start or meta.get("period_start") or ""
            end = c.period_end or meta.get("period_end") or ""
            if not start or not end or (start == "1970-01-01" and end == "1970-01-01" and not meta.get("period_id")):
                if "period" not in missing_dims:
                    missing_dims.append("period")

        if missing_dims:
            return EvidenceSufficiencyResult(
                status=SufficiencyStatus.INSUFFICIENT_IDENTITY,
                action=SufficiencyAction.SKIP,
                reason=f"Fact group contains incomplete identity specifications: missing {', '.join(missing_dims)}.",
                missing_dimensions=missing_dims,
                details={"missing_dimensions": missing_dims},
            )

        # Stage 3: Grounding & Entailment Verification Check
        unverified_facts: list[str] = []
        for c in candidates:
            # Ensure fact has verifiable textual grounding or coordinates
            if not c.chunk_content and not c.bounding_box and not c.statement:
                unverified_facts.append(c.fact_id)

        if unverified_facts:
            return EvidenceSufficiencyResult(
                status=SufficiencyStatus.UNVERIFIED_EVIDENCE,
                action=SufficiencyAction.SKIP,
                reason=f"Candidate observations failed provenance grounding: facts {unverified_facts} lack evidence chunks.",
                missing_dimensions=["evidence_grounding"],
                details={"unverified_facts": unverified_facts},
            )

        # Stage 4: Context Compatibility Check (Scope & Accounting Basis)
        scopes = set()
        bases = set()
        for c in candidates:
            if c.organizational_scope:
                scopes.add(c.organizational_scope.strip().upper())
            if c.accounting_basis:
                bases.add(c.accounting_basis.strip().upper())

        scope_divergent = len(scopes) > 1 and bool("CONSOLIDATED" in scopes and "STANDALONE" in scopes)
        basis_divergent = len(bases) > 1 and bool("IND_AS" in bases or "GAAP" in bases) and "NON_GAAP" in bases
        group_type_context = meta.get("group_type") == "CONTEXTUAL_RECONCILIATION"

        if scope_divergent or basis_divergent or group_type_context:
            reasons = []
            if scope_divergent:
                reasons.append(f"scope divergence ({', '.join(sorted(scopes))})")
            if basis_divergent:
                reasons.append(f"accounting basis divergence ({', '.join(sorted(bases))})")
            if group_type_context:
                reasons.append("tagged contextual reconciliation group")

            reason_str = "; ".join(reasons)
            return EvidenceSufficiencyResult(
                status=SufficiencyStatus.CONTEXT_DIVERGENT,
                action=SufficiencyAction.RECONCILE_CONTEXT,
                reason=f"Contextual divergence detected: {reason_str}; routing to contextual reconciliation tournament.",
                missing_dimensions=[],
                details={
                    "scopes": sorted(list(scopes)),
                    "bases": sorted(list(bases)),
                    "scope_divergent": scope_divergent,
                    "basis_divergent": basis_divergent,
                },
            )

        # Stage 5: Full Adjudication Readiness
        unique_docs = {c.document_id for c in candidates if c.document_id}
        return EvidenceSufficiencyResult(
            status=SufficiencyStatus.SUFFICIENT_FOR_ADJUDICATION,
            action=SufficiencyAction.ADJUDICATE,
            reason=(
                f"Sufficient evidence established across {num_candidates} candidate claims "
                f"from {len(unique_docs)} document sources for adjudication tournament."
            ),
            missing_dimensions=[],
            details={
                "candidate_count": num_candidates,
                "document_count": len(unique_docs),
            },
        )
