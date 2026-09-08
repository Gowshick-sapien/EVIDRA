# EVIDRA Contradictions and Reconciliations Audit Report

- **Job ID:** `JOB-20260908-130025-29b35d`
- **Total Conflicts Detected:** 1

## Detected Discrepancies and Adjudications

### Case 1: Delhivery Limited - RESTATED_CONSOLIDATED_SUMMARY_STATEMENT_OF_PROFIT_AND_LOSS_OF_DELHIVERY_LIMITED_FOR_THE_YEAR_ENDED_MARCH_31_2021 (2021-04-01_2022-03-31)

- **Decision ID:** `DEC-f206d276`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Conflicting claim clusters identified: [-1.98 UNIT_BASE (1 sources), -4.56 UNIT_BASE (1 sources), -5.67 UNIT_BASE (1 sources)]. Direct numerical variance without reconciling disclosure.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 22 | `-1.98` | `-1.98` | UNIT_BASE | `[72.024, 192.5896, 523.444, 340.4979973333333]` |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 22 | `-4.56` | `-4.56` | UNIT_BASE | `[72.024, 192.5896, 523.444, 340.4979973333333]` |
| 3 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 22 | `-5.67` | `-5.67` | UNIT_BASE | `[72.024, 192.5896, 523.444, 340.4979973333333]` |

##### Verbatim Source Evidence Context

- **Claim 1** (01-delhivery-prospectus-2022-excerpt.pdf, p.22): *"|  |  | Restated Consolidated Summary Statement of Profit and Loss of Delhivery Limited for the year ended March 31, 2021 |  |  |  | Spoton |  | Intragroup elimin ation |  |  | ..."*
- **Claim 2** (01-delhivery-prospectus-2022-excerpt.pdf, p.22): *"|  |  | Restated Consolidated Summary Statement of Profit and Loss of Delhivery Limited for the year ended March 31, 2021 |  |  |  | Spoton |  | Intragroup elimin ation |  |  | ..."*
- **Claim 3** (01-delhivery-prospectus-2022-excerpt.pdf, p.22): *"|  |  | Restated Consolidated Summary Statement of Profit and Loss of Delhivery Limited for the year ended March 31, 2021 |  |  |  | Spoton |  | Intragroup elimin ation |  |  | ..."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `FALSIFIED`
- **Critique:** No reconciliation proposal submitted to critique.

---
