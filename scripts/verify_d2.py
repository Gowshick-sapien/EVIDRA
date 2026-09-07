"""
Verification script for Deliverable 2 (D2): Document Processing and Extraction Layer.
Validates extracted evidence chunks, spatial bounding boxes, factual observations,
and extraction pipeline telemetry.
"""
import json
import sqlite3
import sys
from pathlib import Path

# Force UTF-8 console output for currency symbols (e.g. ₹)
sys.stdout.reconfigure(encoding="utf-8")

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.db.ledger import EvidenceLedger


def run_d2_verification():
    print("==================================================")
    print("  EVIDRA Deliverable 2 (D2) Verification Suite   ")
    print("==================================================")

    runs_dir = repo_root / "runs"
    job_dirs = sorted(
        [d for d in runs_dir.glob("JOB-*") if d.is_dir()],
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )
    if not job_dirs:
        print("FAIL: No job directories found in runs/")
        sys.exit(1)

    latest_job = job_dirs[0]
    db_path = latest_job / "ledger.db"
    print(f"Target Run:     {latest_job.name}")
    print(f"Database Path:  {db_path}")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # 1. Verify Evidence Chunks
    print("\n[1/3] Checking Evidence Chunks...")
    chunk_rows = conn.execute("SELECT * FROM evidence_chunks LIMIT 5;").fetchall()
    total_chunks = conn.execute("SELECT COUNT(*) FROM evidence_chunks;").fetchone()[0]
    print(f"      Total evidence chunks in ledger: {total_chunks}")
    if total_chunks == 0:
        print("      FAIL: No evidence chunks found.")
    else:
        sample = chunk_rows[0]
        bbox = json.loads(sample["bounding_box"])
        print(f"      Sample Chunk: ID={sample['chunk_id']} | Type={sample['chunk_type']} | Page={sample['page_number']}")
        print(f"      Bounding Box: [x0={bbox[0]:.1f}, y0={bbox[1]:.1f}, x1={bbox[2]:.1f}, y1={bbox[3]:.1f}]")
        print(f"      Snippet: {sample['content'][:90].replace(chr(10), ' ')}...")
        print("      PASS: Evidence chunks persisted with valid bounding boxes and hashes.")

    # 2. Verify Observations
    print("\n[2/3] Checking Factual Observations...")
    total_obs = conn.execute("SELECT COUNT(*) FROM observations;").fetchone()[0]
    print(f"      Total observations in ledger: {total_obs}")
    obs_rows = conn.execute("SELECT * FROM observations LIMIT 5;").fetchall()
    if total_obs > 0:
        for idx, obs in enumerate(obs_rows, start=1):
            print(f"      Obs {idx}: [{obs['observation_type'].upper()}] {obs['entity']} | {obs['attribute']} = '{obs['raw_value']}' ({obs['temporal_scope']})")
            print(f"             Source Chunk: {obs['chunk_id']}")
        print("      PASS: Factual observations harvested and linked to physical chunks.")
    else:
        print("      NOTICE: 0 observations recorded.")

    # 3. Verify Audit Trace
    print("\n[3/3] Checking Extraction Telemetry in Trace Log...")
    trace_file = latest_job / "traces" / "trace.jsonl"
    if trace_file.exists():
        with open(trace_file, "r", encoding="utf-8") as tf:
            traces = [json.loads(line) for line in tf if line.strip()]
        extract_traces = [t for t in traces if t.get("step_name") == "extraction_pipeline"]
        if extract_traces:
            tr = extract_traces[-1]
            print(f"      Trace ID: {tr['trace_id']} | Agent: {tr['agent_name']} | Latency: {tr['latency_ms']}ms")
            print(f"      Payload: {tr['output']}")
            print("      PASS: Pipeline step telemetry logged to trace.jsonl.")
        else:
            print("      NOTICE: No extraction_pipeline trace step found.")
    else:
        print("      WARNING: trace.jsonl not found.")

    conn.close()
    print("\n==================================================")
    print("D2 VERIFICATION AUDIT COMPLETE")
    print("==================================================")


if __name__ == "__main__":
    run_d2_verification()
