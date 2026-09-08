"""
Unit tests for the EVIDRA Command Line Interface (CLI).
"""
import tempfile
from pathlib import Path
import pytest

# pyrefly: ignore [missing-import]
from src.cli.main import build_parser, main
# pyrefly: ignore [missing-import]
from src.db.ledger import DecisionRecord, EvidenceLedger
# pyrefly: ignore [missing-import]
from src.observability.trace import RunContext, TraceLogger


def test_cli_help(capsys):
    """Verify that --help renders without errors and lists subcommands."""
    parser = build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--help"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "process" in captured.out
    assert "inspect" in captured.out
    assert "report" in captured.out
    assert "replay" in captured.out
    assert "benchmark" in captured.out


def test_cli_process_single_pdf(capsys):
    """Verify processing a single PDF file creates run directory and ledger."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        pdf_file = tmp_path / "sample.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 mock pdf binary")

        runs_dir = tmp_path / "runs"
        exit_code = main(["process", str(pdf_file), "--out-dir", str(runs_dir)])
        assert exit_code == 0

        captured = capsys.readouterr()
        assert "EVIDRA Fact Knowledge Layer - Job Summary" in captured.out
        assert "Documents Ingested:1" in captured.out

        # Verify run folder created
        run_folders = list(runs_dir.glob("JOB-*"))
        assert len(run_folders) == 1
        assert (run_folders[0] / "ledger.db").exists()


def test_cli_inspect_job(capsys):
    """Verify inspecting decisions from an existing job."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        runs_dir = tmp_path / "runs"
        ctx = RunContext(runs_root=runs_dir)
        ctx.init_run()

        # Seed decision in ledger
        ledger = EvidenceLedger(ctx.db_path)
        gid = ledger.create_fact_group("Acme Corp", "operating_income", "FY2024", [], "GRP-001")
        dec = DecisionRecord("DEC-01", gid, "CONTRADICTION", "HIGH", "Discrepancy of  detected")
        ledger.record_decision(dec)

        # Run inspect command
        exit_code = main(["inspect", ctx.job_id, "--runs-dir", str(runs_dir)])
        assert exit_code == 0

        captured = capsys.readouterr()
        assert "DEC-01" in captured.out
        assert "[CONTRADICTION]" in captured.out
        assert "Acme Corp" in captured.out


def test_cli_report_json(capsys):
    """Verify exporting report in JSON format."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        runs_dir = tmp_path / "runs"
        ctx = RunContext(runs_root=runs_dir)
        ctx.init_run(input_files=["filing.pdf"])

        exit_code = main(["report", ctx.job_id, "--format", "json", "--runs-dir", str(runs_dir)])
        assert exit_code == 0

        captured = capsys.readouterr()
        assert ctx.job_id in captured.out
        assert "filing.pdf" in captured.out


def test_cli_replay(capsys):
    """Verify replaying chronological audit traces from an existing job."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        runs_dir = tmp_path / "runs"
        ctx = RunContext(runs_root=runs_dir)
        ctx.init_run()

        # Seed decision trace via TraceLogger
        tracer = TraceLogger(ctx.trace_log_path)
        tracer.log_step(
            step_name="analyze_variance",
            agent_name="VarianceAnalyzer",
            input_payload={"candidates_count": 2},
            output_payload={"decision_path": "A"},
            latency_ms=0.5,
            decision_id="DEC-01",
        )

        exit_code = main(["replay", ctx.job_id, "--runs-dir", str(runs_dir)])
        assert exit_code == 0

        captured = capsys.readouterr()
        assert "EVIDRA Cryptographic Audit Replay" in captured.out
        assert "DEC-01" in captured.out
        assert "analyze_variance" in captured.out


def test_cli_benchmark(capsys):
    """Verify running evaluation benchmarks via CLI."""
    exit_code = main(["benchmark", "--format", "json"])
    assert exit_code == 0

    captured = capsys.readouterr()
    assert '"accuracy": 100.0' in captured.out
    assert '"hallucination_rate": 0.0' in captured.out