from __future__ import annotations

import re
import uuid
from decimal import Decimal
from typing import Any, Optional

# pyrefly: ignore [missing-import]
from src.decision.schemas import (
    CandidateFactView,
    HypothesisClass,
    ValidationStatus,
    ValidatorOutcome,
)


class ArithmeticValidator:
    """Validator performing exact Python Decimal arithmetic variance and tolerance checks."""
    DEFAULT_TOLERANCE = Decimal("0.0001")  # 0.01%

    @classmethod
    def evaluate(
        cls,
        c1: CandidateFactView,
        c2: CandidateFactView,
        tolerance: Decimal = DEFAULT_TOLERANCE,
        hypothesis_id: str = "",
    ) -> ValidatorOutcome:
        v1 = c1.as_decimal
        v2 = c2.as_decimal

        if v1 is None or v2 is None:
            # Fallback to string equality if non-numeric
            equal = c1.normalized_value.strip().lower() == c2.normalized_value.strip().lower()
            status = ValidationStatus.SUPPORTED if equal else ValidationStatus.REFUTED
            return ValidatorOutcome(
                result_id=f"VAL-{uuid.uuid4().hex[:8]}",
                hypothesis_id=hypothesis_id,
                validator_type="ArithmeticValidator",
                outcome=status,
                details={"numeric": False, "string_match": equal},
            )

        delta = abs(v1 - v2)
        denom = max(abs(v1), abs(v2))
        variance_pct = (delta / denom) if denom > Decimal("0") else Decimal("0")
        within_tolerance = variance_pct <= tolerance

        outcome = ValidationStatus.SUPPORTED if within_tolerance else ValidationStatus.REFUTED

        return ValidatorOutcome(
            result_id=f"VAL-{uuid.uuid4().hex[:8]}",
            hypothesis_id=hypothesis_id,
            validator_type="ArithmeticValidator",
            outcome=outcome,
            details={
                "value_1": str(v1),
                "value_2": str(v2),
                "delta": str(delta),
                "variance_pct": float(variance_pct),
                "within_tolerance": within_tolerance,
                "tolerance": float(tolerance),
            },
        )


class RestatementValidator:
    """Validator testing whether variance is explained by an audit restatement or amended filing."""
    RESTATEMENT_KEYWORDS = re.compile(
        r"\b(restated|as\s+restated|retrospectively\s+adjusted|amended|revised|prior\s+period\s+adjustment)\b",
        re.IGNORECASE,
    )

    @classmethod
    def evaluate(
        cls,
        c1: CandidateFactView,
        c2: CandidateFactView,
        hypothesis_id: str = "",
    ) -> ValidatorOutcome:
        # Check explicit version status
        s1_restated = (c1.version_status == "RESTATED")
        s2_restated = (c2.version_status == "RESTATED")

        # Check textual keywords in chunks
        text1_has_kw = bool(cls.RESTATEMENT_KEYWORDS.search(c1.chunk_content or ""))
        text2_has_kw = bool(cls.RESTATEMENT_KEYWORDS.search(c2.chunk_content or ""))

        # Check statement text
        stmt1_has_kw = bool(cls.RESTATEMENT_KEYWORDS.search(c1.statement or ""))
        stmt2_has_kw = bool(cls.RESTATEMENT_KEYWORDS.search(c2.statement or ""))

        is_restatement = (
            (s1_restated != s2_restated)
            or (text1_has_kw != text2_has_kw)
            or stmt1_has_kw
            or stmt2_has_kw
        )

        outcome = ValidationStatus.SUPPORTED if is_restatement else ValidationStatus.INCONCLUSIVE

        return ValidatorOutcome(
            result_id=f"VAL-{uuid.uuid4().hex[:8]}",
            hypothesis_id=hypothesis_id,
            validator_type="RestatementValidator",
            outcome=outcome,
            details={
                "candidate_1_restated": s1_restated or text1_has_kw or stmt1_has_kw,
                "candidate_2_restated": s2_restated or text2_has_kw or stmt2_has_kw,
                "evidence_cited": [c for c in [c1.chunk_content, c2.chunk_content] if cls.RESTATEMENT_KEYWORDS.search(c or "")][:1],
            },
        )


class AccountingBasisValidator:
    """Validator testing whether variance arises from differing accounting standards (GAAP vs Non-GAAP)."""
    NON_GAAP_KEYWORDS = re.compile(
        r"\b(non-gaap|adjusted|ebitda|adjusted\s+ebitda|stock-based\s+compensation|share-based|amortization\s+of\s+intangibles)\b",
        re.IGNORECASE,
    )

    @classmethod
    def evaluate(
        cls,
        c1: CandidateFactView,
        c2: CandidateFactView,
        hypothesis_id: str = "",
    ) -> ValidatorOutcome:
        b1 = (c1.accounting_basis or "").upper()
        b2 = (c2.accounting_basis or "").upper()

        basis_mismatch = bool(b1 and b2 and b1 != b2)

        t1_ng = bool(cls.NON_GAAP_KEYWORDS.search(c1.chunk_content or "")) or bool(cls.NON_GAAP_KEYWORDS.search(c1.statement or ""))
        t2_ng = bool(cls.NON_GAAP_KEYWORDS.search(c2.chunk_content or "")) or bool(cls.NON_GAAP_KEYWORDS.search(c2.statement or ""))

        is_accounting_variance = basis_mismatch or (t1_ng != t2_ng) or ("NON_GAAP" in (b1, b2))

        outcome = ValidationStatus.SUPPORTED if is_accounting_variance else ValidationStatus.INCONCLUSIVE

        return ValidatorOutcome(
            result_id=f"VAL-{uuid.uuid4().hex[:8]}",
            hypothesis_id=hypothesis_id,
            validator_type="AccountingBasisValidator",
            outcome=outcome,
            details={
                "basis_1": b1 or "UNSPECIFIED",
                "basis_2": b2 or "UNSPECIFIED",
                "non_gaap_detected": t1_ng or t2_ng,
            },
        )


class ScopeValidator:
    """Validator testing whether variance is caused by Consolidated vs Standalone organizational scope."""
    SCOPE_KEYWORDS = re.compile(r"\b(standalone|consolidated|parent\s+company|group|subsidiary)\b", re.IGNORECASE)

    @classmethod
    def evaluate(
        cls,
        c1: CandidateFactView,
        c2: CandidateFactView,
        hypothesis_id: str = "",
    ) -> ValidatorOutcome:
        s1 = (c1.organizational_scope or "").upper()
        s2 = (c2.organizational_scope or "").upper()

        scope_mismatch = bool(s1 and s2 and s1 != s2)

        t1_scope = "CONSOLIDATED" if "consolidated" in (c1.chunk_content or "").lower() else ("STANDALONE" if "standalone" in (c1.chunk_content or "").lower() else "")
        t2_scope = "CONSOLIDATED" if "consolidated" in (c2.chunk_content or "").lower() else ("STANDALONE" if "standalone" in (c2.chunk_content or "").lower() else "")

        detected_mismatch = scope_mismatch or bool(t1_scope and t2_scope and t1_scope != t2_scope)

        outcome = ValidationStatus.SUPPORTED if detected_mismatch else ValidationStatus.INCONCLUSIVE

        return ValidatorOutcome(
            result_id=f"VAL-{uuid.uuid4().hex[:8]}",
            hypothesis_id=hypothesis_id,
            validator_type="ScopeValidator",
            outcome=outcome,
            details={
                "scope_1": s1 or t1_scope or "UNSPECIFIED",
                "scope_2": s2 or t2_scope or "UNSPECIFIED",
                "mismatch_confirmed": detected_mismatch,
            },
        )


class TimingValidator:
    """Validator testing whether variance is explained by divergent temporal intervals."""

    @classmethod
    def evaluate(
        cls,
        c1: CandidateFactView,
        c2: CandidateFactView,
        hypothesis_id: str = "",
    ) -> ValidatorOutcome:
        p1 = (c1.period_start, c1.period_end)
        p2 = (c2.period_start, c2.period_end)

        timing_mismatch = (p1 != p2) and (p1 != ("1970-01-01", "1970-01-01")) and (p2 != ("1970-01-01", "1970-01-01"))

        outcome = ValidationStatus.SUPPORTED if timing_mismatch else ValidationStatus.INCONCLUSIVE

        return ValidatorOutcome(
            result_id=f"VAL-{uuid.uuid4().hex[:8]}",
            hypothesis_id=hypothesis_id,
            validator_type="TimingValidator",
            outcome=outcome,
            details={
                "period_1": f"{p1[0]} to {p1[1]}",
                "period_2": f"{p2[0]} to {p2[1]}",
                "intervals_differ": timing_mismatch,
            },
        )
