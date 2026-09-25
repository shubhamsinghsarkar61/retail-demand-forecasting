import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import bigquery
from prophet import Prophet

PROJECT_ID = "sage-sylph-508507-m2"
PRODUCT_ID = "HOBBIES_1_001_CA_1_validation"

OUTPUT_FORECAST = "outputs/prophet_seasonality_forecast.csv"
OUTPUT_COMPONENTS = "outputs/prophet_seasonality_components.png"


def get_m5_data():
    client = bigquery.Client(project=PROJECT_ID)

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
    client = bigquery.Client(project=PROJECT_ID)

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

    calendar = client.query(query).to_dataframe()
    calendar["date"] = pd.to_datetime(calendar["date"])

    return calendar


def prepare_data(sales_df, calendar_df):

    sales_row = sales_df.iloc[0]

    records = []

    for i in range(1, 1914):
        day = f"d_{i}"

        records.append({
            "d": day,
            "y": sales_row[day]
        })

    sales_daily = pd.DataFrame(records)

    df = sales_daily.merge(
        calendar_df,
        on="d",
        how="left"
    )

    df["ds"] = pd.to_datetime(df["date"])

    df["y"] = pd.to_numeric(
        df["y"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["ds", "y"]
    )

    return df[["ds", "y"]]


def create_holidays(calendar_df):

    holidays = []

    for _, row in calendar_df.iterrows():

        if pd.notna(row["event_name_1"]):
            holidays.append({
                "holiday": str(row["event_name_1"]),
                "ds": row["date"]
            })

        if pd.notna(row["event_name_2"]):
            holidays.append({
                "holiday": str(row["event_name_2"]),
                "ds": row["date"]
            })

    holidays_df = pd.DataFrame(holidays)

    if holidays_df.empty:
        return None

    return holidays_df.drop_duplicates()


if __name__ == "__main__":

    print("=" * 60)
    print("WEEK 3 DAY 3 — PROPHET SEASONALITY ANALYSIS")
    print("=" * 60)

    sales_df = get_m5_data()
    calendar_df = get_calendar()

    historical_data = prepare_data(
        sales_df,
        calendar_df
    )

    print(
        f"\nHistorical records: "
        f"{len(historical_data)}"
    )

    holidays_df = create_holidays(
        calendar_df
    )

    print(
        f"M5 holiday events: "
        f"{len(holidays_df)}"
    )

    print("\nTraining Prophet model...")

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        holidays=holidays_df,
        interval_width=0.95
    )

    model.fit(historical_data)

    print("\nGenerating forecast...")

    future = model.make_future_dataframe(
        periods=30,
        freq="D"
    )

    forecast = model.predict(future)

    forecast["yhat"] = forecast["yhat"].clip(
        lower=0
    )

    forecast.to_csv(
        OUTPUT_FORECAST,
        index=False
    )

    print(
        f"\nForecast saved to: "
        f"{OUTPUT_FORECAST}"
    )

    print("\nCreating seasonality components...")

    fig = model.plot_components(
        forecast
    )

    fig.savefig(
        OUTPUT_COMPONENTS,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close("all")

    print(
        f"Components saved to: "
        f"{OUTPUT_COMPONENTS}"
    )

    print("\n" + "=" * 60)
    print("WEEK 3 DAY 3 SEASONALITY ANALYSIS COMPLETED")
    print("=" * 60)