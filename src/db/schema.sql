-- Pragmas for performance, concurrency, and data integrity
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

-- ============================================================================
-- 1. EVIDENCE LAYER (Source Provenance)
-- ============================================================================

CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_hash TEXT NOT NULL UNIQUE,
    page_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidence_chunks (
    chunk_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    chunk_type TEXT CHECK(chunk_type IN ('text', 'table', 'figure')),
    bounding_box TEXT NOT NULL, -- JSON array: [x0, y0, x1, y1]
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chunks_doc_page ON evidence_chunks(document_id, page_number);

-- Context-Enriched Evidence Windows
CREATE TABLE IF NOT EXISTS evidence_windows (
    window_id TEXT PRIMARY KEY,
    chunk_id TEXT NOT NULL UNIQUE,
    document_id TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    section_title TEXT DEFAULT '',
    section_confidence REAL DEFAULT 0.0,
    table_caption TEXT DEFAULT '',
    stated_unit TEXT DEFAULT '',
    stated_currency TEXT DEFAULT '',
    column_headers TEXT DEFAULT '[]',   -- JSON array of column strings
    row_context TEXT DEFAULT '',
    page_header TEXT DEFAULT '',
    footnotes TEXT DEFAULT '[]',        -- JSON array of footnote strings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(chunk_id) REFERENCES evidence_chunks(chunk_id) ON DELETE CASCADE,
    FOREIGN KEY(document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_evidence_windows_doc ON evidence_windows(document_id);
CREATE INDEX IF NOT EXISTS idx_evidence_windows_chunk ON evidence_windows(chunk_id);

-- ============================================================================
-- 2. FACT CONSTRUCTION LAYER (Claims & Normalization)
-- ============================================================================

CREATE TABLE IF NOT EXISTS observations (
    observation_id TEXT PRIMARY KEY,
    chunk_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    statement TEXT NOT NULL,
    entity TEXT NOT NULL,
    attribute TEXT NOT NULL,
    raw_value TEXT NOT NULL,
    observation_type TEXT CHECK(observation_type IN ('numerical', 'semantic', 'event')),
    temporal_scope TEXT NOT NULL,
    provenance_status TEXT CHECK(provenance_status IN ('ENTAILED', 'HALLUCINATED', 'AMBIGUOUS')),
    confidence REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(chunk_id) REFERENCES evidence_chunks(chunk_id) ON DELETE CASCADE,
    FOREIGN KEY(document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_observations_entity_attr ON observations(entity, attribute);

CREATE TABLE IF NOT EXISTS fact_candidates (
    fact_id TEXT PRIMARY KEY,
    observation_id TEXT NOT NULL UNIQUE,
    normalized_value TEXT NOT NULL,
    normalized_unit TEXT NOT NULL,
    normalized_currency TEXT NOT NULL,
    period_start TEXT NOT NULL, -- ISO 8601 YYYY-MM-DD
    period_end TEXT NOT NULL,   -- ISO 8601 YYYY-MM-DD
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(observation_id) REFERENCES observations(observation_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_facts_period ON fact_candidates(period_start, period_end);

-- Additive Table: Fact Identity Signatures
CREATE TABLE IF NOT EXISTS fact_identities (
    identity_id TEXT PRIMARY KEY,
    fact_id TEXT NOT NULL UNIQUE,
    entity_canonical TEXT NOT NULL,
    metric_family TEXT NOT NULL,
    metric_subtype TEXT NOT NULL,
    measurement_type TEXT NOT NULL CHECK(measurement_type IN ('ABSOLUTE_VALUE', 'PERCENTAGE', 'RATE_OF_CHANGE', 'RATIO', 'UNKNOWN')),
    surface_metric TEXT NOT NULL,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    scope TEXT DEFAULT 'UNKNOWN',
    basis TEXT DEFAULT 'UNKNOWN',
    definition TEXT DEFAULT '',
    geography TEXT DEFAULT '',
    source_type TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(fact_id) REFERENCES fact_candidates(fact_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_identities_entity_metric ON fact_identities(entity_canonical, metric_family, metric_subtype);
CREATE INDEX IF NOT EXISTS idx_identities_period ON fact_identities(period_start, period_end);

CREATE TABLE IF NOT EXISTS fact_groups (
    group_id TEXT PRIMARY KEY,
    entity TEXT NOT NULL,
    attribute TEXT NOT NULL,
    period_id TEXT NOT NULL,
    member_count INTEGER NOT NULL DEFAULT 0,
    metric_family TEXT DEFAULT '',
    metric_subtype TEXT DEFAULT '',
    measurement_type TEXT DEFAULT 'UNKNOWN',
    group_type TEXT DEFAULT 'DIRECT_COMPARISON',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS group_members (
    group_id TEXT NOT NULL,
    fact_id TEXT NOT NULL,
    PRIMARY KEY(group_id, fact_id),
    FOREIGN KEY(group_id) REFERENCES fact_groups(group_id) ON DELETE CASCADE,
    FOREIGN KEY(fact_id) REFERENCES fact_candidates(fact_id) ON DELETE CASCADE
);

-- Additive Table: Claim Relationship Graph Edges
CREATE TABLE IF NOT EXISTS claim_relationships (
    relationship_id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL,
    source_fact_id TEXT NOT NULL,
    target_fact_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL CHECK(relationship_type IN ('CORROBORATES', 'CONFLICTS_WITH', 'RECONCILES_WITH', 'INCONCLUSIVE')),
    variance_percentage REAL DEFAULT 0.0,
    bridge_explanation TEXT DEFAULT '',
    details_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(group_id) REFERENCES fact_groups(group_id) ON DELETE CASCADE,
    FOREIGN KEY(source_fact_id) REFERENCES fact_candidates(fact_id) ON DELETE CASCADE,
    FOREIGN KEY(target_fact_id) REFERENCES fact_candidates(fact_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_claim_rel_group ON claim_relationships(group_id);

-- ============================================================================
-- 3. DECISION ENGINE LAYER (Reasoning, Hypotheses & Verdicts)
-- ============================================================================

CREATE TABLE IF NOT EXISTS hypotheses (
    hypothesis_id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL,
    explanation_type TEXT NOT NULL,
    description TEXT NOT NULL,
    likelihood_score REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(group_id) REFERENCES fact_groups(group_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS validator_results (
    result_id TEXT PRIMARY KEY,
    hypothesis_id TEXT NOT NULL,
    validator_type TEXT NOT NULL,
    outcome TEXT CHECK(outcome IN ('SUPPORTED', 'REFUTED', 'INCONCLUSIVE')),
    details_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(hypothesis_id) REFERENCES hypotheses(hypothesis_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS decisions (
    decision_id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL UNIQUE,
    verdict TEXT CHECK(verdict IN ('CORROBORATED', 'CONTRADICTION', 'RECONCILED', 'UNRESOLVED')),
    decision_strength TEXT CHECK(decision_strength IN ('HIGH', 'MEDIUM', 'LOW', 'INSUFFICIENT')),
    reasoning_summary TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(group_id) REFERENCES fact_groups(group_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_decisions_verdict ON decisions(verdict);

CREATE TABLE IF NOT EXISTS decision_traces (
    trace_id TEXT PRIMARY KEY,
    decision_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    input_json TEXT NOT NULL,
    output_json TEXT NOT NULL,
    execution_time_ms REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(decision_id) REFERENCES decisions(decision_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_traces_decision ON decision_traces(decision_id);
