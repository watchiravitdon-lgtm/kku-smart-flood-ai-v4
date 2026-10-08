from pathlib import Path
from html import escape

import joblib
import pandas as pd
import streamlit as st
import folium
from branca.element import Element
from streamlit_folium import st_folium

from src.data_analysis import load_data, feature_importance, create_feature_importance_chart
from src.prediction import predict_risk, apply_realtime_safety_layer
from src.weather_api import PROVINCES, fetch_province_data, fetch_rain_map

st.set_page_config(
    page_title="KKU Smart Flood AI",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_PATH = Path("models/flood_model.pkl")
DATA_PATH = Path("data/flood_data.csv")

if not MODEL_PATH.exists() or not DATA_PATH.exists():
    st.error("ยังไม่มีไฟล์ข้อมูล/โมเดล")
    st.code("python generate_data.py\npython train_model.py\nstreamlit run app.py")
    st.stop()

bundle = joblib.load(MODEL_PATH)
df = load_data()

for key, default in {
    "history": [],
    "province_data": None,
    "province_name": None,
    "api_error": None,
    "rain_map": None,
    "rain_map_error": None,
    "prediction": None,
    "model_prediction": None,
    "probabilities": {},
    "reasons": [],
}.items():
    st.session_state.setdefault(key, default)

st.markdown(
    """
    <style>
    .main-title {font-size: 2.25rem; font-weight: 800; margin-bottom: 0.2rem;}
    .subtitle {font-size: 1.05rem; opacity: .82; margin-bottom: 1rem;}
    .risk-box {padding: 16px; border-radius: 12px; border: 1px solid rgba(128,128,128,.25);}

    .weather-template {
        background: linear-gradient(145deg, #1f568b 0%, #174a7d 100%);
        border-radius: 18px;
        padding: 28px;
        color: white;
        margin: 10px 0 24px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,.16);
    }
    .weather-template .wt-title {
        font-size: 2.0rem;
        font-weight: 800;
        letter-spacing: 2px;
        border-bottom: 2px solid rgba(255,255,255,.75);
        padding-bottom: 10px;
        margin-bottom: 22px;
    }
    .weather-template .wt-city {
        background: rgba(255,255,255,.12);
        display: inline-block;
        padding: 7px 24px;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: 3px;
        border-radius: 2px;
    }
    .weather-template .wt-range {
        font-size: 2.5rem;
        font-weight: 800;
        margin-top: 12px;
    }
    .weather-template .wt-day {
        font-size: 1.15rem;
        opacity: .92;
    }
    .weather-template .wt-icon {
        font-size: 5rem;
        line-height: 1;
        text-align: center;
    }
    .weather-template .wt-condition {
        font-size: 1.35rem;
        text-align: center;
        margin-top: 8px;
    }
    .forecast-grid {
        display: grid;
        grid-template-columns: repeat(6, minmax(0, 1fr));
        gap: 8px;
        margin-top: 18px;
    }
    .forecast-card {
        background: rgba(255,255,255,.13);
        border: 1px solid rgba(255,255,255,.08);
        min-height: 170px;
        padding: 12px 8px;
        text-align: center;
        border-radius: 3px;
    }
    .forecast-card .fc-day {font-size: 1.05rem; font-weight: 700;}
    .forecast-card .fc-date {font-size: .82rem; opacity: .9;}
    .forecast-card .fc-icon {font-size: 2.7rem; margin: 12px 0 8px;}
    .forecast-card .fc-temp {font-size: 1.05rem; font-weight: 700;}
    .forecast-card .fc-rain {font-size: .78rem; margin-top: 7px; opacity: .95;}
    @media (max-width: 900px) {
        .forecast-grid {grid-template-columns: repeat(3, minmax(0, 1fr));}
    }
    @media (max-width: 600px) {
        .weather-template {padding: 18px;}
        .weather-template .wt-title {font-size: 1.45rem;}
        .weather-template .wt-city {font-size: 1.7rem;}
        .weather-template .wt-range {font-size: 1.9rem;}
        .forecast-grid {grid-template-columns: repeat(2, minmax(0, 1fr));}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">🌊 KKU Smart Flood AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">ระบบต้นแบบ AI วิเคราะห์ความเสี่ยงน้ำท่วมจากฝน ระดับน้ำ สถานีตรวจวัด และข้อมูลสภาพอากาศ</div>',
    unsafe_allow_html=True,
)
st.info(
    "ข้อมูลภาคสนามและสภาพอากาศถูกใช้ร่วมกับ Random Forest Prototype "
    "และ deterministic safety layer เพื่ออธิบายผลอย่างโปร่งใส"
)

with st.sidebar:
    st.header("⚙️ การตั้งค่า")
    province = st.selectbox(
        "จังหวัด",
        list(PROVINCES.keys()),
        index=list(PROVINCES.keys()).index("ขอนแก่น"),
    )

    refresh = st.button(
        "🔄 อัปเดตข้อมูลจังหวัด",
        use_container_width=True,
        type="primary",
    )

    st.divider()
    st.caption("เวอร์ชันระบบ: 4.2")
    st.caption("AI: Random Forest")
    st.caption("Map fallback: RID → ThaiWater → Open-Meteo")

province_changed = st.session_state.get("last_selected_province") != province
st.session_state.last_selected_province = province

if refresh or province_changed:
    try:
        with st.spinner(f"กำลังดึงข้อมูลของ {province}..."):
            st.session_state.province_data = fetch_province_data(province)
            st.session_state.province_name = province
            st.session_state.api_error = None
    except Exception as exc:
        st.session_state.api_error = str(exc)

data = st.session_state.province_data
if st.session_state.province_name != province:
    data = None

if st.session_state.api_error:
    st.error(f"API Error: {st.session_state.api_error}")

st.header("1. 📊 ข้อมูลสถานการณ์ปัจจุบัน")

if data:
    metrics = st.columns(4)
    metrics[0].metric("ฝน 1 ชม.", f"{data['rainfall_1h']:.1f} mm")
    metrics[1].metric("ฝน 24 ชม.", f"{data['rainfall_24h']:.1f} mm")
    metrics[2].metric(
        "ฝนสะสม 3 วัน",
        f"{data['rainfall_3d']:.1f} mm" if data["rainfall_3d"] is not None else "ไม่มีข้อมูล",
    )
    metrics[3].metric(
        "ฝนสะสม 7 วัน",
        f"{data['rainfall_7d']:.1f} mm" if data["rainfall_7d"] is not None else "ไม่มีข้อมูล",
    )

    metrics = st.columns(4)
    metrics[0].metric(
        "ระดับน้ำสูงสุด",
        f"{data['water_level_m']:.2f} m" if data["water_level_m"] is not None else "ไม่มีข้อมูล",
    )
    metrics[1].metric("แนวโน้มระดับน้ำ", f"{data['water_trend_m']:+.2f} m")
    metrics[2].metric("สถานีล้นตลิ่ง", data["overbank_count"])
    metrics[3].metric("สถานีเตือน/วิกฤต", data["warning_station_count"])

    weather = st.columns(4)
    weather[0].metric("อุณหภูมิ", f"{data['temperature']:.1f} °C")
    weather[1].metric("ความชื้น", f"{data['humidity']:.0f} %")
    weather[2].metric("ฝนปัจจุบัน", f"{data['current_precipitation']:.1f} mm")
    weather[3].metric("ลม", f"{data['wind_speed']:.1f} km/h")

    st.caption(
        f"จังหวัด {province} | ThaiWater {data['water_station_count']} สถานี | "
        f"อัปเดต {data['updated_at']}"
    )
    if data.get("thaiwater_error"):
        st.warning("ThaiWater ขัดข้องชั่วคราว แต่ Weather Forecast ยังคงโหลดจาก Open-Meteo ได้")

    if data["overbank_count"] > 0:
        st.error(f"⚠️ พบสถานีน้ำล้นตลิ่ง {data['overbank_count']} สถานี")
    elif data["critical_station_count"] > 0:
        st.warning(f"⚠️ พบสถานีระดับวิกฤต {data['critical_station_count']} สถานี")

    if data["water_stations"]:
        st.subheader("สถานีระดับน้ำล่าสุด")
        station_df = pd.DataFrame(data["water_stations"])
        st.dataframe(station_df, use_container_width=True, hide_index=True)
else:
    st.warning("เลือกจังหวัดแล้วกด “อัปเดตข้อมูลจังหวัด” เพื่อดึงข้อมูลล่าสุด")

st.header("2. 🌤️ Weather Forecast — 7 Days")

if data and data.get("forecast") and data["forecast"].get("forecast"):
    forecast = data["forecast"]["forecast"]
    today = forecast[0]

    # Main day follows the supplied template: city + range + date/day + icon + condition.
    forecast_cards = []
    for item in forecast[1:]:
        forecast_cards.append(
            f"""
            <div class="forecast-card">
                <div class="fc-day">{item['day']}</div>
                <div class="fc-date">{item['date_th']}</div>
                <div class="fc-icon">{item['icon']}</div>
                <div class="fc-temp">{item['temp_min']:.0f}° ~ {item['temp_max']:.0f}°C</div>
                <div class="fc-rain">💧 {item['rain_probability']:.0f}% · {item['precipitation_mm']:.1f} mm</div>
            </div>
            """
        )

    # If API returns fewer than 7 days, the grid simply renders what is available.
    cards_html = "".join(forecast_cards)
    source_note = escape(str(data["forecast"].get("source", "Open-Meteo")))

    st.markdown(
        f"""
        <div class="weather-template">
            <div class="wt-title">WEATHER FORECAST</div>
            <div style="display:grid;grid-template-columns:1.35fr .65fr;gap:20px;align-items:center;">
                <div>
                    <div class="wt-city">{escape(province).upper()}</div>
                    <div class="wt-range">{today['temp_min']:.0f}° ~ {today['temp_max']:.0f}°C</div>
                    <div class="wt-day">{today['date_th']} · {today['day']}</div>
                </div>
                <div>
                    <div class="wt-icon">{today['icon']}</div>
                    <div class="wt-condition">{escape(today['condition'])}</div>
                    <div style="text-align:center;margin-top:6px;font-size:.9rem;opacity:.85;">
                        ฝน {today['rain_probability']:.0f}% · {today['precipitation_mm']:.1f} mm
                    </div>
                </div>
            </div>
            <div class="forecast-grid">
                {cards_html}
            </div>
            <div style="margin-top:14px;font-size:.75rem;opacity:.72;">
                Source: {source_note} · Daily forecast · Asia/Bangkok
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("📋 รายละเอียดพยากรณ์ 7 วัน"):
        forecast_df = pd.DataFrame([
            {
                "วัน": x["day"],
                "วันที่": x["date_th"],
                "สภาพอากาศ": x["condition"],
                "ต่ำสุด °C": x["temp_min"],
                "สูงสุด °C": x["temp_max"],
                "ฝน (%)": x["rain_probability"],
                "ฝนสะสม (mm)": x["precipitation_mm"],
                "ลมสูงสุด (km/h)": x["wind_max"],
            }
            for x in forecast
        ])
        st.dataframe(forecast_df, use_container_width=True, hide_index=True)

    resolved = data["forecast"].get("resolved_location", province)
    resolved_admin1 = data["forecast"].get("resolved_admin1", province)
    forecast_updated = data["forecast"].get("updated_at", "ไม่ทราบเวลา")

    st.caption(
        f"ข้อมูลจริงจาก Open-Meteo สำหรับ {resolved}, {resolved_admin1} "
        f"({data['forecast']['latitude']:.4f}, {data['forecast']['longitude']:.4f}) · "
        f"อัปเดต {forecast_updated}"
    )
    st.caption(
        "Forecast ถูกดึงใหม่ตามจังหวัดที่เลือกทุกครั้งที่เปลี่ยนจังหวัดหรือกดอัปเดต "
        "โดยใช้ข้อมูลพยากรณ์ล่าสุดจาก API"
    )
else:
    st.info("อัปเดตข้อมูลจังหวัดก่อนเพื่อแสดง Forecast 7 วัน")

st.header("2. 🗺️ แผนที่ฝนย้อนหลัง 24 ชั่วโมง")

map_col1, map_col2 = st.columns([3, 1])
with map_col1:
    st.caption("ระบบจะพยายามใช้ RID SWOC/HII ก่อน จากนั้น ThaiWater และ Open-Meteo ตามลำดับ")
with map_col2:
    map_refresh = st.button("📍 รีเฟรชแผนที่", use_container_width=True)

if st.session_state.rain_map is None or map_refresh:
    try:
        with st.spinner("กำลังโหลดแผนที่ฝน..."):
            st.session_state.rain_map = fetch_rain_map()
            st.session_state.rain_map_error = None
    except Exception as exc:
        st.session_state.rain_map = []
        st.session_state.rain_map_error = str(exc)

if st.session_state.rain_map_error:
    st.error(st.session_state.rain_map_error)

points = st.session_state.rain_map or []

def rain_color(value):
    if value <= 10:
        return "blue"
    if value <= 20:
        return "lightblue"
    if value <= 35:
        return "green"
    if value <= 50:
        return "yellow"
    if value <= 70:
        return "orange"
    if value <= 90:
        return "darkorange"
    return "red"

if points:
    sources = sorted({p.get("source", "ไม่ระบุ") for p in points})
    st.caption(f"พบ {len(points):,} จุด | แหล่งข้อมูล: {', '.join(sources)}")

    fmap = folium.Map(
        location=[13.5, 101.0],
        zoom_start=6,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    for point in points:
        rain = float(point["rain_24h"])
        popup = (
            f"<b>{escape(str(point['station']))}</b><br>"
            f"จังหวัด: {escape(str(point['province']))}<br>"
            f"ฝน 24 ชม.: {rain:.1f} mm<br>"
            f"เวลา: {escape(str(point.get('time', '')))}<br>"
            f"แหล่งข้อมูล: {escape(str(point.get('source', '')))}"
        )

        folium.CircleMarker(
            location=[point["lat"], point["lon"]],
            radius=5 if rain < 70 else 7,
            color=rain_color(rain),
            fill=True,
            fill_opacity=0.80,
            popup=folium.Popup(popup, max_width=320),
            tooltip=f"{point['province']}: {rain:.1f} mm",
        ).add_to(fmap)

    legend = """
    <div style="
        position: fixed; bottom: 20px; left: 20px; z-index: 9999;
        background: white; padding: 10px 12px; border: 1px solid #999;
        border-radius: 8px; font-size: 12px;">
        <b>ฝนสะสม 24 ชม. (mm)</b><br>
        🔵 ≤10 &nbsp; 🩵 10–20 &nbsp; 🟢 20–35 &nbsp; 🟡 35–50<br>
        🟠 50–70 &nbsp; 🟠 70–90 &nbsp; 🔴 >90
    </div>
    """
    fmap.get_root().html.add_child(Element(legend))
    st_folium(fmap, use_container_width=True, height=620)
else:
    st.warning("ยังไม่มีข้อมูลแผนที่ฝน")

st.header("3. 🗺️ AI Flood Risk Analysis")

if data and data.get("water_level_m") is not None:
    if st.button("🔎 วิเคราะห์ความเสี่ยงด้วย AI", type="primary", use_container_width=True):
        model_prediction, model_probabilities = predict_risk(data)
        final, final_probabilities, reasons = apply_realtime_safety_layer(
            model_prediction,
            model_probabilities,
            data,
        )

        st.session_state.prediction = final
        st.session_state.model_prediction = model_prediction
        st.session_state.probabilities = final_probabilities
        st.session_state.reasons = reasons

        st.session_state.history.insert(
            0,
            {
                "จังหวัด": province,
                "ฝน 1 ชม.": data["rainfall_1h"],
                "ฝน 24 ชม.": data["rainfall_24h"],
                "ฝน 3 วัน": data["rainfall_3d"],
                "ระดับน้ำ": data["water_level_m"],
                "แนวโน้มน้ำ": data["water_trend_m"],
                "ล้นตลิ่ง": data["overbank_count"],
                "AI Model": model_prediction,
                "Final Risk": final,
            },
        )
else:
    st.info("ต้องมีข้อมูลระดับน้ำก่อนจึงจะวิเคราะห์ด้วย AI ได้")

labels = {
    "LOW": "🟢 ความเสี่ยงต่ำ",
    "MEDIUM": "🟡 ความเสี่ยงปานกลาง",
    "HIGH": "🔴 ความเสี่ยงสูง",
}

if st.session_state.prediction:
    st.markdown(
        f'<div class="risk-box"><h2>{labels[st.session_state.prediction]}</h2>'
        f'<p>ผลสุดท้ายจาก AI + Real-time Safety Layer</p></div>',
        unsafe_allow_html=True,
    )

    if st.session_state.model_prediction != st.session_state.prediction:
        st.warning(
            f"โมเดลต้นฉบับประเมิน {st.session_state.model_prediction} "
            f"แต่ Safety Layer ปรับเป็น {st.session_state.prediction} "
            "เพราะพบหลักฐานจากข้อมูลภาคสนาม"
        )

    st.subheader("เหตุผล")
    for reason in st.session_state.reasons:
        st.write(f"• {reason}")

    probs = st.session_state.probabilities
    cols = st.columns(3)
    cols[0].metric("LOW", f"{probs.get('LOW', 0) * 100:.1f}%")
    cols[1].metric("MEDIUM", f"{probs.get('MEDIUM', 0) * 100:.1f}%")
    cols[2].metric("HIGH", f"{probs.get('HIGH', 0) * 100:.1f}%")

st.header("5. 📈 AI Model Performance")

metrics = st.columns(3)
metrics[0].metric("Model Accuracy", f"{bundle['accuracy'] * 100:.2f}%")
metrics[1].metric("Decision Trees", bundle["model"].n_estimators)
metrics[2].metric("Training Dataset", f"{len(df):,}")

st.caption(
    "Accuracy เป็นผลจาก Synthetic Prototype Dataset "
    "ไม่ใช่ค่าความแม่นยำที่รับรองด้วยข้อมูลน้ำท่วมจริง"
)

st.header("6. 🧠 AI Feature Importance")

importance = feature_importance()
st.dataframe(
    importance.style.format({"Importance": "{:.4f}"}),
    use_container_width=True,
    hide_index=True,
)

chart_path = Path("images/feature_importance.png")
if not chart_path.exists():
    create_feature_importance_chart()
st.image(str(chart_path), use_container_width=True)

st.header("7. 📊 Training Dataset")

left, right = st.columns(2)
with left:
    st.subheader("จำนวนข้อมูลแต่ละระดับ")
    st.bar_chart(df["Risk"].value_counts())
with right:
    st.subheader("ตัวอย่างข้อมูล")
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)

st.header("8. 🕘 ประวัติการวิเคราะห์")

if st.session_state.history:
    st.dataframe(
        pd.DataFrame(st.session_state.history),
        use_container_width=True,
        hide_index=True,
    )
    if st.button("🗑️ ล้างประวัติ"):
        st.session_state.history = []
        st.rerun()
else:
    st.caption("ยังไม่มีประวัติการวิเคราะห์")

st.header("9. ℹ️ แหล่งข้อมูลและข้อจำกัด")

st.markdown(
    """
- **ThaiWater** — ข้อมูลฝนและระดับน้ำจากคลังข้อมูลน้ำแห่งชาติ
- **RID SWOC / HII** — แหล่งข้อมูลหลักสำหรับแผนที่ฝน 24 ชั่วโมง
- **Open-Meteo** — ข้อมูลสภาพอากาศและ fallback ของแผนที่
- **Random Forest** — โมเดลต้นแบบที่ฝึกด้วย Synthetic Dataset
- **Real-time Safety Layer** — กฎ deterministic สำหรับยกระดับผลเมื่อพบหลักฐานเสี่ยงจากสถานีจริง

**ข้อจำกัด:** โปรเจกต์นี้เป็นต้นแบบเพื่อการศึกษาและ Portfolio
ไม่ใช่ระบบเตือนภัยอย่างเป็นทางการ และไม่ควรใช้แทนประกาศจากหน่วยงานรัฐ
"""
)

st.warning("⚠️ Prototype สำหรับการศึกษา/Portfolio — ไม่ใช่ระบบตัดสินใจด้านความปลอดภัยในสถานการณ์จริง")
