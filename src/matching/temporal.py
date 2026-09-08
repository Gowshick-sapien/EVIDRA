"""
Temporal Comparability Classification for EVIDRA 2.0 (Phase P1, Gate 2).

Evaluates whether two temporal intervals represent identical periods (direct comparison),
containment (contextual relationship without value comparison), sequential periods,
or non-overlapping disjoint periods.
"""

from __future__ import annotations

from datetime import date, timedelta
from enum import Enum
from typing import Tuple


class TemporalRelation(str, Enum):
    """Classification of the topological relationship between two temporal intervals."""
    EXACT = "EXACT"                       # Identical start and end dates
    CONTAINMENT = "CONTAINMENT"           # One interval fully inside another (e.g. Q4 inside FY24)
    ADJACENT = "ADJACENT"                 # Consecutive periods (e.g. FY23 followed by FY24)
    OVERLAPPING = "OVERLAPPING"           # Partial non-concentric shift (e.g. TTM vs Calendar Year)
    NON_OVERLAPPING = "NON_OVERLAPPING"   # Fully disjoint periods (e.g. FY20 vs FY24)
    UNKNOWN = "UNKNOWN"                   # Unstated or unparsed temporal intervals


class ComparabilityAction(str, Enum):
    """Decision action governing whether numerical variance checks may execute."""
    DIRECTLY_COMPARABLE = "DIRECTLY_COMPARABLE"     # Numerical variance check permitted
    CONTEXTUALLY_RELATED = "CONTEXTUALLY_RELATED"   # Related context only; DO NOT compare values
    SPECIALIZED_TREATMENT = "SPECIALIZED_TREATMENT" # Requires specialized reconciler
    NON_COMPARABLE = "NON_COMPARABLE"               # Disjoint periods; do not group or compare
    UNRESOLVED = "UNRESOLVED"                       # Ambiguous temporal boundaries


class TemporalComparabilityClassifier:
    """
    Evaluates temporal intervals and defines exact comparability actions for Gate 2.
    """

    @classmethod
    def classify(
        cls,
        start1: str,
        end1: str,
        start2: str,
        end2: str,
    ) -> Tuple[TemporalRelation, ComparabilityAction]:
        """
        Classify the temporal relationship between interval 1 [start1, end1] and interval 2 [start2, end2].
        
        Dates must be ISO-8601 strings (YYYY-MM-DD).
        """
        # 1. Guard against unstated or epoch fallback dates
        if (
            not start1 or not end1 or not start2 or not end2
            or start1 == "1970-01-01" or start2 == "1970-01-01"
            or end1 == "1970-01-01" or end2 == "1970-01-01"
        ):
            return TemporalRelation.UNKNOWN, ComparabilityAction.UNRESOLVED

        try:
            d_s1 = date.fromisoformat(start1)
            d_e1 = date.fromisoformat(end1)
            d_s2 = date.fromisoformat(start2)
            d_e2 = date.fromisoformat(end2)
        except (ValueError, TypeError):
            return TemporalRelation.UNKNOWN, ComparabilityAction.UNRESOLVED

        # Guarantee interval orientation
        if d_s1 > d_e1:
            d_s1, d_e1 = d_e1, d_s1
        if d_s2 > d_e2:
            d_s2, d_e2 = d_e2, d_s2

        # 2. Exact Match (Direct Numerical Comparison Permitted)
        if d_s1 == d_s2 and d_e1 == d_e2:
            return TemporalRelation.EXACT, ComparabilityAction.DIRECTLY_COMPARABLE

        # 3. Containment (One interval strictly inside or matching boundary of another)
        # e.g., Q4 (Jan 1 to Mar 31) inside FY (Apr 1 to Mar 31)
        if (d_s1 <= d_s2 and d_e2 <= d_e1) or (d_s2 <= d_s1 and d_e1 <= d_e2):
            return TemporalRelation.CONTAINMENT, ComparabilityAction.CONTEXTUALLY_RELATED

        # 4. Adjacent Periods (Consecutive financial reporting cycles)
        # e.g., FY23 ends 2023-03-31 and FY24 starts 2023-04-01
        if d_e1 + timedelta(days=1) == d_s2 or d_e2 + timedelta(days=1) == d_s1:
            return TemporalRelation.ADJACENT, ComparabilityAction.CONTEXTUALLY_RELATED

        # 5. Non-Overlapping Disjoint Periods
        if d_e1 < d_s2 or d_e2 < d_s1:
            return TemporalRelation.NON_OVERLAPPING, ComparabilityAction.NON_COMPARABLE

        # 6. Overlapping Partial Shift (e.g. 12-month TTM vs 12-month CY)
        return TemporalRelation.OVERLAPPING, ComparabilityAction.SPECIALIZED_TREATMENT
