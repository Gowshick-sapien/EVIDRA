"""
Unit tests for Upgraded Specialist Validators and Reconciliation Proposer (REQ-DEC-EXT-03).
"""
import pytest
from decimal import Decimal

# pyrefly: ignore [missing-import]
from src.decision.schemas import (
    CandidateFactView,
    HypothesisClass,
    SkepticStatus,
    ValidationStatus,
)
# pyrefly: ignore [missing-import]
from src.decision.validators import (
    AccountingBasisValidator,
    ArithmeticValidator,
    RestatementValidator,
    ScopeValidator,
    TimingValidator,
)
# pyrefly: ignore [missing-import]
from src.decision.reconciliation import (
    AdversarialSkepticAgent,
    ReconciliationProposerAgent,
)


def test_timing_validator_containment_and_exact():
    """Verify TimingValidator recognizes containment and exact periods via temporal classifier."""
    c_q4 = CandidateFactView(
        fact_id="F1", observation_id="O1",
        period_start="2024-01-01", period_end="2024-03-31",
        normalized_value="2500", normalized_unit="INR",
    )
    c_fy = CandidateFactView(
        fact_id="F2", observation_id="O2",
        period_start="2023-04-01", period_end="2024-03-31",
        normalized_value="8500", normalized_unit="INR",
    )
    c_exact = CandidateFactView(
        fact_id="F3", observation_id="O3",
        period_start="2024-01-01", period_end="2024-03-31",
        normalized_value="2500", normalized_unit="INR",
    )

    # Q4 vs FY24 -> Containment (Supported timing difference)
    res_contain = TimingValidator.evaluate(c_q4, c_fy)
    assert res_contain.outcome == ValidationStatus.SUPPORTED
    assert res_contain.details["temporal_relation"] == "CONTAINMENT"

    # Q4 vs Q4 -> Exact (Inconclusive for timing variance)
    res_exact = TimingValidator.evaluate(c_q4, c_exact)
    assert res_exact.outcome == ValidationStatus.INCONCLUSIVE
    assert res_exact.details["temporal_relation"] == "EXACT"


def test_scope_validator_consolidated_vs_standalone():
    """Verify ScopeValidator confirms scope mismatch when Consolidated differs from Standalone."""
    c_cons = CandidateFactView(
        fact_id="F1", observation_id="O1",
        organizational_scope="CONSOLIDATED",
        normalized_value="1000", normalized_unit="INR",
        chunk_content="Consolidated statements report 1000 Cr",
    )
    c_stan = CandidateFactView(
        fact_id="F2", observation_id="O2",
        organizational_scope="STANDALONE",
        normalized_value="800", normalized_unit="INR",
        chunk_content="Standalone statements report 800 Cr",
    )
    c_cons2 = CandidateFactView(
        fact_id="F3", observation_id="O3",
        organizational_scope="CONSOLIDATED",
        normalized_value="1000", normalized_unit="INR",
        chunk_content="Consolidated statements report 1000 Cr",
    )

    res_mismatch = ScopeValidator.evaluate(c_cons, c_stan)
    assert res_mismatch.outcome == ValidationStatus.SUPPORTED
    assert res_mismatch.details["mismatch_confirmed"] is True

    res_match = ScopeValidator.evaluate(c_cons, c_cons2)
    assert res_match.outcome == ValidationStatus.INCONCLUSIVE


def test_accounting_basis_validator_non_gaap():
    """Verify AccountingBasisValidator detects GAAP vs Non-GAAP adjustments."""
    c_gaap = CandidateFactView(
        fact_id="F1", observation_id="O1",
        accounting_basis="IND_AS",
        normalized_value="1200", normalized_unit="INR",
        chunk_content="Operating Profit under Ind AS is 1200 Cr",
    )
    c_non_gaap = CandidateFactView(
        fact_id="F2", observation_id="O2",
        accounting_basis="NON_GAAP",
        normalized_value="1450", normalized_unit="INR",
        chunk_content="Adjusted EBITDA is 1450 Cr before share-based payments",
    )

    res = AccountingBasisValidator.evaluate(c_gaap, c_non_gaap)
    assert res.outcome == ValidationStatus.SUPPORTED
    assert res.details["non_gaap_detected"] is True


def test_reconciliation_proposer_and_skeptic_lifecycle():
    """Verify proposer creates proposal from supported validator and skeptic audits citations."""
    c1 = CandidateFactView(
        fact_id="F1", observation_id="O1",
        accounting_basis="IND_AS",
        normalized_value="12000000000", normalized_unit="SCALED_CRORE",
        chunk_content="Operating profit under Ind AS is INR 1,200 Cr.",
    )
    c2 = CandidateFactView(
        fact_id="F2", observation_id="O2",
        accounting_basis="NON_GAAP",
        normalized_value="14500000000", normalized_unit="SCALED_CRORE",
        chunk_content="Adjusted EBITDA is INR 1,450 Cr excluding ESOP expenses.",
    )

    val_res = AccountingBasisValidator.evaluate(c1, c2, hypothesis_id="HYP-1")
    assert val_res.outcome == ValidationStatus.SUPPORTED

    # Propose reconciliation bridge
    proposal = ReconciliationProposerAgent.propose_deterministically(c1, c2, [val_res])
    assert proposal is not None
    assert proposal.explanation_type == HypothesisClass.ACCOUNTING_BASIS
    assert proposal.arithmetic_delta == "2500000000"
    assert "GAAP vs Non-GAAP" in proposal.root_cause

    # Adversarial Skeptic evaluates proposal
    skeptic_res = AdversarialSkepticAgent.critique_deterministically(c1, c2, proposal)
    assert skeptic_res.status == SkepticStatus.SURVIVED
    assert skeptic_res.citations_verified is True
