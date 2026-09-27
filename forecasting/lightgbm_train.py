import pandas as pd
import lightgbm as lgb
from pathlib import Path


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "outputs" / "lightgbm_training_data.csv"
MODEL_FILE = BASE_DIR / "outputs" / "lightgbm_model.txt"


# Load training data
print("Loading LightGBM training data...")
df = pd.read_csv(INPUT_FILE)

print(f"Dataset shape: {df.shape}")


# Features used for training
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

target = "sales"


# Prepare X and y
X = df[features]
y = df[target]


# LightGBM model
model = lgb.LGBMRegressor(
    objective="regression",
    n_estimators=500,
    learning_rate=0.05,
    num_leaves=31,
    max_depth=-1,
    random_state=42,
    n_jobs=-1
)


# Train model
print("Training LightGBM model...")
model.fit(X, y)


# Save trained model
model.booster_.save_model(str(MODEL_FILE))


print("LightGBM model training completed successfully!")
print(f"Model saved to: {MODEL_FILE}")