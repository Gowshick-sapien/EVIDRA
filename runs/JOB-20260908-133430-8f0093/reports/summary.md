# EVIDRA Executive Summary Report

- **Job ID:** `JOB-20260908-133430-8f0093`
- **Created At:** `2026-09-08T13:34:30.396707+00:00`
- **Completed At:** `2026-09-08T13:55:37.160087+00:00`
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
| Fact Groups | 48 | Disputed metric clusters grouped by entity, attribute, and period |
| Decisions Evaluated | 48 | Epistemic adjudications performed by the decision engine |

## 3. Verdict Distribution

| Verdict | Count | Description |
| :--- | :--- | :--- |
| CORROBORATED | 3 | Claims independently validated across multiple sources or coherent singular facts |
| CONTRADICTION | 1 | Direct numerical or factual conflicts that could not be reconciled |
| RECONCILED | 0 | Apparent discrepancies explained by timing, restatement, or accounting scope |
| UNRESOLVED | 44 | Claims with insufficient evidence or ambiguous provenance |

## 4. Evaluated Decisions Summary

| Decision ID | Entity | Metric / Attribute | Period | Verdict | Strength |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DEC-43db78a7` | Delhivery Limited | TOTAL_INFRASTRUCTURE_AREA_IN_MILLION_SQ_FT | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-1a6722c2` | Delhivery Limited | NUMBER_OF_DELIVERY_POINTS | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-707f48c7` | Delhivery Limited | TEAM_SIZE_IN_THOUSAND_PEOPLE | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-a565e9dd` | Delhivery Limited | TRUCKLOAD_MOVEMENTS_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-ea732d8e` | Delhivery Limited | NUMBER_OF_ACTIVE_CUSTOMERS | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-255c2736` | Delhivery Limited | LAUNCH_YEAR_FOR_HEAVY_GOODS_SERVICE | Undated | **UNRESOLVED** | LOW |
| `DEC-2e1c6b19` | Delhivery Limited | EMERGING_AND_FASTEST_GROWING_E_COMMERCE_CATEGORIES | Undated | **UNRESOLVED** | LOW |
| `DEC-a707db86` | Delhivery Limited | REVENUE | 2021-12-31_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-54cbf7a1` | Delhivery Limited | MARKET_POSITIONING | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-3df6d3ce` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_Q3_Q4_FY21 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-71ad9444` | Delhivery Limited | NUMBER_OF_PIN_CODES_REACHED_IN_THOUSAND | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-daeebe08` | Delhivery Limited | EXPRESS_PARCEL_ORDERS_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-23276243` | Delhivery Limited | ORDERS_PROCESSED_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-ef3c15e5` | Delhivery Limited | NUMBER_OF_GATEWAYS | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-5ca719fc` | Delhivery Limited | RATED_AUTOMATED_SORT_CAPACITY_IN_MILLION_PARCELS_PER_DAY | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-d502dca9` | Delhivery Limited | EXPRESS_PARCEL_ORDERS_Q3_Q4_FY21 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-10a9be92` | Delhivery Limited | NETWORK_SIZE_FOR_HEAVY_PARCEL_DELIVERY | Undated | **UNRESOLVED** | LOW |
| `DEC-2b7707ce` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-682f15e1` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_IN_MILLION | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-0dbd3650` | Delhivery Limited | MARKET_POSITION_FISCAL_2021 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-21b2acc5` | Delhivery Limited | FREIGHT_GROWTH_RATE_CAGR | 2018-04-01_2019-03-31 | **UNRESOLVED** | LOW |
| `DEC-d7602747` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-f614b5c1` | Delhivery Limited | RESTATED_NET_LOSS_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-62fdf010` | Delhivery Limited | EARNINGS_BEFORE_INTEREST_TAXES_DEPRECIATION_AND_AMORTIZATION_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-d90d0e5d` | Delhivery Limited | ADJUSTED_EARNINGS_BEFORE_INTEREST_TAXES_DEPRECIATION_AND_AMORTIZATION_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-f8408926` | Delhivery Limited | RESTATED_NET_LOSS_IN_MILLION | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-e1255df4` | Delhivery Limited | EXPENSES | Undated | **UNRESOLVED** | LOW |
| `DEC-1fab368a` | Delhivery Limited | SERVICE_LEVERAGING_CAPABILITIES | Undated | **UNRESOLVED** | LOW |
| `DEC-9f3c1970` | Delhivery Limited | SERVICE_CAPABILITIES | Undated | **UNRESOLVED** | LOW |
| `DEC-5b6487db` | Delhivery Limited | SERVICE_LAUNCH | Undated | **UNRESOLVED** | LOW |
| `DEC-c9ac297f` | Delhivery Limited | FREIGHT_DELIVERED | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-b55a53d8` | Delhivery Limited | PTL_FREIGHT_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-0e01071d` | Delhivery Limited | ACQUISITION | 2021-01-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-30d91a0e` | Delhivery Limited | PTL_FREIGHT_Q3_Q4_FY21 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-0658c7db` | Delhivery Limited | CONSOLIDATED_ASSETS | 2021-03-31_2021-03-31 | **CORROBORATED** | HIGH |
| `DEC-d5eac816` | Delhivery Limited | CONSOLIDATED_EQUITY | 2021-03-31_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-dd215f0a` | Delhivery Limited | CONSOLIDATED_LIABILITIES | 2021-03-31_2021-03-31 | **CORROBORATED** | HIGH |
| `DEC-62e7c8d9` | Spoton Logistics Private Limited | TOTAL_ADJUSTMENT | 2021-08-24_2021-08-24 | **UNRESOLVED** | LOW |
| `DEC-7e7adbad` | Spoton Logistics Private Limited | ADJUSTMENT_FOR_SPOTON_LOGISTICS_PRIVATE_LIMITED_INTERIM_CONSOLIDATED_PROFIT_AND_LOSS_FOR_PERIOD_AUGUST_24_2021_TO_DECEMBER_31_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-20d8abb1` | Spoton Logistics Private Limited | INTRAGROUP_ELIMINATION_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-96c10ddd` | Spoton Logistics Private Limited | ACQUISITION_ADJUSTMENTS_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-dfc58465` | Spoton Logistics Private Limited | N_A | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-9a6e1ac7` | Spoton Logistics Private Limited | TOTAL_ELIMINATION | 2021-04-01_2021-04-01 | **UNRESOLVED** | LOW |
| `DEC-d3a09d8c` | Spoton Logistics Private Limited | TOTAL_ADJUSTMENT_S | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-a741b47b` | Spoton Logistics Private Limited | INTRAGROUP_ELIMINATION_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-0d96ff43` | Spoton Logistics Private Limited | ACQUISITI_ON_ADJUSTM_ENTS_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-10bcd0ba` | Delhivery Limited | RESTATED_CONSOLIDATED_SUMMARY_STATEMENT_OF_PROFIT_AND_LOSS_OF_DELHIVERY_LIMITED_FOR_THE_YEAR_ENDED_MARCH_31_2021 | 2021-04-01_2022-03-31 | **CONTRADICTION** | HIGH |
| `DEC-a68a2980` | Delhivery Limited | RESTATED_CONSOLIDATED_SUMMARY_STATEMENT_OF_PROFIT_AND_LOSS_OF_DELHIVERY_LIMITED_FOR_THE_YEAR_ENDED_MARCH_31_2021 | 2020-04-01_2021-03-31 | **CORROBORATED** | HIGH |
