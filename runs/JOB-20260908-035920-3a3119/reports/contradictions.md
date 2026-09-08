# EVIDRA Contradictions and Reconciliations Audit Report

- **Job ID:** `JOB-20260908-035920-3a3119`
- **Total Conflicts Detected:** 2

## Detected Discrepancies and Adjudications

### Case 1: Restated - Total (2021-04-01_2021-12-31)

- **Decision ID:** `DEC-897edc6d`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(1,234.50) ₹ million` | `1234500000.00` | SCALED_MILLION INR |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(987.65) ₹ million` | `987650000.00` | SCALED_MILLION INR |
| 3 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(1,234.50) ₹ million` | `1234500000.00` | SCALED_MILLION INR |
| 4 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(567.89) ₹ million` | `567890000.00` | SCALED_MILLION INR |
| 5 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(567.89) ₹ million` | `567890000.00` | SCALED_MILLION INR |
| 6 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 27 | `(987.65) ₹ million` | `987650000.00` | SCALED_MILLION INR |

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

---

### Case 2: Reporting Entity -  (2021-04-01_2021-04-01)

- **Decision ID:** `DEC-5f16691d`
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
