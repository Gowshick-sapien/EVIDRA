"""
Unit tests for SchemaInductionEngine in EVIDRA 2.0 (Phase P0).
"""

import pytest

# pyrefly: ignore [missing-import]
from src.extraction.schemas import EvidenceWindow
# pyrefly: ignore [missing-import]
from src.extraction.schema_induction import (
    SchemaInductionEngine,
    DocumentSchema,
    MetricFamily,
    MetricSubtype,
)


def test_primary_entity_resolution_manifest():
    engine = SchemaInductionEngine()
    windows = [
        EvidenceWindow(
            window_id="w1",
            chunk_id="c1",
            document_id="doc1",
            page_number=1,
            chunk_type="text",
            bounding_box=[0.0, 0.0, 100.0, 100.0],
            content="Some report content",
            content_hash="h1",
        )
    ]
    # Trusted manifest entity
    schema = engine.induce_schema("doc1", windows, manifest_entity="Delhivery Limited")
    assert schema.primary_entity == "Delhivery Limited"

    # Generic manifest entity should be ignored and fell back
    schema_generic = engine.induce_schema("doc1", windows, manifest_entity="Reporting Entity")
    assert schema_generic.primary_entity == "Unknown Entity"


def test_primary_entity_resolution_from_content():
    engine = SchemaInductionEngine()
    windows = [
        EvidenceWindow(
            window_id="w1",
            chunk_id="c1",
            document_id="doc1",
            page_number=1,
            chunk_type="text",
            bounding_box=[0.0, 0.0, 100.0, 100.0],
            content="Annual Financial Report of Delhivery Limited for Fiscal Year 2024.",
            content_hash="h1",
            page_header="Delhivery Limited - Annual Report 2024",
        ),
        EvidenceWindow(
            window_id="w2",
            chunk_id="c2",
            document_id="doc1",
            page_number=2,
            chunk_type="text",
            bounding_box=[0.0, 0.0, 100.0, 100.0],
            content="Delhivery Limited is India's largest integrated logistics provider.",
            content_hash="h2",
            page_header="Delhivery Limited - Annual Report 2024",
        ),
    ]
    schema = engine.induce_schema("doc1", windows)
    assert schema.primary_entity == "Delhivery Limited"


def test_metric_taxonomies_induction():
    engine = SchemaInductionEngine()
    table_content = (
        "| Particulars | FY24 | FY23 |\n"
        "|---|---|---|\n"
        "| Revenue from Operations | 8,142 | 7,225 |\n"
        "| Other Income | 340 | 250 |\n"
        "| Freight and handling costs | 4,500 | 4,100 |\n"
        "| Employee benefit expense | 1,400 | 1,300 |\n"
        "| Adjusted EBITDA (1) | 450 | 120 |\n"
        "| Net Profit / (Loss) for the year | 100 | -150 |\n"
        "| Express Parcel shipment volumes (mn) | 740 | 663 |\n"
        "| 1. Borrowings | 500 | 600 |\n"
    )

    windows = [
        EvidenceWindow(
            window_id="w_tbl",
            chunk_id="c_tbl",
            document_id="doc1",
            page_number=5,
            chunk_type="table",
            bounding_box=[50.0, 100.0, 500.0, 400.0],
            content=table_content,
            content_hash="htbl",
            section_title="Financial Statements",
            section_confidence=0.85,
        )
    ]

    schema = engine.induce_schema("doc1", windows, manifest_entity="Delhivery Limited")
    assert schema.document_id == "doc1"
    assert schema.primary_entity == "Delhivery Limited"

    families = {f.family_name: f for f in schema.metric_families}
    assert "REVENUE" in families
    assert "EXPENSES" in families
    assert "PROFITABILITY" in families
    assert "VOLUME" in families
    assert "BALANCE_SHEET" in families

    # Verify REVENUE subtypes
    rev_subtypes = {s.subtype_name: s for s in families["REVENUE"].subtypes}
    assert "REVENUE_FROM_OPERATIONS" in rev_subtypes
    assert "Revenue from Operations" in rev_subtypes["REVENUE_FROM_OPERATIONS"].surface_variants

    # Verify PROFITABILITY subtypes (footnote marker stripped)
    prof_subtypes = {s.subtype_name: s for s in families["PROFITABILITY"].subtypes}
    assert "ADJUSTED_EBITDA" in prof_subtypes
    assert "Adjusted EBITDA (1)" in prof_subtypes["ADJUSTED_EBITDA"].surface_variants

    # Verify lookup via find_subtype
    lookup1 = schema.find_subtype("Revenue from Operations")
    assert lookup1 is not None
    assert lookup1.subtype_name == "REVENUE_FROM_OPERATIONS"

    lookup2 = schema.find_subtype("adjusted ebitda (1)")
    assert lookup2 is not None
    assert lookup2.subtype_name == "ADJUSTED_EBITDA"
