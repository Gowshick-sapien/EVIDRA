"""
Integration and validation tests for Phase P0 Upstream Extraction Foundation.
"""

import tempfile
from pathlib import Path
import pytest
import pymupdf as fitz

# pyrefly: ignore [missing-import]
from src.db.ledger import EvidenceLedger
# pyrefly: ignore [missing-import]
from src.extraction.agents import ExtractionAgent, is_verbatim_entailed, GENERIC_ENTITIES
# pyrefly: ignore [missing-import]
from src.extraction.pipeline import ExtractionPipeline
# pyrefly: ignore [missing-import]
from src.extraction.schemas import (
    EvidenceChunk,
    EvidenceWindow,
    NumericalObservation,
    ObservationBundle,
    SemanticObservation,
)
# pyrefly: ignore [missing-import]
from src.pdf.parser import ExtractedBlock
# pyrefly: ignore [missing-import]
from src.pdf.topology import DocumentTopologyBuilder
# pyrefly: ignore [missing-import]
from src.extraction.windows import EvidenceWindowBuilder


class MockP0ReasoningService:
    """Mock LLM provider testing P0 validation and prompt envelope responses."""

    def __init__(self, produce_generic: bool = False, hallucinate_number: bool = False):
        self.produce_generic = produce_generic
        self.hallucinate_number = hallucinate_number

    def generate_structured(self, prompt, response_model, system_prompt=None, max_retries=3):
        entity = "Reporting Entity" if self.produce_generic else "Delhivery Limited"
        val = "999999" if self.hallucinate_number else "8,142.00"

        return ObservationBundle(
            numerical_observations=[
                NumericalObservation(
                    statement=f"Revenue from operations was INR {val} crores.",
                    entity=entity,
                    attribute="Revenue from Operations",
                    raw_value=val,
                    unit="crore",
                    currency="INR",
                    temporal_scope="FY24",
                    confidence=0.98,
                )
            ],
            semantic_observations=[
                SemanticObservation(
                    statement="The company operates India's largest logistics network.",
                    entity=entity,
                    attribute="Business Overview",
                    raw_value="Largest logistics network",
                    temporal_scope="FY24",
                    confidence=0.95,
                )
            ],
        )


def create_sample_p0_pdf(filepath: Path) -> Path:
    """Create a multi-block PDF containing section headers, narrative text, and financial tables."""
    doc = fitz.open()
    page = doc.new_page()

    # Title / Section
    page.insert_text((50, 40), "Delhivery Limited - Financial Results", fontsize=16)

    # Narrative paragraph
    page.insert_text(
        (50, 80),
        "Delhivery Limited announced strong performance for FY24 with Revenue from operations of INR 8,142.00 crore.",
        fontsize=11,
    )

    # Table layout
    table_lines = [
        "| Particulars | FY24 (INR Cr) | FY23 (INR Cr) |",
        "|---|---|---|",
        "| Revenue from Operations | 8,142.00 | 7,225.00 |",
        "| EBITDA | 450.00 | 120.00 |",
        "| Net Profit / (Loss) | 100.00 | (150.00) |",
    ]
    y = 120
    for line in table_lines:
        page.insert_text((50, y), line, fontsize=10)
        y += 18

    doc.save(str(filepath))
    doc.close()
    return filepath


def test_is_verbatim_entailed():
    """Verify verbatim number entailment with comma, whitespace, and negative notation tolerance."""
    content = "The revenue grew to 8,142.50 crore while net loss was (120.00) crore."
    assert is_verbatim_entailed("8,142.50", content) is True
    assert is_verbatim_entailed("8142.50", content) is True
    assert is_verbatim_entailed("(120.00)", content) is True
    assert is_verbatim_entailed("-120.00", content) is True
    assert is_verbatim_entailed("999999", content) is False
    assert is_verbatim_entailed("", content) is False


def test_validation_rejects_generic_entities():
    """Verify that ExtractionAgent validator filters out generic entities."""
    mock_llm = MockP0ReasoningService(produce_generic=True)
    agent = ExtractionAgent(mock_llm)
    window = EvidenceWindow(
        window_id="w1",
        chunk_id="c1",
        document_id="doc1",
        page_number=1,
        chunk_type="text",
        bounding_box=[0.0, 0.0, 100.0, 100.0],
        content="Delhivery Limited reported revenue of 8,142.00 crore for FY24.",
        content_hash="h1",
    )
    bundle = agent.extract_from_chunk(window, validate=True)
    # The generic observation with entity="Reporting Entity" must be rejected
    assert len(bundle.numerical_observations) == 0
    assert len(bundle.semantic_observations) == 0


def test_validation_rejects_hallucinated_values():
    """Verify that ExtractionAgent validator rejects values not verbatim in window."""
    mock_llm = MockP0ReasoningService(hallucinate_number=True)
    agent = ExtractionAgent(mock_llm)
    window = EvidenceWindow(
        window_id="w1",
        chunk_id="c1",
        document_id="doc1",
        page_number=1,
        chunk_type="text",
        bounding_box=[0.0, 0.0, 100.0, 100.0],
        content="Delhivery Limited reported revenue of 8,142.00 crore for FY24.",
        content_hash="h1",
    )
    bundle = agent.extract_from_chunk(window, validate=True)
    # 999999 is not in content, so numerical observation must be rejected
    assert len(bundle.numerical_observations) == 0
    # Semantic observation should still be retained
    assert len(bundle.semantic_observations) == 1


def test_discover_candidates_budget_and_table_preservation():
    """Verify that 3-tier discovery preserves 100% of tables and honors quotas."""
    windows: list[EvidenceWindow] = []

    # Create 5 tables
    for i in range(5):
        windows.append(
            EvidenceWindow(
                window_id=f"w_tbl_{i}",
                chunk_id=f"c_tbl_{i}",
                document_id="doc1",
                page_number=i + 1,
                chunk_type="table",
                bounding_box=[10, 10, 200, 200],
                content=f"| Revenue | {i*1000} |\n|---|---|\n| Profit | {i*100} |",
                content_hash=f"h_tbl_{i}",
            )
        )

    # Create 40 narrative text blocks with financial indicators
    for i in range(40):
        windows.append(
            EvidenceWindow(
                window_id=f"w_txt_{i}",
                chunk_id=f"c_txt_{i}",
                document_id="doc1",
                page_number=i + 1,
                chunk_type="text",
                bounding_box=[10, 10, 200, 200],
                content=f"The company achieved strong revenue and EBITDA growth of {i*10}% during fiscal FY24.",
                content_hash=f"h_txt_{i}",
            )
        )

    # Instantiate pipeline
    with tempfile.TemporaryDirectory() as tmp_dir:
        ledger = EvidenceLedger(Path(tmp_dir) / "test.db")
        pipeline = ExtractionPipeline(ledger=ledger, per_document_budget=15)

        selected = pipeline.discover_candidates(windows, per_document_budget=15)
        # Quota must be strictly honored (<= 15)
        assert len(selected) == 15
        # All 5 tables MUST be included in the selected candidates
        selected_table_ids = {w.window_id for w in selected if w.chunk_type == "table"}
        assert len(selected_table_ids) == 5
        # Remaining 10 must be text candidates
        selected_text_ids = {w.window_id for w in selected if w.chunk_type == "text"}
        assert len(selected_text_ids) == 10


def test_end_to_end_p0_pipeline():
    """Verify end-to-end P0 pipeline processing, windows persistence, and ledger records."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        db_path = tmp_path / "p0_ledger.db"
        pdf_path = tmp_path / "p0_doc.pdf"
        ev_dir = tmp_path / "evidence"

        create_sample_p0_pdf(pdf_path)

        ledger = EvidenceLedger(db_path)
        mock_llm = MockP0ReasoningService(produce_generic=False, hallucinate_number=False)
        pipeline = ExtractionPipeline(
            ledger=ledger,
            reasoning_service=mock_llm,
            evidence_dir=ev_dir,
            per_document_budget=30,
        )

        res = pipeline.process_document("DOC-DELHIVERY", pdf_path)
        assert res["evidence_chunks_count"] >= 1
        assert res["evidence_windows_count"] >= 1
        assert res["observations_count"] >= 1

        # Verify evidence windows persisted in ledger
        windows_in_db = ledger.get_windows_for_document("DOC-DELHIVERY")
        assert len(windows_in_db) >= 1

        # Verify manifest and schema exported
        manifest_file = ev_dir / "DOC-DELHIVERY_manifest.json"
        assert manifest_file.exists()

        schema_file = ev_dir / "DOC-DELHIVERY_schema.json"
        assert schema_file.exists()

        # Check observations in SQLite
        observations = ledger.get_observations_for_document("DOC-DELHIVERY")
        for obs in observations:
            assert obs.entity.lower() not in GENERIC_ENTITIES
            assert obs.provenance_status == "ENTAILED"
