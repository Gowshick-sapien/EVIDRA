# EVIDRA Executive Summary Report

- **Job ID:** `JOB-20260908-051621-87bfbf`
- **Created At:** `2026-09-08T05:16:21.145581+00:00`
- **Completed At:** `2026-09-08T05:52:47.310792+00:00`
- **Status:** `PROCESSING`

## 1. Ingested Documents

| Document ID | Filename | Pages | SHA-256 Hash |
| :--- | :--- | :--- | :--- |
| DOC-001 | 01-delhivery-prospectus-2022-excerpt.pdf | 100 | `0d7e71e1766e...` |
| DOC-002 | 02-delhivery-annual-report-fy24-excerpt.pdf | 100 | `de6d79adc066...` |

## 2. Pipeline Metrics

| Metric | Count | Description |
| :--- | :--- | :--- |
| Documents Processed | 2 | Total PDF source documents |
| Evidence Chunks | 6280 | Discrete text and table segments preserved with bounding boxes |
| Raw Observations | 43 | Extracted factual statements and metric claims |
| Fact Candidates | 43 | Deterministically normalized values, units, currencies, and dates |
| Fact Groups | 36 | Disputed metric clusters grouped by entity, attribute, and period |
| Decisions Evaluated | 36 | Epistemic adjudications performed by the decision engine |

## 3. Verdict Distribution

| Verdict | Count | Description |
| :--- | :--- | :--- |
| CORROBORATED | 1 | Claims independently validated across multiple sources or coherent singular facts |
| CONTRADICTION | 3 | Direct numerical or factual conflicts that could not be reconciled |
| RECONCILED | 1 | Apparent discrepancies explained by timing, restatement, or accounting scope |
| UNRESOLVED | 31 | Claims with insufficient evidence or ambiguous provenance |

## 4. Evaluated Decisions Summary

| Decision ID | Entity | Metric / Attribute | Period | Verdict | Strength |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DEC-49d42871` | 3,019.35 million | Amount of Investment in Associates | Undated | **UNRESOLVED** | LOW |
| `DEC-ca7baa94` | 40.98% | Extent of Holding | Undated | **UNRESOLVED** | LOW |
| `DEC-a89eb78b` | 39.34% | Extent of Holding | Undated | **UNRESOLVED** | LOW |
| `DEC-03707053` | Reason why the associate is not consolidated | Reason why the associate is not consolidated | Undated | **UNRESOLVED** | LOW |
| `DEC-f11e2457` | Other Expenses | Amount (in crores) | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-cc3d3680` | Other Expenses | % of Revenue from Contracts with Customers | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-c7f0d198` | Other Expenses | % of Revenue from Contracts with Customers | 2022-04-01_2023-03-31 | **CONTRADICTION** | HIGH |
| `DEC-0b84d44c` | Revenue from contract with customers | Total income (I) | Undated | **UNRESOLVED** | LOW |
| `DEC-eeeed654` | Other income | Total income (I) | Undated | **UNRESOLVED** | LOW |
| `DEC-7f6bed4f` | EBITDA | Change in EBITDA | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-ae05dddf` | EBITDA | Value at end of period | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-10366c05` | PAT (Profit/Loss) | Value at end of period | 2023-10-01_2023-12-31 | **UNRESOLVED** | LOW |
| `DEC-35b2576e` | EBITDA | Change over time | 2022-04-01_2023-03-31 | **UNRESOLVED** | LOW |
| `DEC-34b6c002` | Management Commentary | Factors contributing to EBITDA improvement | Undated | **UNRESOLVED** | LOW |
| `DEC-c610d8a2` | Total income | Revenue from Operations | Undated | **RECONCILED** | HIGH |
| `DEC-e4a00cea` | Total Income | Other Income | Undated | **UNRESOLVED** | LOW |
| `DEC-bb7d877b` | Total Income | Net Profit/Loss | Undated | **UNRESOLVED** | LOW |
| `DEC-b882afb7` | Total Income | Loss before exceptional items, share of profit of an associate and tax | Undated | **UNRESOLVED** | LOW |
| `DEC-ee2478cd` | Profit/(Loss) before tax | EBITDA | Undated | **UNRESOLVED** | LOW |
| `DEC-095f7013` | Profit/(Loss) before tax | Net Profit/Loss | Undated | **UNRESOLVED** | LOW |
| `DEC-5e516986` | Profit/(Loss) before tax | Interest Expense | Undated | **UNRESOLVED** | LOW |
| `DEC-cf10e63b` | Total Assets | As of FY23 | 2022-04-01_2023-03-31 | **UNRESOLVED** | LOW |
| `DEC-905473fd` | Net Profit/Loss | For FY24 | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-eb1ccdbc` | Net Profit/Loss | For FY24 compared to FY23 | 2022-04-01_2023-03-31 | **CORROBORATED** | HIGH |
| `DEC-358de72e` | Total Assets | For FY23 compared to FY22 | 2021-04-01_2022-03-31 | **UNRESOLVED** | LOW |
| `DEC-a720ea01` | Revenue from Operations for FY24 | Total Revenue | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-4c22a0fb` | Revenue from Operations for FY23 | Total Revenue | 2022-04-01_2023-03-31 | **UNRESOLVED** | LOW |
| `DEC-debec8ac` | Net Profit/Loss for FY24 | Loss from Operations | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-ff10f878` | Net Profit/Loss for FY23 | Loss from Operations | 2022-04-01_2023-03-31 | **UNRESOLVED** | LOW |
| `DEC-8cfd905c` | Revenue from Operations for FY24 compared to FY23 | Growth Rate | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-001a568d` | Loss from Operations for FY24 compared to FY23 | Reduction Rate | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-415682c5` | Restated | Total | 2021-04-01_2021-12-31 | **CONTRADICTION** | HIGH |
| `DEC-b2f333a4` | Restated | Total | 2021-08-24_2021-08-24 | **UNRESOLVED** | LOW |
| `DEC-44008af8` | Restated | Total | 2021-04-01_2021-04-01 | **CONTRADICTION** | HIGH |
| `DEC-a40f53a5` | Total income (I) | 48,105.30 | Undated | **UNRESOLVED** | LOW |
| `DEC-b498f38f` | Total income (I) | 1,917.64 | Undated | **UNRESOLVED** | LOW |
