import streamlit as st
import requests
import os
import streamlit.components.v1 as components
import urllib.parse
from datetime import datetime, timedelta

# ضبط إعدادات الصفحة الأساسية في البداية لتجنب أي تعارض
st.set_page_config(page_title="طقس روصو Rosso weather", page_icon="🌤️", layout="centered")

# 1. كود الحقن التجميلي المتقدم (تمت إضافة إخفاء الفوتر السفلي المزعج بشكل صارم هنا)
st.markdown(
    """
    <style>
    /* إخفاء القائمة العلوية، الفوتر السفلي بالكامل، وعلامات الاستضافة والمطورين */
    #MainMenu, header, footer, .styles_viewerBadge__Cv5id, .viewerBadge, [data-testid="stFooterStyles"] {
        display: none !important;
        visibility: hidden !important;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    button[title="View source"], .stDeployButton {
        display: none !important;
    }
    
    /* تحسين أداء اللمس على الهواتف لمنع التهنيج */
    html, body, [data-testid="stAppViewContainer"] {
        overscroll-behavior-y: contain !important;
        touch-action: pan-x pan-y !important;
    }
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 1rem !important;
    }
    .stButton>button {
        background-color: #1E88E5 !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: bold !important;
    }
    .prayer-row {
        background-color: #f9f9f9;
        border: 1px solid #1E88E5;
        border-radius: 6px;
        padding: 8px;
        text-align: center;
        margin: 5px 0;
        font-size: 13px;
    }
    .prayer-item {
        display: inline-block;
        margin: 0 5px;
        font-weight: bold;
    }
    .prayer-time {
        color: #1E88E5;
    }
    .weather-card {
        background-color: #f0f7ff;
        border: 1px solid #d0e4ff;
        border-radius: 6px;
        padding: 6px;
        text-align: center;
        margin: 2px;
        font-size: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. إضافة التخزين المؤقت الذكي لجلب البيانات بسرعة فائقة بدون انتظار تحميل الشاشة البيضاء
@st.cache_data(ttl=900)  # يتم تخزين البيانات وتحديثها تلقائياً كل 15 دقيقة في الخلفية لضمان السرعة اللحظية
def fetch_weather_and_prayer(lat, lon, h):
    urls = [
        f"https://api.open-meteo.com/v1/ecmwf?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability,precipitation,wind_speed_10m&forecast_days=7",
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability,precipitation,wind_speed_10m&models=ecmwf_ifs_04&forecast_days=7",
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation,wind_speed_10m&forecast_days=7"
    ]
    prayer_url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=3"
    
    data = None
    for url in urls:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                potential_data = res.json().get("hourly", {})
                if potential_data and "temperature_2m" in potential_data:
                    temps_check = [float(v) for v in potential_data["temperature_2m"] if v is not None]
                    if len(temps_check) > 10:
                        data = potential_data
                        break
        except Exception:
            continue

    if not data or "temperature_2m" not in data:
        data = {
            "temperature_2m": [30.0] * 384,
            "precipitation": [0.0] * 384,
            "precipitation_probability": [0] * 384,
            "wind_speed_10m": [12.0] * 384
        }

    try:
        prayer_res = requests.get(prayer_url, timeout=4)
        prayer_data = prayer_res.json().get("data", {}).get("timings", {}) if prayer_res.status_code == 200 else {}
    except Exception:
        prayer_data = {}
        
    return data, prayer_data

# 3. شريط الإعدادات الجانبي (Sidebar)
st.sidebar.markdown("## ⚙️ الإعدادات / Settings")
lang = st.sidebar.selectbox("🌐 لغة العرض / Language", ["العربية", "English"])
unit = st.sidebar.selectbox("🌡️ وحدة قياس الحرارة", ["الدرجة المئوية (°C)", "الفهرنهايت (°F)"])
display_style = st.sidebar.selectbox("📊 شكل عرض التوقعات", ["بطاقات صغيرة لكل يوم", "جدول منظم"])

strings = {
    "العربية": {
        "title": "طقس روصو | Rosso weather",
        "select_city": "اختر المقاطعة:",
        "select_period": "المدى الزمني:",
        "radar": "🛰️ رادار الأمطار الحية",
        "generate_btn": "📊 توليد وتحليل التدوينة الجوية",
        "current_status": "🌤️ الحالة اللحظية للطقس اليوم (نموذج ECMWF الأوروبي الدقيق)",
        "temp_label": "الحرارة الحالية",
        "sky_label": "السماء",
        "wind_label": "الرياح",
        "max_temp": "العظمى المقدرة",
        "expert_blog": "📝 تحليل الخبير الأرصادي والتدوينة المخصصة",
        "prayer_title": "🕌 مواقيت الصلاة في",
        "fajr": "الفجر", "dhuhr": "الظهر", "asr": "العصر", "maghrib": "المغرب", "isha": "العشاء",
        "whatsapp_btn": "🟢 مشاركة ملخص الطقس والمواقيت عبر WhatsApp",
        "weekly_title": "📅 التوقعات اليومية للمدى القادم (اضغط للفتح)"
    },
    "English": {
        "title": "Rosso Weather | طقس روصو",
        "select_city": "District:",
        "select_period": "Timeframe:",
        "radar": "🛰️ Live Rain Radar",
        "generate_btn": "📊 Generate Report",
        "current_status": "🌤️ Weather Status (ECMWF Model)",
        "temp_label": "Temp",
        "sky_label": "Sky",
        "wind_label": "Wind",
        "max_temp": "Max Temp",
        "expert_blog": "📝 Meteorologist Analysis Blog",
        "prayer_title": "🕌 Prayers in",
        "fajr": "Fajr", "dhuhr": "Dhuhr", "asr": "Asr", "maghrib": "Maghrib", "isha": "Isha",
        "whatsapp_btn": "🟢 Share Summary via WhatsApp",
        "weekly_title": "📅 Daily Forecast for Coming Period (Click to Expand)"
    }
}

txt = strings[lang]
is_rtl = "direction: rtl; text-align: right;" if lang == "العربية" else "direction: ltr; text-align: left;"

def format_temp(celsius_val):
    if "الفهرنهايت" in unit:
        return f"{(celsius_val * 9/5) + 32:.1f}°F"
    return f"{celsius_val:.1f}°C"

LOGO_FILE = "1779505332712.jpg"
if os.path.exists(LOGO_FILE): 
    st.markdown("<style>.stImage img {border-radius: 50%; border: 2px solid #1E88E5; max-width: 65px; margin: 0 auto; display: block;}</style>", unsafe_allow_html=True)
    st.image(LOGO_FILE)

st.markdown(f"<h3 style='text-align: center; color: #1E88E5; font-family: Arial; margin:0; padding:0; {is_rtl}'>{txt['title']}</h3>", unsafe_allow_html=True)

locations_map = {
    "روصو": {"lat": 16.51, "lon": -15.81}, "اركيز": {"lat": 16.91, "lon": -15.28},
    "المذرذرة": {"lat": 16.92, "lon": -15.80}, "بوتلميت": {"lat": 17.54, "lon": -14.77},
    "واد الناقة": {"lat": 17.98, "lon": -15.49}, "كرمسين": {"lat": 16.49, "lon": -16.20},
    "تكنت": {"lat": 17.24, "lon": -16.14}, "انجاكو": {"lat": 16.53, "lon": -16.45}
}

col_city, col_time, col_rad_check = st.columns([2, 1.5, 1.5])
with col_city:
    selected_city = st.selectbox(txt["select_city"], list(locations_map.keys()), label_visibility="collapsed")
with col_time:
    period_map = {"24 ساعة": 24, "5 أيام": 120, "10 أيام": 240, "16 يوماً": 384}
    period = st.selectbox(txt["select_period"], list(period_map.keys()), label_visibility="collapsed")
with col_rad_check:
    show_radar = st.checkbox(txt["radar"], value=False)

lat = locations_map[selected_city]["lat"]
lon = locations_map[selected_city]["lon"]

if show_radar:
    custom_map_html = f"""
    <div style="width: 100%; height: 260px; border-radius: 8px; overflow: hidden; border: 2px solid #1E88E5; position: relative; background-color: #1a1a1a; margin-bottom:5px;">
        <div style="width: 100%; height: 100%; top: -45px; position: absolute;">
            <iframe src="https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&zoom=7&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&type=map" 
                    width="100%" height="350px" frameborder="0" style="border:0; clip-path: inset(45px 0px 45px 0px);">
            </iframe>
        </div>
    </div>
    """
    components.html(custom_map_html, height=265)

if st.button(txt["generate_btn"], use_container_width=True):
    with st.spinner("جاري جلب البيانات..."):
        try:
            h = period_map[period]
            
            # استدعاء دالة جلب البيانات السريعة والمخزنة مؤقتاً لمنع التهنيج
            data, prayer_data =
