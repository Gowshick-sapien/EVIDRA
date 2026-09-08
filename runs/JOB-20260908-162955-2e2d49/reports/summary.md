# EVIDRA Executive Summary Report

- **Job ID:** `JOB-20260908-162955-2e2d49`
- **Created At:** `2026-09-08T16:29:55.192193+00:00`
- **Completed At:** `2026-09-08T16:56:33.021462+00:00`
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
| `DEC-09b5ed5b` | Delhivery Limited | CONSOLIDATED_EQUITY | 2021-03-31_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-b5d3ada6` | Delhivery Limited | CONSOLIDATED_LIABILITIES | 2021-03-31_2021-03-31 | **CORROBORATED** | HIGH |
| `DEC-89eacd6d` | Delhivery Limited | TOTAL_INFRASTRUCTURE_AREA_IN_MILLION_SQ_FT | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-b5767531` | Delhivery Limited | NUMBER_OF_DELIVERY_POINTS | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-5a2d3e1b` | Delhivery Limited | TEAM_SIZE_IN_THOUSAND_PEOPLE | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-ba2b2df2` | Delhivery Limited | TRUCKLOAD_MOVEMENTS_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-20590388` | Delhivery Limited | NUMBER_OF_ACTIVE_CUSTOMERS | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-c82fea43` | Delhivery Limited | LAUNCH_YEAR_FOR_HEAVY_GOODS_SERVICE | Undated | **UNRESOLVED** | LOW |
| `DEC-273fdaee` | Delhivery Limited | EMERGING_AND_FASTEST_GROWING_E_COMMERCE_CATEGORIES | Undated | **UNRESOLVED** | LOW |
| `DEC-99c1116f` | Delhivery Limited | REVENUE | 2021-12-31_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-c11ff0eb` | Delhivery Limited | MARKET_POSITIONING | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-98cc76f2` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_Q3_Q4_FY21 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-8f527fe1` | Delhivery Limited | NUMBER_OF_PIN_CODES_REACHED_IN_THOUSAND | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-6e20c1ed` | Delhivery Limited | EXPRESS_PARCEL_ORDERS_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-0508c046` | Delhivery Limited | ORDERS_PROCESSED_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-7e016bcc` | Delhivery Limited | NUMBER_OF_GATEWAYS | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-be719eac` | Delhivery Limited | RATED_AUTOMATED_SORT_CAPACITY_IN_MILLION_PARCELS_PER_DAY | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-3717cc4c` | Delhivery Limited | EXPRESS_PARCEL_ORDERS_Q3_Q4_FY21 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-15932866` | Delhivery Limited | NETWORK_SIZE_FOR_HEAVY_PARCEL_DELIVERY | Undated | **UNRESOLVED** | LOW |
| `DEC-53d2184e` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-dda33b39` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_IN_MILLION | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-45e6fb78` | Delhivery Limited | MARKET_POSITION_FISCAL_2021 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-eb53856d` | Delhivery Limited | FREIGHT_GROWTH_RATE_CAGR | 2018-04-01_2019-03-31 | **UNRESOLVED** | LOW |
| `DEC-3895947a` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-da173198` | Delhivery Limited | RESTATED_NET_LOSS_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-3240d8e3` | Delhivery Limited | EARNINGS_BEFORE_INTEREST_TAXES_DEPRECIATION_AND_AMORTIZATION_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-d017ab0d` | Delhivery Limited | ADJUSTED_EARNINGS_BEFORE_INTEREST_TAXES_DEPRECIATION_AND_AMORTIZATION_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-6f376879` | Delhivery Limited | RESTATED_NET_LOSS_IN_MILLION | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-bd993cf3` | Delhivery Limited | EXPENSES | Undated | **UNRESOLVED** | LOW |
| `DEC-992ff4bf` | Delhivery Limited | SERVICE_LEVERAGING_CAPABILITIES | Undated | **UNRESOLVED** | LOW |
| `DEC-b881453a` | Delhivery Limited | SERVICE_CAPABILITIES | Undated | **UNRESOLVED** | LOW |
| `DEC-58d3d821` | Delhivery Limited | SERVICE_LAUNCH | Undated | **UNRESOLVED** | LOW |
| `DEC-2be4d41a` | Delhivery Limited | FREIGHT_DELIVERED | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-f85c6952` | Delhivery Limited | PTL_FREIGHT_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-819288ec` | Delhivery Limited | ACQUISITION | 2021-01-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-1af72b9b` | Delhivery Limited | PTL_FREIGHT_Q3_Q4_FY21 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-64d9f1cb` | Delhivery Limited | CONSOLIDATED_ASSETS | 2021-03-31_2021-03-31 | **CORROBORATED** | HIGH |
| `DEC-7990623d` | Delhivery Limited | RESTATED_CONSOLIDATED_SUMMARY_STATEMENT_OF_PROFIT_AND_LOSS_OF_DELHIVERY_LIMITED_FOR_THE_YEAR_ENDED_MARCH_31_2021 | 2021-04-01_2022-03-31 | **CONTRADICTION** | HIGH |
| `DEC-0cbc351a` | Delhivery Limited | RESTATED_CONSOLIDATED_SUMMARY_STATEMENT_OF_PROFIT_AND_LOSS_OF_DELHIVERY_LIMITED_FOR_THE_YEAR_ENDED_MARCH_31_2021 | 2020-04-01_2021-03-31 | **CORROBORATED** | HIGH |
| `DEC-961f6a25` | Spoton Logistics Private Limited | TOTAL_ADJUSTMENT | 2021-08-24_2021-08-24 | **UNRESOLVED** | LOW |
| `DEC-17a1d514` | Spoton Logistics Private Limited | ADJUSTMENT_FOR_SPOTON_LOGISTICS_PRIVATE_LIMITED_INTERIM_CONSOLIDATED_PROFIT_AND_LOSS_FOR_PERIOD_AUGUST_24_2021_TO_DECEMBER_31_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-08cd47fb` | Spoton Logistics Private Limited | INTRAGROUP_ELIMINATION_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-62d4903e` | Spoton Logistics Private Limited | ACQUISITION_ADJUSTMENTS_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-ebfb04d0` | Spoton Logistics Private Limited | N_A | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-ba19ae98` | Spoton Logistics Private Limited | TOTAL_ELIMINATION | 2021-04-01_2021-04-01 | **UNRESOLVED** | LOW |
| `DEC-0c625332` | Spoton Logistics Private Limited | TOTAL_ADJUSTMENT_S | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-8ecde5bc` | Spoton Logistics Private Limited | INTRAGROUP_ELIMINATION_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-cc933883` | Spoton Logistics Private Limited | ACQUISITI_ON_ADJUSTM_ENTS_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
