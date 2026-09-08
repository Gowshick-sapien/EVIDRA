"""
Unit tests for Claim Relationship Graph and Cluster-Based Adjudication (REQ-DEC-EXT-02).
"""
import tempfile
from decimal import Decimal
from pathlib import Path
import pytest

# pyrefly: ignore [missing-import]
from src.db.ledger import (
    DocumentRecord,
    EvidenceChunkRecord,
    EvidenceLedger,
    FactCandidateRecord,
    ObservationRecord,
)
# pyrefly: ignore [missing-import]
from src.decision.engine import FactDecisionEngine, cluster_claims_by_value
# pyrefly: ignore [missing-import]
from src.decision.schemas import CandidateFactView


def test_cluster_claims_by_value():
    """Verify equivalence value clustering groups identical values and tolerates <0.1% rounding."""
    c1 = CandidateFactView(
        fact_id="F1", observation_id="O1", document_id="D1", filename="doc1.pdf",
        page_number=1, bounding_box=[], chunk_content="", statement="",
        raw_value="500 Cr", normalized_value="5000000000", normalized_unit="SCALED_CRORE",
        normalized_currency="INR", period_start="2023-04-01", period_end="2024-03-31",
    )
    c2 = CandidateFactView(
        fact_id="F2", observation_id="O2", document_id="D2", filename="doc2.pdf",
        page_number=5, bounding_box=[], chunk_content="", statement="",
        raw_value="500 Cr", normalized_value="5000000000", normalized_unit="SCALED_CRORE",
        normalized_currency="INR", period_start="2023-04-01", period_end="2024-03-31",
    )
    # Slight rounding within 0.05%
    c3 = CandidateFactView(
        fact_id="F3", observation_id="O3", document_id="D3", filename="doc3.pdf",
        page_number=12, bounding_box=[], chunk_content="", statement="",
        raw_value="500.2 Cr", normalized_value="5002000000", normalized_unit="SCALED_CRORE",
        normalized_currency="INR", period_start="2023-04-01", period_end="2024-03-31",
    )
    # Distinct conflicting value (700 Cr)
    c4 = CandidateFactView(
        fact_id="F4", observation_id="O4", document_id="D4", filename="doc4.pdf",
        page_number=3, bounding_box=[], chunk_content="", statement="",
        raw_value="700 Cr", normalized_value="7000000000", normalized_unit="SCALED_CRORE",
        normalized_currency="INR", period_start="2023-04-01", period_end="2024-03-31",
    )

    clusters = cluster_claims_by_value([c1, c2, c3, c4])
    assert len(clusters) == 2
    # Cluster 1: 500 Cr (c1, c2, c3)
    assert len(clusters[0]["members"]) == 3
    # Cluster 2: 700 Cr (c4)
    assert len(clusters[1]["members"]) == 1


def test_pairwise_tournament_unanimous_corroboration():
    """Verify 3 identical claims across distinct documents yield 3 corroborating edges and UNANIMOUS_CORROBORATION."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_graph.db"
        ledger = EvidenceLedger(db_path)

        # 3 Documents
        ledger.insert_document(DocumentRecord("D1", "Annual_Report.pdf", "h1", 10))
        ledger.insert_document(DocumentRecord("D2", "Earnings_Call.pdf", "h2", 10))
        ledger.insert_document(DocumentRecord("D3", "Prospectus.pdf", "h3", 10))

        # 3 Chunks
        ledger.insert_evidence_chunks([
            EvidenceChunkRecord("CHK1", "D1", 1, "text", [0, 0, 10, 10], "Revenue INR 500 Cr", "ch1"),
            EvidenceChunkRecord("CHK2", "D2", 2, "text", [0, 0, 10, 10], "Revenue INR 500 Cr", "ch2"),
            EvidenceChunkRecord("CHK3", "D3", 3, "text", [0, 0, 10, 10], "Revenue INR 500 Cr", "ch3"),
        ])

        # 3 Observations
        ledger.insert_observations([
            ObservationRecord("O1", "CHK1", "D1", "Revenue INR 500 Cr", "Delhivery", "revenue", "500 Cr", "numerical", "FY24", "ENTAILED", 1.0),
            ObservationRecord("O2", "CHK2", "D2", "Revenue INR 500 Cr", "Delhivery", "revenue", "500 Cr", "numerical", "FY24", "ENTAILED", 1.0),
            ObservationRecord("O3", "CHK3", "D3", "Revenue INR 500 Cr", "Delhivery", "revenue", "500 Cr", "numerical", "FY24", "ENTAILED", 1.0),
        ])

        # 3 Candidates
        ledger.insert_fact_candidates([
            FactCandidateRecord("F1", "O1", "5000000000", "SCALED_CRORE", "INR", "2023-04-01", "2024-03-31"),
            FactCandidateRecord("F2", "O2", "5000000000", "SCALED_CRORE", "INR", "2023-04-01", "2024-03-31"),
            FactCandidateRecord("F3", "O3", "5000000000", "SCALED_CRORE", "INR", "2023-04-01", "2024-03-31"),
        ])

        group_id = ledger.create_fact_group(
            entity="Delhivery",
            attribute="revenue",
            period_id="2023-04-01_2024-03-31",
            fact_ids=["F1", "F2", "F3"],
            group_id="GRP-CORR-01",
        )

        engine = FactDecisionEngine(ledger=ledger)
        res = engine.process_fact_groups()

        assert res["decisions_evaluated"] == 1
        assert res["verdicts"]["CORROBORATED"] == 1

        # Check claim relationships table
        rels = ledger.get_claim_relationships_for_group(group_id)
        # 3 members -> 3 unique pairs: (F1, F2), (F1, F3), (F2, F3)
        assert len(rels) == 3
        for r in rels:
            assert r.relationship_type == "CORROBORATES"

        # Check decision
        card = ledger.get_decision_card("DEC-" + rels[0].relationship_id[4:]) # query decisions
        decs = ledger.get_decisions()
        assert len(decs) == 1
        assert decs[0]["verdict"] == "CORROBORATED"
        assert decs[0]["decision_strength"] == "HIGH"


def test_pairwise_tournament_conflicting_clusters():
    """Verify 4 claims (two ₹500 Cr, two ₹700 Cr) construct a graph with CONFLICTS_WITH edges and CONTRADICTION verdict."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_conflict_graph.db"
        ledger = EvidenceLedger(db_path)

        ledger.insert_document(DocumentRecord("D1", "Filing1.pdf", "h1", 10))
        ledger.insert_document(DocumentRecord("D2", "Filing2.pdf", "h2", 10))

        ledger.insert_evidence_chunks([
            EvidenceChunkRecord("CHK1", "D1", 1, "text", [0, 0, 10, 10], "500 Cr", "ch1"),
            EvidenceChunkRecord("CHK2", "D2", 2, "text", [0, 0, 10, 10], "500 Cr", "ch2"),
            EvidenceChunkRecord("CHK3", "D1", 3, "text", [0, 0, 10, 10], "700 Cr", "ch3"),
            EvidenceChunkRecord("CHK4", "D2", 4, "text", [0, 0, 10, 10], "700 Cr", "ch4"),
        ])

        ledger.insert_observations([
            ObservationRecord("O1", "CHK1", "D1", "Revenue INR 500 Cr", "Delhivery", "revenue", "500 Cr", "numerical", "FY24", "ENTAILED", 1.0),
            ObservationRecord("O2", "CHK2", "D2", "Revenue INR 500 Cr", "Delhivery", "revenue", "500 Cr", "numerical", "FY24", "ENTAILED", 1.0),
            ObservationRecord("O3", "CHK3", "D1", "Revenue INR 700 Cr", "Delhivery", "revenue", "700 Cr", "numerical", "FY24", "ENTAILED", 1.0),
            ObservationRecord("O4", "CHK4", "D2", "Revenue INR 700 Cr", "Delhivery", "revenue", "700 Cr", "numerical", "FY24", "ENTAILED", 1.0),
        ])

        ledger.insert_fact_candidates([
            FactCandidateRecord("F1", "O1", "5000000000", "SCALED_CRORE", "INR", "2023-04-01", "2024-03-31"),
            FactCandidateRecord("F2", "O2", "5000000000", "SCALED_CRORE", "INR", "2023-04-01", "2024-03-31"),
            FactCandidateRecord("F3", "O3", "7000000000", "SCALED_CRORE", "INR", "2023-04-01", "2024-03-31"),
            FactCandidateRecord("F4", "O4", "7000000000", "SCALED_CRORE", "INR", "2023-04-01", "2024-03-31"),
        ])

        group_id = ledger.create_fact_group(
            entity="Delhivery",
            attribute="revenue",
            period_id="2023-04-01_2024-03-31",
            fact_ids=["F1", "F2", "F3", "F4"],
            group_id="GRP-CONF-01",
        )

        engine = FactDecisionEngine(ledger=ledger)
        res = engine.process_fact_groups()

        assert res["decisions_evaluated"] == 1
        assert res["verdicts"]["CONTRADICTION"] == 1

        # 4 members -> 4*3/2 = 6 pairwise edges
        rels = ledger.get_claim_relationships_for_group(group_id)
        assert len(rels) == 6

        types_counts = {r.relationship_type: 0 for r in rels}
        for r in rels:
            types_counts[r.relationship_type] += 1

        assert types_counts["CORROBORATES"] >= 2  # (F1, F2) and (F3, F4)
        assert types_counts["CONFLICTS_WITH"] >= 4  # cross pairs

        decs = ledger.get_decisions()
        assert decs[0]["verdict"] == "CONTRADICTION"
        assert decs[0]["decision_strength"] == "HIGH"


def test_single_candidate_unresolved():
    """Verify single-member fact group terminates in UNRESOLVED with pending status."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_single.db"
        ledger = EvidenceLedger(db_path)

        ledger.insert_document(DocumentRecord("D1", "Single.pdf", "h1", 5))
        ledger.insert_evidence_chunks([
            EvidenceChunkRecord("CHK1", "D1", 1, "text", [0, 0, 10, 10], "500 Cr", "ch1"),
        ])
        ledger.insert_observations([
            ObservationRecord("O1", "CHK1", "D1", "Revenue INR 500 Cr", "Delhivery", "revenue", "500 Cr", "numerical", "FY24", "ENTAILED", 1.0),
        ])
        ledger.insert_fact_candidates([
            FactCandidateRecord("F1", "O1", "5000000000", "SCALED_CRORE", "INR", "2023-04-01", "2024-03-31"),
        ])
        ledger.create_fact_group(
            entity="Delhivery",
            attribute="revenue",
            period_id="2023-04-01_2024-03-31",
            fact_ids=["F1"],
            group_id="GRP-SINGLE-01",
        )

        engine = FactDecisionEngine(ledger=ledger)
        res = engine.process_fact_groups()

        assert res["decisions_evaluated"] == 1
        assert res["verdicts"]["UNRESOLVED"] == 1

        decs = ledger.get_decisions()
        assert decs[0]["verdict"] == "UNRESOLVED"
        assert decs[0]["decision_strength"] == "LOW"
        assert "Single source claim" in decs[0]["reasoning_summary"]
