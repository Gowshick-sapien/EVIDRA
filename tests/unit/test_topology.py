"""
Unit tests for DocumentTopologyBuilder and multi-signal layout classification.
"""
from __future__ import annotations

import pytest

# pyrefly: ignore [missing-import]
from src.pdf.parser import ExtractedBlock
# pyrefly: ignore [missing-import]
from src.pdf.topology import (
    DocumentTopologyBuilder,
    StructuralRole,
)


def test_section_title_detection():
    """Verify that larger font size + bold + section prefix yields SECTION_TITLE."""
    blocks = [
        ExtractedBlock(
            page_number=1,
            block_type="text",
            bounding_box=(50.0, 30.0, 500.0, 45.0),
            content="Annual Report 2024",
            font_size=9.0,
        ),
        ExtractedBlock(
            page_number=1,
            block_type="heading",
            bounding_box=(50.0, 100.0, 400.0, 130.0),
            content="Section 2: Financial Performance",
            font_size=18.0,
            is_bold=True,
        ),
        ExtractedBlock(
            page_number=1,
            block_type="text",
            bounding_box=(50.0, 150.0, 500.0, 200.0),
            content="The company delivered strong operational results with increased volumes.",
            font_size=10.0,
        ),
        ExtractedBlock(
            page_number=1,
            block_type="text",
            bounding_box=(50.0, 220.0, 500.0, 270.0),
            content="Revenue grew by 20% across all customer segments during the year.",
            font_size=10.0,
        ),
    ]

    topology = DocumentTopologyBuilder.build(blocks, document_id="DOC-001")
    assert 1 in topology.pages
    page1 = topology.pages[1]

    # Section title should be detected
    assert len(page1.sections) == 1
    sec = page1.sections[0]
    assert "Financial Performance" in sec.title
    assert sec.confidence >= 0.60

    # Query section for body block at y0=150
    title, conf = topology.get_section_for_block(1, (50.0, 150.0, 500.0, 200.0))
    assert "Financial Performance" in title
    assert conf >= 0.60


def test_header_and_footer_repetition():
    """Verify that repeating text across 3+ pages at page margins is classified as header/footer."""
    blocks = []
    for page in range(1, 5):
        # Top header
        blocks.append(
            ExtractedBlock(
                page_number=page,
                block_type="text",
                bounding_box=(50.0, 20.0, 500.0, 35.0),
                content="Delhivery Limited - Corporate Overview",
                font_size=8.0,
            )
        )
        # Body
        blocks.append(
            ExtractedBlock(
                page_number=page,
                block_type="text",
                bounding_box=(50.0, 150.0, 500.0, 250.0),
                content=f"Unique body content for page {page} with financial disclosures.",
                font_size=10.0,
            )
        )
        # Footer
        blocks.append(
            ExtractedBlock(
                page_number=page,
                block_type="text",
                bounding_box=(50.0, 750.0, 500.0, 765.0),
                content="Page " + str(page) + " of 100",
                font_size=8.0,
            )
        )

    topology = DocumentTopologyBuilder.build(blocks, document_id="DOC-REP")
    assert len(topology.pages) == 4

    for page in range(1, 5):
        page_topo = topology.pages[page]
        assert "Delhivery Limited" in page_topo.header_text
        assert "Page " in page_topo.footer_text


def test_table_caption_detection():
    """Verify that text blocks immediately above table bounding box are identified as captions."""
    blocks = [
        ExtractedBlock(
            page_number=1,
            block_type="text",
            bounding_box=(50.0, 180.0, 450.0, 198.0),
            content="Statement of Consolidated Profit and Loss",
            font_size=11.0,
            is_bold=True,
        ),
        ExtractedBlock(
            page_number=1,
            block_type="table",
            bounding_box=(50.0, 205.0, 500.0, 450.0),
            content="| Particulars | FY24 | FY23 |\n| Revenue | 8,142 | 7,225 |",
        ),
    ]

    topology = DocumentTopologyBuilder.build(blocks, document_id="DOC-TBL")
    page1 = topology.pages[1]

    caption = topology.get_caption_for_table(1, (50.0, 205.0, 500.0, 450.0))
    assert "Statement of Consolidated Profit and Loss" in caption
