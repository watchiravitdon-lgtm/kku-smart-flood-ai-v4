# KKU Smart Flood AI — V4.2

ระบบต้นแบบ AI สำหรับวิเคราะห์ความเสี่ยงน้ำท่วมจากข้อมูลฝน ระดับน้ำ สถานีตรวจวัด และสภาพอากาศ

## จุดเด่น

- Random Forest สำหรับจำแนก `LOW / MEDIUM / HIGH`
- Real-time Safety Layer ตรวจหลักฐานจากข้อมูลสถานีจริง
- แผนที่ฝนย้อนหลัง 24 ชั่วโมงแบบ Interactive
- ระบบ fallback แผนที่ฝน: `RID SWOC/HII → ThaiWater → Open-Meteo`
- วิเคราะห์ Feature Importance
- ตารางสถานีระดับน้ำ
- ประวัติการวิเคราะห์
- รองรับ 77 จังหวัด
- ไม่ต้องใช้ฐานข้อมูลหรือ API key สำหรับโหมดหลัก

## โครงสร้าง

```text
kku-smart-flood-ai-v4/
├── app.py
├── generate_data.py
├── train_model.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── flood_data.csv        # สร้างจาก generate_data.py
├── models/
│   └── flood_model.pkl       # สร้างจาก train_model.py
├── images/
│   └── feature_importance.png
└── src/
    ├── __init__.py
    ├── data_analysis.py
    ├── prediction.py
    └── weather_api.py
```

## วิธีติดตั้ง

```bash
pip install -r requirements.txt
```

## สร้าง Training Dataset

```bash
python generate_data.py
```

## Train AI

```bash
python train_model.py
```

## เปิดเว็บ

```bash
streamlit run app.py
```

## แหล่งข้อมูล

- ThaiWater: https://www.thaiwater.net/
- ThaiWater API: https://api-v3.thaiwater.net/api/v1/thaiwater30/
- Open-Meteo: https://open-meteo.com/
- RID SWOC/HII rainfall API

## หมายเหตุด้าน AI

โมเดลที่ใช้ในโปรเจกต์นี้เป็น **Synthetic Prototype Dataset**
ดังนั้น Accuracy ที่แสดงใน Dashboard ไม่ควรตีความว่าเป็นความแม่นยำของการพยากรณ์น้ำท่วมจริง

Safety Layer เป็นกฎแบบ deterministic เพื่อให้ระบบสามารถอธิบายได้ว่า
เหตุใดผลลัพธ์จึงถูกยกระดับเมื่อพบหลักฐาน เช่น น้ำล้นตลิ่ง สถานีวิกฤต ฝนสะสมสูง หรือระดับน้ำเพิ่มขึ้น


## Weather Forecast 7 วัน

ระบบใช้ Open-Meteo Forecast API แบบรายวัน โดยไม่ต้องใช้ API Key สำหรับการใช้งานฟรีแบบ non-commercial/การศึกษา

ข้อมูลที่แสดง:
- อุณหภูมิต่ำสุด/สูงสุด
- สภาพอากาศจาก WMO Weather Code
- โอกาสเกิดฝน
- ปริมาณฝนรายวัน
- ลมสูงสุดและลมกระโชก
- พระอาทิตย์ขึ้น/ตก

Open-Meteo ระบุว่า Forecast API ฟรีไม่ต้องสมัครสมาชิกหรือใช้ API key และรองรับข้อมูลพยากรณ์หลายวัน โดย free tier มีข้อจำกัดการใช้งานและต้องให้ attribution ตาม CC BY 4.0

Official:
- https://open-meteo.com/
- https://open-meteo.com/en/docs


## ความถูกต้องของ Forecast 7 วัน

เมื่อผู้ใช้เลือกจังหวัด ระบบจะเรียก Open-Meteo Geocoding API เพื่อ resolve
ตำแหน่งของจังหวัด แล้วใช้พิกัดนั้นเรียก Weather Forecast API แบบ `forecast_days=7`

ดังนั้นการเปลี่ยนจังหวัด เช่น ขอนแก่น → ชลบุรี จะทำให้ Forecast 7 วันถูกดึงใหม่
สำหรับตำแหน่งของจังหวัดที่เลือก ไม่ใช้ค่าพยากรณ์ของจังหวัดเดิม

ระบบยังแสดง:
- ตำแหน่งที่ API resolve ได้
- Latitude / Longitude
- เวลาอัปเดตข้อมูล
- แหล่งข้อมูล

หาก ThaiWater ขัดข้องชั่วคราว Forecast จาก Open-Meteo ยังสามารถทำงานแยกได้
