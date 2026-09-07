from __future__ import annotations

import logging
import re
import time
import uuid
from pathlib import Path
from typing import Any, Optional
# pyrefly: ignore [missing-import]
from src.db.ledger import EvidenceChunkRecord, EvidenceLedger, ObservationRecord
# pyrefly: ignore [missing-import]
from src.extraction.agents import ExtractionAgent
# pyrefly: ignore [missing-import]
from src.extraction.schemas import EvidenceChunk
# pyrefly: ignore [missing-import]
from src.llm.provider import OllamaProvider, ReasoningService
# pyrefly: ignore [missing-import]
from src.observability.trace import TraceLogger
# pyrefly: ignore [missing-import]
from src.pdf.parser import ExtractedBlock, PDFParser

logger = logging.getLogger(__name__)

# Keywords indicating potential factual, financial, or corporate content
FINANCIAL_INDICATORS = re.compile(
    r"\b("
    r"\d+[\d,\.]*|"
    r"revenue|profit|loss|ebitda|income|expense|asset|liability|equity|"
    r"borrowing|debt|cash|flow|crore|million|billion|inr|rs|usd|"
    r"margin|ratio|diluted|basic|eps|share|dividend|tax|pat|pbt|"
    r"acquisition|subsidiary|restructur|fiscal|quarter|fy\d\d|"
    r"auditor|director|board|pledge|contingent|capital"
    r")\b",
    re.IGNORECASE,
)


class ExtractionPipeline:
    """Coordinates PDF layout parsing, evidence chunk persistence, LLM fact extraction, and ledger recording."""

    def __init__(
        self,
        ledger: EvidenceLedger,
        tracer: Optional[TraceLogger] = None,
        reasoning_service: Optional[ReasoningService] = None,
        max_llm_chunks: Optional[int] = None,
    ):
        self.ledger = ledger
        self.tracer = tracer
        self.llm = reasoning_service or OllamaProvider()
        self.parser = PDFParser()
        self.agent = ExtractionAgent(self.llm)
        self.max_llm_chunks = max_llm_chunks  # Guardrail for selective inference

    @staticmethod
    def _is_extraction_candidate(block: ExtractedBlock) -> bool:
        """Determine if a block contains tabular data, numbers, or financial terminology."""
        if block.block_type == "table":
            return True
        content = block.content.strip()
        if len(content) < 30:
            return False
        return bool(FINANCIAL_INDICATORS.search(content))

    def process_document(self, document_id: str, pdf_path: Path | str) -> dict[str, Any]:
        """Execute full extraction workflow on a document and persist results to ledger."""
        path = Path(pdf_path)
        start_time = time.perf_counter()

        logger.info(f"Starting extraction pipeline for {document_id}: {path.name}")

        # 1. Parse PDF layout and tables
        extracted_blocks = self.parser.parse_document(path)
        max_page = max((b.page_number for b in extracted_blocks), default=1)

        # Ensure document record exists in ledger or update page count
        with self.ledger.transaction() as conn:
            row = conn.execute("SELECT document_id FROM documents WHERE document_id = ?;", (document_id,)).fetchone()
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

        # 3. Filter candidate chunks for LLM extraction
        candidate_pairs = [
            (chunk, block)
            for chunk, block in zip(evidence_chunks, extracted_blocks)
            if self._is_extraction_candidate(block)
        ]

        # Apply guardrail limit if specified
        if self.max_llm_chunks and len(candidate_pairs) > self.max_llm_chunks:
            # Prioritize tables first, then narrative text with highest keyword density
            candidate_pairs.sort(key=lambda pair: (0 if pair[0].chunk_type == "table" else 1))
            candidate_pairs = candidate_pairs[: self.max_llm_chunks]

        # 4. Invoke extraction agents across candidates
        observations: list[ObservationRecord] = []

        for chunk, _ in candidate_pairs:
            bundle = self.agent.extract_from_chunk(chunk)

            # Map Numerical Observations
            for num in bundle.numerical_observations:
                obs_id = f"OBS-NUM-{uuid.uuid4().hex[:8]}"
                observations.append(
                    ObservationRecord(
                        observation_id=obs_id,
                        chunk_id=chunk.chunk_id,
                        document_id=document_id,
                        statement=num.statement,
                        entity=num.entity or "Reporting Entity",
                        attribute=num.attribute,
                        raw_value=f"{num.raw_value} {num.unit} {num.currency}".strip(),
                        observation_type="numerical",
                        temporal_scope=num.temporal_scope or "Undated",
                        confidence=num.confidence,
                        provenance_status="ENTAILED",
                    )
                )

            # Map Semantic Observations
            for sem in bundle.semantic_observations:
                obs_id = f"OBS-SEM-{uuid.uuid4().hex[:8]}"
                observations.append(
                    ObservationRecord(
                        observation_id=obs_id,
                        chunk_id=chunk.chunk_id,
                        document_id=document_id,
                        statement=sem.statement,
                        entity=sem.entity or "Reporting Entity",
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
                obs_id = f"OBS-EVT-{uuid.uuid4().hex[:8]}"
                observations.append(
                    ObservationRecord(
                        observation_id=obs_id,
                        chunk_id=chunk.chunk_id,
                        document_id=document_id,
                        statement=evt.statement,
                        entity=evt.entity or "Reporting Entity",
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

        # 5. Log audit trace
        if self.tracer:
            self.tracer.log_step(
                step_name="extraction_pipeline",
                agent_name="ExtractionPipeline",
                input_payload={
                    "document_id": document_id,
                    "filename": path.name,
                    "total_layout_blocks": len(extracted_blocks),
                    "candidates_analyzed": len(candidate_pairs),
                },
                output_payload={
                    "evidence_chunks_stored": chunks_inserted,
                    "observations_stored": observations_inserted,
                },
                latency_ms=latency_ms,
            )

        # 6. Execute D3 Verification, Normalization, and Fact Grouping Pipeline
        # pyrefly: ignore [missing-import]
        from src.verification.pipeline import VerificationPipeline
        verif_pipeline = VerificationPipeline(
            ledger=self.ledger,
            tracer=self.tracer,
            reasoning_service=self.llm,
        )
        verif_res = verif_pipeline.process_observations(document_id=document_id)

        return {
            "document_id": document_id,
            "page_count": max_page,
            "evidence_chunks_count": chunks_inserted,
            "observations_count": observations_inserted,
            "fact_candidates_count": verif_res.get("candidates_count", 0),
            "fact_groups_count": verif_res.get("groups_count", 0),
            "latency_ms": round(latency_ms, 2),
        }
