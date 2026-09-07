"""
Contract tests for FastAPI server endpoints.
"""
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# pyrefly: ignore [missing-import]
from src.api.server import create_app
# pyrefly: ignore [missing-import]
from src.db.ledger import (
    DocumentRecord,
    EvidenceChunkRecord,
    ObservationRecord,
    FactCandidateRecord,
    DecisionRecord,
    EvidenceLedger,
)


@pytest.fixture
def client_and_root():
    with tempfile.TemporaryDirectory() as tmp_dir:
        app = create_app(runs_root=tmp_dir)
        client = TestClient(app)
        yield client, Path(tmp_dir)


def test_health_check(client_and_root):
    client, _ = client_and_root
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert data["sqlite"] == "READY"
    assert "ollama" in data


def test_create_job_and_poll_status(client_and_root):
    client, runs_root = client_and_root

    # 1. Post a job with a mock PDF
    files = [("files", ("test_filing.pdf", b"%PDF-1.4 mock content", "application/pdf"))]
    create_resp = client.post("/jobs", files=files)
    assert create_resp.status_code == 202
    data = create_resp.json()
    job_id = data["job_id"]
    assert job_id.startswith("JOB-")

    # 2. Poll job status
    status_resp = client.get(f"/jobs/{job_id}")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["job_id"] == job_id
    assert status_data["status"] in ("PENDING", "PROCESSING", "COMPLETED")
    assert status_data["input_files"] == ["test_filing.pdf"]


def test_job_decisions_and_details(client_and_root):
    client, runs_root = client_and_root

    # Create job
    files = [("files", ("report.pdf", b"%PDF-1.4 content", "application/pdf"))]
    create_resp = client.post("/jobs", files=files)
    job_id = create_resp.json()["job_id"]

    # Manually populate ledger with a decision
    job_dir = runs_root / job_id
    ledger = EvidenceLedger(job_dir / "ledger.db")
    
    doc = DocumentRecord("DOC-01", "report.pdf", "hash01", 5)
    ledger.insert_document(doc)
    chunk = EvidenceChunkRecord("CHK-01", "DOC-01", 1, "text", [10, 20, 30, 40], "Revenue ", "chash01")
    ledger.insert_evidence_chunks([chunk])
    obs = ObservationRecord("OBS-01", "CHK-01", "DOC-01", "Revenue was ", "Corp", "rev", "", "numerical", "FY2024", "ENTAILED", 1.0)
    ledger.insert_observations([obs])
    fact = FactCandidateRecord("F-01", "OBS-01", "50000000", "USD", "USD", "2024-01-01", "2024-12-31")
    ledger.insert_fact_candidates([fact])
    gid = ledger.create_fact_group("Corp", "rev", "FY2024", ["F-01"], "GRP-01")
    dec = DecisionRecord("DEC-99", gid, "CORROBORATED", "HIGH", "Perfect match")
    ledger.record_decision(dec)

    # List decisions
    dec_resp = client.get(f"/jobs/{job_id}/decisions")
    assert dec_resp.status_code == 200
    dec_data = dec_resp.json()
    assert dec_data["count"] == 1
    assert dec_data["decisions"][0]["decision_id"] == "DEC-99"
    assert dec_data["decisions"][0]["verdict"] == "CORROBORATED"

    # Filter with mismatching verdict
    filter_resp = client.get(f"/jobs/{job_id}/decisions?verdict=CONTRADICTION")
    assert filter_resp.status_code == 200
    assert filter_resp.json()["count"] == 0

    # Get decision detail
    detail_resp = client.get(f"/jobs/{job_id}/decisions/DEC-99")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["decision_id"] == "DEC-99"
    assert len(detail_data["claims"]) == 1
    assert detail_data["claims"][0]["normalized_value"] == "50000000"


def test_empty_file_upload_rejection(client_and_root):
    client, _ = client_and_root
    files = [("files", ("empty.pdf", b"", "application/pdf"))]
    resp = client.post("/jobs", files=files)
    assert resp.status_code == 422


def test_nonexistent_job_returns_404(client_and_root):
    client, _ = client_and_root
    resp = client.get("/jobs/JOB-DOES-NOT-EXIST")
    assert resp.status_code == 404