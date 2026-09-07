# EVIDRA: Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning

## Deliverable 4 (D4) Implementation Plan: Decision Engine, LangGraph Reconciliation State Machine, and Audit Tracing

---

## 1. Executive Overview and Epistemic Objective

Deliverable 4 (**D4**) implements the epistemic reasoning and adjudication core of **EVIDRA** (Layer 3).

In Deliverables 1 through 3, the engine prepared physical coordinates, extracted verified observations, normalized monetary quantities into exact Python `Decimal` instances, extracted context dimensions, and clustered synonymous financial attributes into `FactGroup` entities.

Deliverable 4 addresses the central question of financial document reconciliation:
**"How do facts across documents relate -- do they corroborate, contradict, or can they be reconciled?"**

Financial reconciliation cannot rely on naive text similarity or unrestricted generative LLM responses. Generating unconstrained verdicts via prompts leads to sycophancy, hallucinated reconciliations, and arbitrary variance tolerance. To guarantee mathematical and legal rigor, D4 enforces four core principles:
1. **Three Adaptive Decision Paths:** High-volume identical claims bypass LLM inference entirely via pure Python arithmetic (Path A: Deterministic Corroboration). Apparent differences caused by stated contextual parameters route directly to targeted context validators (Path B: Contextual Resolution). Genuine conflicts trigger a multi-agent debate (Path C: Conflict Debate).
2. **Hypothesis Tournament:** When values disagree, the system formulates structured, falsifiable hypotheses spanning five financial variance classes: `RESTATEMENT`, `ACCOUNTING_BASIS`, `SCOPE_MISMATCH`, `TIMING_DIFFERENCE`, and `ERRONEOUS_CONTRADICTION`.
3. **Adversarial Reconciliation Protocol:** A Reconciliation Proposer formulates an explicit explanation bridge, which is then subjected to attack by an isolated Adversarial Skeptic probing for missing evidence, unstated assumptions, or arithmetic discrepancies.
4. **Deterministic Decision Policy Truth Tables:** Final verdicts (**CORROBORATED**, **CONTRADICTION**, **RECONCILED**, **UNRESOLVED**) and categorical confidence ratings (**HIGH**, **MEDIUM**, **LOW**, **INSUFFICIENT**) are determined exclusively by pure Python truth tables. Zero LLM calls occur at the decision gate.

---

## 2. Scope and Boundaries of Deliverable 4

### 2.1 In-Scope Deliverables
* **D4.1: Epistemic State Models and Schema Definitions (`src/decision/schemas.py`):**
  * Pydantic state models for LangGraph execution (`FactDecisionState`, `FactGroupContext`, `VarianceMetrics`).
  * Enums for categorical verdicts (`Verdict`), confidence strength (`DecisionStrength`), hypothesis classes (`HypothesisClass`), validation statuses (`ValidationStatus`), and skeptic verdicts (`SkepticStatus`).
* **D4.2: Specialist Validators (`src/decision/validators.py`):**
  * `ArithmeticValidator`: Pure Python `Decimal` delta calculation, tolerance checks (0.01%), and percentage variance calculation.
  * `RestatementValidator`: Validates subsequent audit adjustments, amended filings, and explicit restatement disclosures.
  * `AccountingBasisValidator`: Verifies GAAP-to-Non-GAAP reconciliation bridge tables, stock-based compensation exclusions, and accounting standard differences (e.g. Ind AS vs US GAAP).
  * `ScopeValidator`: Evaluates legal entity hierarchies (Consolidated group vs Standalone parent entity) and segment disclosures.
  * `TimingValidator`: Evaluates differences arising from calendar quarters vs fiscal month-ends.
* **D4.3: Hypothesis Tournament Generator (`src/decision/hypothesis.py`):**
  * Structured agent formulating candidate explanations for detected numerical or semantic variance.
* **D4.4: Reconciliation Proposer & Adversarial Skeptic (`src/decision/reconciliation.py`):**
  * `ReconciliationProposerAgent`: Synthesizes supported validator findings into an explicit reconciliation bridge.
  * `AdversarialSkepticAgent`: Evaluates the candidate bridge against raw evidence chunks, emitting `SURVIVED`, `FALSIFIED`, or `UNGROUNDED`.
* **D4.5: Deterministic Decision Policy Engine (`src/decision/policy.py`):**
  * Pure Python truth tables mapping validator results, variance metrics, and skeptic outcomes to final categorical verdicts.
  * Defensive fail-safe: defaults unconditionally to `UNRESOLVED` on ambiguity or error.
* **D4.6: LangGraph Reconciliation Workflow Orchestrator (`src/decision/workflow.py`):**
  * StateGraph orchestrating the adaptive paths, state transitions, and error boundaries.
  * Persists `hypotheses`, `validator_results`, `decisions`, and `decision_traces` into the SQLite `ledger.db`.
* **D4.7: CLI and End-to-End Execution (`src/cli/main.py`, `src/decision/engine.py`):**
  * CLI integration enabling automated adjudication during `process` and detailed review during `inspect`.

### 2.2 Out-of-Scope (Deferred to D5)
* Executive Markdown Summary and Contradiction Report generators (`docs/reports/` - Deliverable 5).
* Cross-document benchmark evaluations across synthetic challenge sets and SEC 10-K filings (Deliverable 5).

---

## 3. Requirements Coverage (SRS & NFR Mapping)

### 3.1 Functional Requirements (FR)
* **FR-DEC-01 (Adaptive Decision Paths):** System must route fact groups through Deterministic Corroboration, Contextual Resolution, or Conflict Debate based on variance and context qualifiers.
* **FR-DEC-02 (Pure Python Arithmetic Tolerance):** Value comparisons must utilize Python `Decimal` with a configurable tolerance (default 0.01%).
* **FR-DEC-03 (Hypothesis Tournament):** System must evaluate candidate variance across Restatements, Accounting Bases, Scope Variations, and Timing Differences.
* **FR-DEC-04 (Adversarial Skepticism):** Reconciliations must survive adversarial critique against original source chunks; ungrounded reconciliations must be falsified.
* **FR-DEC-05 (Deterministic Decision Policy):** Final verdicts must be emitted by deterministic Python truth tables, never by an LLM prompt.
* **FR-DEC-06 (Decision Card Generation):** System must populate complete Decision Cards containing entity, attribute, period, verdict, confidence, candidate claims, and audit trace.

### 3.2 Non-Functional Requirements (NFR)
* **NFR-DET-01 (Determinism):** Identical fact candidates and context must produce identical verdicts and reasoning across runs.
* **NFR-LAT-01 (Inference Efficiency):** Path A decisions must execute in under 10 milliseconds without invoking external LLMs.
* **NFR-REL-01 (Relational Integrity):** All decision records must enforce foreign key integrity with `fact_groups` and cascade properly.
* **NFR-AUD-01 (Step-by-Step Auditability):** Every node in the LangGraph workflow must log execution time, inputs, and outputs to `decision_traces`.

---

## 4. Architecture and Pipeline Flow

### 4.1 Layer 3 LangGraph Decision Workflow

```
                        Input FactGroup from Ledger
                                    |
                                    v
                       [ Node 1: Variance Analyzer ]
                                    |
                 +------------------+------------------+
                 |                                     |
        [ Variance <= 0.01% &                 [ Variance > 0.01% or
         Matching Context ]                    Context Mismatch ]
                 |                                     |
                 v (Path A)                            v
      [ Path A: Corroboration ]              [ Node 2: Context Router ]
                 |                                     |
                 |                         +-----------+-----------+
                 |                         |                       |
                 |                 [ Stated Context        [ Context Appears
                 |                    Difference ]             Identical ]
                 |                         |                       |
                 |                         v (Path B)              v (Path C)
                 |                [ Specialist Context     [ Node 3: Hypothesis
                 |                    Validators ]              Tournament ]
                 |                         |                       |
                 |                         |                       v
                 |                         |              [ Node 4: Specialist
                 |                         |                  Validators ]
                 |                         |                       |
                 |                         |                       v
                 |                         |              [ Node 5: Reconciliation
                 |                         |                     Proposer ]
                 |                         |                       |
                 |                         |                       v
                 |                         |              [ Node 6: Adversarial
                 |                         |                     Skeptic ]
                 |                         |                       |
                 +-------------------------+-----------------------+
                                           |
                                           v
                       [ Node 7: Decision Policy Engine ]
                         (Pure Python Truth Tables)
                                           |
                  +------------------------+-----------------------+
                  |                        |                       |
                  v                        v                       v
            CORROBORATED             RECONCILED               CONTRADICTION
                                           |
                                           +-------> UNRESOLVED (Fallback)
                                           |
                                           v
                      [ Node 8: Ledger Persistence & Trace ]
                        (SQLite Transaction: decisions,
                         hypotheses, validator_results,
                                decision_traces)
```

---

## 5. Software Architecture of D4 Components

### 5.1 State Models and Epistemic Enums (`src/decision/schemas.py`)
Defines the Pydantic models governing state progression through LangGraph:
* `Verdict`: Enum `['CORROBORATED', 'CONTRADICTION', 'RECONCILED', 'UNRESOLVED']`.
* `DecisionStrength`: Enum `['HIGH', 'MEDIUM', 'LOW', 'INSUFFICIENT']`.
* `HypothesisClass`: Enum `['RESTATEMENT', 'ACCOUNTING_BASIS', 'SCOPE_MISMATCH', 'TIMING_DIFFERENCE', 'ERRONEOUS_CONTRADICTION']`.
* `ValidationStatus`: Enum `['SUPPORTED', 'REFUTED', 'INCONCLUSIVE']`.
* `SkepticStatus`: Enum `['SURVIVED', 'FALSIFIED', 'UNGROUNDED']`.
* `CandidateFactView`: Lightweight projection of candidate facts including normalized decimal value, unit, currency, period start/end, and source chunk content.
* `FactDecisionState`: The TypedDict / Pydantic model maintaining immutable state across graph nodes:
  * `group_id`: str
  * `entity`: str
  * `attribute`: str
  * `period_id`: str
  * `candidates`: list[CandidateFactView]
  * `variance_pct`: Optional[Decimal]
  * `hypotheses`: list[HypothesisRecord]
  * `validator_results`: list[ValidatorResultRecord]
  * `reconciliation_proposal`: Optional[str]
  * `skeptic_critique`: Optional[SkepticOutcome]
  * `verdict`: Optional[Verdict]
  * `decision_strength`: Optional[DecisionStrength]
  * `reasoning_summary`: Optional[str]
  * `traces`: list[dict[str, Any]]

### 5.2 Specialist Validators (`src/decision/validators.py`)
Specialized evaluation modules executing targeted verification:
* **`ArithmeticValidator`**:
  * Calculates `delta = abs(val1 - val2)`.
  * Computes percentage variance `abs(val1 - val2) / max(abs(val1), abs(val2))`.
  * Evaluates equality within tolerance ($\le 0.0001$).
* **`RestatementValidator`**:
  * Inspects candidate metadata for `version_status == 'RESTATED'`.
  * Checks source chunk text for keywords: `"restated"`, `"as restated"`, `"retrospectively adjusted"`, `"amended"`.
  * If one candidate is Restated and the other is As-Reported for the same period, emits `SUPPORTED`.
* **`AccountingBasisValidator`**:
  * Compares accounting basis dimensions (`IFRS` / `IND_AS` vs `US_GAAP` vs `NON_GAAP`).
  * Scans chunks for reconciliation bridge terminology (`"EBITDA"`, `"Adjusted EBITDA"`, `"stock-based compensation"`, `"depreciation and amortization"`).
* **`ScopeValidator`**:
  * Compares organizational scope (`CONSOLIDATED` vs `STANDALONE`).
  * Checks if differing figures correspond to the parent company entity vs group entity.
* **`TimingValidator`**:
  * Compares exact `(period_start, period_end)` tuples.
  * Detects partial period mismatches (e.g., 9 months vs 12 months) or calendar vs fiscal year offsets.

### 5.3 Hypothesis Tournament Agent (`src/decision/hypothesis.py`)
* Operates when numerical variance exceeds tolerance.
* Evaluates differences in candidate values and available text chunks.
* Emits candidate hypotheses with initial likelihood priors.

### 5.4 Reconciliation Proposer & Adversarial Skeptic (`src/decision/reconciliation.py`)
* **`ReconciliationProposerAgent`**:
  * Synthesizes findings from supported validators into a structured reconciliation bridge explanation.
  * Formulates: (a) root cause of discrepancy, (b) reconciling arithmetic or qualitative bridge, (c) source citations.
* **`AdversarialSkepticAgent`**:
  * Evaluates whether the proposed bridge is directly supported by the source document text or if it relies on unstated assumptions.
  * Emits `SURVIVED` if explicit text or math confirms the explanation; `FALSIFIED` if contradicted; `UNGROUNDED` if assumed without proof.

### 5.5 Deterministic Decision Policy Truth Tables (`src/decision/policy.py`)
The decision engine policy is implemented as pure Python deterministic logic without LLM calls:
```python
class DecisionPolicy:
    TOLERANCE = Decimal("0.0001")  # 0.01%

    @classmethod
    def evaluate(cls, state: FactDecisionState) -> tuple[Verdict, DecisionStrength, str]:
        # Rule 1: Corroboration (Path A)
        if state.is_numerically_equal(cls.TOLERANCE) and state.has_matching_context():
            return Verdict.CORROBORATED, DecisionStrength.HIGH, "Values match within 0.01% under identical entity, period, and scope."

        # Rule 2: Reconciled (Path B / Path C)
        if state.skeptic_status == SkepticStatus.SURVIVED and state.has_supported_reconciliation():
            strength = DecisionStrength.HIGH if state.has_explicit_bridge_math() else DecisionStrength.MEDIUM
            return Verdict.RECONCILED, strength, state.reconciliation_summary

        # Rule 3: Contradiction (Path C)
        if state.has_matching_context() and (
            state.skeptic_status == SkepticStatus.FALSIFIED
            or state.all_reconciliations_refuted()
        ):
            return Verdict.CONTRADICTION, DecisionStrength.HIGH, "Material numerical variance with identical context where all reconciliation hypotheses were refuted."

        # Rule 4: Default Fallback (Fail-Safe)
        return Verdict.UNRESOLVED, DecisionStrength.INSUFFICIENT, "Insufficient evidence or ambiguous context prevented definitive reconciliation."
```

### 5.6 LangGraph Workflow Orchestrator (`src/decision/workflow.py`)
* Implements the `StateGraph(FactDecisionState)`.
* Defines nodes: `analyze_variance`, `evaluate_corroboration`, `route_context`, `generate_hypotheses`, `run_validators`, `propose_reconciliation`, `critique_reconciliation`, `apply_policy`, `persist_decision`.
* Compiles the runnable graph with cycle-free conditional edges.
* Attaches tracing callbacks streaming to `TraceLogger`.

### 5.7 Decision Coordinator (`src/decision/engine.py`)
* Coordinates execution across all unadjudicated `fact_groups` in the SQLite database.
* Connects with `EvidenceLedger` to persist final decisions and traces.

---

## 6. Detailed Implementation Steps

```
+-----------------------------------------------------------------------------------+
|                           D4 IMPLEMENTATION TIMELINE                              |
+-----------------------------------------------------------------------------------+
| Phase 1: Schemas & Epistemic State Models       | src/decision/schemas.py         |
| Phase 2: Specialist Validators                  | src/decision/validators.py      |
| Phase 3: Hypothesis & Reconciliation Agents     | src/decision/hypothesis.py,     |
|                                                 | src/decision/reconciliation.py  |
| Phase 4: Deterministic Decision Policy          | src/decision/policy.py          |
| Phase 5: LangGraph Workflow & Orchestration     | src/decision/workflow.py,       |
|                                                 | src/decision/engine.py          |
| Phase 6: CLI & Pipeline Integration             | src/cli/main.py,                |
|                                                 | src/extraction/pipeline.py      |
| Phase 7: Automated Tests & Verification Script  | tests/unit/test_decision.py,    |
|                                                 | scripts/verify_d4.py            |
+-----------------------------------------------------------------------------------+
```

### Phase 1: State Schemas and Enums (`src/decision/schemas.py`)
* Implement all Pydantic models, TypedDicts, and Enums.
* Ensure serialization compatibility with SQLite schema for `hypotheses`, `validator_results`, `decisions`, and `decision_traces`.

### Phase 2: Specialist Validators (`src/decision/validators.py`)
* Implement `ArithmeticValidator` with pure Python `Decimal`.
* Implement `RestatementValidator` for version and text checking.
* Implement `AccountingBasisValidator` for GAAP / Non-GAAP reconciliation detection.
* Implement `ScopeValidator` for Consolidated vs Standalone detection.
* Implement `TimingValidator` for interval comparison.

### Phase 3: Hypothesis Tournament & Reconciliation Agents (`src/decision/hypothesis.py`, `src/decision/reconciliation.py`)
* Build `HypothesisGeneratorAgent` with structured Pydantic response models.
* Build `ReconciliationProposerAgent` synthesizing supported validator results.
* Build `AdversarialSkepticAgent` evaluating proposed reconciliations against raw chunk text.

### Phase 4: Deterministic Policy Engine (`src/decision/policy.py`)
* Implement pure Python decision truth tables.
* Implement confidence strength calculation rules.
* Implement defensive fallback assigning `UNRESOLVED` to any unhandled or erroneous condition.

### Phase 5: LangGraph State Machine (`src/decision/workflow.py`, `src/decision/engine.py`)
* Build and compile the `StateGraph` using `langgraph.graph`.
* Wire node functions and conditional branch routers.
* Implement batch evaluation coordinator querying `fact_groups` and writing back to `decisions` and `decision_traces`.

### Phase 6: Pipeline and CLI Integration (`src/extraction/pipeline.py`, `src/cli/main.py`)
* Update `ExtractionPipeline` to invoke `FactDecisionEngine` after `VerificationPipeline`.
* Enhance `evidra inspect <job_id>` CLI command to print formatted Decision Cards including claims, hypotheses, validator outcomes, and skeptic critiques.

### Phase 7: Verification and Testing
* Write unit test suite `tests/unit/test_decision.py` testing:
  * Path A Corroboration (< 0.01% variance).
  * Path B Contextual Resolution (Restated vs As-Reported -> RECONCILED).
  * Path C Contradiction (Irreconcilable variance with identical context -> CONTRADICTION).
  * Skeptic Falsification (Ungrounded reconciliation rejected -> CONTRADICTION or UNRESOLVED).
  * Defensive Fail-Safe (Missing data -> UNRESOLVED).
* Create turnkey audit script `scripts/verify_d4.py`.
* Execute end-to-end run on the Delhivery prospectus and review decision outputs.

---

## 7. Verification and Testing Strategy

### 7.1 Automated Unit and Contract Test Suites
* **`tests/unit/test_decision.py`**:
  * `test_arithmetic_tolerance_corroboration`: Tests numerical matching within 0.01% tolerance.
  * `test_restatement_validator_supported`: Tests recognition of restated financial figures.
  * `test_accounting_basis_validator`: Tests GAAP vs Non-GAAP variance detection.
  * `test_scope_validator`: Tests Standalone vs Consolidated detection.
  * `test_adversarial_skeptic_falsification`: Tests rejection of ungrounded reconciliation claims.
  * `test_deterministic_policy_truth_table`: Exhaustively evaluates all rows of the policy truth table.
  * `test_langgraph_workflow_end_to_end`: Executes the compiled state graph on simulated fact groups.

### 7.2 Real-World Document CLI Verification
* Process sample financial filing and run:
  ```powershell
  python -m src.cli.main process sample_docs/01-delhivery-prospectus-2022-excerpt.pdf --max-chunks 3
  ```
* Run inspection command:
  ```powershell
  python -m src.cli.main inspect <job_id>
  ```
* Execute standalone diagnostic script:
  ```powershell
  python scripts/verify_d4.py
  ```

---

## 8. Acceptance Criteria and Sign-off Checklist

- [ ] `src/decision/schemas.py` defines all epistemic enums, Pydantic state models, and views.
- [ ] `src/decision/validators.py` implements all 5 specialist validators using exact `Decimal` arithmetic.
- [ ] `src/decision/hypothesis.py` implements structured hypothesis generation across the 5 variance classes.
- [ ] `src/decision/reconciliation.py` implements proposer and adversarial skeptic agents with explicit citation enforcement.
- [ ] `src/decision/policy.py` implements 100% deterministic decision truth tables with zero LLM calls.
- [ ] `src/decision/workflow.py` compiles a LangGraph `StateGraph` without infinite loops or unbounded transitions.
- [ ] SQLite ledger persistence writes records to `hypotheses`, `validator_results`, `decisions`, and `decision_traces`.
- [ ] `evidra inspect` CLI command renders complete Decision Cards.
- [ ] All automated unit tests in `tests/unit/test_decision.py` pass.
- [ ] Entire test suite (`pytest tests/ -v`) passes with a 100% pass rate.
- [ ] `scripts/verify_d4.py` completes with all checks passing.
- [ ] Absolutely no emojis present in code, documentation, or CLI outputs.
