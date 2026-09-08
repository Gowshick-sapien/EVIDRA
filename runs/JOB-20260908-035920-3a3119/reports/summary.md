# EVIDRA Executive Summary Report

- **Job ID:** `JOB-20260908-035920-3a3119`
- **Created At:** `2026-09-08T03:59:20.766871+00:00`
- **Completed At:** `2026-09-08T04:02:41.729702+00:00`
- **Status:** `PROCESSING`

## 1. Ingested Documents

| Document ID | Filename | Pages | SHA-256 Hash |
| :--- | :--- | :--- | :--- |
| DOC-001 | 01-delhivery-prospectus-2022-excerpt.pdf | 100 | `0d7e71e1766e...` |

## 2. Pipeline Metrics

| Metric | Count | Description |
| :--- | :--- | :--- |
| Documents Processed | 1 | Total PDF source documents |
| Evidence Chunks | 1760 | Discrete text and table segments preserved with bounding boxes |
| Raw Observations | 12 | Extracted factual statements and metric claims |
| Fact Candidates | 12 | Deterministically normalized values, units, currencies, and dates |
| Fact Groups | 6 | Disputed metric clusters grouped by entity, attribute, and period |
| Decisions Evaluated | 6 | Epistemic adjudications performed by the decision engine |

## 3. Verdict Distribution

| Verdict | Count | Description |
| :--- | :--- | :--- |
| CORROBORATED | 0 | Claims independently validated across multiple sources or coherent singular facts |
| CONTRADICTION | 2 | Direct numerical or factual conflicts that could not be reconciled |
| RECONCILED | 0 | Apparent discrepancies explained by timing, restatement, or accounting scope |
| UNRESOLVED | 4 | Claims with insufficient evidence or ambiguous provenance |

## 4. Evaluated Decisions Summary

| Decision ID | Entity | Metric / Attribute | Period | Verdict | Strength |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DEC-897edc6d` | Restated | Total | 2021-04-01_2021-12-31 | **CONTRADICTION** | HIGH |
| `DEC-0e8f767a` | Reporting Entity |  | 2021-08-24_2021-08-24 | **UNRESOLVED** | LOW |
| `DEC-5f16691d` | Reporting Entity |  | 2021-04-01_2021-04-01 | **CONTRADICTION** | HIGH |
| `DEC-6d303059` | Adjustment for Spoton Logistics Private Limited Interim Consolidated Profit and Loss for period August 24, 2021 to December 31, 2021 | Total Adjustment s | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-0deb688e` | Intragroup elimination for period April 1, 2021 to August 23, 2021 | Total Adjustment s | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-fd988cf2` | Acquisiti on Adjustm ents for period April 1, 2021 to August 23, 2021 | Total Adjustment s | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
