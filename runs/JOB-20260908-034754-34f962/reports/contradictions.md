# EVIDRA Contradictions and Reconciliations Audit Report

- **Job ID:** `JOB-20260908-034754-34f962`
- **Total Conflicts Detected:** 4

## Detected Discrepancies and Adjudications

### Case 1: Revenue from Services - FY23 (2022-04-01_2023-03-31)

- **Decision ID:** `DEC-590f544f`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 03-delhivery-q4-fy24-earnings-presentation.pdf | Page 6 | `(₹404) Cr / (5.6%)` | `-4040000000` | SCALED_CR | `[-1.2716666666666666e-06, -0.2000536783333473, 960.12, 543.35995]` |
| 2 | 03-delhivery-q4-fy24-earnings-presentation.pdf | Page 6 | `(₹452) Cr / (6.3%)` | `-4520000000` | SCALED_CR | `[-1.2716666666666666e-06, -0.2000536783333473, 960.12, 543.35995]` |

##### Verbatim Source Evidence Context

- **Claim 1** (03-delhivery-q4-fy24-earnings-presentation.pdf, p.6): *"| ss India’s largest integrated logistics platform (1) FY24 ₹8,142 Cr ₹127Cr / 1.6% ₹76Cr / 0.9% FY24 revenue from services EBITDA / EBITDA margin Adj. EBITDA / Adj. EBITDA marg..."*
- **Claim 2** (03-delhivery-q4-fy24-earnings-presentation.pdf, p.6): *"| ss India’s largest integrated logistics platform (1) FY24 ₹8,142 Cr ₹127Cr / 1.6% ₹76Cr / 0.9% FY24 revenue from services EBITDA / EBITDA margin Adj. EBITDA / Adj. EBITDA marg..."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `FALSIFIED`
- **Critique:** No reconciliation proposal submitted to critique.

---

### Case 2: Restated - Total (2021-04-01_2021-12-31)

- **Decision ID:** `DEC-dc0b19f5`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(987.65) ₹ million` | `987650000.00` | SCALED_MILLION INR | `[72.024, 107.89999999999992, 525.7239999999999, 297.44359679999997]` |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(567.89) ₹ million` | `567890000.00` | SCALED_MILLION INR | `[72.024, 73.43599999999998, 525.7239999999999, 262.8835967999999]` |
| 3 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(1,234.50) ₹ million` | `1234500000.00` | SCALED_MILLION INR | `[72.024, 107.89999999999992, 525.7239999999999, 297.44359679999997]` |
| 4 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(567.89) ₹ million` | `567890000.00` | SCALED_MILLION INR | `[72.024, 107.89999999999992, 525.7239999999999, 297.44359679999997]` |
| 5 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(1,234.50) ₹ million` | `1234500000.00` | SCALED_MILLION INR | `[72.024, 73.43599999999998, 525.7239999999999, 262.8835967999999]` |
| 6 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(987.65) ₹ million` | `987650000.00` | SCALED_MILLION INR | `[72.024, 73.43599999999998, 525.7239999999999, 262.8835967999999]` |

##### Verbatim Source Evidence Context

- **Claim 1** (01-delhivery-prospectus-2022-excerpt.pdf, p.27): *"| (amount in ₹ million, unless otherwise stated) |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | |  |  | Restated | ..."*
- **Claim 2** (01-delhivery-prospectus-2022-excerpt.pdf, p.28): *"| (amount in ₹ million, unless otherwise stated) |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | |  |  | Restated | ..."*
- **Claim 3** (01-delhivery-prospectus-2022-excerpt.pdf, p.27): *"| (amount in ₹ million, unless otherwise stated) |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | |  |  | Restated | ..."*
- **Claim 4** (01-delhivery-prospectus-2022-excerpt.pdf, p.27): *"| (amount in ₹ million, unless otherwise stated) |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | |  |  | Restated | ..."*
- **Claim 5** (01-delhivery-prospectus-2022-excerpt.pdf, p.28): *"| (amount in ₹ million, unless otherwise stated) |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | |  |  | Restated | ..."*
- **Claim 6** (01-delhivery-prospectus-2022-excerpt.pdf, p.28): *"| (amount in ₹ million, unless otherwise stated) |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | |  |  | Restated | ..."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `FALSIFIED`
- **Critique:** No reconciliation proposal submitted to critique.

---

### Case 3: Reporting Entity -  (2021-04-01_2021-04-01)

- **Decision ID:** `DEC-a9caf230`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(345.67)` | `-345.67` | UNIT_BASE | `[72.024, 107.89999999999992, 525.7239999999999, 297.44359679999997]` |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(456.78)` | `-456.78` | UNIT_BASE | `[72.024, 107.89999999999992, 525.7239999999999, 297.44359679999997]` |

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

### Case 4: Total income - Revenue from Operations (Undated)

- **Decision ID:** `DEC-57c1248a`
- **Verdict:** `RECONCILED`
- **Decision Strength:** `HIGH`
- **Reasoning:** Reconciled: Reporting basis difference between NON_GAAP and UNKNOWN.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 02-delhivery-annual-report-fy24-excerpt.pdf | Page 36 | `15.76` | `15.76` | UNIT_BASE | `[53.02360153198242, 355.1919250488281, 548.8419799804688, 552.8157348632812]` |
| 2 | 03-delhivery-q4-fy24-earnings-presentation.pdf | Page 17 | `(5.4%)` | `-5.4` | PERCENT | `[50.408, 80.8006923076923, 921.231846153846, 525.701]` |
| 3 | 02-delhivery-annual-report-fy24-excerpt.pdf | Page 36 | `81,415.38` | `81415.38` | UNIT_BASE | `[53.02360153198242, 355.1919250488281, 548.8419799804688, 552.8157348632812]` |

##### Verbatim Source Evidence Context

- **Claim 1** (02-delhivery-annual-report-fy24-excerpt.pdf, p.36): *"Revenue from contracts with customers 81,415.38 72,253.01 Other income 4,526.96 3,049.48 Total income 85,942.34 75,302.49 Freight, Handling and Servicing Costs 59,707.49 56,694...."*
- **Claim 2** (03-delhivery-q4-fy24-earnings-presentation.pdf, p.17): *"| ₹ Cr | Q4 FY23 | Q3 FY24 | Q4 FY24 | QoQ% | YoY% |  | FY23 | FY24 | YoY% | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | Income |  |  |  |  |  |  |  |  |  | ..."*
- **Claim 3** (02-delhivery-annual-report-fy24-excerpt.pdf, p.36): *"Revenue from contracts with customers 81,415.38 72,253.01 Other income 4,526.96 3,049.48 Total income 85,942.34 75,302.49 Freight, Handling and Servicing Costs 59,707.49 56,694...."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ACCOUNTING_BASIS | Variance arises from differing accounting standards (NON_GAAP vs UNKNOWN). | 0.80 | SUPPORTED |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.50 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `SURVIVED`
- **Critique:** Accounting standard variance explicitly verified: NON_GAAP vs UNKNOWN.

---
