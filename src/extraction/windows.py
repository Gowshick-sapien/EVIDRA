"""
Context-enriched Evidence Window construction for EVIDRA 2.0.
Wraps raw EvidenceChunks in structural envelopes carrying layout context,
section hierarchy, table headers, stated units, and currency definitions.
"""
from __future__ import annotations

import logging
import re
from typing import Optional

# pyrefly: ignore [missing-import]
from src.extraction.schemas import EvidenceChunk, EvidenceWindow
# pyrefly: ignore [missing-import]
from src.pdf.parser import ExtractedBlock
# pyrefly: ignore [missing-import]
from src.pdf.topology import DocumentTopology, StructuralRole

logger = logging.getLogger(__name__)

UNIT_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"(?:in\s+)?(?:rs\.?|₹|inr)\s*(?:in\s+)?(?:crores?|cr\.?)", re.IGNORECASE), "crore", "INR"),
    (re.compile(r"(?:in\s+)?(?:rs\.?|₹|inr)\s*(?:in\s+)?(?:lakhs?|lacs?)", re.IGNORECASE), "lakh", "INR"),
    (re.compile(r"(?:in\s+)?(?:rs\.?|₹|inr)\s*(?:in\s+)?(?:millions?|mn\.?)", re.IGNORECASE), "million", "INR"),
    (re.compile(r"(?:in\s+)?(?:usd|\$)\s*(?:in\s+)?(?:millions?|mn\.?)", re.IGNORECASE), "million", "USD"),
    (re.compile(r"(?:in\s+)?(?:usd|\$)\s*(?:in\s+)?(?:billions?|bn\.?)", re.IGNORECASE), "billion", "USD"),
    (re.compile(r"\b(?:rs\.?|₹|inr)\b", re.IGNORECASE), "", "INR"),
    (re.compile(r"\b(?:\$|usd)\b", re.IGNORECASE), "", "USD"),
    (re.compile(r"\b(?:crores?|cr\.?)\b", re.IGNORECASE), "crore", "INR"),
    (re.compile(r"\b(?:lakhs?|lacs?)\b", re.IGNORECASE), "lakh", "INR"),
    (re.compile(r"\b(?:millions?|mn\.?)\b", re.IGNORECASE), "million", ""),
    (re.compile(r"\b(?:billions?|bn\.?)\b", re.IGNORECASE), "billion", ""),
    (re.compile(r"\b(?:thousands?|k)\b", re.IGNORECASE), "thousand", ""),
]


def extract_unit_and_currency(text: str) -> tuple[str, str]:
    """
    Extract stated financial unit (e.g. crore, lakh, million) and currency (INR, USD)
    from a text span such as a table caption, header, or note.
    """
    if not text:
        return "", ""

    unit = ""
    currency = ""

    for pattern, u, c in UNIT_PATTERNS:
        if pattern.search(text):
            if not unit and u:
                unit = u
            if not currency and c:
                currency = c
            if unit and currency:
                break

    return unit, currency


def parse_table_headers(table_content: str) -> list[str]:
    """Extract column headers from markdown-formatted table text."""
    if not table_content:
        return []

    lines = [line.strip() for line in table_content.splitlines() if line.strip()]
    if not lines:
        return []

    # First line of markdown table typically: | Col1 | Col2 | Col3 |
    first_line = lines[0]
    if "|" in first_line:
        cols = [col.strip() for col in first_line.split("|") if col.strip()]
        # Ignore separator rows like |---|---|
        if cols and not all(re.match(r"^[-:]+$", c) for c in cols):
            return cols

    return []


class EvidenceWindowBuilder:
    """Constructs context-enriched EvidenceWindow envelopes for evidence chunks."""

    @classmethod
    def build_windows(
        cls,
        chunks: list[EvidenceChunk],
        blocks: list[ExtractedBlock],
        topology: DocumentTopology,
    ) -> list[EvidenceWindow]:
        """
        Wrap each EvidenceChunk in an EvidenceWindow binding layout hierarchy,
        section titles, table captions, units, and column metadata.
        """
        windows: list[EvidenceWindow] = []

        # Index blocks by page for proximity lookups
        page_blocks: dict[int, list[ExtractedBlock]] = {}
        for b in blocks:
            page_blocks.setdefault(b.page_number, []).append(b)

        for chunk in chunks:
            bbox = tuple(chunk.bounding_box)
            page_num = chunk.page_number

            # 1. Resolve section title with confidence threshold (>= 0.70)
            sec_title, sec_conf = topology.get_section_for_block(page_num, bbox)
            effective_section = sec_title if sec_conf >= 0.70 else ""

            # 2. Resolve page header
            page_topo = topology.pages.get(page_num)
            page_header = page_topo.header_text if page_topo else ""

            # 3. Context for Tables vs Text
            table_caption = ""
            stated_unit = ""
            stated_currency = ""
            column_headers: list[str] = []
            row_context = ""
            footnotes: list[str] = []

            if chunk.chunk_type == "table":
                # Find caption
                table_caption = topology.get_caption_for_table(page_num, bbox)

                # Parse column headers
                column_headers = parse_table_headers(chunk.content)

                # Find stated units from caption, column headers, or table content
                u_cap, c_cap = extract_unit_and_currency(table_caption)
                u_col, c_col = extract_unit_and_currency(" ".join(column_headers))
                u_body, c_body = extract_unit_and_currency(chunk.content[:250])

                stated_unit = u_cap or u_col or u_body
                stated_currency = c_cap or c_col or c_body

                # Check preceding 3 blocks on the page if unit still missing
                if not stated_unit or not stated_currency:
                    blocks_on_page = page_blocks.get(page_num, [])
                    preceding = [
                        b for b in blocks_on_page
                        if b.bounding_box[3] <= bbox[1] and b.block_type == "text"
                    ]
                    preceding.sort(key=lambda b: b.bounding_box[3], reverse=True)
                    for pb in preceding[:3]:
                        pu, pc = extract_unit_and_currency(pb.content)
                        if not stated_unit and pu:
                            stated_unit = pu
                        if not stated_currency and pc:
                            stated_currency = pc
                        if stated_unit and stated_currency:
                            break

                # Check for footnotes immediately below the table (within 50 points)
                blocks_on_page = page_blocks.get(page_num, [])
                succ = [
                    b for b in blocks_on_page
                    if 0 <= (b.bounding_box[1] - bbox[3]) <= 50.0 and b.block_type == "text"
                ]
                for sb in succ:
                    clean_note = sb.content.strip()
                    if re.match(r"^(?:note|\*|\d+\.|\(i\)|source:)", clean_note, re.IGNORECASE):
                        footnotes.append(clean_note)
            else:
                # Text block unit check
                stated_unit, stated_currency = extract_unit_and_currency(chunk.content)

            window = EvidenceWindow.from_chunk(
                chunk=chunk,
                section_title=effective_section,
                section_confidence=sec_conf,
                table_caption=table_caption,
                stated_unit=stated_unit,
                stated_currency=stated_currency,
                column_headers=column_headers,
                row_context=row_context,
                page_header=page_header,
                footnotes=footnotes,
            )
            windows.append(window)

        return windows
