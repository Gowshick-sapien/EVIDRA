"""
Deliverable 4 (D4) Decision Engine & LangGraph State Machine Audit Script.
Validates:
1. Specialist Validators (Arithmetic, Restatement, AccountingBasis, Scope, Timing)
2. Hypothesis Tournament formulation
3. Reconciliation Proposer & Adversarial Skeptic critique
4. Pure Python Deterministic Decision Policy truth tables
5. LangGraph StateGraph adaptive routing (Path A, Path B, Path C)
6. SQLite ledger persistence for decisions, hypotheses, and decision_traces
"""
import sys
import tempfile
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
from src.decision.engine import FactDecisionEngine
# pyrefly: ignore [missing-import]
from src.decision.hypothesis import HypothesisGeneratorAgent
# pyrefly: ignore [missing-import]
from src.decision.policy import DecisionPolicy
# pyrefly: ignore [missing-import]
from src.decision.reconciliation import (
    AdversarialSkepticAgent,
    ReconciliationProposerAgent,
)
# pyrefly: ignore [missing-import]
from src.decision.schemas import (
    CandidateFactView,
    DecisionStrength,
    HypothesisClass,
    ReconciliationProposal,
    SkepticOutcome,
    SkepticStatus,
    ValidationStatus,
    ValidatorOutcome,
    Verdict,
)
# pyrefly: ignore [missing-import]
from src.decision.validators import (
    AccountingBasisValidator,
    ArithmeticValidator,
    RestatementValidator,
    ScopeValidator,
    TimingValidator,
)
# pyrefly: ignore [missing-import]
from src.decision.workflow import DecisionWorkflowBuilder


def run_d4_verification():
    print("==================================================")
    print("  EVIDRA D4 Decision Engine & State Machine Audit ")
    print("==================================================")

    # 1. Specialist Validators
    print("\n[1/6] Testing Specialist Validators...")
    c1 = CandidateFactView(fact_id="f1", observation_id="o1", normalized_value="1000.00", version_status="AS_REPORTED", accounting_basis="IFRS", organizational_scope="STANDALONE", period_start="2021-04-01", period_end="2021-06-30")
    c2 = CandidateFactView(fact_id="f2", observation_id="o2", normalized_value="1000.05", version_status="RESTATED", accounting_basis="NON_GAAP", organizational_scope="CONSOLIDATED", period_start="2021-04-01", period_end="2022-03-31")

    # Arithmetic tolerance (0.01%)
    res_arith = ArithmeticValidator.evaluate(c1, c2)
    assert res_arith.outcome == ValidationStatus.SUPPORTED
    print("      PASS: ArithmeticValidator (0.005% delta <= 0.01% tolerance)")

    # Restatement
    res_rest = RestatementValidator.evaluate(c1, c2)
    assert res_rest.outcome == ValidationStatus.SUPPORTED
    print("      PASS: RestatementValidator (Restated vs As-Reported detected)")

    # Accounting Basis
    res_basis = AccountingBasisValidator.evaluate(c1, c2)
    assert res_basis.outcome == ValidationStatus.SUPPORTED
    print("      PASS: AccountingBasisValidator (IFRS vs Non-GAAP detected)")

    # Scope
    res_scope = ScopeValidator.evaluate(c1, c2)
    assert res_scope.outcome == ValidationStatus.SUPPORTED
    print("      PASS: ScopeValidator (Standalone vs Consolidated detected)")

    # Timing
    res_time = TimingValidator.evaluate(c1, c2)
    assert res_time.outcome == ValidationStatus.SUPPORTED
    print("      PASS: TimingValidator (Quarter vs Full Year detected)")

    # 2. Hypothesis Tournament Formulation
    print("\n[2/6] Testing Hypothesis Tournament Generation...")
    hyps = HypothesisGeneratorAgent.generate_deterministically(c1, c2)
    hyp_classes = {h.explanation_type for h in hyps}
    assert HypothesisClass.RESTATEMENT in hyp_classes
    assert HypothesisClass.ACCOUNTING_BASIS in hyp_classes
    assert HypothesisClass.SCOPE_MISMATCH in hyp_classes
    assert HypothesisClass.TIMING_DIFFERENCE in hyp_classes
    assert HypothesisClass.ERRONEOUS_CONTRADICTION in hyp_classes
    print(f"      PASS: Generated {len(hyps)} hypotheses across all 5 variance classes.")

    # 3. Reconciliation Proposer & Adversarial Skeptic
    print("\n[3/6] Testing Reconciliation Proposer & Adversarial Skeptic...")
    proposal = ReconciliationProposerAgent.propose_deterministically(c1, c2, [res_rest])
    assert proposal is not None
    assert proposal.explanation_type == HypothesisClass.RESTATEMENT
    print(f"      PASS: Proposer synthesized bridge: '{proposal.root_cause}'")

    critique_survived = AdversarialSkepticAgent.critique_deterministically(c1, c2, proposal)
    assert critique_survived.status == SkepticStatus.SURVIVED
    print(f"      PASS: Skeptic critique: {critique_survived.status} ({critique_survived.critique})")

    # 4. Pure Python Decision Policy Truth Tables
    print("\n[4/6] Testing Deterministic Decision Policy Truth Tables...")
    cA = CandidateFactView(fact_id="fa1", observation_id="oa1", normalized_value="500.00")
    cB = CandidateFactView(fact_id="fa2", observation_id="oa2", normalized_value="500.00")
    cC = CandidateFactView(fact_id="fa3", observation_id="oa3", normalized_value="900.00")

    # Rule 1: Corroborated
    v_corr, s_corr, _ = DecisionPolicy.evaluate([cA, cB], [], None, None, arithmetic_equal=True, matching_context=True)
    assert v_corr == Verdict.CORROBORATED and s_corr == DecisionStrength.HIGH
    print("      PASS: Rule 1: Corroborated (Path A)")

    # Rule 2: Reconciled
    v_rec, s_rec, _ = DecisionPolicy.evaluate([c1, c2], [res_rest], proposal, critique_survived, arithmetic_equal=False, matching_context=False)
    assert v_rec == Verdict.RECONCILED and s_rec == DecisionStrength.HIGH
    print("      PASS: Rule 2: Reconciled (Path B)")

    # Rule 3: Contradiction
    skep_fail = SkepticOutcome(status=SkepticStatus.FALSIFIED, critique="Falsified", citations_verified=False)
    v_contra, s_contra, _ = DecisionPolicy.evaluate([cA, cC], [], None, skep_fail, arithmetic_equal=False, matching_context=True)
    assert v_contra == Verdict.CONTRADICTION and s_contra == DecisionStrength.HIGH
    print("      PASS: Rule 3: Contradiction (Path C)")

    # Rule 4: Fallback Unresolved
    v_unres, s_unres, _ = DecisionPolicy.evaluate([cA], [], None, None)
    assert v_unres == Verdict.UNRESOLVED and s_unres == DecisionStrength.LOW
    print("      PASS: Rule 4: Fallback Unresolved (Single candidate fail-safe)")

    # 5. LangGraph StateGraph Multi-Path Execution
    print("\n[5/6] Testing LangGraph Workflow Routing & Tracing...")
    builder = DecisionWorkflowBuilder()
    graph = builder.build_graph()

    # Path A execution
    resA = graph.invoke({"group_id": "gA", "entity": "E", "attribute": "A", "period_id": "P", "candidates": [cA.model_dump(), cB.model_dump()], "traces": []})
    assert resA["verdict"] == Verdict.CORROBORATED
    print(f"      PASS: Path A executed via LangGraph -> {resA['verdict']} ({len(resA['traces'])} steps)")

    # Path B execution
    resB = graph.invoke({"group_id": "gB", "entity": "E", "attribute": "A", "period_id": "P", "candidates": [c1.model_dump(), c2.model_dump()], "traces": []})
    assert resB["verdict"] == Verdict.RECONCILED
    print(f"      PASS: Path B executed via LangGraph -> {resB['verdict']} ({len(resB['traces'])} steps)")

    # Path C execution
    resC = graph.invoke({"group_id": "gC", "entity": "E", "attribute": "A", "period_id": "P", "candidates": [cA.model_dump(), cC.model_dump()], "traces": []})
    assert resC["verdict"] == Verdict.CONTRADICTION
    print(f"      PASS: Path C executed via LangGraph -> {resC['verdict']} ({len(resC['traces'])} steps)")

    # 6. SQLite Ledger Persistence & Decision Cards
    print("\n[6/6] Testing FactDecisionEngine SQLite Ledger Integration...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "ledger.db"
        ledger = EvidenceLedger(db_path)

        with ledger.transaction() as conn:
            conn.execute("INSERT INTO documents VALUES ('DOC-01', 'prospectus.pdf', 'hash1', 1, '2026-09-08');")
            conn.execute("INSERT INTO evidence_chunks VALUES ('CHK-01', 'DOC-01', 1, 'text', '[10,20,30,40]', 'Revenue 500M', 'chash1', '2026-09-08');")
            conn.execute("INSERT INTO observations VALUES ('OBS-01', 'CHK-01', 'DOC-01', 'Revenue was 500M', 'Delhivery', 'Revenue', '500M', 'numerical', 'FY22', 'ENTAILED', 1.0, '2026-09-08');")
            conn.execute("INSERT INTO observations VALUES ('OBS-02', 'CHK-01', 'DOC-01', 'Operating Revenue was 500M', 'Delhivery', 'Revenue', '500M', 'numerical', 'FY22', 'ENTAILED', 1.0, '2026-09-08');")
            conn.execute("INSERT INTO fact_candidates VALUES ('F-01', 'OBS-01', '500000000', 'SCALED_MILLION', 'USD', '2021-04-01', '2022-03-31', '2026-09-08');")
            conn.execute("INSERT INTO fact_candidates VALUES ('F-02', 'OBS-02', '500000000', 'SCALED_MILLION', 'USD', '2021-04-01', '2022-03-31', '2026-09-08');")

        ledger.create_fact_group("Delhivery", "Revenue", "FY22", ["F-01", "F-02"])

        engine = FactDecisionEngine(ledger=ledger)
        engine_res = engine.process_fact_groups()
        assert engine_res["decisions_evaluated"] == 1
        assert engine_res["verdicts"]["CORROBORATED"] == 1

        decs = ledger.get_decisions()
        assert len(decs) == 1
        card = ledger.get_decision_card(decs[0]["decision_id"])
        assert card is not None
        assert len(card["claims"]) == 2
        assert len(card["traces"]) >= 1
        print(f"      PASS: Ledger recorded decision {decs[0]['decision_id']} with full Decision Card provenance.")

    print("\n==================================================")
    print("ALL DELIVERABLE 4 (D4) VERIFICATION CHECKS PASSED")
    print("==================================================")


if __name__ == "__main__":
    run_d4_verification()
