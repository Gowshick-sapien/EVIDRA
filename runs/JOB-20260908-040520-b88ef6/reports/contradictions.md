# EVIDRA Contradictions and Reconciliations Audit Report

- **Job ID:** `JOB-20260908-040520-b88ef6`
- **Total Conflicts Detected:** 3

## Detected Discrepancies and Adjudications

### Case 1: Revenue from Services - FY23 (2022-04-01_2023-03-31)

- **Decision ID:** `DEC-f0f54944`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 03-delhivery-q4-fy24-earnings-presentation.pdf | Page 6 | `(₹404) Cr / (5.6%)` | `-4040000000` | SCALED_CR |
| 2 | 03-delhivery-q4-fy24-earnings-presentation.pdf | Page 6 | `(₹452) Cr / (6.3%)` | `-4520000000` | SCALED_CR |

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

---

### Case 2: Restated - Total (2021-04-01_2021-12-31)

- **Decision ID:** `DEC-1a7a01db`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(156.78)` | `-156.78` | UNIT_BASE |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(89.76)` | `-89.76` | UNIT_BASE |
| 3 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(567.89) ₹ million` | `567890000.00` | SCALED_MILLION INR |
| 4 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(45.67)` | `-45.67` | UNIT_BASE |
| 5 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(1,234.50) ₹ million` | `1234500000.00` | SCALED_MILLION INR |
| 6 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(987.65) ₹ million` | `987650000.00` | SCALED_MILLION INR |

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

---

### Case 3: Total income - Revenue from Operations (Undated)

- **Decision ID:** `DEC-730a57c8`
- **Verdict:** `RECONCILED`
- **Decision Strength:** `HIGH`
- **Reasoning:** Reconciled: Reporting basis difference between NON_GAAP and UNKNOWN.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 02-delhivery-annual-report-fy24-excerpt.pdf | Page 36 | `81,415.38` | `81415.38` | UNIT_BASE |
| 2 | 03-delhivery-q4-fy24-earnings-presentation.pdf | Page 17 | `(5.4%)` | `-5.4` | PERCENT |
| 3 | 02-delhivery-annual-report-fy24-excerpt.pdf | Page 36 | `15.76` | `15.76` | UNIT_BASE |

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ACCOUNTING_BASIS | Variance arises from differing accounting standards (NON_GAAP vs UNKNOWN). | 0.80 | SUPPORTED |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.50 | EVALUATED |

---
