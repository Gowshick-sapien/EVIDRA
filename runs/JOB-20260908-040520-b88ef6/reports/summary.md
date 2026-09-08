# EVIDRA Executive Summary Report

- **Job ID:** `JOB-20260908-040520-b88ef6`
- **Created At:** `2026-09-08T04:05:20.658835+00:00`
- **Completed At:** `2026-09-08T04:09:58.253960+00:00`
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
| Raw Observations | 27 | Extracted factual statements and metric claims |
| Fact Candidates | 27 | Deterministically normalized values, units, currencies, and dates |
| Fact Groups | 19 | Disputed metric clusters grouped by entity, attribute, and period |
| Decisions Evaluated | 19 | Epistemic adjudications performed by the decision engine |

## 3. Verdict Distribution

| Verdict | Count | Description |
| :--- | :--- | :--- |
| CORROBORATED | 0 | Claims independently validated across multiple sources or coherent singular facts |
| CONTRADICTION | 2 | Direct numerical or factual conflicts that could not be reconciled |
| RECONCILED | 1 | Apparent discrepancies explained by timing, restatement, or accounting scope |
| UNRESOLVED | 16 | Claims with insufficient evidence or ambiguous provenance |

## 4. Evaluated Decisions Summary

| Decision ID | Entity | Metric / Attribute | Period | Verdict | Strength |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DEC-91925856` | Total income | Revenue from operations | 2023-10-01_2023-12-31 | **UNRESOLVED** | LOW |
| `DEC-cf667f93` | Revenue from Services | FY24 | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-41af92ba` | EBITDA Margin | FY24 | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-f0f54944` | Revenue from Services | FY23 | 2022-04-01_2023-03-31 | **CONTRADICTION** | HIGH |
| `DEC-11808fb7` | Revenue from Services | YoY | Undated | **UNRESOLVED** | LOW |
| `DEC-1a7a01db` | Restated | Total | 2021-04-01_2021-12-31 | **CONTRADICTION** | HIGH |
| `DEC-c3386925` | EBITDA | Change in EBITDA | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-28a4fa7a` | EBITDA | Value at end of period | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-61e46ac1` | EBITDA | FY24 | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-bcc36b0a` | PAT (Profit/Loss) | Value at end of period | 2023-10-01_2023-12-31 | **UNRESOLVED** | LOW |
| `DEC-085dba1f` | EBITDA | Change over time | 2022-04-01_2023-03-31 | **UNRESOLVED** | LOW |
| `DEC-6ac743d5` | Management Commentary | Factors contributing to EBITDA improvement | Undated | **UNRESOLVED** | LOW |
| `DEC-730a57c8` | Total income | Revenue from Operations | Undated | **RECONCILED** | HIGH |
| `DEC-8c85569d` | Total income | Non-operating income | Undated | **UNRESOLVED** | LOW |
| `DEC-2cca58df` | Profit/(Loss) before tax | EBITDA | Undated | **UNRESOLVED** | LOW |
| `DEC-521dcbb2` | Profit/(Loss) before tax | Net Profit/Loss | Undated | **UNRESOLVED** | LOW |
| `DEC-383df6a8` | Profit/(Loss) before tax | Interest Expense | Undated | **UNRESOLVED** | LOW |
| `DEC-c515ea8f` | Total income | Revenue from operations | 2023-01-01_2023-03-31 | **UNRESOLVED** | LOW |
| `DEC-d9aa4537` | Total income | Non-operating income | 2023-01-01_2023-03-31 | **UNRESOLVED** | LOW |
