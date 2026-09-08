# EVIDRA Executive Summary Report

- **Job ID:** `JOB-20260908-050945-488f68`
- **Created At:** `2026-09-08T05:09:45.848204+00:00`
- **Completed At:** `2026-09-08T05:14:46.430704+00:00`
- **Status:** `PROCESSING`

## 1. Ingested Documents

| Document ID | Filename | Pages | SHA-256 Hash |
| :--- | :--- | :--- | :--- |
| DOC-001 | 01-delhivery-prospectus-2022-excerpt.pdf | 100 | `0d7e71e1766e...` |
| DOC-002 | 02-delhivery-annual-report-fy24-excerpt.pdf | 100 | `de6d79adc066...` |
| DOC-003 | 03-delhivery-q4-fy24-earnings-presentation.pdf | 27 | `5ca307085c96...` |

## 2. Pipeline Metrics

| Metric | Count | Description |
| :--- | :--- | :--- |
| Documents Processed | 3 | Total PDF source documents |
| Evidence Chunks | 6553 | Discrete text and table segments preserved with bounding boxes |
| Raw Observations | 33 | Extracted factual statements and metric claims |
| Fact Candidates | 33 | Deterministically normalized values, units, currencies, and dates |
| Fact Groups | 24 | Disputed metric clusters grouped by entity, attribute, and period |
| Decisions Evaluated | 24 | Epistemic adjudications performed by the decision engine |

## 3. Verdict Distribution

| Verdict | Count | Description |
| :--- | :--- | :--- |
| CORROBORATED | 0 | Claims independently validated across multiple sources or coherent singular facts |
| CONTRADICTION | 3 | Direct numerical or factual conflicts that could not be reconciled |
| RECONCILED | 1 | Apparent discrepancies explained by timing, restatement, or accounting scope |
| UNRESOLVED | 20 | Claims with insufficient evidence or ambiguous provenance |

## 4. Evaluated Decisions Summary

| Decision ID | Entity | Metric / Attribute | Period | Verdict | Strength |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DEC-67b3be37` | Profit/(Loss) before tax | EBITDA | Undated | **UNRESOLVED** | LOW |
| `DEC-c63e819f` | Profit/(Loss) before tax | Net Profit/Loss | Undated | **UNRESOLVED** | LOW |
| `DEC-38902a40` | Profit/(Loss) before tax | Interest Expense | Undated | **UNRESOLVED** | LOW |
| `DEC-9429c6aa` | Total income | Revenue from operations | 2023-01-01_2023-03-31 | **UNRESOLVED** | LOW |
| `DEC-5872cec2` | Total income | Non-operating income | 2023-01-01_2023-03-31 | **UNRESOLVED** | LOW |
| `DEC-e3c3604e` | Total income | Revenue from operations | 2023-10-01_2023-12-31 | **UNRESOLVED** | LOW |
| `DEC-1c1b07ab` | Revenue from Services | FY24 | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-11d87990` | EBITDA Margin | FY24 | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-d08fa13c` | Revenue from Services | FY23 | 2022-04-01_2023-03-31 | **CONTRADICTION** | HIGH |
| `DEC-87b2fdca` | Revenue from Services | YoY | Undated | **UNRESOLVED** | LOW |
| `DEC-c82838ee` | Restated | Total | 2021-04-01_2021-12-31 | **CONTRADICTION** | HIGH |
| `DEC-9b66a462` | Reporting Entity |  | 2021-08-24_2021-08-24 | **UNRESOLVED** | LOW |
| `DEC-2c7c64f1` | Reporting Entity |  | 2021-04-01_2021-04-01 | **CONTRADICTION** | HIGH |
| `DEC-716707ec` | Adjustment for Spoton Logistics Private Limited Interim Consolidated Profit and Loss for period August 24, 2021 to December 31, 2021 | Total Adjustment s | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-0eb7166e` | Intragroup elimination for period April 1, 2021 to August 23, 2021 | Total Adjustment s | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-aa7f9f74` | Acquisiti on Adjustm ents for period April 1, 2021 to August 23, 2021 | Total Adjustment s | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-7a09cd51` | EBITDA | Change in EBITDA | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-8d1da4c9` | EBITDA | Value at end of period | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-4070f06c` | EBITDA | FY24 | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-2f822c52` | PAT (Profit/Loss) | Value at end of period | 2023-10-01_2023-12-31 | **UNRESOLVED** | LOW |
| `DEC-2d2aaefa` | EBITDA | Change over time | 2022-04-01_2023-03-31 | **UNRESOLVED** | LOW |
| `DEC-2a9ca05e` | Management Commentary | Factors contributing to EBITDA improvement | Undated | **UNRESOLVED** | LOW |
| `DEC-609baaeb` | Total income | Revenue from Operations | Undated | **RECONCILED** | HIGH |
| `DEC-8d0effca` | Total income | Non-operating income | Undated | **UNRESOLVED** | LOW |
