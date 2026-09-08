from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any, Optional
# pyrefly: ignore [missing-import]
from src.db.ledger import (
    DecisionRecord,
    DecisionTraceRecord,
    EvidenceLedger,
    HypothesisRecord,
    ValidatorResultRecord,
)
# pyrefly: ignore [missing-import]
from src.decision.schemas import CandidateFactView, FactDecisionState
# pyrefly: ignore [missing-import]
from src.decision.workflow import DecisionWorkflowBuilder
# pyrefly: ignore [missing-import]
from src.llm.provider import ReasoningService
# pyrefly: ignore [missing-import]
from src.observability.trace import TraceLogger

logger = logging.getLogger(__name__)


class FactDecisionEngine:
    """Orchestrates Layer 3 fact decision reasoning and adjudication across ledger fact groups."""

    def __init__(
        self,
        ledger: EvidenceLedger,
        reasoning_service: Optional[ReasoningService] = None,
        tracer: Optional[TraceLogger] = None,
    ):
        self.ledger = ledger
        self.llm = reasoning_service
        self.tracer = tracer
        self.workflow_builder = DecisionWorkflowBuilder(reasoning_service)
        self.graph = self.workflow_builder.build_graph()

    def process_fact_groups(self, job_id: Optional[str] = None) -> dict[str, Any]:
        """Execute decision workflow on all unadjudicated fact groups in the ledger."""
        start_time = time.perf_counter()

        # 1. Fetch unadjudicated fact groups
        with self.ledger.transaction() as conn:
            query = """
                SELECT g.group_id, g.entity, g.attribute, g.period_id, g.member_count
                FROM fact_groups g
                LEFT JOIN decisions d ON g.group_id = d.group_id
                WHERE d.decision_id IS NULL
            """
            groups = conn.execute(query).fetchall()

        if not groups:
            logger.info("No unadjudicated fact groups found in ledger.")
            return {
                "decisions_evaluated": 0,
                "verdicts": {"CORROBORATED": 0, "CONTRADICTION": 0, "RECONCILED": 0, "UNRESOLVED": 0},
                "latency_ms": 0.0,
            }

        logger.info(f"Evaluating {len(groups)} unadjudicated fact groups with LangGraph decision engine.")

        verdict_counts = {"CORROBORATED": 0, "CONTRADICTION": 0, "RECONCILED": 0, "UNRESOLVED": 0}
        decisions_created = 0

        for g in groups:
            group_id = g["group_id"]
            entity = g["entity"]
            attribute = g["attribute"]
            period_id = g["period_id"]

            # Fetch candidate facts with enriched provenance
            candidates = self._fetch_group_candidates(group_id)

            initial_state: FactDecisionState = {
                "group_id": group_id,
                "entity": entity,
                "attribute": attribute,
                "period_id": period_id,
                "candidates": [c.model_dump() for c in candidates],
                "traces": [],
            }

            try:
                final_state = self.graph.invoke(initial_state)
            except Exception as e:
                logger.error(f"Error evaluating group {group_id} in decision graph: {e}", exc_info=True)
                final_state = {
                    **initial_state,
                    "verdict": "UNRESOLVED",
                    "decision_strength": "INSUFFICIENT",
                    "reasoning_summary": f"Evaluation error: {str(e)}",
                    "traces": initial_state.get("traces", []),
                }

            verdict_str = str(final_state.get("verdict", "UNRESOLVED"))
            if "." in verdict_str:
                verdict_str = verdict_str.split(".")[-1]

            strength_str = str(final_state.get("decision_strength", "INSUFFICIENT"))
            if "." in strength_str:
                strength_str = strength_str.split(".")[-1]

            reasoning = final_state.get("reasoning_summary", "Decision completed.")
            decision_id = f"DEC-{uuid.uuid4().hex[:8]}"

            # Persist to SQLite ledger
            with self.ledger.transaction() as conn:
                # 1. Hypotheses
                for h in final_state.get("hypotheses", []):
                    h_type_str = str(h.get("explanation_type", "ERRONEOUS_CONTRADICTION"))
                    if "." in h_type_str:
                        h_type_str = h_type_str.split(".")[-1]
                    hyp_rec = HypothesisRecord(
                        hypothesis_id=h["hypothesis_id"],
                        group_id=group_id,
                        explanation_type=h_type_str,
                        description=h["description"],
                        likelihood_score=float(h.get("likelihood_score", 0.5)),
                    )
                    self.ledger.insert_hypothesis(hyp_rec)

                # 2. Validator Results
                for v in final_state.get("validator_results", []):
                    outcome_str = str(v.get("outcome", "INCONCLUSIVE"))
                    if "." in outcome_str:
                        outcome_str = outcome_str.split(".")[-1]
                    val_rec = ValidatorResultRecord(
                        result_id=v["result_id"],
                        hypothesis_id=v["hypothesis_id"],
                        validator_type=v["validator_type"],
                        outcome=outcome_str,
                        details_json=json.dumps(v.get("details", {})),
                    )
                    self.ledger.insert_validator_result(val_rec)

                # 3. Decision Record
                dec_rec = DecisionRecord(
                    decision_id=decision_id,
                    group_id=group_id,
                    verdict=verdict_str,
                    decision_strength=strength_str,
                    reasoning_summary=reasoning,
                )
                self.ledger.record_decision(dec_rec)

                # 4. Decision Traces
                for t in final_state.get("traces", []):
                    trace_rec = DecisionTraceRecord(
                        trace_id=f"TRC-DEC-{uuid.uuid4().hex[:8]}",
                        decision_id=decision_id,
                        step_name=t.get("step_name", "decision_step"),
                        agent_name=t.get("agent_name", "DecisionWorkflow"),
                        input_json=json.dumps(t.get("input", {})),
                        output_json=json.dumps(t.get("output", {})),
                        execution_time_ms=float(t.get("execution_time_ms", 0.0)),
                    )
                    self.ledger.append_decision_trace(trace_rec)

                    if self.tracer:
                        self.tracer.log_step(
                            step_name=f"decision_{t.get('step_name')}",
                            agent_name=t.get("agent_name", "DecisionWorkflow"),
                            input_payload=t.get("input", {}),
                            output_payload=t.get("output", {}),
                            latency_ms=float(t.get("execution_time_ms", 0.0)),
                        )

            verdict_counts[verdict_str] = verdict_counts.get(verdict_str, 0) + 1
            decisions_created += 1

        total_latency_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "decisions_evaluated": decisions_created,
            "verdicts": verdict_counts,
            "latency_ms": round(total_latency_ms, 2),
        }

    def _fetch_group_candidates(self, group_id: str) -> list[CandidateFactView]:
        """Fetch all member facts with observations, chunks, and document records for a group."""
        with self.ledger.transaction() as conn:
            query = """
                SELECT f.fact_id, f.observation_id, f.normalized_value, f.normalized_unit,
                       f.normalized_currency, f.period_start, f.period_end,
                       o.document_id, o.statement, o.raw_value,
                       c.page_number, c.bounding_box, c.content AS chunk_content,
                       d.filename
                FROM group_members gm
                JOIN fact_candidates f ON gm.fact_id = f.fact_id
                JOIN observations o ON f.observation_id = o.observation_id
                LEFT JOIN evidence_chunks c ON o.chunk_id = c.chunk_id
                LEFT JOIN documents d ON o.document_id = d.document_id
                WHERE gm.group_id = ?
            """
            rows = conn.execute(query, (group_id,)).fetchall()

        candidates: list[CandidateFactView] = []
        for r in rows:
            bbox = []
            if r["bounding_box"]:
                try:
                    bbox = json.loads(r["bounding_box"])
                except Exception:
                    bbox = []

            # Infer context deterministically from statement and content
            # pyrefly: ignore [missing-import]
            from src.verification.context import ContextResolverAgent
            ctx = ContextResolverAgent.resolve_deterministically(
                statement=r["statement"] or "",
                chunk_content=r["chunk_content"] or "",
                filename=r["filename"] or "",
            )

            candidates.append(
                CandidateFactView(
                    fact_id=r["fact_id"],
                    observation_id=r["observation_id"],
                    document_id=r["document_id"] or "DOC-UNKNOWN",
                    filename=r["filename"] or "",
                    page_number=r["page_number"] or 1,
                    bounding_box=bbox,
                    chunk_content=r["chunk_content"] or "",
                    statement=r["statement"] or "",
                    raw_value=r["raw_value"] or "",
                    normalized_value=r["normalized_value"] or "",
                    normalized_unit=r["normalized_unit"] or "",
                    normalized_currency=r["normalized_currency"] or "",
                    period_start=r["period_start"] or "1970-01-01",
                    period_end=r["period_end"] or "1970-01-01",
                    accounting_basis=ctx.accounting_basis,
                    organizational_scope=ctx.organizational_scope,
                    filing_type=ctx.filing_type,
                    version_status=ctx.version_status,
                )
            )

        return candidates
