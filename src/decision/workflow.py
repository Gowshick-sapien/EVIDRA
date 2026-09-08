from __future__ import annotations

import logging
import time
import uuid
from decimal import Decimal
from typing import Any, Optional

from langgraph.graph import END, START, StateGraph

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
    FactDecisionState,
    HypothesisClass,
    HypothesisProposal,
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
from src.llm.provider import ReasoningService

logger = logging.getLogger(__name__)


class DecisionWorkflowBuilder:
    """Builder for the LangGraph Fact Decision state machine."""

    def __init__(self, reasoning_service: Optional[ReasoningService] = None):
        self.llm = reasoning_service
        self.hypothesis_agent = HypothesisGeneratorAgent(reasoning_service)
        self.proposer_agent = ReconciliationProposerAgent(reasoning_service)
        self.skeptic_agent = AdversarialSkepticAgent(reasoning_service)

    def _to_candidates(self, state: FactDecisionState) -> list[CandidateFactView]:
        raw_list = state.get("candidates", [])
        views: list[CandidateFactView] = []
        for c in raw_list:
            if isinstance(c, CandidateFactView):
                views.append(c)
            elif isinstance(c, dict):
                views.append(CandidateFactView(**c))
        return views

    # Node 1: Analyze Variance & Context
    def node_analyze_variance(self, state: FactDecisionState) -> dict[str, Any]:
        start = time.perf_counter()
        candidates = self._to_candidates(state)
        traces = list(state.get("traces", []))

        if len(candidates) <= 1:
            traces.append({
                "step_name": "analyze_variance",
                "agent_name": "VarianceAnalyzer",
                "execution_time_ms": (time.perf_counter() - start) * 1000.0,
                "input": {"candidates_count": len(candidates)},
                "output": {"path": "A", "note": "Single candidate"},
            })
            return {
                "decision_path": "A",
                "arithmetic_equal": False,
                "matching_context": True,
                "traces": traces,
            }

        c1, c2 = candidates[0], candidates[1]
        val_res = ArithmeticValidator.evaluate(c1, c2)
        arithmetic_equal = (val_res.outcome == ValidationStatus.SUPPORTED)

        # Context Check
        basis_match = (c1.accounting_basis or "").upper() == (c2.accounting_basis or "").upper()
        scope_match = (c1.organizational_scope or "").upper() == (c2.organizational_scope or "").upper()
        version_match = (c1.version_status or "").upper() == (c2.version_status or "").upper()
        time_match = (c1.period_start, c1.period_end) == (c2.period_start, c2.period_end)

        matching_context = bool(basis_match and scope_match and version_match and time_match)

        # Route Selection
        if arithmetic_equal and matching_context:
            path = "A"  # Deterministic Corroboration
        elif not matching_context:
            path = "B"  # Contextual Resolution
        else:
            path = "C"  # Conflict Debate

        traces.append({
            "step_name": "analyze_variance",
            "agent_name": "VarianceAnalyzer",
            "execution_time_ms": (time.perf_counter() - start) * 1000.0,
            "input": {"candidates_count": len(candidates)},
            "output": {
                "decision_path": path,
                "arithmetic_equal": arithmetic_equal,
                "matching_context": matching_context,
            },
        })

        return {
            "decision_path": path,
            "arithmetic_equal": arithmetic_equal,
            "matching_context": matching_context,
            "traces": traces,
        }

    # Node 2: Fast-Path Corroboration
    def node_evaluate_corroboration(self, state: FactDecisionState) -> dict[str, Any]:
        return {}

    # Node 3: Context Routing & Direct Specialist Validators (Path B)
    def node_route_context(self, state: FactDecisionState) -> dict[str, Any]:
        start = time.perf_counter()
        candidates = self._to_candidates(state)
        traces = list(state.get("traces", []))
        c1, c2 = candidates[0], candidates[1]

        # Generate context hypotheses and run validators directly
        hyps = self.hypothesis_agent.generate_deterministically(c1, c2)
        validator_results: list[dict[str, Any]] = []

        for h in hyps:
            h_id = h.hypothesis_id
            if h.explanation_type == HypothesisClass.RESTATEMENT:
                res = RestatementValidator.evaluate(c1, c2, hypothesis_id=h_id)
                validator_results.append(res.model_dump())
            elif h.explanation_type == HypothesisClass.ACCOUNTING_BASIS:
                res = AccountingBasisValidator.evaluate(c1, c2, hypothesis_id=h_id)
                validator_results.append(res.model_dump())
            elif h.explanation_type == HypothesisClass.SCOPE_MISMATCH:
                res = ScopeValidator.evaluate(c1, c2, hypothesis_id=h_id)
                validator_results.append(res.model_dump())
            elif h.explanation_type == HypothesisClass.TIMING_DIFFERENCE:
                res = TimingValidator.evaluate(c1, c2, hypothesis_id=h_id)
                validator_results.append(res.model_dump())

        traces.append({
            "step_name": "route_context",
            "agent_name": "ContextRouter",
            "execution_time_ms": (time.perf_counter() - start) * 1000.0,
            "input": {"context_differences": True},
            "output": {"hypotheses_count": len(hyps), "validator_results_count": len(validator_results)},
        })

        return {
            "hypotheses": [h.model_dump() for h in hyps],
            "validator_results": validator_results,
            "traces": traces,
        }

    # Node 4: Hypothesis Tournament (Path C)
    def node_generate_hypotheses(self, state: FactDecisionState) -> dict[str, Any]:
        start = time.perf_counter()
        candidates = self._to_candidates(state)
        traces = list(state.get("traces", []))
        c1, c2 = candidates[0], candidates[1]

        hyps = self.hypothesis_agent.generate_hypotheses(c1, c2)

        traces.append({
            "step_name": "generate_hypotheses",
            "agent_name": "HypothesisGeneratorAgent",
            "execution_time_ms": (time.perf_counter() - start) * 1000.0,
            "input": {"entity": state.get("entity"), "attribute": state.get("attribute")},
            "output": {"hypotheses": [h.model_dump() for h in hyps]},
        })

        return {
            "hypotheses": [h.model_dump() for h in hyps],
            "traces": traces,
        }

    # Node 5: Run Specialist Validators (Path C)
    def node_run_validators(self, state: FactDecisionState) -> dict[str, Any]:
        start = time.perf_counter()
        candidates = self._to_candidates(state)
        traces = list(state.get("traces", []))
        c1, c2 = candidates[0], candidates[1]

        raw_hyps = state.get("hypotheses", [])
        validator_results: list[dict[str, Any]] = []

        for h_dict in raw_hyps:
            h_id = h_dict["hypothesis_id"]
            h_type = h_dict["explanation_type"]

            if h_type == HypothesisClass.RESTATEMENT:
                res = RestatementValidator.evaluate(c1, c2, hypothesis_id=h_id)
                validator_results.append(res.model_dump())
            elif h_type == HypothesisClass.ACCOUNTING_BASIS:
                res = AccountingBasisValidator.evaluate(c1, c2, hypothesis_id=h_id)
                validator_results.append(res.model_dump())
            elif h_type == HypothesisClass.SCOPE_MISMATCH:
                res = ScopeValidator.evaluate(c1, c2, hypothesis_id=h_id)
                validator_results.append(res.model_dump())
            elif h_type == HypothesisClass.TIMING_DIFFERENCE:
                res = TimingValidator.evaluate(c1, c2, hypothesis_id=h_id)
                validator_results.append(res.model_dump())

        traces.append({
            "step_name": "run_validators",
            "agent_name": "SpecialistValidators",
            "execution_time_ms": (time.perf_counter() - start) * 1000.0,
            "input": {"hypotheses_evaluated": len(raw_hyps)},
            "output": {"validator_results_count": len(validator_results)},
        })

        return {
            "validator_results": validator_results,
            "traces": traces,
        }

    # Node 6: Propose Reconciliation (Paths B & C)
    def node_propose_reconciliation(self, state: FactDecisionState) -> dict[str, Any]:
        start = time.perf_counter()
        candidates = self._to_candidates(state)
        traces = list(state.get("traces", []))
        c1, c2 = candidates[0], candidates[1]

        raw_val_results = state.get("validator_results", [])
        val_objs = [ValidatorOutcome(**v) for v in raw_val_results]
        supported = [v for v in val_objs if v.outcome == ValidationStatus.SUPPORTED]

        proposal = self.proposer_agent.propose_deterministically(c1, c2, supported)

        traces.append({
            "step_name": "propose_reconciliation",
            "agent_name": "ReconciliationProposerAgent",
            "execution_time_ms": (time.perf_counter() - start) * 1000.0,
            "input": {"supported_validators": len(supported)},
            "output": {"proposal": proposal.model_dump() if proposal else None},
        })

        return {
            "reconciliation_proposal": proposal.model_dump() if proposal else None,
            "traces": traces,
        }

    # Node 7: Adversarial Critique (Paths B & C)
    def node_critique_reconciliation(self, state: FactDecisionState) -> dict[str, Any]:
        start = time.perf_counter()
        candidates = self._to_candidates(state)
        traces = list(state.get("traces", []))
        c1, c2 = candidates[0], candidates[1]

        prop_dict = state.get("reconciliation_proposal")
        prop_obj = ReconciliationProposal(**prop_dict) if prop_dict else None

        critique = self.skeptic_agent.critique(c1, c2, prop_obj)

        traces.append({
            "step_name": "critique_reconciliation",
            "agent_name": "AdversarialSkepticAgent",
            "execution_time_ms": (time.perf_counter() - start) * 1000.0,
            "input": {"proposal_root_cause": prop_obj.root_cause if prop_obj else None},
            "output": {"skeptic_status": critique.status, "critique": critique.critique},
        })

        return {
            "skeptic_outcome": critique.model_dump(),
            "traces": traces,
        }

    # Node 8: Deterministic Policy Gate (Zero LLM Calls)
    def node_apply_policy(self, state: FactDecisionState) -> dict[str, Any]:
        start = time.perf_counter()
        candidates = self._to_candidates(state)
        traces = list(state.get("traces", []))

        val_objs = [ValidatorOutcome(**v) for v in state.get("validator_results", [])]
        prop_dict = state.get("reconciliation_proposal")
        prop_obj = ReconciliationProposal(**prop_dict) if prop_dict else None
        skep_dict = state.get("skeptic_outcome")
        skep_obj = SkepticOutcome(**skep_dict) if skep_dict else None

        verdict, strength, summary = DecisionPolicy.evaluate(
            candidates=candidates,
            validator_results=val_objs,
            reconciliation_proposal=prop_obj,
            skeptic_outcome=skep_obj,
            arithmetic_equal=state.get("arithmetic_equal", False),
            matching_context=state.get("matching_context", True),
        )

        traces.append({
            "step_name": "apply_policy",
            "agent_name": "DecisionPolicy",
            "execution_time_ms": (time.perf_counter() - start) * 1000.0,
            "input": {"arithmetic_equal": state.get("arithmetic_equal"), "path": state.get("decision_path")},
            "output": {"verdict": verdict, "decision_strength": strength, "summary": summary},
        })

        return {
            "verdict": verdict,
            "decision_strength": strength,
            "reasoning_summary": summary,
            "traces": traces,
        }

    def build_graph(self) -> Any:
        """Compile the LangGraph StateGraph with all nodes and conditional routes."""
        graph = StateGraph(FactDecisionState)

        # Register nodes
        graph.add_node("analyze_variance", self.node_analyze_variance)
        graph.add_node("evaluate_corroboration", self.node_evaluate_corroboration)
        graph.add_node("route_context", self.node_route_context)
        graph.add_node("generate_hypotheses", self.node_generate_hypotheses)
        graph.add_node("run_validators", self.node_run_validators)
        graph.add_node("propose_reconciliation", self.node_propose_reconciliation)
        graph.add_node("critique_reconciliation", self.node_critique_reconciliation)
        graph.add_node("apply_policy", self.node_apply_policy)

        # Start edge
        graph.add_edge(START, "analyze_variance")

        # Conditional routing from analyze_variance
        def route_decision_path(state: FactDecisionState) -> str:
            path = state.get("decision_path", "A")
            if path == "A":
                return "evaluate_corroboration"
            elif path == "B":
                return "route_context"
            return "generate_hypotheses"

        graph.add_conditional_edges(
            "analyze_variance",
            route_decision_path,
            {
                "evaluate_corroboration": "evaluate_corroboration",
                "route_context": "route_context",
                "generate_hypotheses": "generate_hypotheses",
            },
        )

        # Path A
        graph.add_edge("evaluate_corroboration", "apply_policy")

        # Path B
        graph.add_edge("route_context", "propose_reconciliation")

        # Path C
        graph.add_edge("generate_hypotheses", "run_validators")
        graph.add_edge("run_validators", "propose_reconciliation")

        # Convergence
        graph.add_edge("propose_reconciliation", "critique_reconciliation")
        graph.add_edge("critique_reconciliation", "apply_policy")
        graph.add_edge("apply_policy", END)

        return graph.compile()
