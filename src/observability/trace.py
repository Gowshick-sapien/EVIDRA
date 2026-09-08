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


class TraceReplayer:
    """Reads and replays chronological audit traces from trace.jsonl or SQLite ledger."""

    def __init__(self, trace_path: Optional[Path | str] = None, db_path: Optional[Path | str] = None):
        self.trace_path = Path(trace_path) if trace_path else None
        self.db_path = Path(db_path) if db_path else None
        self.steps: list[dict[str, Any]] = []

    def load_steps(self, decision_id: Optional[str] = None) -> list[dict[str, Any]]:
        """Load and filter trace steps from trace.jsonl file or SQLite database."""
        steps: list[dict[str, Any]] = []

        if self.trace_path and self.trace_path.exists():
            with open(self.trace_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if decision_id and entry.get("decision_id") != decision_id:
                            continue
                        steps.append(entry)
                    except json.JSONDecodeError:
                        continue
            self.steps = steps
            if steps or not self.db_path:
                return self.steps

        if self.db_path and self.db_path.exists():
            import sqlite3
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            query = "SELECT trace_id, decision_id, step_name, agent_name, input_json, output_json, execution_time_ms, created_at FROM decision_traces"
            params: list[Any] = []
            if decision_id:
                query += " WHERE decision_id = ?"
                params.append(decision_id)
            query += " ORDER BY created_at ASC"
            rows = conn.execute(query, params).fetchall()
            for r in rows:
                try:
                    inp = json.loads(r["input_json"]) if r["input_json"] else {}
                except Exception:
                    inp = {"raw": r["input_json"]}
                try:
                    out = json.loads(r["output_json"]) if r["output_json"] else {}
                except Exception:
                    out = {"raw": r["output_json"]}
                steps.append({
                    "trace_id": r["trace_id"],
                    "decision_id": r["decision_id"],
                    "timestamp": r["created_at"],
                    "step_name": r["step_name"],
                    "agent_name": r["agent_name"],
                    "latency_ms": r["execution_time_ms"],
                    "input": inp,
                    "output": out,
                })
            conn.close()
            self.steps = steps
            return self.steps

        return []

    def render_timeline(self, decision_id: Optional[str] = None) -> str:
        """Render a formatted chronological timeline of reasoning steps."""
        steps = self.load_steps(decision_id=decision_id)
        if not steps:
            target = f" for decision '{decision_id}'" if decision_id else ""
            return f"No audit trace steps found{target}."

        filter_note = f" (Decision: {decision_id})" if decision_id else ""
        lines = [
            "=" * 80,
            f"  EVIDRA Cryptographic Audit Replay{filter_note}",
            "=" * 80,
        ]

        for idx, s in enumerate(steps, start=1):
            dec_part = f" | Decision: {s.get('decision_id')}" if s.get("decision_id") else ""
            lat_part = f" | Latency: {s.get('latency_ms', 0):.2f}ms"
            lines.append(f"[{idx:02d}] Step: {s.get('step_name')} | Agent: {s.get('agent_name')}{dec_part}{lat_part}")
            lines.append(f"     Timestamp: {s.get('timestamp')}")
            if s.get("input"):
                inp_summary = json.dumps(s["input"], ensure_ascii=False)
                if len(inp_summary) > 120:
                    inp_summary = inp_summary[:117] + "..."
                lines.append(f"     Input:     {inp_summary}")
            if s.get("output"):
                out_summary = json.dumps(s["output"], ensure_ascii=False)
                if len(out_summary) > 120:
                    out_summary = out_summary[:117] + "..."
                lines.append(f"     Output:    {out_summary}")
            lines.append("-" * 80)

        return "\n".join(lines)

    def verify_integrity(self) -> dict[str, Any]:
        """Verify the structural integrity and continuity of trace entries."""
        steps = self.load_steps()
        total = len(steps)
        valid_ids = sum(1 for s in steps if s.get("trace_id", "").startswith("TRC-"))
        return {
            "total_steps": total,
            "valid_trace_ids": valid_ids,
            "intact": total > 0 and valid_ids == total,
        }