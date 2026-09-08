from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# pyrefly: ignore [missing-import]
from src.db.ledger import EvidenceLedger
# pyrefly: ignore [missing-import]
from src.observability.trace import RunContext


class ReportGenerator:
    """Generates structured Markdown reports for an EVIDRA job run."""

    def __init__(self, ledger: EvidenceLedger, run_context: RunContext):
        self.ledger = ledger
        self.ctx = run_context
        self.reports_dir = run_context.reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_all_reports(self) -> dict[str, Path]:
        """Generate summary.md, contradictions.md, and unresolved.md."""
        return {
            "summary": self.generate_summary_report(),
            "contradictions": self.generate_contradictions_report(),
            "unresolved": self.generate_unresolved_report(),
        }

    def generate_summary_report(self) -> Path:
        """Generate executive summary.md report."""
        summary = self.ledger.get_job_summary()
        documents = self.ledger.get_documents()
        decisions = self.ledger.get_decisions()
        manifest = self.ctx.get_manifest()

        lines: list[str] = [
            "# EVIDRA Executive Summary Report",
            "",
            f"- **Job ID:** `{self.ctx.job_id}`",
            f"- **Created At:** `{manifest.get('created_at', 'N/A')}`",
            f"- **Completed At:** `{datetime.now(timezone.utc).isoformat()}`",
            f"- **Status:** `{manifest.get('status', 'COMPLETED')}`",
            "",
            "## 1. Ingested Documents",
            "",
            "| Document ID | Filename | Pages | SHA-256 Hash |",
            "| :--- | :--- | :--- | :--- |",
        ]

        for doc in documents:
            h_short = doc.get("file_hash", "")[:12] + "..." if doc.get("file_hash") else "N/A"
            lines.append(f"| {doc.get('document_id')} | {doc.get('filename')} | {doc.get('page_count')} | `{h_short}` |")

        lines.extend([
            "",
            "## 2. Pipeline Metrics",
            "",
            "| Metric | Count | Description |",
            "| :--- | :--- | :--- |",
            f"| Documents Processed | {summary.get('documents_count', 0)} | Total PDF source documents |",
            f"| Evidence Chunks | {summary.get('evidence_chunks_count', 0)} | Discrete text and table segments preserved with bounding boxes |",
            f"| Raw Observations | {summary.get('observations_count', 0)} | Extracted factual statements and metric claims |",
            f"| Fact Candidates | {summary.get('fact_candidates_count', 0)} | Deterministically normalized values, units, currencies, and dates |",
            f"| Fact Groups | {summary.get('fact_groups_count', 0)} | Disputed metric clusters grouped by entity, attribute, and period |",
            f"| Decisions Evaluated | {summary.get('decisions_count', 0)} | Epistemic adjudications performed by the decision engine |",
            "",
            "## 3. Verdict Distribution",
            "",
            "| Verdict | Count | Description |",
            "| :--- | :--- | :--- |",
            f"| CORROBORATED | {summary['verdicts'].get('CORROBORATED', 0)} | Claims independently validated across multiple sources or coherent singular facts |",
            f"| CONTRADICTION | {summary['verdicts'].get('CONTRADICTION', 0)} | Direct numerical or factual conflicts that could not be reconciled |",
            f"| RECONCILED | {summary['verdicts'].get('RECONCILED', 0)} | Apparent discrepancies explained by timing, restatement, or accounting scope |",
            f"| UNRESOLVED | {summary['verdicts'].get('UNRESOLVED', 0)} | Claims with insufficient evidence or ambiguous provenance |",
            "",
            "## 4. Evaluated Decisions Summary",
            "",
        ])

        if not decisions:
            lines.append("No decisions evaluated for this job run.")
        else:
            lines.extend([
                "| Decision ID | Entity | Metric / Attribute | Period | Verdict | Strength |",
                "| :--- | :--- | :--- | :--- | :--- | :--- |",
            ])
            for d in decisions:
                lines.append(
                    f"| `{d['decision_id']}` | {d.get('entity', 'N/A')} | {d.get('attribute', 'N/A')} | {d.get('period_id', 'N/A')} | **{d.get('verdict')}** | {d.get('decision_strength')} |"
                )

        lines.append("")
        content = "\n".join(lines)
        report_path = self.reports_dir / "summary.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        return report_path

    def generate_contradictions_report(self) -> Path:
        """Generate contradictions.md report detailing genuine conflicts and reconciliations."""
        all_decisions = self.ledger.get_decisions()
        conflict_decisions = [
            d for d in all_decisions if d.get("verdict") in ("CONTRADICTION", "RECONCILED")
        ]

        lines: list[str] = [
            "# EVIDRA Contradictions and Reconciliations Audit Report",
            "",
            f"- **Job ID:** `{self.ctx.job_id}`",
            f"- **Total Conflicts Detected:** {len(conflict_decisions)}",
            "",
        ]

        if not conflict_decisions:
            lines.extend([
                "## Status",
                "",
                "No genuine contradictions or discrepancies were identified among the evaluated candidate facts.",
                "All multi-source observations demonstrated arithmetic coherence within tolerance.",
                "",
            ])
        else:
            lines.extend([
                "## Detected Discrepancies and Adjudications",
                "",
            ])

            for idx, d in enumerate(conflict_decisions, start=1):
                card = self.ledger.get_decision_card(d["decision_id"]) or d
                entity = d.get("entity", "Reporting Entity")
                attribute = d.get("attribute", "Metric")
                period_id = d.get("period_id", "Undated")
                verdict = d.get("verdict", "UNKNOWN")
                strength = d.get("decision_strength", "N/A")
                reasoning = d.get("reasoning_summary", "No reasoning summary provided.")

                lines.extend([
                    f"### Case {idx}: {entity} - {attribute} ({period_id})",
                    "",
                    f"- **Decision ID:** `{d['decision_id']}`",
                    f"- **Verdict:** `{verdict}`",
                    f"- **Decision Strength:** `{strength}`",
                    f"- **Reasoning:** {reasoning}",
                    "",
                    "#### Competing Fact Claims",
                    "",
                    "| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency |",
                    "| :--- | :--- | :--- | :--- | :--- | :--- |",
                ])

                claims = card.get("claims", [])
                for c_idx, claim in enumerate(claims, start=1):
                    doc_name = claim.get("filename", "Unknown Document")
                    page_num = claim.get("page_number", 1)
                    stated = claim.get("raw_value", "N/A")
                    norm_val = claim.get("normalized_value", "N/A")
                    unit = f"{claim.get('normalized_unit', '')} {claim.get('normalized_currency', '')}".strip()
                    lines.append(
                        f"| {c_idx} | {doc_name} | Page {page_num} | `{stated}` | `{norm_val}` | {unit} |"
                    )

                hypotheses = card.get("hypotheses", [])
                if hypotheses:
                    lines.extend([
                        "",
                        "#### Hypotheses Evaluated",
                        "",
                        "| Class | Description | Likelihood | Status |",
                        "| :--- | :--- | :--- | :--- |",
                    ])
                    for h in hypotheses:
                        h_type = h.get("explanation_type", "Hypothesis")
                        desc = h.get("description", "N/A")
                        score = f"{h.get('likelihood_score', 0.0):.2f}"
                        validators = h.get("validators", [])
                        status = validators[0].get("outcome", "EVALUATED") if validators else "EVALUATED"
                        lines.append(f"| {h_type} | {desc} | {score} | {status} |")

                lines.extend(["", "---", ""])

        content = "\n".join(lines)
        report_path = self.reports_dir / "contradictions.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        return report_path

    def generate_unresolved_report(self) -> Path:
        """Generate unresolved.md report detailing facts with insufficient evidence."""
        all_decisions = self.ledger.get_decisions()
        unresolved_decisions = [
            d for d in all_decisions if d.get("verdict") == "UNRESOLVED"
        ]

        lines: list[str] = [
            "# EVIDRA Unresolved Fact Candidates Report",
            "",
            f"- **Job ID:** `{self.ctx.job_id}`",
            f"- **Total Unresolved Decisions:** {len(unresolved_decisions)}",
            "",
        ]

        if not unresolved_decisions:
            lines.extend([
                "## Status",
                "",
                "No unresolved fact groups were identified in this run.",
                "All candidate fact clusters were successfully corroborated, reconciled, or flagged as contradiction.",
                "",
            ])
        else:
            lines.extend([
                "## Unresolved Items and Recommendations",
                "",
            ])

            for idx, d in enumerate(unresolved_decisions, start=1):
                card = self.ledger.get_decision_card(d["decision_id"]) or d
                entity = d.get("entity", "Reporting Entity")
                attribute = d.get("attribute", "Metric")
                period_id = d.get("period_id", "Undated")
                strength = d.get("decision_strength", "INSUFFICIENT")
                reasoning = d.get("reasoning_summary", "Insufficient evidence for conclusive adjudication.")

                lines.extend([
                    f"### Item {idx}: {entity} - {attribute} ({period_id})",
                    "",
                    f"- **Decision ID:** `{d['decision_id']}`",
                    f"- **Adjudication Strength:** `{strength}`",
                    f"- **Reasoning:** {reasoning}",
                    "",
                    "#### Evaluated Claims",
                    "",
                    "| # | Source Document | Page | Stated Value | Normalized Value | Provenance |",
                    "| :--- | :--- | :--- | :--- | :--- | :--- |",
                ])

                claims = card.get("claims", [])
                for c_idx, claim in enumerate(claims, start=1):
                    doc_name = claim.get("filename", "Unknown Document")
                    page_num = claim.get("page_number", 1)
                    raw_val = claim.get("raw_value", "N/A")
                    norm_val = claim.get("normalized_value", "N/A")
                    prov = claim.get("provenance_status", "ENTAILED")
                    lines.append(f"| {c_idx} | {doc_name} | Page {page_num} | `{raw_val}` | `{norm_val}` | {prov} |")

                lines.extend([
                    "",
                    "#### Analyst Recommendations",
                    "",
                    "- Obtain supplementary statutory filings (e.g. audited annual balance sheet notes or restatement disclosures).",
                    "- Verify whether accounting policy definitions or consolidation perimeters changed across comparative periods.",
                    "- Inspect raw table footnotes or schedule references for unparsed caveats.",
                    "",
                    "---",
                    "",
                ])

        content = "\n".join(lines)
        report_path = self.reports_dir / "unresolved.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        return report_path
