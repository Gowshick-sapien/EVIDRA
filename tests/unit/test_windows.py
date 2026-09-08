"""
Unit tests for EvidenceWindowBuilder and unit extraction routines.
"""
from __future__ import annotations

import pytest

# pyrefly: ignore [missing-import]
from src.extraction.schemas import EvidenceChunk, EvidenceWindow
# pyrefly: ignore [missing-import]
from src.extraction.windows import (
    EvidenceWindowBuilder,
    extract_unit_and_currency,
    parse_table_headers,
)
# pyrefly: ignore [missing-import]
from src.pdf.parser import ExtractedBlock
# pyrefly: ignore [missing-import]
from src.pdf.topology import DocumentTopologyBuilder


def test_unit_and_currency_extraction():
    """Verify regex extraction of financial units and currency symbols."""
    assert extract_unit_and_currency("Consolidated Financial Statements (in Rs. Crores)") == ("crore", "INR")
    assert extract_unit_and_currency("Statement of Profit and Loss (Amount in Rs. Lakhs)") == ("lakh", "INR")
    assert extract_unit_and_currency("Segment Revenue (USD in Millions)") == ("million", "USD")
    assert extract_unit_and_currency("Rs. 8,142 Cr") == ("crore", "INR")
    assert extract_unit_and_currency("Total Shipments (in Thousands)") == ("thousand", "")
    assert extract_unit_and_currency("Normal narrative with no financial units") == ("", "")


def test_parse_table_headers():
    """Verify extraction of column headers from markdown table text."""
    table_text = (
        "| Particulars | Q4 FY24 | Q3 FY24 | FY24 | FY23 |\n"
        "|---|---|---|---|---|\n"
        "| Revenue from Operations | 2,142 | 2,050 | 8,142 | 7,225 |\n"
    )
    headers = parse_table_headers(table_text)
    assert headers == ["Particulars", "Q4 FY24", "Q3 FY24", "FY24", "FY23"]


def test_evidence_window_builder_table_context():
    """Verify that EvidenceWindowBuilder enriches a table chunk with inherited context."""
    # 1. Blocks
    blocks = [
        ExtractedBlock(
            page_number=1,
            block_type="heading",
            bounding_box=(50.0, 50.0, 400.0, 80.0),
            content="Section 4: Financial Review",
            font_size=18.0,
            is_bold=True,
        ),
        ExtractedBlock(
            page_number=1,
            block_type="text",
            bounding_box=(50.0, 100.0, 300.0, 115.0),
            content="(All amounts in Rs. Crores unless otherwise stated)",
            font_size=9.0,
        ),
        ExtractedBlock(
            page_number=1,
            block_type="text",
            bounding_box=(50.0, 130.0, 350.0, 145.0),
            content="Table 1: Revenue by Service Line",
            font_size=11.0,
            is_bold=True,
        ),
        ExtractedBlock(
            page_number=1,
            block_type="table",
            bounding_box=(50.0, 150.0, 500.0, 350.0),
            content=(
                "| Service Line | FY24 | FY23 |\n"
                "|---|---|---|\n"
                "| Express Parcel | 5,500 | 4,800 |\n"
                "| Part Truckload | 1,400 | 1,100 |\n"
            ),
        ),
    ]

    # 2. Chunks
    chunks = [
        EvidenceChunk.create(
            document_id="DOC-TEST",
            page_number=b.page_number,
            chunk_type=b.block_type if b.block_type in ("text", "table", "figure") else "text",
            bounding_box=list(b.bounding_box),
            content=b.content,
        )
        for b in blocks
    ]

    # 3. Build topology and windows
    topology = DocumentTopologyBuilder.build(blocks, document_id="DOC-TEST")
    windows = EvidenceWindowBuilder.build_windows(chunks, blocks, topology)

    assert len(windows) == 4
    table_win = windows[3]

    assert table_win.chunk_type == "table"
    assert table_win.stated_unit == "crore"
    assert table_win.stated_currency == "INR"
    assert "Financial Review" in table_win.section_title
    assert table_win.section_confidence >= 0.70
    assert table_win.column_headers == ["Service Line", "FY24", "FY23"]
    assert table_win.window_id.startswith("WIN-")
