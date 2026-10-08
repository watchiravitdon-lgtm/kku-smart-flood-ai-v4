from pathlib import Path
import numpy as np
import pandas as pd

SEED = 2026
N = 8000
rng = np.random.default_rng(SEED)

rain_1h = np.clip(rng.gamma(1.8, 5, N), 0, 100)
rain_24h = np.clip(rain_1h + rng.gamma(2.2, 18, N), 0, 300)
rain_3d = np.clip(rain_24h + rng.gamma(2.0, 35, N), 0, 600)
rain_7d = np.clip(rain_3d + rng.gamma(2.0, 55, N), 0, 1000)

water_level = np.clip(rng.normal(1.0, 0.45, N), 0.05, 4.5)
water_trend = np.clip(rng.normal(0.03, 0.14, N), -0.6, 1.0)
humidity = np.clip(rng.normal(78, 11, N), 35, 100)
temperature = np.clip(rng.normal(29, 3.5, N), 18, 42)

situation = rng.choice([1, 2, 3, 4, 5], N, p=[0.52, 0.20, 0.13, 0.10, 0.05])
overbank = np.where(situation == 5, rng.integers(1, 4, N), 0)
warning = np.where(situation >= 3, rng.integers(0, 5, N), 0)
critical = np.where(situation >= 4, rng.integers(0, 3, N), 0)

score = (
    rain_1h * 0.34
    + rain_24h * 0.18
    + rain_3d * 0.10
    + rain_7d * 0.035
    + water_level * 24
    + water_trend * 55
    + humidity * 0.20
    + (situation - 1) * 18
    + overbank * 55
    + warning * 8
    + critical * 18
    - temperature * 0.6
    + rng.normal(0, 7, N)
)

risk = np.select(
    [score < 65, score < 120],
    ["LOW", "MEDIUM"],
    default="HIGH",
)

df = pd.DataFrame({
    "Rainfall_1h_mm": np.round(rain_1h, 2),
    "Rainfall_24h_mm": np.round(rain_24h, 2),
    "Rainfall_3d_mm": np.round(rain_3d, 2),
    "Rainfall_7d_mm": np.round(rain_7d, 2),
    "Water_Level_m": np.round(water_level, 2),
    "Water_Trend_m": np.round(water_trend, 3),
    "Humidity_percent": np.round(humidity, 2),
    "Temperature_C": np.round(temperature, 2),
    "Max_Situation_Level": situation,
    "Overbank_Count": overbank,
    "Warning_Station_Count": warning,
    "Critical_Station_Count": critical,
    "Risk": risk,
})

Path("data").mkdir(exist_ok=True)
df.to_csv("data/flood_data.csv", index=False)
print(f"Created {len(df):,} rows")
print(df["Risk"].value_counts())
