from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple
from pydantic import BaseModel, Field

MAGNITUDE_MULTIPLIERS: dict[str, Decimal] = {
    # Indian numbering
    "crore": Decimal("10000000"),
    "crores": Decimal("10000000"),
    "cr": Decimal("10000000"),
    "lakh": Decimal("100000"),
    "lakhs": Decimal("100000"),
    "lac": Decimal("100000"),
    "lacs": Decimal("100000"),
    "arab": Decimal("1000000000"),
    # Western numbering
    "thousand": Decimal("1000"),
    "thousands": Decimal("1000"),
    "k": Decimal("1000"),
    "million": Decimal("1000000"),
    "millions": Decimal("1000000"),
    "mn": Decimal("1000000"),
    "m": Decimal("1000000"),
    "billion": Decimal("1000000000"),
    "billions": Decimal("1000000000"),
    "bn": Decimal("1000000000"),
    "b": Decimal("1000000000"),
    "trillion": Decimal("1000000000000"),
    "trillions": Decimal("1000000000000"),
    "tn": Decimal("1000000000000"),
}

CURRENCY_SYMBOLS: dict[str, str] = {
    "₹": "INR",
    "rs": "INR",
    "rs.": "INR",
    "inr": "INR",
    "rupees": "INR",
    "$": "USD",
    "usd": "USD",
    "us$": "USD",
    "dollars": "USD",
    "€": "EUR",
    "eur": "EUR",
    "euros": "EUR",
    "£": "GBP",
    "gbp": "GBP",
    "pounds": "GBP",
}


class FactCandidateModel(BaseModel):
    """Normalized, canonical representation of a verified financial fact candidate."""
    fact_id: str
    observation_id: str
    normalized_value: str
    normalized_unit: str
    normalized_currency: str
    period_start: str
    period_end: str


class DecimalNormalizer:
    """Pure Python deterministic normalizer using exact decimal.Decimal arithmetic."""

    @staticmethod
    def normalize(
        raw_value: str,
        stated_unit: str = "",
    ) -> Tuple[Optional[Decimal], str]:
        """Convert a raw financial string into an exact Decimal and standardized unit."""
        if not raw_value or not raw_value.strip():
            return None, ""

        text = raw_value.strip()

        # Check for percentage
        is_percent = "%" in text or "percent" in stated_unit.lower() or "percentage" in stated_unit.lower()

        # Strip currency symbols, commas, and percentage characters
        clean_text = text
        for symbol in ("₹", "$", "€", "£", "Rs.", "Rs", "INR", "USD", "EUR", "GBP", "%"):
            clean_text = clean_text.replace(symbol, "")

        clean_text = clean_text.replace(",", "").strip()

        # Check for bracketed negative numbers e.g. "(1,234.50)" -> "-1234.50"
        is_negative = False
        bracket_match = re.match(r"^\((.+)\)$", clean_text)
        if bracket_match:
            is_negative = True
            clean_text = bracket_match.group(1).strip()
        elif clean_text.startswith("-"):
            is_negative = True
            clean_text = clean_text[1:].strip()

        # Extract numerical token
        num_match = re.search(r"[-+]?\d*\.?\d+", clean_text)
        if not num_match:
            return None, ""

        num_str = num_match.group(0)
        try:
            base_dec = Decimal(num_str)
            if is_negative:
                base_dec = -base_dec
        except InvalidOperation:
            return None, ""

        # Check for embedded or stated magnitude words
        combined_context = f"{text} {stated_unit}".lower()
        multiplier = Decimal("1")
        resolved_unit = "UNIT_BASE"

        if is_percent:
            resolved_unit = "PERCENT"
        else:
            for word, factor in MAGNITUDE_MULTIPLIERS.items():
                pattern = r"\b" + re.escape(word) + r"\b"
                if re.search(pattern, combined_context):
                    multiplier = factor
                    resolved_unit = f"SCALED_{word.upper()}"
                    break

        scaled_dec = base_dec * multiplier
        return scaled_dec, resolved_unit


class CurrencyNormalizer:
    """Standardizes currency designations to ISO 4217 codes without unauthorized conversion."""

    @staticmethod
    def normalize(currency_str: str, raw_value_context: str = "") -> str:
        combined = f"{currency_str} {raw_value_context}".lower()
        for symbol, iso_code in CURRENCY_SYMBOLS.items():
            pattern = r"(^|\W)" + re.escape(symbol) + r"($|\W)"
            if re.search(pattern, combined):
                return iso_code
        return ""


class TemporalNormalizer:
    """Maps human financial fiscal periods to ISO 8601 calendar bounds (period_start, period_end)."""

    @staticmethod
    def normalize(temporal_str: str) -> Tuple[str, str]:
        """Convert a fiscal string to ISO date interval."""
        if not temporal_str or not temporal_str.strip():
            return "1970-01-01", "1970-01-01"

        raw = temporal_str.strip()
        text = raw.lower()

        # 1. Indian Multi-year Fiscal Span: e.g. FY 2021-22, FY 2021-2022, FY21-22
        fy_span_match = re.search(r"\b(?:fy|fiscal)\s*(?:20)?(\d{2})[-/](?:20)?(\d{2})\b", text)
        if fy_span_match:
            start_yy = int(fy_span_match.group(1))
            end_yy = int(fy_span_match.group(2))
            start_yr = 2000 + start_yy if start_yy < 50 else 1900 + start_yy
            end_yr = 2000 + end_yy if end_yy < 50 else 1900 + end_yy
            return f"{start_yr}-04-01", f"{end_yr}-03-31"

        # 2. Indian Fiscal Year Patterns: FY22, FY2022, Fiscal 2022
        fy_match = re.search(r"\b(?:fy|fiscal)\s*(?:20)?(\d{2})\b", text)
        if fy_match:
            yy = int(fy_match.group(1))
            end_year = 2000 + yy if yy < 50 else 1900 + yy
            start_year = end_year - 1

            if "q1" in text or "first quarter" in text:
                return f"{start_year}-04-01", f"{start_year}-06-30"
            elif "q2" in text or "second quarter" in text:
                return f"{start_year}-07-01", f"{start_year}-09-30"
            elif "q3" in text or "third quarter" in text:
                return f"{start_year}-10-01", f"{start_year}-12-31"
            elif "q4" in text or "fourth quarter" in text:
                return f"{end_year}-01-01", f"{end_year}-03-31"
            elif "nine months" in text:
                return f"{start_year}-04-01", f"{start_year}-12-31"
            elif "six months" in text or "half year" in text or "h1" in text:
                return f"{start_year}-04-01", f"{start_year}-09-30"

            return f"{start_year}-04-01", f"{end_year}-03-31"

        # 3. Explicit Partial Ended Periods (Checked before generic point-in-time)
        nine_mo_match = re.search(r"nine months ended (?:december|dec)\s*31,?\s*(\d{4})", text)
        if nine_mo_match:
            yr = int(nine_mo_match.group(1))
            return f"{yr}-04-01", f"{yr}-12-31"

        six_mo_match = re.search(r"six months ended (?:september|sep)\s*30,?\s*(\d{4})", text)
        if six_mo_match:
            yr = int(six_mo_match.group(1))
            return f"{yr}-04-01", f"{yr}-09-30"

        # 4. Calendar Year Patterns: CY2021, CY21, Calendar 2022
        cy_match = re.search(r"\b(?:cy|calendar)\s*(?:20)?(\d{2})\b", text)
        if cy_match:
            yy = int(cy_match.group(1))
            year = 2000 + yy if yy < 50 else 1900 + yy
            return f"{year}-01-01", f"{year}-12-31"

        # 5. Point-in-Time: e.g. "March 31, 2022" or "As of March 31, 2022"
        month_map = {
            "january": "01", "jan": "01",
            "february": "02", "feb": "02",
            "march": "03", "mar": "03",
            "april": "04", "apr": "04",
            "may": "05",
            "june": "06", "jun": "06",
            "july": "07", "jul": "07",
            "august": "08", "aug": "08",
            "september": "09", "sep": "09", "sept": "09",
            "october": "10", "oct": "10",
            "november": "11", "nov": "11",
            "december": "12", "dec": "12",
        }
        point_match = re.search(r"\b([a-zA-Z]+)\s+(\d{1,2}),?\s+(\d{4})\b", raw)
        if point_match:
            mon_str = point_match.group(1).lower()
            if mon_str in month_map:
                mm = month_map[mon_str]
                dd = int(point_match.group(2))
                yyyy = point_match.group(3)
                iso_date = f"{yyyy}-{mm}-{dd:02d}"
                return iso_date, iso_date

        # Fallback: Search for any 4-digit year
        year_match = re.search(r"\b(20\d{2}|19\d{2})\b", text)
        if year_match:
            y = year_match.group(1)
            return f"{y}-01-01", f"{y}-12-31"

        return "1970-01-01", "1970-01-01"
