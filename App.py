import streamlit as st
import json
import urllib.request
import os
from datetime import datetime

# 1. تنسيق الواجهة وحذف الأدوات المزعجة
st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"] { overscroll-behavior-y: contain; touch-action: pan-x pan-y !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    header, footer, #MainMenu { visibility: hidden !important; }
    th, td { text-align: right !important; padding: 8px !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. مصفوفة المقاطعات والمراكز (مختصرة ومثالية)
locations_map = {
    "روصو (العاصمة)": {"lat": 16.5165, "lon": -15.8050},
    "المذرذرة": {"lat": 16.9200, "lon": -15.7900},
    "اركيز": {"lat": 16.9150, "lon": -15.2830},
    "بوتلميت": {"lat": 17.5480, "lon": -14.7350},
    "كرمسين": {"lat": 16.4950, "lon": -16.2550},
    "تكنت": {"lat": 17.1600, "lon": -16.0100},
    "انتيكان": {"lat": 16.5400, "lon": -15.1500},
    "واد الناقة": {"lat": 17.9100, "lon": -15.4800},
    "أم القرى": {"lat": 16.7200, "lon": -15.9000},
    "النبغية": {"lat": 17.1500, "lon": -15.1200}
}

# 3. بناء الشريط الجانبي (مواقيت الصلاة والقائمة بدون حزم إضافية)
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>⛈️ منصة نصرة</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>🕋 مواقيت الصلاة (الترارزة)</h4>", unsafe_allow_html=True)
    
    # جدول مواقيت الصلاة خفيف جداً بـ HTML
    st.markdown("""
    <table style='width:100%; direction: rtl; border: 1px solid #ddd; border-collapse: collapse;'>
        <tr style='background-color: #1E88E5; color: white;'><th>الصلاة</th><th>التوقيت</th></tr>
        <tr><td>الفجر</td><td>05:05</td></tr><tr><td>الشروق</td><td>06:34</td></tr>
        <tr><td>الظهر</td><td>13:02</td></tr><tr><td>العصر</td><td>16:19</td></tr>
        <tr><td>المغرب</td><td>19:31</td></tr><tr><td>العشاء</td><td>20:50</td></tr>
    </table>
    """, unsafe_allow_html=True)
    
    st.write("---")
    selected_city = st.selectbox("📍 اختر المقاطعة أو المركز الإداري:", list(locations_map.keys()))

# 4. الواجهة الرئيسية والتوقعات الحية
st.title("⛈️ نصرة - منصة طقس روصو والترارزة")
st.markdown(f"<h5>رصد حي ومباشر وتوقعات الأمطار في: <b style='color: #1E88E5;'>{selected_city}</b></h5>", unsafe_allow_html=True)

lat = locations_map[selected_city]["lat"]
lon = locations_map[selected_city]["lon"]

# جلب البيانات عبر urllib الأساسية (أمن وسريع ومضمون)
@st.cache_data(ttl=600)
def fetch_weather_light(latitude, longitude):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&hourly=temperature_2m,rain,precipitation_probability&timezone=Africa/Nouakchott"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except:
        return None

weather_json = fetch_weather_light(lat, lon)

if weather_json:
    current = weather_json["current_weather"]
    
    # كروت الحالة الرصدية الفورية
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🌡️ الحرارة الحالية", value=f"{current['temperature']} °C")
    with col2:
        st.metric(label="💨 سرعة الرياح", value=f"{current['windspeed']} كم/س")
    with col3:
        st.metric(label="👀 كود الحالة", value=f"مستقر ({current['weathercode']})")
        
    st.write("---")
    
    # 5. جدول رصد توقعات الأمطار الخفيف (بدون Pandas الحزمة المسببة للانهيار)
    st.subheader("⛈️ رصد توقعات الأمطار للساعات القادمة")
    hourly = weather_json["hourly"]
    
    table_rows = ""
    for i in range(8): # عرض 8 ساعات قادمة فقط للاختصار والسلاسة
        time_clean = hourly["time"][i].split("T")[1]
        temp = hourly["temperature_2m"][i]
        prob = hourly["precipitation_probability"][i]
        rain = hourly["rain"][i]
        table_rows += f"<tr><td>{time_clean}</td><td>{temp}°C</td><td>{prob}%</td><td>{rain} ملم</td></tr>"
        
    st.markdown(f"""
    <table style='width:100%; direction: rtl; border-collapse: collapse; text-align: center;'>
        <tr style='background-color: #f2f2f2;'><th>الوقت</th><th>الحرارة</th><th>احتمالية المطر</th><th>كمية المطر</th></tr>
        {table_rows}
    </table>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # 6. الرادار التفاعلي المباشر (حركة السحب والبروق)
    st.subheader("🗺️ الرادار التفاعلي المباشر وحركة السحب والبروق")
    windy_url = f"https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&detailLat={lat}&detailLon={lon}&zoom=8&level=surface&overlay=rain&product=ecmwf&type=map"
    st.components.v1.iframe(windy_url, height=450, scrolling=False)

else:
    st.error("عذراً، فشل الاتصال بخادم الأرصاد الجوية الحية. يرجى التحقق من الإنترنت.")

st.write("---")
st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>منصة نصرة الرقمية لطقس ولاية الترارزة • بيانات أرصاد حقيقية دقيقة</p>", unsafe_allow_html=True)
