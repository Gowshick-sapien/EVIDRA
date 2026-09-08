from __future__ import annotations

import logging
import uuid
from typing import Optional
from pydantic import BaseModel, Field

# pyrefly: ignore [missing-import]
from src.decision.schemas import (
    CandidateFactView,
    HypothesisClass,
    HypothesisProposal,
)
# pyrefly: ignore [missing-import]
from src.llm.provider import ReasoningService

logger = logging.getLogger(__name__)


class HypothesisListModel(BaseModel):
    """Container model for structured LLM hypothesis generation."""
    hypotheses: list[HypothesisProposal] = Field(
        description="List of distinct, falsifiable financial variance hypotheses"
    )


HYPOTHESIS_SYSTEM_PROMPT = """You are an expert forensic financial analyst in EVIDRA.
Your task is to formulate distinct, testable hypotheses explaining why two reported figures for the same financial metric differ.

You must categorize each hypothesis into one of 5 strict classes:
1. RESTATEMENT: Difference caused by an audit restatement, revision, or retrospective adjustment.
2. ACCOUNTING_BASIS: Difference caused by GAAP vs Non-GAAP, Ind AS / IFRS, or EBITDA exclusions.
3. SCOPE_MISMATCH: Difference caused by Consolidated Group vs Standalone legal entity figures.
4. TIMING_DIFFERENCE: Difference caused by differing fiscal period lengths or calendar quarter vs custom fiscal cycles.
5. ERRONEOUS_CONTRADICTION: Genuine irreconcilable error or conflicting reporting without explanatory basis.

Rules:
- Generate 2 to 4 concrete, testable hypotheses based on the provided candidates and evidence chunks.
- Assign a realistic likelihood_score (0.0 to 1.0) based strictly on available evidence.
"""


class HypothesisGeneratorAgent:
    """Agent that formulates structured, falsifiable hypotheses for financial variance."""

    def __init__(self, reasoning_service: Optional[ReasoningService] = None):
        self.llm = reasoning_service

    @classmethod
    def generate_deterministically(
        cls,
        c1: CandidateFactView,
        c2: CandidateFactView,
    ) -> list[HypothesisProposal]:
        """Formulate candidate hypotheses based on deterministic context indicators."""
        hypotheses: list[HypothesisProposal] = []

        # 1. Restatement Check
        s1_rest = c1.version_status == "RESTATED"
        s2_rest = c2.version_status == "RESTATED"
        if s1_rest != s2_rest:
            hypotheses.append(
                HypothesisProposal(
                    hypothesis_id=f"HYP-REST-{uuid.uuid4().hex[:6]}",
                    explanation_type=HypothesisClass.RESTATEMENT,
                    description="Variance explained by audit restatement or amended filing revision between reporting periods.",
                    likelihood_score=0.85,
                )
            )

        # 2. Accounting Basis Check
        b1 = (c1.accounting_basis or "").upper()
        b2 = (c2.accounting_basis or "").upper()
        if (b1 and b2 and b1 != b2) or ("NON_GAAP" in (b1, b2)):
            hypotheses.append(
                HypothesisProposal(
                    hypothesis_id=f"HYP-BASIS-{uuid.uuid4().hex[:6]}",
                    explanation_type=HypothesisClass.ACCOUNTING_BASIS,
                    description=f"Variance arises from differing accounting standards ({b1 or 'GAAP'} vs {b2 or 'Non-GAAP'}).",
                    likelihood_score=0.80,
                )
            )

        # 3. Scope Mismatch Check
        sc1 = (c1.organizational_scope or "").upper()
        sc2 = (c2.organizational_scope or "").upper()
        if sc1 and sc2 and sc1 != sc2:
            hypotheses.append(
                HypothesisProposal(
                    hypothesis_id=f"HYP-SCOPE-{uuid.uuid4().hex[:6]}",
                    explanation_type=HypothesisClass.SCOPE_MISMATCH,
                    description=f"Variance stems from entity scope variation ({sc1} parent entity vs {sc2} group figures).",
                    likelihood_score=0.80,
                )
            )

        # 4. Timing Difference Check
        p1 = (c1.period_start, c1.period_end)
        p2 = (c2.period_start, c2.period_end)
        if p1 != p2 and p1 != ("1970-01-01", "1970-01-01") and p2 != ("1970-01-01", "1970-01-01"):
            hypotheses.append(
                HypothesisProposal(
                    hypothesis_id=f"HYP-TIME-{uuid.uuid4().hex[:6]}",
                    explanation_type=HypothesisClass.TIMING_DIFFERENCE,
                    description=f"Variance is attributable to divergent reporting periods ({p1[0]} to {p1[1]} vs {p2[0]} to {p2[1]}).",
                    likelihood_score=0.75,
                )
            )

        # 5. Always include baseline Contradiction hypothesis
        hypotheses.append(
            HypothesisProposal(
                hypothesis_id=f"HYP-CONTRA-{uuid.uuid4().hex[:6]}",
                explanation_type=HypothesisClass.ERRONEOUS_CONTRADICTION,
                description="Figures represent mutually incompatible claims with no valid accounting reconciliation.",
                likelihood_score=0.50 if hypotheses else 0.75,
            )
        )

        return hypotheses

    def generate_hypotheses(
        self,
        c1: CandidateFactView,
        c2: CandidateFactView,
    ) -> list[HypothesisProposal]:
        """Generate hypotheses using deterministic heuristics, optionally augmented by LLM."""
        deterministic = self.generate_deterministically(c1, c2)

        # If deterministic rules already identified strong explanatory hypotheses, return them
        if len(deterministic) > 1 or not self.llm:
            return deterministic

        prompt = f"""Evaluate the variance between these two financial observations:

Claim 1:
- Statement: {c1.statement}
- Normalized Value: {c1.normalized_value} {c1.normalized_unit} {c1.normalized_currency}
- Context: Scope={c1.organizational_scope}, Basis={c1.accounting_basis}, Version={c1.version_status}
- Chunk Excerpt: {c1.chunk_content[:500]}

Claim 2:
- Statement: {c2.statement}
- Normalized Value: {c2.normalized_value} {c2.normalized_unit} {c2.normalized_currency}
- Context: Scope={c2.organizational_scope}, Basis={c2.accounting_basis}, Version={c2.version_status}
- Chunk Excerpt: {c2.chunk_content[:500]}

Formulate the most plausible financial variance hypotheses explaining the discrepancy.
"""
        try:
            result = self.llm.generate_structured(
                prompt=prompt,
                response_model=HypothesisListModel,
                system_prompt=HYPOTHESIS_SYSTEM_PROMPT,
            )
            if result and result.hypotheses:
                return result.hypotheses
        except Exception as e:
            logger.warning(f"LLM hypothesis generation failed ({e}); falling back to deterministic hypotheses.")

        return deterministic
