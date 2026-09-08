"""
Evidence Ledger persistence layer for EVIDRA.
Provides a thread-safe SQLite-backed system of record for all evidence,
observations, fact candidates, hypotheses, decisions, and audit traces.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Generator, Optional


@dataclass
class DocumentRecord:
    document_id: str
    filename: str
    file_hash: str
    page_count: int
    created_at: Optional[str] = None


@dataclass
class EvidenceChunkRecord:
    chunk_id: str
    document_id: str
    page_number: int
    chunk_type: str  # text, table, figure
    bounding_box: list[float] | tuple[float, float, float, float]
    content: str
    content_hash: str
    created_at: Optional[str] = None


@dataclass
class EvidenceWindowRecord:
    window_id: str
    chunk_id: str
    document_id: str
    page_number: int
    section_title: str = ""
    section_confidence: float = 0.0
    table_caption: str = ""
    stated_unit: str = ""
    stated_currency: str = ""
    column_headers: str = "[]"
    row_context: str = ""
    page_header: str = ""
    footnotes: str = "[]"
    created_at: Optional[str] = None


@dataclass
class ObservationRecord:
    observation_id: str
    chunk_id: str
    document_id: str
    statement: str
    entity: str
    attribute: str
    raw_value: str
    observation_type: str  # numerical, semantic, event
    temporal_scope: str
    provenance_status: str  # ENTAILED, HALLUCINATED, AMBIGUOUS
    confidence: float
    created_at: Optional[str] = None


@dataclass
class FactCandidateRecord:
    fact_id: str
    observation_id: str
    normalized_value: str
    normalized_unit: str
    normalized_currency: str
    period_start: str  # ISO YYYY-MM-DD
    period_end: str    # ISO YYYY-MM-DD
    created_at: Optional[str] = None


@dataclass
class FactGroupRecord:
    group_id: str
    entity: str
    attribute: str
    period_id: str
    member_count: int = 0
    created_at: Optional[str] = None


@dataclass
class HypothesisRecord:
    hypothesis_id: str
    group_id: str
    explanation_type: str
    description: str
    likelihood_score: float
    created_at: Optional[str] = None


@dataclass
class ValidatorResultRecord:
    result_id: str
    hypothesis_id: str
    validator_type: str
    outcome: str  # SUPPORTED, REFUTED, INCONCLUSIVE
    details_json: str
    created_at: Optional[str] = None


@dataclass
class DecisionRecord:
    decision_id: str
    group_id: str
    verdict: str  # CORROBORATED, CONTRADICTION, RECONCILED, UNRESOLVED
    decision_strength: str  # HIGH, MEDIUM, LOW, INSUFFICIENT
    reasoning_summary: str
    created_at: Optional[str] = None


@dataclass
class DecisionTraceRecord:
    trace_id: str
    decision_id: str
    step_name: str
    agent_name: str
    input_json: str
    output_json: str
    execution_time_ms: float
    created_at: Optional[str] = None


class EvidenceLedger:
    """SQLite-backed relational repository for the Fact Knowledge Layer."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_schema()

    def get_connection(self) -> sqlite3.Connection:
        """Create a configured SQLite connection with foreign keys and WAL mode."""
        conn = sqlite3.connect(str(self.db_path), timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        return conn

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager managing atomic transactional boundaries."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_schema(self) -> None:
        """Initialize the database schema if tables do not exist."""
        schema_file = Path(__file__).parent / "schema.sql"
        if schema_file.exists():
            with open(schema_file, "r", encoding="utf-8") as f:
                ddl = f.read()
            with self.transaction() as conn:
                conn.executescript(ddl)
        else:
            raise FileNotFoundError(f"Schema file not found at {schema_file}")

    # =========================================================================
    # Insert Operations
    # =========================================================================

    def insert_document(self, doc: DocumentRecord) -> str:
        """Insert a document record."""
        query = """
            INSERT INTO documents (document_id, filename, file_hash, page_count)
            VALUES (?, ?, ?, ?)
        """
        with self.transaction() as conn:
            conn.execute(query, (doc.document_id, doc.filename, doc.file_hash, doc.page_count))
        return doc.document_id

    def insert_evidence_chunks(self, chunks: list[EvidenceChunkRecord]) -> int:
        """Bulk insert evidence chunk records."""
        if not chunks:
            return 0
        query = """
            INSERT INTO evidence_chunks (chunk_id, document_id, page_number, chunk_type, bounding_box, content, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        rows = [
            (
                c.chunk_id,
                c.document_id,
                c.page_number,
                c.chunk_type,
                json.dumps(list(c.bounding_box)),
                c.content,
                c.content_hash,
            )
            for c in chunks
        ]
        with self.transaction() as conn:
            conn.executemany(query, rows)
        return len(chunks)

    def insert_evidence_windows(self, windows: list[EvidenceWindowRecord]) -> int:
        """Bulk insert or replace evidence window records."""
        if not windows:
            return 0
        query = """
            INSERT INTO evidence_windows (
                window_id, chunk_id, document_id, page_number,
                section_title, section_confidence, table_caption,
                stated_unit, stated_currency, column_headers,
                row_context, page_header, footnotes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(chunk_id) DO UPDATE SET
                section_title=excluded.section_title,
                section_confidence=excluded.section_confidence,
                table_caption=excluded.table_caption,
                stated_unit=excluded.stated_unit,
                stated_currency=excluded.stated_currency,
                column_headers=excluded.column_headers,
                row_context=excluded.row_context,
                page_header=excluded.page_header,
                footnotes=excluded.footnotes
        """
        rows = [
            (
                w.window_id,
                w.chunk_id,
                w.document_id,
                w.page_number,
                w.section_title,
                w.section_confidence,
                w.table_caption,
                w.stated_unit,
                w.stated_currency,
                w.column_headers if isinstance(w.column_headers, str) else json.dumps(w.column_headers),
                w.row_context,
                w.page_header,
                w.footnotes if isinstance(w.footnotes, str) else json.dumps(w.footnotes),
            )
            for w in windows
        ]
        with self.transaction() as conn:
            conn.executemany(query, rows)
        return len(windows)

    def get_evidence_window(self, chunk_id: str) -> Optional[EvidenceWindowRecord]:
        """Retrieve a specific EvidenceWindowRecord by chunk_id."""
        query = "SELECT * FROM evidence_windows WHERE chunk_id = ?"
        with self.transaction() as conn:
            row = conn.execute(query, (chunk_id,)).fetchone()
            if not row:
                return None
            return EvidenceWindowRecord(
                window_id=row["window_id"],
                chunk_id=row["chunk_id"],
                document_id=row["document_id"],
                page_number=row["page_number"],
                section_title=row["section_title"] or "",
                section_confidence=float(row["section_confidence"] or 0.0),
                table_caption=row["table_caption"] or "",
                stated_unit=row["stated_unit"] or "",
                stated_currency=row["stated_currency"] or "",
                column_headers=row["column_headers"] or "[]",
                row_context=row["row_context"] or "",
                page_header=row["page_header"] or "",
                footnotes=row["footnotes"] or "[]",
                created_at=row["created_at"],
            )

    def get_windows_for_document(self, document_id: str) -> list[EvidenceWindowRecord]:
        """Retrieve all evidence windows for a given document."""
        query = "SELECT * FROM evidence_windows WHERE document_id = ? ORDER BY page_number ASC"
        with self.transaction() as conn:
            rows = conn.execute(query, (document_id,)).fetchall()
            return [
                EvidenceWindowRecord(
                    window_id=r["window_id"],
                    chunk_id=r["chunk_id"],
                    document_id=r["document_id"],
                    page_number=r["page_number"],
                    section_title=r["section_title"] or "",
                    section_confidence=float(r["section_confidence"] or 0.0),
                    table_caption=r["table_caption"] or "",
                    stated_unit=r["stated_unit"] or "",
                    stated_currency=r["stated_currency"] or "",
                    column_headers=r["column_headers"] or "[]",
                    row_context=r["row_context"] or "",
                    page_header=r["page_header"] or "",
                    footnotes=r["footnotes"] or "[]",
                    created_at=r["created_at"],
                )
                for r in rows
            ]

    def insert_observations(self, observations: list[ObservationRecord]) -> int:
        """Bulk insert observation records."""
        if not observations:
            return 0
        query = """
            INSERT INTO observations (
                observation_id, chunk_id, document_id, statement, entity, attribute,
                raw_value, observation_type, temporal_scope, provenance_status, confidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        rows = [
            (
                o.observation_id,
                o.chunk_id,
                o.document_id,
                o.statement,
                o.entity,
                o.attribute,
                o.raw_value,
                o.observation_type,
                o.temporal_scope,
                o.provenance_status,
                o.confidence,
            )
            for o in observations
        ]
        with self.transaction() as conn:
            conn.executemany(query, rows)
        return len(observations)

    def get_observations_for_document(self, document_id: str) -> list[ObservationRecord]:
        """Retrieve all observations extracted for a given document."""
        query = "SELECT * FROM observations WHERE document_id = ? ORDER BY created_at ASC"
        with self.transaction() as conn:
            rows = conn.execute(query, (document_id,)).fetchall()
            return [
                ObservationRecord(
                    observation_id=r["observation_id"],
                    chunk_id=r["chunk_id"],
                    document_id=r["document_id"],
                    statement=r["statement"],
                    entity=r["entity"],
                    attribute=r["attribute"],
                    raw_value=r["raw_value"],
                    observation_type=r["observation_type"],
                    temporal_scope=r["temporal_scope"],
                    provenance_status=r["provenance_status"],
                    confidence=float(r["confidence"] or 1.0),
                    created_at=r["created_at"],
                )
                for r in rows
            ]

    def insert_fact_candidates(self, facts: list[FactCandidateRecord]) -> int:
        """Bulk insert normalized fact candidate records."""
        if not facts:
            return 0
        query = """
            INSERT INTO fact_candidates (
                fact_id, observation_id, normalized_value, normalized_unit,
                normalized_currency, period_start, period_end
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        rows = [
            (
                f.fact_id,
                f.observation_id,
                f.normalized_value,
                f.normalized_unit,
                f.normalized_currency,
                f.period_start,
                f.period_end,
            )
            for f in facts
        ]
        with self.transaction() as conn:
            conn.executemany(query, rows)
        return len(facts)

    def create_fact_group(
        self,
        entity: str,
        attribute: str,
        period_id: str,
        fact_ids: list[str],
        group_id: Optional[str] = None,
    ) -> str:
        """Create a fact group and associate its member fact candidates."""
        gid = group_id or f"GRP-{uuid.uuid4().hex[:8]}"
        group_query = """
            INSERT INTO fact_groups (group_id, entity, attribute, period_id, member_count)
            VALUES (?, ?, ?, ?, ?)
        """
        member_query = """
            INSERT INTO group_members (group_id, fact_id)
            VALUES (?, ?)
        """
        with self.transaction() as conn:
            conn.execute(group_query, (gid, entity, attribute, period_id, len(fact_ids)))
            for fid in fact_ids:
                conn.execute(member_query, (gid, fid))
        return gid

    def insert_hypothesis(self, hyp: HypothesisRecord) -> str:
        """Insert a reasoning hypothesis."""
        query = """
            INSERT INTO hypotheses (hypothesis_id, group_id, explanation_type, description, likelihood_score)
            VALUES (?, ?, ?, ?, ?)
        """
        with self.transaction() as conn:
            conn.execute(query, (hyp.hypothesis_id, hyp.group_id, hyp.explanation_type, hyp.description, hyp.likelihood_score))
        return hyp.hypothesis_id

    def insert_validator_result(self, res: ValidatorResultRecord) -> str:
        """Insert specialist validator outcome."""
        query = """
            INSERT INTO validator_results (result_id, hypothesis_id, validator_type, outcome, details_json)
            VALUES (?, ?, ?, ?, ?)
        """
        with self.transaction() as conn:
            conn.execute(query, (res.result_id, res.hypothesis_id, res.validator_type, res.outcome, res.details_json))
        return res.result_id

    def record_decision(self, decision: DecisionRecord) -> str:
        """Record final epistemic decision."""
        query = """
            INSERT INTO decisions (decision_id, group_id, verdict, decision_strength, reasoning_summary)
            VALUES (?, ?, ?, ?, ?)
        """
        with self.transaction() as conn:
            conn.execute(query, (decision.decision_id, decision.group_id, decision.verdict, decision.decision_strength, decision.reasoning_summary))
        return decision.decision_id

    def append_decision_trace(self, trace: DecisionTraceRecord) -> str:
        """Append an audit trace step for a decision."""
        query = """
            INSERT INTO decision_traces (trace_id, decision_id, step_name, agent_name, input_json, output_json, execution_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self.transaction() as conn:
            conn.execute(query, (trace.trace_id, trace.decision_id, trace.step_name, trace.agent_name, trace.input_json, trace.output_json, trace.execution_time_ms))
        return trace.trace_id

    # =========================================================================
    # Query & Retrieval Operations
    # =========================================================================

    def get_document(self, document_id: str) -> Optional[dict[str, Any]]:
        """Retrieve document metadata by document_id."""
        with self.transaction() as conn:
            row = conn.execute("SELECT * FROM documents WHERE document_id = ?", (document_id,)).fetchone()
            return dict(row) if row else None

    def get_documents(self) -> list[dict[str, Any]]:
        """List all ingested documents."""
        with self.transaction() as conn:
            rows = conn.execute("SELECT * FROM documents ORDER BY created_at ASC").fetchall()
            return [dict(r) for r in rows]

    def get_evidence_chunks(self, document_id: str) -> list[dict[str, Any]]:
        """Retrieve evidence chunks for a document."""
        with self.transaction() as conn:
            rows = conn.execute("SELECT * FROM evidence_chunks WHERE document_id = ? ORDER BY page_number ASC", (document_id,)).fetchall()
            res = []
            for r in rows:
                d = dict(r)
                d["bounding_box"] = json.loads(d["bounding_box"])
                res.append(d)
            return res

    def get_decisions(self, verdict_filter: Optional[str] = None) -> list[dict[str, Any]]:
        """List decisions with optional verdict filtering."""
        query = """
            SELECT d.decision_id, d.group_id, d.verdict, d.decision_strength, d.reasoning_summary,
                   g.entity, g.attribute, g.period_id, g.member_count, d.created_at
            FROM decisions d
            JOIN fact_groups g ON d.group_id = g.group_id
        """
        params: list[Any] = []
        if verdict_filter:
            query += " WHERE d.verdict = ?"
            params.append(verdict_filter.upper())
        query += " ORDER BY d.created_at DESC"
        with self.transaction() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_decision_card(self, decision_id: str) -> Optional[dict[str, Any]]:
        """Retrieve a complete Decision Card including claims, provenance, hypotheses, and traces."""
        with self.transaction() as conn:
            d_row = conn.execute("SELECT * FROM decisions WHERE decision_id = ?", (decision_id,)).fetchone()
            if not d_row:
                return None
            decision = dict(d_row)

            # Fact Group
            g_row = conn.execute("SELECT * FROM fact_groups WHERE group_id = ?", (decision["group_id"],)).fetchone()
            decision["group"] = dict(g_row) if g_row else {}

            # Member Fact Candidates with Observations and Evidence Chunks
            claims_query = """
                SELECT f.fact_id, f.normalized_value, f.normalized_unit, f.normalized_currency,
                       f.period_start, f.period_end,
                       o.observation_id, o.statement, o.raw_value, o.observation_type, o.temporal_scope,
                       o.provenance_status, o.confidence,
                       c.chunk_id, c.document_id, c.page_number, c.chunk_type, c.bounding_box, c.content,
                       d.filename
                FROM group_members gm
                JOIN fact_candidates f ON gm.fact_id = f.fact_id
                JOIN observations o ON f.observation_id = o.observation_id
                JOIN evidence_chunks c ON o.chunk_id = c.chunk_id
                JOIN documents d ON c.document_id = d.document_id
                WHERE gm.group_id = ?
            """
            c_rows = conn.execute(claims_query, (decision["group_id"],)).fetchall()
            claims = []
            for cr in c_rows:
                cd = dict(cr)
                cd["bounding_box"] = json.loads(cd["bounding_box"])
                claims.append(cd)
            decision["claims"] = claims

            # Hypotheses & Validator Results
            h_rows = conn.execute("SELECT * FROM hypotheses WHERE group_id = ?", (decision["group_id"],)).fetchall()
            hypotheses = []
            for hr in h_rows:
                hd = dict(hr)
                v_rows = conn.execute("SELECT * FROM validator_results WHERE hypothesis_id = ?", (hd["hypothesis_id"],)).fetchall()
                hd["validators"] = [dict(vr) for vr in v_rows]
                hypotheses.append(hd)
            decision["hypotheses"] = hypotheses

            # Traces
            t_rows = conn.execute("SELECT * FROM decision_traces WHERE decision_id = ? ORDER BY created_at ASC", (decision_id,)).fetchall()
            decision["traces"] = [dict(tr) for tr in t_rows]

            return decision

    def get_job_summary(self) -> dict[str, Any]:
        """Aggregate statistical summary of all records in the ledger."""
        with self.transaction() as conn:
            docs_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            chunks_count = conn.execute("SELECT COUNT(*) FROM evidence_chunks").fetchone()[0]
            obs_count = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
            facts_count = conn.execute("SELECT COUNT(*) FROM fact_candidates").fetchone()[0]
            groups_count = conn.execute("SELECT COUNT(*) FROM fact_groups").fetchone()[0]
            decisions_count = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]

            verdicts_rows = conn.execute(
                "SELECT verdict, COUNT(*) FROM decisions GROUP BY verdict"
            ).fetchall()
            verdict_breakdown = {row[0]: row[1] for row in verdicts_rows}

            return {
                "documents_count": docs_count,
                "evidence_chunks_count": chunks_count,
                "observations_count": obs_count,
                "fact_candidates_count": facts_count,
                "fact_groups_count": groups_count,
                "decisions_count": decisions_count,
                "verdicts": {
                    "CORROBORATED": verdict_breakdown.get("CORROBORATED", 0),
                    "CONTRADICTION": verdict_breakdown.get("CONTRADICTION", 0),
                    "RECONCILED": verdict_breakdown.get("RECONCILED", 0),
                    "UNRESOLVED": verdict_breakdown.get("UNRESOLVED", 0),
                },
            }
