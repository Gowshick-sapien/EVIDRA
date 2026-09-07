"""
Unit tests for RunContext and TraceLogger.
"""
import json
import tempfile
from pathlib import Path
import pytest

from src.observability.trace import RunContext, TraceLogger


def test_run_context_lifecycle():
    with tempfile.TemporaryDirectory() as tmp_dir:
        ctx = RunContext(runs_root=tmp_dir)
        assert ctx.run_dir.name.startswith("JOB-")
        
        ctx.init_run(input_files=["doc1.pdf", "doc2.pdf"])
        assert ctx.run_dir.exists()
        assert ctx.documents_dir.exists()
        assert ctx.evidence_dir.exists()
        assert ctx.reports_dir.exists()
        assert ctx.traces_dir.exists()
        assert ctx.run_manifest_path.exists()

        manifest = ctx.get_manifest()
        assert manifest["status"] == "PROCESSING"
        assert manifest["input_files"] == ["doc1.pdf", "doc2.pdf"]

        # Complete run
        ctx.complete_run(summary={"facts": 10, "decisions": 5})
        updated = ctx.get_manifest()
        assert updated["status"] == "COMPLETED"
        assert updated["summary"]["facts"] == 10
        assert updated["completed_at"] is not None


def test_trace_logger():
    with tempfile.TemporaryDirectory() as tmp_dir:
        trace_file = Path(tmp_dir) / "trace.jsonl"
        logger = TraceLogger(trace_file)

        t1 = logger.log_step("ExtractNumerical", "NumericalExtractor", {"text": "rev"}, {"val": 100}, 12.5)
        assert t1.startswith("TRC-")

        t2 = logger.log_step("AdversarialChallenge", "AdversarialSkeptic", {"hyp": "H1"}, {"status": "SURVIVED"}, 45.2, decision_id="DEC-01")
        assert t2.startswith("TRC-")

        # Read back JSONL
        with open(trace_file, "r", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f]
        
        assert len(lines) == 2
        assert lines[0]["step_name"] == "ExtractNumerical"
        assert lines[1]["decision_id"] == "DEC-01"
        assert lines[1]["output"]["status"] == "SURVIVED"