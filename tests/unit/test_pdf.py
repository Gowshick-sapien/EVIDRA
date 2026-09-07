import tempfile
from pathlib import Path
import pymupdf as fitz
import pytest

# pyrefly: ignore [missing-import]
from src.pdf.parser import PDFParser
# pyrefly: ignore [missing-import]
from src.pdf.tables import TableExtractor


def create_synthetic_pdf(filepath: Path) -> Path:
    """Create a syntactically valid PDF containing a heading, paragraph, and table lines."""
    doc = fitz.open()
    page = doc.new_page(width=600, height=800)
    
    # 1. Insert Heading
    page.insert_text((50, 50), "DELHIVERY FINANCIAL SUMMARY", fontsize=16, fontname="helv")
    
    # 2. Insert Narrative Text
    page.insert_text(
        (50, 80),
        "Revenue from operations increased by 89% in Fiscal 2022 to reach INR 6,882.29 million.",
        fontsize=10,
        fontname="helv",
    )
    
    # 3. Draw a table grid and insert text
    # Table bounds: x0=50, y0=120, x1=450, y1=200
    page.draw_rect(fitz.Rect(50, 120, 450, 200), width=1)
    page.draw_line(fitz.Point(50, 150), fitz.Point(450, 150), width=1)
    page.draw_line(fitz.Point(250, 120), fitz.Point(250, 200), width=1)
    
    page.insert_text((60, 140), "Financial Metric", fontsize=10, fontname="helv")
    page.insert_text((260, 140), "FY2022 (INR Millions)", fontsize=10, fontname="helv")
    page.insert_text((60, 180), "Revenue from Operations", fontsize=10, fontname="helv")
    page.insert_text((260, 180), "6,882.29", fontsize=10, fontname="helv")
    
    doc.save(str(filepath))
    doc.close()
    return filepath


def test_pdf_parser_extracts_blocks():
    """Verify that PDFParser extracts layout blocks with bounding boxes."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "synthetic.pdf"
        create_synthetic_pdf(pdf_path)
        
        parser = PDFParser()
        blocks = parser.parse_document(pdf_path)
        
        assert len(blocks) >= 2
        # Check for heading
        headings = [b for b in blocks if b.block_type == "heading"]
        assert len(headings) >= 1
        assert "DELHIVERY" in headings[0].content
        assert headings[0].bounding_box[0] >= 0.0
        assert headings[0].page_number == 1


def test_table_extractor_finds_grid():
    """Verify that TableExtractor discovers explicit table boundaries."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "synthetic.pdf"
        create_synthetic_pdf(pdf_path)
        
        extractor = TableExtractor()
        tables = extractor.extract_all_tables(pdf_path)
        
        assert len(tables) >= 1
        tbl = tables[0]
        assert tbl.page_number == 1
        assert len(tbl.bounding_box) == 4
        assert "|" in tbl.markdown_representation


def test_pdf_parser_defensive_on_missing_or_corrupt_files():
    """Verify parser returns empty list without raising for invalid files."""
    parser = PDFParser()
    with tempfile.TemporaryDirectory() as tmp_dir:
        corrupt_file = Path(tmp_dir) / "corrupt.pdf"
        corrupt_file.write_bytes(b"not a valid pdf binary")
        
        blocks = parser.parse_document(corrupt_file)
        assert blocks == []
