import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "outputs/prophet_evaluation.csv"
OUTPUT_FILE = "outputs/prophet_actual_vs_predicted.png"

df = pd.read_csv(INPUT_FILE)
df["ds"] = pd.to_datetime(df["ds"])

plt.figure(figsize=(14, 6))

plt.plot(
    df["ds"],
    df["y"],
    label="Actual Demand"
)

plt.plot(
    df["ds"],
    df["yhat"],
    label="Prophet Prediction"
)

plt.title(
    "Prophet Demand Forecast — Actual vs Predicted"
)

plt.xlabel("Date")
plt.ylabel("Sales Quantity")

plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=150
)

plt.close()

print("=" * 60)
print("WEEK 3 DAY 2 — ACCURACY VISUALIZATION")
print("=" * 60)
print(f"Visualization saved to: {OUTPUT_FILE}")
print("VISUALIZATION COMPLETED")
print("=" * 60)