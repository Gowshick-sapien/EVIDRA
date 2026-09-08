"""
Pydantic API request and response models for EVIDRA.
"""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall system health status (OK, DEGRADED)")
    sqlite: str = Field(..., description="SQLite driver status")
    ollama: str = Field(..., description="Ollama daemon status")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")


class JobCreateResponse(BaseModel):
    job_id: str = Field(..., description="Unique job execution identifier")
    status: str = Field("PENDING", description="Job status")
    created_at: str = Field(..., description="Creation timestamp")
    file_count: int = Field(..., description="Number of uploaded files accepted")
    message: str = Field("Job accepted for processing", description="Status message")


class JobStatusResponse(BaseModel):
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Job status (PENDING, PROCESSING, COMPLETED, FAILED)")
    created_at: str = Field(..., description="Job creation timestamp")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    input_files: list[str] = Field(default_factory=list, description="List of ingested filenames")
    summary: dict[str, Any] = Field(default_factory=dict, description="Execution summary statistics")
    errors: list[str] = Field(default_factory=list, description="Error messages if failed")


class DecisionItemResponse(BaseModel):
    decision_id: str
    group_id: str
    verdict: str
    decision_strength: str
    reasoning_summary: str
    entity: str
    attribute: str
    period_id: str
    member_count: int
    created_at: Optional[str] = None


class DecisionListResponse(BaseModel):
    job_id: str
    count: int
    decisions: list[DecisionItemResponse]


class DecisionDetailResponse(BaseModel):
    decision_id: str
    group_id: str
    verdict: str
    decision_strength: str
    reasoning_summary: str
    created_at: Optional[str] = None
    group: dict[str, Any] = Field(default_factory=dict)
    claims: list[dict[str, Any]] = Field(default_factory=list)
    hypotheses: list[dict[str, Any]] = Field(default_factory=list)
    traces: list[dict[str, Any]] = Field(default_factory=list)


class TraceItemResponse(BaseModel):
    trace_id: str
    decision_id: Optional[str] = None
    timestamp: str
    step_name: str
    agent_name: str
    latency_ms: float
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)


class TraceListResponse(BaseModel):
    job_id: str
    decision_id: Optional[str] = None
    count: int
    traces: list[TraceItemResponse]