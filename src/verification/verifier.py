from __future__ import annotations

import logging
from typing import Literal, Optional
from pydantic import BaseModel, Field

# pyrefly: ignore [missing-import]
from src.llm.provider import ReasoningService

logger = logging.getLogger(__name__)


class VerificationVerdict(BaseModel):
    """Result of adversarial claim-to-chunk entailment verification."""
    status: Literal["ENTAILED", "HALLUCINATED", "AMBIGUOUS"] = Field(
        description="Verification verdict: ENTAILED if supported, HALLUCINATED if ungrounded, AMBIGUOUS if insufficient context"
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Verification confidence score")
    explanation: str = Field(description="Audit justification citing specific words or explaining absence")


VERIFIER_SYSTEM_PROMPT = """You are an adversarial financial evidence verification auditor in EVIDRA (Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning).

Your sole responsibility is to verify whether a candidate financial CLAIM is directly, explicitly supported by the cited SOURCE DOCUMENT EXCERPT.

VERIFICATION RULES:
1. STRICT GROUNDING: Every number, metric name, entity, currency, and date in the claim must be directly traceable to the excerpt.
2. HALLUCINATION DETECTION: If the claim asserts a figure, company name, or assertion NOT found in the excerpt (or contradicts the excerpt), you MUST return status="HALLUCINATED".
3. TRUTHFUL ENTAILMENT: If the claim accurately reports facts explicitly printed in the excerpt, return status="ENTAILED".
4. INSUFFICIENT CONTEXT: If the excerpt is a fragmented sentence, truncated table header, or lacks context to determine truthfulness, return status="AMBIGUOUS".
5. OUTPUT FORMAT: You must return valid JSON matching the VerificationVerdict schema.
"""


class EvidenceVerifierAgent:
    """Agent evaluating whether extracted claims are faithfully grounded in source chunks."""

    def __init__(self, reasoning_service: ReasoningService):
        self.llm = reasoning_service

    def verify_observation(
        self,
        statement: str,
        chunk_content: str,
    ) -> VerificationVerdict:
        """Adversarially evaluate an observation against its cited source chunk."""
        clean_statement = statement.strip()
        clean_chunk = chunk_content.strip()

        # Fast heuristic check: If chunk is empty or trivially short
        if not clean_chunk or len(clean_chunk) < 15:
            return VerificationVerdict(
                status="AMBIGUOUS",
                confidence=0.5,
                explanation="Source chunk content is empty or trivially short.",
            )

        # Truncate extremely long tables to prompt length
        if len(clean_chunk) > 1500:
            lines = clean_chunk.splitlines()
            clean_chunk = "\n".join(lines[:25]) + "\n[... truncated table rows ...]"

        prompt = (
            f"SOURCE DOCUMENT EXCERPT:\n"
            f"-----------------------------------------\n"
            f"{clean_chunk}\n"
            f"-----------------------------------------\n\n"
            f"CANDIDATE CLAIM TO AUDIT:\n"
            f"\"{clean_statement}\"\n\n"
            f"Does the SOURCE DOCUMENT EXCERPT directly and faithfully support the CANDIDATE CLAIM?"
        )

        try:
            verdict = self.llm.generate_structured(
                prompt=prompt,
                response_model=VerificationVerdict,
                system_prompt=VERIFIER_SYSTEM_PROMPT,
                max_retries=2,
            )
            return verdict
        except Exception as e:
            logger.warning(f"Verification call failed for claim '{clean_statement[:40]}...': {e}")
            # Fallback to AMBIGUOUS on LLM execution error
            return VerificationVerdict(
                status="AMBIGUOUS",
                confidence=0.5,
                explanation=f"Automated verification call encountered an error: {e}",
            )
