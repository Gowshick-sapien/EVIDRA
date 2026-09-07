import tempfile
from pathlib import Path
import pytest
# pyrefly: ignore [missing-import]
from src.db.ledger import EvidenceLedger, ObservationRecord
# pyrefly: ignore [missing-import]
from src.matching.embeddings import FactGroupEngine
# pyrefly: ignore [missing-import]
from src.verification.context import ContextResolverAgent
# pyrefly: ignore [missing-import]
from src.verification.pipeline import VerificationPipeline
# pyrefly: ignore [missing-import]
from src.verification.verifier import EvidenceVerifierAgent, VerificationVerdict


class MockVerifierLLM:
    """Mock LLM returning predefined verification verdicts for testing."""

    def __init__(self, verdict: str = "ENTAILED"):
        self.verdict = verdict

    def generate_structured(self, prompt, response_model, system_prompt=None, max_retries=2):
        return VerificationVerdict(
            status=self.verdict,
            confidence=0.99,
            explanation="Mock verification explanation",
        )


def test_context_resolver_deterministic():
    """Verify deterministic qualifier extraction from terminology."""
    ctx1 = ContextResolverAgent.resolve_deterministically(
        statement="Consolidated Revenue from Operations under Ind AS",
        chunk_content="Restated Consolidated Financial Statements",
        filename="prospectus.pdf",
    )
    assert ctx1.organizational_scope == "CONSOLIDATED"
    assert ctx1.accounting_basis == "IFRS"
    assert ctx1.filing_type == "PROSPECTUS"
    assert ctx1.version_status == "RESTATED"

    ctx2 = ContextResolverAgent.resolve_deterministically(
        statement="Adjusted EBITDA (Non-GAAP metric)",
        chunk_content="Standalone Annual Report",
        filename="10k_annual_report.pdf",
    )
    assert ctx2.organizational_scope == "STANDALONE"
    assert ctx2.accounting_basis == "NON_GAAP"
    assert ctx2.filing_type == "ANNUAL_REPORT"


def test_verifier_agent_mock():
    """Verify EvidenceVerifierAgent dispatches prompt and returns verdict."""
    mock_entailed = MockVerifierLLM("ENTAILED")
    verifier = EvidenceVerifierAgent(mock_entailed)
    res = verifier.verify_observation(
        statement="Revenue was INR 6,882.29 million",
        chunk_content="Total Revenue: INR 6,882.29 million for the period.",
    )
    assert res.status == "ENTAILED"

    mock_hallucinated = MockVerifierLLM("HALLUCINATED")
    verifier_bad = EvidenceVerifierAgent(mock_hallucinated)
    res_bad = verifier_bad.verify_observation(
        statement="Revenue was USD 500 Billion",
        chunk_content="Total Revenue: INR 6,882.29 million for the period.",
    )
    assert res_bad.status == "HALLUCINATED"


def test_fact_group_engine_hard_blocking():
    """Verify facts for different entities or periods are never grouped together."""
    engine = FactGroupEngine()
    candidates = [
        {"fact_id": "F1", "entity": "Delhivery", "attribute": "Revenue", "period_start": "2021-04-01", "period_end": "2022-03-31"},
        {"fact_id": "F2", "entity": "Delhivery", "attribute": "Revenue", "period_start": "2020-04-01", "period_end": "2021-03-31"},
        {"fact_id": "F3", "entity": "BlueDart", "attribute": "Revenue", "period_start": "2021-04-01", "period_end": "2022-03-31"},
    ]
    groups = engine.group_candidates(candidates)
    # Must yield 3 completely distinct groups
    assert len(groups) == 3
    for g, member_ids in groups:
        assert len(member_ids) == 1


def test_fact_group_engine_semantic_clustering():
    """Verify synonymous attributes in same period cluster into unified FactGroup."""
    engine = FactGroupEngine()
    candidates = [
        {"fact_id": "F1", "entity": "Delhivery", "attribute": "Revenue from operations", "period_start": "2021-04-01", "period_end": "2022-03-31"},
        {"fact_id": "F2", "entity": "Delhivery", "attribute": "Operating Revenue", "period_start": "2021-04-01", "period_end": "2022-03-31"},
        {"fact_id": "F3", "entity": "Delhivery", "attribute": "Total Non-Current Borrowings", "period_start": "2021-04-01", "period_end": "2022-03-31"},
    ]
    groups = engine.group_candidates(candidates)
    # Revenue from operations and Operating Revenue should cluster together
    assert len(groups) == 2
    multi_member_groups = [(g, members) for g, members in groups if len(members) == 2]
    assert len(multi_member_groups) == 1
    assert set(multi_member_groups[0][1]) == {"F1", "F2"}


def test_verification_pipeline_end_to_end():
    """Verify VerificationPipeline populates fact_candidates, fact_groups, and group_members."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "ledger.db"
        ledger = EvidenceLedger(db_path)

        # Seed document
        with ledger.transaction() as conn:
            conn.execute("INSERT INTO documents (document_id, filename, file_hash, page_count) VALUES ('DOC-01', 'file.pdf', 'hash1', 1);")
            conn.execute("INSERT INTO evidence_chunks (chunk_id, document_id, page_number, chunk_type, bounding_box, content, content_hash) VALUES ('CHK-01', 'DOC-01', 1, 'text', '[]', 'Revenue INR 500 Cr', 'chash1');")

        # Seed observations
        obs1 = ObservationRecord(
            observation_id="OBS-01",
            chunk_id="CHK-01",
            document_id="DOC-01",
            statement="Revenue was INR 500 Crores in FY22",
            entity="Delhivery",
            attribute="Revenue from operations",
            raw_value="INR 500 Crores",
            observation_type="numerical",
            temporal_scope="FY22",
            confidence=1.0,
            provenance_status="ENTAILED",
        )
        obs2 = ObservationRecord(
            observation_id="OBS-02",
            chunk_id="CHK-01",
            document_id="DOC-01",
            statement="Operating Revenue was INR 500 Crores in FY22",
            entity="Delhivery",
            attribute="Operating Revenue",
            raw_value="INR 500 Crores",
            observation_type="numerical",
            temporal_scope="FY22",
            confidence=1.0,
            provenance_status="ENTAILED",
        )
        ledger.insert_observations([obs1, obs2])

        pipeline = VerificationPipeline(ledger=ledger, skip_verifier=True)
        res = pipeline.process_observations()

        assert res["candidates_count"] == 2
        assert res["groups_count"] == 1  # Clustered into 1 group

        summary = ledger.get_job_summary()
        assert summary["fact_candidates_count"] == 2
        assert summary["fact_groups_count"] == 1
