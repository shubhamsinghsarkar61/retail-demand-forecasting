# M5 Retail Demand Forecasting

## Week 1 - Day 7: Data Quality, Lineage & Handover Documentation

---

## 1. Project Overview

The Retail Demand Forecasting & Inventory Optimization platform is designed to help retail and supply-chain teams predict future product demand and make better inventory decisions.

The project uses the **M5 Forecasting Dataset**, which contains historical Walmart retail sales data together with calendar information and selling prices.

The overall system will combine:

* BigQuery
* Python
* SQL
* dbt
* Time-series forecasting
* Machine learning
* Streamlit
* Inventory optimization

The long-term objective is to move from historical sales analysis toward proactive demand forecasting, stockout prevention, overstock detection, and intelligent restocking recommendations.

---

# 2. Week 1 Objective

The objective of Week 1 was to establish the raw data architecture and verify that the M5 dataset is reliable enough for downstream transformations and forecasting.

Week 1 covered:

1. BigQuery environment setup
2. M5 dataset loading
3. Data quality validation
4. Data cleaning validation
5. Intelligent data readiness assessment
6. Data quality scoring
7. Documentation and Week 2 handover

---

# 3. Source Data Architecture

The raw M5 data is stored in the following BigQuery project and dataset:

**Project:** `sage-sylph-508507-m2`

**Dataset:** `m5_raw`

### Raw Tables

| Table                    | Purpose                                                    |
| ------------------------ | ---------------------------------------------------------- |
| `calendar`               | Calendar dates, weeks, months, years and event information |
| `sell_prices`            | Historical selling prices by store, item and week          |
| `sales_train_validation` | Historical product-level sales observations                |
| `sales_train_evaluation` | Evaluation-period sales data                               |

---

# 4. Data Flow

The Week 1 architecture is:

```text
M5 Forecasting Dataset
        |
        v
    BigQuery
        |
        v
     m5_raw
        |
        +------------------+
        |                  |
        v                  v
    calendar          sell_prices
        |
        |
        v
sales_train_validation
        |
        v
Data Quality Validation
        |
        v
Data Readiness Assessment
        |
        v
Week 2 dbt Transformations
```

---

# 5. Day 4 - Data Quality Validation

Initial data quality checks were performed on the raw BigQuery tables.

## Calendar

* Rows: **1,969**
* Unique dates: **1,969**
* Date range: **2011-01-29 to 2016-06-19**
* Duplicate dates: **0**
* Required-field NULL values: **0**

### Result

**PASS — Calendar data is valid.**

---

## Sell Prices

* Rows: **6,841,121**
* Invalid/zero/negative prices: **0**
* Minimum price: **0.01**
* Maximum price: **107.32**
* Average price: **4.41**

### Result

**PASS — Pricing data is valid.**

---

## Sales

* Rows: **30,490**
* Duplicate IDs: **0**
* Required identifier NULL values: **0**
* `d_1` minimum: **0**
* `d_1` maximum: **360**
* Negative `d_1` values: **0**

### Result

**PASS — Sales data is structurally valid.**

---

# 6. Day 5 - Data Cleaning Validation

Day 5 focused on validating the consistency and usability of the raw data.

The following checks were completed:

* Calendar uniqueness
* Sales ID uniqueness
* Required sales identifiers
* Negative sales validation
* Price validation
* Sales/calendar date-range readiness
* Item coverage between sales and pricing data

The sales dataset contains:

**3,049 unique items**

The pricing dataset also contains:

**3,049 unique items**

### Result

The raw M5 data was confirmed to be ready for downstream transformation.

**STATUS: READY FOR WEEK 2 DBT TRANSFORMATIONS**

---

# 7. Day 6 - Intelligent Data Readiness Pipeline

Day 6 introduced an automated data-readiness pipeline instead of relying only on manual inspection.

The pipeline validates:

1. Schema structure
2. Calendar readiness
3. Sales data readiness
4. Pricing data readiness
5. Sales-to-price item integrity
6. Sales-to-price store integrity
7. Critical anomalies

---

# 8. Schema Validation

Required fields were validated against the BigQuery table schemas.

### Validated Tables

* `calendar`
* `sell_prices`
* `sales_train_validation`

### Result

```text
calendar schema              PASS
sell_prices schema           PASS
sales_train_validation      PASS
```

**STATUS: PASS**

---

# 9. Referential Integrity

Cross-table relationships were checked between sales and pricing data.

### Item Integrity

Unmatched sales items:

**0**

Therefore, every item appearing in the sales data exists in the pricing data.

### Store Integrity

Unmatched sales stores:

**0**

Therefore, every store appearing in the sales data exists in the pricing data.

### Result

**STATUS: PASS**

---

# 10. Anomaly Detection

The Day 6 pipeline also identifies unusual observations.

The following observations were detected:

* Invalid prices: **0**
* Prices greater than 100: **3**
* Negative sales: **0**
* Sales greater than 100: **13**

The high-price and high-sales observations were retained because they are not automatically invalid and may represent legitimate retail activity.

The critical checks therefore passed successfully.

### Result

**PASS — No critical anomalies detected.**

---

# 11. Automated Data Quality Score

Seven major validation checks were evaluated.

```text
Checks passed : 7/7
Quality Score : 100/100
Status        : EXCELLENT
```

### Final Data Quality Score

# 100 / 100

This indicates that the validated source data satisfies all defined critical readiness checks for the Week 2 transformation stage.

---

# 12. Data Lineage

The planned transformation lineage is:

```text
M5 Dataset
    |
    v
BigQuery Raw Layer
    |
    +---- calendar
    |
    +---- sell_prices
    |
    +---- sales_train_validation
    |
    v
dbt Staging Layer
    |
    +---- stg_calendar
    +---- stg_sell_prices
    +---- stg_sales
    |
    v
dbt Intermediate Layer
    |
    +---- int_daily_sales
    +---- int_sales_with_prices
    |
    v
dbt Data Marts
    |
    +---- mart_weekly_demand
    +---- mart_monthly_demand
    +---- mart_store_demand
    +---- mart_product_demand
    |
    v
Forecasting Models
    |
    +---- Prophet
    +---- LightGBM
    |
    v
Demand Forecast
    |
    v
Inventory Optimization
```

---

# 13. Week 2 dbt Handoff

The validated raw data is ready to become the input for the dbt transformation layer.

## Planned Staging Models

### `stg_calendar`

Responsible for:

* Standardizing calendar fields
* Cleaning date-related columns
* Preparing event information

### `stg_sell_prices`

Responsible for:

* Standardizing price fields
* Preparing store/item/week relationships
* Preparing pricing features

### `stg_sales`

Responsible for:

* Standardizing sales identifiers
* Preparing historical sales observations
* Preparing the dataset for aggregation

---

# 14. Planned Intermediate Models

## `int_daily_sales`

Will transform the historical sales structure into an analysis-friendly daily sales model.

## `int_sales_with_prices`

Will combine sales information with relevant pricing information.

These models will provide the foundation for demand analysis and forecasting.

---

# 15. Planned Data Marts

The Week 2 transformation layer will prepare business-oriented data marts.

### Weekly Demand

`mart_weekly_demand`

Purpose:

* Weekly demand analysis
* Trend analysis
* Forecasting preparation

### Monthly Demand

`mart_monthly_demand`

Purpose:

* Monthly demand trends
* Seasonality analysis
* Business reporting

### Store Demand

`mart_store_demand`

Purpose:

* Store-level demand analysis
* Store comparison
* Forecasting by location

### Product Demand

`mart_product_demand`

Purpose:

* Product-level demand analysis
* High-volume product identification
* Forecasting preparation

---

# 16. Data Quality Rules for Future dbt Models

The following rules should be implemented as dbt tests during Week 2.

### Primary Key Checks

Expected unique identifiers should be tested for:

* Sales records
* Calendar dates
* Appropriate staging models

### NOT NULL Checks

Important business fields should not contain NULL values:

* `item_id`
* `store_id`
* `dept_id`
* `cat_id`
* `date`
* `sell_price`

### Value Checks

Important numerical fields should satisfy:

```text
sales >= 0
sell_price > 0
```

### Relationship Checks

The transformation layer should preserve valid relationships between:

```text
sales → items
sales → stores
sales → prices
sales → calendar
```

---

# 17. Permission Constraint Encountered

During Day 6, creation of a new BigQuery dataset/table layer was attempted.

The current user account does not have:

```text
bigquery.datasets.create
```

and does not have:

```text
bigquery.tables.create
```

permission on the existing `m5_raw` dataset.

Therefore, Day 6 was redesigned as a read-only data-readiness validation process.

This approach:

* Preserves the raw source tables
* Does not modify production/raw data
* Avoids unnecessary permission changes
* Produces a reproducible readiness report
* Hands the validated source data to the Week 2 dbt layer

---

# 18. Day 6 Readiness Report

The automated pipeline generated:

```text
week1_day6_data_readiness_report.md
```

The report records:

* Data quality score
* Validation results
* Source tables
* Data architecture
* Important findings
* dbt handoff information
* Permission constraints

---

# 19. Week 1 Final Architecture

At the end of Week 1, the project has established:

```text
                    M5 DATASET
                        |
                        v
                  BIGQUERY RAW
                        |
        +---------------+---------------+
        |               |               |
        v               v               v
    CALENDAR       SELL PRICES       SALES
        |               |               |
        +---------------+---------------+
                        |
                        v
             DATA QUALITY PIPELINE
                        |
        +---------------+---------------+
        |               |               |
        v               v               v
     Schema       Integrity       Anomalies
        |               |               |
        +---------------+---------------+
                        |
                        v
                 QUALITY SCORE
                     100/100
                        |
                        v
                DBT HANDOFF READY
```

---

# 20. Week 1 Completion Status

| Area                     | Status   |
| ------------------------ | -------- |
| BigQuery setup           | COMPLETE |
| M5 raw data loading      | COMPLETE |
| Data quality validation  | COMPLETE |
| Data cleaning validation | COMPLETE |
| Schema validation        | COMPLETE |
| Referential integrity    | COMPLETE |
| Anomaly detection        | COMPLETE |
| Automated quality score  | COMPLETE |
| Documentation            | COMPLETE |
| dbt handoff              | READY    |

---

# 21. Week 1 Conclusion

Week 1 successfully established the raw data foundation for the Retail Demand Forecasting & Inventory Optimization platform.

The M5 dataset was validated across schema, completeness, consistency, relationships, and critical anomalies.

The automated readiness pipeline achieved:

**DATA QUALITY SCORE: 100/100**

The raw BigQuery data is therefore ready to enter the Week 2 dbt transformation stage.

---

## Week 2 Starting Point

The next stage is:

```text
BigQuery Raw Data
        ↓
dbt Staging Models
        ↓
dbt Intermediate Models
        ↓
Weekly / Monthly Data Marts
        ↓
Forecasting Features
        ↓
Prophet + LightGBM
```

**WEEK 1 — DATA ARCHITECTURE & ETL: COMPLETED**

**WEEK 2 — DBT TRANSFORMATIONS: READY TO START**
