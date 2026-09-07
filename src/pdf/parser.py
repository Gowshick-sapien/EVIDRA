from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional
import pymupdf as fitz
import pdfplumber

# pyrefly: ignore [missing-import]
from src.pdf.tables import ExtractedTable, TableExtractor

logger = logging.getLogger(__name__)


@dataclass
class ExtractedBlock:
    """Represents a discrete text block, heading, or table extracted from a PDF page."""
    page_number: int
    block_type: Literal["text", "heading", "table", "figure"]
    bounding_box: tuple[float, float, float, float]  # (x0, y0, x1, y1)
    content: str
    font_size: float = 0.0
    font_name: str = ""
    is_bold: bool = False


class PDFParser:
    """Dual-engine PDF parser using PyMuPDF for layout text and pdfplumber for tables."""

    def __init__(self, table_extractor: Optional[TableExtractor] = None):
        self.table_extractor = table_extractor or TableExtractor()

    @staticmethod
    def _is_inside_table(
        block_bbox: tuple[float, float, float, float],
        table_bboxes: list[tuple[float, float, float, float]],
        margin: float = 3.0,
    ) -> bool:
        """Determine if a text block's center falls inside any table bounding box."""
        bx0, by0, bx1, by1 = block_bbox
        cx = (bx0 + bx1) / 2.0
        cy = (by0 + by1) / 2.0

        for tx0, ty0, tx1, ty1 in table_bboxes:
            if (tx0 - margin <= cx <= tx1 + margin) and (ty0 - margin <= cy <= ty1 + margin):
                return True
        return False

    def parse_page(
        self,
        fitz_page: fitz.Page,
        plumber_page: Optional[pdfplumber.page.Page],
        page_number: int,
    ) -> list[ExtractedBlock]:
        """Parse a single page into non-duplicated text and table blocks."""
        page_blocks: list[ExtractedBlock] = []
        table_bboxes: list[tuple[float, float, float, float]] = []

        # 1. Extract tables via pdfplumber
        if plumber_page is not None:
            try:
                extracted_tables = self.table_extractor.extract_tables_from_page(plumber_page, page_number)
                for tbl in extracted_tables:
                    if not tbl.markdown_representation.strip():
                        continue
                    table_bboxes.append(tbl.bounding_box)
                    page_blocks.append(
                        ExtractedBlock(
                            page_number=page_number,
                            block_type="table",
                            bounding_box=tbl.bounding_box,
                            content=tbl.markdown_representation,
                        )
                    )
            except Exception as e:
                logger.warning(f"Table extraction failed on page {page_number}: {e}")

        # 2. Extract text blocks via PyMuPDF dict extraction
        try:
            page_dict = fitz_page.get_text("dict")
            for block in page_dict.get("blocks", []):
                if block.get("type") != 0:  # 0 is text block, 1 is image
                    continue

                bbox = tuple(block["bbox"])  # (x0, y0, x1, y1)
                
                # Mask out text falling inside table boundaries
                if self._is_inside_table(bbox, table_bboxes):
                    continue

                # Accumulate text spans and analyze font metadata
                block_lines = []
                max_font_size = 0.0
                font_names = []
                is_bold = False

                for line in block.get("lines", []):
                    line_spans = []
                    for span in line.get("spans", []):
                        span_text = span.get("text", "")
                        if span_text:
                            line_spans.append(span_text)
                        size = span.get("size", 0.0)
                        if size > max_font_size:
                            max_font_size = size
                        font_names.append(span.get("font", ""))
                        if "bold" in span.get("font", "").lower() or span.get("flags", 0) & 2 != 0:
                            is_bold = True
                    
                    joined_line = " ".join(line_spans).strip()
                    if joined_line:
                        block_lines.append(joined_line)

                content = "\n".join(block_lines).strip()
                if not content:
                    continue

                # Classify block type based on font size and weight
                block_type: Literal["text", "heading", "table", "figure"] = "text"
                if max_font_size >= 12.0 and is_bold:
                    block_type = "heading"
                elif max_font_size >= 14.0:
                    block_type = "heading"

                primary_font = font_names[0] if font_names else ""
                page_blocks.append(
                    ExtractedBlock(
                        page_number=page_number,
                        block_type=block_type,
                        bounding_box=bbox,
                        content=content,
                        font_size=round(max_font_size, 2),
                        font_name=primary_font,
                        is_bold=is_bold,
                    )
                )
        except Exception as e:
            logger.warning(f"Text extraction failed on page {page_number}: {e}")

        # 3. Sort blocks in visual reading order (top to bottom, left to right)
        page_blocks.sort(key=lambda b: (b.bounding_box[1], b.bounding_box[0]))
        return page_blocks

    def parse_document(self, pdf_path: Path | str) -> list[ExtractedBlock]:
        """Parse full PDF document into sequential, deduplicated ExtractedBlock instances."""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF document not found: {path}")

        all_blocks: list[ExtractedBlock] = []
        try:
            doc = fitz.open(str(path))
        except Exception as e:
            logger.warning(f"PyMuPDF failed to open '{path}': {e}")
            return []

        try:
            with pdfplumber.open(str(path)) as plumber_pdf:
                for page_idx in range(len(doc)):
                    page_num = page_idx + 1
                    fitz_page = doc[page_idx]
                    plumber_page = plumber_page = plumber_pdf.pages[page_idx] if page_idx < len(plumber_pdf.pages) else None
                    blocks = self.parse_page(fitz_page, plumber_page, page_num)
                    all_blocks.extend(blocks)
        except Exception as e:
            # Fallback to pure fitz parsing if pdfplumber fails
            logger.warning(f"pdfplumber failed on '{path}': {e}. Falling back to PyMuPDF only.")
            for page_idx in range(len(doc)):
                page_num = page_idx + 1
                fitz_page = doc[page_idx]
                blocks = self.parse_page(fitz_page, None, page_num)
                all_blocks.extend(blocks)
        finally:
            doc.close()

        return all_blocks
