"""
Evaluation framework and benchmark metrics engine for EVIDRA (Layer 4).
Runs benchmark scenarios and evaluates precision, recall, accuracy,
and hallucination rate across epistemic verdicts.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field


class BenchmarkCase(BaseModel):
    """Specification of a standardized financial evaluation case."""
    case_id: str = Field(..., description="Unique case identifier (e.g. BENCH-01)")
    name: str = Field(..., description="Human-readable scenario title")
    description: str = Field(..., description="Detailed financial and accounting context")
    target_entity: str = Field(..., description="Corporate entity name to evaluate")
    target_attribute: str = Field(..., description="Financial metric or attribute")
    target_period: str = Field(..., description="Reporting interval or date")
    expected_verdict: str = Field(..., description="Ground truth verdict (CORROBORATED, CONTRADICTION, RECONCILED, UNRESOLVED)")
    expected_strength: Optional[str] = Field(None, description="Expected confidence level (HIGH, MEDIUM, LOW, INSUFFICIENT)")
    expected_hypothesis: Optional[str] = Field(None, description="Expected winning hypothesis class")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Supplementary test parameters")


class BenchmarkCaseResult(BaseModel):
    """Result of evaluating an individual benchmark scenario."""
    case_id: str
    name: str
    passed: bool
    expected_verdict: str
    actual_verdict: str
    expected_strength: Optional[str] = None
    actual_strength: Optional[str] = None
    winning_hypothesis: Optional[str] = None
    reasoning_summary: str = ""
    latency_ms: float = 0.0
    errors: list[str] = Field(default_factory=list)


class EvaluationMetrics(BaseModel):
    """Aggregated quantitative performance metrics for a benchmark run."""
    total_cases: int
    passed_cases: int
    accuracy: float
    precision_by_verdict: dict[str, float] = Field(default_factory=dict)
    recall_by_verdict: dict[str, float] = Field(default_factory=dict)
    f1_by_verdict: dict[str, float] = Field(default_factory=dict)
    hallucination_rate: float = 0.0  # Percentage of ungrounded reconciliations emitted
    case_results: list[BenchmarkCaseResult] = Field(default_factory=list)


class EvaluationHarness:
    """Calculates evaluation metrics across benchmark results."""

    @staticmethod
    def compute_metrics(results: list[BenchmarkCaseResult]) -> EvaluationMetrics:
        """Compute precision, recall, F1, accuracy, and hallucination rate."""
        total = len(results)
        if total == 0:
            return EvaluationMetrics(total_cases=0, passed_cases=0, accuracy=0.0)

        passed = sum(1 for r in results if r.passed)
        accuracy = round((passed / total) * 100.0, 2)

        verdicts = ["CORROBORATED", "CONTRADICTION", "RECONCILED", "UNRESOLVED"]
        tp: dict[str, int] = {v: 0 for v in verdicts}
        fp: dict[str, int] = {v: 0 for v in verdicts}
        fn: dict[str, int] = {v: 0 for v in verdicts}

        ungrounded_count = 0
        for r in results:
            exp = r.expected_verdict
            act = r.actual_verdict

            if exp == act:
                tp[exp] = tp.get(exp, 0) + 1
            else:
                fp[act] = fp.get(act, 0) + 1
                fn[exp] = fn.get(exp, 0) + 1

            # Hallucination check: emitted RECONCILED when ground truth was CONTRADICTION or UNRESOLVED
            if act == "RECONCILED" and exp in ("CONTRADICTION", "UNRESOLVED"):
                ungrounded_count += 1

        precision: dict[str, float] = {}
        recall: dict[str, float] = {}
        f1: dict[str, float] = {}

        for v in verdicts:
            true_pos = tp[v]
            false_pos = fp[v]
            false_neg = fn[v]

            p = (true_pos / (true_pos + false_pos)) if (true_pos + false_pos) > 0 else 1.0
            r = (true_pos / (true_pos + false_neg)) if (true_pos + false_neg) > 0 else 1.0
            f = (2 * p * r / (p + r)) if (p + r) > 0 else 1.0

            precision[v] = round(p * 100.0, 2)
            recall[v] = round(r * 100.0, 2)
            f1[v] = round(f * 100.0, 2)

        hallucination_rate = round((ungrounded_count / total) * 100.0, 2)

        return EvaluationMetrics(
            total_cases=total,
            passed_cases=passed,
            accuracy=accuracy,
            precision_by_verdict=precision,
            recall_by_verdict=recall,
            f1_by_verdict=f1,
            hallucination_rate=hallucination_rate,
            case_results=results,
        )

    @staticmethod
    def render_scorecard(metrics: EvaluationMetrics) -> str:
        """Render clean Markdown evaluation scorecard."""
        lines = [
            "# EVIDRA Evaluation Benchmark Scorecard",
            "",
            f"- **Total Scenarios Evaluated:** {metrics.total_cases}",
            f"- **Passed Scenarios:** {metrics.passed_cases}",
            f"- **Overall Accuracy:** {metrics.accuracy:.1f}%",
            f"- **Hallucination Rate:** {metrics.hallucination_rate:.1f}%",
            "",
            "## 1. Metric Breakdown by Epistemic Verdict",
            "",
            "| Verdict Class | Precision | Recall | F1 Score |",
            "| :--- | :--- | :--- | :--- |",
        ]

        for v in ["CORROBORATED", "CONTRADICTION", "RECONCILED", "UNRESOLVED"]:
            p = metrics.precision_by_verdict.get(v, 100.0)
            r = metrics.recall_by_verdict.get(v, 100.0)
            f = metrics.f1_by_verdict.get(v, 100.0)
            lines.append(f"| **{v}** | {p:.1f}% | {r:.1f}% | {f:.1f}% |")

        lines.extend([
            "",
            "## 2. Individual Scenario Results",
            "",
            "| Case ID | Scenario Name | Expected | Actual | Latency | Status |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ])

        for c in metrics.case_results:
            status = "PASS" if c.passed else "FAIL"
            lines.append(
                f"| `{c.case_id}` | {c.name} | **{c.expected_verdict}** | **{c.actual_verdict}** | {c.latency_ms:.2f}ms | **{status}** |"
            )

        lines.append("")
        return "\n".join(lines)


def run_all_benchmarks() -> EvaluationMetrics:
    """Execute the four mandatory evaluation benchmarks and return metrics."""
    import tempfile
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
    from src.observability.trace import TraceLogger

    results: list[BenchmarkCaseResult] = []

    # Scenario 1: Dual-Source Corroboration
    t0 = time.perf_counter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        ledger = EvidenceLedger(tmp_path / "ledger.db")
        tracer = TraceLogger(tmp_path / "trace.jsonl")
        ledger.insert_document(DocumentRecord("DOC-PR", "press_release.pdf", "hash_pr", 4))
        ledger.insert_document(DocumentRecord("DOC-10K", "annual_report.pdf", "hash_10k", 85))
        c1 = EvidenceChunkRecord("CHK-01", "DOC-PR", 1, "text", [50, 100, 400, 120], "Acme Corp Revenue USD 12,400M FY2024", "h1")
        c2 = EvidenceChunkRecord("CHK-02", "DOC-10K", 42, "table", [70, 200, 520, 380], "Total Revenue: USD 12,400 million FY2024", "h2")
        ledger.insert_evidence_chunks([c1, c2])
        obs1 = ObservationRecord("OBS-01", "CHK-01", "DOC-PR", "Revenue USD 12,400M", "Acme Corp", "Revenue", "USD 12,400M", "numerical", "FY2024", "ENTAILED", 1.0)
        obs2 = ObservationRecord("OBS-02", "CHK-02", "DOC-10K", "Revenue USD 12,400M", "Acme Corp", "Revenue", "USD 12,400 million", "numerical", "FY2024", "ENTAILED", 1.0)
        ledger.insert_observations([obs1, obs2])
        fc1 = FactCandidateRecord("FC-01", "OBS-01", "12400000000.00", "SCALED_MILLION", "USD", "2024-01-01", "2024-12-31")
        fc2 = FactCandidateRecord("FC-02", "OBS-02", "12400000000.00", "SCALED_MILLION", "USD", "2024-01-01", "2024-12-31")
        ledger.insert_fact_candidates([fc1, fc2])
        ledger.create_fact_group("Acme Corp", "Revenue", "FY2024", ["FC-01", "FC-02"], "GRP-SCEN-1")
        engine = FactDecisionEngine(ledger=ledger, tracer=tracer)
        engine.process_fact_groups()
        decs = ledger.get_decisions()
        v = decs[0]["verdict"] if decs else "UNRESOLVED"
        s = decs[0]["decision_strength"] if decs else "LOW"
        r_sum = decs[0]["reasoning_summary"] if decs else ""
    lat1 = (time.perf_counter() - t0) * 1000.0
    results.append(BenchmarkCaseResult(
        case_id="BENCH-01",
        name="Dual-Source Corroboration Benchmark",
        passed=(v == "CORROBORATED"),
        expected_verdict="CORROBORATED",
        actual_verdict=v,
        expected_strength="HIGH",
        actual_strength=s,
        reasoning_summary=r_sum,
        latency_ms=round(lat1, 2),
    ))

    # Scenario 2: Direct Numerical Contradiction
    t0 = time.perf_counter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        ledger = EvidenceLedger(tmp_path / "ledger.db")
        tracer = TraceLogger(tmp_path / "trace.jsonl")
        ledger.insert_document(DocumentRecord("DOC-A", "doc_a.pdf", "hash_a", 5))
        ledger.insert_document(DocumentRecord("DOC-B", "doc_b.pdf", "hash_b", 5))
        c1 = EvidenceChunkRecord("CHK-11", "DOC-A", 2, "text", [50, 100, 400, 120], "Acme Operating Profit USD 450M", "h11")
        c2 = EvidenceChunkRecord("CHK-12", "DOC-B", 8, "table", [70, 150, 480, 300], "Acme Operating Profit USD 520M", "h12")
        ledger.insert_evidence_chunks([c1, c2])
        obs1 = ObservationRecord("OBS-11", "CHK-11", "DOC-A", "Operating Profit USD 450M", "Acme Corp", "Operating Profit", "USD 450M", "numerical", "FY2024", "ENTAILED", 1.0)
        obs2 = ObservationRecord("OBS-12", "CHK-12", "DOC-B", "Operating Profit USD 520M", "Acme Corp", "Operating Profit", "USD 520M", "numerical", "FY2024", "ENTAILED", 1.0)
        ledger.insert_observations([obs1, obs2])
        fc1 = FactCandidateRecord("FC-11", "OBS-11", "450000000.00", "SCALED_MILLION", "USD", "2024-01-01", "2024-12-31")
        fc2 = FactCandidateRecord("FC-12", "OBS-12", "520000000.00", "SCALED_MILLION", "USD", "2024-01-01", "2024-12-31")
        ledger.insert_fact_candidates([fc1, fc2])
        ledger.create_fact_group("Acme Corp", "Operating Profit", "FY2024", ["FC-11", "FC-12"], "GRP-SCEN-2")
        engine = FactDecisionEngine(ledger=ledger, tracer=tracer)
        engine.process_fact_groups()
        decs = ledger.get_decisions()
        v = decs[0]["verdict"] if decs else "UNRESOLVED"
        s = decs[0]["decision_strength"] if decs else "LOW"
        r_sum = decs[0]["reasoning_summary"] if decs else ""
    lat2 = (time.perf_counter() - t0) * 1000.0
    results.append(BenchmarkCaseResult(
        case_id="BENCH-02",
        name="Direct Numerical Contradiction Benchmark",
        passed=(v == "CONTRADICTION"),
        expected_verdict="CONTRADICTION",
        actual_verdict=v,
        expected_strength="HIGH",
        actual_strength=s,
        reasoning_summary=r_sum,
        latency_ms=round(lat2, 2),
    ))

    # Scenario 3: Defensible Reconciliation (Accounting Basis)
    t0 = time.perf_counter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        ledger = EvidenceLedger(tmp_path / "ledger.db")
        tracer = TraceLogger(tmp_path / "trace.jsonl")
        ledger.insert_document(DocumentRecord("DOC-GA", "annual_report.pdf", "hash_ga", 100))
        ledger.insert_document(DocumentRecord("DOC-NG", "q4_presentation.pdf", "hash_ng", 25))
        c1 = EvidenceChunkRecord("CHK-21", "DOC-GA", 35, "table", [50, 100, 500, 300], "Operating Income GAAP INR 81,415.38 Lakhs", "h21")
        c2 = EvidenceChunkRecord("CHK-22", "DOC-NG", 12, "table", [60, 120, 520, 320], "Adjusted EBITDA Non-GAAP INR 85,942.34 Lakhs", "h22")
        ledger.insert_evidence_chunks([c1, c2])
        obs1 = ObservationRecord("OBS-21", "CHK-21", "DOC-GA", "Operating Income GAAP", "Delhivery", "Operating Income", "81,415.38", "numerical", "FY24", "ENTAILED", 1.0)
        obs2 = ObservationRecord("OBS-22", "CHK-22", "DOC-NG", "Adjusted EBITDA Non-GAAP", "Delhivery", "Operating Income", "85,942.34", "numerical", "FY24", "ENTAILED", 1.0)
        ledger.insert_observations([obs1, obs2])
        fc1 = FactCandidateRecord("FC-21", "OBS-21", "81415.38", "SCALED_LAKH", "INR", "2023-04-01", "2024-03-31")
        fc2 = FactCandidateRecord("FC-22", "OBS-22", "85942.34", "SCALED_LAKH", "INR", "2023-04-01", "2024-03-31")
        ledger.insert_fact_candidates([fc1, fc2])
        ledger.create_fact_group("Delhivery", "Operating Income", "FY24", ["FC-21", "FC-22"], "GRP-SCEN-3")
        engine = FactDecisionEngine(ledger=ledger, tracer=tracer)
        engine.process_fact_groups()
        decs = ledger.get_decisions()
        v = decs[0]["verdict"] if decs else "UNRESOLVED"
        s = decs[0]["decision_strength"] if decs else "LOW"
        r_sum = decs[0]["reasoning_summary"] if decs else ""
    lat3 = (time.perf_counter() - t0) * 1000.0
    results.append(BenchmarkCaseResult(
        case_id="BENCH-03",
        name="Defensible Reconciliation Benchmark",
        passed=(v == "RECONCILED"),
        expected_verdict="RECONCILED",
        actual_verdict=v,
        expected_strength="HIGH",
        actual_strength=s,
        reasoning_summary=r_sum,
        latency_ms=round(lat3, 2),
    ))

    # Scenario 4: Defensive Failure Handling
    t0 = time.perf_counter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        ledger = EvidenceLedger(tmp_path / "ledger.db")
        tracer = TraceLogger(tmp_path / "trace.jsonl")
        ledger.insert_document(DocumentRecord("DOC-C", "partial.pdf", "hash_c", 5))
        c1 = EvidenceChunkRecord("CHK-31", "DOC-C", 1, "text", [50, 100, 400, 120], "Isolated Metric USD 320M", "h31")
        ledger.insert_evidence_chunks([c1])
        obs1 = ObservationRecord("OBS-31", "CHK-31", "DOC-C", "Isolated Metric", "Acme Corp", "Net Cash", "USD 320M", "numerical", "FY2024", "ENTAILED", 1.0)
        ledger.insert_observations([obs1])
        fc1 = FactCandidateRecord("FC-31", "OBS-31", "320000000.00", "SCALED_MILLION", "USD", "2024-01-01", "2024-12-31")
        ledger.insert_fact_candidates([fc1])
        ledger.create_fact_group("Acme Corp", "Net Cash", "FY2024", ["FC-31"], "GRP-SCEN-4")
        engine = FactDecisionEngine(ledger=ledger, tracer=tracer)
        engine.process_fact_groups()
        decs = ledger.get_decisions()
        v = decs[0]["verdict"] if decs else "UNRESOLVED"
        s = decs[0]["decision_strength"] if decs else "LOW"
        r_sum = decs[0]["reasoning_summary"] if decs else ""
    lat4 = (time.perf_counter() - t0) * 1000.0
    results.append(BenchmarkCaseResult(
        case_id="BENCH-04",
        name="Defensive Failure Handling Benchmark",
        passed=(v == "UNRESOLVED"),
        expected_verdict="UNRESOLVED",
        actual_verdict=v,
        expected_strength="LOW",
        actual_strength=s,
        reasoning_summary=r_sum,
        latency_ms=round(lat4, 2),
    ))

    return EvaluationHarness.compute_metrics(results)
