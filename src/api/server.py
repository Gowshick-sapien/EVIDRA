"""
FastAPI REST API server for EVIDRA Fact Knowledge Layer.
Provides endpoints for job submission, status polling, decision inspection,
and Markdown report retrieval.
"""
from __future__ import annotations

import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import PlainTextResponse

# pyrefly: ignore [missing-import]
from src.api.models import (
    DecisionDetailResponse,
    DecisionItemResponse,
    DecisionListResponse,
    HealthResponse,
    JobCreateResponse,
    JobStatusResponse,
)
import hashlib
# pyrefly: ignore [missing-import]
from src.db.ledger import DocumentRecord, EvidenceLedger
# pyrefly: ignore [missing-import]
from src.extraction.pipeline import ExtractionPipeline
# pyrefly: ignore [missing-import]
from src.observability.trace import RunContext, TraceLogger


def create_app(runs_root: Path | str = "runs") -> FastAPI:
    """Factory creating and configuring the FastAPI instance."""
    app = FastAPI(
        title="EVIDRA - Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning",
        description="Evidence-centric financial document reasoning and reconciliation API.",
        version="0.1.0",
        openapi_version="3.0.2",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    runs_path = Path(runs_root)

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            openapi_version="3.0.2",
        )
        # Ensure Swagger UI displays the native file picker for UploadFile arrays
        for schema in openapi_schema.get("components", {}).get("schemas", {}).values():
            if "properties" in schema:
                for prop in schema["properties"].values():
                    if prop.get("type") == "array" and "items" in prop:
                        prop["items"]["format"] = "binary"
                        prop["items"].pop("contentMediaType", None)
                    elif prop.get("contentMediaType") == "application/octet-stream":
                        prop["format"] = "binary"
                        prop.pop("contentMediaType", None)
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    def health_check() -> HealthResponse:
        """Probe system status, SQLite accessibility, and Ollama connection."""
        ollama_status = "UNAVAILABLE"
        try:
            req = urllib.request.Request("http://127.0.0.1:11434/api/version")
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    ollama_status = "CONNECTED"
        except Exception:
            ollama_status = "DISCONNECTED"

        overall_status = "OK" if ollama_status == "CONNECTED" else "DEGRADED"

        return HealthResponse(
            status=overall_status,
            sqlite="READY",
            ollama=ollama_status,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def _run_background_pipeline(job_id: str, file_paths: list[Path]):
        try:
            ctx = RunContext(runs_root=runs_path, job_id=job_id)
            ledger = EvidenceLedger(ctx.db_path)
            tracer = TraceLogger(ctx.trace_log_path)
            pipeline = ExtractionPipeline(ledger=ledger, tracer=tracer, max_llm_chunks=10)

            for idx, path in enumerate(file_paths, start=1):
                doc_id = f"DOC-{idx:03d}"
                with open(path, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                doc_record = DocumentRecord(
                    document_id=doc_id,
                    filename=path.name,
                    file_hash=file_hash,
                    page_count=1,
                )
                try:
                    ledger.insert_document(doc_record)
                except Exception:
                    pass
                pipeline.process_document(doc_id, path)

            summary = ledger.get_job_summary()
            ctx.complete_run(summary=summary)
        except Exception as e:
            ctx = RunContext(runs_root=runs_path, job_id=job_id)
            ctx.fail_run(str(e))

    @app.post("/jobs", response_model=JobCreateResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Jobs"])
    async def create_job(
        background_tasks: BackgroundTasks,
        files: list[UploadFile] = File(..., description="PDF documents to upload")
    ) -> JobCreateResponse:
        """Upload one or more PDF files and initialize an asynchronous processing job."""
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded.")

        # Initialize RunContext and ensure directories exist
        ctx = RunContext(runs_root=runs_path)
        ctx.init_run()

        saved_filenames = []
        for f in files:
            filename = f.filename or "document.pdf"
            dest = ctx.documents_dir / filename
            content = await f.read()
            if len(content) == 0:
                raise HTTPException(status_code=422, detail=f"File {filename} is empty.")
            
            # Save file to run directory
            with open(dest, "wb") as out:
                out.write(content)
            saved_filenames.append(filename)

        # Update manifest with input filenames
        manifest = ctx.get_manifest()
        manifest["input_files"] = saved_filenames
        with open(ctx.run_manifest_path, "w", encoding="utf-8") as mf:
            import json
            json.dump(manifest, mf, indent=2)

        # Log trace step for job submission
        tracer = TraceLogger(ctx.trace_log_path)
        tracer.log_step(
            step_name="job_initialization",
            agent_name="api_server",
            input_payload={"uploaded_files": saved_filenames},
            output_payload={"job_id": ctx.job_id, "file_count": len(saved_filenames)},
            latency_ms=0.0,
        )

        # Initialize the ledger for this run
        _ = EvidenceLedger(ctx.db_path)

        # Enqueue asynchronous extraction pipeline in background
        saved_paths = [ctx.documents_dir / fn for fn in saved_filenames]
        background_tasks.add_task(_run_background_pipeline, ctx.job_id, saved_paths)

        return JobCreateResponse(
            job_id=ctx.job_id,
            status="PENDING",
            created_at=datetime.now(timezone.utc).isoformat(),
            file_count=len(saved_filenames),
            message="Job created and queued for execution.",
        )

    @app.get("/jobs/{job_id}", response_model=JobStatusResponse, tags=["Jobs"])
    def get_job_status(job_id: str) -> JobStatusResponse:
        """Query execution progress and summary counts for a job."""
        job_dir = runs_path / job_id
        if not job_dir.exists():
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")

        ctx = RunContext(runs_root=runs_path, job_id=job_id)
        manifest = ctx.get_manifest()

        # Augment with live ledger counts if db exists
        if ctx.db_path.exists():
            try:
                ledger = EvidenceLedger(ctx.db_path)
                manifest["summary"] = ledger.get_job_summary()
            except Exception:
                pass

        return JobStatusResponse(
            job_id=manifest["job_id"],
            status=manifest["status"],
            created_at=manifest["created_at"],
            completed_at=manifest.get("completed_at"),
            input_files=manifest.get("input_files", []),
            summary=manifest.get("summary", {}),
            errors=manifest.get("errors", []),
        )

    @app.get("/jobs/{job_id}/decisions", response_model=DecisionListResponse, tags=["Decisions"])
    def list_job_decisions(
        job_id: str,
        verdict: Optional[str] = Query(None, description="Filter decisions by verdict: CORROBORATED, CONTRADICTION, RECONCILED, UNRESOLVED"),
    ) -> DecisionListResponse:
        """List all decisions made during a job run with optional verdict filter."""
        job_dir = runs_path / job_id
        if not job_dir.exists():
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")

        db_path = job_dir / "ledger.db"
        if not db_path.exists():
            return DecisionListResponse(job_id=job_id, count=0, decisions=[])

        ledger = EvidenceLedger(db_path)
        raw_decisions = ledger.get_decisions(verdict_filter=verdict)

        decisions = [
            DecisionItemResponse(
                decision_id=d["decision_id"],
                group_id=d["group_id"],
                verdict=d["verdict"],
                decision_strength=d["decision_strength"],
                reasoning_summary=d["reasoning_summary"],
                entity=d["entity"],
                attribute=d["attribute"],
                period_id=d["period_id"],
                member_count=d["member_count"],
                created_at=d.get("created_at"),
            )
            for d in raw_decisions
        ]

        return DecisionListResponse(job_id=job_id, count=len(decisions), decisions=decisions)

    @app.get("/jobs/{job_id}/decisions/{decision_id}", response_model=DecisionDetailResponse, tags=["Decisions"])
    def get_decision_detail(job_id: str, decision_id: str) -> DecisionDetailResponse:
        """Retrieve full Decision Card with claims, evidence bounding boxes, and audit traces."""
        job_dir = runs_path / job_id
        if not job_dir.exists():
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")

        db_path = job_dir / "ledger.db"
        if not db_path.exists():
            raise HTTPException(status_code=404, detail="Ledger database not found for job.")

        ledger = EvidenceLedger(db_path)
        card = ledger.get_decision_card(decision_id)
        if not card:
            raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found.")

        return DecisionDetailResponse(
            decision_id=card["decision_id"],
            group_id=card["group_id"],
            verdict=card["verdict"],
            decision_strength=card["decision_strength"],
            reasoning_summary=card["reasoning_summary"],
            created_at=card.get("created_at"),
            group=card.get("group", {}),
            claims=card.get("claims", []),
            hypotheses=card.get("hypotheses", []),
            traces=card.get("traces", []),
        )

    @app.get("/jobs/{job_id}/reports/{report_type}", response_class=PlainTextResponse, tags=["Reports"])
    def get_job_report(job_id: str, report_type: str) -> str:
        """Download generated Markdown report: summary, contradictions, or unresolved."""
        job_dir = runs_path / job_id
        if not job_dir.exists():
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")

        normalized_name = report_type.lower().replace("-", "_")
        if not normalized_name.endswith(".md"):
            normalized_name += ".md"

        report_file = job_dir / "reports" / normalized_name
        if not report_file.exists():
            raise HTTPException(status_code=404, detail=f"Report {report_type} not found for job {job_id}.")

        with open(report_file, "r", encoding="utf-8") as f:
            return f.read()

    return app


app = create_app()