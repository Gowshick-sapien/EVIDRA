"""
Unit tests for the SQLite EvidenceLedger persistence engine.
Validates all CRUD operations, foreign key cascades, and transactional integrity.
"""
import json
import sqlite3
import tempfile
from pathlib import Path
import pytest

# pyrefly: ignore [missing-import]
from src.db.ledger import (
    DocumentRecord,
    EvidenceChunkRecord,
    EvidenceWindowRecord,
    ObservationRecord,
    FactCandidateRecord,
    HypothesisRecord,
    ValidatorResultRecord,
    DecisionRecord,
    DecisionTraceRecord,
    EvidenceLedger,
)


@pytest.fixture
def temp_ledger():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_ledger.db"
        ledger = EvidenceLedger(db_path)
        yield ledger


def test_schema_initialization(temp_ledger):
    """Verify that all tables are created during initialization."""
    with temp_ledger.transaction() as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row[0] for row in cursor.fetchall()}
    
    expected_tables = {
        "documents",
        "evidence_chunks",
        "evidence_windows",
        "observations",
        "fact_candidates",
        "fact_groups",
        "group_members",
        "hypotheses",
        "validator_results",
        "decisions",
        "decision_traces",
    }
    assert expected_tables.issubset(tables)


def test_document_crud(temp_ledger):
    """Verify document insertion and retrieval."""
    doc = DocumentRecord(
        document_id="DOC-001",
        filename="Q3_Report.pdf",
        file_hash="hash123456",
        page_count=10,
    )
    doc_id = temp_ledger.insert_document(doc)
    assert doc_id == "DOC-001"

    retrieved = temp_ledger.get_document("DOC-001")
    assert retrieved is not None
    assert retrieved["filename"] == "Q3_Report.pdf"
    assert retrieved["page_count"] == 10

    # Duplicate file hash must raise IntegrityError
    duplicate_doc = DocumentRecord(
        document_id="DOC-002",
        filename="Another.pdf",
        file_hash="hash123456",
        page_count=5,
    )
    with pytest.raises(sqlite3.IntegrityError):
        temp_ledger.insert_document(duplicate_doc)


def test_evidence_chunks_and_observations(temp_ledger):
    """Verify chunk and observation insertion with foreign key integrity."""
    doc = DocumentRecord(
        document_id="DOC-100",
        filename="Annual_Report.pdf",
        file_hash="hash_annual",
        page_count=20,
    )
    temp_ledger.insert_document(doc)

    chunks = [
        EvidenceChunkRecord(
            chunk_id="CHK-001",
            document_id="DOC-100",
            page_number=3,
            chunk_type="text",
            bounding_box=[72.0, 100.0, 500.0, 140.0],
            content="Total revenue reached $100M in FY2024.",
            content_hash="chash001",
        ),
        EvidenceChunkRecord(
            chunk_id="CHK-002",
            document_id="DOC-100",
            page_number=5,
            chunk_type="table",
            bounding_box=[50.0, 200.0, 550.0, 450.0],
            content="Revenue: $100M | Operating Income: $20M",
            content_hash="chash002",
        ),
    ]
    count = temp_ledger.insert_evidence_chunks(chunks)
    assert count == 2

    retrieved_chunks = temp_ledger.get_evidence_chunks("DOC-100")
    assert len(retrieved_chunks) == 2
    assert retrieved_chunks[0]["bounding_box"] == [72.0, 100.0, 500.0, 140.0]

    # Observations
    observations = [
        ObservationRecord(
            observation_id="OBS-001",
            chunk_id="CHK-001",
            document_id="DOC-100",
            statement="Revenue reached $100M in FY2024",
            entity="Acme Corp",
            attribute="revenue",
            raw_value="$100M",
            observation_type="numerical",
            temporal_scope="FY2024",
            provenance_status="ENTAILED",
            confidence=0.98,
        )
    ]
    obs_count = temp_ledger.insert_observations(observations)
    assert obs_count == 1

    retrieved_obs = temp_ledger.get_observations_for_document("DOC-100")
    assert len(retrieved_obs) == 1
    assert retrieved_obs[0].statement == "Revenue reached $100M in FY2024"


def test_fact_grouping_and_decision_card(temp_ledger):
    """Verify the full relationship lifecycle: facts -> group -> hypotheses -> decision -> trace."""
    # 1. Setup Document, Chunks, and Observations
    doc1 = DocumentRecord("DOC-A", "PR.pdf", "hash_a", 4)
    doc2 = DocumentRecord("DOC-B", "10K.pdf", "hash_b", 40)
    temp_ledger.insert_document(doc1)
    temp_ledger.insert_document(doc2)

    chunks = [
        EvidenceChunkRecord("CHK-A1", "DOC-A", 1, "text", [10, 10, 100, 50], "Revenue $100M", "h1"),
        EvidenceChunkRecord("CHK-B1", "DOC-B", 12, "table", [20, 20, 200, 100], "Revenue $98M", "h2"),
    ]
    temp_ledger.insert_evidence_chunks(chunks)

    obs = [
        ObservationRecord("OBS-A1", "CHK-A1", "DOC-A", "Revenue was $100M", "Acme", "revenue", "$100M", "numerical", "FY2024", "ENTAILED", 0.99),
        ObservationRecord("OBS-B1", "CHK-B1", "DOC-B", "Revenue was $98M", "Acme", "revenue", "$98M", "numerical", "FY2024", "ENTAILED", 0.99),
    ]
    temp_ledger.insert_observations(obs)

    # 2. Fact Candidates
    facts = [
        FactCandidateRecord("FACT-1", "OBS-A1", "100000000", "USD", "USD", "2024-01-01", "2024-12-31"),
        FactCandidateRecord("FACT-2", "OBS-B1", "98000000", "USD", "USD", "2024-01-01", "2024-12-31"),
    ]
    temp_ledger.insert_fact_candidates(facts)

    # 3. Fact Group
    group_id = temp_ledger.create_fact_group("Acme", "revenue", "FY2024", ["FACT-1", "FACT-2"], "GRP-REV-01")
    assert group_id == "GRP-REV-01"

    # 4. Hypothesis & Validator Result
    hyp = HypothesisRecord("HYP-01", "GRP-REV-01", "RESTATEMENT", "Revenue restated due to audit", 0.85)
    temp_ledger.insert_hypothesis(hyp)

    val = ValidatorResultRecord("VAL-01", "HYP-01", "RestatementValidator", "SUPPORTED", json.dumps({"note": "Found 10-K/A"}))
    temp_ledger.insert_validator_result(val)

    # 5. Final Decision
    decision = DecisionRecord("DEC-01", "GRP-REV-01", "RECONCILED", "HIGH", "Variance explained by restatement")
    temp_ledger.record_decision(decision)

    # 6. Audit Trace
    trace = DecisionTraceRecord("TRC-01", "DEC-01", "PolicyEvaluation", "DecisionPolicyEngine", "{}", "{}", 4.5)
    temp_ledger.append_decision_trace(trace)

    # 7. Query Decision Card
    card = temp_ledger.get_decision_card("DEC-01")
    assert card is not None
    assert card["verdict"] == "RECONCILED"
    assert card["decision_strength"] == "HIGH"
    assert len(card["claims"]) == 2
    assert card["claims"][0]["normalized_value"] in ("100000000", "98000000")
    assert len(card["hypotheses"]) == 1
    assert card["hypotheses"][0]["validators"][0]["outcome"] == "SUPPORTED"
    assert len(card["traces"]) == 1

    # 8. Summary statistics
    summary = temp_ledger.get_job_summary()
    assert summary["documents_count"] == 2
    assert summary["evidence_chunks_count"] == 2
    assert summary["fact_candidates_count"] == 2
    assert summary["decisions_count"] == 1
    assert summary["verdicts"]["RECONCILED"] == 1


def test_transaction_rollback(temp_ledger):
    """Verify that failures within a transaction block trigger a clean rollback."""
    doc = DocumentRecord("DOC-FAIL", "Test.pdf", "hash_fail", 1)
    temp_ledger.insert_document(doc)

    # Attempt inserting an observation referencing a non-existent chunk_id
    invalid_obs = ObservationRecord(
        observation_id="OBS-INVALID",
        chunk_id="NON_EXISTENT_CHUNK",
        document_id="DOC-FAIL",
        statement="Fail",
        entity="Fail",
        attribute="fail",
        raw_value="0",
        observation_type="numerical",
        temporal_scope="2024",
        provenance_status="ENTAILED",
        confidence=1.0,
    )
    with pytest.raises(sqlite3.IntegrityError):
        temp_ledger.insert_observations([invalid_obs])

    # Confirm that nothing was inserted
    summary = temp_ledger.get_job_summary()
    assert summary["observations_count"] == 0


def test_evidence_windows_crud(temp_ledger):
    """Verify insertion, conflict update, and retrieval of evidence windows."""
    doc = DocumentRecord("DOC-WIN", "Report.pdf", "hash_win", 5)
    temp_ledger.insert_document(doc)

    chunk = EvidenceChunkRecord(
        chunk_id="CHK-WIN001",
        document_id="DOC-WIN",
        page_number=1,
        chunk_type="table",
        bounding_box=[10.0, 20.0, 100.0, 200.0],
        content="| Revenue | 500 |",
        content_hash="hash_c1",
    )
    temp_ledger.insert_evidence_chunks([chunk])

    win = EvidenceWindowRecord(
        window_id="WIN-001",
        chunk_id="CHK-WIN001",
        document_id="DOC-WIN",
        page_number=1,
        section_title="Financial Summary",
        section_confidence=0.88,
        table_caption="Table 1: Revenue",
        stated_unit="crore",
        stated_currency="INR",
        column_headers='["Metric", "Value"]',
        row_context="Revenue",
        page_header="Annual Report 2024",
        footnotes='["1. Audited figures"]',
    )
    count = temp_ledger.insert_evidence_windows([win])
    assert count == 1

    # Retrieve by chunk_id
    retrieved = temp_ledger.get_evidence_window("CHK-WIN001")
    assert retrieved is not None
    assert retrieved.window_id == "WIN-001"
    assert retrieved.section_title == "Financial Summary"
    assert retrieved.section_confidence == 0.88
    assert retrieved.stated_unit == "crore"

    # Retrieve by document_id
    doc_windows = temp_ledger.get_windows_for_document("DOC-WIN")
    assert len(doc_windows) == 1
    assert doc_windows[0].chunk_id == "CHK-WIN001"

    # Test conflict update
    win_updated = EvidenceWindowRecord(
        window_id="WIN-001",
        chunk_id="CHK-WIN001",
        document_id="DOC-WIN",
        page_number=1,
        section_title="Updated Section",
        section_confidence=0.95,
        table_caption="Updated Caption",
        stated_unit="lakh",
        stated_currency="INR",
    )
    temp_ledger.insert_evidence_windows([win_updated])
    retrieved2 = temp_ledger.get_evidence_window("CHK-WIN001")
    assert retrieved2.section_title == "Updated Section"
    assert retrieved2.section_confidence == 0.95
    assert retrieved2.stated_unit == "lakh"
