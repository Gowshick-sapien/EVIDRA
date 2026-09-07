# Fact Knowledge Layer

Welcome to the Fact Knowledge Layer prototype. This system is designed to solve a fundamental problem in information extraction and epistemic reasoning: **How do we reliably determine when two documents agree, disagree, or can be logically reconciled?**

Rather than relying on opaque AI to simply output "answers," this system builds an auditable, evidence-centric ledger. It treats Large Language Models (LLMs) not as infallible oracles, but as specialized reasoning workers within a deterministic, rule-based workflow.

## The Core Philosophy

The Fact Knowledge Layer operates on five foundational principles:

1. **Evidence Before Fact:** No claim enters the system without a verifiable link back to its exact source document, page, and bounding box.
2. **Observation != Fact != Decision:** The system strictly separates what a document *states* from what the system *decides* is true.
3. **Context Before Contradiction:** If Document A says "Revenue is 100" and Document B says "Revenue is 120", they do not automatically contradict. The system first investigates differences in time periods, organizational scopes, currencies, and definitions.
4. **Challenge Your Own Reasoning:** Every time the system proposes a reconciliation (an explanation for why both documents could be right), an adversarial "skeptic" agent attempts to falsify that explanation using the original evidence.
5. **Know When You Don't Know:** When evidence is insufficient to confidently reconcile a discrepancy, the system explicitly outputs an `UNRESOLVED` state rather than guessing.

## How It Works

The system operates across four layers:

* **Layer 1: Document Ingestion:** PDFs are processed to extract text and tables with precise coordinates.
* **Layer 2: Fact Construction:** Claims are extracted and, crucially, run through an independent *Evidence Verifier* to ensure they are strictly supported by the source text.
* **Layer 3: Fact Decision Engine:** A multi-agent debate determines if facts corroborate, contradict, or can be reconciled based on their contextual dimensions (e.g., temporal or scope differences).
* **Layer 4: Observability:** Every decision is recorded with a full, reproducible audit trace.

## Inspecting the Results

This project is built for transparency. While it processes complex documents, the output is designed for human review:

* **Executive Summaries (Markdown):** High-level reports outlining the major findings, corroborated facts, and identified contradictions.
* **Decision Traces (JSON/JSONL):** Complete, step-by-step audit logs showing exactly how a decision was reached, including the hypotheses generated, the validations run, and the adversarial challenges overcome.
* **Evidence Ledger (SQLite):** A fully relational database tracking the provenance of every data point from the raw PDF text up to the final verdict.

## Running the System

To submit documents and view the reasoning process:
1. Ensure the system is running locally (this prototype operates entirely locally to ensure data privacy and cost control).
2. Submit a batch of PDF documents via the command-line interface or the interactive API endpoint.
3. Review the generated `runs/` directory, which will contain the fully synthesized reports and the complete evidence ledger for the processing job.
