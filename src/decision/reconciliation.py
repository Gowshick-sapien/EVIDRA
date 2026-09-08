from __future__ import annotations

import logging
from typing import Optional
from pydantic import BaseModel, Field

# pyrefly: ignore [missing-import]
from src.decision.schemas import (
    CandidateFactView,
    HypothesisClass,
    ReconciliationProposal,
    SkepticOutcome,
    SkepticStatus,
    ValidationStatus,
    ValidatorOutcome,
)
# pyrefly: ignore [missing-import]
from src.llm.provider import ReasoningService

logger = logging.getLogger(__name__)


class SkepticResponseModel(BaseModel):
    """Pydantic model for structured adversarial skeptic evaluations."""
    status: SkepticStatus = Field(
        description="SURVIVED if explicitly supported, FALSIFIED if contradicted, UNGROUNDED if relying on unstated assumptions"
    )
    critique: str = Field(description="Adversarial evaluation explaining evidentiary gaps or confirming proof")
    citations_verified: bool = Field(description="True if all claims and numbers are directly in the excerpts")
    unstated_assumptions: list[str] = Field(default_factory=list, description="List of unstated assumptions made by the proposer")


SKEPTIC_SYSTEM_PROMPT = """You are an Adversarial Financial Skeptic in EVIDRA.
Your sole job is to ruthlessly stress-test and attempt to falsify proposed reconciliation explanations between conflicting financial figures.

Audit Rules:
1. CITATION VERIFICATION: Check whether cited excerpts actually support the claimed reconciliation.
2. UNSTATED ASSUMPTIONS: If the proposer assumes something (e.g. 'likely represents tax timing' or 'probably excluded items') without verbatim proof in the excerpts, mark UNGROUNDED.
3. CONTRADICTION: If the excerpts state the numbers should be identical or contradict the bridge, mark FALSIFIED.
4. SURVIVED: Only emit status='SURVIVED' if the reconciliation bridge and numbers are directly, unambiguously corroborated by the excerpts.
"""


class ReconciliationProposerAgent:
    """Agent that synthesizes supported validator findings into an explicit reconciliation bridge."""

    def __init__(self, reasoning_service: Optional[ReasoningService] = None):
        self.llm = reasoning_service

    @classmethod
    def propose_deterministically(
        cls,
        c1: CandidateFactView,
        c2: CandidateFactView,
        supported_validators: list[ValidatorOutcome],
    ) -> Optional[ReconciliationProposal]:
        """Synthesize candidate explanation bridge from supported specialist validator outcomes."""
        if not supported_validators:
            return None

        # Pick highest-priority supported validator
        val_types = {v.validator_type: v for v in supported_validators}

        if "RestatementValidator" in val_types:
            v = val_types["RestatementValidator"]
            diff_str = f"from {c1.normalized_value} to {c2.normalized_value}"
            return ReconciliationProposal(
                supported_hypothesis_id=v.hypothesis_id,
                explanation_type=HypothesisClass.RESTATEMENT,
                root_cause="Audit Restatement",
                reconciliation_bridge=f"Variance {diff_str} is explained by a subsequent audit restatement or amended filing.",
                arithmetic_delta=str(abs((c1.as_decimal or 0) - (c2.as_decimal or 0))),
                citations=[c1.chunk_content[:200], c2.chunk_content[:200]],
            )

        if "AccountingBasisValidator" in val_types:
            v = val_types["AccountingBasisValidator"]
            return ReconciliationProposal(
                supported_hypothesis_id=v.hypothesis_id,
                explanation_type=HypothesisClass.ACCOUNTING_BASIS,
                root_cause="Accounting Standard Discrepancy (GAAP vs Non-GAAP)",
                reconciliation_bridge=f"Reporting basis difference between {c1.accounting_basis or 'Standard'} and {c2.accounting_basis or 'Adjusted'}.",
                arithmetic_delta=str(abs((c1.as_decimal or 0) - (c2.as_decimal or 0))),
                citations=[c1.chunk_content[:200], c2.chunk_content[:200]],
            )

        if "ScopeValidator" in val_types:
            v = val_types["ScopeValidator"]
            return ReconciliationProposal(
                supported_hypothesis_id=v.hypothesis_id,
                explanation_type=HypothesisClass.SCOPE_MISMATCH,
                root_cause="Organizational Scope Difference",
                reconciliation_bridge=f"Entity scope variance between {c1.organizational_scope or 'Standalone'} parent and {c2.organizational_scope or 'Consolidated'} group.",
                arithmetic_delta=str(abs((c1.as_decimal or 0) - (c2.as_decimal or 0))),
                citations=[c1.chunk_content[:200], c2.chunk_content[:200]],
            )

        if "TimingValidator" in val_types:
            v = val_types["TimingValidator"]
            return ReconciliationProposal(
                supported_hypothesis_id=v.hypothesis_id,
                explanation_type=HypothesisClass.TIMING_DIFFERENCE,
                root_cause="Temporal Scope Variance",
                reconciliation_bridge=f"Reporting periods differ: [{c1.period_start} to {c1.period_end}] vs [{c2.period_start} to {c2.period_end}].",
                arithmetic_delta=str(abs((c1.as_decimal or 0) - (c2.as_decimal or 0))),
                citations=[c1.chunk_content[:200], c2.chunk_content[:200]],
            )

        return None


class AdversarialSkepticAgent:
    """Agent that subjects proposed reconciliations to rigorous adversarial falsification."""

    def __init__(self, reasoning_service: Optional[ReasoningService] = None):
        self.llm = reasoning_service

    @classmethod
    def critique_deterministically(
        cls,
        c1: CandidateFactView,
        c2: CandidateFactView,
        proposal: Optional[ReconciliationProposal],
    ) -> SkepticOutcome:
        """Evaluate proposal against citations and context deterministically."""
        if not proposal:
            return SkepticOutcome(
                status=SkepticStatus.FALSIFIED,
                critique="No viable reconciliation hypothesis was supported by evidence.",
                citations_verified=False,
            )

        # Restatement verification
        if proposal.explanation_type == HypothesisClass.RESTATEMENT:
            rest_confirmed = (
                (c1.version_status == "RESTATED" or c2.version_status == "RESTATED")
                or ("restated" in (c1.chunk_content or "").lower() or "restated" in (c2.chunk_content or "").lower())
            )
            if rest_confirmed:
                return SkepticOutcome(
                    status=SkepticStatus.SURVIVED,
                    critique="Restatement disclosure is explicitly confirmed in source documents.",
                    citations_verified=True,
                )
            return SkepticOutcome(
                status=SkepticStatus.UNGROUNDED,
                critique="Restatement assumed without explicit 'restated' or 'amended' disclosures in evidence chunks.",
                citations_verified=False,
                unstated_assumptions=["Assumed unannounced revision"],
            )

        # Scope mismatch verification
        if proposal.explanation_type == HypothesisClass.SCOPE_MISMATCH:
            sc1 = (c1.organizational_scope or "").upper()
            sc2 = (c2.organizational_scope or "").upper()
            if sc1 and sc2 and sc1 != sc2:
                return SkepticOutcome(
                    status=SkepticStatus.SURVIVED,
                    critique=f"Entity scope difference explicitly verified: {sc1} vs {sc2}.",
                    citations_verified=True,
                )
            return SkepticOutcome(
                status=SkepticStatus.UNGROUNDED,
                critique="Scope difference assumed but both candidates lack clear standalone vs consolidated labels.",
                citations_verified=False,
            )

        # Accounting basis verification
        if proposal.explanation_type == HypothesisClass.ACCOUNTING_BASIS:
            b1 = (c1.accounting_basis or "").upper()
            b2 = (c2.accounting_basis or "").upper()
            if b1 and b2 and b1 != b2:
                return SkepticOutcome(
                    status=SkepticStatus.SURVIVED,
                    critique=f"Accounting standard variance explicitly verified: {b1} vs {b2}.",
                    citations_verified=True,
                )
            return SkepticOutcome(
                status=SkepticStatus.UNGROUNDED,
                critique="Accounting basis variance asserted without clear Non-GAAP reconciliation table in evidence.",
                citations_verified=False,
            )

        # Timing difference verification
        if proposal.explanation_type == HypothesisClass.TIMING_DIFFERENCE:
            p1 = (c1.period_start, c1.period_end)
            p2 = (c2.period_start, c2.period_end)
            if p1 != p2:
                return SkepticOutcome(
                    status=SkepticStatus.SURVIVED,
                    critique=f"Reporting periods confirmed to diverge: {p1} vs {p2}.",
                    citations_verified=True,
                )

        return SkepticOutcome(
            status=SkepticStatus.UNGROUNDED,
            critique="Reconciliation bridge lacks explicit grounding in source text.",
            citations_verified=False,
        )

    def critique(
        self,
        c1: CandidateFactView,
        c2: CandidateFactView,
        proposal: Optional[ReconciliationProposal],
    ) -> SkepticOutcome:
        """Execute adversarial critique, falling back to deterministic checks if LLM is unavailable."""
        if not proposal:
            return SkepticOutcome(
                status=SkepticStatus.FALSIFIED,
                critique="No reconciliation proposal submitted to critique.",
                citations_verified=False,
            )

        if not self.llm:
            return self.critique_deterministically(c1, c2, proposal)

        prompt = f"""Evaluate this proposed financial reconciliation:

PROPOSED RECONCILIATION:
- Root Cause: {proposal.root_cause}
- Explanation Bridge: {proposal.reconciliation_bridge}
- Arithmetic Delta: {proposal.arithmetic_delta}

SOURCE EVIDENCE CHUNKS:
Chunk 1: {c1.chunk_content[:600]}
Chunk 2: {c2.chunk_content[:600]}

Verify whether the proposed reconciliation is directly substantiated by the text, or if it relies on unstated assumptions.
"""
        try:
            resp = self.llm.generate_structured(
                prompt=prompt,
                response_model=SkepticResponseModel,
                system_prompt=SKEPTIC_SYSTEM_PROMPT,
            )
            if resp:
                return SkepticOutcome(
                    status=resp.status,
                    critique=resp.critique,
                    citations_verified=resp.citations_verified,
                    unstated_assumptions=resp.unstated_assumptions,
                )
        except Exception as e:
            logger.warning(f"Adversarial skeptic LLM call failed ({e}); falling back to deterministic critique.")

        return self.critique_deterministically(c1, c2, proposal)
