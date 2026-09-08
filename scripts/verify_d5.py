"""
Turnkey diagnostic audit script for Deliverable 5 (D5).
Validates TraceReplayer, ReportGenerator, Evaluator, and the 4 mandatory assignment benchmarks.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

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
    BenchmarkCaseResult,
    EvaluationHarness,
    run_all_benchmarks,
)
# pyrefly: ignore [missing-import]
from src.observability.reports import ReportGenerator
# pyrefly: ignore [missing-import]
from src.observability.trace import RunContext, TraceLogger, TraceReplayer


def main() -> int:
    print("=" * 60)
    print("  EVIDRA Deliverable 5 (D5) Observability & Evaluation Audit")
    print("=" * 60 + "\n")

    # 1. Audit TraceLogger and TraceReplayer
    print("[1/4] Auditing Cryptographic Trace Engine & TraceReplayer...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        trace_file = tmp_path / "trace.jsonl"
        logger = TraceLogger(trace_file)
        t_id = logger.log_step(
            step_name="audit_check",
            agent_name="DiagnosticAgent",
            input_payload={"test": 1},
            output_payload={"status": "OK"},
            latency_ms=1.5,
            decision_id="DEC-TEST",
        )
        assert t_id.startswith("TRC-"), "Trace ID generation failed."

        replayer = TraceReplayer(trace_path=trace_file)
        steps = replayer.load_steps()
        assert len(steps) == 1, f"Expected 1 step, found {len(steps)}"
        assert steps[0]["step_name"] == "audit_check"

        integrity = replayer.verify_integrity()
        assert integrity["intact"] is True, "Trace integrity verification failed."
        timeline = replayer.render_timeline(decision_id="DEC-TEST")
        assert "EVIDRA Cryptographic Audit Replay" in timeline
        print("      PASS: TraceLogger and TraceReplayer validated.")

    # 2. Audit Enhanced ReportGenerator (Markdown & JSON)
    print("[2/4] Auditing Production Reporting Suite (Markdown & JSON)...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        ctx = RunContext(runs_root=tmp_path, job_id="JOB-AUDIT-D5")
        ctx.init_run()
        ledger = EvidenceLedger(ctx.db_path)

        # Ingest a sample contradiction to check bounding box rendering
        ledger.insert_document(DocumentRecord("DOC-01", "report_a.pdf", "hash_a", 10))
        c1 = EvidenceChunkRecord("CHK-01", "DOC-01", 1, "text", [10, 20, 30, 40], "Revenue INR 100Cr", "h01")
        c2 = EvidenceChunkRecord("CHK-02", "DOC-01", 2, "text", [15, 25, 35, 45], "Revenue INR 120Cr", "h02")
        ledger.insert_evidence_chunks([c1, c2])

        obs1 = ObservationRecord("OBS-01", "CHK-01", "DOC-01", "Revenue INR 100Cr", "Corp", "Revenue", "100Cr", "numerical", "FY24", "ENTAILED", 1.0)
        obs2 = ObservationRecord("OBS-02", "CHK-02", "DOC-01", "Revenue INR 120Cr", "Corp", "Revenue", "120Cr", "numerical", "FY24", "ENTAILED", 1.0)
        ledger.insert_observations([obs1, obs2])

        fc1 = FactCandidateRecord("FC-01", "OBS-01", "1000000000", "SCALED_CR", "INR", "2023-04-01", "2024-03-31")
        fc2 = FactCandidateRecord("FC-02", "OBS-02", "1200000000", "SCALED_CR", "INR", "2023-04-01", "2024-03-31")
        ledger.insert_fact_candidates([fc1, fc2])

        gid = ledger.create_fact_group("Corp", "Revenue", "FY24", ["FC-01", "FC-02"], "GRP-AUDIT-01")
        engine = FactDecisionEngine(ledger=ledger)
        engine.process_fact_groups()

        gen = ReportGenerator(ledger=ledger, run_context=ctx)
        reports = gen.generate_all_reports()

        assert reports["summary"].exists(), "summary.md missing."
        assert reports["contradictions"].exists(), "contradictions.md missing."
        assert reports["unresolved"].exists(), "unresolved.md missing."
        assert reports["json"].exists(), "summary.json missing."

        contradictions_text = reports["contradictions"].read_text(encoding="utf-8")
        assert "Coordinates [x0, y0, x1, y1]" in contradictions_text
        assert "[10, 20, 30, 40]" in contradictions_text
        assert "Verbatim Source Evidence Context" in contradictions_text
        print("      PASS: Reports generated with bounding boxes and structured JSON.")

    # 3. Audit Evaluation Framework & Metrics Engine
    print("[3/4] Auditing Evaluation Framework & Metrics Calculation...")
    dummy_cases = [
        BenchmarkCaseResult(case_id="T-01", name="Corroboration", passed=True, expected_verdict="CORROBORATED", actual_verdict="CORROBORATED"),
        BenchmarkCaseResult(case_id="T-02", name="Contradiction", passed=True, expected_verdict="CONTRADICTION", actual_verdict="CONTRADICTION"),
        BenchmarkCaseResult(case_id="T-03", name="Reconciliation", passed=True, expected_verdict="RECONCILED", actual_verdict="RECONCILED"),
        BenchmarkCaseResult(case_id="T-04", name="Failure Handling", passed=True, expected_verdict="UNRESOLVED", actual_verdict="UNRESOLVED"),
    ]
    metrics = EvaluationHarness.compute_metrics(dummy_cases)
    assert metrics.accuracy == 100.0
    assert metrics.hallucination_rate == 0.0
    scorecard = EvaluationHarness.render_scorecard(metrics)
    assert "**Overall Accuracy:** 100.0%" in scorecard
    print("      PASS: Metric calculations and scorecard generation verified.")

    # 4. Execute Mandatory Assignment Benchmark Scenarios
    print("[4/4] Executing Mandatory Assignment Benchmark Scenarios...")
    bench_metrics = run_all_benchmarks()
    assert bench_metrics.total_cases == 4, f"Expected 4 benchmarks, got {bench_metrics.total_cases}"
    assert bench_metrics.passed_cases == 4, f"Only {bench_metrics.passed_cases}/4 benchmarks passed."
    assert bench_metrics.accuracy == 100.0, f"Accuracy was {bench_metrics.accuracy}%"
    assert bench_metrics.hallucination_rate == 0.0, f"Hallucination rate was {bench_metrics.hallucination_rate}%"

    for r in bench_metrics.case_results:
        print(f"      - {r.case_id}: {r.name} -> {r.actual_verdict} (Latency: {r.latency_ms:.1f}ms) [PASS]")

    print("\n" + "=" * 60)
    print("  ALL DELIVERABLE 5 (D5) QUALITY CHECKS PASSED")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
