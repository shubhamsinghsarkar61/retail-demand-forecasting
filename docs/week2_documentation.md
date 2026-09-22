# Week 2 — dbt Transformation & Documentation

## Project
Retail Demand Forecasting & Inventory Optimization

## Objective

The objective of Week 2 is to transform the raw M5 retail sales data into structured datasets suitable for demand analysis and forecasting.

---

## Data Sources

The dbt project uses the following BigQuery source tables from the `m5_raw` dataset:

- `calendar`
- `sell_prices`
- `sales_train_validation`
- `sales_train_evaluation`

---

## Week 2 Transformations

### Day 1 — dbt Project Setup

Configured the dbt project and BigQuery connection for the retail demand forecasting pipeline.

### Day 2 — BigQuery Connection

Verified the dbt connection with the BigQuery warehouse and validated the development environment.

### Day 3 — Raw Sources

Configured the M5 raw BigQuery tables as dbt sources using `sources.yml`.

### Day 4 — Daily Sales Transformation

Created `int_daily_sales` to transform the wide-format M5 sales data into daily sales records.

The transformation:

- Unpivots daily sales columns (`d_1` to `d_1913`)
- Connects sales records with calendar information
- Produces date-level sales data
- Preserves product, department, category and store information

### Day 5 — Sales & Pricing Transformation

Created `int_sales_with_prices`.

The transformation combines:

- Daily sales
- Calendar information
- Weekly selling prices

The price data is joined using:

- `item_id`
- `store_id`
- `wm_yr_wk`

This produces an enriched dataset containing both sales quantity and selling price.

### Day 6 — Weekly Demand Mart

Created `mart_weekly_demand`.

The model aggregates daily sales into weekly demand metrics.

### Weekly Metrics

The model produces:

- `total_sales_quantity`
- `avg_daily_sales`
- `avg_sell_price`
- `sales_days`
- `week_start_date`
- `week_end_date`

The aggregation is performed by:

- Item
- Department
- Category
- Store
- State
- Retail week

---

## Transformation Flow

Raw M5 Data

↓

BigQuery Sources

↓

Daily Sales Transformation

↓

Calendar Enrichment

↓

Price Enrichment

↓

Weekly Demand Aggregation

↓

`mart_weekly_demand`

↓

Forecasting Pipeline

---

## dbt Documentation

dbt documentation was generated successfully using:

bash
dbt docs generate