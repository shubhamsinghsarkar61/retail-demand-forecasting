import pandas as pd
import numpy as np

INPUT_FILE = "outputs/prophet_evaluation.csv"
OUTPUT_FILE = "outputs/prophet_metrics_improved.csv"


def calculate_metrics(actual, predicted):

    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    # MAE
    mae = np.mean(np.abs(actual - predicted))

    # RMSE
    rmse = np.sqrt(
        np.mean((actual - predicted) ** 2)
    )

    # MAPE — exclude zero actual values
    non_zero = actual != 0

    if non_zero.sum() > 0:
        mape = np.mean(
            np.abs(
                (actual[non_zero] - predicted[non_zero])
                / actual[non_zero]
            )
        ) * 100
    else:
        mape = np.nan

    # WAPE
    total_actual = np.sum(np.abs(actual))

    if total_actual > 0:
        wape = (
            np.sum(np.abs(actual - predicted))
            / total_actual
        ) * 100
    else:
        wape = np.nan

    # SMAPE
    denominator = (
        np.abs(actual) +
        np.abs(predicted)
    )

    valid = denominator != 0

    if valid.sum() > 0:
        smape = np.mean(
            2 * np.abs(
                actual[valid] - predicted[valid]
            ) / denominator[valid]
        ) * 100
    else:
        smape = np.nan

    return mae, rmse, mape, wape, smape


if __name__ == "__main__":

    print("=" * 60)
    print("WEEK 3 DAY 3 — IMPROVED PROPHET METRICS")
    print("=" * 60)

    print("\nReading evaluation data...")

    df = pd.read_csv(INPUT_FILE)

    actual = df["y"].values
    predicted = df["yhat"].values

    mae, rmse, mape, wape, smape = calculate_metrics(
        actual,
        predicted
    )

    print("\nIMPROVED MODEL EVALUATION")
    print("=" * 60)

    print(f"MAE   : {mae:.4f}")
    print(f"RMSE  : {rmse:.4f}")
    print(f"MAPE  : {mape:.2f}%")
    print(f"WAPE  : {wape:.2f}%")
    print(f"SMAPE : {smape:.2f}%")

    metrics = pd.DataFrame({
        "metric": [
            "MAE",
            "RMSE",
            "MAPE",
            "WAPE",
            "SMAPE"
        ],
        "value": [
            mae,
            rmse,
            mape,
            wape,
            smape
        ]
    })

    metrics.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nMetrics saved to: "
        f"{OUTPUT_FILE}"
    )

    print("\n" + "=" * 60)
    print("WEEK 3 DAY 3 IMPROVED METRICS COMPLETED")
    print("=" * 60)