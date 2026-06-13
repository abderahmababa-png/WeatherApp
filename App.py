           import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة العامة واختيار المظهر الواسع
st.set_page_config(
    page_title="منصة طقس روصو والترارزة",
    page_icon="⛈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تحسين مظهر الواجهة وإخفاء شريط أدوات التطوير العلوي (GitHub & Fork)
st.markdown("""
    <style>
    /* توجيه الواجهة بالكامل لتناسب اللغة العربية */
    .reportview-container .main .block-container { direction: rtl; }
    .sidebar .sidebar-content { direction: rtl; }
    th, td { text-align: right !important; }
    
    /* إخفاء الشريط العلوي بالكامل (شعار جيت هوب، زر Fork، والنقاط الثلاث) */
    header { visibility: hidden; }
    
    /* إخفاء القائمة الافتراضية وتذييل الصفحة الخاص بـ Streamlit لزيادة الاحترافية */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)


# 2. إعداد بيانات المدن والمقاطعات في ولاية الترارزة
CITIES = {
    "روصو (العاصمة)": {"lat": 16.5165, "lon": -15.8050},
    "المذرذرة": {"lat": 16.9200, "lon": -15.7900},
    "اركيز": {"lat": 16.9150, "lon": -15.2830},
    "بوتلميت": {"lat": 17.5480, "lon": -14.7350},
    "كرمسين": {"lat": 16.4950, "lon": -16.2550},
    "تكنت": {"lat": 17.1600, "lon": -16.0100}
}


# --- 3. الشريط الجانبي (Sidebar) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🕋 مواقيت الصلاة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>التوقيت المحلي لمدينة روصو وضواحيها</p>", unsafe_allow_html=True)
    st.write("---")
    
    # عرض المواقيت في جدول مدمج وبسيط لا يأخذ مساحة عمودية كبيرة
    prayer_data = {
        "الصلاة": ["الفجر", "الظهر", "العصر", "المغرب", "العشاء"],
        "الوقت": ["05:05", "13:00", "16:15", "19:30", "20:45"]
    }
    df_prayer = pd.DataFrame(prayer_data)
    st.table(df_prayer.set_index("الصلاة"))
    
    st.write("---")
    
    # إضافة خيار اختيار المدينة داخل الشريط الجانبي أيضاً لتنظيف الواجهة الرئيسية
    st.markdown("### 📍 تحديد الموقع")
    selected_city = st.selectbox("اختر المقاطعة أو المركز المُراد رصده:", list(CITIES.keys()))
    
    st.write("---")
    st.caption(f"آخر تحديث للواجهة: {datetime.now().strftime('%H:%M')}")


# --- 4. القسم الرئيسي للتطبيق (Main Page) ---
st.title("🌤️ منصة طقس روصو الرقمية (Rosso Weather)")
st.markdown(f"متابعة حية ومباشرة للحالة الجوية الحالية وتوقعات الأمطار في **{selected_city}** بناءً على الأرصاد الفعلية ونماذج الطقس العالمية.")
st.write("---")

# جلب الإحداثيات بناءً على اختيار المستخدم
lat = CITIES[selected_city]["lat"]
lon = CITIES[selected_city]["lon"]


# 5. دالة جلب بيانات الطقس الحقيقية من Open-Meteo API
@st.cache_data(ttl=600)  # تحديث التخزين المؤقت كل 10 دقائق
def fetch_weather_data(latitude, longitude):
    # نطلب بيانات الطقس الحالي + توقعات المطر والرطوبة لكل ساعة لـ 24 ساعة القادمة
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
    # أ. استخراج بيانات الطقس الحالي
    current = weather_json["current_weather"]
    
    # تحويل كود الطقس الرقمي إلى وصف نصي واقعي ومباشر
    weather_codes = {
        0: "سماء صافية مستقرة", 1: "صافي غالباً", 2: "غائم جزئياً", 3: "غائم بالكامل",
        51: "رذاذ خفيف", 53: "رذاذ معتدل", 61: "أمطار خفيفة", 63: "أمطار معتدلة", 
        65: "أمطار غزيرة", 80: "زخات مطر خفيفة", 81: "زخات مطر قوية"
    }
    status_desc = weather_codes.get(current["weathercode"], "مستقر")

    # ب. عرض المؤشرات الحالية في أعمدة جذابة ومباشرة
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="🌡️ درجة الحرارة الحالية", value=f"{current['temperature']} °C")
    with col2:
        st.metric(label="📊 الحالة الرصدية الفعلية", value=status_desc)
    with col3:
        st.metric(label="💨 سرعة الرياح", value=f"{current['windspeed']} كم/س")
    with col4:
        # جلب الرطوبة الحالية من أول قراءة متاح في التوقعات الساعية
        current_humidity = weather_json["hourly"]["relative_humidity_2m"][0]
        st.metric(label="💧 نسبة الرطوبة", value=f"{current_humidity}%")

    st.write("---")

    # ج. قسم توقعات الأمطار للساعات القادمة (مهم جداً لمراقبة الخريف)
    st.subheader("⛈️ جدول رصد توقعات الأمطار (خلال الساعات القادمة)")
    
    hourly_data = weather_json["hourly"]
    # تحويل البيانات إلى dataframe وعرض الساعات الـ 6 القادمة فقط للاختصار والدقة
    df_hourly = pd.DataFrame({
        "الوقت": [t.split("T")[1] for t in hourly_data["time"][:6]],
        "درجة الحرارة (°C)": hourly_data["temperature_2m"][:6],
        "احتمالية المطر (%)": hourly_data["precipitation_probability"][:6],
        "كمية المطر المتوقعة (ملم)": hourly_data["rain"][:6]
    })
    
    st.dataframe(df_hourly.set_index("الوقت"), use_container_width=True)
    
    st.write("---")

    # د. قسم خريطة الرادار التفاعلية المباشرة (Windy)
    st.subheader("🗺️ الرادار المباشر وحركة السحب والأمطار")
    st.markdown("الرادار مضبوط تلقائياً على نموذج **ECMWF** الأوروبي لمتابعة الجبهات الماطرة وجبهات السحب الحية فوق المنطقة جنوب موريتانيا.")
    
    # تضمين خريطة Windy التفاعلية مع تمرير إحداثيات المدينة المختارة ديناميكياً
    windy_iframe_url = f"https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&detailLat={lat}&detailLon={lon}&width=1000&height=500&zoom=8&level=surface&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default&radarRange=-1"
    
    st.components.v1.iframe(windy_iframe_url, height=500, scrolling=False)

else:
    st.error("عذراً، فشل التطبيق في الاتصال بـ API الأرصاد الجوية. يرجى التحقق من اتصال الإنترنت أو المحاولة لاحقاً.")

# تذييل الصفحة وثبات الهوية الموثوقة للتطبيق
st.write("---")
st.markdown("<p style='text-align: center; color: gray;'>تطبيق Rosso Weather - بيانات مرصودة حقيقية خالية من التخمين</p>", unsafe_allow_html=True)
