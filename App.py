import streamlit as st
import requests
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="روصو للطقس - Rosso Weather", page_icon="🌤️", layout="wide")

# --- 1. الشريط الجانبي (Sidebar) لمواقيت الصلاة ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🕋 مواقيت الصلاة</h2>", unsafe_allow_title=True)
    st.markdown("<p style='text-align: center; color: gray;'>مدينة روصو وضواحيها</p>", unsafe_allow_html=True)
    st.write("---")
    
    # عرض المواقيت في جدول منظم وأنيق يناسب الشريط الجانبي
    timings = {
        "الصلاة": ["الفجر", "الظهر", "العصر", "المغرب", "العشاء"],
        "الوقت": ["05:05", "13:00", "16:15", "19:30", "20:45"]
    }
    df_pray = pd.DataFrame(timings)
    st.table(df_pray.set_index("الصلاة"))
    
    st.write("---")
    st.caption("ملاحظة: يرجى مراعاة فروق التوقيت المحلية.")

# --- 2. القسم الرئيسي للتطبيق (Main Page) ---
st.title("🌤️ منصة طقس روصو الرقمية")
st.markdown("متابعة حية ومباشرة للحالة الجوية في عاصمة ولاية الترارزة بناءً على الأرصاد الفعلية.")
st.write("---")

# إحداثيات مدينة روصو
LAT, LON = 16.5165, -15.8050

# جلب بيانات الطقس الحية من API موثوق (بدون توقعات عشوائية أو غبار غير مرئي)
@st.cache_data(ttl=600)  # تخزين مؤقت للبيانات لمدة 10 دقائق
def get_live_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=rain,relative_humidity_2m"
    try:
        response = requests.get(url).json()
        return response['current_weather'], response['hourly']
    except:
        return None, None

current, hourly = get_live_weather(LAT, LON)

if current:
    # عرض المؤشرات الأساسية للطقس الحالي
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="🌡️ درجة الحرارة الحالية", value=f"{current['temperature']} °C")
    with col2:
        # تحويل كود الطقس إلى وصف واقعي بسيط
        weather_desc = "صافي ومستقر" if current['weathercode'] == 0 else "غائم جزئياً" if current['weathercode'] in [1,2,3] else "أمطار"
        st.metric(label="📊 حالة السماء الحالية", value=weather_desc)
    with col3:
        st.metric(label="💨 سرعة الرياح", value=f"{current['windspeed']} كم/س")
        
    st.write("---")
    
    # --- 3. قسم خريطة الرادار التفاعلية (Windy / Radar Layers) ---
    st.subheader("🗺️ الرادار المباشر وحركة السحب")
    
    # تضمين خريطة تفاعلية لـ Windy تركز على منطقة روصو وجنوب موريتانيا
    # يمكنك تغيير الـ overlay إلى 'rain' لمتابعة السحب الممطرة في الخريف
    windy_url = f"https://embed.windy.com/embed2.html?lat={LAT}&lon={lon}&detailLat={LAT}&detailLon={lon}&width=700&height=450&zoom=8&level=surface&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default&radarRange=-1"
    
    st.components.v1.iframe(windy_url, height=450, scrolling=False)

else:
    st.error("عذراً، تعذر الاتصال بمزود بيانات الطقس حالياً. يرجى إعادة المحاولة لاحقاً.")

# تثبيت تذييل الصفحة
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>تطبيق Rosso Weather - بيانات دقيقة ومباشرة من الرادار</p>", unsafe_allow_html=True)
