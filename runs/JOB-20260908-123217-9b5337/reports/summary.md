# EVIDRA Executive Summary Report

- **Job ID:** `JOB-20260908-123217-9b5337`
- **Created At:** `2026-09-08T12:32:17.291335+00:00`
- **Completed At:** `2026-09-08T12:53:08.813163+00:00`
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
| `DEC-214bc20a` | Delhivery Limited | RESTATED_NET_LOSS_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-548b2391` | Delhivery Limited | EARNINGS_BEFORE_INTEREST_TAXES_DEPRECIATION_AND_AMORTIZATION_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-debb59b4` | Delhivery Limited | ADJUSTED_EARNINGS_BEFORE_INTEREST_TAXES_DEPRECIATION_AND_AMORTIZATION_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-91bf617d` | Delhivery Limited | RESTATED_NET_LOSS_IN_MILLION | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-fef918fb` | Delhivery Limited | EXPENSES | Undated | **UNRESOLVED** | LOW |
| `DEC-13e82f47` | Delhivery Limited | SERVICE_LEVERAGING_CAPABILITIES | Undated | **UNRESOLVED** | LOW |
| `DEC-b901ef3c` | Delhivery Limited | SERVICE_CAPABILITIES | Undated | **UNRESOLVED** | LOW |
| `DEC-b458bcd4` | Delhivery Limited | SERVICE_LAUNCH | Undated | **UNRESOLVED** | LOW |
| `DEC-9bbc86a9` | Delhivery Limited | FREIGHT_DELIVERED | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-ecb7c73a` | Delhivery Limited | PTL_FREIGHT_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-38f59863` | Delhivery Limited | ACQUISITION | 2021-01-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-d0c13b88` | Delhivery Limited | PTL_FREIGHT_Q3_Q4_FY21 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-8a27c874` | Delhivery Limited | CONSOLIDATED_ASSETS | 2021-03-31_2021-03-31 | **CORROBORATED** | HIGH |
| `DEC-9c11d3fe` | Delhivery Limited | CONSOLIDATED_EQUITY | 2021-03-31_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-b45fbbd4` | Delhivery Limited | CONSOLIDATED_LIABILITIES | 2021-03-31_2021-03-31 | **CORROBORATED** | HIGH |
| `DEC-0015a6f3` | Delhivery Limited | TOTAL_INFRASTRUCTURE_AREA_IN_MILLION_SQ_FT | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-740d4f3e` | Delhivery Limited | NUMBER_OF_DELIVERY_POINTS | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-28b3502d` | Delhivery Limited | TEAM_SIZE_IN_THOUSAND_PEOPLE | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-485278e4` | Delhivery Limited | TRUCKLOAD_MOVEMENTS_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-3ecc2382` | Delhivery Limited | NUMBER_OF_ACTIVE_CUSTOMERS | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-662f43df` | Delhivery Limited | LAUNCH_YEAR_FOR_HEAVY_GOODS_SERVICE | Undated | **UNRESOLVED** | LOW |
| `DEC-1317c6ec` | Delhivery Limited | EMERGING_AND_FASTEST_GROWING_E_COMMERCE_CATEGORIES | Undated | **UNRESOLVED** | LOW |
| `DEC-51d21bfa` | Delhivery Limited | REVENUE | 2021-12-31_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-976eed78` | Delhivery Limited | MARKET_POSITIONING | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-2abaf39e` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_Q3_Q4_FY21 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-10ed6b91` | Delhivery Limited | NUMBER_OF_PIN_CODES_REACHED_IN_THOUSAND | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-203ec1a3` | Delhivery Limited | EXPRESS_PARCEL_ORDERS_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-365a4be7` | Delhivery Limited | ORDERS_PROCESSED_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-b8efcf4e` | Delhivery Limited | NUMBER_OF_GATEWAYS | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-5d4ad9c8` | Delhivery Limited | RATED_AUTOMATED_SORT_CAPACITY_IN_MILLION_PARCELS_PER_DAY | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-daf933ab` | Delhivery Limited | EXPRESS_PARCEL_ORDERS_Q3_Q4_FY21 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-c6bf590c` | Delhivery Limited | NETWORK_SIZE_FOR_HEAVY_PARCEL_DELIVERY | Undated | **UNRESOLVED** | LOW |
| `DEC-2cb7ff03` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-692218d9` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_IN_MILLION | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-42f71cd6` | Delhivery Limited | MARKET_POSITION_FISCAL_2021 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-2a17327a` | Delhivery Limited | FREIGHT_GROWTH_RATE_CAGR | 2018-04-01_2019-03-31 | **UNRESOLVED** | LOW |
| `DEC-fe737957` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-df24a7f6` | Spoton Logistics Private Limited | TOTAL_ADJUSTMENT | 2021-08-24_2021-08-24 | **UNRESOLVED** | LOW |
| `DEC-41203e8a` | Spoton Logistics Private Limited | ADJUSTMENT_FOR_SPOTON_LOGISTICS_PRIVATE_LIMITED_INTERIM_CONSOLIDATED_PROFIT_AND_LOSS_FOR_PERIOD_AUGUST_24_2021_TO_DECEMBER_31_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-0fc7ad2d` | Spoton Logistics Private Limited | INTRAGROUP_ELIMINATION_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-693c82ec` | Spoton Logistics Private Limited | ACQUISITION_ADJUSTMENTS_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-1428702b` | Spoton Logistics Private Limited | N_A | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-f3876b4d` | Spoton Logistics Private Limited | TOTAL_ELIMINATION | 2021-04-01_2021-04-01 | **UNRESOLVED** | LOW |
| `DEC-658952f0` | Spoton Logistics Private Limited | TOTAL_ADJUSTMENT_S | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-d87ce5d5` | Spoton Logistics Private Limited | INTRAGROUP_ELIMINATION_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-ffdd42b2` | Spoton Logistics Private Limited | ACQUISITI_ON_ADJUSTM_ENTS_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-e625fc5b` | Delhivery Limited | RESTATED_CONSOLIDATED_SUMMARY_STATEMENT_OF_PROFIT_AND_LOSS_OF_DELHIVERY_LIMITED_FOR_THE_YEAR_ENDED_MARCH_31_2021 | 2021-04-01_2022-03-31 | **CONTRADICTION** | HIGH |
| `DEC-1381c98f` | Delhivery Limited | RESTATED_CONSOLIDATED_SUMMARY_STATEMENT_OF_PROFIT_AND_LOSS_OF_DELHIVERY_LIMITED_FOR_THE_YEAR_ENDED_MARCH_31_2021 | 2020-04-01_2021-03-31 | **CORROBORATED** | HIGH |
