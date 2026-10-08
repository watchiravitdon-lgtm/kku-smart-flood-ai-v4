from pathlib import Path
import joblib
import pandas as pd

MODEL_PATH = Path("models/flood_model.pkl")

def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "ไม่พบ models/flood_model.pkl กรุณารัน generate_data.py และ train_model.py ก่อน"
        )
    return joblib.load(MODEL_PATH)

def predict_risk(data):
    bundle = load_model()
    model = bundle["model"]
    features = bundle["features"]

    row = {
        feature: float(data.get(feature, 0) or 0)
        for feature in features
    }
    X = pd.DataFrame([row])
    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]

    return prediction, {
        cls: float(prob)
        for cls, prob in zip(model.classes_, probabilities)
    }

def apply_realtime_safety_layer(prediction, probabilities, data):
    """
    Combines the prototype ML result with explicit real-time evidence.
    This layer is deterministic and can escalate risk; it does not claim
    that adjusted percentages are calibrated real-world probabilities.
    """
    overbank = int(data.get("overbank_count") or 0)
    critical = int(data.get("critical_station_count") or 0)
    warning = int(data.get("warning_station_count") or 0)
    situation = int(data.get("max_situation_level") or 0)
    rain24 = float(data.get("rainfall_24h") or 0)
    rain3 = data.get("rainfall_3d")
    rain3 = float(rain3) if rain3 is not None else 0
    trend = float(data.get("water_trend_m") or 0)

    final = prediction
    reasons = []

    if overbank > 0 or situation >= 5:
        final = "HIGH"
        reasons.append(f"พบสถานีน้ำล้นตลิ่ง {overbank} สถานี")
    elif critical > 0 or situation >= 4:
        final = "HIGH"
        reasons.append(f"พบสถานีระดับวิกฤต {critical} สถานี")
    elif warning >= 2 or situation >= 3:
        if final == "LOW":
            final = "MEDIUM"
        reasons.append(f"พบสถานีเฝ้าระวัง/เตือนภัย {warning} สถานี")

    if rain24 >= 70 or (rain3 > 0 and rain3 >= 120):
        if final == "LOW":
            final = "MEDIUM"
        reasons.append("ปริมาณฝนสะสมอยู่ในระดับสูง")

    if trend >= 0.20:
        if final == "LOW":
            final = "MEDIUM"
        reasons.append("ระดับน้ำมีแนวโน้มเพิ่มขึ้น")

    adjusted = {
        "LOW": float(probabilities.get("LOW", 0)),
        "MEDIUM": float(probabilities.get("MEDIUM", 0)),
        "HIGH": float(probabilities.get("HIGH", 0)),
    }

    if final != prediction:
        adjusted = {key: value * 0.35 for key, value in adjusted.items()}
        adjusted[final] += 0.65

    total = sum(adjusted.values()) or 1
    adjusted = {key: value / total for key, value in adjusted.items()}

    if not reasons:
        reasons.append("ยังไม่พบหลักฐานภาคสนามที่เข้าข่ายการยกระดับความเสี่ยง")

    return final, adjusted, reasons
