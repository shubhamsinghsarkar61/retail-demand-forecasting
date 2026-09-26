import pandas as pd
import numpy as np
from pathlib import Path

# ---------------------------------------------------------
# WEEK 3 - DAY 4
# LightGBM Forecasting Dataset Preparation
# ---------------------------------------------------------

# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Input dataset
TRAIN_FILE = BASE_DIR / "sales_train_validation.csv"

print("Loading M5 sales dataset...")
print(f"Input file: {TRAIN_FILE}")

# Load data
df = pd.read_csv(TRAIN_FILE)

print("\nOriginal dataset shape:")
print(df.shape)

# ---------------------------------------------------------
# Select manageable recent history
# ---------------------------------------------------------

id_columns = [
    "id",
    "item_id",
    "dept_id",
    "cat_id",
    "store_id",
    "state_id"
]

date_columns = [col for col in df.columns if col.startswith("d_")]

print(f"\nNumber of daily columns: {len(date_columns)}")

# Keep latest 90 days for memory-efficient Day-4 preparation
recent_days = date_columns[-90:]

print(f"Using latest {len(recent_days)} days for model preparation.")

# ---------------------------------------------------------
# Convert selected data to long format
# ---------------------------------------------------------

df_long = df.melt(
    id_vars=id_columns,
    value_vars=recent_days,
    var_name="day",
    value_name="sales"
)

print("\nLong-format dataset shape:")
print(df_long.shape)

# ---------------------------------------------------------
# Basic cleaning
# ---------------------------------------------------------

df_long["sales"] = pd.to_numeric(
    df_long["sales"],
    errors="coerce"
).fillna(0)

df_long["day_number"] = (
    df_long["day"]
    .str.replace("d_", "", regex=False)
    .astype(int)
)

# Sort correctly for time-series feature creation
df_long = df_long.sort_values(
    ["id", "day_number"]
).reset_index(drop=True)

# ---------------------------------------------------------
# Create LightGBM features
# ---------------------------------------------------------

print("\nCreating forecasting features...")

# Lag features
df_long["lag_1"] = df_long.groupby("id")["sales"].shift(1)
df_long["lag_7"] = df_long.groupby("id")["sales"].shift(7)
df_long["lag_14"] = df_long.groupby("id")["sales"].shift(14)
df_long["lag_28"] = df_long.groupby("id")["sales"].shift(28)

# Rolling features
df_long["rolling_mean_7"] = (
    df_long.groupby("id")["sales"]
    .transform(lambda x: x.shift(1).rolling(7).mean())
)

df_long["rolling_mean_28"] = (
    df_long.groupby("id")["sales"]
    .transform(lambda x: x.shift(1).rolling(28).mean())
)

# Time features
df_long["day_of_week"] = (df_long["day_number"] - 1) % 7
df_long["week_number"] = (df_long["day_number"] - 1) // 7

# ---------------------------------------------------------
# Remove rows where lag/rolling features are unavailable
# ---------------------------------------------------------

df_model = df_long.dropna().copy()

print("\nModel dataset shape:")
print(df_model.shape)

# ---------------------------------------------------------
# Save prepared dataset
# ---------------------------------------------------------

output_file = OUTPUT_DIR / "lightgbm_training_data.csv"

df_model.to_csv(
    output_file,
    index=False
)

print("\nDay-4 preparation completed successfully!")
print(f"Saved file: {output_file}")

print("\nFinal columns:")
print(df_model.columns.tolist())