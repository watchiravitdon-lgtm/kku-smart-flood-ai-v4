from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

FEATURES = [
    "Rainfall_1h_mm",
    "Rainfall_24h_mm",
    "Rainfall_3d_mm",
    "Rainfall_7d_mm",
    "Water_Level_m",
    "Water_Trend_m",
    "Humidity_percent",
    "Temperature_C",
    "Max_Situation_Level",
    "Overbank_Count",
    "Warning_Station_Count",
    "Critical_Station_Count",
]

df = pd.read_csv("data/flood_data.csv")
X, y = df[FEATURES], df["Risk"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=14,
    min_samples_leaf=2,
    random_state=42,
    class_weight="balanced_subsample",
    n_jobs=-1,
)
model.fit(X_train, y_train)

pred = model.predict(X_test)
accuracy = accuracy_score(y_test, pred)
labels = ["LOW", "MEDIUM", "HIGH"]
cm = confusion_matrix(y_test, pred, labels=labels)

print(f"Accuracy: {accuracy:.4f}")
print(classification_report(y_test, pred, labels=labels))

Path("models").mkdir(exist_ok=True)
joblib.dump(
    {
        "model": model,
        "features": FEATURES,
        "classes": list(model.classes_),
        "accuracy": float(accuracy),
        "confusion_matrix": cm.tolist(),
        "version": "4.0",
    },
    "models/flood_model.pkl",
)
print("Saved models/flood_model.pkl")
