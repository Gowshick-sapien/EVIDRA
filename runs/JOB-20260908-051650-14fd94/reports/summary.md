# EVIDRA Executive Summary Report

- **Job ID:** `JOB-20260908-051650-14fd94`
- **Created At:** `2026-09-08T05:16:50.167338+00:00`
- **Completed At:** `2026-09-08T05:52:38.537455+00:00`
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
| Fact Candidates | 40 | Deterministically normalized values, units, currencies, and dates |
| Fact Groups | 28 | Disputed metric clusters grouped by entity, attribute, and period |
| Decisions Evaluated | 28 | Epistemic adjudications performed by the decision engine |

## 3. Verdict Distribution

| Verdict | Count | Description |
| :--- | :--- | :--- |
| CORROBORATED | 3 | Claims independently validated across multiple sources or coherent singular facts |
| CONTRADICTION | 2 | Direct numerical or factual conflicts that could not be reconciled |
| RECONCILED | 0 | Apparent discrepancies explained by timing, restatement, or accounting scope |
| UNRESOLVED | 23 | Claims with insufficient evidence or ambiguous provenance |

## 4. Evaluated Decisions Summary

| Decision ID | Entity | Metric / Attribute | Period | Verdict | Strength |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DEC-749bd109` | Employee Benefits Expense | Total Expenses | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-e1f7c044` | Employee Benefits Expense | Percentage of Revenue | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-6d5bb878` | Employee Benefits Expense | Increase Reason | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-2529dc52` | Other Expenses | Amount (in crores) | 2023-04-01_2024-03-31 | **CORROBORATED** | HIGH |
| `DEC-0cc39d13` | Other Expenses | % change in amount (in percentage) | 2023-04-01_2024-03-31 | **CORROBORATED** | HIGH |
| `DEC-47848c97` | Other Expenses | % of Revenue from Contracts with Customers | 2023-04-01_2024-03-31 | **CORROBORATED** | HIGH |
| `DEC-73d1a51a` | Revenue from Operations | Total Revenues | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-802413f6` | Net Profit/Loss | Total Net Loss After Tax | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-431df5d1` | Net Profit/Loss | Total Comprehensive Loss | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-ebfc245c` | Audit | Audit Status | Undated | **UNRESOLVED** | LOW |
| `DEC-3eeddc8f` | Restated | Total | 2021-04-01_2021-04-01 | **CONTRADICTION** | HIGH |
| `DEC-1d749e91` | Revenue | Revenue from Contracts with Customers | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-95180657` | EBITDA | Earnings Before Interest, Taxes, Depreciation and Amortization | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-8817671d` | Adjusted EBITDA | Adjusted Earnings Before Interest, Taxes, Depreciation and Amortization | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-e5e21e93` | Loss | Net Profit/Loss | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-93472fb6` | Customer Base | Number of Active Customers | Undated | **UNRESOLVED** | LOW |
| `DEC-bdc0988d` | Total income (I) | 48,105.30 | Undated | **UNRESOLVED** | LOW |
| `DEC-ac69f81d` | Total income (I) | 1,917.64 | Undated | **UNRESOLVED** | LOW |
| `DEC-f697db03` | Total Income (I) | Revenue from Operations | Undated | **UNRESOLVED** | LOW |
| `DEC-c5282c27` | Total Income (I) | Other income | Undated | **UNRESOLVED** | LOW |
| `DEC-d70965ad` | Revenue from contract with customers | Total income (I) | Undated | **UNRESOLVED** | LOW |
| `DEC-8498ac53` | Other income | Total income (I) | Undated | **UNRESOLVED** | LOW |
| `DEC-85936781` | 3,019.35 million | Amount of Investment in Associates | Undated | **UNRESOLVED** | LOW |
| `DEC-8322e357` | 40.98% | Extent of Holding | Undated | **UNRESOLVED** | LOW |
| `DEC-be0310e4` | 39.34% | Extent of Holding | Undated | **UNRESOLVED** | LOW |
| `DEC-7c59bfdc` | Reporting Entity |  | Undated | **UNRESOLVED** | LOW |
| `DEC-71f5ca90` | Restated | Total | 2021-04-01_2021-12-31 | **CONTRADICTION** | HIGH |
| `DEC-b5b7e15e` | Restated | Total | 2021-08-24_2021-08-24 | **UNRESOLVED** | LOW |
