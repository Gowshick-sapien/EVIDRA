# EVIDRA Executive Summary Report

- **Job ID:** `JOB-20260908-130025-29b35d`
- **Created At:** `2026-09-08T13:00:25.298444+00:00`
- **Completed At:** `2026-09-08T13:21:07.346714+00:00`
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
| `DEC-fe2a8f55` | Delhivery Limited | CONSOLIDATED_EQUITY | 2021-03-31_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-5b7b84b1` | Delhivery Limited | CONSOLIDATED_LIABILITIES | 2021-03-31_2021-03-31 | **CORROBORATED** | HIGH |
| `DEC-c2b95b72` | Delhivery Limited | TOTAL_INFRASTRUCTURE_AREA_IN_MILLION_SQ_FT | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-b42b2420` | Delhivery Limited | NUMBER_OF_DELIVERY_POINTS | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-ca79125e` | Delhivery Limited | TEAM_SIZE_IN_THOUSAND_PEOPLE | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-c26e93fa` | Delhivery Limited | TRUCKLOAD_MOVEMENTS_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-859ccd6d` | Delhivery Limited | NUMBER_OF_ACTIVE_CUSTOMERS | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-05427ef9` | Delhivery Limited | LAUNCH_YEAR_FOR_HEAVY_GOODS_SERVICE | Undated | **UNRESOLVED** | LOW |
| `DEC-89921726` | Delhivery Limited | EMERGING_AND_FASTEST_GROWING_E_COMMERCE_CATEGORIES | Undated | **UNRESOLVED** | LOW |
| `DEC-01e9bd6d` | Delhivery Limited | REVENUE | 2021-12-31_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-e92d4ded` | Delhivery Limited | MARKET_POSITIONING | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-8634884c` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_Q3_Q4_FY21 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-782846e9` | Delhivery Limited | NUMBER_OF_PIN_CODES_REACHED_IN_THOUSAND | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-9972fbb8` | Delhivery Limited | EXPRESS_PARCEL_ORDERS_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-b17ac3fa` | Delhivery Limited | ORDERS_PROCESSED_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-3c897e84` | Delhivery Limited | NUMBER_OF_GATEWAYS | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-683be3d0` | Delhivery Limited | RATED_AUTOMATED_SORT_CAPACITY_IN_MILLION_PARCELS_PER_DAY | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-dba18d81` | Delhivery Limited | EXPRESS_PARCEL_ORDERS_Q3_Q4_FY21 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-1c4969e8` | Delhivery Limited | NETWORK_SIZE_FOR_HEAVY_PARCEL_DELIVERY | Undated | **UNRESOLVED** | LOW |
| `DEC-a8b39587` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-4c071ba5` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_IN_MILLION | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-9183a3e6` | Delhivery Limited | MARKET_POSITION_FISCAL_2021 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-70d29286` | Delhivery Limited | FREIGHT_GROWTH_RATE_CAGR | 2018-04-01_2019-03-31 | **UNRESOLVED** | LOW |
| `DEC-36f6f7b3` | Delhivery Limited | REVENUE_FROM_CONTRACTS_WITH_CUSTOMERS_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-d9bcfbf2` | Delhivery Limited | RESTATED_CONSOLIDATED_SUMMARY_STATEMENT_OF_PROFIT_AND_LOSS_OF_DELHIVERY_LIMITED_FOR_THE_YEAR_ENDED_MARCH_31_2021 | 2020-04-01_2021-03-31 | **CORROBORATED** | HIGH |
| `DEC-626ad12e` | Delhivery Limited | RESTATED_NET_LOSS_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-dd97760f` | Delhivery Limited | EARNINGS_BEFORE_INTEREST_TAXES_DEPRECIATION_AND_AMORTIZATION_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-c22f37e4` | Delhivery Limited | ADJUSTED_EARNINGS_BEFORE_INTEREST_TAXES_DEPRECIATION_AND_AMORTIZATION_IN_CRORES | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-c637db98` | Delhivery Limited | RESTATED_NET_LOSS_IN_MILLION | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-7e00532a` | Delhivery Limited | EXPENSES | Undated | **UNRESOLVED** | LOW |
| `DEC-f86496c5` | Delhivery Limited | SERVICE_LEVERAGING_CAPABILITIES | Undated | **UNRESOLVED** | LOW |
| `DEC-a368d3f5` | Delhivery Limited | SERVICE_CAPABILITIES | Undated | **UNRESOLVED** | LOW |
| `DEC-b49a0875` | Delhivery Limited | SERVICE_LAUNCH | Undated | **UNRESOLVED** | LOW |
| `DEC-3548755c` | Delhivery Limited | FREIGHT_DELIVERED | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-9acb18d1` | Delhivery Limited | PTL_FREIGHT_FY21 | 2020-04-01_2021-03-31 | **UNRESOLVED** | LOW |
| `DEC-22edc61a` | Delhivery Limited | ACQUISITION | 2021-01-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-4547bccf` | Delhivery Limited | PTL_FREIGHT_Q3_Q4_FY21 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-938ac3b6` | Delhivery Limited | CONSOLIDATED_ASSETS | 2021-03-31_2021-03-31 | **CORROBORATED** | HIGH |
| `DEC-745f8f8e` | Spoton Logistics Private Limited | TOTAL_ADJUSTMENT | 2021-08-24_2021-08-24 | **UNRESOLVED** | LOW |
| `DEC-310883a8` | Spoton Logistics Private Limited | ADJUSTMENT_FOR_SPOTON_LOGISTICS_PRIVATE_LIMITED_INTERIM_CONSOLIDATED_PROFIT_AND_LOSS_FOR_PERIOD_AUGUST_24_2021_TO_DECEMBER_31_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-d70f2742` | Spoton Logistics Private Limited | INTRAGROUP_ELIMINATION_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-7cb99085` | Spoton Logistics Private Limited | ACQUISITION_ADJUSTMENTS_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-68d21401` | Spoton Logistics Private Limited | N_A | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-411be74d` | Spoton Logistics Private Limited | TOTAL_ELIMINATION | 2021-04-01_2021-04-01 | **UNRESOLVED** | LOW |
| `DEC-af0e677e` | Spoton Logistics Private Limited | TOTAL_ADJUSTMENT_S | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-ffe20a4e` | Spoton Logistics Private Limited | INTRAGROUP_ELIMINATION_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-0e5c6979` | Spoton Logistics Private Limited | ACQUISITI_ON_ADJUSTM_ENTS_FOR_PERIOD_APRIL_1_2021_TO_AUGUST_23_2021 | 2021-04-01_2021-12-31 | **UNRESOLVED** | LOW |
| `DEC-f206d276` | Delhivery Limited | RESTATED_CONSOLIDATED_SUMMARY_STATEMENT_OF_PROFIT_AND_LOSS_OF_DELHIVERY_LIMITED_FOR_THE_YEAR_ENDED_MARCH_31_2021 | 2021-04-01_2022-03-31 | **CONTRADICTION** | HIGH |
