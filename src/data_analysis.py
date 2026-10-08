from pathlib import Path
import joblib
import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = Path("data/flood_data.csv")
MODEL_PATH = Path("models/flood_model.pkl")

def load_data():
    return pd.read_csv(DATA_PATH)

def load_bundle():
    return joblib.load(MODEL_PATH)

def feature_importance():
    bundle = load_bundle()
    model = bundle["model"]
    return (
        pd.DataFrame({
            "Feature": bundle["features"],
            "Importance": model.feature_importances_,
        })
        .sort_values("Importance", ascending=False)
        .reset_index(drop=True)
    )

def create_feature_importance_chart(output="images/feature_importance.png"):
    importance = feature_importance().sort_values("Importance")
    Path(output).parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(9, 6))
    plt.barh(importance["Feature"], importance["Importance"])
    plt.xlabel("Importance")
    plt.title("AI Feature Importance")
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()
