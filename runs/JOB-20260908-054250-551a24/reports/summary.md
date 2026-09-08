# EVIDRA Executive Summary Report

- **Job ID:** `JOB-20260908-054250-551a24`
- **Created At:** `2026-09-08T05:42:50.825996+00:00`
- **Completed At:** `2026-09-08T05:50:10.472906+00:00`
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
| Raw Observations | 37 | Extracted factual statements and metric claims |
| Fact Candidates | 37 | Deterministically normalized values, units, currencies, and dates |
| Fact Groups | 20 | Disputed metric clusters grouped by entity, attribute, and period |
| Decisions Evaluated | 20 | Epistemic adjudications performed by the decision engine |

## 3. Verdict Distribution

| Verdict | Count | Description |
| :--- | :--- | :--- |
| CORROBORATED | 2 | Claims independently validated across multiple sources or coherent singular facts |
| CONTRADICTION | 5 | Direct numerical or factual conflicts that could not be reconciled |
| RECONCILED | 0 | Apparent discrepancies explained by timing, restatement, or accounting scope |
| UNRESOLVED | 13 | Claims with insufficient evidence or ambiguous provenance |

## 4. Evaluated Decisions Summary

| Decision ID | Entity | Metric / Attribute | Period | Verdict | Strength |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DEC-f3f11984` | Revenue from Services | FY24 | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-76fe0e4a` | EBITDA Margin | FY24 | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-83c140a6` | Revenue from Services | FY23 | 2022-04-01_2023-03-31 | **UNRESOLVED** | LOW |
| `DEC-49e00f54` | EBITDA Margin | FY23 | 2022-04-01_2023-03-31 | **UNRESOLVED** | LOW |
| `DEC-115e3307` | Reporting Entity |  | Undated | **CONTRADICTION** | HIGH |
| `DEC-82a77fdc` | Reporting Entity |  | 2023-04-01_2024-03-31 | **CONTRADICTION** | HIGH |
| `DEC-40240a2d` | Restated | Total | 2021-04-01_2021-12-31 | **CONTRADICTION** | HIGH |
| `DEC-39cc587b` | Restated | Total | 2021-08-24_2021-08-24 | **UNRESOLVED** | LOW |
| `DEC-e55f34b1` | Restated | Total | 2021-04-01_2021-04-01 | **CONTRADICTION** | HIGH |
| `DEC-8bfec45c` | EBITDA | Change in Value | 2022-04-01_2023-03-31 | **CORROBORATED** | HIGH |
| `DEC-6d1ad17b` | EBITDA | Value at End Period | 2023-04-01_2024-03-31 | **CORROBORATED** | HIGH |
| `DEC-e017b4f7` | EBITDA | FY24 | 2023-04-01_2024-03-31 | **UNRESOLVED** | LOW |
| `DEC-78948f5e` | PAT | Value at End Period | 2023-10-01_2023-12-31 | **UNRESOLVED** | LOW |
| `DEC-e4b3b9d4` | Management Commentary | General Business Strategy | Undated | **UNRESOLVED** | LOW |
| `DEC-35a320ea` | Total income | Revenue from Operations | Undated | **UNRESOLVED** | LOW |
| `DEC-45207bec` | Profit/(Loss) before tax | EBITDA | Undated | **UNRESOLVED** | LOW |
| `DEC-89999bb4` | Profit/(Loss) before tax | Net Profit/Loss | Undated | **UNRESOLVED** | LOW |
| `DEC-e3ff02fa` | Profit/(Loss) before tax | Interest Expense | Undated | **UNRESOLVED** | LOW |
| `DEC-bb879e10` | Total income | Revenue from operations | 2023-01-01_2023-03-31 | **CONTRADICTION** | HIGH |
| `DEC-422c9473` | Total income | Revenue from operations | 2023-10-01_2023-12-31 | **UNRESOLVED** | LOW |
