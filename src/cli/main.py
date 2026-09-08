"""
Command Line Interface for EVIDRA Fact Knowledge Layer.
Built using standard library argparse for zero-dependency execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Optional

# pyrefly: ignore [missing-import]
from src.db.ledger import DocumentRecord, EvidenceLedger
# pyrefly: ignore [missing-import]
from src.observability.trace import RunContext, TraceLogger
# pyrefly: ignore [missing-import]
from src.extraction.pipeline import ExtractionPipeline


def compute_file_hash(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def handle_process(args: argparse.Namespace) -> int:
    """Execute the process command on a PDF file or directory."""
    raw_paths = args.path if isinstance(args.path, list) else [args.path]
    pdf_files: list[Path] = []
    seen = set()

    for raw in raw_paths:
        target_path = Path(raw)
        if not target_path.exists():
            print(f"Warning: Target path '{target_path}' does not exist.", file=sys.stderr)
            continue

        if target_path.is_file():
            if target_path.suffix.lower() == ".pdf":
                resolved = str(target_path.resolve()).lower()
                if resolved not in seen:
                    seen.add(resolved)
                    pdf_files.append(target_path)
            else:
                print(f"Warning: File '{target_path}' is not a PDF.", file=sys.stderr)
        elif target_path.is_dir():
            for child in sorted(target_path.iterdir()):
                if child.is_file() and child.suffix.lower() == ".pdf":
                    resolved = str(child.resolve()).lower()
                    if resolved not in seen:
                        seen.add(resolved)
                        pdf_files.append(child)

    if not pdf_files:
        print("Error: No valid PDF files found to process.", file=sys.stderr)
        return 1

    # Initialize Run Context
    runs_dir = Path(args.out_dir) if args.out_dir else Path("runs")
    ctx = RunContext(runs_root=runs_dir)
    ctx.init_run(input_files=[p.name for p in pdf_files])
    tracer = TraceLogger(ctx.trace_log_path)
    tracer.log_step(
        step_name="document_ingestion",
        agent_name="cli_pipeline",
        input_payload={"pdf_files": [p.name for p in pdf_files]},
        output_payload={"documents_ingested": len(pdf_files)},
        latency_ms=0.0,
    )
    ledger = EvidenceLedger(ctx.db_path)

    # Ingest document records into ledger
    for idx, pdf_path in enumerate(pdf_files, start=1):
        doc_id = f"DOC-{idx:03d}"
        file_hash = compute_file_hash(pdf_path)
        dest_path = ctx.documents_dir / pdf_path.name
        with open(pdf_path, "rb") as src_f, open(dest_path, "wb") as dst_f:
            dst_f.write(src_f.read())

        doc_record = DocumentRecord(
            document_id=doc_id,
            filename=pdf_path.name,
            file_hash=file_hash,
            page_count=1,
        )
        ledger.insert_document(doc_record)

        # Execute D2 Extraction Pipeline
        max_chunks = None if getattr(args, "all_chunks", False) else getattr(args, "max_chunks", 2)
        if getattr(args, "skip_llm", False):
            max_chunks = 0

        pipeline = ExtractionPipeline(
            ledger=ledger,
            tracer=tracer,
            max_llm_chunks=max_chunks,
            skip_verifier=getattr(args, "fast", False),
            evidence_dir=ctx.evidence_dir,
        )
        pipeline.process_document(doc_id, dest_path, defer_reasoning=True)

    # Multi-document fact grouping and adjudication
    # pyrefly: ignore [missing-import]
    from src.verification.pipeline import VerificationPipeline
    # pyrefly: ignore [missing-import]
    from src.decision.engine import FactDecisionEngine
    # pyrefly: ignore [missing-import]
    from src.observability.reports import ReportGenerator

    verif_pipeline = VerificationPipeline(
        ledger=ledger,
        tracer=tracer,
        skip_verifier=getattr(args, "fast", False),
    )
    verif_pipeline.group_candidates()

    decision_engine = FactDecisionEngine(
        ledger=ledger,
        tracer=tracer,
    )
    decision_engine.process_fact_groups()

    # Generate Markdown reports
    report_gen = ReportGenerator(ledger, ctx)
    report_gen.generate_all_reports()

    summary = ledger.get_job_summary()
    ctx.complete_run(summary=summary)

    # Print summary table
    print("\n" + "=" * 60)
    print("  EVIDRA Fact Knowledge Layer - Job Summary")
    print("=" * 60)
    print(f"  Job ID:            {ctx.job_id}")
    print(f"  Run Directory:     {ctx.run_dir}")
    print(f"  Documents Ingested:{len(pdf_files)}")
    print(f"  Evidence Chunks:   {summary['evidence_chunks_count']}")
    print(f"  Observations:      {summary['observations_count']}")
    print(f"  Fact Candidates:   {summary['fact_candidates_count']}")
    print(f"  Fact Groups:       {summary['fact_groups_count']}")
    print(f"  Decisions Made:    {summary['decisions_count']}")
    print("-" * 60)
    print(f"  Corroborated:      {summary['verdicts']['CORROBORATED']}")
    print(f"  Contradictions:    {summary['verdicts']['CONTRADICTION']}")
    print(f"  Reconciled:        {summary['verdicts']['RECONCILED']}")
    print(f"  Unresolved:        {summary['verdicts']['UNRESOLVED']}")
    print("=" * 60 + "\n")

    return 0


def handle_inspect(args: argparse.Namespace) -> int:
    """Execute the inspect command to review decisions for a job."""
    runs_dir = Path(args.runs_dir) if args.runs_dir else Path("runs")
    job_dir = runs_dir / args.job_id
    db_path = job_dir / "ledger.db"

    if not db_path.exists():
        print(f"Error: Ledger database not found for job '{args.job_id}' at '{db_path}'.", file=sys.stderr)
        return 1

    ledger = EvidenceLedger(db_path)
    decisions = ledger.get_decisions(verdict_filter=args.verdict)

    if not decisions:
        filter_str = f" with verdict '{args.verdict}'" if args.verdict else ""
        print(f"No decisions found for job '{args.job_id}'{filter_str}.")
        return 0

    print("\n" + "=" * 75)
    print(f"  Decisions for Job: {args.job_id}")
    print("=" * 75)

    for d in decisions:
        card = ledger.get_decision_card(d['decision_id'])
        print(f"  Decision ID: {d['decision_id']}  |  Verdict: [{d['verdict']}]  |  Strength: {d['decision_strength']}")
        print(f"  Entity:      {d['entity']}  |  Attribute: {d['attribute']}  |  Period: {d['period_id']}")
        print(f"  Reasoning:   {d['reasoning_summary']}")

        if card and card.get("claims"):
            print("  Evaluated Facts:")
            for idx, c in enumerate(card["claims"], start=1):
                doc_cite = f"{c.get('filename', 'doc.pdf')} (p.{c.get('page_number', 1)})"
                print(f"    [{idx}] Value: {c.get('normalized_value')} {c.get('normalized_unit')} {c.get('normalized_currency')} | Source: {doc_cite}")
                if c.get("statement"):
                    print(f"        Statement: {c['statement'][:100]}")

        if card and card.get("hypotheses"):
            print("  Tested Hypotheses:")
            for h in card["hypotheses"]:
                print(f"    - [{h.get('explanation_type')}] {h.get('description')} (likelihood: {h.get('likelihood_score')})")

        if card and card.get("traces"):
            print(f"  Audit Traces: {len(card['traces'])} reasoning steps recorded.")
        print("-" * 75)

    return 0


def handle_report(args: argparse.Namespace) -> int:
    """Execute the report command to print or export generated reports."""
    runs_dir = Path(args.runs_dir) if args.runs_dir else Path("runs")
    job_dir = runs_dir / args.job_id

    if not job_dir.exists():
        print(f"Error: Job directory '{job_dir}' not found.", file=sys.stderr)
        return 1

    if args.format == "json":
        json_report = job_dir / "reports" / "summary.json"
        if json_report.exists():
            with open(json_report, "r", encoding="utf-8") as f:
                print(f.read())
            return 0
        manifest_path = job_dir / "run.json"
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                print(f.read())
            return 0
        else:
            print("Error: Report JSON and run.json not found.", file=sys.stderr)
            return 1
    else:
        report_name = f"{args.type.lower().replace('-', '_')}.md"
        report_path = job_dir / "reports" / report_name
        if report_path.exists():
            with open(report_path, "r", encoding="utf-8") as f:
                print(f.read())
            return 0
        else:
            # Fallback to printing manifest summary
            manifest_path = job_dir / "run.json"
            if manifest_path.exists():
                with open(manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                print(f"# Job Summary: {args.job_id}\n")
                print(f"- Status: {data.get('status')}")
                print(f"- Input Files: {', '.join(data.get('input_files', []))}")
                print(f"- Summary: {data.get('summary')}")
                return 0
            print(f"Error: Report '{report_name}' not found for job '{args.job_id}'.", file=sys.stderr)
            return 1


def handle_replay(args: argparse.Namespace) -> int:
    """Execute the replay command to chronologically inspect decision audit traces."""
    runs_dir = Path(args.runs_dir) if args.runs_dir else Path("runs")
    job_dir = runs_dir / args.job_id

    if not job_dir.exists():
        print(f"Error: Job directory '{job_dir}' not found.", file=sys.stderr)
        return 1

    from src.observability.trace import TraceReplayer

    replayer = TraceReplayer(
        trace_path=job_dir / "traces" / "trace.jsonl",
        db_path=job_dir / "ledger.db",
    )

    timeline = replayer.render_timeline(decision_id=args.decision_id)
    print(timeline)
    return 0


def handle_benchmark(args: argparse.Namespace) -> int:
    """Execute the mandatory evaluation benchmarks and display scorecard."""
    from src.observability.evaluator import EvaluationHarness, run_all_benchmarks

    print("Running EVIDRA mandatory assignment benchmark scenarios...")
    metrics = run_all_benchmarks()

    if getattr(args, "format", "text") == "json":
        print(metrics.model_dump_json(indent=2))
    else:
        scorecard = EvaluationHarness.render_scorecard(metrics)
        print("\n" + scorecard)

    return 0 if metrics.accuracy == 100.0 else 1


def handle_serve(args: argparse.Namespace) -> int:
    """Launch the FastAPI server via uvicorn."""
    try:
        import uvicorn
        print(f"Starting EVIDRA API server on http://{args.host}:{args.port} (Swagger docs at /docs)...")
        uvicorn.run("src.api.server:app", host=args.host, port=args.port, reload=args.reload)
        return 0
    except ImportError:
        print("Error: 'uvicorn' is required to run the server. Install it with 'pip install uvicorn'.", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    """Build and configure the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="evidra",
        description="EVIDRA - Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # process subcommand
    proc_parser = subparsers.add_parser("process", help="Process a PDF file or directory of PDFs")
    proc_parser.add_argument("path", nargs="+", help="Path(s) to PDF file(s) or directories containing PDFs")
    proc_parser.add_argument("--out-dir", default="runs", help="Base directory for job runs (default: runs)")
    proc_parser.add_argument("--max-chunks", type=int, default=2, help="Max candidate chunks for LLM extraction (default: 2)")
    proc_parser.add_argument("--all-chunks", action="store_true", help="Extract all candidate chunks without limit")
    proc_parser.add_argument("--skip-llm", action="store_true", help="Extract layout chunks and tables only, skipping LLM")
    proc_parser.add_argument("--fast", action="store_true", help="Fast mode: bypass secondary LLM verification pass to accelerate multi-document processing")
    proc_parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    # inspect subcommand
    insp_parser = subparsers.add_parser("inspect", help="Inspect decisions and traces for a job run")
    insp_parser.add_argument("job_id", help="Job identifier (e.g. JOB-20260907-XXXXXX)")
    insp_parser.add_argument("--verdict", choices=["CORROBORATED", "CONTRADICTION", "RECONCILED", "UNRESOLVED"], help="Filter by verdict")
    insp_parser.add_argument("--runs-dir", default="runs", help="Base directory for job runs (default: runs)")

    # report subcommand
    rep_parser = subparsers.add_parser("report", help="Display or export job reports")
    rep_parser.add_argument("job_id", help="Job identifier")
    rep_parser.add_argument("--type", default="summary", choices=["summary", "contradictions", "unresolved"], help="Report type")
    rep_parser.add_argument("--format", default="markdown", choices=["markdown", "json"], help="Output format")
    rep_parser.add_argument("--runs-dir", default="runs", help="Base directory for job runs (default: runs)")

    # serve subcommand
    srv_parser = subparsers.add_parser("serve", help="Start the FastAPI server")
    srv_parser.add_argument("--host", default="127.0.0.1", help="Host binding (default: 127.0.0.1)")
    srv_parser.add_argument("--port", type=int, default=8000, help="Port binding (default: 8000)")
    srv_parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    # replay subcommand
    replay_parser = subparsers.add_parser("replay", help="Replay chronological audit traces for a job or decision")
    replay_parser.add_argument("job_id", help="Job identifier")
    replay_parser.add_argument("--decision-id", help="Filter replay by specific decision identifier")
    replay_parser.add_argument("--runs-dir", default="runs", help="Base directory for job runs (default: runs)")

    # benchmark subcommand
    bench_parser = subparsers.add_parser("benchmark", help="Run mandatory evaluation benchmark scenarios")
    bench_parser.add_argument("--format", default="text", choices=["text", "json"], help="Output format (default: text)")

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Main CLI entry point."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "process":
        return handle_process(args)
    elif args.command == "inspect":
        return handle_inspect(args)
    elif args.command == "report":
        return handle_report(args)
    elif args.command == "replay":
        return handle_replay(args)
    elif args.command == "benchmark":
        return handle_benchmark(args)
    elif args.command == "serve":
        return handle_serve(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())