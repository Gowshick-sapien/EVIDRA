import tempfile
from pathlib import Path
import pytest
import pymupdf as fitz

# pyrefly: ignore [missing-import]
from src.db.ledger import EvidenceLedger
# pyrefly: ignore [missing-import]
from src.extraction.agents import ExtractionAgent
# pyrefly: ignore [missing-import]
from src.extraction.pipeline import ExtractionPipeline
# pyrefly: ignore [missing-import]
from src.extraction.schemas import (
    EvidenceChunk,
    NumericalObservation,
    ObservationBundle,
    SemanticObservation,
)
# pyrefly: ignore [missing-import]
from src.llm.provider import ReasoningService


class MockReasoningService:
    """Mock LLM provider returning deterministic observation bundles without network access."""

    def generate_structured(self, prompt, response_model, system_prompt=None, max_retries=3):
        # pyrefly: ignore [missing-import]
        from src.verification.verifier import VerificationVerdict
        # pyrefly: ignore [missing-import]
        from src.verification.context import FinancialContext
        if response_model == VerificationVerdict:
            return VerificationVerdict(status="ENTAILED", confidence=1.0, explanation="Entailed test observation")
        if response_model == FinancialContext:
            return FinancialContext(accounting_basis="IND_AS", filing_type="PROSPECTUS")
        return ObservationBundle(
            numerical_observations=[
                NumericalObservation(
                    statement="Revenue from operations was INR 6,882.29 million.",
                    entity="Delhivery",
                    attribute="Revenue from Operations",
                    raw_value="6,882.29",
                    unit="Millions",
                    currency="INR",
                    temporal_scope="FY22",
                    confidence=0.98,
                )
            ],
            semantic_observations=[
                SemanticObservation(
                    statement="The company operates an integrated express logistics network.",
                    entity="Delhivery",
                    attribute="Business Overview",
                    raw_value="Integrated express logistics network",
                    temporal_scope="FY22",
                    confidence=0.95,
                )
            ],
        )


def create_test_pdf(filepath: Path) -> Path:
    """Create simple single-page PDF with clear financial text."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 100),
        "Delhivery reported Revenue from operations of INR 6,882.29 million for FY22.",
        fontsize=12,
    )
    doc.save(str(filepath))
    doc.close()
    return filepath


def test_evidence_chunk_hashing():
    """Verify that EvidenceChunk produces deterministic cryptographic IDs."""
    c1 = EvidenceChunk.create("DOC-01", 1, "text", [10, 20, 30, 40], "Revenue INR 100M")
    c2 = EvidenceChunk.create("DOC-01", 1, "text", [10, 20, 30, 40], "Revenue INR 100M")
    c3 = EvidenceChunk.create("DOC-01", 1, "text", [10, 20, 30, 40], "Revenue INR 200M")

    assert c1.chunk_id == c2.chunk_id
    assert c1.chunk_id.startswith("CHK-")
    assert c1.chunk_id != c3.chunk_id


def test_extraction_agent_with_mock():
    """Verify ExtractionAgent formats prompt and handles ObservationBundle."""
    mock_llm = MockReasoningService()
    agent = ExtractionAgent(mock_llm)
    chunk = EvidenceChunk.create("DOC-01", 1, "text", [10, 20, 30, 40], "Some financial disclosure")

    bundle = agent.extract_from_chunk(chunk)
    assert len(bundle.numerical_observations) == 1
    assert bundle.numerical_observations[0].attribute == "Revenue from Operations"
    assert bundle.numerical_observations[0].currency == "INR"


def test_extraction_pipeline_end_to_end():
    """Verify ExtractionPipeline populates evidence_chunks and observations in SQLite."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        db_path = tmp_path / "ledger.db"
        pdf_path = tmp_path / "doc.pdf"
        create_test_pdf(pdf_path)

        ledger = EvidenceLedger(db_path)
        mock_llm = MockReasoningService()
        pipeline = ExtractionPipeline(ledger=ledger, reasoning_service=mock_llm)

        summary = pipeline.process_document("DOC-TEST", pdf_path)
        assert summary["evidence_chunks_count"] >= 1
        assert summary["observations_count"] >= 2

        # Verify records exist in SQLite
        db_summary = ledger.get_job_summary()
        assert db_summary["evidence_chunks_count"] >= 1
        assert db_summary["observations_count"] >= 2
