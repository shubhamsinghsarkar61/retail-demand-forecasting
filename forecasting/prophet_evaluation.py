import pandas as pd
import numpy as np
from google.cloud import bigquery
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error

PROJECT_ID = "sage-sylph-508507-m2"
PRODUCT_ID = "HOBBIES_1_001_CA_1_validation"

TRAIN_DAYS = 1793
TEST_DAYS = 120


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

    return df


def create_holidays(calendar_df):

    holidays = []

    for _, row in calendar_df.iterrows():

        date = row["date"]

        event_1 = row["event_name_1"]
        event_2 = row["event_name_2"]

        if pd.notna(event_1):

            holidays.append({
                "holiday": str(event_1),
                "ds": date
            })

        if pd.notna(event_2):

            holidays.append({
                "holiday": str(event_2),
                "ds": date
            })

    holidays_df = pd.DataFrame(holidays)

    if holidays_df.empty:
        return None

    return holidays_df.drop_duplicates()


def calculate_metrics(actual, predicted):

    mae = mean_absolute_error(
        actual,
        predicted
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predicted
        )
    )

    non_zero = actual != 0

    if non_zero.sum() > 0:

        mape = np.mean(
            np.abs(
                (actual[non_zero] -
                 predicted[non_zero])
                /
                actual[non_zero]
            )
        ) * 100

    else:

        mape = np.nan

    return mae, rmse, mape


if __name__ == "__main__":

    print("=" * 60)
    print("WEEK 3 DAY 2 — PROPHET MODEL EVALUATION")
    print("=" * 60)

    sales_df = get_m5_data()

    print(f"Product: {PRODUCT_ID}")

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

    train = historical_data.iloc[
        :TRAIN_DAYS
    ][["ds", "y"]].copy()

    test = historical_data.iloc[
        TRAIN_DAYS:
    ][["ds", "y"]].copy()

    print(
        f"\nTraining records: "
        f"{len(train)}"
    )

    print(
        f"Testing records: "
        f"{len(test)}"
    )

    print("\nTraining Prophet model...")

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        holidays=holidays_df,
        interval_width=0.95
    )

    model.fit(train)

    print("\nGenerating test-period forecast...")

    future = model.make_future_dataframe(
        periods=TEST_DAYS,
        freq="D"
    )

    forecast = model.predict(
        future
    )

    predictions = forecast[
        ["ds", "yhat"]
    ].tail(TEST_DAYS)

    predictions["yhat"] = predictions[
        "yhat"
    ].clip(lower=0)

    evaluation = test.merge(
        predictions,
        on="ds",
        how="inner"
    )

    mae, rmse, mape = calculate_metrics(
        evaluation["y"].values,
        evaluation["yhat"].values
    )

    print("\nMODEL EVALUATION")
    print("=" * 60)

    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"MAPE : {mape:.2f}%")

    print("\nActual vs Predicted Sample")
    print("=" * 60)

    print(
        evaluation.head(10).to_string(
            index=False
        )
    )

    output_file = (
        "outputs/prophet_evaluation.csv"
    )

    evaluation.to_csv(
        output_file,
        index=False
    )

    metrics_file = (
        "outputs/prophet_metrics.csv"
    )

    metrics_df = pd.DataFrame({
        "product_id": [PRODUCT_ID],
        "train_days": [TRAIN_DAYS],
        "test_days": [TEST_DAYS],
        "MAE": [mae],
        "RMSE": [rmse],
        "MAPE": [mape]
    })

    metrics_df.to_csv(
        metrics_file,
        index=False
    )

    print(
        f"\nEvaluation saved to: "
        f"{output_file}"
    )

    print(
        f"Metrics saved to: "
        f"{metrics_file}"
    )

    print("\n" + "=" * 60)
    print("WEEK 3 DAY 2 EVALUATION COMPLETED")
    print("=" * 60)