from __future__ import annotations

import logging
from typing import Optional

# pyrefly: ignore [missing-import]
from src.extraction.schemas import EvidenceChunk, ObservationBundle
# pyrefly: ignore [missing-import]
from src.llm.provider import ExtractionParseError, ReasoningService

logger = logging.getLogger(__name__)


EXTRACTION_SYSTEM_PROMPT = """You are an expert financial document extraction agent in EVIDRA (Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning).

Your goal is to extract factual, non-extrapolated observations from an evidence chunk into structured JSON.

STRICT EXTRACTION RULES:
1. VERBATIM FIDELITY: Record values, currencies, units, and statements EXACTLY as written in the source chunk. Never round, estimate, or calculate numbers not explicitly printed.
2. NEGATIVE VALUES: Preserve negative number formatting such as parentheses (e.g., "(1,234.50)" or "-5.4%").
3. TEMPORAL SCOPE: Extract the explicit fiscal period, quarter, or date mentioned (e.g., "FY22", "March 31, 2021", "Nine months ended Dec 31, 2021"). If no period is stated, use "Undated".
4. ATTRIBUTES: Normalize financial metric names to clear standard accounting terms (e.g., "Revenue from Operations", "EBITDA", "Net Profit/Loss", "Total Assets", "Borrowings", "Contingent Liabilities").
5. EMPTY CHUNKS: If the chunk contains only page numbers, boilerplate legal disclaimer fragments, or index listings with no meaningful business or financial statements, return empty arrays for all fields.
6. NO EXTRAPOLATION: Never infer or hallucinate facts that are not directly stated in the excerpt.
"""


class ExtractionAgent:
    """Agent responsible for harvesting factual observations from individual evidence chunks."""

    def __init__(self, reasoning_service: ReasoningService):
        self.llm = reasoning_service

    def extract_from_chunk(self, chunk: EvidenceChunk) -> ObservationBundle:
        """Analyze an EvidenceChunk and extract all structured factual claims."""
        # Fast filter: Ignore chunks that are trivially short or blank
        content = chunk.content.strip()
        if len(content) < 20:
            return ObservationBundle()

        if chunk.chunk_type == "table":
            table_text = chunk.content
            lines = table_text.splitlines()
            if len(lines) > 12:
                table_text = "\n".join(lines[:12]) + "\n| ... [rows truncated] |"
            if len(table_text) > 800:
                table_text = table_text[:800] + "\n... [table truncated]"

            prompt = (
                f"DOCUMENT EVIDENCE CHUNK (TABLE on Page {chunk.page_number}):\n"
                f"-----------------------------------------\n"
                f"{table_text}\n"
                f"-----------------------------------------\n\n"
                f"Extract the top 3-5 core financial metric line items (e.g., Revenue, EBITDA, PAT, Net Profit, Margin) "
                f"as 'numerical_observations' with their exact period and unit. "
                f"Include any specific notes or qualitative caveats present in the table as 'semantic_observations'."
            )
        else:
            text_content = chunk.content
            if len(text_content) > 800:
                text_content = text_content[:800] + "\n... [text truncated]"

            prompt = (
                f"DOCUMENT EVIDENCE CHUNK (TEXT on Page {chunk.page_number}):\n"
                f"-----------------------------------------\n"
                f"{text_content}\n"
                f"-----------------------------------------\n\n"
                f"Extract the top 3-5 explicit financial metrics (e.g., Revenue, EBITDA, PAT, Profit/Loss) "
                f"as 'numerical_observations', "
                f"and key management commentary, accounting policies, or risk factors as 'semantic_observations'."
            )

        try:
            bundle = self.llm.generate_structured(
                prompt=prompt,
                response_model=ObservationBundle,
                system_prompt=EXTRACTION_SYSTEM_PROMPT,
                max_retries=1,
            )
            return bundle
        except ExtractionParseError as e:
            logger.warning(
                f"Failed to parse observations from chunk {chunk.chunk_id} on page {chunk.page_number}: {e}"
            )
            return ObservationBundle()
        except Exception as e:
            logger.error(
                f"Unexpected error during extraction from chunk {chunk.chunk_id}: {e}"
            )
            return ObservationBundle()
