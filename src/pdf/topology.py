"""
Multi-signal layout hierarchy inference for EVIDRA 2.0.
Analyzes document layout, font metrics, spatial margins, and table proximity
to infer structural roles (section titles, table captions, headers, footers)
with explicit confidence scores rather than brittle single-threshold heuristics.
"""
from __future__ import annotations

import logging
import math
import re
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

# pyrefly: ignore [missing-import]
from src.pdf.parser import ExtractedBlock

logger = logging.getLogger(__name__)

CAPTION_PREFIXES = re.compile(
    r"^(?:table|statement of|notes? to|schedule|exhibit|figure|chart|consolidated statement)\b",
    re.IGNORECASE,
)
SECTION_PREFIXES = re.compile(
    r"^(?:section|part|item|chapter|schedule|\d+\.|\([a-z]\))\b",
    re.IGNORECASE,
)


PAGE_NUMBER_PATTERN = re.compile(
    r"^(?:page\s+)?\d+(?:\s*(?:of|/|-)\s*\d+)?$",
    re.IGNORECASE,
)


class StructuralRole(str, Enum):
    SECTION_TITLE = "SECTION_TITLE"
    TABLE_CAPTION = "TABLE_CAPTION"
    HEADER = "HEADER"
    FOOTER = "FOOTER"
    FOOTNOTE = "FOOTNOTE"
    BODY = "BODY"


class SectionNode(BaseModel):
    """Represents an inferred section heading and its spatial properties."""
    title: str
    title_bbox: tuple[float, float, float, float]
    font_size: float
    confidence: float
    page_number: int
    children_indices: list[int] = Field(default_factory=list)


class PageTopology(BaseModel):
    """Structural layout topology for a single document page."""
    page_number: int
    header_text: str = ""
    footer_text: str = ""
    sections: list[SectionNode] = Field(default_factory=list)
    table_captions: list[tuple[str, tuple[float, float, float, float]]] = Field(
        default_factory=list,
        description="List of (caption_text, bounding_box) for detected captions",
    )
    classified_roles: dict[int, tuple[str, float]] = Field(
        default_factory=dict,
        description="Map of block index on page to (StructuralRole, confidence)",
    )


class DocumentTopology(BaseModel):
    """Complete document layout topology across all pages."""
    document_id: str
    pages: dict[int, PageTopology] = Field(default_factory=dict)

    def get_section_for_block(
        self, page_number: int, block_bbox: tuple[float, float, float, float]
    ) -> tuple[str, float]:
        """
        Find the nearest active section title above the given bounding box on the page.
        Returns (section_title, confidence). If none found, returns ('', 0.0).
        """
        page_topo = self.pages.get(page_number)
        if not page_topo or not page_topo.sections:
            return "", 0.0

        by0 = block_bbox[1]
        active_sec = None
        min_dist = float("inf")

        for sec in page_topo.sections:
            sec_y1 = sec.title_bbox[3]
            if sec_y1 <= by0:
                dist = by0 - sec_y1
                if dist < min_dist:
                    min_dist = dist
                    active_sec = sec

        if active_sec:
            return active_sec.title, active_sec.confidence
        return "", 0.0

    def get_caption_for_table(
        self, page_number: int, table_bbox: tuple[float, float, float, float]
    ) -> str:
        """Find the nearest table caption immediately preceding a table bounding box."""
        page_topo = self.pages.get(page_number)
        if not page_topo or not page_topo.table_captions:
            return ""

        ty0 = table_bbox[1]
        best_caption = ""
        min_dist = 40.0  # Maximum 40 points above table

        for cap_text, cap_bbox in page_topo.table_captions:
            cy1 = cap_bbox[3]
            if 0 <= (ty0 - cy1) <= min_dist:
                min_dist = ty0 - cy1
                best_caption = cap_text

        return best_caption


class DocumentTopologyBuilder:
    """Infers structural hierarchy from a flat sequence of ExtractedBlocks."""

    @staticmethod
    def _compute_page_font_stats(blocks: list[ExtractedBlock]) -> tuple[float, float]:
        """Compute mean and standard deviation of font sizes on a page."""
        font_sizes = [b.font_size for b in blocks if b.block_type != "table" and b.font_size > 0]
        if not font_sizes:
            return 10.0, 1.0
        mean = sum(font_sizes) / len(font_sizes)
        variance = sum((s - mean) ** 2 for s in font_sizes) / max(1, len(font_sizes) - 1)
        std_dev = math.sqrt(variance)
        return mean, max(std_dev, 0.5)

    @classmethod
    def build(
        cls,
        blocks: list[ExtractedBlock],
        document_id: str = "",
        page_height: float = 792.0,
    ) -> DocumentTopology:
        """
        Construct a DocumentTopology from extracted blocks across all pages.
        Uses multi-signal inference: Z-score font size, font style flags,
        spatial margins, repetition frequency, whitespace, and table proximity.
        """
        # 1. Group blocks by page
        pages_dict: dict[int, list[tuple[int, ExtractedBlock]]] = {}
        for global_idx, block in enumerate(blocks):
            pages_dict.setdefault(block.page_number, []).append((global_idx, block))

        # 2. Count content occurrences across pages to identify repeating headers/footers
        text_page_counts: dict[str, set[int]] = {}
        for block in blocks:
            if block.block_type == "text" and len(block.content.strip()) < 120:
                norm_text = " ".join(block.content.strip().lower().split())
                if len(norm_text) > 5:
                    text_page_counts.setdefault(norm_text, set()).add(block.page_number)

        repeating_texts = {text for text, p_set in text_page_counts.items() if len(p_set) >= 3}

        topology = DocumentTopology(document_id=document_id)

        # 3. Classify layout for each page
        for page_num, page_items in sorted(pages_dict.items()):
            page_blocks = [b for _, b in page_items]
            mean_font, std_font = cls._compute_page_font_stats(page_blocks)

            table_bboxes = [b.bounding_box for b in page_blocks if b.block_type == "table"]

            page_topo = PageTopology(page_number=page_num)
            classified: dict[int, tuple[str, float]] = {}
            sections: list[SectionNode] = []

            for local_idx, (global_idx, block) in enumerate(page_items):
                if block.block_type == "table":
                    classified[local_idx] = (StructuralRole.BODY.value, 1.0)
                    continue

                content = block.content.strip()
                norm_content = " ".join(content.lower().split())
                bbox = block.bounding_box
                y0, y1 = bbox[1], bbox[3]

                # Calculate Z-score font size
                z_font = (block.font_size - mean_font) / std_font if std_font > 0 else 0.0

                # Multi-signal accumulator
                scores: dict[StructuralRole, float] = {role: 0.0 for role in StructuralRole}

                # --- HEADER Signals ---
                if y0 < page_height * 0.10:
                    scores[StructuralRole.HEADER] += 0.40
                if norm_content in repeating_texts and y0 < page_height * 0.15:
                    scores[StructuralRole.HEADER] += 0.45
                if PAGE_NUMBER_PATTERN.search(content) and y0 < page_height * 0.12:
                    scores[StructuralRole.HEADER] += 0.40

                # --- FOOTER Signals ---
                if y1 > page_height * 0.90:
                    scores[StructuralRole.FOOTER] += 0.40
                if norm_content in repeating_texts and y1 > page_height * 0.85:
                    scores[StructuralRole.FOOTER] += 0.45
                if PAGE_NUMBER_PATTERN.search(content) and y1 > page_height * 0.85:
                    scores[StructuralRole.FOOTER] += 0.40

                # --- TABLE CAPTION Signals ---
                for tx0, ty0, tx1, ty1 in table_bboxes:
                    # Within 30 points above a table
                    if 0 <= (ty0 - y1) <= 30.0:
                        scores[StructuralRole.TABLE_CAPTION] += 0.50
                        if CAPTION_PREFIXES.search(content):
                            scores[StructuralRole.TABLE_CAPTION] += 0.40
                        break

                # --- SECTION TITLE Signals ---
                if z_font >= 1.5:
                    scores[StructuralRole.SECTION_TITLE] += 0.45
                elif z_font >= 1.0:
                    scores[StructuralRole.SECTION_TITLE] += 0.25

                if block.is_bold:
                    scores[StructuralRole.SECTION_TITLE] += 0.25

                if SECTION_PREFIXES.search(content):
                    scores[StructuralRole.SECTION_TITLE] += 0.25

                if len(content) < 100 and "\n" not in content and z_font >= 0.5:
                    scores[StructuralRole.SECTION_TITLE] += 0.15

                # Disqualify section title if in header/footer area or too long
                if scores[StructuralRole.HEADER] >= 0.70 or scores[StructuralRole.FOOTER] >= 0.70:
                    scores[StructuralRole.SECTION_TITLE] = 0.0
                if len(content) > 180:
                    scores[StructuralRole.SECTION_TITLE] = 0.0

                # Determine best structural role
                best_role = StructuralRole.BODY
                best_score = 0.0

                for role, score in scores.items():
                    if score > best_score:
                        best_score = score
                        best_role = role

                confidence = max(0.2, min(1.0, best_score if best_score > 0 else 0.5))
                if best_score < 0.50:
                    best_role = StructuralRole.BODY
                    confidence = 0.80

                classified[local_idx] = (best_role.value, confidence)

                # Collect structural items
                if best_role == StructuralRole.SECTION_TITLE and confidence >= 0.55:
                    clean_title = re.sub(r"\s+", " ", content).strip()
                    sections.append(
                        SectionNode(
                            title=clean_title,
                            title_bbox=bbox,
                            font_size=block.font_size,
                            confidence=confidence,
                            page_number=page_num,
                        )
                    )
                elif best_role == StructuralRole.TABLE_CAPTION and confidence >= 0.50:
                    clean_caption = re.sub(r"\s+", " ", content).strip()
                    page_topo.table_captions.append((clean_caption, bbox))
                elif best_role == StructuralRole.HEADER and not page_topo.header_text:
                    page_topo.header_text = content
                elif best_role == StructuralRole.FOOTER and not page_topo.footer_text:
                    page_topo.footer_text = content

            page_topo.sections = sections
            page_topo.classified_roles = classified
            topology.pages[page_num] = page_topo

        return topology
