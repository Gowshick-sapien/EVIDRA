from decimal import Decimal
import pytest
# pyrefly: ignore [missing-import]
from src.verification.normalizers import CurrencyNormalizer, DecimalNormalizer


def test_indian_numbering_system():
    """Verify that Crores and Lakhs scale to exact Decimals."""
    val_cr, unit_cr = DecimalNormalizer.normalize("INR 4,810.50 Crores")
    assert val_cr == Decimal("48105000000.00")
    assert unit_cr == "SCALED_CRORES"

    val_lakh, unit_lakh = DecimalNormalizer.normalize("Rs. 25.75 Lakhs")
    assert val_lakh == Decimal("2575000.00")
    assert unit_lakh == "SCALED_LAKHS"

    val_arab, unit_arab = DecimalNormalizer.normalize("2 Arab")
    assert val_arab == Decimal("2000000000")


def test_western_numbering_system():
    """Verify that Millions, Billions, and Thousands scale to exact Decimals."""
    val_mn, unit_mn = DecimalNormalizer.normalize("6,882.29 million")
    assert val_mn == Decimal("6882290000.00")
    assert unit_mn == "SCALED_MILLION"

    val_bn, unit_bn = DecimalNormalizer.normalize("$ 1.5 Billion")
    assert val_bn == Decimal("1500000000.0")
    assert unit_bn == "SCALED_BILLION"

    val_k, unit_k = DecimalNormalizer.normalize("500 K")
    assert val_k == Decimal("500000")


def test_bracketed_negatives_and_percentages():
    """Verify bracketed negative numbers and percentages."""
    val_neg, _ = DecimalNormalizer.normalize("(4,810.50)")
    assert val_neg == Decimal("-4810.50")

    val_pct, unit_pct = DecimalNormalizer.normalize("12.4%")
    assert val_pct == Decimal("12.4")
    assert unit_pct == "PERCENT"

    val_pct_neg, unit_pct_neg = DecimalNormalizer.normalize("(5.2)%")
    assert val_pct_neg == Decimal("-5.2")
    assert unit_pct_neg == "PERCENT"


def test_exact_decimal_arithmetic_no_float_drift():
    """Confirm mathematical precision without standard IEEE 754 floating point drift."""
    val1, _ = DecimalNormalizer.normalize("0.1")
    val2, _ = DecimalNormalizer.normalize("0.2")
    assert val1 + val2 == Decimal("0.3")
    assert str(val1 + val2) != "0.30000000000000004"


def test_currency_normalization():
    """Verify ISO 4217 standard currency mapping."""
    assert CurrencyNormalizer.normalize("₹ in million") == "INR"
    assert CurrencyNormalizer.normalize("Rs. 500") == "INR"
    assert CurrencyNormalizer.normalize("USD 1,000") == "USD"
    assert CurrencyNormalizer.normalize("$ 50") == "USD"
    assert CurrencyNormalizer.normalize("EUR 200") == "EUR"
    assert CurrencyNormalizer.normalize("£ 100") == "GBP"
    assert CurrencyNormalizer.normalize("No monetary unit here") == ""
