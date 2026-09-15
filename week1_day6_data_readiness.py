from google.cloud import bigquery
from datetime import datetime

# ============================================================
# WEEK 1 - DAY 6
# M5 RETAIL DEMAND FORECASTING
# INTELLIGENT DATA READINESS PIPELINE
# ============================================================

PROJECT_ID = "sage-sylph-508507-m2"
DATASET_ID = "m5_raw"

client = bigquery.Client(project=PROJECT_ID)


def run_query(query):
    return list(client.query(query).result())


def header(title):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


# ============================================================
# 1. SCHEMA VALIDATION
# ============================================================

def validate_schema():

    header("1. SCHEMA VALIDATION")

    expected_columns = {
        "calendar": [
            "date",
            "wm_yr_wk",
            "wday",
            "month",
            "year"
        ],

        "sell_prices": [
            "store_id",
            "item_id",
            "wm_yr_wk",
            "sell_price"
        ],

        "sales_train_validation": [
            "id",
            "item_id",
            "dept_id",
            "cat_id",
            "store_id",
            "state_id"
        ]
    }

    passed = True

    for table_name, required_columns in expected_columns.items():

        query = f"""
        SELECT column_name
        FROM `{PROJECT_ID}.{DATASET_ID}.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = '{table_name}'
        """

        actual_columns = {
            row.column_name
            for row in run_query(query)
        }

        missing = [
            column
            for column in required_columns
            if column not in actual_columns
        ]

        if not missing:
            print(f"PASS: {table_name} schema is valid.")
        else:
            print(
                f"FAIL: {table_name} missing columns: {missing}"
            )
            passed = False

    return passed


# ============================================================
# 2. CALENDAR READINESS
# ============================================================

def validate_calendar():

    header("2. CALENDAR READINESS")

    table = f"`{PROJECT_ID}.{DATASET_ID}.calendar`"

    query = f"""
    SELECT
        COUNT(*) AS total_rows,
        COUNT(DISTINCT date) AS unique_dates,
        COUNTIF(date IS NULL) AS null_dates,
        MIN(date) AS min_date,
        MAX(date) AS max_date
    FROM {table}
    """

    result = run_query(query)[0]

    print(f"Rows          : {result.total_rows:,}")
    print(f"Unique dates  : {result.unique_dates:,}")
    print(f"NULL dates    : {result.null_dates:,}")
    print(f"Date range    : {result.min_date} to {result.max_date}")

    passed = (
        result.total_rows == result.unique_dates
        and result.null_dates == 0
    )

    if passed:
        print("PASS: Calendar is ready for forecasting.")
    else:
        print("WARNING: Calendar requires review.")

    return passed


# ============================================================
# 3. SALES READINESS
# ============================================================

def validate_sales():

    header("3. SALES DATA READINESS")

    table = f"`{PROJECT_ID}.{DATASET_ID}.sales_train_validation`"

    query = f"""
    SELECT
        COUNT(*) AS total_rows,
        COUNT(DISTINCT id) AS unique_ids,
        COUNTIF(item_id IS NULL) AS null_items,
        COUNTIF(store_id IS NULL) AS null_stores,
        COUNTIF(dept_id IS NULL) AS null_departments,
        COUNTIF(cat_id IS NULL) AS null_categories,
        COUNTIF(d_1 < 0) AS negative_sales
    FROM {table}
    """

    result = run_query(query)[0]

    print(f"Rows              : {result.total_rows:,}")
    print(f"Unique IDs        : {result.unique_ids:,}")
    print(f"NULL item IDs     : {result.null_items:,}")
    print(f"NULL store IDs    : {result.null_stores:,}")
    print(f"NULL departments  : {result.null_departments:,}")
    print(f"NULL categories   : {result.null_categories:,}")
    print(f"Negative sales    : {result.negative_sales:,}")

    passed = (
        result.total_rows == result.unique_ids
        and result.null_items == 0
        and result.null_stores == 0
        and result.null_departments == 0
        and result.null_categories == 0
        and result.negative_sales == 0
    )

    if passed:
        print("PASS: Sales data is structurally ready.")
    else:
        print("WARNING: Sales data requires review.")

    return passed


# ============================================================
# 4. PRICE READINESS
# ============================================================

def validate_prices():

    header("4. PRICING DATA READINESS")

    table = f"`{PROJECT_ID}.{DATASET_ID}.sell_prices`"

    query = f"""
    SELECT
        COUNT(*) AS total_rows,
        COUNTIF(store_id IS NULL) AS null_stores,
        COUNTIF(item_id IS NULL) AS null_items,
        COUNTIF(wm_yr_wk IS NULL) AS null_weeks,
        COUNTIF(sell_price IS NULL) AS null_prices,
        COUNTIF(sell_price <= 0) AS invalid_prices,
        MIN(sell_price) AS min_price,
        MAX(sell_price) AS max_price,
        AVG(sell_price) AS avg_price
    FROM {table}
    """

    result = run_query(query)[0]

    print(f"Rows              : {result.total_rows:,}")
    print(f"NULL stores       : {result.null_stores:,}")
    print(f"NULL items        : {result.null_items:,}")
    print(f"NULL weeks        : {result.null_weeks:,}")
    print(f"NULL prices       : {result.null_prices:,}")
    print(f"Invalid prices    : {result.invalid_prices:,}")
    print(f"Minimum price     : {result.min_price}")
    print(f"Maximum price     : {result.max_price}")
    print(f"Average price     : {result.avg_price:.2f}")

    passed = (
        result.null_stores == 0
        and result.null_items == 0
        and result.null_weeks == 0
        and result.null_prices == 0
        and result.invalid_prices == 0
    )

    if passed:
        print("PASS: Pricing data is ready.")
    else:
        print("WARNING: Pricing data requires review.")

    return passed


# ============================================================
# 5. ITEM REFERENTIAL INTEGRITY
# ============================================================

def validate_item_relationship():

    header("5. SALES ↔ PRICE ITEM INTEGRITY")

    sales = f"`{PROJECT_ID}.{DATASET_ID}.sales_train_validation`"
    prices = f"`{PROJECT_ID}.{DATASET_ID}.sell_prices`"

    query = f"""
    SELECT COUNT(*) AS unmatched_items
    FROM (
        SELECT DISTINCT item_id
        FROM {sales}
    ) s
    LEFT JOIN (
        SELECT DISTINCT item_id
        FROM {prices}
    ) p
    USING (item_id)
    WHERE p.item_id IS NULL
    """

    unmatched = run_query(query)[0].unmatched_items

    print(f"Unmatched items: {unmatched:,}")

    passed = unmatched == 0

    if passed:
        print("PASS: Every sales item exists in pricing data.")
    else:
        print("WARNING: Some sales items have no pricing record.")

    return passed


# ============================================================
# 6. STORE REFERENTIAL INTEGRITY
# ============================================================

def validate_store_relationship():

    header("6. SALES ↔ PRICE STORE INTEGRITY")

    sales = f"`{PROJECT_ID}.{DATASET_ID}.sales_train_validation`"
    prices = f"`{PROJECT_ID}.{DATASET_ID}.sell_prices`"

    query = f"""
    SELECT COUNT(*) AS unmatched_stores
    FROM (
        SELECT DISTINCT store_id
        FROM {sales}
    ) s
    LEFT JOIN (
        SELECT DISTINCT store_id
        FROM {prices}
    ) p
    USING (store_id)
    WHERE p.store_id IS NULL
    """

    unmatched = run_query(query)[0].unmatched_stores

    print(f"Unmatched stores: {unmatched:,}")

    passed = unmatched == 0

    if passed:
        print("PASS: Every sales store exists in pricing data.")
    else:
        print("WARNING: Some sales stores have no pricing records.")

    return passed


# ============================================================
# 7. ANOMALY DETECTION
# ============================================================

def anomaly_detection():

    header("7. ANOMALY DETECTION")

    prices = f"`{PROJECT_ID}.{DATASET_ID}.sell_prices`"

    price_query = f"""
    SELECT
        COUNTIF(sell_price <= 0) AS invalid_prices,
        COUNTIF(sell_price > 100) AS high_price_records
    FROM {prices}
    """

    price_result = run_query(price_query)[0]

    sales = f"`{PROJECT_ID}.{DATASET_ID}.sales_train_validation`"

    sales_query = f"""
    SELECT
        COUNTIF(d_1 < 0) AS negative_sales,
        COUNTIF(d_1 > 100) AS high_sales_records
    FROM {sales}
    """

    sales_result = run_query(sales_query)[0]

    print(f"Invalid prices      : {price_result.invalid_prices:,}")
    print(f"Prices > 100        : {price_result.high_price_records:,}")
    print(f"Negative sales      : {sales_result.negative_sales:,}")
    print(f"Sales > 100         : {sales_result.high_sales_records:,}")

    # High values are reported but not treated as errors.
    # They may represent legitimate retail observations.

    if price_result.high_price_records > 0:
        print(
            "INFO: High-price records detected; "
            "retained because they are not automatically invalid."
        )

    if sales_result.high_sales_records > 0:
        print(
            "INFO: High-sales records detected; "
            "retained because they may represent legitimate demand."
        )

    passed = (
        price_result.invalid_prices == 0
        and sales_result.negative_sales == 0
    )

    if passed:
        print("PASS: No critical anomalies detected.")
    else:
        print("WARNING: Critical anomalies detected.")

    return passed


# ============================================================
# 8. AUTOMATED QUALITY SCORE
# ============================================================

def calculate_quality_score(results):

    header("8. AUTOMATED DATA QUALITY SCORE")

    passed = sum(results)
    total = len(results)

    score = (passed / total) * 100

    print(f"Checks passed : {passed}/{total}")
    print(f"Quality Score : {score:.0f}/100")

    if score == 100:
        print("STATUS: EXCELLENT")
    elif score >= 90:
        print("STATUS: VERY GOOD")
    elif score >= 75:
        print("STATUS: ACCEPTABLE")
    else:
        print("STATUS: NEEDS REVIEW")

    return score


# ============================================================
# 9. DBT HANDOFF READINESS
# ============================================================

def dbt_handoff():

    header("9. DBT HANDOFF READINESS")

    print("Source dataset      : m5_raw")
    print("Calendar source     : calendar")
    print("Pricing source      : sell_prices")
    print("Sales source        : sales_train_validation")
    print()
    print("Recommended dbt layers:")
    print("  staging/")
    print("      stg_calendar")
    print("      stg_sell_prices")
    print("      stg_sales")
    print()
    print("  intermediate/")
    print("      int_daily_sales")
    print("      int_sales_with_prices")
    print()
    print("  marts/")
    print("      mart_weekly_demand")
    print("      mart_monthly_demand")
    print("      mart_store_demand")
    print("      mart_product_demand")
    print()
    print("PASS: Raw data is ready for Week 2 dbt transformations.")


# ============================================================
# 10. GENERATE LOCAL READINESS REPORT
# ============================================================

def generate_report(score, results):

    header("10. GENERATE DAY 6 READINESS REPORT")

    report_file = "week1_day6_data_readiness_report.md"

    status = "READY" if score >= 90 else "REVIEW REQUIRED"

    report = f"""# M5 Retail Demand Forecasting
## Week 1 - Day 6 Data Readiness Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Data Quality

- Quality Score: **{score:.0f}/100**
- Validation Checks: **{sum(results)}/{len(results)}**
- Overall Status: **{status}**

## Validation Areas

- Schema validation
- Calendar readiness
- Sales data readiness
- Pricing data readiness
- Item referential integrity
- Store referential integrity
- Critical anomaly detection

## Source Tables

- `m5_raw.calendar`
- `m5_raw.sell_prices`
- `m5_raw.sales_train_validation`

## Architecture

Raw M5 Dataset
→ Data Quality Validation
→ Data Readiness Assessment
→ dbt Staging
→ dbt Transformations
→ Forecasting Models
→ Inventory Optimization

## Important Findings

No critical negative sales or invalid prices were detected.

High-value price and sales records were identified as anomalies for monitoring,
but they were retained because they may represent legitimate retail activity.

## Week 2 Handoff

The validated M5 source data is ready for dbt staging and transformation.

## Permission Note

The current user account has read/query access to the source dataset but does
not have permission to create tables in `m5_raw`. Therefore, Day 6 performs
read-only validation and produces a local readiness report. Table creation
and transformation will be handled during the dbt stage with the appropriate
warehouse permissions.

## Final Status

**WEEK 1 - DAY 6 COMPLETED SUCCESSFULLY**
"""

    with open(report_file, "w", encoding="utf-8") as file:
        file.write(report)

    print(f"PASS: Report generated -> {report_file}")


# ============================================================
# MAIN
# ============================================================

print("\n" + "#" * 72)
print("WEEK 1 - DAY 6")
print("M5 RETAIL DEMAND FORECASTING")
print("INTELLIGENT DATA READINESS PIPELINE")
print("#" * 72)

try:

    results = []

    results.append(validate_schema())
    results.append(validate_calendar())
    results.append(validate_sales())
    results.append(validate_prices())
    results.append(validate_item_relationship())
    results.append(validate_store_relationship())
    results.append(anomaly_detection())

    score = calculate_quality_score(results)

    if score < 90:
        raise RuntimeError(
            "Data quality score is below 90. Review failed checks."
        )

    dbt_handoff()

    generate_report(score, results)

    header("FINAL DAY 6 STATUS")

    print("PASS: Schema validation")
    print("PASS: Calendar validation")
    print("PASS: Sales validation")
    print("PASS: Pricing validation")
    print("PASS: Item referential integrity")
    print("PASS: Store referential integrity")
    print("PASS: Anomaly detection")
    print(f"PASS: Data Quality Score = {score:.0f}/100")
    print("PASS: Readiness report generated")
    print("PASS: Raw BigQuery tables preserved")
    print("PASS: No additional BigQuery permissions required")
    print("PASS: Week 2 dbt handoff ready")

    print("\n" + "=" * 72)
    print("WEEK 1 - DAY 6 COMPLETED SUCCESSFULLY")
    print("=" * 72)

except Exception as error:

    header("DAY 6 FAILED")

    print("ERROR:")
    print(error)