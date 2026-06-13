import streamlit as st
import requests
import os
import streamlit.components.v1 as components
import urllib.parse
import pandas as pd
from datetime import datetime, timedelta

# 1. إعدادات الصفحة العامة واختيار المظهر الواسع
st.set_page_config(
    page_title="منصة طقس روصو والترارزة",
    page_icon="⛈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تحسين مظهر الواجهة بالـ CSS ومنع مشاكل اللمس على الهواتف وإخفاء شريط أدوات التطوير (GitHub & Fork)
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
    /* توجيه الواجهة بالكامل لتناسب اللغة العربية */
    .reportview-container .main .block-container { direction: rtl; }
    .sidebar .sidebar-content { direction: rtl; }
    th, td { text-align: right !important; }
    
    /* إخفاء الشريط العلوي لـ GitHub وزر Fork تماماً لتصبح الواجهة رسمية ونظيفة */
    header { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# 2. متغيرات إعدادات النظام واللغة والمظهر الأصلي
lang = "ar"
unit = "metric"
display_style = "detailed"
is_rtl = True

# 3. نصوص وهيكل واجهة التطبيق الأصلية بالكامل لـ "منصة نصرة"
strings = {
    "ar": {
        "title": "⛈️ نصرة - منصة طقس روصو والترارزة",
        "subtitle": "رصد حي ومباشر للحالة الجوية، توقعات الأمطار، وحركة السحب الحية جنوب موريتانيا",
        "select_city": "📍 اختر المقاطعة أو المركز الإداري المُراد رصده:",
        "current_weather": "📊 الحالة الرصدية الفعلية الحالية بالتفصيل",
        "temp": "🌡️ درجة الحرارة الحالية",
        "wind": "💨 سرعة واتجاه الرياح العالمية",
        "humidity": "💧 رطوبة الغلاف الجوي الحالية",
        "status": "👀 حالة السماء والرصد الفعلي",
        "rain_table": "⛈️ جدول رصد توقعات الأمطار للساعات القادمة (مراقبة الخريف والسيول)",
        "radar_title": "🗺️ الرادار التفاعلي المباشر وحركة السحب والبروق",
        "radar_desc": "الرادار مضبوط تلقائياً على نموذج ECMWF الأوروبي لمتابعة الجبهات الماطرة وجبهات السحب الحية فوق المنطقة جنوب موريتانيا والمناطق المحاذية للنهر.",
        "prayer_title": "🕋 مواقيت الصلاة (روصو وضواحيها)",
        "prayer_sub": "التوقيت المحلي لولاية الترارزة وضواحيها وفق الهيئة الرسمية شفاها الله",
        "footer_text": "منصة نصرة الرقمية لطقس ولاية الترارزة • بيانات أرصاد حقيقية دقيقة ومباشرة خالية من التخمين والتنبؤات العشوائية",
        "error_api": "عذراً، فشل التطبيق في الاتصال بخادم الأرصاد الجوية الحية. يرجى التحقق من اتصال الإنترنت أو تحديث المتصفح.",
        "time": "الوقت والتوقيت",
        "hourly_temp": "الحرارة المرصودة (°C)",
        "hourly_pop": "احتمالية هطول المطر (%)",
        "hourly_rain": "كمية المطر المتوقعة (ملم)",
        "wind_speed_unit": "كم/س",
        "humidity_unit": "%"
    }
}

txt = strings[lang]

# 4. مصفوفة الإحداثيات والمواقع الجغرافية الكاملة والموسعة لقرى ومدن ولاية الترارزة
locations_map = {
    "روصو (العاصمة)": {"lat": 16.5165, "lon": -15.8050},
    "المذرذرة": {"lat": 16.9200, "lon": -15.7900},
    "اركيز": {"lat": 16.9150, "lon": -15.2830},
    "بوتلميت": {"lat": 17.5480, "lon": -14.7350},
    "كرمسين": {"lat": 16.4950, "lon": -16.2550},
    "تكنت": {"lat": 17.1600, "lon": -16.0100},
    "انتيكان": {"lat": 16.5400, "lon": -15.1500},
    "واد الناقة": {"lat": 17.9100, "lon": -15.4800},
    "جول": {"lat": 16.1200, "lon": -15.1000},
    "لكوارب": {"lat": 16.5200, "lon": -15.7900},
    "أم القرى": {"lat": 16.7200, "lon": -15.9000},
    "النبغية": {"lat": 17.1500, "lon": -15.1200},
    "الذريرة": {"lat": 16.6500, "lon": -15.4500},
    "ابير التورس": {"lat": 16.9800, "lon": -15.5500},
    "التكند الجيد": {"lat": 17.1400, "lon": -16.0200},
    "المبروك": {"lat": 16.6000, "lon": -15.3000}
}

LOGO_FILE = "1779505332712.jpg"

def format_temp(t):
    return f"{t} °C"

# --- 5. بناء الشريط الجانبي (Sidebar) لجدول مواقيت الصلاة والموقع ---
with st.sidebar:
    # التحقق وعرض صورة الشعار الرسمية المرفوعة في مستودعك الخاص
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    else:
        st.markdown(f"<h2 style='text-align: center; color: #1E3A8A;'>{txt['title']}</h2>", unsafe_allow_html=True)
        
    st.markdown(f"<h3 style='text-align: center; color: #1E3A8A;'>{txt['prayer_title']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: gray; font-size: 13px;'>{txt['prayer_sub']}</p>", unsafe_allow_html=True)
    
    # جدول مواقيت الصلاة المفصل الكامل
    prayer_data = {
        "الصلاة": ["الفجر", "الشروق", "الظهر", "العصر", "المغرب", "العشاء"],
        "الوقت": ["05:05", "06:34", "13:02", "16:19", "19:31", "20:50"]
    }
    df_prayer = pd.DataFrame(prayer_data)
    st.table(df_prayer.set_index("الصلاة"))
    
    st.write("---")
    st.markdown(f"### {txt['select_city']}")
    selected_city = st.selectbox("", list(locations_map.keys()), label_visibility="collapsed")
    st.write("---")
    
    # حساب وعرض فارق التوقيت لآخر تحديث للواجهة الجانبية
    current_time_str = datetime.now().strftime('%H:%M:%S')
    st.caption(f"آخر تحديث تلقائي للواجهة الحالية: {current_time_str}")

# --- 6. القسم الرئيسي للتطبيق المنصة الكبرى (Main Page) ---
st.title(txt["title"])
st.markdown(f"<h4 style='color: gray;'>{txt['subtitle']} في مقاطعة <span style='color: #1E88E5; font-weight: bold;'>{selected_city}</span></h4>", unsafe_allow_html=True)
st.write("---")

lat = locations_map[selected_city]["lat"]
lon = locations_map[selected_city]["lon"]

# دالة جلب بيانات الطقس الحقيقية والمكثفة من API العالمي المعتمد
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
    current = weather_json["current_weather"]
    
    # مصفوفة فك التشفير البرمجية الشاملة لجميع أكواد حالات السماء والطقس والأمطار المحتملة
    weather_codes = {
        0: "سماء صافية مستقرة تماماً", 
        1: "صافي إلى قليل الغيوم غالباً", 
        2: "غيوم متفرقة جزئياً في الأفق", 
        3: "غائم بالكامل سماء ملبدة",
        45: "تشكل ضباب كثيف منخفض الرؤية", 
        48: "ضباب جليدي ممتد على النهر",
        51: "رذاذ خفيف ناعم ديمومة", 
        53: "رذاذ معتدل متقطع المظهر", 
        55: "رذاذ كثيف هاضل",
        61: "أمطار خفيفة مستمرة في الهطول", 
        63: "أمطار معتدلة هاضلة مباركة", 
        65: "أمطار غزيرة رعدية متواصلة",
        71: "تساقط خفيف للبرد الثلجي",
        73: "تساقط معتدل للبرد في الأجواء",
        75: "تساقط كثيف للبرد على اليابسة",
        80: "زخات مطرية خفيفة سريعة المرور", 
        81: "زخات مطر قوية متقطعة في الترارزة", 
        82: "عواصف مطرية عنيفة وسيول جارية",
        95: "عاصفة رعدية خفيفة إلى معتدلة السحب",
        96: "عاصفة رعدية قوية مصحوبة بالبرد الكثيف"
    }
    status_desc = weather_codes.get(current["weathercode"], "مستقر وطبيعي حالياً")

    st.subheader(txt["current_weather"])
    
    # توزيع مؤشرات الـ Metrics الأربعة الكبرى في أعمدة أفقية واسعة ومتناسقة
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label=txt["temp"], value=format_temp(current['temperature']))
    with col2:
        st.metric(label=txt["status"], value=status_desc)
    with col3:
        st.metric(label=txt["wind"], value=f"{current['windspeed']} {txt['wind_speed_unit']}")
    with col4:
        current_humidity = weather_json["hourly"]["relative_humidity_2m"][0]
        st.metric(label=txt["humidity"], value=f"{current_humidity}{txt['humidity_unit']}")

    st.write("---")

    # عرض جدول التوقعات التفصيلي الكامل للساعات القادمة لمراقبة أمطار الخريف
    st.subheader(txt["rain_table"])
    
    hourly_data = weather_json["hourly"]
    # بناء الـ DataFrame بالتسميات الأصلية الصحيحة لواجهتك لـ 12 قراءة متتالية
    df_hourly = pd.DataFrame({
        txt["time"]: [t.split("T")[1] for t in hourly_data["time"][:12]],
        txt["hourly_temp"]: hourly_data["temperature_2m"][:12],
        txt["hourly_pop"]: hourly_data["precipitation_probability"][:12],
        txt["hourly_rain"]: hourly_data["rain"][:12]
    })
    st.dataframe(df_hourly.set_index(txt["time"]), use_container_width=True)
    
    st.write("---")

    # تضمين رادار خريطة Windy الذكية التفاعلية لتتبع حركة السحب والبروق الحية
    st.subheader(txt["radar_title"])
    st.markdown(f"<p style='color: gray; font-size: 15px;'>{txt['radar_desc']}</p>", unsafe_allow_html=True)
    
    windy_url = f"https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&detailLat={lat}&detailLon={lon}&width=1000&height=500&zoom=8&level=surface&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default&radarRange=-1"
    components.iframe(windy_url, height=560, scrolling=False)

else:
    st.error(txt["error_api"])

# تذييل الصفحة وثبات الهوية البرمجية الموثوقة لمنصة نصرة وطقس روصو
st.write("---")
st.markdown(f"<p style='text-align: center; color: #1E3A8A; font-weight: bold; font
