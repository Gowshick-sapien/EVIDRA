from __future__ import annotations

import tempfile
from decimal import Decimal
from pathlib import Path
import pytest

# pyrefly: ignore [missing-import]
from src.db.ledger import EvidenceLedger, FactCandidateRecord, ObservationRecord
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


def test_arithmetic_validator_tolerance():
    """Verify arithmetic tolerance logic using exact Python Decimal."""
    c1 = CandidateFactView(fact_id="f1", observation_id="o1", normalized_value="10000.00")
    c2 = CandidateFactView(fact_id="f2", observation_id="o2", normalized_value="10000.50")
    c3 = CandidateFactView(fact_id="f3", observation_id="o3", normalized_value="10500.00")

    # 10000.50 is within 0.01% (delta=0.5 / 10000.50 = 0.00005 <= 0.0001)
    res_within = ArithmeticValidator.evaluate(c1, c2)
    assert res_within.outcome == ValidationStatus.SUPPORTED
    assert res_within.details["within_tolerance"] is True

    # 10500.00 exceeds 0.01% (delta=500 / 10500 = 0.0476 > 0.0001)
    res_exceed = ArithmeticValidator.evaluate(c1, c3)
    assert res_exceed.outcome == ValidationStatus.REFUTED
    assert res_exceed.details["within_tolerance"] is False


def test_restatement_validator():
    """Verify detection of audit restatements between reporting periods."""
    c_orig = CandidateFactView(
        fact_id="f1",
        observation_id="o1",
        normalized_value="5000",
        version_status="AS_REPORTED",
        chunk_content="Audited standalone balance sheet 2021",
    )
    c_rest = CandidateFactView(
        fact_id="f2",
        observation_id="o2",
        normalized_value="5200",
        version_status="RESTATED",
        chunk_content="Restated financial statements for the year ended March 31, 2021",
    )

    res = RestatementValidator.evaluate(c_orig, c_rest)
    assert res.outcome == ValidationStatus.SUPPORTED
    assert res.details["candidate_2_restated"] is True


def test_accounting_basis_validator():
    """Verify detection of GAAP vs Non-GAAP reporting differences."""
    c_gaap = CandidateFactView(
        fact_id="f1",
        observation_id="o1",
        normalized_value="1000",
        accounting_basis="IFRS",
        statement="Net profit under Ind AS",
    )
    c_nongaap = CandidateFactView(
        fact_id="f2",
        observation_id="o2",
        normalized_value="1250",
        accounting_basis="NON_GAAP",
        statement="Adjusted EBITDA excluding share-based payments",
        chunk_content="Reconciliation of Non-GAAP Adjusted EBITDA",
    )

    res = AccountingBasisValidator.evaluate(c_gaap, c_nongaap)
    assert res.outcome == ValidationStatus.SUPPORTED
    assert res.details["non_gaap_detected"] is True


def test_scope_validator():
    """Verify detection of Standalone vs Consolidated corporate scope variations."""
    c_standalone = CandidateFactView(
        fact_id="f1",
        observation_id="o1",
        normalized_value="4000",
        organizational_scope="STANDALONE",
        chunk_content="Standalone Revenue from operations",
    )
    c_consolidated = CandidateFactView(
        fact_id="f2",
        observation_id="o2",
        normalized_value="7000",
        organizational_scope="CONSOLIDATED",
        chunk_content="Consolidated Revenue from operations for the group",
    )

    res = ScopeValidator.evaluate(c_standalone, c_consolidated)
    assert res.outcome == ValidationStatus.SUPPORTED
    assert res.details["mismatch_confirmed"] is True


def test_timing_validator():
    """Verify detection of divergent temporal intervals."""
    c_q1 = CandidateFactView(
        fact_id="f1",
        observation_id="o1",
        normalized_value="1500",
        period_start="2021-04-01",
        period_end="2021-06-30",
    )
    c_fy = CandidateFactView(
        fact_id="f2",
        observation_id="o2",
        normalized_value="6800",
        period_start="2021-04-01",
        period_end="2022-03-31",
    )

    res = TimingValidator.evaluate(c_q1, c_fy)
    assert res.outcome == ValidationStatus.SUPPORTED
    assert res.details["intervals_differ"] is True


def test_hypothesis_generator_deterministic():
    """Verify deterministic hypothesis generation covers all variance classes."""
    c1 = CandidateFactView(
        fact_id="f1",
        observation_id="o1",
        normalized_value="100",
        version_status="AS_REPORTED",
        accounting_basis="IFRS",
        organizational_scope="STANDALONE",
        period_start="2021-04-01",
        period_end="2021-06-30",
    )
    c2 = CandidateFactView(
        fact_id="f2",
        observation_id="o2",
        normalized_value="150",
        version_status="RESTATED",
        accounting_basis="NON_GAAP",
        organizational_scope="CONSOLIDATED",
        period_start="2021-04-01",
        period_end="2022-03-31",
    )

    hyps = HypothesisGeneratorAgent.generate_deterministically(c1, c2)
    hyp_types = {h.explanation_type for h in hyps}

    assert HypothesisClass.RESTATEMENT in hyp_types
    assert HypothesisClass.ACCOUNTING_BASIS in hyp_types
    assert HypothesisClass.SCOPE_MISMATCH in hyp_types
    assert HypothesisClass.TIMING_DIFFERENCE in hyp_types
    assert HypothesisClass.ERRONEOUS_CONTRADICTION in hyp_types


def test_adversarial_skeptic_falsification():
    """Verify skeptic rejects ungrounded reconciliation proposals."""
    c1 = CandidateFactView(fact_id="f1", observation_id="o1", normalized_value="100", chunk_content="Raw text A")
    c2 = CandidateFactView(fact_id="f2", observation_id="o2", normalized_value="200", chunk_content="Raw text B")

    # Propose restatement without any restatement keywords in chunks
    proposal = ReconciliationProposal(
        supported_hypothesis_id="H-TEST",
        explanation_type=HypothesisClass.RESTATEMENT,
        root_cause="Audit Restatement",
        reconciliation_bridge="Assumed revision without citation",
        arithmetic_delta="100",
    )

    critique = AdversarialSkepticAgent.critique_deterministically(c1, c2, proposal)
    assert critique.status == SkepticStatus.UNGROUNDED
    assert critique.citations_verified is False


def test_deterministic_decision_policy_truth_tables():
    """Verify all four categorical outcomes in DecisionPolicy truth table."""
    c1 = CandidateFactView(fact_id="f1", observation_id="o1", normalized_value="100.00")
    c2 = CandidateFactView(fact_id="f2", observation_id="o2", normalized_value="100.00")

    # 1. Single candidate -> UNRESOLVED
    v_single, s_single, _ = DecisionPolicy.evaluate([c1], [], None, None)
    assert v_single == Verdict.UNRESOLVED
    assert s_single == DecisionStrength.LOW

    # 2. Corroborated -> CORROBORATED (HIGH)
    v_corr, s_corr, _ = DecisionPolicy.evaluate([c1, c2], [], None, None, arithmetic_equal=True, matching_context=True)
    assert v_corr == Verdict.CORROBORATED
    assert s_corr == DecisionStrength.HIGH

    # 3. Supported & Survived -> RECONCILED (HIGH)
    val = ValidatorOutcome(result_id="v1", hypothesis_id="h1", validator_type="RestatementValidator", outcome=ValidationStatus.SUPPORTED)
    prop = ReconciliationProposal(supported_hypothesis_id="h1", explanation_type=HypothesisClass.RESTATEMENT, root_cause="Restatement", reconciliation_bridge="Bridge", arithmetic_delta="10.0")
    skep = SkepticOutcome(status=SkepticStatus.SURVIVED, critique="Confirmed", citations_verified=True)
    v_rec, s_rec, _ = DecisionPolicy.evaluate([c1, c2], [val], prop, skep, arithmetic_equal=False, matching_context=False)
    assert v_rec == Verdict.RECONCILED
    assert s_rec == DecisionStrength.HIGH

    # 4. Falsified / Refuted -> CONTRADICTION (HIGH)
    skep_f = SkepticOutcome(status=SkepticStatus.FALSIFIED, critique="Contradicted", citations_verified=False)
    v_contra, s_contra, _ = DecisionPolicy.evaluate([c1, c2], [], None, skep_f, arithmetic_equal=False, matching_context=True)
    assert v_contra == Verdict.CONTRADICTION
    assert s_contra == DecisionStrength.HIGH

    # 5. Ungrounded -> UNRESOLVED (LOW)
    skep_u = SkepticOutcome(status=SkepticStatus.UNGROUNDED, critique="Speculative", citations_verified=False)
    v_unres, s_unres, _ = DecisionPolicy.evaluate([c1, c2], [], None, skep_u, arithmetic_equal=False, matching_context=False)
    assert v_unres == Verdict.UNRESOLVED


def test_langgraph_workflow_paths():
    """Verify compilation and execution of Path A, Path B, and Path C in LangGraph."""
    builder = DecisionWorkflowBuilder()
    graph = builder.build_graph()

    # Path A: Exact Match
    cA1 = CandidateFactView(fact_id="f1", observation_id="o1", normalized_value="100.00").model_dump()
    cA2 = CandidateFactView(fact_id="f2", observation_id="o2", normalized_value="100.00").model_dump()
    resA = graph.invoke({"group_id": "gA", "entity": "E", "attribute": "A", "period_id": "P", "candidates": [cA1, cA2], "traces": []})
    assert resA["verdict"] == Verdict.CORROBORATED
    assert resA["decision_strength"] == DecisionStrength.HIGH

    # Path B: Restated Scope
    cB1 = CandidateFactView(fact_id="f1", observation_id="o1", normalized_value="100.00", version_status="AS_REPORTED", chunk_content="Report 2021").model_dump()
    cB2 = CandidateFactView(fact_id="f2", observation_id="o2", normalized_value="120.00", version_status="RESTATED", chunk_content="Restated 2022").model_dump()
    resB = graph.invoke({"group_id": "gB", "entity": "E", "attribute": "A", "period_id": "P", "candidates": [cB1, cB2], "traces": []})
    assert resB["verdict"] == Verdict.RECONCILED

    # Path C: Conflict
    cC1 = CandidateFactView(fact_id="f1", observation_id="o1", normalized_value="100.00", chunk_content="Report A").model_dump()
    cC2 = CandidateFactView(fact_id="f2", observation_id="o2", normalized_value="900.00", chunk_content="Report B").model_dump()
    resC = graph.invoke({"group_id": "gC", "entity": "E", "attribute": "A", "period_id": "P", "candidates": [cC1, cC2], "traces": []})
    assert resC["verdict"] == Verdict.CONTRADICTION


def test_fact_decision_engine_persistence():
    """Verify FactDecisionEngine batch processes groups and populates decisions and decision_traces in SQLite."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "ledger.db"
        ledger = EvidenceLedger(db_path)

        with ledger.transaction() as conn:
            conn.execute("INSERT INTO documents VALUES ('DOC-1', 'test.pdf', 'h1', 1, '2026-09-08');")
            conn.execute("INSERT INTO evidence_chunks VALUES ('CHK-1', 'DOC-1', 1, 'text', '[0,0,10,10]', 'Revenue 500M', 'ch1', '2026-09-08');")
            conn.execute("INSERT INTO observations VALUES ('OBS-1', 'CHK-1', 'DOC-1', 'Rev 500M', 'Corp', 'Revenue', '500M', 'numerical', 'FY22', 'ENTAILED', 1.0, '2026-09-08');")
            conn.execute("INSERT INTO observations VALUES ('OBS-2', 'CHK-1', 'DOC-1', 'Rev 500M', 'Corp', 'Revenue', '500M', 'numerical', 'FY22', 'ENTAILED', 1.0, '2026-09-08');")
            conn.execute("INSERT INTO fact_candidates VALUES ('F1', 'OBS-1', '500000000', 'SCALED_MILLION', 'USD', '2021-04-01', '2022-03-31', '2026-09-08');")
            conn.execute("INSERT INTO fact_candidates VALUES ('F2', 'OBS-2', '500000000', 'SCALED_MILLION', 'USD', '2021-04-01', '2022-03-31', '2026-09-08');")

        ledger.create_fact_group("Corp", "Revenue", "FY22", ["F1", "F2"])

        engine = FactDecisionEngine(ledger=ledger)
        summary = engine.process_fact_groups()

        assert summary["decisions_evaluated"] == 1
        assert summary["verdicts"]["CORROBORATED"] == 1

        # Verify records in ledger
        decs = ledger.get_decisions()
        assert len(decs) == 1
        assert decs[0]["verdict"] == "CORROBORATED"
        assert decs[0]["decision_strength"] == "HIGH"

        # Check Decision Card
        card = ledger.get_decision_card(decs[0]["decision_id"])
        assert card is not None
        assert len(card["claims"]) == 2
        assert len(card["traces"]) >= 1


def test_multi_pdf_cross_document_corroboration():
    """Verify that candidate facts originating from two distinct physical PDF documents corroborate across documents."""
    import pymupdf as fitz
    from src.db.ledger import DocumentRecord, EvidenceChunkRecord
    from src.matching.embeddings import FactGroupEngine

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        db_path = tmp_path / "ledger.db"
        ledger = EvidenceLedger(db_path)

        # 1. Create Document A (Earnings Release)
        pdf_a = tmp_path / "acme_earnings_q3.pdf"
        doc_a = fitz.open()
        p_a = doc_a.new_page()
        p_a.insert_text((50, 100), "Acme Corporation reported Total Revenues of USD 8,500 million for Q3 2024.", fontsize=12)
        doc_a.save(str(pdf_a))
        doc_a.close()

        # 2. Create Document B (Form 10-Q Filing)
        pdf_b = tmp_path / "acme_form_10q.pdf"
        doc_b = fitz.open()
        p_b = doc_b.new_page()
        p_b.insert_text((50, 100), "Acme Corporation recorded Total Revenues of USD 8,500 million for the quarter ended September 30, 2024.", fontsize=12)
        doc_b.save(str(pdf_b))
        doc_b.close()

        # Ingest both documents into SQLite
        ledger.insert_document(DocumentRecord("DOC-A", pdf_a.name, "hash_a", 1))
        ledger.insert_document(DocumentRecord("DOC-B", pdf_b.name, "hash_b", 1))

        # Ingest evidence chunks with physical bounding boxes
        c_a = EvidenceChunkRecord("CHK-A", "DOC-A", 1, "text", [50, 100, 400, 120], "Acme Total Revenues USD 8,500 million Q3 2024", "chash_a")
        c_b = EvidenceChunkRecord("CHK-B", "DOC-B", 1, "text", [50, 100, 450, 120], "Acme Total Revenues USD 8,500 million quarter ended Sep 30, 2024", "chash_b")
        ledger.insert_evidence_chunks([c_a, c_b])

        # Record observations from each document
        obs_a = ObservationRecord(
            observation_id="OBS-A",
            chunk_id="CHK-A",
            document_id="DOC-A",
            statement="Total Revenues of USD 8,500 million for Q3 2024",
            entity="Acme Corporation",
            attribute="Total Revenues",
            raw_value="USD 8,500 million",
            observation_type="numerical",
            temporal_scope="Q3 2024",
            confidence=0.98,
            provenance_status="ENTAILED",
        )
        obs_b = ObservationRecord(
            observation_id="OBS-B",
            chunk_id="CHK-B",
            document_id="DOC-B",
            statement="Total Revenues of USD 8,500 million for the quarter ended September 30, 2024",
            entity="Acme Corporation",
            attribute="Total Revenues",
            raw_value="USD 8,500 million",
            observation_type="numerical",
            temporal_scope="Q3 2024",
            confidence=0.99,
            provenance_status="ENTAILED",
        )
        ledger.insert_observations([obs_a, obs_b])

        # Record normalized fact candidates
        f_a = FactCandidateRecord("FCT-A", "OBS-A", "8500000000", "SCALED_MILLION", "USD", "2024-07-01", "2024-09-30")
        f_b = FactCandidateRecord("FCT-B", "OBS-B", "8500000000", "SCALED_MILLION", "USD", "2024-07-01", "2024-09-30")
        ledger.insert_fact_candidates([f_a, f_b])

        # Two-tier grouping across documents
        group_engine = FactGroupEngine()
        candidates = [
            {"fact_id": "FCT-A", "entity": "Acme Corporation", "attribute": "Total Revenues", "period_start": "2024-07-01", "period_end": "2024-09-30"},
            {"fact_id": "FCT-B", "entity": "Acme Corporation", "attribute": "Total Revenues", "period_start": "2024-07-01", "period_end": "2024-09-30"},
        ]
        clusters = group_engine.group_candidates(candidates)
        assert len(clusters) == 1
        grp_record, member_fact_ids = clusters[0]
        assert set(member_fact_ids) == {"FCT-A", "FCT-B"}

        # Persist FactGroup with members across Document A and Document B
        ledger.create_fact_group(
            entity=grp_record.entity,
            attribute=grp_record.attribute,
            period_id=grp_record.period_id,
            fact_ids=member_fact_ids,
            group_id=grp_record.group_id,
        )

        # Adjudicate via FactDecisionEngine
        decision_engine = FactDecisionEngine(ledger=ledger)
        summary = decision_engine.process_fact_groups()

        assert summary["decisions_evaluated"] == 1
        assert summary["verdicts"]["CORROBORATED"] == 1

        # Inspect Decision Card
        decs = ledger.get_decisions()
        card = ledger.get_decision_card(decs[0]["decision_id"])
        assert card["verdict"] == "CORROBORATED"
        assert card["decision_strength"] == "HIGH"

        # Verify dual-document provenance
        doc_names = {claim["filename"] for claim in card["claims"]}
        assert doc_names == {"acme_earnings_q3.pdf", "acme_form_10q.pdf"}
