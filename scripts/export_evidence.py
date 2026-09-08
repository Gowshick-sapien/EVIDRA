"""
Utility script to populate runs/<JOB_ID>/evidence/ directories from ledger.db
for human inspection and audit verification.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def export_evidence_for_job(job_dir: Path) -> None:
    db_path = job_dir / "ledger.db"
    ev_dir = job_dir / "evidence"
    if not db_path.exists():
        return

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    try:
        count = cur.execute("SELECT count(*) FROM evidence_chunks").fetchone()[0]
    except Exception:
        return
    if count == 0:
        return

    tables_dir = ev_dir / "tables"
    cands_dir = ev_dir / "candidates"
    tables_dir.mkdir(parents=True, exist_ok=True)
    cands_dir.mkdir(parents=True, exist_ok=True)

    # 1. Export structural table snapshots
    tables = cur.execute(
        "SELECT chunk_id, document_id, page_number, bounding_box, content FROM evidence_chunks WHERE chunk_type = 'table'"
    ).fetchall()
    for cid, doc_id, page, bbox, content in tables:
        t_file = tables_dir / f"{doc_id}_p{page}_{cid[:8]}.md"
        with open(t_file, "w", encoding="utf-8") as f:
            f.write(f"# Extracted Table: {doc_id} (Page {page})\n\n")
            f.write(f"- **Chunk ID:** `{cid}`\n")
            f.write(f"- **Bounding Box:** `{bbox}`\n\n")
            f.write("## Table Content\n\n")
            f.write(content + "\n")

    # 2. Export candidate chunks associated with observations
    cands = cur.execute(
        "SELECT DISTINCT c.chunk_id, c.document_id, c.page_number, c.chunk_type, c.bounding_box, c.content "
        "FROM observations o JOIN evidence_chunks c ON o.chunk_id = c.chunk_id"
    ).fetchall()
    for cid, doc_id, page, ctype, bbox, content in cands:
        c_file = cands_dir / f"{doc_id}_p{page}_{cid[:8]}.md"
        with open(c_file, "w", encoding="utf-8") as f:
            f.write(f"# Candidate Evidence Chunk: {doc_id} (Page {page})\n\n")
            f.write(f"- **Chunk ID:** `{cid}`\n")
            f.write(f"- **Type:** `{ctype}`\n")
            f.write(f"- **Bounding Box:** `{bbox}`\n\n")
            f.write("## Raw Content\n\n")
            f.write(content + "\n")

    # 3. Export document manifests
    docs = cur.execute("SELECT document_id, filename, page_count FROM documents").fetchall()
    for doc_id, fname, page_cnt in docs:
        tot_chunks = cur.execute("SELECT count(*) FROM evidence_chunks WHERE document_id = ?", (doc_id,)).fetchone()[0]
        tbl_chunks = cur.execute(
            "SELECT count(*) FROM evidence_chunks WHERE document_id = ? AND chunk_type = 'table'", (doc_id,)
        ).fetchone()[0]
        txt_chunks = cur.execute(
            "SELECT count(*) FROM evidence_chunks WHERE document_id = ? AND chunk_type = 'text'", (doc_id,)
        ).fetchone()[0]
        cand_ids = [
            r[0] for r in cur.execute("SELECT DISTINCT chunk_id FROM observations WHERE document_id = ?", (doc_id,)).fetchall()
        ]

        manifest = {
            "document_id": doc_id,
            "filename": fname,
            "page_count": page_cnt,
            "total_chunks": tot_chunks,
            "table_chunks_count": tbl_chunks,
            "text_chunks_count": txt_chunks,
            "candidate_chunks_count": len(cand_ids),
            "candidate_chunk_ids": cand_ids,
        }
        with open(ev_dir / f"{doc_id}_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    print(f"Populated evidence directory for {job_dir.name}: {len(tables)} tables, {len(cands)} candidate chunks, {len(docs)} document manifests.")


def main():
    runs_dir = Path("runs")
    for job_dir in sorted(runs_dir.glob("JOB-*")):
        if job_dir.is_dir():
            export_evidence_for_job(job_dir)


if __name__ == "__main__":
    main()
