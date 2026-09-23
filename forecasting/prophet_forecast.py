import os
import pandas as pd
from google.cloud import bigquery
from prophet import Prophet


# ==========================================
# Week 3 Day 1 — Production Prophet Model
# ==========================================

PROJECT_ID = "sage-sylph-508507-m2"

PRODUCT_ID = "HOBBIES_1_001_CA_1_validation"

OUTPUT_DIR = "outputs"


def get_m5_data():
    """Read one product's historical M5 sales."""

    client = bigquery.Client(
        project=PROJECT_ID
    )

    day_columns = ", ".join(
        [f"d_{i}" for i in range(1, 1914)]
    )

    query = f"""
    SELECT
        id,
        item_id,
        store_id,
        state_id,
        {day_columns}
    FROM `{PROJECT_ID}.m5_raw.sales_train_validation`
    WHERE id = "{PRODUCT_ID}"
    """

    print("\nReading M5 sales from BigQuery...")

    return client.query(query).to_dataframe()


def get_calendar():
    """Read M5 calendar and event information."""

    client = bigquery.Client(
        project=PROJECT_ID
    )

    query = f"""
    SELECT
        d,
        date,
        event_name_1,
        event_type_1,
        event_name_2,
        event_type_2
    FROM `{PROJECT_ID}.m5_raw.calendar`
    ORDER BY date
    """

    print("Reading M5 calendar...")

    calendar = client.query(
        query
    ).to_dataframe()

    calendar["date"] = pd.to_datetime(
        calendar["date"]
    )

    return calendar


def prepare_data(
    sales_df,
    calendar_df
):
    """Convert M5 wide-format sales into daily data."""

    sales_row = sales_df.iloc[0]

    records = []

    for i in range(1, 1914):

        day = f"d_{i}"

        records.append(
            {
                "d": day,
                "y": sales_row[day]
            }
        )

    sales_daily = pd.DataFrame(records)

    df = sales_daily.merge(
        calendar_df,
        on="d",
        how="left"
    )

    df["ds"] = pd.to_datetime(
        df["date"]
    )

    df["y"] = pd.to_numeric(
        df["y"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["ds", "y"]
    )

    return df


def create_holidays(calendar_df):
    """Create Prophet holiday dataframe from M5 events."""

    holidays = []

    for _, row in calendar_df.iterrows():

        date = row["date"]

        event_1 = row["event_name_1"]
        event_2 = row["event_name_2"]

        if pd.notna(event_1):
            holidays.append(
                {
                    "holiday": str(event_1),
                    "ds": date
                }
            )

        if pd.notna(event_2):
            holidays.append(
                {
                    "holiday": str(event_2),
                    "ds": date
                }
            )

    holidays_df = pd.DataFrame(
        holidays
    )

    if holidays_df.empty:
        return None

    holidays_df = holidays_df.drop_duplicates()

    return holidays_df


def train_model(
    historical_data,
    holidays_df
):
    """Train Prophet with weekly/yearly seasonality and M5 events."""

    print("\nTraining production Prophet model...")

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        holidays=holidays_df,
        interval_width=0.95
    )

    model.fit(
        historical_data[["ds", "y"]]
    )

    return model


def generate_forecast(model):
    """Generate next 30 days of demand."""

    print("\nGenerating 30-day forecast...")

    future = model.make_future_dataframe(
        periods=30,
        freq="D"
    )

    forecast = model.predict(
        future
    )

    forecast = forecast[
        [
            "ds",
            "yhat",
            "yhat_lower",
            "yhat_upper"
        ]
    ]

    # Retail demand cannot be negative.
    forecast["yhat"] = (
        forecast["yhat"]
        .clip(lower=0)
    )

    forecast["yhat_lower"] = (
        forecast["yhat_lower"]
        .clip(lower=0)
    )

    forecast["yhat_upper"] = (
        forecast["yhat_upper"]
        .clip(lower=0)
    )

    return forecast


def save_forecast(forecast):
    """Save forecast as CSV."""

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    output_file = os.path.join(
        OUTPUT_DIR,
        "prophet_forecast.csv"
    )

    forecast.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nForecast saved to: {output_file}"
    )


if __name__ == "__main__":

    print("=" * 60)
    print("WEEK 3 DAY 1 — PRODUCTION PROPHET FORECASTING")
    print("=" * 60)

    # Step 1 — M5 sales
    sales_df = get_m5_data()

    print(
        f"Product: {PRODUCT_ID}"
    )

    # Step 2 — Calendar
    calendar_df = get_calendar()

    # Step 3 — Prepare historical data
    historical_data = prepare_data(
        sales_df,
        calendar_df
    )

    print(
        f"\nHistorical records: "
        f"{len(historical_data)}"
    )

    # Step 4 — Create M5 holiday events
    holidays_df = create_holidays(
        calendar_df
    )

    if holidays_df is not None:
        print(
            f"M5 holiday events: "
            f"{len(holidays_df)}"
        )
    else:
        print(
            "No M5 holiday events found."
        )

    # Step 5 — Train Prophet
    model = train_model(
        historical_data,
        holidays_df
    )

    # Step 6 — Forecast
    forecast = generate_forecast(
        model
    )

    # Only show future 30 days
    future_forecast = forecast.tail(30)

    print("\n30-DAY DEMAND FORECAST")
    print("=" * 60)

    print(
        future_forecast.to_string(
            index=False
        )
    )

    # Step 7 — Save
    save_forecast(
        forecast
    )

    print("\n" + "=" * 60)
    print("WEEK 3 DAY 1 COMPLETED")
    print("=" * 60)