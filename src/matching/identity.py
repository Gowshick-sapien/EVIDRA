"""
Fact Identity Signature and Measurement Semantics for EVIDRA 2.0 (Phase P1).

Defines structured semantic identity signatures with explicit dimensional typing
to prevent cross-dimensional fact conflation and ungrounded comparisons.
"""

from __future__ import annotations

import re
import uuid
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field

# pyrefly: ignore [missing-import]
from src.extraction.schema_induction import (
    CORPORATE_ENTITY_PATTERNS,
    FAMILY_KEYWORD_MAP,
    GENERIC_ENTITIES,
    DocumentSchema,
)


class MeasurementType(str, Enum):
    """Dimensional classification of a numerical financial or operational fact."""
    ABSOLUTE_VALUE = "ABSOLUTE_VALUE"   # Currency amounts (INR 8,142 Cr), counts (15,000 pincodes)
    PERCENTAGE = "PERCENTAGE"           # Margins, proportions (12.5% EBITDA Margin)
    RATE_OF_CHANGE = "RATE_OF_CHANGE"   # Growth rates, YoY, QoQ changes (+29.8% YoY)
    RATIO = "RATIO"                     # Multiples, coverage ratios (1.4x Debt-to-Equity)
    UNKNOWN = "UNKNOWN"


class FactIdentitySignature(BaseModel):
    """
    Structured semantic identity of a verified financial fact candidate.
    
    Two facts may only be directly compared if their identities match across:
    entity_canonical, metric_family, metric_subtype, and measurement_type.
    """
    identity_id: str = Field(description="Deterministic identifier: ID-{fact_id[4:]}")
    fact_id: str = Field(description="Foreign key referencing fact_candidates")
    entity_canonical: str = Field(description="Resolved legal corporate entity")
    metric_family: str = Field(description="High-level category (e.g., REVENUE, PROFITABILITY)")
    metric_subtype: str = Field(description="Specific line-item variant (e.g., OPERATING_REVENUE)")
    measurement_type: MeasurementType = Field(description="Dimensional typing (ABSOLUTE, PERCENTAGE, etc.)")
    surface_metric: str = Field(description="Verbatim extracted metric attribute string")
    period_start: str = Field(description="ISO 8601 start date YYYY-MM-DD")
    period_end: str = Field(description="ISO 8601 end date YYYY-MM-DD")
    scope: str = Field(default="UNKNOWN", description="CONSOLIDATED, STANDALONE, or UNKNOWN")
    basis: str = Field(default="UNKNOWN", description="IND_AS, GAAP, NON_GAAP, or UNKNOWN")
    definition: str = Field(default="", description="Qualifying footnotes or definition strings")
    geography: str = Field(default="", description="Geographic jurisdiction or segment")
    source_type: str = Field(default="", description="ANNUAL_REPORT, PRESENTATION, PROSPECTUS")


class MeasurementClassifier:
    """
    Deterministic rule-based classifier for numerical measurement types.
    Strictly separates growth rates from percentage margins and absolute currency amounts.
    """

    RATE_PATTERNS = [
        re.compile(r"\b(?:yoy|qoq|mom|growth|cagr|annualized|rate\s+of\s+change)\b", re.I),
        re.compile(r"\b(?:increased|decreased|grew|declined|surge|drop)\s+by\b", re.I),
        re.compile(r"[-+]\s*\d+(?:\.\d+)?\s*%", re.I),
        re.compile(r"\b\d+(?:\.\d+)?%\s*(?:growth|increase|decrease|decline|yoy|qoq|cagr)\b", re.I),
    ]

    RATIO_PATTERNS = [
        re.compile(r"\b\d+(?:\.\d+)?\s*x\b", re.I),
        re.compile(r"\b(?:debt[- ]to[- ]equity|current\s+ratio|quick\s+ratio|multiple|times|coverage\s+ratio)\b", re.I),
    ]

    PERCENT_PATTERNS = [
        re.compile(r"\bmargin\b", re.I),
        re.compile(r"\b(?:percent|percentage|share|proportion|yield|return\s+on|roa|roe|roce)\b", re.I),
        re.compile(r"%", re.I),
    ]

    ABSOLUTE_INDICATORS = [
        "rs", "rs.", "inr", "usd", "eur", "gbp", "$", "₹", "€", "£",
        "crore", "crores", "cr", "lakh", "lakhs", "lac", "lacs",
        "million", "millions", "mn", "billion", "billions", "bn", "thousand", "thousands",
        "shipment", "shipments", "parcel", "parcels", "package", "order", "orders",
        "pincode", "pincodes", "pin codes", "center", "centers", "gateway", "gateways",
        "vehicle", "vehicles", "fleet", "client", "clients", "customer", "customers",
    ]

    @classmethod
    def classify(
        cls,
        raw_value: str,
        attribute: str,
        unit: str = "",
        statement: str = "",
    ) -> MeasurementType:
        """Deterministically determine the MeasurementType from observation context."""
        context = f"{raw_value} {attribute} {unit} {statement}".lower()

        # 1. Rate of Change takes highest precedence (e.g. +29.8% YoY or Revenue Growth: 15%)
        for pattern in cls.RATE_PATTERNS:
            if pattern.search(context):
                return MeasurementType.RATE_OF_CHANGE

        # 2. Ratio takes second precedence (e.g. 1.4x or Debt-to-Equity Ratio)
        for pattern in cls.RATIO_PATTERNS:
            if pattern.search(context):
                return MeasurementType.RATIO

        # 3. Percentage / Margin (e.g. 12.5% EBITDA Margin)
        for pattern in cls.PERCENT_PATTERNS:
            if pattern.search(context):
                return MeasurementType.PERCENTAGE

        # 4. Absolute Value default for monetary, volume, or count items
        for indicator in cls.ABSOLUTE_INDICATORS:
            pattern = r"(?:\b|\W)" + re.escape(indicator) + r"(?:\b|\W)"
            if re.search(pattern, context):
                return MeasurementType.ABSOLUTE_VALUE

        # Default fallback
        return MeasurementType.ABSOLUTE_VALUE


def normalize_canonical_entity(
    entity: str,
    schema_primary_entity: Optional[str] = None,
) -> str:
    """Resolve raw entity strings to canonical corporate identity."""
    clean = str(entity or "").strip()
    if clean.lower() in GENERIC_ENTITIES or not clean:
        if schema_primary_entity and schema_primary_entity.lower() not in GENERIC_ENTITIES:
            return schema_primary_entity.strip()
        return "Unknown Corporate Entity"

    # Match corporate suffixes
    for pattern in CORPORATE_ENTITY_PATTERNS:
        match = pattern.search(clean)
        if match:
            cand = match.group(1).strip()
            cand = re.sub(r"^(?:For|To|By|From|In|Of)\s+", "", cand, flags=re.I)
            if cand.lower() not in GENERIC_ENTITIES:
                return cand

    # Strip punctuation and common legal suffixes for matching consistency
    sub_clean = re.sub(r"[^\w\s]", " ", clean)
    sub_clean = re.sub(r"\b(limited|ltd|corporation|corp|incorporated|inc|llc|holdings)\b", "", sub_clean, flags=re.I)
    sub_clean = " ".join(sub_clean.split())
    if sub_clean and sub_clean.lower() not in GENERIC_ENTITIES:
        return sub_clean.title()

    if schema_primary_entity and schema_primary_entity.lower() not in GENERIC_ENTITIES:
        return schema_primary_entity.strip()

    return clean or "Unknown Corporate Entity"


class FactIdentityBuilder:
    """Constructs FactIdentitySignatures for verified fact candidates."""

    @classmethod
    def build(
        cls,
        fact_id: str,
        observation: dict[str, Any],
        period_start: str,
        period_end: str,
        schema: Optional[DocumentSchema] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> FactIdentitySignature:
        """Assemble structured FactIdentitySignature from candidate components."""
        entity_raw = observation.get("entity", "")
        attr_raw = observation.get("attribute", "")
        raw_val = observation.get("raw_value", "")
        unit = observation.get("unit", "")
        statement = observation.get("statement", "")

        primary_entity = schema.primary_entity if schema else None
        entity_canonical = normalize_canonical_entity(entity_raw, primary_entity)

        # 1. Measurement Classification
        measurement_type = MeasurementClassifier.classify(
            raw_value=raw_val,
            attribute=attr_raw,
            unit=unit,
            statement=statement,
        )

        # 2. Schema-derived Metric Family and Subtype
        metric_family = "OPERATIONAL_METRICS"
        metric_subtype = ""

        if schema:
            matched_subtype = schema.find_subtype(attr_raw)
            if matched_subtype:
                metric_subtype = matched_subtype.subtype_name
                # Find family containing this subtype
                for fam in schema.metric_families:
                    for sub in fam.subtypes:
                        if sub.subtype_name == metric_subtype:
                            metric_family = fam.family_name
                            break

        if not metric_family or metric_family == "OPERATIONAL_METRICS":
            # Keyword fallback for family
            lower_attr = f"{attr_raw} {statement}".lower()
            for fam_name, keywords in FAMILY_KEYWORD_MAP.items():
                for kw in keywords:
                    if kw in lower_attr:
                        metric_family = fam_name
                        break
                if metric_family != "OPERATIONAL_METRICS":
                    break

        if not metric_subtype:
            slug = re.sub(r"[^A-Za-z0-9]+", "_", attr_raw).strip("_").upper()
            common_aliases = {
                "REVENUE_FROM_OPERATIONS": "OPERATING_REVENUE",
                "INCOME_FROM_OPERATIONS": "OPERATING_REVENUE",
                "OPERATING_REVENUE": "OPERATING_REVENUE",
                "OPERATING_INCOME": "OPERATING_PROFIT",
                "OPERATING_PROFIT": "OPERATING_PROFIT",
                "PROFIT_AFTER_TAX": "PAT",
                "PROFIT_BEFORE_TAX": "PBT",
            }
            metric_subtype = common_aliases.get(slug, slug or "GENERAL_METRIC")

        # 3. Context Fields
        ctx = context or {}
        scope = ctx.get("organizational_scope", "UNKNOWN") or "UNKNOWN"
        basis = ctx.get("accounting_basis", "UNKNOWN") or "UNKNOWN"
        source_type = ctx.get("filing_type", "") or ""

        identity_id = f"ID-{fact_id[4:] if fact_id.startswith('FCT-') else fact_id}"

        return FactIdentitySignature(
            identity_id=identity_id,
            fact_id=fact_id,
            entity_canonical=entity_canonical,
            metric_family=metric_family,
            metric_subtype=metric_subtype,
            measurement_type=measurement_type,
            surface_metric=attr_raw,
            period_start=period_start,
            period_end=period_end,
            scope=scope,
            basis=basis,
            definition="",
            geography="",
            source_type=source_type,
        )
