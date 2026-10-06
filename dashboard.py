
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
# RECOMMENDED STOCK
# ============================================================

st.subheader("📦 Recommended Stock")

recommended_stock = selected_forecast["yhat"].sum()

recommended_stock = max(
    0,
    round(recommended_stock)
)

safety_stock = round(
    recommended_stock * 0.20
)

total_recommended_stock = (
    recommended_stock + safety_stock
)

stock_col1, stock_col2, stock_col3 = st.columns(3)

with stock_col1:

    st.metric(
        "Forecasted Demand",
        f"{recommended_stock} units"
    )

with stock_col2:

    st.metric(
        "Safety Stock",
        f"{safety_stock} units"
    )

with stock_col3:

    st.metric(
        "Recommended Stock",
        f"{total_recommended_stock} units"
    )

    # ============================================================
# RESTOCKING RECOMMENDATION
# ============================================================

st.subheader("🔄 Restocking Recommendation")

if total_recommended_stock > 0:

    restock_status = "Restock Recommended"

    restock_message = (
        f"Maintain approximately "
        f"{total_recommended_stock} units "
        f"for the selected forecast period."
    )

else:

    restock_status = "No Restock Required"

    restock_message = (
        "No additional stock is recommended "
        "for the selected forecast period."
    )

st.info(
    f"**{restock_status}**\n\n"
    f"{restock_message}"
)
# ============================================================
# RESTOCK PRIORITY
# ============================================================

st.subheader("🚨 Restock Priority")

if total_recommended_stock >= 100:
    priority = "High"
    priority_message = "High stock requirement — prioritize replenishment."

elif total_recommended_stock >= 50:
    priority = "Medium"
    priority_message = "Moderate stock requirement — monitor inventory."

else:
    priority = "Low"
    priority_message = "Low stock requirement — routine monitoring is sufficient."

priority_col1, priority_col2 = st.columns(2)

with priority_col1:
    st.metric(
        "Priority",
        priority
    )

with priority_col2:
    st.info(priority_message)
    # ============================================================
# WHAT-IF SCENARIO SIMULATOR
# ============================================================

st.subheader("🔮 What-If Scenario Simulator")

scenario_col1, scenario_col2 = st.columns(2)

with scenario_col1:

    price_change = st.slider(
        "💰 Price Change (%)",
        min_value=-30,
        max_value=30,
        value=0,
        step=5
    )

with scenario_col2:

    promotion_impact = st.slider(
        "📢 Promotion Impact (%)",
        min_value=0,
        max_value=50,
        value=0,
        step=5
    )
    # ============================================================
# WHAT-IF DEMAND CALCULATION
# ============================================================

base_demand = selected_forecast["yhat"].sum()

price_effect = 1 - (price_change / 100)

promotion_effect = 1 + (promotion_impact / 100)

what_if_demand = (
    base_demand
    * price_effect
    * promotion_effect
)

what_if_demand = max(
    0,
    round(what_if_demand)
)

st.markdown("### 📊 Scenario Result")

result_col1, result_col2 = st.columns(2)

with result_col1:

    st.metric(
        "Base Forecast",
        f"{round(base_demand)} units"
    )

with result_col2:

    st.metric(
        "What-If Forecast",
        f"{what_if_demand} units"
    )
    # ============================================================
# WHAT-IF FORECAST COMPARISON
# ============================================================

st.markdown("### 📈 Base vs What-If Forecast")

comparison_df = selected_forecast[
    ["ds", "yhat"]
].copy()

comparison_df["What-If Forecast"] = (
    comparison_df["yhat"]
    * price_effect
    * promotion_effect
)

comparison_df = comparison_df.rename(
    columns={
        "ds": "Date",
        "yhat": "Base Forecast"
    }
)

st.line_chart(
    comparison_df.set_index("Date")[
        ["Base Forecast", "What-If Forecast"]
    ]
)
# ============================================================
# SCENARIO IMPACT SUMMARY
# ============================================================

demand_change = what_if_demand - round(base_demand)

if demand_change > 0:

    impact_message = (
        f"Demand may increase by approximately "
        f"{demand_change} units under this scenario."
    )

elif demand_change < 0:

    impact_message = (
        f"Demand may decrease by approximately "
        f"{abs(demand_change)} units under this scenario."
    )

else:

    impact_message = (
        "No significant demand change under the current scenario."
    )

st.info(
    f"**Scenario Impact:** {impact_message}"
)
# ============================================================
# HOLIDAY / EVENT IMPACT
# ============================================================

st.markdown("### 📅 Holiday / Event Impact")

holiday_impact = st.slider(
    "Holiday / Event Demand Impact (%)",
    min_value=0,
    max_value=50,
    value=0,
    step=5
)

holiday_effect = 1 + (holiday_impact / 100)

advanced_what_if_demand = (
    what_if_demand * holiday_effect
)

advanced_what_if_demand = max(
    0,
    round(advanced_what_if_demand)
)

st.metric(
    "Adjusted Demand with Event Impact",
    f"{advanced_what_if_demand} units"
)
# ============================================================
# LEAD TIME ADJUSTMENT
# ============================================================

st.markdown("### 🚚 Supplier Lead Time")

lead_time_days = st.slider(
    "Supplier Lead Time (Days)",
    min_value=1,
    max_value=30,
    value=7,
    step=1
)

daily_demand = advanced_what_if_demand / max(
    1,
    len(selected_forecast)
)

lead_time_stock = round(
    daily_demand * lead_time_days
)

st.metric(
    "Lead Time Stock Requirement",
    f"{lead_time_stock} units"
)
# ============================================================
# INVENTORY IMPACT
# ============================================================

st.markdown("### 📦 Inventory Impact")

current_inventory = st.number_input(
    "Current Inventory (Units)",
    min_value=0,
    value=100,
    step=10
)

required_inventory = (
    advanced_what_if_demand
    + lead_time_stock
)

inventory_gap = (
    required_inventory
    - current_inventory
)

if inventory_gap > 0:

    inventory_status = "Additional Stock Required"

else:

    inventory_status = "Inventory Sufficient"

inventory_col1, inventory_col2 = st.columns(2)

with inventory_col1:

    st.metric(
        "Required Inventory",
        f"{required_inventory} units"
    )

with inventory_col2:

    st.metric(
        "Inventory Gap",
        f"{max(0, inventory_gap)} units"
    )

st.info(
    f"**{inventory_status}**"
)
# ============================================================
# UPDATED STOCKOUT RISK
# ============================================================

st.markdown("### ⚠️ Updated Stockout Risk")

if required_inventory > 0:

    stockout_ratio = (
        inventory_gap / required_inventory
    )

else:

    stockout_ratio = 0

stockout_risk = max(
    0,
    min(
        100,
        round(stockout_ratio * 100)
    )
)

if stockout_risk >= 70:

    risk_level = "High"

elif stockout_risk >= 40:

    risk_level = "Medium"

else:

    risk_level = "Low"

risk_col1, risk_col2 = st.columns(2)

with risk_col1:

    st.metric(
        "Stockout Risk",
        f"{stockout_risk}%"
    )

with risk_col2:

    st.metric(
        "Risk Level",
        risk_level
    )

st.progress(
    stockout_risk / 100
)
# ============================================================
# SCENARIO RECOMMENDATION
# ============================================================

st.markdown("### 💡 Scenario Recommendation")

if stockout_risk >= 70:

    recommendation = (
        "High stockout risk detected. "
        "Increase inventory and prioritize replenishment."
    )

elif stockout_risk >= 40:

    recommendation = (
        "Moderate stockout risk. "
        "Monitor inventory and consider early replenishment."
    )

else:

    recommendation = (
        "Low stockout risk. "
        "Current inventory appears sufficient for the scenario."
    )

st.success(
    f"**Recommendation:** {recommendation}"
)
# ============================================================
# PRODUCT PRIORITY
# ============================================================

st.markdown("### 🎯 Product Priority")

priority_score = min(
    100,
    round(
        (stockout_risk * 0.6)
        + (min(demand_change, 100) * 0.4)
    )
)

if priority_score >= 70:

    priority_status = "🔴 High Priority"

elif priority_score >= 40:

    priority_status = "🟡 Medium Priority"

else:

    priority_status = "🟢 Low Priority"

priority_col1, priority_col2 = st.columns(2)

with priority_col1:

    st.metric(
        "Priority Score",
        f"{priority_score}/100"
    )

with priority_col2:

    st.metric(
        "Priority Status",
        priority_status
    )
    # ============================================================
# HIGH-RISK IDENTIFICATION
# ============================================================

st.markdown("### ⚠️ Risk Classification")

if stockout_risk >= 70:
    risk_status = "🔴 High Risk"
    risk_message = "Immediate inventory attention required."

elif stockout_risk >= 40:
    risk_status = "🟡 Medium Risk"
    risk_message = "Inventory should be monitored closely."

else:
    risk_status = "🟢 Low Risk"
    risk_message = "Inventory level is currently under control."

risk_col1, risk_col2 = st.columns(2)

with risk_col1:
    st.metric(
        "Risk Status",
        risk_status
    )

with risk_col2:
    st.info(risk_message)
    # ============================================================
# OVERSTOCK DETECTION
# ============================================================

st.markdown("### 📦 Overstock Detection")

overstock_threshold = round(
    advanced_what_if_demand * 1.5
)

if current_inventory > overstock_threshold:

    overstock_status = "🔴 Overstock Detected"

    overstock_message = (
        f"Current inventory is approximately "
        f"{current_inventory - overstock_threshold} units "
        f"above the recommended threshold."
    )

else:

    overstock_status = "🟢 No Overstock"

    overstock_message = (
        "Current inventory is within the recommended range."
    )

overstock_col1, overstock_col2 = st.columns(2)

with overstock_col1:

    st.metric(
        "Overstock Status",
        overstock_status
    )

with overstock_col2:

    st.info(overstock_message)
    # ============================================================
# RECOMMENDED ACTION
# ============================================================

st.markdown("### 💡 Recommended Action")

if stockout_risk >= 70:

    recommended_action = (
        "🚨 Increase inventory immediately and "
        "prioritize replenishment."
    )

elif stockout_risk >= 40:

    recommended_action = (
        "⚠️ Monitor inventory closely and "
        "consider early replenishment."
    )

elif current_inventory > overstock_threshold:

    recommended_action = (
        "📦 Reduce excess inventory and "
        "avoid unnecessary replenishment."
    )

else:

    recommended_action = (
        "✅ Maintain current inventory levels "
        "and continue regular monitoring."
    )

st.success(
    f"**Recommended Action:** {recommended_action}"
)
# ============================================================
# INVENTORY ACTION SUMMARY
# ============================================================

st.markdown("### 📊 Inventory Action Summary")

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:

    st.metric(
        "Priority Score",
        f"{priority_score}/100"
    )

with summary_col2:

    st.metric(
        "Stockout Risk",
        f"{stockout_risk}%"
    )

with summary_col3:

    if current_inventory > overstock_threshold:
        inventory_condition = "Overstock"
    elif inventory_gap > 0:
        inventory_condition = "Shortage"
    else:
        inventory_condition = "Balanced"

    st.metric(
        "Inventory Condition",
        inventory_condition
    )

st.info(
    f"**Action Summary:** "
    f"{priority_status} | "
    f"{risk_status} | "
    f"{inventory_condition}"
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
