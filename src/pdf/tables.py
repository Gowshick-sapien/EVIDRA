from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
import pdfplumber


@dataclass(frozen=True)
class TableCell:
    """Represents an individual table cell with spatial coordinates."""
    row_index: int
    col_index: int
    text: str
    bounding_box: tuple[float, float, float, float]  # (x0, top, x1, bottom)


@dataclass
class ExtractedTable:
    """Represents a structured table extracted from a single PDF page."""
    page_number: int
    bounding_box: tuple[float, float, float, float]  # (x0, top, x1, bottom)
    headers: list[str]
    rows: list[list[str]]
    cells: list[TableCell] = field(default_factory=list)
    markdown_representation: str = ""

    def to_markdown(self) -> str:
        """Render table as a clean Markdown table."""
        if not self.headers and not self.rows:
            return ""

        headers = [h.strip().replace("\n", " ") for h in self.headers]
        # Clean headers if empty
        if not any(headers):
            num_cols = max(len(r) for r in self.rows) if self.rows else 0
            headers = [f"Col {i+1}" for i in range(num_cols)]

        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        for row in self.rows:
            # Pad row if needed to match header length
            clean_row = [str(c).strip().replace("\n", " ") for c in row]
            if len(clean_row) < len(headers):
                clean_row.extend([""] * (len(headers) - len(clean_row)))
            elif len(clean_row) > len(headers):
                clean_row = clean_row[:len(headers)]
            lines.append("| " + " | ".join(clean_row) + " |")

        return "\n".join(lines)


class TableExtractor:
    """Extracts structured tables from PDF pages using pdfplumber."""

    def __init__(self, table_settings: Optional[dict[str, Any]] = None):
        self.table_settings = table_settings or {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "explicit_vertical_lines": [],
            "explicit_horizontal_lines": [],
            "snap_tolerance": 3,
            "join_tolerance": 3,
            "edge_min_length": 3,
            "min_words_vertical": 3,
            "min_words_horizontal": 1,
            "intersection_tolerance": 3,
        }

    def extract_tables_from_page(
        self,
        page: pdfplumber.page.Page,
        page_number: int,
    ) -> list[ExtractedTable]:
        """Detect and extract all tables on a given pdfplumber page."""
        extracted: list[ExtractedTable] = []
        
        # Try default line-based extraction first
        tables = page.find_tables(table_settings=self.table_settings)
        
        # Optional text-based fallback only when explicitly enabled in settings
        if not tables and self.table_settings.get("use_text_fallback", False):
            fallback_settings = {
                "vertical_strategy": "text",
                "horizontal_strategy": "text",
                "min_words_vertical": 3,
                "snap_tolerance": 4,
            }
            cand_tables = page.find_tables(table_settings=fallback_settings)
            tables = []
            for tbl in cand_tables:
                raw_data = tbl.extract()
                if raw_data and len(raw_data) >= 2 and len(raw_data[0]) >= 2:
                    cell_texts = [str(c or "").strip() for row in raw_data for c in row if c]
                    if cell_texts:
                        avg_len = sum(len(c) for c in cell_texts) / len(cell_texts)
                        if len(raw_data[0]) <= 8 and avg_len >= 3.0:
                            tables.append(tbl)

        for tbl in tables:
            bbox = tbl.bbox  # (x0, top, x1, bottom)
            raw_data = tbl.extract()
            if not raw_data or len(raw_data) < 2:
                continue

            # First non-empty row serves as header
            headers = [str(c or "").strip() for c in raw_data[0]]
            rows = [[str(c or "").strip() for c in r] for r in raw_data[1:]]

            # Build TableCell models if cell coordinates are available
            cells: list[TableCell] = []
            if hasattr(tbl, "cells"):
                for r_idx, row in enumerate(raw_data):
                    for c_idx, val in enumerate(row):
                        cells.append(
                            TableCell(
                                row_index=r_idx,
                                col_index=c_idx,
                                text=str(val or "").strip(),
                                bounding_box=bbox,
                            )
                        )

            table_obj = ExtractedTable(
                page_number=page_number,
                bounding_box=bbox,
                headers=headers,
                rows=rows,
                cells=cells,
            )
            table_obj.markdown_representation = table_obj.to_markdown()
            extracted.append(table_obj)

        return extracted

    def extract_all_tables(self, pdf_path: Path | str) -> list[ExtractedTable]:
        """Extract all tables across all pages of a PDF document."""
        all_tables: list[ExtractedTable] = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_idx, page in enumerate(pdf.pages, start=1):
                tables = self.extract_tables_from_page(page, page_idx)
                all_tables.extend(tables)
        return all_tables
