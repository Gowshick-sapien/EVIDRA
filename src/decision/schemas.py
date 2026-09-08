from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Any, Optional, TypedDict
from pydantic import BaseModel, Field


class Verdict(str, Enum):
    """Categorical epistemic verdicts for fact group relationships."""
    CORROBORATED = "CORROBORATED"
    CONTRADICTION = "CONTRADICTION"
    RECONCILED = "RECONCILED"
    UNRESOLVED = "UNRESOLVED"


class DecisionStrength(str, Enum):
    """Categorical confidence ratings reflecting evidentiary completeness."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT = "INSUFFICIENT"


class HypothesisClass(str, Enum):
    """Variance classification categories for hypothesis tournaments."""
    RESTATEMENT = "RESTATEMENT"
    ACCOUNTING_BASIS = "ACCOUNTING_BASIS"
    SCOPE_MISMATCH = "SCOPE_MISMATCH"
    TIMING_DIFFERENCE = "TIMING_DIFFERENCE"
    ERRONEOUS_CONTRADICTION = "ERRONEOUS_CONTRADICTION"


class ValidationStatus(str, Enum):
    """Outcome status for specialist validator evaluations."""
    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"
    INCONCLUSIVE = "INCONCLUSIVE"


class SkepticStatus(str, Enum):
    """Verdict of adversarial skeptic critique."""
    SURVIVED = "SURVIVED"
    FALSIFIED = "FALSIFIED"
    UNGROUNDED = "UNGROUNDED"


class CandidateFactView(BaseModel):
    """Projected candidate fact enriched with provenance, context, and exact decimal value."""
    fact_id: str
    observation_id: str
    document_id: str = "DOC-UNKNOWN"
    filename: str = ""
    page_number: int = 1
    bounding_box: list[float] = Field(default_factory=list)
    chunk_content: str = ""
    statement: str = ""
    raw_value: str = ""
    normalized_value: str = ""
    normalized_unit: str = ""
    normalized_currency: str = ""
    period_start: str = "1970-01-01"
    period_end: str = "1970-01-01"
    accounting_basis: Optional[str] = None
    organizational_scope: Optional[str] = None
    filing_type: Optional[str] = None
    version_status: Optional[str] = None

    @property
    def as_decimal(self) -> Optional[Decimal]:
        """Convert normalized_value string to Python Decimal if applicable."""
        try:
            return Decimal(self.normalized_value)
        except Exception:
            return None


class HypothesisProposal(BaseModel):
    """Candidate explanation generated during hypothesis tournament."""
    hypothesis_id: str
    explanation_type: HypothesisClass
    description: str
    likelihood_score: float = Field(default=0.5, ge=0.0, le=1.0)


class ValidatorOutcome(BaseModel):
    """Result of a specialist validator test against a hypothesis."""
    result_id: str
    hypothesis_id: str
    validator_type: str
    outcome: ValidationStatus
    details: dict[str, Any] = Field(default_factory=dict)


class ReconciliationProposal(BaseModel):
    """Structured explanation bridge synthesizing supported validator findings."""
    supported_hypothesis_id: str
    explanation_type: HypothesisClass
    root_cause: str
    reconciliation_bridge: str
    arithmetic_delta: Optional[str] = None
    citations: list[str] = Field(default_factory=list)


class SkepticOutcome(BaseModel):
    """Adversarial critique testing the integrity of a reconciliation proposal."""
    status: SkepticStatus
    critique: str
    citations_verified: bool = False
    unstated_assumptions: list[str] = Field(default_factory=list)


class FactDecisionState(TypedDict, total=False):
    """Immutable state dictionary flowing through LangGraph workflow nodes."""
    group_id: str
    entity: str
    attribute: str
    period_id: str
    candidates: list[dict[str, Any]]
    decision_path: str  # "A" (Corroboration), "B" (Contextual), "C" (Conflict)
    variance_pct: Optional[float]
    arithmetic_equal: bool
    matching_context: bool
    hypotheses: list[dict[str, Any]]
    validator_results: list[dict[str, Any]]
    reconciliation_proposal: Optional[dict[str, Any]]
    skeptic_outcome: Optional[dict[str, Any]]
    verdict: Optional[str]
    decision_strength: Optional[str]
    reasoning_summary: Optional[str]
    traces: list[dict[str, Any]]
    error: Optional[str]
