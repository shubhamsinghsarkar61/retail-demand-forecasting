
import streamlit as st
import pandas as pd
from pathlib import Path
from google.cloud import bigquery


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Retail Demand Forecasting",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("📊 Retail Demand Forecasting & Inventory Optimization")

st.markdown(
    """
    **AI-powered demand forecasting dashboard**

    Analyze historical sales and future demand forecasts
    for better inventory planning.
    """
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🎛️ Forecast Controls")

store = st.sidebar.selectbox(
    "Store",
    ["CA_1", "CA_2", "CA_3", "CA_4"]
)

department = st.sidebar.selectbox(
    "Department",
    [
        "All Departments",
        "HOBBIES",
        "FOODS",
        "HOUSEHOLD"
    ]
)

forecast_period = st.sidebar.selectbox(
    "Forecast Period",
    [7, 14, 30],
    index=2
)


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

FORECAST_FILE = (
    BASE_DIR
    / "outputs"
    / "prophet_forecast.csv"
)


# ============================================================
# LOAD FORECAST DATA
# ============================================================

if not FORECAST_FILE.exists():

    st.error(
        "Forecast file not found: "
        f"{FORECAST_FILE}"
    )

    st.stop()


forecast_df = pd.read_csv(
    FORECAST_FILE
)


# ============================================================
# PREPARE FORECAST DATA
# ============================================================

forecast_df["ds"] = pd.to_datetime(
    forecast_df["ds"]
)


# ============================================================
# SELECT FORECAST PERIOD
# ============================================================

selected_forecast = forecast_df.head(
    forecast_period
).copy()


# ============================================================
# BIGQUERY CONNECTION
# ============================================================

PROJECT_ID = "sage-sylph-508507-m2"

client = bigquery.Client(
    project=PROJECT_ID
)


# ============================================================
# M5 DAY COLUMNS
# ============================================================

day_columns = ",\n    ".join(
    [f"d_{i}" for i in range(1, 1914)]
)


# ============================================================
# LOAD ACTUAL SALES DATA
# ============================================================

actual_query = f"""
SELECT
    item_id,
    store_id,
    dept_id,
    cat_id,
    state_id,
    {day_columns}
FROM `sage-sylph-508507-m2.m5_raw.sales_train_validation`
WHERE id = 'HOBBIES_1_001_CA_1_validation'
"""


try:

    actual_df = client.query(
        actual_query
    ).to_dataframe()

except Exception as e:

    st.error(
        f"Unable to load actual sales data from BigQuery: {e}"
    )

    st.stop()


# ============================================================
# CHECK ACTUAL DATA
# ============================================================

if actual_df.empty:

    st.error(
        "No actual sales data found for "
        "HOBBIES_1_001_CA_1_validation."
    )

    st.stop()


# ============================================================
# PREPARE ACTUAL SALES DATA
# ============================================================

actual_row = actual_df.iloc[0]

actual_sales = []

for i in range(1, 1914):

    actual_sales.append(
        {
            "day_id": f"d_{i}",
            "sales": actual_row[f"d_{i}"]
        }
    )


actual_sales_df = pd.DataFrame(
    actual_sales
)


# ============================================================
# LOAD M5 CALENDAR
# ============================================================

calendar_query = """
SELECT
    d,
    date
FROM `sage-sylph-508507-m2.m5_raw.calendar`
ORDER BY
    date
"""


try:

    calendar_df = client.query(
        calendar_query
    ).to_dataframe()

except Exception as e:

    st.error(
        f"Unable to load calendar data: {e}"
    )

    st.stop()


calendar_df["date"] = pd.to_datetime(
    calendar_df["date"]
)


# ============================================================
# PREPARE ACTUAL SALES WITH DATES
# ============================================================

actual_sales_df = actual_sales_df.merge(
    calendar_df,
    left_on="day_id",
    right_on="d",
    how="left"
)


actual_sales_df = actual_sales_df[
    [
        "day_id",
        "date",
        "sales"
    ]
]


# ============================================================
# KPI SECTION
# ============================================================

st.subheader("📌 Forecast Summary")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Forecast Days",
        forecast_period
    )


with col2:

    average_demand = selected_forecast[
        "yhat"
    ].mean()

    st.metric(
        "Average Predicted Demand",
        f"{average_demand:.2f}"
    )


with col3:

    total_demand = selected_forecast[
        "yhat"
    ].sum()

    st.metric(
        "Total Predicted Demand",
        f"{total_demand:.2f}"
    )


with col4:

    maximum_demand = selected_forecast[
        "yhat"
    ].max()

    st.metric(
        "Peak Predicted Demand",
        f"{maximum_demand:.2f}"
    )


# ============================================================
# FORECAST VISUALIZATION
# ============================================================

st.subheader("📈 Demand Forecast")

if "yhat" in selected_forecast.columns:

    chart_data = selected_forecast.set_index(
        "ds"
    )

    forecast_chart = pd.DataFrame()

    forecast_chart["Predicted Demand"] = (
        chart_data["yhat"]
    )

    if "yhat_lower" in chart_data.columns:

        forecast_chart["Lower Bound"] = (
            chart_data["yhat_lower"]
        )

    if "yhat_upper" in chart_data.columns:

        forecast_chart["Upper Bound"] = (
            chart_data["yhat_upper"]
        )

    st.line_chart(
        forecast_chart,
        width="stretch"
    )

else:

    st.warning(
        "Forecast prediction column 'yhat' not found."
    )
    # ============================================================
# STOCKOUT RISK
# ============================================================

st.subheader("⚠️ Stockout Risk")

average_forecast = selected_forecast["yhat"].mean()
# Calculate 0-100 stockout risk score

max_forecast = selected_forecast["yhat"].max()

if max_forecast > 0:

    stockout_risk_score = (
        average_forecast / max_forecast
    ) * 100

else:

    stockout_risk_score = 0


stockout_risk_score = min(
    max(stockout_risk_score, 0),
    100
)

if average_forecast <= 2:
    risk_level = "Low"
elif average_forecast <= 5:
    risk_level = "Medium"
else:
    risk_level = "High"

risk_col1, risk_col2, risk_col3 = st.columns(3)

with risk_col1:
    st.metric(
        "Average Forecast Demand",
        f"{average_forecast:.2f}"
    )

with risk_col2:
    st.metric(
        "Stockout Risk",
        risk_level
    )

with risk_col3:
    st.metric(
        "Risk Score",
        f"{stockout_risk_score:.0f}/100"
    )
    st.progress(
    int(stockout_risk_score),
    text=f"Stockout Risk Score: {stockout_risk_score:.0f}/100"
)
# ============================================================
# DEMAND TREND
# ============================================================

st.subheader("📈 Demand Trend")

first_forecast = selected_forecast["yhat"].iloc[0]
last_forecast = selected_forecast["yhat"].iloc[-1]

if last_forecast > first_forecast:

    trend = "Increasing 📈"

elif last_forecast < first_forecast:

    trend = "Decreasing 📉"

else:

    trend = "Stable ➡️"


trend_change = last_forecast - first_forecast

trend_col1, trend_col2 = st.columns(2)

with trend_col1:

    st.metric(
        "Demand Trend",
        trend
    )

with trend_col2:

    st.metric(
        "Demand Change",
        f"{trend_change:+.2f}"
    )

# ============================================================
# ACTUAL VS FORECAST
# ============================================================

st.subheader("📊 Actual vs Forecast")


actual_plot = actual_sales_df[
    [
        "date",
        "sales"
    ]
].copy()


actual_plot = actual_plot.rename(
    columns={
        "sales": "Actual Demand"
    }
)


forecast_plot = selected_forecast[
    [
        "ds",
        "yhat"
    ]
].copy()


forecast_plot = forecast_plot.rename(
    columns={
        "ds": "date",
        "yhat": "Forecast Demand"
    }
)


# Combine actual and forecast data

comparison_df = pd.concat(
    [
        actual_plot[
            [
                "date",
                "Actual Demand"
            ]
        ],
        forecast_plot[
            [
                "date",
                "Forecast Demand"
            ]
        ]
    ],
    ignore_index=True
)


comparison_df = (
    comparison_df
    .groupby("date", as_index=True)
    .sum()
)


# Show comparison chart

st.line_chart(
    comparison_df,
    width="stretch"
)


# ============================================================
# FORECAST TABLE
# ============================================================

st.subheader("📋 Forecast Details")

display_forecast = selected_forecast.copy()

display_forecast["ds"] = (
    display_forecast["ds"]
    .dt.strftime("%Y-%m-%d")
)


columns_to_display = [
    "ds",
    "yhat"
]


if "yhat_lower" in display_forecast.columns:

    columns_to_display.append(
        "yhat_lower"
    )


if "yhat_upper" in display_forecast.columns:

    columns_to_display.append(
        "yhat_upper"
    )


st.dataframe(
    display_forecast[
        columns_to_display
    ],
    width="stretch"
)


# ============================================================
# CURRENT SELECTION
# ============================================================

st.subheader("🎯 Current Selection")

selection_col1, selection_col2 = st.columns(2)


with selection_col1:

    st.write(
        f"**Store:** {store}"
    )
