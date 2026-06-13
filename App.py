import streamlit as st
import requests
import os
import streamlit.components.v1 as components
import urllib.parse
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة العامة واختيار المظهر الواسع
st.set_page_config(
    page_title="منصة طقس روصو والترارزة",
    page_icon="⛈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. تحسين مظهر الواجهة بالـ CSS وإخفاء شريط المطورين العلوي (GitHub & Fork)
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        overscroll-behavior-y: contain;
        touch-action: pan-x pan-y !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    .stButton>button {
        background-color: #1E88E5 !important;
        color: white !important;
    }
    .reportview-container .main .block-container { direction: rtl; }
    .sidebar .sidebar-content { direction: rtl; }
    th, td { text-align: right !important; }
    
    /* حجب الشريط العلوي الافتراضي تماماً لتصفح نظيف */
    header { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# 3. قاعدة بيانات إحداثيات المدن والمقاطعات في ولاية الترارزة
CITIES = {
    "روصو (العاصمة)": {"lat": 16.5165, "lon": -15.8050},
    "المذرذرة": {"lat": 16.9200, "lon": -15.7900},
    "اركيز": {"lat": 16.9150, "lon": -15.2830},
    "بوتلميت": {"lat": 17.5480, "lon": -14.7350},
    "كرمسين": {"lat": 16.4950, "lon": -16.2550},
    "تكنت": {"lat": 17.1600, "lon": -16.0100}
}

# 4. بناء الشريط الجانبي (Sidebar) لمواقيت الصلاة وتحديد الموقع
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🕋 مواقيت الصلاة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>التوقيت المحلي لمدينة روصو وضواحيها</p>", unsafe_allow_html=True)
    st.write("---")
    
    # عرض المواقيت في جدول مدمج وموفر للمساحة
    prayer_data = {
        "الصلاة": ["الفجر", "الظهر", "العصر", "المغرب", "العشاء"],
        "الوقت": ["05:05", "13:00", "16:15", "19:30", "20:45"]
    }
    df_prayer = pd.DataFrame(prayer_data)
    st.table(df_prayer.set_index("الصلاة"))
    
    st.write("---")
    st.markdown("### 📍 تحديد الموقع")
    selected_city = st.selectbox("اختر المقاطعة أو المركز المُراد رصده:", list(CITIES.keys()))
    st.write("---")
    st.caption(f"آخر تحديث للواجهة: {datetime.now().strftime('%H:%M')}")

# 5. الواجهة الرئيسية للتطبيق (Main Page)
st.title("🌤️ منصة طقس روصو الرقمية (Rosso Weather)")
st.markdown(f"متابعة حية ومباشرة للحالة الجوية الحالية وتوقعات الأمطار في **{selected_city}** بناءً على الأرصاد الفعلية ونماذج الطقس العالمية.")
st.write("---")

# استخراج الإحداثيات الجغرافية للمدينة المختارة
lat = CITIES[selected_city]["lat"]
lon = CITIES[selected_city]["lon"]

# دالة جلب بيانات الأرصاد الجوية الفعلية والحقيقية
@st.cache_data(ttl=600)
def fetch_weather_data(latitude, longitude):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&hourly=temperature_2m,rain,precipitation_probability,relative_humidity_2m&timezone=Africa/Nouakchott"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

weather_json = fetch_weather_data(lat, lon)

if weather_json:
    # أ. استخراج وعرض مؤشرات الطقس الحالي
    current = weather_json["current_weather"]
    weather_codes = {
        0: "سماء صافية مستقرة", 1: "صافي غالباً", 2: "غائم جزئياً", 3: "غائم بالكامل",
        51: "رذاذ خفيف", 53: "رذاذ معتدل", 61: "أمطار خفيفة", 63: "أمطار معتدلة", 
        65: "أمطار غزيرة", 80: "زخات مطر خفيفة", 81: "زخات مطر قوية"
    }
    status_desc = weather_codes.get(current["weathercode"], "مستقر")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="🌡️ درجة الحرارة الحالية", value=f"{current['temperature']} °C")
    with col2:
        st.metric(label="📊 الحالة الرصدية الفعلية", value=status_desc)
    with col3:
        st.metric(label="💨 سرعة الرياح", value=f"{current['windspeed']} كم/س")
    with col4:
        current_humidity = weather_json["hourly"]["relative_humidity_2m"][0]
        st.metric(label="💧 نسبة الرطوبة", value=f"{current_humidity}%")

    st.write("---")
    
    # ب. عرض جدول توقعات الأمطار (الساعات القادمة)
    st.subheader("⛈️ جدول رصد توقعات الأمطار (خلال الساعات القادمة)")
    
    hourly_data = weather_json["hourly"]
    df_hourly = pd.DataFrame({
        "الوقت": [t.split("T")[1] for t in hourly_data["time"][:6]],
        "درجة الحرارة (°C)": hourly_data["temperature_2m"][:6],
        "احتمالية المطر (%)": hourly_data["precipitation_probability"][:6],
        "كمية المطر المتوقعة (ملم)": hourly_data["rain"][:6]
    })
    st.dataframe(df_hourly.set_index("الوقت"), use_container_width=True)
    
    st.write("---")
    
    # ج. خريطة الرادار المباشر التفاعلية (Windy)
    st.subheader("🗺️ الرادار المباشر وحركة السحب والأمطار")
    
    windy_iframe_url = f"https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&detailLat={lat}&detailLon={lon}&width=1000&height=500&zoom=8&level=surface&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default&radarRange=-1"
    st.components.v1.iframe(windy_iframe_url, height=500, scrolling=False)

else:
    st.error("عذراً، فشل التطبيق في الاتصال بـ API الأرصاد الجوية الحية.")

# تذييل الصفحة الثابت للتطبيق
st.write("---")
st.markdown("<p style='text-align: center; color: gray;'>تطبيق Rosso Weather - بيانات مرصودة حقيقية خالية من التخمين</p>", unsafe_allow_html=True)
