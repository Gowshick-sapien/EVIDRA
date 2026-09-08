"""
Unit tests for 4-Gate Contextual Fact Resolution (REQ-MAT-EXT-01).
"""
import pytest
from src.matching.embeddings import ContextualFactGroupEngine
from src.matching.identity import (
    FactIdentitySignature,
    MeasurementType,
)


@pytest.fixture
def group_engine():
    return ContextualFactGroupEngine()


def test_gate_1_entity_grounding(group_engine):
    """Gate 1: Fact candidates from different legal entities must never be grouped."""
    candidates = [
        {"fact_id": "F1", "entity": "Delhivery Limited", "attribute": "Revenue", "period_start": "2023-04-01", "period_end": "2024-03-31"},
        {"fact_id": "F2", "entity": "Blue Dart Express", "attribute": "Revenue", "period_start": "2023-04-01", "period_end": "2024-03-31"},
    ]
    sigs = {
        "F1": FactIdentitySignature(
            identity_id="ID1", fact_id="F1", entity_canonical="Delhivery Limited",
            metric_family="REVENUE", metric_subtype="REVENUE", measurement_type=MeasurementType.ABSOLUTE_VALUE,
            surface_metric="Revenue", period_start="2023-04-01", period_end="2024-03-31",
        ),
        "F2": FactIdentitySignature(
            identity_id="ID2", fact_id="F2", entity_canonical="Blue Dart Express",
            metric_family="REVENUE", metric_subtype="REVENUE", measurement_type=MeasurementType.ABSOLUTE_VALUE,
            surface_metric="Revenue", period_start="2023-04-01", period_end="2024-03-31",
        ),
    }

    groups = group_engine.group_candidates(candidates, signatures=sigs)
    assert len(groups) == 2
    for grp, fids in groups:
        assert len(fids) == 1


def test_gate_3a_measurement_type_isolation(group_engine):
    """Gate 3: Absolute value (INR 8,142 Cr) and growth rate (+29.8% YoY) must never be grouped."""
    candidates = [
        {"fact_id": "F1", "entity": "Delhivery Limited", "attribute": "Revenue", "raw_value": "8142 Cr", "period_start": "2023-04-01", "period_end": "2024-03-31"},
        {"fact_id": "F2", "entity": "Delhivery Limited", "attribute": "Revenue Growth", "raw_value": "+29.8%", "period_start": "2023-04-01", "period_end": "2024-03-31"},
    ]
    sigs = {
        "F1": FactIdentitySignature(
            identity_id="ID1", fact_id="F1", entity_canonical="Delhivery Limited",
            metric_family="REVENUE", metric_subtype="REVENUE", measurement_type=MeasurementType.ABSOLUTE_VALUE,
            surface_metric="Revenue", period_start="2023-04-01", period_end="2024-03-31",
        ),
        "F2": FactIdentitySignature(
            identity_id="ID2", fact_id="F2", entity_canonical="Delhivery Limited",
            metric_family="REVENUE", metric_subtype="REVENUE_GROWTH", measurement_type=MeasurementType.RATE_OF_CHANGE,
            surface_metric="Revenue Growth", period_start="2023-04-01", period_end="2024-03-31",
        ),
    }

    groups = group_engine.group_candidates(candidates, signatures=sigs)
    assert len(groups) == 2
    types_found = {grp.measurement_type for grp, _ in groups}
    assert "ABSOLUTE_VALUE" in types_found
    assert "RATE_OF_CHANGE" in types_found


def test_gate_2_temporal_containment_isolation(group_engine):
    """Gate 2: Full-year FY24 revenue and Q4 FY24 revenue must be placed in separate direct comparison groups."""
    candidates = [
        {"fact_id": "F1", "entity": "Delhivery Limited", "attribute": "Revenue", "period_start": "2023-04-01", "period_end": "2024-03-31"},
        {"fact_id": "F2", "entity": "Delhivery Limited", "attribute": "Revenue", "period_start": "2024-01-01", "period_end": "2024-03-31"},
    ]
    sigs = {
        "F1": FactIdentitySignature(
            identity_id="ID1", fact_id="F1", entity_canonical="Delhivery Limited",
            metric_family="REVENUE", metric_subtype="REVENUE", measurement_type=MeasurementType.ABSOLUTE_VALUE,
            surface_metric="Revenue", period_start="2023-04-01", period_end="2024-03-31",
        ),
        "F2": FactIdentitySignature(
            identity_id="ID2", fact_id="F2", entity_canonical="Delhivery Limited",
            metric_family="REVENUE", metric_subtype="REVENUE", measurement_type=MeasurementType.ABSOLUTE_VALUE,
            surface_metric="Revenue", period_start="2024-01-01", period_end="2024-03-31",
        ),
    }

    groups = group_engine.group_candidates(candidates, signatures=sigs)
    assert len(groups) == 2
    periods_found = {grp.period_id for grp, _ in groups}
    assert "2023-04-01_2024-03-31" in periods_found
    assert "2024-01-01_2024-03-31" in periods_found


def test_gate_3b_metric_subtype_isolation(group_engine):
    """Gate 3: Distinct metric subtypes (OPERATING_REVENUE vs SERVICE_REVENUE) must be partitioned."""
    candidates = [
        {"fact_id": "F1", "entity": "Delhivery Limited", "attribute": "Operating Revenue", "period_start": "2023-04-01", "period_end": "2024-03-31"},
        {"fact_id": "F2", "entity": "Delhivery Limited", "attribute": "Service Revenue", "period_start": "2023-04-01", "period_end": "2024-03-31"},
    ]
    sigs = {
        "F1": FactIdentitySignature(
            identity_id="ID1", fact_id="F1", entity_canonical="Delhivery Limited",
            metric_family="REVENUE", metric_subtype="OPERATING_REVENUE", measurement_type=MeasurementType.ABSOLUTE_VALUE,
            surface_metric="Operating Revenue", period_start="2023-04-01", period_end="2024-03-31",
        ),
        "F2": FactIdentitySignature(
            identity_id="ID2", fact_id="F2", entity_canonical="Delhivery Limited",
            metric_family="REVENUE", metric_subtype="SERVICE_REVENUE", measurement_type=MeasurementType.ABSOLUTE_VALUE,
            surface_metric="Service Revenue", period_start="2023-04-01", period_end="2024-03-31",
        ),
    }

    groups = group_engine.group_candidates(candidates, signatures=sigs)
    assert len(groups) == 2
    subtypes_found = {grp.metric_subtype for grp, _ in groups}
    assert subtypes_found == {"OPERATING_REVENUE", "SERVICE_REVENUE"}


def test_gate_4_context_compatibility_divergence_tagging(group_engine):
    """Gate 4: Scope mismatch (Consolidated vs Standalone) tags group as CONTEXTUAL_COMPARISON."""
    candidates = [
        {"fact_id": "F1", "entity": "Delhivery Limited", "attribute": "Revenue", "period_start": "2023-04-01", "period_end": "2024-03-31"},
        {"fact_id": "F2", "entity": "Delhivery Limited", "attribute": "Revenue", "period_start": "2023-04-01", "period_end": "2024-03-31"},
    ]
    sigs = {
        "F1": FactIdentitySignature(
            identity_id="ID1", fact_id="F1", entity_canonical="Delhivery Limited",
            metric_family="REVENUE", metric_subtype="REVENUE", measurement_type=MeasurementType.ABSOLUTE_VALUE,
            surface_metric="Revenue", period_start="2023-04-01", period_end="2024-03-31",
            scope="CONSOLIDATED", basis="IND_AS",
        ),
        "F2": FactIdentitySignature(
            identity_id="ID2", fact_id="F2", entity_canonical="Delhivery Limited",
            metric_family="REVENUE", metric_subtype="REVENUE", measurement_type=MeasurementType.ABSOLUTE_VALUE,
            surface_metric="Revenue", period_start="2023-04-01", period_end="2024-03-31",
            scope="STANDALONE", basis="IND_AS",
        ),
    }

    groups = group_engine.group_candidates(candidates, signatures=sigs)
    assert len(groups) == 1
    grp, fids = groups[0]
    assert len(fids) == 2
    assert grp.group_type == "CONTEXTUAL_COMPARISON"


def test_4gate_corroborating_match(group_engine):
    """Verify that claims matching across all 4 gates form a DIRECT_COMPARISON group with member_count = 2."""
    candidates = [
        {"fact_id": "F1", "entity": "Delhivery Limited", "attribute": "Revenue from Operations", "period_start": "2023-04-01", "period_end": "2024-03-31"},
        {"fact_id": "F2", "entity": "Delhivery Limited", "attribute": "Revenue from operations", "period_start": "2023-04-01", "period_end": "2024-03-31"},
    ]
    sigs = {
        "F1": FactIdentitySignature(
            identity_id="ID1", fact_id="F1", entity_canonical="Delhivery Limited",
            metric_family="REVENUE", metric_subtype="OPERATING_REVENUE", measurement_type=MeasurementType.ABSOLUTE_VALUE,
            surface_metric="Revenue from Operations", period_start="2023-04-01", period_end="2024-03-31",
            scope="CONSOLIDATED", basis="IND_AS",
        ),
        "F2": FactIdentitySignature(
            identity_id="ID2", fact_id="F2", entity_canonical="Delhivery Limited",
            metric_family="REVENUE", metric_subtype="OPERATING_REVENUE", measurement_type=MeasurementType.ABSOLUTE_VALUE,
            surface_metric="Revenue from operations", period_start="2023-04-01", period_end="2024-03-31",
            scope="CONSOLIDATED", basis="IND_AS",
        ),
    }

    groups = group_engine.group_candidates(candidates, signatures=sigs)
    assert len(groups) == 1
    grp, fids = groups[0]
    assert len(fids) == 2
    assert fids == ["F1", "F2"]
    assert grp.group_type == "DIRECT_COMPARISON"
    assert grp.metric_family == "REVENUE"
    assert grp.metric_subtype == "OPERATING_REVENUE"
    assert grp.measurement_type == "ABSOLUTE_VALUE"
