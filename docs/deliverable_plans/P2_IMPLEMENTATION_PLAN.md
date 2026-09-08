# EVIDRA 2.0: Deliverable Phase P2 Implementation Plan: Validate Core Reasoning Tournament

> **Parent Specification:** [docs/DELIVERABLES_DEFINITION_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/DELIVERABLES_DEFINITION_V2.md)  
> **Architecture Reference:** [docs/ARCHITECTURE_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/ARCHITECTURE_V2.md)  
> **SRS Reference:** [docs/SRS_V2.md](file:///d:/projects/superjoin/EVIDRA/docs/SRS_V2.md)  
> **Status:** Ready for Review and Approval (Target Branch: `dev_v2`)  
> **Deliverable Phase:** P2 (Validate Core Reasoning Tournament Against Real Data)  

---

## 1. Executive Overview and Epistemic Objective

Deliverable Phase P2 validates and operationalizes the **Core Reasoning Tournament** (Layer 3) of EVIDRA 2.0 against real corporate filings from the Delhivery starter dataset.

In Architecture 1, the LangGraph tournament was designed around 5 specialist validators (`ArithmeticValidator`, `RestatementValidator`, `AccountingBasisValidator`, `ScopeValidator`, `TimingValidator`), hypothesis generation, reconciliation proposal, adversarial skeptic audit, and a deterministic decision policy. However, empirical evaluation revealed three fundamental operational deficiencies:

1. **Absence of Pre-Tournament Sufficiency Screening:** Fact groups were fed directly into variance analysis regardless of evidentiary completeness. Groups lacking resolved identities, single-source candidates, or unverified claims wastefully traversed LangGraph tournaments or caused arbitrary errors.
2. **Uncalibrated Reconciliation Bridge:** The conditions under which specialist validators successfully trigger a reconciliation proposal were theoretical, lacking calibration against multi-source corporate financial disclosures (such as Ind AS vs Non-GAAP Adjusted EBITDA, or Consolidated vs Standalone restatements).
3. **Lack of Mutually Exclusive Sibling Outcomes:** The system lacked end-to-end verification ensuring that the four core epistemic verdicts—**Corroboration**, **Contradiction**, **Reconciliation**, and **UNRESOLVED**—operate as strictly mutually exclusive, fully audited outcomes across real multi-document filings.

Phase P2 establishes the governing principle of Layer 3:

> **No claim may enter the reasoning tournament without passing a categorical evidence sufficiency gate; and no variance may be declared a contradiction until specialist validators and adversarial critique have evaluated all structural disclosure reconciliations.**

Phase P2 implements:
1. A deterministic **Rule-Based Evidence Sufficiency Gate** (`src/decision/sufficiency.py`) replacing ad-hoc logic with transparent categorical rules.
2. Calibrated **Specialist Validators and Reconciliation Bridge** (`src/decision/validators.py`, `src/decision/reconciliation.py`) upgraded to utilize `FactIdentitySignature` attributes (`scope`, `basis`, `temporal_comparability`).
3. Validated end-to-end tournament execution across the four benchmark financial discrepancy scenarios on actual Delhivery PDF filings.

---

## 2. Requirements Coverage (SRS V2 Mapping)

The following table maps the Software Requirements Specification (SRS V2) requirements satisfied by Deliverable Phase P2:

| Requirement ID | Requirement Statement | P2 Implementation Mechanism | Target Module |
| :--- | :--- | :--- | :--- |
| **REQ-DEC-EXT-01** | Rule-Based Evidence Sufficiency Indicator | `EvidenceSufficiencyGate` evaluating identity completeness, candidate count, entailment verification, and context compatibility, routing deterministically to `ADJUDICATE`, `DEFER`, `SKIP`, or `CONTEXT_DIVERGENT`. | `src/decision/sufficiency.py`<br>`src/decision/schemas.py` |
| **REQ-DEC-EXT-03** | Core Reasoning Validation on Real Corporate Data | Calibrated reconciliation bridge triggering when at least one specialist validator confirms structural divergence without refutation; validation of the 4 benchmark outcomes on Delhivery data. | `src/decision/reconciliation.py`<br>`src/decision/validators.py`<br>`src/decision/workflow.py` |
| **REQ-LEDG-EXT-02** | Complete Decision Ledger Traceability | Extended decision traces logging sufficiency screening results, validator execution details, hypothesis rankings, and skeptic critiques. | `src/decision/engine.py`<br>`src/db/ledger.py` |

---

## 3. Scope and Architectural Deliverables

Phase P2 delivers two primary functional deliverables and complete verification across real Delhivery corporate filings:

### D-P2.1: Rule-Based Evidence Sufficiency Gate (`src/decision/sufficiency.py`)
- Categorical rule engine evaluating four sequential criteria:
  1. **Identity Completeness:** Entity canonical, metric family, subtype, measurement type, and temporal boundaries must be fully resolved. If missing -> `INSUFFICIENT_IDENTITY` (Route: fast-path `UNRESOLVED`).
  2. **Candidate Count & Source Multiplicity:** Candidate facts must number $\ge 2$ from distinct document chunks or pages. If single candidate -> `SINGLE_SOURCE_PENDING` (Route: `DEFER` to Active Acquisition / Evidence Gap Engine).
  3. **Grounding & Entailment Verification:** All candidate observations must have `ENTAILED` verification status. If unverified -> `UNVERIFIED_EVIDENCE` (Route: `SKIP`).
  4. **Context Compatibility:** Identifies whether candidate facts share matching `scope` (`Consolidated` vs `Standalone`) and `basis` (`Ind AS` vs `Non-GAAP`). If divergent -> `CONTEXT_DIVERGENT` (Route: Contextual Reconciliation Tournament - Path B).
  5. **Sufficient for Adjudication:** If all checks pass -> `SUFFICIENT_FOR_ADJUDICATION` (Route: Standard Tournament - Path A / Path C).
- Output: Structured `EvidenceSufficiencyResult` with status, action, reasoning, and missing dimensions.

### D-P2.2: Core Reasoning Tournament Calibration & Real-Data Validation
- **Specialist Validator Upgrades (`src/decision/validators.py`):**
  - Integrate `FactIdentitySignature` fields:
    - `TimingValidator`: Evaluate date intervals using Phase P1's `TemporalComparabilityClassifier`.
    - `ScopeValidator`: Check normalized `scope` from `fact_identities` (`CONSOLIDATED` vs `STANDALONE`) in addition to text keywords.
    - `AccountingBasisValidator`: Check normalized `basis` from `fact_identities` (`IND_AS`, `GAAP`, `NON_GAAP`) and detect non-GAAP metrics (Adjusted EBITDA, adjusted net profit).
    - `RestatementValidator`: Identify explicit restatement annotations and historical filing revisions.
    - `ArithmeticValidator`: Confirm exact numerical tolerances and subtotal additivity.
- **Reconciliation Bridge Calibration (`src/decision/reconciliation.py`):**
  - Trigger `ReconciliationProposal` deterministically when at least one specialist validator is `SUPPORTED` and zero validators are `REFUTED`.
  - Calculate exact `arithmetic_delta` and construct human-readable explanations citing specific source chunks.
  - Stress-test explanations using `AdversarialSkepticAgent` to ensure that ungrounded assumptions result in `UNGROUNDED` or `FALSIFIED`.
- **Workflow & Decision Engine Integration (`src/decision/workflow.py`, `src/decision/engine.py`):**
  - Incorporate `EvidenceSufficiencyGate` into tournament state machine and batch engine.
  - Ensure strict mutual exclusivity of verdicts: `CORROBORATED`, `CONTRADICTION`, `RECONCILED`, `UNRESOLVED`.
  - Validate against the four core demonstration cases using real Delhivery prospectus, annual report, and earnings presentation data.

---

## 4. Granular Component Design & Implementation Details

### 4.1 Component 1: Rule-Based Evidence Sufficiency Gate (`src/decision/sufficiency.py`)

#### Schema Extensions (`src/decision/schemas.py`)
```python
class SufficiencyStatus(str, Enum):
    """Categorical evaluation of evidentiary readiness for decision tournament."""
    SUFFICIENT_FOR_ADJUDICATION = "SUFFICIENT_FOR_ADJUDICATION"
    SINGLE_SOURCE_PENDING = "SINGLE_SOURCE_PENDING"
    INSUFFICIENT_IDENTITY = "INSUFFICIENT_IDENTITY"
    UNVERIFIED_EVIDENCE = "UNVERIFIED_EVIDENCE"
    CONTEXT_DIVERGENT = "CONTEXT_DIVERGENT"


class SufficiencyAction(str, Enum):
    """Deterministic routing action emitted by the sufficiency gate."""
    ADJUDICATE = "ADJUDICATE"
    DEFER = "DEFER"
    SKIP = "SKIP"
    RECONCILE_CONTEXT = "RECONCILE_CONTEXT"


class EvidenceSufficiencyResult(BaseModel):
    """Structured outcome of evidence sufficiency evaluation."""
    status: SufficiencyStatus
    action: SufficiencyAction
    reason: str
    missing_dimensions: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)
```

#### Gate Architecture (`src/decision/sufficiency.py`)
```text
Fact Group + Candidates + Fact Identity Signatures
                       |
                       v
[Gate 1: Identity Completeness Check]
  Are entity_canonical, metric_family, metric_subtype, and periods non-empty?
       |--- NO  --> Status: INSUFFICIENT_IDENTITY
       |            Action: SKIP -> Fast-path UNRESOLVED (Strength: INSUFFICIENT)
       v YES
[Gate 2: Candidate Multiplicity Check]
  Are there >= 2 comparable candidates from distinct windows/pages?
       |--- NO  --> Status: SINGLE_SOURCE_PENDING
       |            Action: DEFER -> Route to Evidence Gap Engine (Strength: LOW)
       v YES
[Gate 3: Grounding & Entailment Check]
  Did all candidate observations pass extraction verification (status == ENTAILED)?
       |--- NO  --> Status: UNVERIFIED_EVIDENCE
       |            Action: SKIP -> Reject unverified candidate facts
       v YES
[Gate 4: Context Compatibility Check]
  Do candidate scopes (Consolidated/Standalone) or accounting bases diverge?
       |--- YES --> Status: CONTEXT_DIVERGENT
       |            Action: RECONCILE_CONTEXT -> Route to Path B (Contextual Tournament)
       v NO
[Gate 5: Full Adjudication Readiness]
  Status: SUFFICIENT_FOR_ADJUDICATION
  Action: ADJUDICATE -> Route to Standard Pairwise Tournament (Path A / Path C)
```

---

### 4.2 Component 2: Calibrated Specialist Validators & Reconciliation Bridge

#### Upgraded Specialist Validators (`src/decision/validators.py`)
1. **`TimingValidator` Upgrade:**
   - Instead of naive tuple comparison `(p1 != p2)`, invoke `TemporalComparabilityClassifier.classify(p1, p2)`.
   - If `relation == TemporalRelation.CONTAINMENT`: output `SUPPORTED` with detail `SUB_PERIOD_CONTAINMENT` (e.g., Q4 inside FY24).
   - If `relation == TemporalRelation.ADJACENT`: output `SUPPORTED` with detail `SEQUENTIAL_PERIOD_TREND` (e.g., FY23 vs FY24).
   - If `relation == TemporalRelation.EXACT`: output `INCONCLUSIVE` (timing does not explain variance).
2. **`ScopeValidator` Upgrade:**
   - Inspect normalized `scope` attribute from `FactIdentitySignature` (`CONSOLIDATED` vs `STANDALONE`).
   - If scopes differ: output `SUPPORTED` with exact delta citation.
   - If scopes match: output `INCONCLUSIVE`.
3. **`AccountingBasisValidator` Upgrade:**
   - Inspect normalized `basis` attribute from `FactIdentitySignature` (`IND_AS`, `GAAP`, `NON_GAAP`).
   - Scan for non-GAAP disclosure indicators: `Adjusted EBITDA`, `Normalized Net Profit`, `EBITDA before share-based payments`.
   - If non-GAAP adjustment detected: output `SUPPORTED` with bridge metadata.
4. **`RestatementValidator` Upgrade:**
   - Scan for explicit restatement column headers and footnotes (`Restated Consolidated Summary Statement of Profit and Loss`).
   - Detect differences in filing vintage or audit status between earlier and later disclosures.

#### Reconciliation Bridge Calibration (`src/decision/reconciliation.py`)
- **Proposer Rule:** When `supported_validators` contains $\ge 1$ item and zero validators emit `ValidationStatus.REFUTED`:
  - Construct a structured `ReconciliationProposal` with:
    - Root cause (`SCOPE_MISMATCH`, `ACCOUNTING_BASIS`, `RESTATEMENT`, `TIMING_DIFFERENCE`).
    - Exact arithmetic delta: $|v_1 - v_2|$.
    - Evidence citations from both source chunks.
- **Skeptic Calibration:**
  - Verify that the bridge explanation cites numbers actually present in the excerpts.
  - If the bridge introduces ungrounded assumptions (e.g., guessing an unstated tax rate or unexplained operational expense), emit `SkepticStatus.UNGROUNDED`.
  - If numbers directly contradict source text, emit `SkepticStatus.FALSIFIED`.
  - If cited numbers and reconciling differences are verbatim supported, emit `SkepticStatus.SURVIVED`.

---

### 4.3 Component 3: Fact Decision Engine & Workflow Integration

#### Decision Engine Integration (`src/decision/engine.py`)
At the start of `process_fact_groups()`:
```python
sufficiency = EvidenceSufficiencyGate.evaluate(group, candidates, identities)

if sufficiency.action == SufficiencyAction.SKIP:
    # Fast-path UNRESOLVED without invoking LangGraph
    verdict = Verdict.UNRESOLVED
    strength = DecisionStrength.INSUFFICIENT
    reasoning = sufficiency.reason
elif sufficiency.action == SufficiencyAction.DEFER:
    # Single candidate awaiting second source
    verdict = Verdict.UNRESOLVED
    strength = DecisionStrength.LOW
    reasoning = sufficiency.reason
elif sufficiency.action == SufficiencyAction.RECONCILE_CONTEXT:
    # Route directly to Path B contextual reconciliation tournament
    ...
elif sufficiency.action == SufficiencyAction.ADJUDICATE:
    # Route to full pairwise tournament across candidates
    ...
```

#### Deterministic Policy Invariants (`src/decision/policy.py`)
- **Path A (Corroboration):** Numerical variance within 0.01% tolerance + identical scope and basis -> `CORROBORATED` (`HIGH` strength).
- **Path B (Reconciliation):** Numerical variance $> 0.01\%$ + supported specialist validator + skeptic `SURVIVED` -> `RECONCILED` (`HIGH` strength if arithmetic bridge present, `MEDIUM` otherwise).
- **Path C (Contradiction):** Numerical variance $> 0.01\%$ + zero supported validators or skeptic `FALSIFIED`/`UNGROUNDED` -> `CONTRADICTION` (`HIGH` strength).
- **Path D (UNRESOLVED):** Insufficient identity, single candidate, or unverified evidence -> `UNRESOLVED` (`LOW` or `INSUFFICIENT` strength).

---

## 5. Demonstration Cases on Real Delhivery Filings

Phase P2 validates the four canonical epistemic outcomes against real financial disclosures from the Delhivery prospectus, annual report, and earnings presentations:

```text
+-----------------------------------------------------------------------------------------------+
| EVIDRA 2.0 Four Canonical Demonstration Cases                                                |
+-------------------+---------------------------------------------+-----------------------------+
| Case Type         | Financial Metric / Scenario                 | Verified Outcome            |
+-------------------+---------------------------------------------+-----------------------------+
| 1. Corroboration  | Revenue from Operations (FY2021)            | Verdict: CORROBORATED       |
|                   | Prospectus Table (p.22) vs Table (p.27)     | Strength: HIGH              |
|                   | Value: 36,465.27 million INR                | Variance: 0.00%             |
+-------------------+---------------------------------------------+-----------------------------+
| 2. Contradiction  | Intragroup Eliminations / Net Adjustments   | Verdict: CONTRADICTION      |
|                   | Prospectus Table (p.22) conflicting rows    | Strength: HIGH              |
|                   | Values: -5.67 vs -4.56 vs -1.98             | Unreconciled Variance       |
+-------------------+---------------------------------------------+-----------------------------+
| 3. Reconciliation | Operating Profit vs Adjusted EBITDA (FY24)  | Verdict: RECONCILED         |
|                   | Ind AS Operating Profit vs Non-GAAP EBITDA  | Strength: HIGH              |
|                   | Reconciled via Non-GAAP Adjustment Note     | Bridge: ESOP + Amortization |
+-------------------+---------------------------------------------+-----------------------------+
| 4. UNRESOLVED     | Isolated Metric (Net Cash / Single Source)  | Verdict: UNRESOLVED         |
|                   | Awaiting independent second source filing   | Strength: LOW               |
|                   | Sufficiency: SINGLE_SOURCE_PENDING          | Audited Evidence Gap logged |
+-------------------+---------------------------------------------+-----------------------------+
```

---

## 6. Implementation Sequence and Step-by-Step Milestones

```text
Step 1: Sufficiency Schemas & EvidenceSufficiencyGate Implementation
        ├── Define SufficiencyStatus and SufficiencyAction enums in schemas.py
        ├── Implement EvidenceSufficiencyResult model
        └── Create src/decision/sufficiency.py with 4-stage evaluation logic

Step 2: Unit Testing for Evidence Sufficiency Gate
        ├── Create tests/unit/test_sufficiency.py
        └── Verify all 5 routing conditions (INSUFFICIENT_IDENTITY, SINGLE_SOURCE,
            UNVERIFIED, CONTEXT_DIVERGENT, SUFFICIENT)

Step 3: Specialist Validator Upgrades with FactIdentitySignature
        ├── Upgrade TimingValidator using TemporalComparabilityClassifier
        ├── Upgrade ScopeValidator with normalized scope attribute
        ├── Upgrade AccountingBasisValidator with Non-GAAP indicators
        └── Calibrate ReconciliationProposerAgent in src/decision/reconciliation.py

Step 4: Decision Engine & Workflow Integration
        ├── Integrate EvidenceSufficiencyGate into src/decision/engine.py
        ├── Connect sufficiency results to decision traces in SQLite ledger
        └── Ensure fast-path UNRESOLVED for single/incomplete claims

Step 5: Full Automated Regression Suite
        ├── Execute tests/unit/ (verify >= 95 unit tests)
        ├── Execute tests/contracts/ (verify 7 API tests)
        ├── Execute tests/evaluation/ (verify benchmark scenarios)
        └── Confirm 100% test pass rate across the repository

Step 6: Real-World Demonstration on Delhivery Dataset
        ├── Execute pipeline across prospectus, annual report, and earnings deck
        ├── Verify occurrence of all 4 outcomes (CORROBORATED, CONTRADICTION,
            RECONCILED, UNRESOLVED)
        └── Generate contradictions.md and summary reports for audit review
```

---

## 7. Verification and Testing Strategy

### 7.1 Automated Unit & Contract Tests
- **`tests/unit/test_sufficiency.py` [NEW]:**
  - `test_sufficiency_gate_insufficient_identity`: Rejects candidate facts missing canonical entity or metric family.
  - `test_sufficiency_gate_single_source`: Evaluates 1-candidate group, returning `SINGLE_SOURCE_PENDING` and action `DEFER`.
  - `test_sufficiency_gate_unverified_evidence`: Rejects candidates flagged as unverified or hallucinated.
  - `test_sufficiency_gate_context_divergent`: Detects Consolidated vs Standalone scope divergence, returning action `RECONCILE_CONTEXT`.
  - `test_sufficiency_gate_sufficient_adjudication`: Passes clean 2-candidate group with matching identities, returning action `ADJUDICATE`.
- **`tests/unit/test_validators_p2.py` [NEW / UPDATED]:**
  - Verify upgraded `TimingValidator` with temporal containment intervals.
  - Verify upgraded `ScopeValidator` with normalized `FactIdentitySignature` scopes.
  - Verify upgraded `AccountingBasisValidator` with Non-GAAP EBITDA reconciliations.
  - Verify `ReconciliationProposerAgent` creates valid bridge proposals when supported.
- **`tests/evaluation/test_scenarios.py`:**
  - Verify end-to-end benchmark scenarios 1 through 4 pass cleanly with updated sufficiency gate.

### 7.2 Manual Real-Data Verification Commands
```powershell
# 1. Full unit and contract test execution
pytest tests/ -v

# 2. End-to-end process on Delhivery Prospectus
python -m src.cli.main process sample_docs/01-delhivery-prospectus-2022-excerpt.pdf --max-chunks 15

# 3. Multi-document process demonstrating Corroboration and Reconciliation
python -m src.cli.main process sample_docs/01-delhivery-prospectus-2022-excerpt.pdf sample_docs/02-delhivery-annual-report-2024-excerpt.pdf sample_docs/03-delhivery-earnings-presentation-q4fy24.pdf --max-chunks 30
```

---

## 8. Risks, Architectural Invariants, and Governance

1. **Zero-LLM Decision Invariant:**
   - Verdicts (`CORROBORATED`, `CONTRADICTION`, `RECONCILED`, `UNRESOLVED`) are strictly derived by deterministic Python rules in `DecisionPolicy` and `EvidenceSufficiencyGate`. The LLM is never invoked at the decision threshold.
2. **Mutual Exclusivity Invariant:**
   - Every fact group receives exactly one primary verdict. `UNRESOLVED` is an audited, first-class epistemic status, not an unhandled exception or discarded record.
3. **Ledger Immutability:**
   - All sufficiency evaluations, validator results, reconciliation proposals, and skeptic audits are written to SQLite tables and JSONL traces with immutable run identifiers.
4. **Zero Emoji Constraint:**
   - In accordance with repository rules, no emoji characters may appear in source code, log messages, test assertions, or generated markdown reports.
