from __future__ import annotations

import logging
import time
import uuid
from pathlib import Path
from typing import Any, Optional
# pyrefly: ignore [missing-import]
from src.db.ledger import EvidenceLedger, FactCandidateRecord
# pyrefly: ignore [missing-import]
from src.llm.provider import OllamaProvider, ReasoningService
# pyrefly: ignore [missing-import]
from src.matching.embeddings import FactGroupEngine
# pyrefly: ignore [missing-import]
from src.observability.trace import TraceLogger
# pyrefly: ignore [missing-import]
from src.verification.context import ContextResolverAgent
# pyrefly: ignore [missing-import]
from src.verification.normalizers import (
    CurrencyNormalizer,
    DecimalNormalizer,
    TemporalNormalizer,
)
# pyrefly: ignore [missing-import]
from src.verification.verifier import EvidenceVerifierAgent

logger = logging.getLogger(__name__)


class VerificationPipeline:
    """Orchestrates observation verification, context resolution, normalization, and fact grouping."""

    def __init__(
        self,
        ledger: EvidenceLedger,
        tracer: Optional[TraceLogger] = None,
        reasoning_service: Optional[ReasoningService] = None,
        skip_verifier: bool = False,
    ):
        self.ledger = ledger
        self.tracer = tracer
        self.llm = reasoning_service or OllamaProvider()
        self.verifier = EvidenceVerifierAgent(self.llm)
        self.context_resolver = ContextResolverAgent(self.llm)
        self.group_engine = FactGroupEngine()
        self.skip_verifier = skip_verifier

    def process_observations(self, document_id: Optional[str] = None) -> dict[str, Any]:
        """Execute verification, normalization, and fact candidate grouping on ledger observations."""
        start_time = time.perf_counter()

        # 1. Fetch ungrounded/candidate observations and their evidence chunks
        with self.ledger.transaction() as conn:
            query = """
                SELECT o.*, c.content AS chunk_content
                FROM observations o
                LEFT JOIN evidence_chunks c ON o.chunk_id = c.chunk_id
                WHERE o.provenance_status != 'HALLUCINATED'
            """
            params = []
            if document_id:
                query += " AND o.document_id = ?"
                params.append(document_id)
            
            obs_rows = conn.execute(query, params).fetchall()

        if not obs_rows:
            logger.info("No active observations to verify and normalize.")
            return {"candidates_count": 0, "groups_count": 0, "hallucinations_flagged": 0}

        fact_records: list[FactCandidateRecord] = []
        candidate_dicts: list[dict[str, Any]] = []
        hallucinations_flagged = 0

        for row in obs_rows:
            obs_id = row["observation_id"]
            statement = row["statement"]
            chunk_content = row["chunk_content"] or ""
            raw_value = row["raw_value"]
            entity = row["entity"]
            attribute = row["attribute"]
            temporal_scope = row["temporal_scope"]

            # Adversarial Entailment Verification (optional or on non-empty chunks)
            if not self.skip_verifier and chunk_content:
                verdict = self.verifier.verify_observation(statement, chunk_content)
                if getattr(verdict, "status", None) == "HALLUCINATED":
                    expl = getattr(verdict, "explanation", "Flagged by verifier agent")
                    logger.warning(
                        f"Observation {obs_id} flagged as HALLUCINATED: {expl}"
                    )
                    hallucinations_flagged += 1
                    with self.ledger.transaction() as conn:
                        conn.execute(
                            "UPDATE observations SET provenance_status = 'HALLUCINATED' WHERE observation_id = ?;",
                            (obs_id,),
                        )
                    continue

            # Deterministic Normalization
            norm_val, norm_unit = DecimalNormalizer.normalize(raw_value)
            norm_currency = CurrencyNormalizer.normalize(raw_value)
            period_start, period_end = TemporalNormalizer.normalize(temporal_scope)

            fact_id = f"FCT-{uuid.uuid4().hex[:8]}"
            normalized_val_str = str(norm_val) if norm_val is not None else raw_value

            fact_record = FactCandidateRecord(
                fact_id=fact_id,
                observation_id=obs_id,
                normalized_value=normalized_val_str,
                normalized_unit=norm_unit,
                normalized_currency=norm_currency,
                period_start=period_start,
                period_end=period_end,
            )
            fact_records.append(fact_record)
            candidate_dicts.append({
                "fact_id": fact_id,
                "observation_id": obs_id,
                "entity": entity,
                "attribute": attribute,
                "raw_value": raw_value,
                "normalized_value": normalized_val_str,
                "period_start": period_start,
                "period_end": period_end,
            })

        # 2. Bulk insert Fact Candidates into SQLite
        candidates_inserted = 0
        if fact_records:
            candidates_inserted = self.ledger.insert_fact_candidates(fact_records)
            logger.info(f"Persisted {candidates_inserted} fact candidates to ledger.")

        # 3. Two-Tier Candidate Grouping & Blocking
        grouped_clusters = self.group_engine.group_candidates(candidate_dicts)
        groups_created = 0

        for group_record, fact_ids in grouped_clusters:
            try:
                self.ledger.create_fact_group(
                    entity=group_record.entity,
                    attribute=group_record.attribute,
                    period_id=group_record.period_id,
                    fact_ids=fact_ids,
                    group_id=group_record.group_id,
                )
                groups_created += 1
            except Exception as e:
                logger.warning(f"Failed to create fact group {group_record.group_id}: {e}")

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        # 4. Telemetry Logging
        if self.tracer:
            self.tracer.log_step(
                step_name="verification_pipeline",
                agent_name="VerificationPipeline",
                input_payload={"observations_processed": len(obs_rows)},
                output_payload={
                    "candidates_created": candidates_inserted,
                    "groups_created": groups_created,
                    "hallucinations_flagged": hallucinations_flagged,
                },
                latency_ms=latency_ms,
            )

        return {
            "candidates_count": candidates_inserted,
            "groups_count": groups_created,
            "hallucinations_flagged": hallucinations_flagged,
            "latency_ms": round(latency_ms, 2),
        }
