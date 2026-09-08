"""
ExtractionPipeline for EVIDRA 2.0 (Phase P0).

Coordinates PDF layout parsing, layout topology analysis, context-enriched
evidence windows, lightweight schema induction, 3-tier budget-aware candidate
discovery, LLM fact extraction, and ledger persistence.
"""

from __future__ import annotations

import json
import logging
import re
import time
import uuid
from pathlib import Path
from typing import Any, List, Optional, Tuple

# pyrefly: ignore [missing-import]
from src.db.ledger import (
    EvidenceChunkRecord,
    EvidenceLedger,
    EvidenceWindowRecord,
    ObservationRecord,
)
# pyrefly: ignore [missing-import]
from src.extraction.agents import GENERIC_ENTITIES, ExtractionAgent
# pyrefly: ignore [missing-import]
from src.extraction.schemas import EvidenceChunk, EvidenceWindow
# pyrefly: ignore [missing-import]
from src.extraction.schema_induction import SchemaInductionEngine
# pyrefly: ignore [missing-import]
from src.extraction.windows import EvidenceWindowBuilder
# pyrefly: ignore [missing-import]
from src.llm.provider import OllamaProvider, ReasoningService
# pyrefly: ignore [missing-import]
from src.observability.trace import TraceLogger
# pyrefly: ignore [missing-import]
from src.pdf.parser import ExtractedBlock, PDFParser
# pyrefly: ignore [missing-import]
from src.pdf.topology import DocumentTopologyBuilder

logger = logging.getLogger(__name__)

# Keywords indicating potential factual, financial, or corporate content
FINANCIAL_INDICATORS = re.compile(
    r"\b("
    r"\d+[\d,\.]*|"
    r"revenue|profit|loss|ebitda|income|expense|asset|liability|equity|"
    r"borrowing|debt|cash|flow|crore|million|billion|lakh|inr|rs|usd|"
    r"margin|ratio|diluted|basic|eps|share|dividend|tax|pat|pbt|"
    r"acquisition|subsidiary|restructur|fiscal|quarter|fy\d\d|"
    r"auditor|director|board|pledge|contingent|capital|"
    r"shipment|volume|parcel|express|freight"
    r")\b",
    re.IGNORECASE,
)


class ExtractionPipeline:
    """Coordinates PDF layout parsing, topology inference, window context enrichment, and fact extraction."""

    def __init__(
        self,
        ledger: EvidenceLedger,
        tracer: Optional[TraceLogger] = None,
        reasoning_service: Optional[ReasoningService] = None,
        max_llm_chunks: Optional[int] = None,
        skip_verifier: bool = False,
        evidence_dir: Optional[Path | str] = None,
        per_document_budget: int = 30,
    ):
        self.ledger = ledger
        self.tracer = tracer
        self.llm = reasoning_service or OllamaProvider()
        self.parser = PDFParser()
        self.agent = ExtractionAgent(self.llm)
        self.max_llm_chunks = max_llm_chunks  # Guardrail limit
        self.skip_verifier = skip_verifier
        self.per_document_budget = max_llm_chunks if max_llm_chunks is not None else per_document_budget
        if evidence_dir:
            self.evidence_dir = Path(evidence_dir)
        elif hasattr(ledger, "db_path") and ledger.db_path:
            self.evidence_dir = Path(ledger.db_path).parent / "evidence"
        else:
            self.evidence_dir = None

    @staticmethod
    def _is_extraction_candidate(block: ExtractedBlock) -> bool:
        """Determine if a block contains tabular data, numbers, or financial terminology."""
        if block.block_type == "table":
            return True
        content = block.content.strip()
        if len(content) < 30:
            return False
        return bool(FINANCIAL_INDICATORS.search(content))

    @staticmethod
    def _score_candidate(chunk: EvidenceChunk) -> int:
        """Score candidate chunks by financial keyword density, numerical tokens, and concise length."""
        content_lower = chunk.content.lower()
        score = 0
        keywords = (
            "revenue", "ebitda", "operating income", "total income", "profit",
            "loss", "balance sheet", "crore", "lakh", "million", "fy24", "fy23", "fy22", "q4"
        )
        for kw in keywords:
            if kw in content_lower:
                score += 2
        num_digits = sum(c.isdigit() for c in chunk.content)
        if num_digits > 15:
            score += 3
        if chunk.chunk_type == "table":
            score += 2
        if 200 <= len(chunk.content) <= 1800:
            score += 4
        elif len(chunk.content) > 3000:
            score -= 5
        return score

    @staticmethod
    def _score_candidate_window(window: EvidenceWindow) -> int:
        """Score candidate windows by financial keyword density, numerical tokens, and layout context."""
        content_lower = window.content.lower()
        score = 0
        keywords = (
            "revenue", "ebitda", "operating income", "total income", "profit",
            "loss", "balance sheet", "crore", "lakh", "million", "fy24", "fy23", "fy22", "q4",
            "express parcel", "shipment", "freight", "borrowings", "cash flow"
        )
        for kw in keywords:
            if kw in content_lower:
                score += 2
        num_digits = sum(c.isdigit() for c in window.content)
        if num_digits > 15:
            score += 3
        if window.chunk_type == "table":
            score += 4
        if window.section_title and window.section_confidence >= 0.70:
            score += 2
        if 200 <= len(window.content) <= 1800:
            score += 4
        elif len(window.content) > 3000:
            score -= 5
        return score

    def discover_candidates(
        self,
        windows: List[EvidenceWindow],
        per_document_budget: int = 30,
    ) -> List[EvidenceWindow]:
        """
        3-Tier Budget-Aware Candidate Discovery:
        - Tier 1: 100% of tables retained; text filtered for minimum length & financial indicators.
        - Tier 2: Relevance scoring across text candidates.
        - Tier 3: Budget allocation prioritizing all tables, then top scoring text candidates.
        """
        tables: List[EvidenceWindow] = []
        text_candidates: List[EvidenceWindow] = []

        for w in windows:
            if w.chunk_type == "table":
                tables.append(w)
            else:
                content = w.content.strip()
                if len(content) >= 40 and FINANCIAL_INDICATORS.search(content):
                    text_candidates.append(w)

        # Tier 2: Relevance Scoring across both tables and text
        scored_tables = [(w, self._score_candidate_window(w)) for w in tables]
        scored_tables.sort(key=lambda item: item[1], reverse=True)

        scored_texts = [(w, self._score_candidate_window(w)) for w in text_candidates]
        scored_texts.sort(key=lambda item: item[1], reverse=True)

        # Tier 3: Budget-Aware Allocation
        total_budget = self.max_llm_chunks if self.max_llm_chunks is not None else per_document_budget

        # If both tables and text exist and tables exceed total budget, guarantee a 30% allocation to text
        if text_candidates and len(tables) >= total_budget:
            text_target = max(1, int(total_budget * 0.30))
            table_target = total_budget - text_target
            selected = [w for w, _ in scored_tables[:table_target]]
            selected.extend([w for w, _ in scored_texts[:text_target]])
        else:
            # When tables fit within budget, retain all tables and fill remainder with text
            selected = [w for w, _ in scored_tables[:total_budget]]
            remaining = max(0, total_budget - len(selected))
            selected.extend([w for w, _ in scored_texts[:remaining]])

        return selected

    def process_document(
        self,
        document_id: str,
        pdf_path: Path | str,
        defer_reasoning: bool = False,
    ) -> dict[str, Any]:
        """Execute full P0 extraction workflow on a document and persist results to ledger."""
        path = Path(pdf_path)
        start_time = time.perf_counter()

        logger.info(f"Starting extraction pipeline for {document_id}: {path.name}")

        # 1. Parse PDF layout and tables
        extracted_blocks = self.parser.parse_document(path)
        max_page = max((b.page_number for b in extracted_blocks), default=1)

        # Ensure document record exists in ledger or update page count
        with self.ledger.transaction() as conn:
            row = conn.execute(
                "SELECT document_id FROM documents WHERE document_id = ?;", (document_id,)
            ).fetchone()
            if not row:
                import hashlib
                with open(path, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                conn.execute(
                    "INSERT INTO documents (document_id, filename, file_hash, page_count) VALUES (?, ?, ?, ?);",
                    (document_id, path.name, file_hash, max_page),
                )
            else:
                conn.execute(
                    "UPDATE documents SET page_count = ? WHERE document_id = ?;",
                    (max_page, document_id),
                )

        # 2. Convert ExtractedBlocks to EvidenceChunks and persist
        evidence_chunks: list[EvidenceChunk] = []
        chunk_records: list[EvidenceChunkRecord] = []

        for block in extracted_blocks:
            chunk = EvidenceChunk.create(
                document_id=document_id,
                page_number=block.page_number,
                chunk_type=block.block_type if block.block_type in ("text", "table", "figure") else "text",
                bounding_box=list(block.bounding_box),
                content=block.content,
            )
            evidence_chunks.append(chunk)
            chunk_records.append(
                EvidenceChunkRecord(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    page_number=chunk.page_number,
                    chunk_type=chunk.chunk_type,
                    bounding_box=chunk.bounding_box,
                    content=chunk.content,
                    content_hash=chunk.content_hash,
                )
            )

        chunks_inserted = self.ledger.insert_evidence_chunks(chunk_records)
        logger.info(f"Persisted {chunks_inserted} evidence chunks for {document_id}")

        # 3. Multi-Signal Layout Hierarchy Inference
        topology_builder = DocumentTopologyBuilder()
        doc_topology = topology_builder.build(
            blocks=extracted_blocks,
            document_id=document_id,
        )

        # 4. Context-Enriched Evidence Windows
        window_builder = EvidenceWindowBuilder()
        evidence_windows = window_builder.build_windows(
            chunks=evidence_chunks,
            blocks=extracted_blocks,
            topology=doc_topology,
        )

        window_records = [
            EvidenceWindowRecord(
                window_id=w.window_id,
                chunk_id=w.chunk_id,
                document_id=w.document_id,
                page_number=w.page_number,
                section_title=w.section_title,
                section_confidence=w.section_confidence,
                table_caption=w.table_caption,
                stated_unit=w.stated_unit,
                stated_currency=w.stated_currency,
                column_headers=json.dumps(w.column_headers),
                row_context=w.row_context,
                page_header=w.page_header,
                footnotes=json.dumps(w.footnotes),
            )
            for w in evidence_windows
        ]
        windows_inserted = self.ledger.insert_evidence_windows(window_records)
        logger.info(f"Persisted {windows_inserted} evidence windows for {document_id}")

        # 5. Lightweight Schema Induction
        schema_engine = SchemaInductionEngine()
        doc_schema = schema_engine.induce_schema(document_id, evidence_windows)
        primary_entity = doc_schema.primary_entity
        logger.info(
            f"Induced schema for {document_id}: primary_entity='{primary_entity}', "
            f"metric_families={len(doc_schema.metric_families)}"
        )

        # 6. 3-Tier Budget-Aware Candidate Discovery
        candidate_windows = self.discover_candidates(
            windows=evidence_windows,
            per_document_budget=self.per_document_budget,
        )
        logger.info(
            f"Selected {len(candidate_windows)} candidate windows for inference "
            f"(budget={self.per_document_budget})"
        )

        # Export cached evidence artifacts if evidence_dir is configured
        if self.evidence_dir:
            try:
                ev_dir = Path(self.evidence_dir)
                tables_dir = ev_dir / "tables"
                cands_dir = ev_dir / "candidates"
                tables_dir.mkdir(parents=True, exist_ok=True)
                cands_dir.mkdir(parents=True, exist_ok=True)

                for w in evidence_windows:
                    if w.chunk_type == "table":
                        tbl_file = tables_dir / f"{document_id}_p{w.page_number}_{w.chunk_id[:8]}.md"
                        if not tbl_file.exists():
                            with open(tbl_file, "w", encoding="utf-8") as f:
                                f.write(f"# Extracted Table: {document_id} (Page {w.page_number})\n\n")
                                f.write(f"- **Window ID:** `{w.window_id}`\n")
                                f.write(f"- **Chunk ID:** `{w.chunk_id}`\n")
                                f.write(f"- **Section:** {w.section_title} (conf: {w.section_confidence:.2f})\n")
                                f.write(f"- **Caption:** {w.table_caption}\n")
                                f.write(f"- **Stated Unit:** {w.stated_unit} {w.stated_currency}\n\n")
                                f.write("## Table Content\n\n")
                                f.write(w.content + "\n")

                for w in candidate_windows:
                    cand_file = cands_dir / f"{document_id}_p{w.page_number}_{w.chunk_id[:8]}.md"
                    with open(cand_file, "w", encoding="utf-8") as f:
                        f.write(f"# Candidate Window: {document_id} (Page {w.page_number})\n\n")
                        f.write(f"- **Window ID:** `{w.window_id}`\n")
                        f.write(f"- **Type:** `{w.chunk_type}`\n")
                        f.write(f"- **Section:** {w.section_title}\n")
                        f.write(f"- **Stated Unit:** {w.stated_unit} {w.stated_currency}\n\n")
                        f.write("## Content\n\n")
                        f.write(w.content + "\n")

                manifest_file = ev_dir / f"{document_id}_manifest.json"
                manifest = {
                    "document_id": document_id,
                    "filename": path.name,
                    "page_count": max_page,
                    "primary_entity": primary_entity,
                    "total_chunks": len(evidence_chunks),
                    "total_windows": len(evidence_windows),
                    "table_chunks_count": sum(1 for w in evidence_windows if w.chunk_type == "table"),
                    "text_chunks_count": sum(1 for w in evidence_windows if w.chunk_type == "text"),
                    "candidate_windows_count": len(candidate_windows),
                    "candidate_window_ids": [w.window_id for w in candidate_windows],
                }
                with open(manifest_file, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, indent=2)

                schema_file = ev_dir / f"{document_id}_schema.json"
                with open(schema_file, "w", encoding="utf-8") as f:
                    json.dump(doc_schema.model_dump(), f, indent=2)
            except Exception as e:
                logger.warning(f"Failed to export evidence artifacts for {document_id}: {e}")

        # 7. Invoke extraction agents across candidates
        observations: list[ObservationRecord] = []

        for idx, window in enumerate(candidate_windows, 1):
            print(
                f"  -> Extracting {document_id} window {idx}/{len(candidate_windows)} "
                f"(Page {window.page_number}, {window.chunk_type})... ",
                end="",
                flush=True,
            )
            chunk_start = time.perf_counter()
            bundle = self.agent.extract_from_chunk(
                chunk=window,
                primary_entity=primary_entity if primary_entity != "Unknown Entity" else None,
            )
            chunk_time = time.perf_counter() - chunk_start
            n_obs = (
                len(bundle.numerical_observations)
                + len(bundle.semantic_observations)
                + len(bundle.event_observations)
            )
            print(f"done in {chunk_time:.1f}s ({n_obs} observations)")

            # Resolve fallback entity if LLM extracted generic placeholder
            default_entity = primary_entity if primary_entity != "Unknown Entity" else "Delhivery Limited"

            # Map Numerical Observations
            for num in bundle.numerical_observations:
                entity = num.entity.strip() if num.entity and num.entity.strip().lower() not in GENERIC_ENTITIES else default_entity
                obs_id = f"OBS-NUM-{uuid.uuid4().hex[:8]}"

                raw_val = num.raw_value
                if num.unit and num.unit.lower() not in raw_val.lower():
                    raw_val = f"{raw_val} {num.unit}".strip()
                if num.currency and num.currency.lower() not in raw_val.lower():
                    raw_val = f"{raw_val} {num.currency}".strip()

                observations.append(
                    ObservationRecord(
                        observation_id=obs_id,
                        chunk_id=window.chunk_id,
                        document_id=document_id,
                        statement=num.statement,
                        entity=entity,
                        attribute=num.attribute,
                        raw_value=raw_val,
                        observation_type="numerical",
                        temporal_scope=num.temporal_scope or "Undated",
                        confidence=num.confidence,
                        provenance_status="ENTAILED",
                    )
                )

            # Map Semantic Observations
            for sem in bundle.semantic_observations:
                entity = sem.entity.strip() if sem.entity and sem.entity.strip().lower() not in GENERIC_ENTITIES else default_entity
                obs_id = f"OBS-SEM-{uuid.uuid4().hex[:8]}"
                observations.append(
                    ObservationRecord(
                        observation_id=obs_id,
                        chunk_id=window.chunk_id,
                        document_id=document_id,
                        statement=sem.statement,
                        entity=entity,
                        attribute=sem.attribute,
                        raw_value=sem.raw_value,
                        observation_type="semantic",
                        temporal_scope=sem.temporal_scope or "Undated",
                        confidence=sem.confidence,
                        provenance_status="ENTAILED",
                    )
                )

            # Map Event Observations
            for evt in bundle.event_observations:
                entity = evt.entity.strip() if evt.entity and evt.entity.strip().lower() not in GENERIC_ENTITIES else default_entity
                obs_id = f"OBS-EVT-{uuid.uuid4().hex[:8]}"
                observations.append(
                    ObservationRecord(
                        observation_id=obs_id,
                        chunk_id=window.chunk_id,
                        document_id=document_id,
                        statement=evt.statement,
                        entity=entity,
                        attribute=evt.attribute,
                        raw_value=evt.raw_value,
                        observation_type="event",
                        temporal_scope=evt.temporal_scope or "Undated",
                        confidence=evt.confidence,
                        provenance_status="ENTAILED",
                    )
                )

        observations_inserted = 0
        if observations:
            observations_inserted = self.ledger.insert_observations(observations)
            logger.info(f"Persisted {observations_inserted} observations for {document_id}")

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        # 8. Log audit trace
        if self.tracer:
            self.tracer.log_step(
                step_name="extraction_pipeline",
                agent_name="ExtractionPipeline",
                input_payload={
                    "document_id": document_id,
                    "filename": path.name,
                    "total_layout_blocks": len(extracted_blocks),
                    "candidates_analyzed": len(candidate_windows),
                },
                output_payload={
                    "evidence_chunks_stored": chunks_inserted,
                    "evidence_windows_stored": windows_inserted,
                    "observations_stored": observations_inserted,
                },
                latency_ms=latency_ms,
            )

        # 9. Execute D3 Verification, Normalization, and Fact Grouping Pipeline
        # pyrefly: ignore [missing-import]
        from src.verification.pipeline import VerificationPipeline
        verif_pipeline = VerificationPipeline(
            ledger=self.ledger,
            tracer=self.tracer,
            reasoning_service=self.llm,
            skip_verifier=self.skip_verifier,
        )
        verif_res = verif_pipeline.process_observations(
            document_id=document_id,
            defer_grouping=defer_reasoning,
        )

        # 10. Execute D4 Fact Decision Engine
        dec_res = {}
        if not defer_reasoning:
            # pyrefly: ignore [missing-import]
            from src.decision.engine import FactDecisionEngine
            decision_engine = FactDecisionEngine(
                ledger=self.ledger,
                reasoning_service=self.llm,
                tracer=self.tracer,
            )
            dec_res = decision_engine.process_fact_groups()

        return {
            "document_id": document_id,
            "page_count": max_page,
            "evidence_chunks_count": chunks_inserted,
            "evidence_windows_count": windows_inserted,
            "observations_count": observations_inserted,
            "fact_candidates_count": verif_res.get("candidates_count", 0),
            "fact_groups_count": verif_res.get("groups_count", 0),
            "decisions_count": dec_res.get("decisions_evaluated", 0),
            "latency_ms": round(latency_ms, 2),
        }
