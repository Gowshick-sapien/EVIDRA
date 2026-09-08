# EVIDRA Executive Summary Report

- **Job ID:** `JOB-20260908-112515-c44d4f`
- **Created At:** `2026-09-08T11:25:15.759720+00:00`
- **Completed At:** `2026-09-08T11:45:54.645494+00:00`
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
| Raw Observations | 57 | Extracted factual statements and metric claims |
| Fact Candidates | 56 | Deterministically normalized values, units, currencies, and dates |
| Fact Groups | 37 | Disputed metric clusters grouped by entity, attribute, and period |
| Decisions Evaluated | 37 | Epistemic adjudications performed by the decision engine |

## 3. Verdict Distribution

| Verdict | Count | Description |
| :--- | :--- | :--- |
| CORROBORATED | 1 | Claims independently validated across multiple sources or coherent singular facts |
| CONTRADICTION | 7 | Direct numerical or factual conflicts that could not be reconciled |
| RECONCILED | 1 | Apparent discrepancies explained by timing, restatement, or accounting scope |
| UNRESOLVED | 28 | Claims with insufficient evidence or ambiguous provenance |

## 4. Evaluated Decisions Summary

| Decision ID | Entity | Metric / Attribute | Period | Verdict | Strength |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DEC-7f4b0064` | Delhivery Limited | rated automated sort capacity (in million parcels per day) | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-2889824c` | Delhivery Limited | number of active customers | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-83bdc5b2` | Delhivery Limited | Revenue from contracts with customers (Q3-Q4 FY21) | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-a6bfa25e` | Delhivery Limited | Express parcel orders (Q3-Q4 FY21) | 2021-04-01_2021-12-31 | **CONTRADICTION** | HIGH |
| `DEC-a0b42fa6` | Delhivery Limited | Freight Growth Rate (CAGR) | 2018-04-01_2019-03-31 | **UNRESOLVED** | LOW |
| `DEC-b733e9bd` | Delhivery Limited | Acquisition | 2021-01-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-00511742` | Delhivery Limited | number of PIN codes reached (in thousand) | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-71b6e27a` | Delhivery Limited | total infrastructure area (in million sq ft) | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-047e7cac` | Delhivery Limited | number of delivery points | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-10cb85ee` | Delhivery Limited | team size (in thousand people) | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-b955bf84` | Delhivery Limited | revenue from contracts with customers (in crores) | 2020-04-01_2021-03-31 | **RECONCILED** | HIGH |
| `DEC-5c8f216d` | Delhivery Limited | restated net loss (in crores) | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-174dac98` | Delhivery Limited | earnings before interest, taxes, depreciation and amortization (in crores) | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-dac60be4` | Delhivery Limited | Freight Delivered | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-2d4df365` | Delhivery Limited | Market Positioning | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-6e240025` | Delhivery Limited | Express parcel orders (FY21) | 2020-04-01_2021-03-31 | **CONTRADICTION** | HIGH |
| `DEC-6a18721c` | Delhivery Limited | PTL freight (FY21) | 2020-04-01_2021-03-31 | **CONTRADICTION** | HIGH |
| `DEC-786cd4e0` | Delhivery Limited | Market Position (Fiscal 2021) | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-bd1e95dd` | Delhivery Limited | Consolidated Assets | 2021-03-31_2021-03-31 | **CONTRADICTION** | HIGH |
| `DEC-34db1b4d` | Delhivery Limited | Revenue | 2021-12-31_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-eedfb4c6` | Delhivery Limited | number of gateways | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-5b54c2bd` | Spoton Logistics Private Limited | Total Adjustment | 2021-08-24_2021-08-24 | **UNRESOLVED** | LOW |
| `DEC-aa6f941b` | Spoton Logistics Private Limited | Total Elimination | 2021-04-01_2021-04-01 | **UNRESOLVED** | LOW |
| `DEC-02aaad35` | Delhivery Limited | Restated Consolidated Summary Statement of Profit and Loss of Delhivery Limited for the year ended March 31, 2021 | 2021-04-01_2022-03-31 | **CONTRADICTION** | HIGH |
| `DEC-bdf35d8a` | Spoton Logistics Private Limited | Total Adjustment s | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-dc1da038` | Spoton Logistics Private Limited | Intragroup elimination for period April 1, 2021 to August 23, 2021 | 2021-04-01_2021-12-31 | **CONTRADICTION** | HIGH |
| `DEC-28169e34` | Spoton Logistics Private Limited | Acquisiti on Adjustm ents for period April 1, 2021 to August 23, 2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-53758673` | Spoton Logistics Private Limited | Adjustment for Spoton Logistics Private Limited Interim Consolidated Profit and Loss for period August 24, 2021 to December 31, 2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-df3dcdbc` | Spoton Logistics Private Limited | Acquisition adjustments for period April 1, 2021 to August 23, 2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-a36d855c` | Spoton Logistics Private Limited | N/A | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-9f9f931c` | Delhivery Limited | Expenses | Undated | **UNRESOLVED** | LOW |
| `DEC-0cf19f01` | Delhivery Limited | Launch Year for Heavy Goods Service | Undated | **UNRESOLVED** | LOW |
| `DEC-ae2be9ef` | Delhivery Limited | Service Leveraging Capabilities | Undated | **CORROBORATED** | HIGH |
| `DEC-e8a56d09` | Delhivery Limited | Network Size for Heavy Parcel Delivery | Undated | **UNRESOLVED** | LOW |
| `DEC-041cc090` | Delhivery Limited | Emerging and Fastest Growing E-Commerce Categories | Undated | **UNRESOLVED** | LOW |
| `DEC-f83cd9a4` | Delhivery Limited | Service Launch | Undated | **UNRESOLVED** | LOW |
| `DEC-13466921` | Delhivery Limited | Restated Consolidated Summary Statement of Profit and Loss of Delhivery Limited for the year ended March 31, 2021 | 2020-04-01_2021-03-31 | **CONTRADICTION** | HIGH |
