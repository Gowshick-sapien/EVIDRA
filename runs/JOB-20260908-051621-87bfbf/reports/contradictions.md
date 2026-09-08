# EVIDRA Contradictions and Reconciliations Audit Report

- **Job ID:** `JOB-20260908-051621-87bfbf`
- **Total Conflicts Detected:** 4

## Detected Discrepancies and Adjudications

### Case 1: Other Expenses - % of Revenue from Contracts with Customers (2022-04-01_2023-03-31)

- **Decision ID:** `DEC-c7f0d198`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 02-delhivery-annual-report-fy24-excerpt.pdf | Page 36 | `-0.92%` | `-0.92` | PERCENT | `[896.0786743164062, 317.4962463378906, 1141.7679443359375, 413.4183044433594]` |
| 2 | 02-delhivery-annual-report-fy24-excerpt.pdf | Page 36 | `8.38%` | `8.38` | PERCENT | `[896.0786743164062, 317.4962463378906, 1141.7679443359375, 413.4183044433594]` |

##### Verbatim Source Evidence Context

- **Claim 1** (02-delhivery-annual-report-fy24-excerpt.pdf, p.36): *"Other expenses include allowances for doubtful debts, travelling and conveyance, cash management service charges, software and technology cost, and repairs and maintenance. Othe..."*
- **Claim 2** (02-delhivery-annual-report-fy24-excerpt.pdf, p.36): *"Other expenses include allowances for doubtful debts, travelling and conveyance, cash management service charges, software and technology cost, and repairs and maintenance. Othe..."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `FALSIFIED`
- **Critique:** No reconciliation proposal submitted to critique.

---

### Case 2: Total income - Revenue from Operations (Undated)

- **Decision ID:** `DEC-c610d8a2`
- **Verdict:** `RECONCILED`
- **Decision Strength:** `HIGH`
- **Reasoning:** Reconciled: Reporting basis difference between UNKNOWN and NON_GAAP.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 02-delhivery-annual-report-fy24-excerpt.pdf | Page 22 | `74,540.82` | `74540.82` | UNIT_BASE | `[53.02337646484375, 248.16851806640625, 545.6913452148438, 315.1364440917969]` |
| 2 | 02-delhivery-annual-report-fy24-excerpt.pdf | Page 36 | `81,415.38` | `81415.38` | UNIT_BASE | `[53.02360153198242, 355.1919250488281, 548.8419799804688, 552.8157348632812]` |
| 3 | 02-delhivery-annual-report-fy24-excerpt.pdf | Page 36 | `15.76` | `15.76` | UNIT_BASE | `[53.02360153198242, 355.1919250488281, 548.8419799804688, 552.8157348632812]` |

##### Verbatim Source Evidence Context

- **Claim 1** (02-delhivery-annual-report-fy24-excerpt.pdf, p.22): *"Revenue from Operations 74,540.82 66,586.61 81,415.38 72,253.01 Other Income 4,753.49 3,311.74 4,526.96 3,049.48 Total Income 79,294.31 69,898.35 85,942.34 75,302.49 Less: Total..."*
- **Claim 2** (02-delhivery-annual-report-fy24-excerpt.pdf, p.36): *"Revenue from contracts with customers 81,415.38 72,253.01 Other income 4,526.96 3,049.48 Total income 85,942.34 75,302.49 Freight, Handling and Servicing Costs 59,707.49 56,694...."*
- **Claim 3** (02-delhivery-annual-report-fy24-excerpt.pdf, p.36): *"Revenue from contracts with customers 81,415.38 72,253.01 Other income 4,526.96 3,049.48 Total income 85,942.34 75,302.49 Freight, Handling and Servicing Costs 59,707.49 56,694...."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ACCOUNTING_BASIS | Variance arises from differing accounting standards (UNKNOWN vs NON_GAAP). | 0.80 | SUPPORTED |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.50 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `SURVIVED`
- **Critique:** Accounting standard variance explicitly verified: UNKNOWN vs NON_GAAP.

---

### Case 3: Restated - Total (2021-04-01_2021-12-31)

- **Decision ID:** `DEC-415682c5`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(1,234.50) ₹ million` | `1234500000.00` | SCALED_MILLION INR | `[72.024, 107.89999999999992, 525.7239999999999, 297.44359679999997]` |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(987.65) ₹ million` | `987650000.00` | SCALED_MILLION INR | `[72.024, 107.89999999999992, 525.7239999999999, 297.44359679999997]` |
| 3 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(567.89) ₹ million` | `567890000.00` | SCALED_MILLION INR | `[72.024, 107.89999999999992, 525.7239999999999, 297.44359679999997]` |

##### Verbatim Source Evidence Context

- **Claim 1** (01-delhivery-prospectus-2022-excerpt.pdf, p.27): *"| (amount in ₹ million, unless otherwise stated) |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | |  |  | Restated | ..."*
- **Claim 2** (01-delhivery-prospectus-2022-excerpt.pdf, p.27): *"| (amount in ₹ million, unless otherwise stated) |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | |  |  | Restated | ..."*
- **Claim 3** (01-delhivery-prospectus-2022-excerpt.pdf, p.27): *"| (amount in ₹ million, unless otherwise stated) |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | |  |  | Restated | ..."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `FALSIFIED`
- **Critique:** No reconciliation proposal submitted to critique.

---

### Case 4: Restated - Total (2021-04-01_2021-04-01)

- **Decision ID:** `DEC-44008af8`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(87.65)` | `-87.65` | UNIT_BASE | `[72.024, 107.89999999999992, 525.7239999999999, 297.44359679999997]` |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(45.67)` | `-45.67` | UNIT_BASE | `[72.024, 107.89999999999992, 525.7239999999999, 297.44359679999997]` |

##### Verbatim Source Evidence Context

- **Claim 1** (01-delhivery-prospectus-2022-excerpt.pdf, p.27): *"| (amount in ₹ million, unless otherwise stated) |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | |  |  | Restated | ..."*
- **Claim 2** (01-delhivery-prospectus-2022-excerpt.pdf, p.27): *"| (amount in ₹ million, unless otherwise stated) |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | |  |  | Restated | ..."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `FALSIFIED`
- **Critique:** No reconciliation proposal submitted to critique.

---
