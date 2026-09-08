"""
Mandatory Assignment Evaluation Scenarios (Layer 4 - D5.4).
Exhaustively tests the four required benchmark cases:
1. Corroboration Benchmark: Dual-source validation yielding CORROBORATED
2. Direct Contradiction Benchmark: Irreconcilable conflict yielding CONTRADICTION
3. Defensible Reconciliation Benchmark: Stated differences yielding RECONCILED
4. Defensive Failure Handling Benchmark: Corrupt text/single source yielding UNRESOLVED
"""
from __future__ import annotations

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
from src.decision.engine import FactDecisionEngine
# pyrefly: ignore [missing-import]
from src.observability.evaluator import (
    BenchmarkCase,
    BenchmarkCaseResult,
    EvaluationHarness,
)
# pyrefly: ignore [missing-import]
from src.observability.trace import RunContext, TraceLogger


def test_benchmark_scenario_1_dual_source_corroboration():
    """Scenario 1: Identical metrics across Press Release and Annual Report yield CORROBORATED."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        ledger = EvidenceLedger(tmp_path / "ledger.db")
        tracer = TraceLogger(tmp_path / "trace.jsonl")

        # Ingest documents: Press Release & 10-K
        ledger.insert_document(DocumentRecord("DOC-PR", "q4_press_release.pdf", "hash_pr", 4))
        ledger.insert_document(DocumentRecord("DOC-10K", "annual_report_10k.pdf", "hash_10k", 85))

        # Ingest evidence chunks with spatial coordinates
        c1 = EvidenceChunkRecord("CHK-01", "DOC-PR", 1, "text", [50, 100, 400, 120], "Acme Corp Total Revenue USD 12,400M for FY2024", "h1")
        c2 = EvidenceChunkRecord("CHK-02", "DOC-10K", 42, "table", [70, 200, 520, 380], "Total Revenue: USD 12,400 million (Year ended Dec 31, 2024)", "h2")
        ledger.insert_evidence_chunks([c1, c2])

        # Observations
        obs1 = ObservationRecord("OBS-01", "CHK-01", "DOC-PR", "Acme Corp Total Revenue USD 12,400M", "Acme Corp", "Revenue", "USD 12,400M", "numerical", "FY2024", "ENTAILED", 1.0)
        obs2 = ObservationRecord("OBS-02", "CHK-02", "DOC-10K", "Total Revenue: USD 12,400 million", "Acme Corp", "Revenue", "USD 12,400 million", "numerical", "FY2024", "ENTAILED", 1.0)
        ledger.insert_observations([obs1, obs2])

        # Normalized Fact Candidates
        fc1 = FactCandidateRecord("FC-01", "OBS-01", "12400000000.00", "SCALED_MILLION", "USD", "2024-01-01", "2024-12-31")
        fc2 = FactCandidateRecord("FC-02", "OBS-02", "12400000000.00", "SCALED_MILLION", "USD", "2024-01-01", "2024-12-31")
        ledger.insert_fact_candidates([fc1, fc2])

        # Form Fact Group
        gid = ledger.create_fact_group("Acme Corp", "Revenue", "FY2024", ["FC-01", "FC-02"], "GRP-SCENARIO-1")

        # Execute Decision Engine
        engine = FactDecisionEngine(ledger=ledger, tracer=tracer)
        res = engine.process_fact_groups()
        assert res["decisions_evaluated"] == 1

        # Verify Decision Card
        decs = ledger.get_decisions()
        assert len(decs) == 1
        d = decs[0]
        assert d["verdict"] == "CORROBORATED"
        assert d["decision_strength"] == "HIGH"

        card = ledger.get_decision_card(d["decision_id"])
        assert card is not None
        assert len(card["claims"]) == 2
        # Verify dual physical document provenance
        doc_sources = {c["document_id"] for c in card["claims"]}
        assert doc_sources == {"DOC-PR", "DOC-10K"}


def test_benchmark_scenario_2_direct_contradiction():
    """Scenario 2: Discrepant figures under identical context with no valid reconciliation yield CONTRADICTION."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        ledger = EvidenceLedger(tmp_path / "ledger.db")
        tracer = TraceLogger(tmp_path / "trace.jsonl")

        ledger.insert_document(DocumentRecord("DOC-A", "earnings_release.pdf", "hash_a", 5))
        ledger.insert_document(DocumentRecord("DOC-B", "investor_deck.pdf", "hash_b", 20))

        c1 = EvidenceChunkRecord("CHK-11", "DOC-A", 2, "text", [50, 100, 400, 120], "Acme Operating Profit USD 450M for FY2024", "h11")
        c2 = EvidenceChunkRecord("CHK-12", "DOC-B", 8, "table", [70, 150, 480, 300], "Acme Operating Profit USD 520M for FY2024", "h12")
        ledger.insert_evidence_chunks([c1, c2])

        obs1 = ObservationRecord("OBS-11", "CHK-11", "DOC-A", "Acme Operating Profit USD 450M", "Acme Corp", "Operating Profit", "USD 450M", "numerical", "FY2024", "ENTAILED", 1.0)
        obs2 = ObservationRecord("OBS-12", "CHK-12", "DOC-B", "Acme Operating Profit USD 520M", "Acme Corp", "Operating Profit", "USD 520M", "numerical", "FY2024", "ENTAILED", 1.0)
        ledger.insert_observations([obs1, obs2])

        # 450M vs 520M: material discrepancy > 0.01% with identical context
        fc1 = FactCandidateRecord("FC-11", "OBS-11", "450000000.00", "SCALED_MILLION", "USD", "2024-01-01", "2024-12-31")
        fc2 = FactCandidateRecord("FC-12", "OBS-12", "520000000.00", "SCALED_MILLION", "USD", "2024-01-01", "2024-12-31")
        ledger.insert_fact_candidates([fc1, fc2])

        gid = ledger.create_fact_group("Acme Corp", "Operating Profit", "FY2024", ["FC-11", "FC-12"], "GRP-SCENARIO-2")

        engine = FactDecisionEngine(ledger=ledger, tracer=tracer)
        res = engine.process_fact_groups()
        assert res["decisions_evaluated"] == 1

        decs = ledger.get_decisions()
        assert len(decs) == 1
        d = decs[0]
        assert d["verdict"] == "CONTRADICTION"
        assert d["decision_strength"] == "HIGH"


def test_benchmark_scenario_3_defensible_reconciliation_accounting_basis():
    """Scenario 3: Non-GAAP vs GAAP accounting difference yields RECONCILED with hypothesis explanation."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        ledger = EvidenceLedger(tmp_path / "ledger.db")
        tracer = TraceLogger(tmp_path / "trace.jsonl")

        ledger.insert_document(DocumentRecord("DOC-GA", "annual_report_gaap.pdf", "hash_ga", 100))
        ledger.insert_document(DocumentRecord("DOC-NG", "q4_presentation_nongaap.pdf", "hash_ng", 25))

        c1 = EvidenceChunkRecord("CHK-21", "DOC-GA", 35, "table", [50, 100, 500, 300], "Operating Income under Ind AS / GAAP: INR 81,415.38 Lakhs", "h21")
        c2 = EvidenceChunkRecord("CHK-22", "DOC-NG", 12, "table", [60, 120, 520, 320], "Adjusted EBITDA (Non-GAAP exclusion of share-based payment): INR 85,942.34 Lakhs", "h22")
        ledger.insert_evidence_chunks([c1, c2])

        # Observation 1 has GAAP context, Observation 2 has NON_GAAP context
        obs1 = ObservationRecord(
            "OBS-21", "CHK-21", "DOC-GA", "Operating Income under Ind AS / GAAP: INR 81,415.38 Lakhs",
            "Delhivery", "Operating Income", "81,415.38", "numerical", "FY24", "ENTAILED", 1.0
        )
        obs2 = ObservationRecord(
            "OBS-22", "CHK-22", "DOC-NG", "Adjusted EBITDA (Non-GAAP): INR 85,942.34 Lakhs",
            "Delhivery", "Operating Income", "85,942.34", "numerical", "FY24", "ENTAILED", 1.0
        )
        ledger.insert_observations([obs1, obs2])

        fc1 = FactCandidateRecord("FC-21", "OBS-21", "81415.38", "SCALED_LAKH", "INR", "2023-04-01", "2024-03-31")
        fc2 = FactCandidateRecord("FC-22", "OBS-22", "85942.34", "SCALED_LAKH", "INR", "2023-04-01", "2024-03-31")
        ledger.insert_fact_candidates([fc1, fc2])

        gid = ledger.create_fact_group("Delhivery", "Operating Income", "FY24", ["FC-21", "FC-22"], "GRP-SCENARIO-3")

        engine = FactDecisionEngine(ledger=ledger, tracer=tracer)
        res = engine.process_fact_groups()
        assert res["decisions_evaluated"] == 1

        decs = ledger.get_decisions()
        assert len(decs) == 1
        d = decs[0]
        assert d["verdict"] == "RECONCILED"
        assert d["decision_strength"] == "HIGH"

        card = ledger.get_decision_card(d["decision_id"])
        assert card is not None
        assert any(h["explanation_type"] == "ACCOUNTING_BASIS" for h in card["hypotheses"])


def test_benchmark_scenario_4_defensive_failure_handling():
    """Scenario 4: Single candidate observation gracefully yields UNRESOLVED without crashing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        ledger = EvidenceLedger(tmp_path / "ledger.db")
        tracer = TraceLogger(tmp_path / "trace.jsonl")

        ledger.insert_document(DocumentRecord("DOC-C", "partial_filing.pdf", "hash_c", 10))
        c1 = EvidenceChunkRecord("CHK-31", "DOC-C", 5, "text", [50, 100, 400, 120], "Isolated Metric: Net Cash USD 320M", "h31")
        ledger.insert_evidence_chunks([c1])

        obs1 = ObservationRecord("OBS-31", "CHK-31", "DOC-C", "Isolated Metric: Net Cash USD 320M", "Acme Corp", "Net Cash", "USD 320M", "numerical", "FY2024", "ENTAILED", 1.0)
        ledger.insert_observations([obs1])

        fc1 = FactCandidateRecord("FC-31", "OBS-31", "320000000.00", "SCALED_MILLION", "USD", "2024-01-01", "2024-12-31")
        ledger.insert_fact_candidates([fc1])

        gid = ledger.create_fact_group("Acme Corp", "Net Cash", "FY2024", ["FC-31"], "GRP-SCENARIO-4")

        engine = FactDecisionEngine(ledger=ledger, tracer=tracer)
        res = engine.process_fact_groups()
        assert res["decisions_evaluated"] == 1

        decs = ledger.get_decisions()
        assert len(decs) == 1
        d = decs[0]
        assert d["verdict"] == "UNRESOLVED"
        assert d["decision_strength"] == "LOW"


def test_evaluation_harness_metrics_computation():
    """Verify EvaluationHarness accurately computes accuracy, precision, recall, and hallucination rate."""
    cases = [
        BenchmarkCaseResult(
            case_id="BENCH-01",
            name="Corroboration Test",
            passed=True,
            expected_verdict="CORROBORATED",
            actual_verdict="CORROBORATED",
            latency_ms=1.2,
        ),
        BenchmarkCaseResult(
            case_id="BENCH-02",
            name="Contradiction Test",
            passed=True,
            expected_verdict="CONTRADICTION",
            actual_verdict="CONTRADICTION",
            latency_ms=2.5,
        ),
        BenchmarkCaseResult(
            case_id="BENCH-03",
            name="Reconciliation Test",
            passed=True,
            expected_verdict="RECONCILED",
            actual_verdict="RECONCILED",
            latency_ms=3.1,
        ),
        BenchmarkCaseResult(
            case_id="BENCH-04",
            name="Defensive Failure Test",
            passed=True,
            expected_verdict="UNRESOLVED",
            actual_verdict="UNRESOLVED",
            latency_ms=0.8,
        ),
    ]

    metrics = EvaluationHarness.compute_metrics(cases)
    assert metrics.total_cases == 4
    assert metrics.passed_cases == 4
    assert metrics.accuracy == 100.0
    assert metrics.hallucination_rate == 0.0
    for v in ["CORROBORATED", "CONTRADICTION", "RECONCILED", "UNRESOLVED"]:
        assert metrics.precision_by_verdict[v] == 100.0
        assert metrics.recall_by_verdict[v] == 100.0

    scorecard = EvaluationHarness.render_scorecard(metrics)
    assert "# EVIDRA Evaluation Benchmark Scorecard" in scorecard
    assert "**Overall Accuracy:** 100.0%" in scorecard
    assert "**Hallucination Rate:** 0.0%" in scorecard
