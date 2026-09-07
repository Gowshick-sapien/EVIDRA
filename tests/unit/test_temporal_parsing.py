import pytest
# pyrefly: ignore [missing-import]
from src.verification.normalizers import TemporalNormalizer


def test_fiscal_year_interval():
    """Verify Indian fiscal year bounds (April 1 to March 31)."""
    assert TemporalNormalizer.normalize("FY22") == ("2021-04-01", "2022-03-31")
    assert TemporalNormalizer.normalize("Fiscal 2022") == ("2021-04-01", "2022-03-31")
    assert TemporalNormalizer.normalize("FY 2021-22") == ("2021-04-01", "2022-03-31")
    assert TemporalNormalizer.normalize("FY21") == ("2020-04-01", "2021-03-31")


def test_quarterly_intervals():
    """Verify Indian fiscal year quarter boundaries."""
    assert TemporalNormalizer.normalize("Q1 FY22") == ("2021-04-01", "2021-06-30")
    assert TemporalNormalizer.normalize("Q2 FY22") == ("2021-07-01", "2021-09-30")
    assert TemporalNormalizer.normalize("Q3 FY22") == ("2021-10-01", "2021-12-31")
    assert TemporalNormalizer.normalize("Q4 FY22") == ("2022-01-01", "2022-03-31")


def test_partial_periods():
    """Verify nine-month and six-month period parsing."""
    assert TemporalNormalizer.normalize("Nine months ended December 31, 2021") == ("2021-04-01", "2021-12-31")
    assert TemporalNormalizer.normalize("Six months ended Sep 30, 2021") == ("2021-04-01", "2021-09-30")


def test_calendar_year_and_point_in_time():
    """Verify calendar year and exact point-in-time dates."""
    assert TemporalNormalizer.normalize("CY2021") == ("2021-01-01", "2021-12-31")
    assert TemporalNormalizer.normalize("March 31, 2022") == ("2022-03-31", "2022-03-31")
    assert TemporalNormalizer.normalize("As of December 31, 2021") == ("2021-12-31", "2021-12-31")


def test_fallback_on_unparseable_date():
    """Verify safe fallback for undated or ambiguous temporal strings."""
    assert TemporalNormalizer.normalize("Undated") == ("1970-01-01", "1970-01-01")
    assert TemporalNormalizer.normalize("") == ("1970-01-01", "1970-01-01")
