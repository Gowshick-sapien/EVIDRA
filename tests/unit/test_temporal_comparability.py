"""
Unit tests for Temporal Comparability Classification (REQ-TMP-EXT-01, Gate 2).
"""
import pytest
from src.matching.temporal import (
    ComparabilityAction,
    TemporalComparabilityClassifier,
    TemporalRelation,
)


def test_temporal_exact_match():
    """Verify exact match permits direct numerical comparison."""
    rel, action = TemporalComparabilityClassifier.classify(
        "2023-04-01", "2024-03-31",
        "2023-04-01", "2024-03-31",
    )
    assert rel == TemporalRelation.EXACT
    assert action == ComparabilityAction.DIRECTLY_COMPARABLE


def test_temporal_containment_quarter_in_fiscal_year():
    """Verify Q4 inside FY24 is classified as containment and blocks direct value comparison."""
    # Q4 FY24 (2024-01-01 to 2024-03-31) inside FY24 (2023-04-01 to 2024-03-31)
    rel, action = TemporalComparabilityClassifier.classify(
        "2024-01-01", "2024-03-31",
        "2023-04-01", "2024-03-31",
    )
    assert rel == TemporalRelation.CONTAINMENT
    assert action == ComparabilityAction.CONTEXTUALLY_RELATED

    # Reverse order
    rel_rev, action_rev = TemporalComparabilityClassifier.classify(
        "2023-04-01", "2024-03-31",
        "2024-01-01", "2024-03-31",
    )
    assert rel_rev == TemporalRelation.CONTAINMENT
    assert action_rev == ComparabilityAction.CONTEXTUALLY_RELATED


def test_temporal_containment_half_year():
    """Verify H1 inside FY24 is classified as containment."""
    # H1 FY24 (2023-04-01 to 2023-09-30) inside FY24 (2023-04-01 to 2024-03-31)
    rel, action = TemporalComparabilityClassifier.classify(
        "2023-04-01", "2023-09-30",
        "2023-04-01", "2024-03-31",
    )
    assert rel == TemporalRelation.CONTAINMENT
    assert action == ComparabilityAction.CONTEXTUALLY_RELATED


def test_temporal_containment_point_in_time():
    """Verify point-in-time balance sheet date inside fiscal year."""
    rel, action = TemporalComparabilityClassifier.classify(
        "2024-03-31", "2024-03-31",
        "2023-04-01", "2024-03-31",
    )
    assert rel == TemporalRelation.CONTAINMENT
    assert action == ComparabilityAction.CONTEXTUALLY_RELATED


def test_temporal_adjacent_periods():
    """Verify consecutive fiscal years are classified as adjacent."""
    # FY23 (2022-04-01 to 2023-03-31) and FY24 (2023-04-01 to 2024-03-31)
    rel, action = TemporalComparabilityClassifier.classify(
        "2022-04-01", "2023-03-31",
        "2023-04-01", "2024-03-31",
    )
    assert rel == TemporalRelation.ADJACENT
    assert action == ComparabilityAction.CONTEXTUALLY_RELATED

    # Reverse order
    rel_rev, action_rev = TemporalComparabilityClassifier.classify(
        "2023-04-01", "2024-03-31",
        "2022-04-01", "2023-03-31",
    )
    assert rel_rev == TemporalRelation.ADJACENT
    assert action_rev == ComparabilityAction.CONTEXTUALLY_RELATED


def test_temporal_non_overlapping_disjoint():
    """Verify disjoint periods are classified as non-comparable."""
    # FY20 vs FY24
    rel, action = TemporalComparabilityClassifier.classify(
        "2019-04-01", "2020-03-31",
        "2023-04-01", "2024-03-31",
    )
    assert rel == TemporalRelation.NON_OVERLAPPING
    assert action == ComparabilityAction.NON_COMPARABLE


def test_temporal_overlapping_partial_shift():
    """Verify partial shift (e.g. CY2023 vs FY24) is classified as specialized treatment."""
    # CY2023 (2023-01-01 to 2023-12-31) vs FY24 (2023-04-01 to 2024-03-31)
    rel, action = TemporalComparabilityClassifier.classify(
        "2023-01-01", "2023-12-31",
        "2023-04-01", "2024-03-31",
    )
    assert rel == TemporalRelation.OVERLAPPING
    assert action == ComparabilityAction.SPECIALIZED_TREATMENT


def test_temporal_unknown_fallback():
    """Verify unstated or epoch fallback dates terminate in unresolved."""
    rel, action = TemporalComparabilityClassifier.classify(
        "1970-01-01", "1970-01-01",
        "2023-04-01", "2024-03-31",
    )
    assert rel == TemporalRelation.UNKNOWN
    assert action == ComparabilityAction.UNRESOLVED
