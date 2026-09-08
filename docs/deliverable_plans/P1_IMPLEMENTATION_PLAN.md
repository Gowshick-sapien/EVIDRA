# EVIDRA 2.0: Deliverable Phase P1 Implementation Plan: Semantic Identity and Contextual Resolution

> **Parent Specification:** [docs/DELIVERABLES_DEFINITION_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/DELIVERABLES_DEFINITION_V2.md)  
> **Architecture Reference:** [docs/ARCHITECTURE_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/ARCHITECTURE_V2.md)  
> **SRS Reference:** [docs/SRS_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/SRS_V2.md)  
> **Status:** Ready for Implementation (Development Branch: `dev_v2`)  
> **Deliverable Phase:** P1 (Make Identity Trustworthy)  

---

## 1. Executive Overview and Epistemic Objective

Deliverable Phase P1 implements **Semantic Identity and Contextual Resolution** for EVIDRA 2.0. Empirical analysis of the V1 pipeline on multi-document corporate filings proved that **unconstrained attribute grouping without structural identity signatures produces 100% false contradictions**:

```text
V1 Fact Grouping Bottleneck:
  Raw Candidate Facts
       | (Flat Cosine Similarity on Attribute Names: threshold = 0.82)
       v
  Conflated Fact Groups:
    - INR 8,142 Cr (Absolute Revenue) grouped with 12.5% (EBITDA Margin)
    - FY2024 Revenue (12 months) grouped with Q4 FY2024 Revenue (3 months)
    - Standalone Revenue grouped with Consolidated Revenue
       |
       v
  100% False-Positive Contradictions & Truncated Multi-Member Groups
```

In accordance with EVIDRA 2.0's governing principle:
> **Numerical variance checks must never precede identity verification; two facts may only be compared if their Fact Identity Signatures match across entity, metric family, subtype, and measurement type.**

Phase P1 replaces unconstrained attribute clustering with a disciplined 4-Gate resolution architecture. It guarantees that:
1. Every candidate fact is formalized into a structured **Fact Identity Signature** equipped with explicit **Measurement Semantics** (`ABSOLUTE_VALUE`, `PERCENTAGE`, `RATE_OF_CHANGE`, `RATIO`).
2. Temporal relationships are formally classified into explicit comparability classes (`EXACT_MATCH`, `CONTAINMENT`, `ADJACENT_PERIOD`, `OVERLAPPING`, `NON_OVERLAPPING`).
3. Facts are grouped across documents through **4 disciplined verification gates**, cleanly separating direct numerical comparison groups from contextual reconciliation groups.
4. Fact groups with $N \ge 2$ members are evaluated across the core Architecture 1 LangGraph tournament using a **Claim Relationship Graph** with typed edges (`CORROBORATES`, `CONFLICTS_WITH`, `RECONCILES_WITH`) and value equivalence clustering, eliminating naive majority voting.

---

## 2. Requirements Coverage (SRS V2 Mapping)

The following table maps the specific Software Requirements Specification (SRS V2) requirements satisfied by Deliverable Phase P1:

| Requirement ID | Requirement Statement | P1 Implementation Mechanism | Target Module |
| :--- | :--- | :--- | :--- |
| **REQ-ID-RES-01** | Fact Identity Signature formalization with explicit Measurement Semantics. | `FactIdentitySignature` model and deterministic `MeasurementClassifier` assigning dimensional typing (`ABSOLUTE_VALUE`, `PERCENTAGE`, `RATE_OF_CHANGE`, `RATIO`). | `src/matching/identity.py`<br>`src/extraction/schemas.py` |
| **REQ-TMP-EXT-01** | Temporal Comparability Classification (Gate 2). | `TemporalComparabilityClassifier` classifying date pairs into `EXACT_MATCH`, `CONTAINMENT`, `ADJACENT_PERIOD`, `OVERLAPPING`, `NON_OVERLAPPING`, and `UNKNOWN`. | `src/matching/temporal.py` |
| **REQ-MAT-EXT-01** | 4-Gate Contextual Fact Resolution pipeline. | Redesign of `FactGroupEngine` into a 4-gate verification sequence: Gate 1 Entity, Gate 2 Temporal, Gate 3 Metric & Measurement, Gate 4 Context Routing. | `src/matching/embeddings.py`<br>`src/verification/pipeline.py` |
| **REQ-DEC-EXT-02** | Claim Relationship Graph and Cluster-Based Adjudication. | Multi-member tournament orchestrator executing $N(N-1)/2$ pairwise evaluations, constructing typed edge graph, and clustering by normalized value equivalence. | `src/decision/engine.py`<br>`src/decision/workflow.py` |
| **REQ-LEDG-EXT-02** | Additive schema migrations and ledger persistence for Fact Identities and Claim Relationships. | Database tables `fact_identities` and `claim_relationships`, plus extended columns on `fact_groups`. | `src/db/schema.sql`<br>`src/db/ledger.py` |

---

## 3. Scope and Architectural Deliverables

Phase P1 delivers three core functional deliverables and one infrastructure schema migration:

### D-P1.0: Fact Identity & Relationship Schema Migration
- Additive SQL migration in `src/db/schema.sql`:
  - `fact_identities` table capturing structured identity signatures.
  - `claim_relationships` table storing pairwise graph edges (`CORROBORATES`, `CONFLICTS_WITH`, `RECONCILES_WITH`).
  - Additive columns on `fact_groups`: `metric_family`, `metric_subtype`, `measurement_type`, `group_type`.
- Extended dataclasses `FactIdentityRecord` and `ClaimRelationshipRecord` in `src/db/ledger.py`.
- Extended ledger CRUD and query methods in `src/db/ledger.py`.

### D-P1.1: Fact Identity Signature & Temporal Comparability
- Implementation of `src/matching/identity.py`:
  - `MeasurementType` Enum (`ABSOLUTE_VALUE`, `PERCENTAGE`, `RATE_OF_CHANGE`, `RATIO`, `UNKNOWN`).
  - Deterministic `MeasurementClassifier` evaluating units, symbols, and keywords.
  - `FactIdentitySignature` schema binding canonical entity, metric family, metric subtype, measurement type, verbatim surface metric, ISO dates, scope, and accounting basis.
  - `FactIdentityBuilder` constructing identity signatures by combining observation text, candidate normalization, document schema induction, and context resolution.
- Implementation of `src/matching/temporal.py`:
  - `TemporalRelation` Enum (`EXACT`, `CONTAINMENT`, `ADJACENT`, `OVERLAPPING`, `NON_OVERLAPPING`, `UNKNOWN`).
  - `ComparabilityAction` Enum (`DIRECTLY_COMPARABLE`, `CONTEXTUALLY_RELATED`, `SPECIALIZED_TREATMENT`, `NON_COMPARABLE`, `UNRESOLVED`).
  - `TemporalComparabilityClassifier` evaluating intervals for strict date equality, period containment (e.g. Q4 inside FY24), adjacent reporting periods, partial shifts, and disjoint spans.

### D-P1.2: 4-Gate Contextual Fact Resolution
- Refactoring of `src/matching/embeddings.py` (`FactGroupEngine`):
  - **Gate 1 (Entity Grounding):** Canonical entity resolution enforcing strict corporate entity alignment.
  - **Gate 2 (Temporal Comparability):** Direct comparison fact groups formed only when temporal relationship evaluates to `DIRECTLY_COMPARABLE`. Pairs with `CONTEXTUALLY_RELATED` form contextual context groups without direct numerical variance comparison.
  - **Gate 3 (Metric & Measurement Compatibility):** Hard block on measurement type mismatches (`ABSOLUTE_VALUE` vs `RATE_OF_CHANGE`). Same family + same subtype forms direct comparison group; same family + distinct subtype forms contextual family group.
  - **Gate 4 (Context Compatibility):** Mismatches in `scope` (Consolidated vs Standalone) or `basis` (Ind AS vs Non-GAAP) routes group to Path B (Contextual Reconciliation).
  - BGE embedding semantic fallback used strictly for matching verbatim surface variants within the same metric family and measurement type.
- Integration into `src/verification/pipeline.py`:
  - Binding `FactIdentitySignature` during candidate normalization.
  - Generating partitioned fact groups with explicit metadata headers.

### D-P1.3: Claim Relationship Graph & Cluster-Based Adjudication
- Refactoring of `src/decision/engine.py` and `src/decision/workflow.py`:
  - Elimination of the binary `candidates[0], candidates[1]` limitation.
  - Enumeration and execution of all unique candidate pairs $(c_i, c_j)$ across the unchanged Architecture 1 LangGraph tournament.
  - Construction of an in-memory and ledger-persisted `ClaimRelationshipGraph` with typed edges (`CORROBORATES`, `CONFLICTS_WITH`, `RECONCILES_WITH`).
  - Claim equivalence clustering: grouping claims by normalized numerical value and unit within $\epsilon = 0.001$.
  - Graph-level synthesis verdict:
    - **1 Cluster:** `UNANIMOUS_CORROBORATION` (Verdict: `CORROBORATED`).
    - **2+ Clusters with Supported Reconciliation Edges:** `RECONCILED_CLUSTERS` (Verdict: `RECONCILED`).
    - **2+ Clusters with Unreconciled Conflict Edges:** `CONFLICTING_CLAIM_CLUSTERS` (Verdict: `CONTRADICTION`).
    - **Single Candidate or Inconclusive Evidence:** Verdict: `UNRESOLVED`.

---

## 4. Detailed Component Specifications

### 4.1 Database Migration & Ledger Data Access

#### SQL Schema Extension (`src/db/schema.sql`)
```sql
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
```

#### Additive Columns on `fact_groups`:
```sql
ALTER TABLE fact_groups ADD COLUMN metric_family TEXT DEFAULT '';
ALTER TABLE fact_groups ADD COLUMN metric_subtype TEXT DEFAULT '';
ALTER TABLE fact_groups ADD COLUMN measurement_type TEXT DEFAULT 'UNKNOWN';
ALTER TABLE fact_groups ADD COLUMN group_type TEXT DEFAULT 'DIRECT_COMPARISON'; -- DIRECT_COMPARISON | CONTEXTUAL_COMPARISON
```

#### Python Dataclasses (`src/db/ledger.py`)
```python
@dataclass
class FactIdentityRecord:
    identity_id: str
    fact_id: str
    entity_canonical: str
    metric_family: str
    metric_subtype: str
    measurement_type: str
    surface_metric: str
    period_start: str
    period_end: str
    scope: str = "UNKNOWN"
    basis: str = "UNKNOWN"
    definition: str = ""
    geography: str = ""
    source_type: str = ""

@dataclass
class ClaimRelationshipRecord:
    relationship_id: str
    group_id: str
    source_fact_id: str
    target_fact_id: str
    relationship_type: str  # CORROBORATES | CONFLICTS_WITH | RECONCILES_WITH | INCONCLUSIVE
    variance_percentage: float = 0.0
    bridge_explanation: str = ""
    details_json: str = "{}"
```

#### Ledger CRUD Methods to Implement in `EvidenceLedger`:
- `insert_fact_identities(identities: list[FactIdentityRecord]) -> int`
- `get_fact_identity(fact_id: str) -> Optional[FactIdentityRecord]`
- `insert_claim_relationships(relationships: list[ClaimRelationshipRecord]) -> int`
- `get_claim_relationships_for_group(group_id: str) -> list[ClaimRelationshipRecord]`
- Extended `create_fact_group()` accepting `metric_family`, `metric_subtype`, `measurement_type`, and `group_type`.

---

### 4.2 Fact Identity Signature & Measurement Classifier (`src/matching/identity.py`)

#### Measurement Semantics Models:
```python
class MeasurementType(str, Enum):
    ABSOLUTE_VALUE = "ABSOLUTE_VALUE"   # Currency amounts (INR 8,142 Cr), counts (15,000 pincodes)
    PERCENTAGE = "PERCENTAGE"           # Margins, proportions (12.5% EBITDA Margin)
    RATE_OF_CHANGE = "RATE_OF_CHANGE"   # Growth rates, YoY, QoQ changes (+29.8% YoY)
    RATIO = "RATIO"                     # Multiples, coverage ratios (1.4x Debt-to-Equity)
    UNKNOWN = "UNKNOWN"

class FactIdentitySignature(BaseModel):
    identity_id: str
    fact_id: str
    entity_canonical: str
    metric_family: str
    metric_subtype: str
    measurement_type: MeasurementType
    surface_metric: str
    period_start: str
    period_end: str
    scope: str = "UNKNOWN"
    basis: str = "UNKNOWN"
    definition: str = ""
    geography: str = ""
    source_type: str = ""
```

#### Deterministic Measurement Classifier:
```python
class MeasurementClassifier:
    """Classifies numerical observations into explicit measurement types."""

    RATE_PATTERNS = [
        re.compile(r"\b(?:yoy|qoq|mom|growth|cagr|annualized|increase|decrease|rate of change)\b", re.I),
        re.compile(r"[-+]\d+(?:\.\d+)?%", re.I),
    ]
    PERCENT_PATTERNS = [
        re.compile(r"%\s*margin\b", re.I),
        re.compile(r"\bmargin\b", re.I),
        re.compile(r"\b(?:percent|percentage|share|proportion|yield|return on|roa|roe|roce)\b", re.I),
        re.compile(r"%", re.I),
    ]
    RATIO_PATTERNS = [
        re.compile(r"\b\d+(?:\.\d+)?x\b", re.I),
        re.compile(r"\b(?:ratio|multiple|times|debt-to-equity|coverage)\b", re.I),
    ]

    @classmethod
    def classify(cls, raw_value: str, attribute: str, unit: str, statement: str) -> MeasurementType:
        context = f"{raw_value} {attribute} {unit} {statement}".lower()

        for pattern in cls.RATE_PATTERNS:
            if pattern.search(context):
                return MeasurementType.RATE_OF_CHANGE

        for pattern in cls.RATIO_PATTERNS:
            if pattern.search(context):
                return MeasurementType.RATIO

        for pattern in cls.PERCENT_PATTERNS:
            if pattern.search(context):
                return MeasurementType.PERCENTAGE

        if any(curr in context for curr in ["rs", "inr", "usd", "$", "₹", "crore", "lakh", "million", "billion"]):
            return MeasurementType.ABSOLUTE_VALUE

        return MeasurementType.ABSOLUTE_VALUE
```

---

### 4.3 Temporal Comparability Classification (`src/matching/temporal.py`)

Temporal interval overlap does not establish identical temporal claims. Direct numerical comparison requires strict period equivalence.

```python
class TemporalRelation(str, Enum):
    EXACT = "EXACT"
    CONTAINMENT = "CONTAINMENT"
    ADJACENT = "ADJACENT"
    OVERLAPPING = "OVERLAPPING"
    NON_OVERLAPPING = "NON_OVERLAPPING"
    UNKNOWN = "UNKNOWN"

class ComparabilityAction(str, Enum):
    DIRECTLY_COMPARABLE = "DIRECTLY_COMPARABLE"     # Direct numerical comparison permitted
    CONTEXTUALLY_RELATED = "CONTEXTUALLY_RELATED"   # Related temporal context; DO NOT compare values
    SPECIALIZED_TREATMENT = "SPECIALIZED_TREATMENT" # Disjoint shift; requires specialized reconciler
    NON_COMPARABLE = "NON_COMPARABLE"               # Disjoint periods; do not group
    UNRESOLVED = "UNRESOLVED"                       # Ambiguous temporal boundaries

class TemporalComparabilityClassifier:
    """Classifies temporal relationships and defines exact comparison actions."""

    @classmethod
    def classify(
        cls,
        start1: str,
        end1: str,
        start2: str,
        end2: str,
    ) -> tuple[TemporalRelation, ComparabilityAction]:
        if start1 == "1970-01-01" or start2 == "1970-01-01":
            return TemporalRelation.UNKNOWN, ComparabilityAction.UNRESOLVED

        d_s1 = date.fromisoformat(start1)
        d_e1 = date.fromisoformat(end1)
        d_s2 = date.fromisoformat(start2)
        d_e2 = date.fromisoformat(end2)

        # 1. Exact Match
        if d_s1 == d_s2 and d_e1 == d_e2:
            return TemporalRelation.EXACT, ComparabilityAction.DIRECTLY_COMPARABLE

        # 2. Containment (e.g. Q4 3-month inside FY 12-month)
        if (d_s1 <= d_s2 and d_e2 <= d_e1) or (d_s2 <= d_s1 and d_e1 <= d_e2):
            return TemporalRelation.CONTAINMENT, ComparabilityAction.CONTEXTUALLY_RELATED

        # 3. Adjacent (e.g. FY23 ending 2023-03-31 and FY24 starting 2023-04-01)
        if d_e1 + timedelta(days=1) == d_s2 or d_e2 + timedelta(days=1) == d_s1:
            return TemporalRelation.ADJACENT, ComparabilityAction.CONTEXTUALLY_RELATED

        # 4. Non-Overlapping Disjoint
        if d_e1 < d_s2 or d_e2 < d_s1:
            return TemporalRelation.NON_OVERLAPPING, ComparabilityAction.NON_COMPARABLE

        # 5. Overlapping Partial Shift
        return TemporalRelation.OVERLAPPING, ComparabilityAction.SPECIALIZED_TREATMENT
```

---

### 4.4 4-Gate Contextual Fact Resolution (`src/matching/embeddings.py`)

Redesigns `FactGroupEngine` to group candidates across documents using 4 sequential gates:

```python
class ContextualFactGroupEngine:
    """4-Gate candidate fact grouping engine combining structural signatures with embedding fallback."""

    def __init__(
        self,
        embedding_model_name: str = "BAAI/bge-small-en-v1.5",
        similarity_threshold: float = 0.88,
    ):
        self.model_name = embedding_model_name
        self.similarity_threshold = similarity_threshold
        self._model = None

    def group_candidates(
        self,
        candidates: list[CandidateFactView],
        signatures: dict[str, FactIdentitySignature],
    ) -> list[tuple[FactGroupRecord, list[str], str]]:
        """
        Group candidates through the 4-gate verification sequence.
        
        Returns:
            List of tuples: (FactGroupRecord, [fact_ids], group_type)
        """
        # Step 1: Gate 1 Hard Blocking on Canonical Entity
        entity_partitions: dict[str, list[CandidateFactView]] = {}
        for c in candidates:
            sig = signatures.get(c.fact_id)
            entity_key = sig.entity_canonical if sig else normalize_entity_name(c.entity)
            entity_partitions.setdefault(entity_key, []).append(c)

        fact_groups: list[tuple[FactGroupRecord, list[str], str]] = []

        for entity_key, members in entity_partitions.items():
            # Step 2: Gate 3 Dimensional Hard Blocking on MeasurementType & MetricFamily
            family_partitions: dict[tuple[str, str], list[CandidateFactView]] = {}
            for m in members:
                sig = signatures.get(m.fact_id)
                m_type = sig.measurement_type.value if sig else "UNKNOWN"
                m_fam = sig.metric_family if sig else "OPERATIONAL_METRICS"
                family_partitions.setdefault((m_type, m_fam), []).append(m)

            for (m_type, m_fam), fam_members in family_partitions.items():
                # Step 3: Gate 2 Temporal Comparability Clustering
                temporal_clusters = self._cluster_by_temporal_comparability(fam_members)

                for temp_cluster in temporal_clusters:
                    # Step 4: Gate 3 Subtype & Surface Proximity + Gate 4 Context Routing
                    resolved_subgroups = self._resolve_subtypes_and_context(
                        temp_cluster, signatures
                    )
                    fact_groups.extend(resolved_subgroups)

        return fact_groups
```

#### Gate 2 Temporal Clustering Logic:
1. For each pair $(c_1, c_2)$ in the partition, classify temporal comparability.
2. If relation is `EXACT`, candidates join the `DIRECT_COMPARISON` subgroup.
3. If relation is `CONTAINMENT` or `ADJACENT`, candidates are partitioned into separate primary direct groups, but registered in a linked `CONTEXTUAL_COMPARISON` fact group to provide supporting context without numerical variance checking.
4. If relation is `NON_OVERLAPPING`, grouping between them is strictly prevented.

---

### 4.5 Claim Relationship Graph & Cluster-Based Adjudication (`src/decision/engine.py`, `src/decision/workflow.py`)

Replaces binary `candidates[0], candidates[1]` assumption with graph synthesis:

```python
class ClaimCluster(BaseModel):
    cluster_id: str
    canonical_value: Decimal
    canonical_unit: str
    member_fact_ids: list[str]
    citations: list[str]  # e.g., ["Annual Report p.36", "Earnings Presentation p.6"]

class ClaimRelationshipGraph(BaseModel):
    group_id: str
    nodes: list[str]  # fact_ids
    edges: list[ClaimRelationshipRecord] = Field(default_factory=list)
    clusters: list[ClaimCluster] = Field(default_factory=list)
    synthesis_verdict: str  # CORROBORATED | RECONCILED | CONTRADICTION | UNRESOLVED
    synthesis_explanation: str
```

#### Pairwise Evaluation and Synthesis Protocol:
1. For a fact group with members $\{c_1, c_2, \dots, c_N\}$ ($N \ge 2$):
   - Enumerate all unique pairs $P = \{(c_i, c_j) \mid 1 \le i < j \le N\}$.
   - For each pair $(c_i, c_j)$, invoke the core Architecture 1 LangGraph tournament.
   - Record the resulting relationship edge in `claim_relationships`:
     - Arithmetic equality ($\Delta \le 0.1\%$) and matching context -> `CORROBORATES`.
     - Arithmetic variance with supported validator bridge (e.g. Non-GAAP, Restatement) -> `RECONCILES_WITH`.
     - Arithmetic variance without validator bridge -> `CONFLICTS_WITH`.
     - Inconclusive evidence -> `INCONCLUSIVE`.
2. Equivalence Value Clustering:
   - Group members whose normalized numerical values match within relative tolerance $\epsilon = 0.001$ into value clusters $C_1, C_2, \dots, C_K$.
3. Graph Synthesis Rules:
   - **$K = 1$ (Single Value Cluster):** Every cross-pair corroborates -> `UNANIMOUS_CORROBORATION` (Verdict: `CORROBORATED`, Strength: `HIGH`).
   - **$K \ge 2$ (Multiple Value Clusters) with Valid Reconciliation:** Every cross-cluster pair is linked by a validated `RECONCILES_WITH` edge -> `RECONCILED_CLUSTERS` (Verdict: `RECONCILED`, Strength: `HIGH` or `MEDIUM`).
   - **$K \ge 2$ with Direct Variance:** Cross-cluster pairs have `CONFLICTS_WITH` edges without structural reconciliation -> `CONFLICTING_CLAIM_CLUSTERS` (Verdict: `CONTRADICTION`, Strength: `HIGH`).
   - **$N = 1$ or Ambiguous Graph:** Verdict: `UNRESOLVED` (Strength: `INSUFFICIENT`).

---

## 5. File Modification Inventory

| File Path | Action | Scope of Changes |
| :--- | :--- | :--- |
| `src/db/schema.sql` | **Modify** | Add `fact_identities` table, `claim_relationships` table, and additive columns on `fact_groups` (`metric_family`, `metric_subtype`, `measurement_type`, `group_type`). |
| `src/db/ledger.py` | **Modify** | Add `FactIdentityRecord` and `ClaimRelationshipRecord` dataclasses; add CRUD methods `insert_fact_identities()`, `get_fact_identity()`, `insert_claim_relationships()`, `get_claim_relationships_for_group()`. |
| `src/extraction/schemas.py` | **Modify** | Export `MeasurementType` and `FactIdentitySignature` schemas. |
| `src/matching/identity.py` | **Create** | Implement `MeasurementType`, `MeasurementClassifier`, `FactIdentitySignature`, and `FactIdentityBuilder`. |
| `src/matching/temporal.py` | **Create** | Implement `TemporalRelation`, `ComparabilityAction`, and `TemporalComparabilityClassifier`. |
| `src/matching/embeddings.py` | **Modify** | Redesign `FactGroupEngine` into `ContextualFactGroupEngine` executing the 4-gate verification sequence. |
| `src/verification/pipeline.py` | **Modify** | Integrate `FactIdentityBuilder` into candidate normalization; update grouping call to pass identity signatures. |
| `src/decision/engine.py` | **Modify** | Replace binary `candidates[0], candidates[1]` extraction with pairwise tournament execution, graph edge logging, and cluster synthesis. |
| `src/decision/workflow.py` | **Modify** | Support pair evaluation harness and cluster-aware state representations. |
| `tests/unit/test_identity.py` | **Create** | Unit tests for measurement classification (`ABSOLUTE_VALUE`, `PERCENTAGE`, `RATE_OF_CHANGE`, `RATIO`) and identity signature construction. |
| `tests/unit/test_temporal_comparability.py` | **Create** | Unit tests for temporal comparability classification (`EXACT_MATCH`, `CONTAINMENT`, `ADJACENT_PERIOD`, `OVERLAPPING`, `NON_OVERLAPPING`). |
| `tests/unit/test_4gate_resolution.py` | **Create** | Unit tests verifying the 4-gate fact resolution pipeline and metric isolation. |
| `tests/unit/test_claim_graph.py` | **Create** | Unit tests verifying pairwise tournament execution, typed graph edges, value clustering, and synthesis verdicts. |

---

## 6. Step-by-Step Implementation Sequence

The implementation proceeds in six sequential, test-driven steps:

```text
Step 1: Database & Ledger Schema Migration
  └── Modify src/db/schema.sql and src/db/ledger.py
  └── Verify with pytest tests/unit/test_ledger.py

Step 2: Fact Identity Signature & Measurement Classifier
  └── Implement src/matching/identity.py and export in src/extraction/schemas.py
  └── Verify with tests/unit/test_identity.py

Step 3: Temporal Comparability Classifier
  └── Implement src/matching/temporal.py
  └── Verify with tests/unit/test_temporal_comparability.py

Step 4: 4-Gate Contextual Fact Resolution
  └── Redesign src/matching/embeddings.py and update src/verification/pipeline.py
  └── Verify with tests/unit/test_4gate_resolution.py

Step 5: Claim Relationship Graph & Value Clustering
  └── Update src/decision/engine.py and src/decision/workflow.py
  └── Verify with tests/unit/test_claim_graph.py

Step 6: End-to-End Multi-Document Verification on Delhivery Filings
  └── Run full pipeline across Delhivery Prospectus, Annual Report, and Earnings Presentation
  └── Verify zero false contradictions from metric mixing or temporal containment
```

---

## 7. Testing & Verification Plan

### 7.1 Unit Tests

1. **Measurement Classification Tests (`tests/unit/test_identity.py`):**
   - Verify `ABSOLUTE_VALUE` for `₹8,142 Cr`, `USD 120M`, `15,000 pincodes`.
   - Verify `PERCENTAGE` for `12.5% EBITDA Margin`, `PAT Margin 4.2%`.
   - Verify `RATE_OF_CHANGE` for `+29.8% YoY`, `revenue grew 18% QoQ`.
   - Verify `RATIO` for `1.4x`, `Debt-to-equity ratio of 0.8`.
   - Verify that absolute currency facts and percentage growth rates receive different `MeasurementType` values.

2. **Temporal Comparability Tests (`tests/unit/test_temporal_comparability.py`):**
   - Test `EXACT`: `2023-04-01` to `2024-03-31` vs `2023-04-01` to `2024-03-31` -> `DIRECTLY_COMPARABLE`.
   - Test `CONTAINMENT`: `2024-01-01` to `2024-03-31` (Q4) inside `2023-04-01` to `2024-03-31` (FY24) -> `CONTEXTUALLY_RELATED` (value comparison blocked).
   - Test `ADJACENT`: `2022-04-01` to `2023-03-31` (FY23) and `2023-04-01` to `2024-03-31` (FY24) -> `CONTEXTUALLY_RELATED`.
   - Test `NON_OVERLAPPING`: `2020-04-01` to `2021-03-31` vs `2023-04-01` to `2024-03-31` -> `NON_COMPARABLE` (grouping blocked).

3. **4-Gate Resolution Tests (`tests/unit/test_4gate_resolution.py`):**
   - Gate 1: Candidates for `Delhivery Limited` and `FedEx Corp` are never grouped together.
   - Gate 2: FY24 and Q4 FY24 claims are not placed into a direct numerical comparison group.
   - Gate 3: `Revenue from Operations` (Absolute) and `Revenue Growth %` (Rate) are strictly partitioned into separate groups.
   - Gate 4: `Consolidated Revenue` and `Standalone Revenue` are tagged for `CONTEXTUAL_COMPARISON` (Path B).

4. **Claim Relationship Graph Tests (`tests/unit/test_claim_graph.py`):**
   - Test 3 identical claims (₹500, ₹500, ₹500 across 3 documents) -> 3 corroborating edges, 1 cluster -> `UNANIMOUS_CORROBORATION`.
   - Test 4 claims (two ₹500, two ₹700) -> 2 value clusters, conflicting edges -> `CONFLICTING_CLAIM_CLUSTERS` (Verdict: `CONTRADICTION`).
   - Test 2 claims with Ind AS operating profit vs Adjusted EBITDA -> 2 clusters with supported Non-GAAP bridge -> `RECONCILED_CLUSTERS` (Verdict: `RECONCILED`).
   - Test single-member claim -> Verdict: `UNRESOLVED`.

### 7.2 Real Document Verification (Delhivery Dataset)

Execute the upgraded pipeline on the three Delhivery filings:
- `01-delhivery-prospectus-2022-excerpt.pdf`
- `02-delhivery-annual-report-2024-excerpt.pdf`
- `03-delhivery-earnings-presentation-q4fy24.pdf`

**Acceptance Thresholds:**
- **Zero False Contradictions from Dimensional Conflation:** 0 groups mixing `ABSOLUTE_VALUE` with `RATE_OF_CHANGE` or `PERCENTAGE`.
- **Zero False Contradictions from Temporal Containment:** 0 groups comparing annual revenue with quarterly revenue directly.
- **Multi-Member Group Handling:** 100% of candidate facts in groups with $N \ge 3$ members evaluated across the relationship tournament.
- **Clean Subtype Separation:** `Revenue from Operations` and `Revenue from Services` preserved as distinct subtypes.

---

## 8. Failure Modes, Edge Cases & Mitigations

| Failure Mode / Edge Case | Architectural Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Hybrid Percentage/Rate Metric Strings** | Strings like "Revenue Growth Rate: 15% Margin" contain both rate and percentage keywords. | Classifier prioritizes `RATE_OF_CHANGE` over `PERCENTAGE` whenever directional tokens (`growth`, `yoy`, `qoq`, `cagr`, `+`, `-`) are present. |
| **Point-in-Time Balance Sheet Dates vs Period Income Statement Dates** | "As of March 31, 2024" has `start == end`, whereas FY24 has a 365-day interval. | `TemporalComparabilityClassifier` classifies a point-in-time date falling on the terminal boundary of a period as `CONTAINMENT`, preventing direct variance comparison against full-year flows. |
| **Rounding Differences Across Documents** | One filing reports ₹8,142.34 Cr while another reports ₹8,142 Cr. | Value clustering groups claims within a relative numerical tolerance $\epsilon = 0.001$ (0.1%), logging exact precision variance without triggering false contradictions. |
| **Disconnected Pairwise Graph Components** | In multi-member groups ($N \ge 4$), some pairs may yield `INCONCLUSIVE` while others corroborate. | Graph synthesis uses connected component analysis: if all members belong to a single value cluster, the verdict is `CORROBORATED` despite isolated inconclusive edges. |
| **Missing Metric Subtype from Schema Induction** | Line item text was not discovered during upstream table row induction. | `FactIdentityBuilder` falls back to sanitized verbatim `observation.attribute` slug as subtype, assigning parent family via keyword classifier. |
| **Unstated Legal Entity in Subsidiary Tables** | Notes to accounts disclose joint venture or subsidiary metrics without repeating the primary company name. | `FactIdentityBuilder` inherits `primary_entity` from `DocumentSchema` when observation entity is generic or unstated, with explicit confidence logging. |
