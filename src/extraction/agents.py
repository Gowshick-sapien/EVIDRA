"""
ExtractionAgent for EVIDRA 2.0 (Phase P0).

Harvests structured numerical, semantic, and event observations from
context-enriched EvidenceWindows with strict anti-generic entity enforcement,
unit/currency context inheritance, and verbatim entailment verification.
"""

from __future__ import annotations

import logging
import re
from typing import Optional, Set, Union

# pyrefly: ignore [missing-import]
from src.extraction.schemas import (
    EvidenceChunk,
    EvidenceWindow,
    NumericalObservation,
    ObservationBundle,
    SemanticObservation,
)
# pyrefly: ignore [missing-import]
from src.llm.provider import ExtractionParseError, ReasoningService
# pyrefly: ignore [missing-import]
from src.verification.normalizers import TemporalNormalizer

logger = logging.getLogger(__name__)

GENERIC_ENTITIES: Set[str] = {
    "reporting entity",
    "the company",
    "company",
    "management",
    "total",
    "consolidated",
    "standalone",
    "group",
    "unknown entity",
    "n/a",
    "none",
    "our company",
}

EXTRACTION_SYSTEM_PROMPT = """You are an expert financial document extraction agent in EVIDRA (Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning).

Your goal is to extract factual, non-extrapolated observations from an evidence window into structured JSON.

STRICT EXTRACTION RULES:
1. VERBATIM FIDELITY: Record values, currencies, units, and statements EXACTLY as written in the source chunk. Never round, estimate, or calculate numbers not explicitly printed.
2. NEGATIVE VALUES: Preserve negative number formatting such as parentheses (e.g., "(1,234.50)" or "-5.4%").
3. TEMPORAL SCOPE: Extract the explicit fiscal period, quarter, or date mentioned (e.g., "FY22", "March 31, 2021", "Nine months ended Dec 31, 2021"). Never use generic undated terms if a period is identifiable.
4. ENTITY FIDELITY: Identify the specific legal corporate entity (e.g., "Delhivery Limited"). NEVER output generic placeholders like 'Reporting Entity', 'the Company', or 'Management'.
5. INHERITED CONTEXT: Use the stated units, currencies, section titles, and table captions provided in the envelope to disambiguate rows and columns.
6. EMPTY CHUNKS: If the chunk contains only boilerplate legal disclaimers, headers/footers, or index listings with no meaningful business or financial statements, return empty arrays for all fields.
7. NO EXTRAPOLATION: Never infer or hallucinate facts that are not directly stated in the excerpt.
"""


def is_verbatim_entailed(raw_val: str, content: str) -> bool:
    """Verify that the raw numerical value appears verbatim in the source content."""
    if not raw_val or not raw_val.strip():
        return False
    raw_str = raw_val.strip()
    if raw_str in content:
        return True

    # Strip commas and whitespace
    clean_val = re.sub(r"[\s,]", "", raw_str)
    clean_content = re.sub(r"[\s,]", "", content)
    if clean_val and clean_val in clean_content:
        return True

    # Numeric digits check (handling negative parentheses e.g. (150) vs -150)
    val_digits = re.sub(r"[^\d.]", "", raw_str)
    if len(val_digits) >= 2 and val_digits in clean_content:
        return True

    return False


class ExtractionAgent:
    """Agent responsible for harvesting factual observations from EvidenceWindows."""

    def __init__(self, reasoning_service: ReasoningService):
        self.llm = reasoning_service

    def extract_from_chunk(
        self,
        chunk: Union[EvidenceChunk, EvidenceWindow],
        primary_entity: Optional[str] = None,
        validate: bool = True,
    ) -> ObservationBundle:
        """
        Analyze an EvidenceWindow (or EvidenceChunk) and extract structured factual claims.
        Applies prompt envelope injection, unit inheritance, and post-extraction validation.
        """
        content = chunk.content.strip()
        if len(content) < 20:
            return ObservationBundle()

        if isinstance(chunk, EvidenceWindow):
            window = chunk
        else:
            window = EvidenceWindow.from_chunk(chunk)

        section_display = (
            window.section_title
            if window.section_confidence >= 0.70 and window.section_title
            else "N/A"
        )
        caption_display = window.table_caption or "N/A"
        units_display = f"{window.stated_unit} {window.stated_currency}".strip() or "N/A"
        columns_display = ", ".join(window.column_headers) if window.column_headers else "N/A"

        entity_instruction = ""
        if primary_entity and primary_entity.lower() not in GENERIC_ENTITIES:
            entity_instruction = (
                f"PRIMARY ENTITY: {primary_entity}\n"
                f"Use '{primary_entity}' unless a specific subsidiary or third party is explicitly named.\n"
            )

        if window.chunk_type == "table":
            table_text = window.content
            lines = table_text.splitlines()
            if len(lines) > 15:
                table_text = "\n".join(lines[:15]) + "\n| ... [rows truncated] |"
            if len(table_text) > 1000:
                table_text = table_text[:1000] + "\n... [table truncated]"

            prompt = (
                f"DOCUMENT: {window.document_id}\n"
                f"PAGE: {window.page_number}\n"
                f"SECTION: {section_display}\n"
                f"TABLE CAPTION: {caption_display}\n"
                f"STATED UNITS: {units_display}\n"
                f"COLUMN HEADERS: {columns_display}\n"
                f"{entity_instruction}\n"
                f"CONTENT (TABLE):\n"
                f"-----------------------------------------\n"
                f"{table_text}\n"
                f"-----------------------------------------\n\n"
                f"Extract the top 3-5 core financial metric line items (e.g., Revenue, EBITDA, PAT, Net Profit, Volumes) "
                f"as 'numerical_observations' with their exact period, unit, and currency.\n"
                f"STRICT RULE: Never output generic entities ('Reporting Entity', 'the Company', 'Company', 'Management').\n"
                f"Include any specific notes or qualitative caveats present in the table as 'semantic_observations'."
            )
        else:
            text_content = window.content
            if len(text_content) > 1000:
                text_content = text_content[:1000] + "\n... [text truncated]"

            prompt = (
                f"DOCUMENT: {window.document_id}\n"
                f"PAGE: {window.page_number}\n"
                f"SECTION: {section_display}\n"
                f"TABLE CAPTION: {caption_display}\n"
                f"STATED UNITS: {units_display}\n"
                f"{entity_instruction}\n"
                f"CONTENT (TEXT):\n"
                f"-----------------------------------------\n"
                f"{text_content}\n"
                f"-----------------------------------------\n\n"
                f"Extract explicit financial and operational metrics as 'numerical_observations', "
                f"and key management commentary, accounting policies, or risk factors as 'semantic_observations'.\n"
                f"STRICT RULE: Never output generic entities ('Reporting Entity', 'the Company', 'Company', 'Management')."
            )

        try:
            bundle = self.llm.generate_structured(
                prompt=prompt,
                response_model=ObservationBundle,
                system_prompt=EXTRACTION_SYSTEM_PROMPT,
                max_retries=1,
            )
        except ExtractionParseError as e:
            logger.warning(
                f"Failed to parse observations from chunk {window.chunk_id} on page {window.page_number}: {e}"
            )
            return ObservationBundle()
        except Exception as e:
            logger.error(
                f"Unexpected error during extraction from chunk {window.chunk_id}: {e}"
            )
            return ObservationBundle()

        # Context inheritance: apply stated unit and currency if missing on observation
        for obs in bundle.numerical_observations:
            if not obs.unit and window.stated_unit:
                obs.unit = window.stated_unit
            if not obs.currency and window.stated_currency:
                obs.currency = window.stated_currency

        # Post-extraction quality validation
        if validate:
            valid_numerical: list[NumericalObservation] = []
            for obs in bundle.numerical_observations:
                if self.validate_numerical_observation(obs, window):
                    valid_numerical.append(obs)
                else:
                    logger.debug(
                        f"Filtered invalid numerical observation: entity='{obs.entity}', "
                        f"raw_value='{obs.raw_value}', temporal='{obs.temporal_scope}'"
                    )
            bundle.numerical_observations = valid_numerical

            valid_semantic: list[SemanticObservation] = []
            for sem in bundle.semantic_observations:
                if self.validate_semantic_observation(sem, window):
                    valid_semantic.append(sem)
                else:
                    logger.debug(f"Filtered invalid semantic observation: entity='{sem.entity}'")
            bundle.semantic_observations = valid_semantic

        return bundle

    def validate_numerical_observation(
        self,
        obs: NumericalObservation,
        window: EvidenceWindow,
    ) -> bool:
        """Reject observations with generic entities, non-verbatim numbers, or invalid dates."""
        # 1. Reject generic placeholders
        if obs.entity.strip().lower() in GENERIC_ENTITIES:
            return False

        # 2. Raw value verbatim entailment
        if not is_verbatim_entailed(obs.raw_value, window.content):
            return False

        # 3. Valid non-epoch temporal parsing
        start, end = TemporalNormalizer.normalize(obs.temporal_scope)
        if start == "1970-01-01" and end == "1970-01-01":
            return False

        return True

    def validate_semantic_observation(
        self,
        obs: SemanticObservation,
        window: EvidenceWindow,
    ) -> bool:
        """Reject semantic observations with generic entities."""
        if obs.entity.strip().lower() in GENERIC_ENTITIES:
            return False
        return True
