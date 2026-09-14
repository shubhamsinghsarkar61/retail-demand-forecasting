from google.cloud import bigquery

# ============================================================
# WEEK 1 - DAY 4
# M5 RETAIL DEMAND FORECASTING
# DATA QUALITY & VALIDATION
# ============================================================

PROJECT_ID = "sage-sylph-508507-m2"
DATASET_ID = "m5_raw"

client = bigquery.Client(project=PROJECT_ID)

# ------------------------------------------------------------
# Helper function
# ------------------------------------------------------------

def run_query(query):
    """Execute a BigQuery query and return the result."""
    return list(client.query(query).result())


def print_header(table_name):
    print("\n" + "=" * 70)
    print(f"DATA QUALITY CHECK: {table_name}")
    print("=" * 70)


# ============================================================
# 1. CALENDAR TABLE
# ============================================================

def check_calendar():

    table = f"`{PROJECT_ID}.{DATASET_ID}.calendar`"

    print_header("calendar")

    # Row count
    query = f"""
        SELECT COUNT(*) AS row_count
        FROM {table}
    """

    row_count = run_query(query)[0].row_count
    print(f"\nRows: {row_count:,}")

    # Duplicate date check
    query = f"""
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT date) AS unique_dates
        FROM {table}
    """

    result = run_query(query)[0]

    print("\n--- 1. Duplicate Date Check ---")

    if result.total_rows == result.unique_dates:
        print("PASS: No duplicate dates found.")
    else:
        print(
            f"WARNING: {result.total_rows - result.unique_dates:,} "
            "duplicate dates found."
        )

    # Date range
    query = f"""
        SELECT
            MIN(date) AS minimum_date,
            MAX(date) AS maximum_date
        FROM {table}
    """

    result = run_query(query)[0]

    print("\n--- 2. Date Validation ---")
    print(f"Minimum date: {result.minimum_date}")
    print(f"Maximum date: {result.maximum_date}")

    # Null checks for important columns
    query = f"""
        SELECT
            COUNTIF(date IS NULL) AS null_date,
            COUNTIF(wm_yr_wk IS NULL) AS null_week,
            COUNTIF(wday IS NULL) AS null_wday,
            COUNTIF(month IS NULL) AS null_month,
            COUNTIF(year IS NULL) AS null_year
        FROM {table}
    """

    result = run_query(query)[0]

    print("\n--- 3. Required Field Check ---")

    nulls = {
        "date": result.null_date,
        "wm_yr_wk": result.null_week,
        "wday": result.null_wday,
        "month": result.null_month,
        "year": result.null_year,
    }

    has_nulls = False

    for column, count in nulls.items():
        if count > 0:
            print(f"WARNING: {column} has {count:,} NULL values.")
            has_nulls = True

    if not has_nulls:
        print("PASS: No NULL values in required calendar fields.")

    # Event NULLs are expected
    print("\n--- 4. Event Field Validation ---")
    print(
        "INFO: NULL event_name/event_type values are expected "
        "for dates without events."
    )


# ============================================================
# 2. SELL PRICES TABLE
# ============================================================

def check_sell_prices():

    table = f"`{PROJECT_ID}.{DATASET_ID}.sell_prices`"

    print_header("sell_prices")

    # Row count
    query = f"""
        SELECT COUNT(*) AS row_count
        FROM {table}
    """

    row_count = run_query(query)[0].row_count
    print(f"\nRows: {row_count:,}")

    # NULL check
    query = f"""
        SELECT
            COUNTIF(store_id IS NULL) AS null_store,
            COUNTIF(item_id IS NULL) AS null_item,
            COUNTIF(wm_yr_wk IS NULL) AS null_week,
            COUNTIF(sell_price IS NULL) AS null_price
        FROM {table}
    """

    result = run_query(query)[0]

    print("\n--- 1. Missing Values ---")

    nulls = {
        "store_id": result.null_store,
        "item_id": result.null_item,
        "wm_yr_wk": result.null_week,
        "sell_price": result.null_price,
    }

    has_nulls = False

    for column, count in nulls.items():
        if count > 0:
            print(f"WARNING: {column} has {count:,} NULL values.")
            has_nulls = True

    if not has_nulls:
        print("PASS: No NULL values in required fields.")

    # Negative price check
    query = f"""
        SELECT COUNT(*) AS negative_prices
        FROM {table}
        WHERE sell_price < 0
    """

    negative_prices = run_query(query)[0].negative_prices

    print("\n--- 2. Price Validation ---")

    if negative_prices == 0:
        print("PASS: No negative prices found.")
    else:
        print(f"WARNING: {negative_prices:,} negative prices found.")

    # Zero price check
    query = f"""
        SELECT COUNT(*) AS zero_prices
        FROM {table}
        WHERE sell_price = 0
    """

    zero_prices = run_query(query)[0].zero_prices

    if zero_prices == 0:
        print("PASS: No zero prices found.")
    else:
        print(f"INFO: {zero_prices:,} records have zero price.")

    # Price range
    query = f"""
        SELECT
            MIN(sell_price) AS minimum_price,
            MAX(sell_price) AS maximum_price,
            AVG(sell_price) AS average_price
        FROM {table}
    """

    result = run_query(query)[0]

    print("\n--- 3. Price Statistics ---")
    print(f"Minimum price: {result.minimum_price}")
    print(f"Maximum price: {result.maximum_price}")
    print(f"Average price: {result.average_price:.2f}")


# ============================================================
# 3. SALES TRAIN VALIDATION TABLE
# ============================================================

def check_sales_validation():

    table = f"`{PROJECT_ID}.{DATASET_ID}.sales_train_validation`"

    print_header("sales_train_validation")

    # Row count
    query = f"""
        SELECT COUNT(*) AS row_count
        FROM {table}
    """

    row_count = run_query(query)[0].row_count
    print(f"\nRows: {row_count:,}")

    # Important identifier NULL checks
    query = f"""
        SELECT
            COUNTIF(id IS NULL) AS null_id,
            COUNTIF(item_id IS NULL) AS null_item,
            COUNTIF(dept_id IS NULL) AS null_department,
            COUNTIF(cat_id IS NULL) AS null_category,
            COUNTIF(store_id IS NULL) AS null_store,
            COUNTIF(state_id IS NULL) AS null_state
        FROM {table}
    """

    result = run_query(query)[0]

    print("\n--- 1. Missing Identifier Values ---")

    nulls = {
        "id": result.null_id,
        "item_id": result.null_item,
        "dept_id": result.null_department,
        "cat_id": result.null_category,
        "store_id": result.null_store,
        "state_id": result.null_state,
    }

    has_nulls = False

    for column, count in nulls.items():
        if count > 0:
            print(f"WARNING: {column} has {count:,} NULL values.")
            has_nulls = True

    if not has_nulls:
        print("PASS: No NULL values in identifier columns.")

    # Duplicate ID check
    query = f"""
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT id) AS unique_ids
        FROM {table}
    """

    result = run_query(query)[0]

    print("\n--- 2. Duplicate ID Check ---")

    if result.total_rows == result.unique_ids:
        print("PASS: No duplicate customer/item IDs found.")
    else:
        print(
            f"WARNING: {result.total_rows - result.unique_ids:,} "
            "duplicate IDs found."
        )

    # Sales columns are d_1, d_2 ... and may contain zeros.
    # Check total sales through BigQuery.
    query = f"""
        SELECT
            SUM(d_1) AS total_d1_sales,
            MIN(d_1) AS minimum_d1_sales,
            MAX(d_1) AS maximum_d1_sales
        FROM {table}
    """

    result = run_query(query)[0]

    print("\n--- 3. Sales Value Validation ---")
    print(f"Minimum d_1 sales: {result.minimum_d1_sales}")
    print(f"Maximum d_1 sales: {result.maximum_d1_sales}")
    print(f"Total d_1 sales: {result.total_d1_sales}")

    if result.minimum_d1_sales >= 0:
        print("PASS: No negative sales values detected in d_1.")
    else:
        print("WARNING: Negative sales values detected in d_1.")


# ============================================================
# 4. SALES TRAIN EVALUATION TABLE
# ============================================================

def check_sales_evaluation():

    table = f"`{PROJECT_ID}.{DATASET_ID}.sales_train_evaluation`"

    print_header("sales_train_evaluation")

    # Row count
    query = f"""
        SELECT COUNT(*) AS row_count
        FROM {table}
    """

    row_count = run_query(query)[0].row_count
    print(f"\nRows: {row_count:,}")

    # Identifier NULL checks
    query = f"""
        SELECT
            COUNTIF(id IS NULL) AS null_id,
            COUNTIF(item_id IS NULL) AS null_item,
            COUNTIF(dept_id IS NULL) AS null_department,
            COUNTIF(cat_id IS NULL) AS null_category,
            COUNTIF(store_id IS NULL) AS null_store,
            COUNTIF(state_id IS NULL) AS null_state
        FROM {table}
    """

    result = run_query(query)[0]

    print("\n--- 1. Missing Identifier Values ---")

    nulls = {
        "id": result.null_id,
        "item_id": result.null_item,
        "dept_id": result.null_department,
        "cat_id": result.null_category,
        "store_id": result.null_store,
        "state_id": result.null_state,
    }

    has_nulls = False

    for column, count in nulls.items():
        if count > 0:
            print(f"WARNING: {column} has {count:,} NULL values.")
            has_nulls = True

    if not has_nulls:
        print("PASS: No NULL values in identifier columns.")

    # Duplicate ID check
    query = f"""
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT id) AS unique_ids
        FROM {table}
    """

    result = run_query(query)[0]

    print("\n--- 2. Duplicate ID Check ---")

    if result.total_rows == result.unique_ids:
        print("PASS: No duplicate IDs found.")
    else:
        print(
            f"WARNING: {result.total_rows - result.unique_ids:,} "
            "duplicate IDs found."
        )

    # Sales validation
    query = f"""
        SELECT
            SUM(d_1) AS total_d1_sales,
            MIN(d_1) AS minimum_d1_sales,
            MAX(d_1) AS maximum_d1_sales
        FROM {table}
    """

    result = run_query(query)[0]

    print("\n--- 3. Sales Value Validation ---")
    print(f"Minimum d_1 sales: {result.minimum_d1_sales}")
    print(f"Maximum d_1 sales: {result.maximum_d1_sales}")
    print(f"Total d_1 sales: {result.total_d1_sales}")

    if result.minimum_d1_sales >= 0:
        print("PASS: No negative sales values detected in d_1.")
    else:
        print("WARNING: Negative sales values detected in d_1.")


# ============================================================
# MAIN PROGRAM
# ============================================================

print("\n" + "#" * 70)
print("WEEK 1 - DAY 4")
print("M5 RETAIL DEMAND FORECASTING")
print("DATA QUALITY & VALIDATION")
print("#" * 70)

try:
    check_calendar()
    check_sell_prices()
    check_sales_validation()
    check_sales_evaluation()

    print("\n" + "=" * 70)
    print("DAY 4 DATA QUALITY CHECKS EXECUTED SUCCESSFULLY")
    print("=" * 70)

except Exception as error:

    print("\n" + "=" * 70)
    print("DAY 4 DATA QUALITY CHECK FAILED")
    print("=" * 70)

    print("\nERROR:")
    print(error)
