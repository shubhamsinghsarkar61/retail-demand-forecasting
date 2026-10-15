import pandas as pd
import lightgbm as lgb
from pathlib import Path


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "outputs" / "lightgbm_training_data.csv"
MODEL_FILE = BASE_DIR / "outputs" / "lightgbm_model.txt"
OUTPUT_FILE = BASE_DIR / "outputs" / "lightgbm_forecast.csv"


# Load training data
print("Loading forecasting data...")
df = pd.read_csv(INPUT_FILE)

print(f"Dataset shape: {df.shape}")


# Features used during training
features = [
    "day_number",
    "lag_1",
    "lag_7",
    "lag_14",
    "lag_28",
    "rolling_mean_7",
    "rolling_mean_28",
    "day_of_week",
    "week_number"
]


# Load trained LightGBM model
print("Loading trained LightGBM model...")
model = lgb.Booster(model_file=str(MODEL_FILE))


# Generate predictions
print("Generating LightGBM forecasts...")
df["forecast"] = model.predict(df[features])
df["forecast"] = df["forecast"].clip(lower=0)


# Keep required forecast columns
forecast_df = df[
    [
        "id",
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id",
        "day",
        "sales",
        "forecast"
    ]
]


# Save forecast output
forecast_df.to_csv(OUTPUT_FILE, index=False)


print("LightGBM forecast generation completed successfully!")
print(f"Forecast saved to: {OUTPUT_FILE}")
print(f"Forecast shape: {forecast_df.shape}")