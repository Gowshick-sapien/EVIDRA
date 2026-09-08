from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Optional

# pyrefly: ignore [missing-import]
from src.decision.schemas import (
    CandidateFactView,
    DecisionStrength,
    FactDecisionState,
    ReconciliationProposal,
    SkepticOutcome,
    SkepticStatus,
    ValidationStatus,
    ValidatorOutcome,
    Verdict,
)

logger = logging.getLogger(__name__)


class DecisionPolicy:
    """Pure Python deterministic decision truth table engine.
    Zero LLM calls are made at the verdict gate.
    """
    TOLERANCE = Decimal("0.0001")  # 0.01%

    @classmethod
    def evaluate(
        cls,
        candidates: list[CandidateFactView],
        validator_results: list[ValidatorOutcome],
        reconciliation_proposal: Optional[ReconciliationProposal],
        skeptic_outcome: Optional[SkepticOutcome],
        arithmetic_equal: bool = False,
        matching_context: bool = True,
    ) -> tuple[Verdict, DecisionStrength, str]:
        """Apply deterministic decision rules to evaluate final fact group verdict."""
        # Edge Case: Single fact candidate
        if len(candidates) <= 1:
            return (
                Verdict.UNRESOLVED,
                DecisionStrength.LOW,
                "Single fact candidate observed; awaiting independent second source for corroboration.",
            )

        # Rule 1: Corroboration (Path A)
        if arithmetic_equal and matching_context:
            return (
                Verdict.CORROBORATED,
                DecisionStrength.HIGH,
                "Values corroborate within 0.01% tolerance under identical entity, period, and scope.",
            )

        # Rule 2: Reconciled (Path B & Path C)
        supported_validators = [v for v in validator_results if v.outcome == ValidationStatus.SUPPORTED]
        if (
            skeptic_outcome
            and skeptic_outcome.status == SkepticStatus.SURVIVED
            and supported_validators
            and reconciliation_proposal
        ):
            has_math_bridge = bool(reconciliation_proposal.arithmetic_delta)
            strength = DecisionStrength.HIGH if has_math_bridge else DecisionStrength.MEDIUM
            return (
                Verdict.RECONCILED,
                strength,
                f"Reconciled: {reconciliation_proposal.reconciliation_bridge}",
            )

        # Rule 3: Genuine Contradiction (Path C)
        # Numerical variance under matching context, and skeptic falsified or all hypotheses refuted
        all_refuted = (
            validator_results
            and all(v.outcome in (ValidationStatus.REFUTED, ValidationStatus.INCONCLUSIVE) for v in validator_results)
            and not supported_validators
        )
        is_skeptic_falsified = bool(skeptic_outcome and skeptic_outcome.status == SkepticStatus.FALSIFIED)

        if matching_context and not arithmetic_equal and (all_refuted or is_skeptic_falsified):
            return (
                Verdict.CONTRADICTION,
                DecisionStrength.HIGH,
                "Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.",
            )

        # Rule 4: Defensive Fallback (UNRESOLVED)
        if skeptic_outcome and skeptic_outcome.status == SkepticStatus.UNGROUNDED:
            return (
                Verdict.UNRESOLVED,
                DecisionStrength.LOW,
                f"Reconciliation relies on ungrounded assumptions: {skeptic_outcome.critique}",
            )

        return (
            Verdict.UNRESOLVED,
            DecisionStrength.INSUFFICIENT,
            "Insufficient evidence or ambiguous reporting context prevented definitive reconciliation.",
        )
