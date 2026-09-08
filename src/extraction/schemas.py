from __future__ import annotations

import hashlib
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, field_validator


def _normalize_confidence(v: Any) -> float:
    """Normalize confidence inputs, handling percentage scales (0-100) defensively."""
    try:
        val = float(v)
        if val > 1.0:
            val = val / 100.0
        return max(0.0, min(1.0, val))
    except (ValueError, TypeError):
        return 1.0


class BoundingBox(BaseModel):
    """Normalized spatial bounding box [x0, y0, x1, y1] on a PDF page."""
    x0: float
    y0: float
    x1: float
    y1: float

    def to_list(self) -> list[float]:
        return [self.x0, self.y0, self.x1, self.y1]


class EvidenceChunk(BaseModel):
    """A discrete spatial text block, table, or figure extracted from a document."""
    chunk_id: str = Field(description="Deterministic cryptographic identifier: CHK-{sha256[:8]}")
    document_id: str = Field(description="Parent document identifier")
    page_number: int = Field(description="1-indexed page number where chunk resides")
    chunk_type: Literal["text", "table", "figure"] = Field(description="Structural modality")
    bounding_box: list[float] = Field(description="[x0, y0, x1, y1] page coordinates")
    content: str = Field(description="Raw text or formatted Markdown representation")
    content_hash: str = Field(description="SHA-256 hash of content string")

    @classmethod
    def create(
        cls,
        document_id: str,
        page_number: int,
        chunk_type: Literal["text", "table", "figure"],
        bounding_box: list[float],
        content: str,
    ) -> EvidenceChunk:
        """Deterministically instantiate an EvidenceChunk with cryptographic ID."""
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        raw_key = f"{document_id}:{page_number}:{bounding_box}:{content_hash}"
        chunk_id = f"CHK-{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[:8]}"
        return cls(
            chunk_id=chunk_id,
            document_id=document_id,
            page_number=page_number,
            chunk_type=chunk_type,
            bounding_box=bounding_box,
            content=content,
            content_hash=content_hash,
        )


class NumericalObservation(BaseModel):
    """An explicit financial metric extracted verbatim from text or a table."""
    statement: str = Field(description="Exact statement or row summary containing the claim")
    entity: str = Field(description="Corporate entity, subsidiary, or segment referred to")
    attribute: str = Field(description="Standardized metric name (e.g. Revenue, EBITDA, PAT, Basic EPS, Net Worth)")
    raw_value: str = Field(description="Exact numerical text as written (e.g. 5,000.50, (12.4)%)")
    unit: str = Field(default="", description="Stated unit (e.g. Millions, Crores, Thousands, Percent, Ratio)")
    currency: str = Field(default="", description="Currency symbol or ISO code (e.g. INR, Rs., USD) or empty if non-monetary")
    temporal_scope: str = Field(description="Fiscal period or point-in-time date (e.g. FY22, Q3 FY21, March 31, 2022)")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence score")

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, v: Any) -> float:
        return _normalize_confidence(v)


class SemanticObservation(BaseModel):
    """A qualitative disclosure, accounting policy, risk factor, or management commentary."""
    statement: str = Field(description="Exact sentence or passage extracted from document")
    entity: str = Field(description="Corporate entity or segment discussed")
    attribute: str = Field(description="Category (e.g. Risk Factor, Accounting Policy, Management Commentary, Industry Overview)")
    raw_value: str = Field(description="Qualitative assertion or key summary phrase")
    temporal_scope: str = Field(description="Temporal applicability or reporting period")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence score")

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, v: Any) -> float:
        return _normalize_confidence(v)


class EventObservation(BaseModel):
    """A discrete corporate action, leadership change, restructuring, or legal development."""
    statement: str = Field(description="Exact description of corporate action or event")
    entity: str = Field(description="Corporate entity involved in event")
    attribute: str = Field(description="Event classification (e.g. Acquisition, Restructuring, Board Appointment, Capital Raising)")
    raw_value: str = Field(description="Core event detail or transaction value")
    temporal_scope: str = Field(description="Date or time frame of occurrence (e.g. 2021-12-08, December 2021)")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence score")

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, v: Any) -> float:
        return _normalize_confidence(v)


class ObservationBundle(BaseModel):
    """Container holding all factual observations harvested from an evidence chunk."""
    numerical_observations: list[NumericalObservation] = Field(default_factory=list)
    semantic_observations: list[SemanticObservation] = Field(default_factory=list)
    event_observations: list[EventObservation] = Field(default_factory=list)
