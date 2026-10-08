from datetime import datetime
from typing import Any
import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
THAIWATER_BASE = "https://api-v3.thaiwater.net/api/v1/thaiwater30"
RID_RAIN_URL = "https://swoc-api-service.rid.go.th/api/rainfall-hii-24hr/"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "KKU-Smart-Flood-AI/4.0",
    "Referer": "https://www.thaiwater.net/",
}

PROVINCES = {
    "กรุงเทพมหานคร": (13.7563, 100.5018), "กระบี่": (8.0863, 98.9063),
    "กาญจนบุรี": (14.0228, 99.5328), "กาฬสินธุ์": (16.4314, 103.5059),
    "กำแพงเพชร": (16.4828, 99.5227), "ขอนแก่น": (16.4322, 102.8236),
    "จันทบุรี": (12.6113, 102.1038), "ฉะเชิงเทรา": (13.6904, 101.0779),
    "พระนครศรีอยุธยา": (14.3532, 100.5689), "ชลบุรี": (13.3611, 100.9847),
    "ชัยนาท": (15.1852, 100.1251), "ชัยภูมิ": (15.8068, 102.0310),
    "ชุมพร": (10.4930, 99.1800), "ตรัง": (7.5594, 99.6114),
    "ตราด": (12.2428, 102.5175), "ตาก": (16.8830, 99.1258),
    "นครนายก": (14.2069, 101.2131), "นครปฐม": (13.8199, 100.0622),
    "นครพนม": (17.3920, 104.7695), "นครราชสีมา": (14.9799, 102.0977),
    "นครศรีธรรมราช": (8.4304, 99.9631), "นครสวรรค์": (15.7047, 100.1372),
    "นนทบุรี": (13.8621, 100.5144), "นราธิวาส": (6.4255, 101.8253),
    "น่าน": (18.7756, 100.7730), "บึงกาฬ": (18.3609, 103.6464),
    "บุรีรัมย์": (14.9930, 103.1029), "ปทุมธานี": (14.0208, 100.5250),
    "ประจวบคีรีขันธ์": (11.8100, 99.7971), "ปราจีนบุรี": (14.0500, 101.3700),
    "ปัตตานี": (6.8698, 101.2500), "พะเยา": (19.1664, 99.9019),
    "พังงา": (8.4509, 98.5255), "พัทลุง": (7.6167, 100.0740),
    "พิจิตร": (16.4420, 100.3488), "พิษณุโลก": (16.8211, 100.2659),
    "ภูเก็ต": (7.8804, 98.3923), "มหาสารคาม": (16.1851, 103.3020),
    "มุกดาหาร": (16.5453, 104.7235), "ยะลา": (6.5411, 101.2804),
    "ยโสธร": (15.7926, 104.1453), "ร้อยเอ็ด": (16.0538, 103.6520),
    "ระนอง": (9.9529, 98.6085), "ระยอง": (12.6814, 101.2816),
    "ราชบุรี": (13.5283, 99.8134), "ลพบุรี": (14.7995, 100.6534),
    "ลำปาง": (18.2888, 99.4909), "ลำพูน": (18.5745, 99.0087),
    "ศรีสะเกษ": (15.1186, 104.3220), "สกลนคร": (17.1546, 104.1348),
    "สงขลา": (7.1898, 100.5954), "สตูล": (6.6238, 100.0674),
    "สมุทรปราการ": (13.5991, 100.5998), "สมุทรสงคราม": (13.4098, 99.9925),
    "สมุทรสาคร": (13.5475, 100.2744), "สระบุรี": (14.5289, 100.9101),
    "สระแก้ว": (13.8240, 102.0645), "สิงห์บุรี": (14.8936, 100.3967),
    "สุพรรณบุรี": (14.4745, 100.1177), "สุราษฎร์ธานี": (9.1382, 99.3217),
    "สุรินทร์": (14.8818, 103.4936), "สุโขทัย": (17.0078, 99.8265),
    "หนองคาย": (17.8783, 102.7413), "หนองบัวลำภู": (17.2041, 102.4407),
    "อำนาจเจริญ": (15.8657, 104.6258), "อุดรธานี": (17.4138, 102.7875),
    "อุตรดิตถ์": (17.6201, 100.0993), "อุทัยธานี": (15.3835, 100.0246),
    "อุบลราชธานี": (15.2287, 104.8564), "อ่างทอง": (14.5896, 100.4554),
    "เชียงราย": (19.9105, 99.8406), "เชียงใหม่": (18.7883, 98.9853),
    "เพชรบุรี": (13.1119, 99.9398), "เพชรบูรณ์": (16.4190, 101.1606),
    "เลย": (17.4860, 101.7223), "แพร่": (18.1446, 100.1403),
    "แม่ฮ่องสอน": (19.3010, 97.9685),
}
PROVINCES = dict(sorted(PROVINCES.items()))

# ThaiWater official province codes.
PROVINCE_CODES = {
    "กรุงเทพมหานคร":10,"สมุทรปราการ":11,"นนทบุรี":12,"ปทุมธานี":13,
    "พระนครศรีอยุธยา":14,"อ่างทอง":15,"ลพบุรี":16,"สิงห์บุรี":17,
    "ชัยนาท":18,"สระบุรี":19,"ชลบุรี":20,"ระยอง":21,"จันทบุรี":22,
    "ตราด":23,"ฉะเชิงเทรา":24,"ปราจีนบุรี":25,"นครนายก":26,"สระแก้ว":27,
    "นครราชสีมา":30,"บุรีรัมย์":31,"สุรินทร์":32,"ศรีสะเกษ":33,
    "อุบลราชธานี":34,"ยโสธร":35,"ชัยภูมิ":36,"อำนาจเจริญ":37,"บึงกาฬ":38,
    "หนองบัวลำภู":39,"ขอนแก่น":40,"อุดรธานี":41,"เลย":42,"หนองคาย":43,
    "มหาสารคาม":44,"ร้อยเอ็ด":45,"กาฬสินธุ์":46,"สกลนคร":47,"นครพนม":48,
    "มุกดาหาร":49,"เชียงใหม่":50,"ลำพูน":51,"ลำปาง":52,"อุตรดิตถ์":53,
    "แพร่":54,"น่าน":55,"พะเยา":56,"เชียงราย":57,"แม่ฮ่องสอน":58,
    "นครสวรรค์":60,"อุทัยธานี":61,"กำแพงเพชร":62,"ตาก":63,"สุโขทัย":64,
    "พิษณุโลก":65,"พิจิตร":66,"เพชรบูรณ์":67,"ราชบุรี":70,"กาญจนบุรี":71,
    "สุพรรณบุรี":72,"นครปฐม":73,"สมุทรสงคราม":75,"สมุทรสาคร":74,
    "เพชรบุรี":76,"ประจวบคีรีขันธ์":77,"ภูเก็ต":83,"สุราษฎร์ธานี":84,
    "ระนอง":85,"ชุมพร":86,"กระบี่":81,"พังงา":82,"นครศรีธรรมราช":80,
    "สงขลา":90,"สตูล":91,"ตรัง":92,"พัทลุง":93,"ปัตตานี":94,"ยะลา":95,
    "นราธิวาส":96,
}

def _num(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None

def _get_json(base, path="", params=None, timeout=25, headers=None):
    response = requests.get(
        f"{base}{path}",
        params=params,
        headers=headers or HEADERS,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()

def _rows(payload: Any):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    for key in ("data", "rainfall_data", "waterlevel_data", "result", "items", "records"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            nested = _rows(value)
            if nested:
                return nested
    return []

def _province_name(row):
    geo = row.get("geocode") or {}
    value = geo.get("province_name") or row.get("province_name") or row.get("province") or ""
    if isinstance(value, dict):
        return value.get("th") or value.get("en") or value.get("name") or ""
    return str(value)

def _station_name(row):
    station = row.get("station") or {}
    value = (
        station.get("tele_station_name")
        or station.get("station_name")
        or row.get("station_name")
        or row.get("name")
        or "ไม่ระบุชื่อสถานี"
    )
    if isinstance(value, dict):
        return value.get("th") or value.get("en") or value.get("name") or "ไม่ระบุชื่อสถานี"
    return str(value)

def fetch_thaiwater(province):
    code = PROVINCE_CODES.get(province)
    if code is None:
        raise ValueError(f"ไม่มีรหัส ThaiWater สำหรับ {province}")

    rain_rows = _rows(_get_json(THAIWATER_BASE, "/public/rain_24h", {"province_code": code}))
    filtered_rain = [
        row for row in rain_rows
        if _province_name(row) in ("", province)
    ]

    rain24 = [x for x in (_num(r.get("rain_24h")) for r in filtered_rain) if x is not None]
    rain1 = [x for x in (_num(r.get("rain_1h")) for r in filtered_rain) if x is not None]

    try:
        rain3_rows = _rows(_get_json(THAIWATER_BASE, "/provinces/rain3d"))
    except Exception:
        rain3_rows = []
    try:
        rain7_rows = _rows(_get_json(THAIWATER_BASE, "/provinces/rain7d"))
    except Exception:
        rain7_rows = []

    def province_max(rows, key):
        values = []
        for row in rows:
            if _province_name(row) not in ("", province):
                continue
            value = _num(row.get(key))
            if value is not None:
                values.append(value)
        return max(values) if values else None

    water_rows = _rows(_get_json(THAIWATER_BASE, "/public/waterlevel_load"))
    water_rows = [row for row in water_rows if _province_name(row) == province]

    levels, trends, stations = [], [], []
    overbank = warning = critical = 0

    for row in water_rows:
        level = _num(row.get("waterlevel_msl"))
        previous = _num(row.get("waterlevel_msl_previous"))
        situation = int(_num(row.get("situation_level")) or 0)
        bank_status = str(row.get("diff_wl_bank_text") or "ไม่ระบุ")

        if level is not None:
            levels.append(level)
        if level is not None and previous is not None:
            trends.append(level - previous)

        if "ล้นตลิ่ง" in bank_status:
            overbank += 1
        if situation >= 3:
            warning += 1
        if situation >= 4:
            critical += 1

        if level is not None:
            stations.append({
                "station": _station_name(row),
                "level_msl": level,
                "trend_m": (level - previous) if previous is not None else None,
                "situation_level": situation or None,
                "bank_status": bank_status,
            })

    return {
        "province": province,
        "province_code": code,
        "rainfall_1h": max(rain1) if rain1 else 0.0,
        "rainfall_24h": max(rain24) if rain24 else 0.0,
        "rainfall_3d": province_max(rain3_rows, "rain_3d"),
        "rainfall_7d": province_max(rain7_rows, "rain_7d"),
        "rain_station_count": len(filtered_rain),
        "water_level_m": max(levels) if levels else None,
        "water_level_avg_m": sum(levels) / len(levels) if levels else None,
        "water_trend_m": max(trends) if trends else 0.0,
        "water_station_count": len(stations),
        "overbank_count": overbank,
        "warning_station_count": warning,
        "critical_station_count": critical,
        "max_situation_level": max(
            (s["situation_level"] or 0 for s in stations),
            default=0,
        ),
        "water_stations": sorted(
            stations,
            key=lambda item: item["level_msl"],
            reverse=True,
        )[:30],
        "updated_at": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"),
    }


WMO_WEATHER = {
    0: ("ท้องฟ้าแจ่มใส", "☀️"),
    1: ("มีเมฆเล็กน้อย", "🌤️"),
    2: ("มีเมฆบางส่วน", "⛅"),
    3: ("มีเมฆมาก", "☁️"),
    45: ("หมอก", "🌫️"),
    48: ("หมอกเกาะตัว", "🌫️"),
    51: ("ฝนปรอยเล็กน้อย", "🌦️"),
    53: ("ฝนปรอย", "🌦️"),
    55: ("ฝนปรอยหนัก", "🌧️"),
    56: ("ฝนเยือกแข็งเล็กน้อย", "🌧️"),
    57: ("ฝนเยือกแข็ง", "🌧️"),
    61: ("ฝนเล็กน้อย", "🌦️"),
    63: ("ฝนปานกลาง", "🌧️"),
    65: ("ฝนตกหนัก", "🌧️"),
    66: ("ฝนเยือกแข็ง", "🌧️"),
    67: ("ฝนเยือกแข็งหนัก", "🌧️"),
    71: ("หิมะเล็กน้อย", "🌨️"),
    73: ("หิมะ", "🌨️"),
    75: ("หิมะตกหนัก", "❄️"),
    77: ("เกล็ดหิมะ", "❄️"),
    80: ("ฝนซู่เล็กน้อย", "🌦️"),
    81: ("ฝนซู่", "🌧️"),
    82: ("ฝนซู่หนัก", "⛈️"),
    85: ("หิมะซู่", "🌨️"),
    86: ("หิมะซู่หนัก", "❄️"),
    95: ("พายุฝนฟ้าคะนอง", "⛈️"),
    96: ("พายุฝนฟ้าคะนองและลูกเห็บ", "⛈️"),
    99: ("พายุฝนฟ้าคะนองรุนแรง", "⛈️"),
}

THAI_DAYS = {
    "Monday": "จันทร์", "Tuesday": "อังคาร", "Wednesday": "พุธ",
    "Thursday": "พฤหัสบดี", "Friday": "ศุกร์", "Saturday": "เสาร์",
    "Sunday": "อาทิตย์",
}

THAI_MONTHS = {
    1: "ม.ค.", 2: "ก.พ.", 3: "มี.ค.", 4: "เม.ย.", 5: "พ.ค.", 6: "มิ.ย.",
    7: "ก.ค.", 8: "ส.ค.", 9: "ก.ย.", 10: "ต.ค.", 11: "พ.ย.", 12: "ธ.ค.",
}

def weather_code_info(code):
    try:
        code = int(code)
    except (TypeError, ValueError):
        code = 0
    return WMO_WEATHER.get(code, ("สภาพอากาศทั่วไป", "🌤️"))

def format_thai_date(date_string):
    from datetime import datetime
    dt = datetime.fromisoformat(str(date_string))
    return f"{dt.day:02d} {THAI_MONTHS[dt.month]}"

def format_day_name(date_string):
    from datetime import datetime
    dt = datetime.fromisoformat(str(date_string))
    return THAI_DAYS.get(dt.strftime("%A"), dt.strftime("%A"))

def resolve_province_coordinates(province):
    """
    Resolve the selected Thai province to a real Open-Meteo location.
    Falls back to the built-in province coordinate only if geocoding fails.
    The forecast is therefore tied to the selected province rather than
    to one hard-coded national location.
    """
    if province not in PROVINCES:
        raise ValueError(f"ไม่พบจังหวัด {province}")

    fallback_lat, fallback_lon = PROVINCES[province]

    # Search both Thai and English province names where possible.
    # Open-Meteo geocoding is free and accepts language/country filters.
    queries = [
        (province, "th"),
        (province, "en"),
    ]

    for name, language in queries:
        try:
            response = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={
                    "name": f"{name}, Thailand",
                    "count": 10,
                    "language": language,
                    "format": "json",
                    "countryCode": "TH",
                },
                headers=HEADERS,
                timeout=15,
            )
            response.raise_for_status()
            results = response.json().get("results") or []

            # Prefer a Thai result whose admin1/name matches the province.
            for item in results:
                admin1 = str(item.get("admin1") or "")
                item_name = str(item.get("name") or "")
                country = str(item.get("country_code") or "")
                if country == "TH" and (
                    province in admin1 or province in item_name or
                    item_name in province
                ):
                    return (
                        float(item["latitude"]),
                        float(item["longitude"]),
                        item_name,
                        admin1,
                    )

            # If no exact admin match, use the first Thai result.
            if results:
                item = results[0]
                return (
                    float(item["latitude"]),
                    float(item["longitude"]),
                    str(item.get("name") or province),
                    str(item.get("admin1") or province),
                )
        except Exception:
            continue

    return fallback_lat, fallback_lon, province, province

def fetch_weather_forecast(province, forecast_days=7):
    """
    Free Open-Meteo daily forecast. No API key required for the free
    non-commercial tier. Requests exactly one location and up to 7 days.
    """
    lat, lon, resolved_name, resolved_admin1 = resolve_province_coordinates(province)
    days = max(1, min(int(forecast_days), 7))

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ",".join([
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "rain_sum",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "sunrise",
            "sunset",
        ]),
        "forecast_days": days,
        "timezone": "Asia/Bangkok",
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }

    payload = _get_json(OPEN_METEO_URL, params=params, timeout=25)
    daily = payload.get("daily", {})

    required = ["time", "weather_code", "temperature_2m_max", "temperature_2m_min"]
    if any(key not in daily for key in required):
        raise RuntimeError("Open-Meteo ไม่ส่งข้อมูล daily forecast ครบตามที่ระบบต้องการ")

    result = []
    for i, date in enumerate(daily["time"]):
        code = daily["weather_code"][i]
        condition, icon = weather_code_info(code)

        result.append({
            "date": date,
            "day": format_day_name(date),
            "date_th": format_thai_date(date),
            "weather_code": int(code),
            "condition": condition,
            "icon": icon,
            "temp_max": float(daily["temperature_2m_max"][i]),
            "temp_min": float(daily["temperature_2m_min"][i]),
            "apparent_max": float(daily.get("apparent_temperature_max", [0] * len(result))[i] or 0),
            "apparent_min": float(daily.get("apparent_temperature_min", [0] * len(result))[i] or 0),
            "precipitation_mm": float(daily.get("precipitation_sum", [0] * len(result))[i] or 0),
            "rain_mm": float(daily.get("rain_sum", [0] * len(result))[i] or 0),
            "rain_probability": float(daily.get("precipitation_probability_max", [0] * len(result))[i] or 0),
            "wind_max": float(daily.get("wind_speed_10m_max", [0] * len(result))[i] or 0),
            "gust_max": float(daily.get("wind_gusts_10m_max", [0] * len(result))[i] or 0),
            "sunrise": str(daily.get("sunrise", [""] * len(result))[i]),
            "sunset": str(daily.get("sunset", [""] * len(result))[i]),
        })

    return {
        "province": province,
        "resolved_location": resolved_name,
        "resolved_admin1": resolved_admin1,
        "latitude": lat,
        "longitude": lon,
        "timezone": payload.get("timezone", "Asia/Bangkok"),
        "forecast": result,
        "source": "Open-Meteo Weather Forecast API",
        "updated_at": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"),
    }

def fetch_weather(province):
    if province not in PROVINCES:
        raise ValueError(f"ไม่พบจังหวัด {province}")

    lat, lon = PROVINCES[province]
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "timezone": "Asia/Bangkok",
    }
    payload = _get_json(OPEN_METEO_URL, params=params, timeout=20)
    current = payload.get("current", {})

    return {
        "latitude": lat,
        "longitude": lon,
        "temperature": float(current.get("temperature_2m") or 0),
        "humidity": float(current.get("relative_humidity_2m") or 0),
        "current_precipitation": float(current.get("precipitation") or 0),
        "wind_speed": float(current.get("wind_speed_10m") or 0),
        "weather_updated_at": current.get("time", ""),
    }

def fetch_province_data(province):
    result = {
        "province": province,
        "province_code": PROVINCE_CODES.get(province),
        "rainfall_1h": 0.0,
        "rainfall_24h": 0.0,
        "rainfall_3d": None,
        "rainfall_7d": None,
        "rain_station_count": 0,
        "water_level_m": None,
        "water_level_avg_m": None,
        "water_trend_m": 0.0,
        "water_station_count": 0,
        "overbank_count": 0,
        "warning_station_count": 0,
        "critical_station_count": 0,
        "max_situation_level": 0,
        "water_stations": [],
    }

    # Each source is independent, so a temporary outage in one service
    # does not prevent the real 7-day forecast from loading.
    try:
        result.update(fetch_thaiwater(province))
        result["thaiwater_error"] = None
    except Exception as exc:
        result["thaiwater_error"] = str(exc)

    try:
        result.update(fetch_weather(province))
        result["weather_error"] = None
    except Exception as exc:
        result["weather_error"] = str(exc)

    # This is the required live 7-day forecast for the selected province.
    result["forecast"] = fetch_weather_forecast(province, 7)
    return result

def _first(obj, keys):
    if not isinstance(obj, dict):
        return None
    for key in keys:
        value = obj.get(key)
        if value not in (None, ""):
            return value
    return None

def _coords(row):
    candidates = [
        row,
        row.get("station") or {},
        row.get("station_info") or {},
        row.get("stationInfo") or {},
        row.get("location") or {},
        row.get("geocode") or {},
    ]
    lat = lon = None
    for obj in candidates:
        if lat is None:
            lat = _num(_first(obj, ("lat", "latitude", "Latitude", "LAT")))
        if lon is None:
            lon = _num(_first(obj, ("lon", "long", "longitude", "Longitude", "LONG")))
        if lat is not None and lon is not None:
            break
    return lat, lon

def _normalize_rid_row(row):
    if not isinstance(row, dict):
        return None

    lat, lon = _coords(row)
    if lat is None or lon is None:
        return None

    rain = _num(_first(row, (
        "rain_24h", "rain24h", "rainfall_24h", "rainfall24h",
        "rainfall", "value", "rain",
    )))
    if rain is None:
        return None

    province = _first(row, ("province", "province_name", "provinceName"))
    if isinstance(province, dict):
        province = _first(province, ("th", "name", "province_name"))

    timestamp = _first(row, (
        "datetime", "date_time", "rainfall_datetime",
        "rainfallDateTime", "timestamp", "time",
    )) or ""

    if not (5.0 <= lat <= 21.5 and 97.0 <= lon <= 106.5):
        return None

    return {
        "lat": lat,
        "lon": lon,
        "rain_24h": rain,
        "station": str(_first(row, ("station_name", "stationName", "name")) or _station_name(row)),
        "province": str(province or _province_name(row) or "ไม่ระบุ"),
        "time": str(timestamp),
        "source": "RID SWOC / HII",
    }

def fetch_rain_map_rid():
    payload = _get_json(
        RID_RAIN_URL,
        timeout=25,
        headers={"Accept": "application/json", "User-Agent": HEADERS["User-Agent"]},
    )
    rows = _rows(payload)
    points = [point for point in (_normalize_rid_row(row) for row in rows) if point]
    if not points:
        raise RuntimeError("RID SWOC API ไม่พบจุดสถานีฝนที่มีพิกัด")
    return points

def fetch_rain_map_thaiwater():
    rows = _rows(_get_json(THAIWATER_BASE, "/public/rain_24h"))
    points = []

    for row in rows:
        lat, lon = _coords(row)
        rain = _num(row.get("rain_24h"))
        if lat is None or lon is None or rain is None:
            continue
        if not (5.0 <= lat <= 21.5 and 97.0 <= lon <= 106.5):
            continue

        points.append({
            "lat": lat,
            "lon": lon,
            "rain_24h": rain,
            "station": _station_name(row),
            "province": _province_name(row) or "ไม่ระบุ",
            "time": str(
                row.get("rainfall_datetime")
                or row.get("rainfall_time")
                or row.get("timestamp")
                or ""
            ),
            "source": "ThaiWater",
        })

    if not points:
        raise RuntimeError("ThaiWater ไม่พบข้อมูลพิกัดสถานีฝน")
    return points

def fetch_rain_map_open_meteo():
    names = list(PROVINCES)
    latitudes = ",".join(str(PROVINCES[name][0]) for name in names)
    longitudes = ",".join(str(PROVINCES[name][1]) for name in names)

    params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "hourly": "precipitation",
        "past_days": 1,
        "forecast_days": 0,
        "timezone": "Asia/Bangkok",
    }

    response = requests.get(OPEN_METEO_URL, params=params, timeout=35)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        payload = [payload]

    points = []
    for index, item in enumerate(payload[:len(names)]):
        hourly = item.get("hourly", {}) if isinstance(item, dict) else {}
        times = hourly.get("time", []) or []
        values = hourly.get("precipitation", []) or []

        pairs = [
            (time, _num(value))
            for time, value in zip(times, values)
            if _num(value) is not None
        ]
        if not pairs:
            continue

        last24 = pairs[-24:]
        total = sum(value for _, value in last24)
        province = names[index]
        lat, lon = PROVINCES[province]

        points.append({
            "lat": lat,
            "lon": lon,
            "rain_24h": total,
            "station": f"จุดตัวแทนจังหวัด {province}",
            "province": province,
            "time": last24[-1][0],
            "source": "Open-Meteo (จุดตัวแทนจังหวัด)",
        })

    if not points:
        raise RuntimeError("Open-Meteo ไม่พบข้อมูลฝนย้อนหลัง 24 ชั่วโมง")
    return points

def fetch_rain_map():
    errors = []

    for source_name, loader in (
        ("RID SWOC / HII", fetch_rain_map_rid),
        ("ThaiWater", fetch_rain_map_thaiwater),
        ("Open-Meteo", fetch_rain_map_open_meteo),
    ):
        try:
            points = loader()
            for point in points:
                point.setdefault("source", source_name)
            return points
        except Exception as exc:
            errors.append(f"{source_name}: {exc}")

    raise RuntimeError("โหลดแผนที่ฝนจากทุกแหล่งไม่สำเร็จ | " + " | ".join(errors))
