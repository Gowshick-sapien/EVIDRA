# EVIDRA Contradictions and Reconciliations Audit Report

- **Job ID:** `JOB-20260908-033558-efe832`
- **Total Conflicts Detected:** 4

## Detected Discrepancies and Adjudications

### Case 1: Total income - Revenue from Operations (Undated)

- **Decision ID:** `DEC-7f68f69d`
- **Verdict:** `RECONCILED`
- **Decision Strength:** `HIGH`
- **Reasoning:** Reconciled: Reporting basis difference between UNKNOWN and NON_GAAP.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 03-delhivery-q4-fy24-earnings-presentation.pdf | Page 17 | `(5.4%)` | `-5.4` | PERCENT |
| 2 | 02-delhivery-annual-report-fy24-excerpt.pdf | Page 36 | `15.76` | `15.76` | UNIT_BASE |
| 3 | 02-delhivery-annual-report-fy24-excerpt.pdf | Page 36 | `81,415.38` | `81415.38` | UNIT_BASE |

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ACCOUNTING_BASIS | Variance arises from differing accounting standards (UNKNOWN vs NON_GAAP). | 0.80 | SUPPORTED |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.50 | EVALUATED |

---

### Case 2: Revenue from Services - FY23 (2022-04-01_2023-03-31)

- **Decision ID:** `DEC-e79437b5`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 03-delhivery-q4-fy24-earnings-presentation.pdf | Page 6 | `(₹404) Cr / (5.6%)` | `-404` | PERCENT |
| 2 | 03-delhivery-q4-fy24-earnings-presentation.pdf | Page 6 | `(₹452) Cr / (6.3%)` | `-452` | PERCENT |

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

---

### Case 3: Restated - Total (2021-04-01_2021-12-31)

- **Decision ID:** `DEC-a0decfcb`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(567.89) ₹ million` | `567890000.00` | SCALED_MILLION INR |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(987.65) ₹ million` | `987650000.00` | SCALED_MILLION INR |
| 3 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(567.89) ₹ million` | `567890000.00` | SCALED_MILLION INR |
| 4 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(1,234.50) ₹ million` | `1234500000.00` | SCALED_MILLION INR |
| 5 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(1,234.50) ₹ million` | `1234500000.00` | SCALED_MILLION INR |
| 6 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(987.65) ₹ million` | `987650000.00` | SCALED_MILLION INR |

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

---

### Case 4: Reporting Entity -  (2021-04-01_2021-04-01)

- **Decision ID:** `DEC-77e622dd`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(456.78)` | `-456.78` | UNIT_BASE |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(345.67)` | `-345.67` | UNIT_BASE |

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

---
