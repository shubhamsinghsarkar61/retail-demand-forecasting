import streamlit as st
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Retail Demand Forecasting",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM HEADER
# --------------------------------------------------

st.title("📊 Retail Demand Forecasting & Inventory Optimization")

st.markdown(
    """
    **AI-powered retail demand intelligence dashboard**

    Analyze historical demand and forecast future sales to support
    better inventory planning and decision-making.
    """
)

st.divider()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("🎛️ Dashboard Controls")

store = st.sidebar.selectbox(
    "Select Store",
    [
        "CA_1",
        "CA_2",
        "CA_3",
        "CA_4",
        "TX_1",
        "TX_2",
        "TX_3",
        "WI_1",
        "WI_2",
        "WI_3"
    ]
)

department = st.sidebar.selectbox(
    "Select Department",
    [
        "All Departments",
        "FOODS",
        "HOBBIES",
        "HOUSEHOLD"
    ]
)

forecast_days = st.sidebar.selectbox(
    "Forecast Period",
    [
        7,
        14,
        30
    ],
    index=2
)

st.sidebar.divider()

st.sidebar.info(
    "Week 4 Day 1 — Dashboard Foundation"
)


# --------------------------------------------------
# LOAD EXISTING FORECAST DATA
# --------------------------------------------------

forecast_file = Path(
    "outputs/prophet_forecast.csv"
)

if forecast_file.exists():

    forecast_df = pd.read_csv(
        forecast_file
    )

    if "ds" in forecast_df.columns:
        forecast_df["ds"] = pd.to_datetime(
            forecast_df["ds"]
        )

    st.success(
        "Forecast data loaded successfully."
    )

else:

    forecast_df = pd.DataFrame()

    st.warning(
        "Forecast file not found."
    )


# --------------------------------------------------
# DASHBOARD SUMMARY
# --------------------------------------------------

st.subheader("📌 Forecast Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Selected Store",
        store
    )

with col2:
    st.metric(
        "Department",
        department
    )

with col3:
    st.metric(
        "Forecast Horizon",
        f"{forecast_days} Days"
    )

with col4:

    if not forecast_df.empty:
        st.metric(
            "Forecast Records",
            len(forecast_df)
        )
    else:
        st.metric(
            "Forecast Records",
            "0"
        )
        # --------------------------------------------------
# APPLY FORECAST PERIOD
# --------------------------------------------------

if not forecast_df.empty and "ds" in forecast_df.columns:

    forecast_df = forecast_df.sort_values("ds")

    selected_forecast = forecast_df.head(
        forecast_days
    ).copy()

else:

    selected_forecast = pd.DataFrame()


# --------------------------------------------------
# CURRENT SELECTION
# --------------------------------------------------

st.divider()

st.subheader("🔎 Current Selection")

selection_col1, selection_col2 = st.columns(2)

with selection_col1:

    st.write(
        f"**Store:** {store}"
    )

    st.write(
        f"**Department:** {department}"
    )

with selection_col2:

    st.write(
        f"**Forecast Period:** "
        f"{forecast_days} days"
    )

    st.write(
        "**Model:** Prophet"
    )


# --------------------------------------------------
# DATA PREVIEW
# --------------------------------------------------

if not forecast_df.empty:

    st.divider()

    st.subheader("📄 Forecast Data Preview")

    st.dataframe(
    selected_forecast,
    use_container_width=True
)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Retail Demand Forecasting & Inventory Optimization | "
    "Week 4 Dashboard"
)