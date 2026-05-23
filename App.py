import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="طقس روصو الذكي", page_icon="⛈️", layout="centered")

st.markdown("<h1 style='text-align: center;'>⛈️ تطبيق طقس روصو الذكي</h1>", unsafe_allow_html=True)
st.write("---")

# 1. الخريطة التفاعلية
st.subheader("📍 خريطة الطقس التفاعلية")
# ننشئ خريطة بمركز روصو
m = folium.Map(location=[16.51, -15.81], zoom_start=10)
folium.Marker([16.51, -15.81], popup="روصو", tooltip="روصو").add_to(m)
# عرض الخريطة
st_folium(m, width=700, height=300)

# 2. التحليل
location = st.text_input("📍 اكتب اسم المنطقة المراد تحليلها:", "روصو")
lat, lon = (16.51, -15.81) if "روصو" in location else (20.0, -12.0)

period = st.selectbox("📆 اختر الفترة الزمنية:", [
    "اليوم القادم (24 ساعة)", "الأيام الـ 3 القادمة", "أسبوع قادم", "16 يوماً"
])

if st.button("🚀 بدء التحليل"):
    with st.spinner("جاري التحليل..."):
        try:
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=precipitation_probability,precipitation,relative_humidity_700hPa&forecast_days=16&timezone=auto"
            weather_res = requests.get(weather_url).json()
            
            if "hourly" in weather_res:
                hours = {"اليوم القادم (24 ساعة)": 24, "الأيام الـ 3 القادمة": 72, "أسبوع قادم": 168, "16 يوماً": 384}[period]
                
                raw_prob = weather_res["hourly"]["precipitation_probability"][:hours]
                raw_precip = weather_res["hourly"]["precipitation"][:hours]
                
                max_prob = max([x if x is not None else 0 for x in raw_prob])
                total_precip = sum([x if x is not None else 0.0 for x in raw_precip])
                
                st.success("🎯 تحليل جاهز!")
                st.write(f"**أعلى احتمالية أمطار:** {max_prob}%")
                st.write(f"**مجموع التساقطات المتوقع:** {total_precip:.1f} ملم")
        except Exception as e:
            st.error(f"خطأ: {e}")
            
