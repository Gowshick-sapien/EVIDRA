"""
Unit tests for Rule-Based Evidence Sufficiency Gate (REQ-DEC-EXT-01).
"""
import pytest

# pyrefly: ignore [missing-import]
from src.decision.schemas import (
    CandidateFactView,
    SufficiencyAction,
    SufficiencyStatus,
)
# pyrefly: ignore [missing-import]
from src.decision.sufficiency import EvidenceSufficiencyGate


def test_sufficiency_empty_candidates():
    """Verify empty candidate list yields INSUFFICIENT_IDENTITY with SKIP action."""
    res = EvidenceSufficiencyGate.evaluate([])
    assert res.status == SufficiencyStatus.INSUFFICIENT_IDENTITY
    assert res.action == SufficiencyAction.SKIP
    assert "candidates" in res.missing_dimensions


def test_sufficiency_single_source():
    """Verify single candidate yields SINGLE_SOURCE_PENDING with DEFER action."""
    c = CandidateFactView(
        fact_id="F1",
        observation_id="O1",
        document_id="DOC1",
        raw_value="500 Cr",
        normalized_value="5000000000",
        normalized_unit="SCALED_CRORE",
        period_start="2023-04-01",
        period_end="2024-03-31",
        chunk_content="Revenue is 500 Cr",
        statement="Revenue is 500 Cr",
    )
    meta = {"entity": "Delhivery Limited", "attribute": "Revenue", "period_id": "FY24"}
    res = EvidenceSufficiencyGate.evaluate([c], group_metadata=meta)

    assert res.status == SufficiencyStatus.SINGLE_SOURCE_PENDING
    assert res.action == SufficiencyAction.DEFER
    assert "second_source" in res.missing_dimensions
    assert "Single source claim" in res.reason


def test_sufficiency_missing_identity():
    """Verify generic entity yields INSUFFICIENT_IDENTITY with SKIP action."""
    c1 = CandidateFactView(
        fact_id="F1", observation_id="O1", document_id="DOC1",
        normalized_value="500", normalized_unit="INR",
        period_start="2023-04-01", period_end="2024-03-31",
        chunk_content="500", statement="500",
    )
    c2 = CandidateFactView(
        fact_id="F2", observation_id="O2", document_id="DOC2",
        normalized_value="500", normalized_unit="INR",
        period_start="2023-04-01", period_end="2024-03-31",
        chunk_content="500", statement="500",
    )
    meta = {"entity": "The Company", "attribute": "Revenue"}  # Generic entity
    res = EvidenceSufficiencyGate.evaluate([c1, c2], group_metadata=meta)

    assert res.status == SufficiencyStatus.INSUFFICIENT_IDENTITY
    assert res.action == SufficiencyAction.SKIP
    assert "entity" in res.missing_dimensions


def test_sufficiency_unverified_evidence():
    """Verify candidate lacking chunk and bounding box yields UNVERIFIED_EVIDENCE."""
    c1 = CandidateFactView(
        fact_id="F1", observation_id="O1", document_id="DOC1",
        normalized_value="500", normalized_unit="INR",
        period_start="2023-04-01", period_end="2024-03-31",
        chunk_content="", bounding_box=[], statement="",
    )
    c2 = CandidateFactView(
        fact_id="F2", observation_id="O2", document_id="DOC2",
        normalized_value="500", normalized_unit="INR",
        period_start="2023-04-01", period_end="2024-03-31",
        chunk_content="500", statement="500",
    )
    meta = {"entity": "Delhivery Limited", "attribute": "Revenue", "period_id": "FY24"}
    res = EvidenceSufficiencyGate.evaluate([c1, c2], group_metadata=meta)

    assert res.status == SufficiencyStatus.UNVERIFIED_EVIDENCE
    assert res.action == SufficiencyAction.SKIP
    assert "evidence_grounding" in res.missing_dimensions


def test_sufficiency_context_divergent_scope():
    """Verify scope mismatch yields CONTEXT_DIVERGENT with RECONCILE_CONTEXT action."""
    c1 = CandidateFactView(
        fact_id="F1", observation_id="O1", document_id="DOC1",
        normalized_value="500", normalized_unit="INR",
        period_start="2023-04-01", period_end="2024-03-31",
        organizational_scope="CONSOLIDATED",
        chunk_content="Consolidated 500", statement="Consolidated 500",
    )
    c2 = CandidateFactView(
        fact_id="F2", observation_id="O2", document_id="DOC2",
        normalized_value="450", normalized_unit="INR",
        period_start="2023-04-01", period_end="2024-03-31",
        organizational_scope="STANDALONE",
        chunk_content="Standalone 450", statement="Standalone 450",
    )
    meta = {"entity": "Delhivery Limited", "attribute": "Revenue", "period_id": "FY24"}
    res = EvidenceSufficiencyGate.evaluate([c1, c2], group_metadata=meta)

    assert res.status == SufficiencyStatus.CONTEXT_DIVERGENT
    assert res.action == SufficiencyAction.RECONCILE_CONTEXT
    assert "scope divergence" in res.reason


def test_sufficiency_adjudication_ready():
    """Verify complete, matching multi-candidate group yields SUFFICIENT_FOR_ADJUDICATION."""
    c1 = CandidateFactView(
        fact_id="F1", observation_id="O1", document_id="DOC1",
        normalized_value="5000000000", normalized_unit="SCALED_CRORE",
        period_start="2023-04-01", period_end="2024-03-31",
        organizational_scope="CONSOLIDATED",
        accounting_basis="IND_AS",
        chunk_content="Revenue 500 Cr", statement="Revenue 500 Cr",
    )
    c2 = CandidateFactView(
        fact_id="F2", observation_id="O2", document_id="DOC2",
        normalized_value="5000000000", normalized_unit="SCALED_CRORE",
        period_start="2023-04-01", period_end="2024-03-31",
        organizational_scope="CONSOLIDATED",
        accounting_basis="IND_AS",
        chunk_content="Revenue 500 Cr", statement="Revenue 500 Cr",
    )
    meta = {
        "entity": "Delhivery Limited",
        "attribute": "Revenue",
        "metric_family": "REVENUE",
        "period_id": "FY24",
    }
    res = EvidenceSufficiencyGate.evaluate([c1, c2], group_metadata=meta)

    assert res.status == SufficiencyStatus.SUFFICIENT_FOR_ADJUDICATION
    assert res.action == SufficiencyAction.ADJUDICATE
    assert "Sufficient evidence established" in res.reason
    assert res.details["candidate_count"] == 2
    assert res.details["document_count"] == 2
