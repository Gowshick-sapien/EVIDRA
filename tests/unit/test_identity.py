"""
Unit tests for Fact Identity Signature and Measurement Semantics (REQ-ID-RES-01).
"""
import pytest
from src.matching.identity import (
    FactIdentityBuilder,
    FactIdentitySignature,
    MeasurementClassifier,
    MeasurementType,
    normalize_canonical_entity,
)
from src.extraction.schema_induction import (
    DocumentSchema,
    MetricFamily,
    MetricSubtype,
)


def test_measurement_classifier_rate_of_change():
    """Verify classification of growth rates, YoY, and QoQ metrics."""
    assert MeasurementClassifier.classify("+29.8%", "Revenue Growth", "%", "Revenue grew by +29.8% YoY") == MeasurementType.RATE_OF_CHANGE
    assert MeasurementClassifier.classify("18.5%", "YoY Growth", "%", "Total shipments grew 18.5% YoY") == MeasurementType.RATE_OF_CHANGE
    assert MeasurementClassifier.classify("-5.2%", "EBITDA growth", "%", "declined by 5.2% QoQ") == MeasurementType.RATE_OF_CHANGE
    assert MeasurementClassifier.classify("12%", "CAGR", "%", "5-year CAGR of 12%") == MeasurementType.RATE_OF_CHANGE


def test_measurement_classifier_percentage_margin():
    """Verify classification of margins, ratios expressed as %, and returns."""
    assert MeasurementClassifier.classify("12.5%", "EBITDA Margin", "%", "EBITDA margin reached 12.5%") == MeasurementType.PERCENTAGE
    assert MeasurementClassifier.classify("4.2%", "PAT Margin", "%", "Profit after tax margin of 4.2%") == MeasurementType.PERCENTAGE
    assert MeasurementClassifier.classify("15.0%", "Return on Equity", "%", "ROE of 15.0%") == MeasurementType.PERCENTAGE
    assert MeasurementClassifier.classify("65%", "Market Share", "%", "Express parcel market share is 65%") == MeasurementType.PERCENTAGE


def test_measurement_classifier_ratio():
    """Verify classification of financial multiples and coverage ratios."""
    assert MeasurementClassifier.classify("1.4x", "Debt to Equity", "x", "Debt-to-equity ratio of 1.4x") == MeasurementType.RATIO
    assert MeasurementClassifier.classify("3.5", "EV/EBITDA", "multiple", "Trading at EV/EBITDA multiple of 3.5") == MeasurementType.RATIO
    assert MeasurementClassifier.classify("2.1x", "Interest Coverage", "times", "Interest coverage ratio 2.1x") == MeasurementType.RATIO


def test_measurement_classifier_absolute_value():
    """Verify classification of monetary amounts and physical volume counts."""
    assert MeasurementClassifier.classify("8,142 Cr", "Revenue", "Crore", "Revenue from operations was ₹8,142 Cr") == MeasurementType.ABSOLUTE_VALUE
    assert MeasurementClassifier.classify("$120M", "Net Income", "USD", "Net income of $120M") == MeasurementType.ABSOLUTE_VALUE
    assert MeasurementClassifier.classify("15,000", "Pincodes Covered", "", "Delhivery covers 15,000 pincodes") == MeasurementType.ABSOLUTE_VALUE
    assert MeasurementClassifier.classify("1,200", "Express Centers", "", "Operates 1,200 express delivery centers") == MeasurementType.ABSOLUTE_VALUE


def test_normalize_canonical_entity():
    """Verify legal corporate entity resolution and generic placeholder rejection."""
    assert normalize_canonical_entity("Delhivery Limited") == "Delhivery Limited"
    assert normalize_canonical_entity("Delhivery Ltd.") == "Delhivery Ltd"
    assert normalize_canonical_entity("For Delhivery Limited") == "Delhivery Limited"
    
    # Generic placeholders fall back to document schema or Unknown
    assert normalize_canonical_entity("Reporting Entity", "Delhivery Limited") == "Delhivery Limited"
    assert normalize_canonical_entity("the Company", "Delhivery Limited") == "Delhivery Limited"
    assert normalize_canonical_entity("Management") == "Unknown Corporate Entity"


def test_fact_identity_builder_with_schema():
    """Verify end-to-end FactIdentitySignature assembly with induced schema binding."""
    schema = DocumentSchema(
        document_id="DOC-01",
        primary_entity="Delhivery Limited",
        metric_families=[
            MetricFamily(
                family_name="REVENUE",
                subtypes=[
                    MetricSubtype(
                        subtype_name="OPERATING_REVENUE",
                        surface_variants=["Revenue from Operations", "Revenue from operations"],
                    )
                ],
            )
        ],
    )

    obs = {
        "entity": "Delhivery Limited",
        "attribute": "Revenue from Operations",
        "raw_value": "8,142 Cr",
        "unit": "Crore",
        "statement": "Revenue from Operations was Rs. 8,142 Crores in FY24.",
    }

    sig = FactIdentityBuilder.build(
        fact_id="FCT-REV01",
        observation=obs,
        period_start="2023-04-01",
        period_end="2024-03-31",
        schema=schema,
        context={"organizational_scope": "CONSOLIDATED", "accounting_basis": "IND_AS"},
    )

    assert isinstance(sig, FactIdentitySignature)
    assert sig.fact_id == "FCT-REV01"
    assert sig.entity_canonical == "Delhivery Limited"
    assert sig.metric_family == "REVENUE"
    assert sig.metric_subtype == "OPERATING_REVENUE"
    assert sig.measurement_type == MeasurementType.ABSOLUTE_VALUE
    assert sig.period_start == "2023-04-01"
    assert sig.period_end == "2024-03-31"
    assert sig.scope == "CONSOLIDATED"
    assert sig.basis == "IND_AS"


def test_fact_identity_builder_blocks_measurement_conflation():
    """Verify that absolute revenue and revenue growth rate receive distinct MeasurementTypes."""
    schema = DocumentSchema(document_id="DOC-01", primary_entity="Delhivery Limited")

    obs_abs = {
        "entity": "Delhivery Limited",
        "attribute": "Revenue from Operations",
        "raw_value": "₹8,142 Cr",
        "unit": "Crore",
        "statement": "Revenue from Operations: Rs. 8,142 Cr",
    }
    obs_rate = {
        "entity": "Delhivery Limited",
        "attribute": "Revenue Growth",
        "raw_value": "+29.8%",
        "unit": "%",
        "statement": "Revenue grew by +29.8% YoY",
    }

    sig_abs = FactIdentityBuilder.build("FCT-01", obs_abs, "2023-04-01", "2024-03-31", schema)
    sig_rate = FactIdentityBuilder.build("FCT-02", obs_rate, "2023-04-01", "2024-03-31", schema)

    assert sig_abs.measurement_type == MeasurementType.ABSOLUTE_VALUE
    assert sig_rate.measurement_type == MeasurementType.RATE_OF_CHANGE
    assert sig_abs.measurement_type != sig_rate.measurement_type
