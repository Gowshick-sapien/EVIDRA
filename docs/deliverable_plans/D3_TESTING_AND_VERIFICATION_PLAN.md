# EVIDRA: Evidence-Driven Architecture for Fact Validation and Knowledge Reasoning

## Deliverable 3 (D3) Testing and Verification Plan: Verification, Context, and Normalization Layer

---

## 1. Testing Philosophy and Numerical Precision Mandate

Deliverable 3 (**D3**) represents the epistemological foundation of **EVIDRA** (Layer 2b), responsible for bridging raw, unverified observations into audited, normalized, and semantically grouped fact candidates.

Quality assurance for D3 enforces four strict mandates:
1. **Mathematical Precision & Zero Float Drift:** Floating-point arithmetic is strictly prohibited in financial value comparisons. All monetary units, Indian numbering denominations (Crores, Lakhs, Arabs), Western denominations (Millions, Billions, Thousands), and accounting notations (bracketed negatives, percentages) must normalize to exact Python `Decimal` instances.
2. **Deterministic Temporal Anchoring:** Free-form financial period descriptions (fiscal years, quarters, partial trailing periods, calendar years) must resolve deterministically into discrete ISO 8601 interval tuples `(period_start, period_end)`.
3. **Adversarial Claim-to-Chunk Entailment:** Before any observation is admitted as a fact candidate, an adversarial verification agent validates whether the claim is strictly entailed by the underlying chunk content. Ungrounded figures or assertions are marked `HALLUCINATED`.
4. **Two-Tier Fact Grouping:** Financial attributes describing identical economic metrics within the same temporal window must cluster into unified `FactGroup` entities using hard temporal/entity blocking combined with dense semantic embedding similarity (`BAAI/bge-small-en-v1.5` cosine similarity >= 0.82).

---

## 2. Automated Test Suites (39 Passing Tests)

The complete automated test suite contains 39 tests across 10 test modules, running under strict asyncio and pytest modes.

### 2.1 Numerical and Denomination Normalization (`tests/unit/test_decimal_units.py`)
* **Target Module:** [src/verification/normalizers.py](file:///d:/projects/superjoin/EVIDRA/src/verification/normalizers.py)
* **Execution Command:**
  ```powershell
  pytest tests/unit/test_decimal_units.py -v
  ```
* **Coverage Scope:**
  * `test_indian_numbering_system`: Verifies scaling of Crores (`10^7`), Lakhs (`10^5`), and Arabs (`10^9`) to exact `Decimal` values.
  * `test_western_numbering_system`: Verifies scaling of Millions (`10^6`), Billions (`10^9`), and Thousands (`10^3`).
  * `test_bracketed_negatives_and_percentages`: Tests conversion of accounting bracket notation `(4,810.50)` to negative decimals `-4810.50` and percentage scaling.
  * `test_exact_decimal_arithmetic_no_float_drift`: Confirms `0.1 + 0.2 == 0.3` without IEEE 754 floating-point drift.
  * `test_currency_normalization`: Validates ISO 4217 currency mapping for INR, USD, EUR, GBP.

### 2.2 Temporal Scope Normalization (`tests/unit/test_temporal_parsing.py`)
* **Target Module:** [src/verification/normalizers.py](file:///d:/projects/superjoin/EVIDRA/src/verification/normalizers.py)
* **Execution Command:**
  ```powershell
  pytest tests/unit/test_temporal_parsing.py -v
  ```
* **Coverage Scope:**
  * `test_fiscal_year_standard`: Verifies Indian fiscal year boundaries (`FY22` -> `2021-04-01` to `2022-03-31`).
  * `test_fiscal_quarter_parsing`: Verifies quarterly boundaries (`Q1 FY24`, `Q2 FY2023`, `Q4 FY21`).
  * `test_calendar_year_parsing`: Verifies calendar year intervals (`Cal 2022`, `CY 2021`).
  * `test_partial_period_parsing`: Verifies multi-month disclosures (`Nine months ended Dec 31, 2021`).
  * `test_fallback_handling`: Validates deterministic fallback intervals for undated metrics (`1970-01-01`).

### 2.3 Verification, Context Resolution, and Semantic Grouping (`tests/unit/test_verification.py`)
* **Target Modules:** [src/verification/verifier.py](file:///d:/projects/superjoin/EVIDRA/src/verification/verifier.py), [src/verification/context.py](file:///d:/projects/superjoin/EVIDRA/src/verification/context.py), [src/matching/embeddings.py](file:///d:/projects/superjoin/EVIDRA/src/matching/embeddings.py), [src/verification/pipeline.py](file:///d:/projects/superjoin/EVIDRA/src/verification/pipeline.py)
* **Execution Command:**
  ```powershell
  pytest tests/unit/test_verification.py -v
  ```
* **Coverage Scope:**
  * `test_context_resolver_deterministic`: Verifies extraction of accounting basis (`IFRS`, `US_GAAP`, `NON_GAAP`), organizational scope (`CONSOLIDATED`, `STANDALONE`), filing type (`PROSPECTUS`, `ANNUAL_REPORT`), and version status (`RESTATED`).
  * `test_evidence_verifier_entailed`: Confirms that grounded observations produce `ENTAILED` verdicts.
  * `test_evidence_verifier_hallucinated`: Confirms that contradictory or fabricated figures produce `HALLUCINATED` verdicts.
  * `test_fact_group_engine_semantic_clustering`: Validates that synonymous attributes ("Revenue from operations" and "Operating Revenue") cluster into a unified `FactGroup` with 2 members.
  * `test_verification_pipeline_end_to_end`: Validates end-to-end processing of ledger observations into `fact_candidates`, `fact_groups`, and `group_members`.

### 2.4 Complete Regression Test Suite
* **Execution Command:**
  ```powershell
  pytest tests/ -v
  ```
* **Results:**
  ```text
  collected 39 items

  tests\contracts\test_api.py .....                                        [ 12%]
  tests\unit\test_cli.py ....                                              [ 23%]
  tests\unit\test_decimal_units.py .....                                   [ 35%]
  tests\unit\test_extraction.py ...                                        [ 43%]
  tests\unit\test_ledger.py .....                                          [ 56%]
  tests\unit\test_llm.py ..                                                [ 61%]
  tests\unit\test_pdf.py ...                                               [ 69%]
  tests\unit\test_temporal_parsing.py .....                                [ 82%]
  tests\unit\test_trace.py ..                                              [ 87%]
  tests\unit\test_verification.py .....                                    [100%]

  ======================= 39 passed, 3 warnings in 26.35s =======================
  ```

---

## 3. Turnkey Audit Verification Script (`scripts/verify_d3.py`)

A dedicated verification script [scripts/verify_d3.py](file:///d:/projects/superjoin/EVIDRA/scripts/verify_d3.py) provides standalone diagnostic validation of the entire D3 pipeline:

* **Execution Command:**
  ```powershell
  python scripts/verify_d3.py
  ```
* **Output:**
  ```text
  ==================================================
    EVIDRA D3 Verification and Normalization Audit  
  ==================================================

  [1/4] Testing Decimal & Multiplier Normalization...
        PASS: 'INR 6,882.29 million' -> 6882290000.00 INR
        PASS: 'Rs. 450.50 Crores' -> 4505000000.00 INR
        PASS: 'Rs. (125.40 Lakhs)' -> -12540000.00 INR
        PASS: 'USD 1.25 Billion' -> 1250000000.00 USD
        PASS: 'EUR (50.00)' -> -50.00 EUR

  [2/4] Testing Temporal Scope ISO 8601 Normalization...
        PASS: 'FY22' -> [2021-04-01 to 2022-03-31]
        PASS: 'FY2023' -> [2022-04-01 to 2023-03-31]
        PASS: 'Q1 FY24' -> [2023-04-01 to 2023-06-30]
        PASS: 'Nine months ended Dec 31, 2021' -> [2021-04-01 to 2021-12-31]
        PASS: 'Cal 2022' -> [2022-01-01 to 2022-12-31]

  [3/4] Testing Context Resolution Deterministic Engine...
        PASS: Scope=CONSOLIDATED, Basis=IFRS, Type=PROSPECTUS, Version=RESTATED

  [4/4] Testing FactGroup Semantic Grouping Engine...
        PASS: Clustered 3 candidates into 2 groups (synonymous attributes merged)

  [5/5] Inspecting SQLite Ledger Run Records...
        Inspecting: ledger.db in JOB-20260907-191318-f7be96
        - Evidence Chunks: 1461
        - Observations:    1
        - Fact Candidates: 1
        - Fact Groups:     1
        PASS: Ledger schema, Fact Candidates, and Fact Groups verified.

  ==================================================
  ALL DELIVERABLE 3 (D3) VERIFICATION CHECKS PASSED
  ==================================================
  ```

---

## 4. Real-World Document CLI Run Verification

The complete ingestion and extraction CLI command was executed against the primary test document:
```powershell
python -m src.cli.main process sample_docs/01-delhivery-prospectus-2022-excerpt.pdf --max-chunks 2
```

### 4.1 CLI Output Summary Table
```text
============================================================
  EVIDRA Fact Knowledge Layer - Job Summary
============================================================
  Job ID:            JOB-20260907-191318-f7be96
  Run Directory:     runs\JOB-20260907-191318-f7be96
  Documents Ingested:1
  Evidence Chunks:   1461
  Observations:      1
  Fact Candidates:   1
  Fact Groups:       1
  Decisions Made:    0
------------------------------------------------------------
  Corroborated:      0
  Contradictions:    0
  Reconciled:        0
  Unresolved:        0
============================================================
```

### 4.2 SQLite Ledger Direct Audit
Inspection of `runs/JOB-20260907-191318-f7be96/ledger.db` confirms relational integrity:
* **Observations:** `OBS-SEM-8515e55a` stored with `provenance_status='ENTAILED'`.
* **Fact Candidates:** `FCT-bfd25afe` mapped to observation `OBS-SEM-8515e55a`, with exact normalized strings and temporal bounds.
* **Fact Groups:** `GRP-7e2da3c1` created with `member_count=1`.
* **Group Members:** Relational mapping linking `GRP-7e2da3c1` -> `FCT-bfd25afe`.

---

## 5. Deliverable D3 Execution Verification Matrix

| Component | Target Artifact | Requirement Verified | Verification Method | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Decimal Normalizer** | `src/verification/normalizers.py` | Exact Python `Decimal` across Indian & Western units | `tests/unit/test_decimal_units.py` | **PASSED** |
| **Temporal Normalizer** | `src/verification/normalizers.py` | Discrete ISO 8601 interval tuples for financial periods | `tests/unit/test_temporal_parsing.py` | **PASSED** |
| **Currency Normalizer** | `src/verification/normalizers.py` | ISO 4217 standard currency mapping | `tests/unit/test_decimal_units.py` | **PASSED** |
| **Verifier Agent** | `src/verification/verifier.py` | Adversarial claim-to-chunk entailment detection | `tests/unit/test_verification.py` | **PASSED** |
| **Context Resolver** | `src/verification/context.py` | GAAP/Non-GAAP, Consolidated/Standalone, Filing qualifiers | `tests/unit/test_verification.py` | **PASSED** |
| **Fact Group Engine** | `src/matching/embeddings.py` | Hard temporal blocking + BGE embedding clustering | `tests/unit/test_verification.py` | **PASSED** |
| **Verification Pipeline** | `src/verification/pipeline.py` | End-to-end ledger integration | `scripts/verify_d3.py` & CLI execution | **PASSED** |
| **Regression Suite** | Entire Test Suite | 39 unit, contract, and integration tests | `pytest tests/ -v` | **PASSED** |
