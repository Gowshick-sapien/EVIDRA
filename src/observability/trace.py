"""
Observability and run directory management for EVIDRA.
Manages job directories, run manifests, and streaming JSONL audit traces.
"""
from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class RunContext:
    """Manages the lifecycle and isolated file system hierarchy for a job run."""

    def __init__(self, runs_root: Path | str = "runs", job_id: Optional[str] = None):
        self.runs_root = Path(runs_root)
        if job_id:
            self.job_id = job_id
        else:
            now_str = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            short_id = uuid.uuid4().hex[:6]
            self.job_id = f"JOB-{now_str}-{short_id}"

        self.run_dir = self.runs_root / self.job_id
        self.documents_dir = self.run_dir / "documents"
        self.evidence_dir = self.run_dir / "evidence"
        self.reports_dir = self.run_dir / "reports"
        self.traces_dir = self.run_dir / "traces"

        self.db_path = self.run_dir / "ledger.db"
        self.trace_log_path = self.traces_dir / "trace.jsonl"
        self.run_manifest_path = self.run_dir / "run.json"

    def init_run(self, input_files: Optional[list[str]] = None) -> None:
        """Create the directory structure and write the initial run.json manifest."""
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.traces_dir.mkdir(parents=True, exist_ok=True)

        manifest = {
            "job_id": self.job_id,
            "status": "PROCESSING",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
            "input_files": input_files or [],
            "summary": {},
            "errors": [],
        }
        with open(self.run_manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    def complete_run(self, summary: dict[str, Any], status: str = "COMPLETED") -> None:
        """Mark the run as completed and update the manifest."""
        manifest = self.get_manifest()
        manifest["status"] = status
        manifest["completed_at"] = datetime.now(timezone.utc).isoformat()
        manifest["summary"] = summary
        with open(self.run_manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    def fail_run(self, error_message: str) -> None:
        """Record a critical failure into the run manifest."""
        manifest = self.get_manifest()
        manifest["status"] = "FAILED"
        manifest["completed_at"] = datetime.now(timezone.utc).isoformat()
        manifest["errors"].append(error_message)
        with open(self.run_manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    def get_manifest(self) -> dict[str, Any]:
        """Read current run.json manifest."""
        if not self.run_manifest_path.exists():
            return {
                "job_id": self.job_id,
                "status": "PENDING",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": None,
                "input_files": [],
                "summary": {},
                "errors": [],
            }
        with open(self.run_manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def from_existing(cls, run_dir: Path | str) -> RunContext:
        """Load an existing RunContext from a run directory."""
        path = Path(run_dir)
        if not path.exists():
            raise FileNotFoundError(f"Run directory not found: {path}")
        job_id = path.name
        runs_root = path.parent
        ctx = cls(runs_root=runs_root, job_id=job_id)
        return ctx


class TraceLogger:
    """Appends step-by-step audit entries to the JSONL trace log."""

    def __init__(self, trace_file_path: Path | str):
        self.trace_file_path = Path(trace_file_path)
        self.trace_file_path.parent.mkdir(parents=True, exist_ok=True)

    def log_step(
        self,
        step_name: str,
        agent_name: str,
        input_payload: Any,
        output_payload: Any,
        latency_ms: float = 0.0,
        decision_id: Optional[str] = None,
    ) -> str:
        """Append a single structured log line to trace.jsonl."""
        trace_id = f"TRC-{uuid.uuid4().hex[:8]}"
        entry = {
            "trace_id": trace_id,
            "decision_id": decision_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step_name": step_name,
            "agent_name": agent_name,
            "latency_ms": round(latency_ms, 2),
            "input": input_payload,
            "output": output_payload,
        }
        with open(self.trace_file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return trace_id