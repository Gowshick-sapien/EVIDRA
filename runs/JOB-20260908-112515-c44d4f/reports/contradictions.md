# EVIDRA Contradictions and Reconciliations Audit Report

- **Job ID:** `JOB-20260908-112515-c44d4f`
- **Total Conflicts Detected:** 8

## Detected Discrepancies and Adjudications

### Case 1: Delhivery Limited - Express parcel orders (Q3-Q4 FY21) (2021-04-01_2021-12-31)

- **Decision ID:** `DEC-a6bfa25e`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 55 | `438,795 tonnes million` | `438795000000` | SCALED_MILLION | `[72.02400207519531, 476.83563232421875, 525.8096923828125, 763.8873291015625]` |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 55 | `406.51 million` | `406510000.00` | SCALED_MILLION | `[72.02400207519531, 476.83563232421875, 525.8096923828125, 763.8873291015625]` |

##### Verbatim Source Evidence Context

- **Claim 1** (01-delhivery-prospectus-2022-excerpt.pdf, p.55): *"We were the largest and fastest growing fully-integrated logistics services player in India by revenue as of Fiscal 2021, according to the RedSeer Report, which has been exclusi..."*
- **Claim 2** (01-delhivery-prospectus-2022-excerpt.pdf, p.55): *"We were the largest and fastest growing fully-integrated logistics services player in India by revenue as of Fiscal 2021, according to the RedSeer Report, which has been exclusi..."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `FALSIFIED`
- **Critique:** No reconciliation proposal submitted to critique.

---

### Case 2: Delhivery Limited - revenue from contracts with customers (in crores) (2020-04-01_2021-03-31)

- **Decision ID:** `DEC-b955bf84`
- **Verdict:** `RECONCILED`
- **Decision Strength:** `HIGH`
- **Reasoning:** Reconciled: Reporting basis difference between UNKNOWN and NON_GAAP.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 55 | `₹36,465.27 million` | `36465270000.00` | SCALED_MILLION | `[72.02400207519531, 476.83563232421875, 525.8096923828125, 763.8873291015625]` |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 44 | `16,538.97` | `16538.97` | UNIT_BASE | `[74.54399871826172, 528.9309692382812, 522.1848754882812, 750.9926147460938]` |
| 3 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 44 | `16,538.97 million INR` | `16538970000.00` | SCALED_MILLION INR | `[74.54399871826172, 528.9309692382812, 522.1848754882812, 750.9926147460938]` |

##### Verbatim Source Evidence Context

- **Claim 1** (01-delhivery-prospectus-2022-excerpt.pdf, p.55): *"We were the largest and fastest growing fully-integrated logistics services player in India by revenue as of Fiscal 2021, according to the RedSeer Report, which has been exclusi..."*
- **Claim 2** (01-delhivery-prospectus-2022-excerpt.pdf, p.44): *"2021 PIN code reach 13,485 15,875 16,677 17,488 Infrastructure (in million square feet) 5.96 9.85 12.23 14.27 No. of gateways 73 83 88 82 Rated Automated Sort Capacity   (in mil..."*
- **Claim 3** (01-delhivery-prospectus-2022-excerpt.pdf, p.44): *"2021 PIN code reach 13,485 15,875 16,677 17,488 Infrastructure (in million square feet) 5.96 9.85 12.23 14.27 No. of gateways 73 83 88 82 Rated Automated Sort Capacity   (in mil..."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ACCOUNTING_BASIS | Variance arises from differing accounting standards (UNKNOWN vs NON_GAAP). | 0.80 | SUPPORTED |
| SCOPE_MISMATCH | Variance stems from entity scope variation (SEGMENT parent entity vs UNKNOWN group figures). | 0.80 | SUPPORTED |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.50 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `SURVIVED`
- **Critique:** Accounting standard variance explicitly verified: UNKNOWN vs NON_GAAP.

---

### Case 3: Delhivery Limited - Express parcel orders (FY21) (2020-04-01_2021-03-31)

- **Decision ID:** `DEC-6e240025`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 55 | `289.20 million` | `289200000.00` | SCALED_MILLION | `[72.02400207519531, 476.83563232421875, 525.8096923828125, 763.8873291015625]` |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 55 | `47.37 million` | `47370000.00` | SCALED_MILLION | `[72.02400207519531, 476.83563232421875, 525.8096923828125, 763.8873291015625]` |

##### Verbatim Source Evidence Context

- **Claim 1** (01-delhivery-prospectus-2022-excerpt.pdf, p.55): *"We were the largest and fastest growing fully-integrated logistics services player in India by revenue as of Fiscal 2021, according to the RedSeer Report, which has been exclusi..."*
- **Claim 2** (01-delhivery-prospectus-2022-excerpt.pdf, p.55): *"We were the largest and fastest growing fully-integrated logistics services player in India by revenue as of Fiscal 2021, according to the RedSeer Report, which has been exclusi..."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `FALSIFIED`
- **Critique:** No reconciliation proposal submitted to critique.

---

### Case 4: Delhivery Limited - PTL freight (FY21) (2020-04-01_2021-03-31)

- **Decision ID:** `DEC-6a18721c`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 55 | `46,878 million` | `46878000000` | SCALED_MILLION | `[72.02400207519531, 476.83563232421875, 525.8096923828125, 763.8873291015625]` |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 55 | `373,854 tonnes million` | `373854000000` | SCALED_MILLION | `[72.02400207519531, 476.83563232421875, 525.8096923828125, 763.8873291015625]` |

##### Verbatim Source Evidence Context

- **Claim 1** (01-delhivery-prospectus-2022-excerpt.pdf, p.55): *"We were the largest and fastest growing fully-integrated logistics services player in India by revenue as of Fiscal 2021, according to the RedSeer Report, which has been exclusi..."*
- **Claim 2** (01-delhivery-prospectus-2022-excerpt.pdf, p.55): *"We were the largest and fastest growing fully-integrated logistics services player in India by revenue as of Fiscal 2021, according to the RedSeer Report, which has been exclusi..."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `FALSIFIED`
- **Critique:** No reconciliation proposal submitted to critique.

---

### Case 5: Delhivery Limited - Consolidated Assets (2021-03-31_2021-03-31)

- **Decision ID:** `DEC-bd1e95dd`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 25 | `(B) million INR` | `(B) million INR` | INR | `[50.664, 105.70727272727271, 562.0799999999999, 215.21272409090906]` |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 25 | `(A) million INR` | `(A) million INR` | INR | `[50.664, 105.70727272727271, 562.0799999999999, 215.21272409090906]` |
| 3 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 25 | `(A)` | `(A)` |  | `[50.664, 105.70727272727271, 562.0799999999999, 215.21272409090906]` |
| 4 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 25 | `(F)` | `(F)` |  | `[50.664, 105.70727272727271, 562.0799999999999, 215.21272409090906]` |
| 5 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 25 | `(B)` | `(B)` |  | `[50.664, 105.70727272727271, 562.0799999999999, 215.21272409090906]` |

##### Verbatim Source Evidence Context

- **Claim 1** (01-delhivery-prospectus-2022-excerpt.pdf, p.25): *"|  |  |  |  | Restated |  | Spoton Logistics Private Limited Special Purpose Consolidated Balance Sheet as at March 31, 2021 | Intragroup elimin ation | Acquisition Adjustments ..."*
- **Claim 2** (01-delhivery-prospectus-2022-excerpt.pdf, p.25): *"|  |  |  |  | Restated |  | Spoton Logistics Private Limited Special Purpose Consolidated Balance Sheet as at March 31, 2021 | Intragroup elimin ation | Acquisition Adjustments ..."*
- **Claim 3** (01-delhivery-prospectus-2022-excerpt.pdf, p.25): *"|  |  |  |  | Restated |  | Spoton Logistics Private Limited Special Purpose Consolidated Balance Sheet as at March 31, 2021 | Intragroup elimin ation | Acquisition Adjustments ..."*
- **Claim 4** (01-delhivery-prospectus-2022-excerpt.pdf, p.25): *"|  |  |  |  | Restated |  | Spoton Logistics Private Limited Special Purpose Consolidated Balance Sheet as at March 31, 2021 | Intragroup elimin ation | Acquisition Adjustments ..."*
- **Claim 5** (01-delhivery-prospectus-2022-excerpt.pdf, p.25): *"|  |  |  |  | Restated |  | Spoton Logistics Private Limited Special Purpose Consolidated Balance Sheet as at March 31, 2021 | Intragroup elimin ation | Acquisition Adjustments ..."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `FALSIFIED`
- **Critique:** No reconciliation proposal submitted to critique.

---

### Case 6: Delhivery Limited - Restated Consolidated Summary Statement of Profit and Loss of Delhivery Limited for the year ended March 31, 2021 (2021-04-01_2022-03-31)

- **Decision ID:** `DEC-02aaad35`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 22 | `-4.56` | `-4.56` | UNIT_BASE | `[72.024, 192.5896, 523.444, 340.4979973333333]` |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 22 | `-5.67` | `-5.67` | UNIT_BASE | `[72.024, 192.5896, 523.444, 340.4979973333333]` |
| 3 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 22 | `-1.98` | `-1.98` | UNIT_BASE | `[72.024, 192.5896, 523.444, 340.4979973333333]` |

##### Verbatim Source Evidence Context

- **Claim 1** (01-delhivery-prospectus-2022-excerpt.pdf, p.22): *"|  |  | Restated Consolidated Summary Statement of Profit and Loss of Delhivery Limited for the year ended March 31, 2021 |  |  |  | Spoton |  | Intragroup elimin ation |  |  | ..."*
- **Claim 2** (01-delhivery-prospectus-2022-excerpt.pdf, p.22): *"|  |  | Restated Consolidated Summary Statement of Profit and Loss of Delhivery Limited for the year ended March 31, 2021 |  |  |  | Spoton |  | Intragroup elimin ation |  |  | ..."*
- **Claim 3** (01-delhivery-prospectus-2022-excerpt.pdf, p.22): *"|  |  | Restated Consolidated Summary Statement of Profit and Loss of Delhivery Limited for the year ended March 31, 2021 |  |  |  | Spoton |  | Intragroup elimin ation |  |  | ..."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `FALSIFIED`
- **Critique:** No reconciliation proposal submitted to critique.

---

### Case 7: Spoton Logistics Private Limited - Intragroup elimination for period April 1, 2021 to August 23, 2021 (2021-04-01_2021-12-31)

- **Decision ID:** `DEC-dc1da038`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 28 | `(4.5%)` | `-4.5` | PERCENT | `[72.024, 73.43599999999998, 525.7239999999999, 262.8835967999999]` |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 29 | `(567.89) million INR` | `567890000.00` | SCALED_MILLION INR | `[72.024, 73.43599999999998, 525.7239999999999, 262.8835967999999]` |

##### Verbatim Source Evidence Context

- **Claim 1** (01-delhivery-prospectus-2022-excerpt.pdf, p.28): *"| (amount in ₹ million, unless otherwise stated) |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | |  |  | Restated | ..."*
- **Claim 2** (01-delhivery-prospectus-2022-excerpt.pdf, p.29): *"| (amount in ₹ million, unless otherwise stated) |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | |  |  | Restated | ..."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `FALSIFIED`
- **Critique:** No reconciliation proposal submitted to critique.

---

### Case 8: Delhivery Limited - Restated Consolidated Summary Statement of Profit and Loss of Delhivery Limited for the year ended March 31, 2021 (2020-04-01_2021-03-31)

- **Decision ID:** `DEC-13466921`
- **Verdict:** `CONTRADICTION`
- **Decision Strength:** `HIGH`
- **Reasoning:** Material numerical variance under identical reporting context where all reconciliation hypotheses were refuted.

#### Competing Fact Claims

| # | Source Document | Page | Stated Value | Normalized Value | Unit / Currency | Coordinates [x0, y0, x1, y1] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 24 | `(Note: Spoton is a special purpose entity)` | `(Note: Spoton is a special purpose entity)` |  | `[72.024, 86.18959999999996, 523.444, 221.09359999999992]` |
| 2 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 23 | `(Note: Spoton is a subsidiary)` | `(Note: Spoton is a subsidiary)` |  | `[72.024, 86.18959999999996, 523.444, 221.09359999999992]` |
| 3 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 24 | `(Note: Acquisition adjustments are made to account for changes in fair value or other factors related to acquisitions)` | `(Note: Acquisition adjustments are made to account for changes in fair value or other factors related to acquisitions)` |  | `[72.024, 86.18959999999996, 523.444, 221.09359999999992]` |
| 4 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 23 | `(Note: Intragroup eliminations are not included in consolidated statements)` | `(Note: Intragroup eliminations are not included in consolidated statements)` |  | `[72.024, 86.18959999999996, 523.444, 221.09359999999992]` |
| 5 | 01-delhivery-prospectus-2022-excerpt.pdf | Page 24 | `(Note: Intragroup eliminations are adjustments made to remove intercompany transactions)` | `(Note: Intragroup eliminations are adjustments made to remove intercompany transactions)` |  | `[72.024, 86.18959999999996, 523.444, 221.09359999999992]` |

##### Verbatim Source Evidence Context

- **Claim 1** (01-delhivery-prospectus-2022-excerpt.pdf, p.24): *"|  |  | Restated Consolidated Summary Statement of Profit and Loss of Delhivery Limited for the year ended March 31, 2021 |  | Spoton |  | Intragroup elimin ation | Acquisition ..."*
- **Claim 2** (01-delhivery-prospectus-2022-excerpt.pdf, p.23): *"|  |  | Restated Consolidated Summary Statement of Profit and Loss of Delhivery Limited for the year ended March 31, 2021 |  | Spoton |  | Intragroup elimin ation | Acquisition ..."*
- **Claim 3** (01-delhivery-prospectus-2022-excerpt.pdf, p.24): *"|  |  | Restated Consolidated Summary Statement of Profit and Loss of Delhivery Limited for the year ended March 31, 2021 |  | Spoton |  | Intragroup elimin ation | Acquisition ..."*
- **Claim 4** (01-delhivery-prospectus-2022-excerpt.pdf, p.23): *"|  |  | Restated Consolidated Summary Statement of Profit and Loss of Delhivery Limited for the year ended March 31, 2021 |  | Spoton |  | Intragroup elimin ation | Acquisition ..."*
- **Claim 5** (01-delhivery-prospectus-2022-excerpt.pdf, p.24): *"|  |  | Restated Consolidated Summary Statement of Profit and Loss of Delhivery Limited for the year ended March 31, 2021 |  | Spoton |  | Intragroup elimin ation | Acquisition ..."*

#### Hypotheses Evaluated

| Class | Description | Likelihood | Status |
| :--- | :--- | :--- | :--- |
| ERRONEOUS_CONTRADICTION | Figures represent mutually incompatible claims with no valid accounting reconciliation. | 0.75 | EVALUATED |

#### Adversarial Skeptic Audit

- **Status:** `FALSIFIED`
- **Critique:** No reconciliation proposal submitted to critique.

---
