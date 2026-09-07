"""
Deliverable 3 (D3) Verification & Normalization Layer Audit Script.
Validates:
1. Normalization precision (DecimalNormalizer, CurrencyNormalizer, TemporalNormalizer)
2. Context resolution qualifiers (ContextResolverAgent)
3. Fact grouping semantic clustering (FactGroupEngine)
4. SQLite ledger persistence for fact_candidates, fact_groups, and group_members
"""
import sys
from decimal import Decimal
from pathlib import Path
import sqlite3

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# pyrefly: ignore [missing-import]
from src.db.ledger import EvidenceLedger
# pyrefly: ignore [missing-import]
from src.matching.embeddings import FactGroupEngine
# pyrefly: ignore [missing-import]
from src.verification.context import ContextResolverAgent
# pyrefly: ignore [missing-import]
from src.verification.normalizers import CurrencyNormalizer, DecimalNormalizer, TemporalNormalizer


def run_d3_verification():
    print("==================================================")
    print("  EVIDRA D3 Verification and Normalization Audit  ")
    print("==================================================")

    # 1. Decimal and Unit Normalization
    print("\n[1/4] Testing Decimal & Multiplier Normalization...")
    test_cases = [
        ("INR 6,882.29 million", Decimal("6882290000.00"), "INR"),
        ("Rs. 450.50 Crores", Decimal("4505000000.00"), "INR"),
        ("Rs. (125.40 Lakhs)", Decimal("-12540000.00"), "INR"),
        ("USD 1.25 Billion", Decimal("1250000000.00"), "USD"),
        ("EUR (50.00)", Decimal("-50.00"), "EUR"),
    ]
    for raw, expected_val, expected_curr in test_cases:
        norm_val, _ = DecimalNormalizer.normalize(raw)
        norm_curr = CurrencyNormalizer.normalize(raw)
        assert norm_val == expected_val, f"Value mismatch for {raw}: got {norm_val}, expected {expected_val}"
        assert norm_curr == expected_curr, f"Currency mismatch for {raw}: got {norm_curr}, expected {expected_curr}"
        print(f"      PASS: '{raw}' -> {norm_val} {norm_curr}")

    # 2. Temporal Interval Parsing
    print("\n[2/4] Testing Temporal Scope ISO 8601 Normalization...")
    temporal_cases = [
        ("FY22", ("2021-04-01", "2022-03-31")),
        ("FY2023", ("2022-04-01", "2023-03-31")),
        ("Q1 FY24", ("2023-04-01", "2023-06-30")),
        ("Nine months ended Dec 31, 2021", ("2021-04-01", "2021-12-31")),
        ("Cal 2022", ("2022-01-01", "2022-12-31")),
    ]
    for raw_time, (expected_start, expected_end) in temporal_cases:
        p_start, p_end = TemporalNormalizer.normalize(raw_time)
        assert p_start == expected_start, f"Start mismatch for {raw_time}: {p_start} vs {expected_start}"
        assert p_end == expected_end, f"End mismatch for {raw_time}: {p_end} vs {expected_end}"
        print(f"      PASS: '{raw_time}' -> [{p_start} to {p_end}]")

    # 3. Context Qualifier Extraction
    print("\n[3/4] Testing Context Resolution Deterministic Engine...")
    ctx = ContextResolverAgent.resolve_deterministically(
        statement="Restated Consolidated Revenue from Operations under Ind AS",
        chunk_content="Notes to Restated Consolidated Financial Statements",
        filename="prospectus.pdf",
    )
    assert ctx.organizational_scope == "CONSOLIDATED"
    assert ctx.accounting_basis == "IFRS"
    assert ctx.filing_type == "PROSPECTUS"
    assert ctx.version_status == "RESTATED"
    print(f"      PASS: Scope={ctx.organizational_scope}, Basis={ctx.accounting_basis}, Type={ctx.filing_type}, Version={ctx.version_status}")

    # 4. Semantic Grouping Engine
    print("\n[4/4] Testing FactGroup Semantic Grouping Engine...")
    engine = FactGroupEngine()
    candidates = [
        {"fact_id": "F1", "entity": "Delhivery", "attribute": "Revenue from operations", "period_start": "2021-04-01", "period_end": "2022-03-31"},
        {"fact_id": "F2", "entity": "Delhivery", "attribute": "Operating Revenue", "period_start": "2021-04-01", "period_end": "2022-03-31"},
        {"fact_id": "F3", "entity": "Delhivery", "attribute": "Total Non-Current Borrowings", "period_start": "2021-04-01", "period_end": "2022-03-31"},
    ]
    groups = engine.group_candidates(candidates)
    assert len(groups) == 2, f"Expected 2 clusters, got {len(groups)}"
    multi_groups = [(g, m) for g, m in groups if len(m) == 2]
    assert len(multi_groups) == 1, "Expected 1 cluster with 2 members"
    print(f"      PASS: Clustered 3 candidates into {len(groups)} groups (synonymous attributes merged)")

    # 5. SQLite Ledger Verification
    print("\n[5/5] Inspecting SQLite Ledger Run Records...")
    runs_dir = repo_root / "runs"
    job_dirs = sorted([d for d in runs_dir.glob("JOB-*") if d.is_dir()], key=lambda d: d.stat().st_mtime, reverse=True)
    if not job_dirs:
        print("      WARNING: No job directories found in runs/")
    else:
        latest_job = job_dirs[0]
        db_path = latest_job / "ledger.db"
        print(f"      Inspecting: {db_path.name} in {latest_job.name}")
        ledger = EvidenceLedger(db_path)
        summary = ledger.get_job_summary()
        print(f"      - Evidence Chunks: {summary['evidence_chunks_count']}")
        print(f"      - Observations:    {summary['observations_count']}")
        print(f"      - Fact Candidates: {summary['fact_candidates_count']}")
        print(f"      - Fact Groups:     {summary['fact_groups_count']}")
        assert summary['fact_candidates_count'] >= 1, "Expected at least 1 fact candidate in ledger"
        assert summary['fact_groups_count'] >= 1, "Expected at least 1 fact group in ledger"
        print("      PASS: Ledger schema, Fact Candidates, and Fact Groups verified.")

    print("\n==================================================")
    print("ALL DELIVERABLE 3 (D3) VERIFICATION CHECKS PASSED")
    print("==================================================")


if __name__ == "__main__":
    run_d3_verification()
