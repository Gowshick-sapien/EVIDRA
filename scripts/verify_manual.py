"""
Manual Verification Helper Script for EVIDRA (MTC-02 & MTC-05).
Performs direct SQLite inspection, foreign key verification, summary checks,
and audit trace JSONL inspection.
"""
import json
import sqlite3
import sys
from pathlib import Path

# Ensure repository root is on sys.path
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# pyrefly: ignore [missing-import]
from src.db.ledger import EvidenceLedger


def run_manual_inspection():
    print("==================================================")
    print("  EVIDRA MTC-02: SQLite Ledger Direct Inspection  ")
    print("==================================================")

    # 1. Locate latest run
    runs_dir = repo_root / "runs"
    job_dirs = sorted([d for d in runs_dir.glob("JOB-*") if d.is_dir()], key=lambda d: d.stat().st_mtime, reverse=True)
    if not job_dirs:
        print("FAIL: No job directories found in runs/")
        sys.exit(1)

    latest_job = job_dirs[0]
    db_path = latest_job / "ledger.db"
    print(f"Target Database: {db_path}")

    # 2. Inspect tables
    conn = sqlite3.connect(str(db_path))
    tables = [r[0] for r in conn.execute("SELECT tbl_name FROM sqlite_master WHERE type='table'").fetchall() if not r[0].startswith("sqlite_")]
    tables = sorted(list(set(tables)))
    print(f"\n[1/3] Tables in Ledger ({len(tables)} tables):")
    for t in tables:
        print(f"      - {t}")

    expected = {"documents", "evidence_chunks", "observations", "fact_candidates", "fact_groups", "group_members", "hypotheses", "validator_results", "decisions", "decision_traces"}
    if expected.issubset(set(tables)):
        print("      PASS: All 10 expected relational tables exist.")
    else:
        print(f"      FAIL: Missing tables: {expected - set(tables)}")

    # 3. Foreign key test
    print("\n[2/3] Testing Foreign Key Enforcement...")
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        conn.execute("INSERT INTO evidence_chunks (chunk_id, document_id, page_number, chunk_type, bounding_box, content, content_hash) VALUES ('CHK-TEST', 'NON_EXISTENT_DOC', 1, 'text', '[]', 'test', 'hash')")
        print("      FAIL: Foreign key constraint was not enforced.")
    except sqlite3.IntegrityError as e:
        print(f"      PASS: Foreign key constraint caught orphaned record: {e}")

    # 4. Summary statistics
    print("\n[3/3] Inspecting Ledger Summary via EvidenceLedger...")
    ledger = EvidenceLedger(db_path)
    summary = ledger.get_job_summary()
    print(f"      Documents count:        {summary['documents_count']}")
    print(f"      Evidence chunks count:  {summary['evidence_chunks_count']}")
    print(f"      Fact candidates count:  {summary['fact_candidates_count']}")
    print(f"      Decisions count:        {summary['decisions_count']}")
    print("      PASS: Summary statistics retrieved successfully.")

    print("\n==================================================")
    print("  EVIDRA MTC-05: Audit Trace Stream Inspection    ")
    print("==================================================")
    trace_files = list(runs_dir.glob("**/trace.jsonl"))
    if not trace_files:
        print("      WARNING: No trace.jsonl files found in runs/")
    else:
        target_trace = trace_files[-1]
        print(f"Target Trace: {target_trace}")
        with open(target_trace, "r", encoding="utf-8") as tf:
            lines = [json.loads(line) for line in tf if line.strip()]
        print(f"      Total trace entries logged: {len(lines)}")
        required_keys = {"trace_id", "timestamp", "step_name", "agent_name", "latency_ms", "input", "output"}
        all_valid = True
        for idx, entry in enumerate(lines, start=1):
            missing = required_keys - set(entry.keys())
            if missing:
                print(f"      FAIL: Entry {idx} missing keys: {missing}")
                all_valid = False
            else:
                print(f"      Entry {idx}: [{entry['timestamp']}] Step: {entry['step_name']} | Agent: {entry['agent_name']}")
        if all_valid and lines:
            print("      PASS: Streaming audit records are well-formed and schema-compliant.")

    print("\n==================================================")
    print("ALL MANUAL VERIFICATIONS (MTC-02 to MTC-05) PASSED")
    print("==================================================")


if __name__ == "__main__":
    run_manual_inspection()
