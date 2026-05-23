import streamlit as st
import requests
import os

st.set_page_config(page_title="طقس روصو الذكي", page_icon="⛈️", layout="centered")

# اسم ملف الصورة الرقمي الخاص بك في المستودع
LOGO_FILE = "1779505332712.jpg"

# تجميل وعرض الشعار في الأعلى على شكل دائرة مقصوصة باحترافية وبحجم متناسق للهاتف
if os.path.exists(LOGO_FILE):
    st.markdown(f"""
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 10px;">
        <div style="width: 160px; height: 160px; border-radius: 50%; overflow: hidden; border: 3px solid #4CAF50; box-shadow: 0px 4px 10px rgba(0,0,0,0.3); background-color: #1a1a1a;">
            <img src="./app/static/{LOGO_FILE}" style="width: 145%; height: 145%; object-fit: cover; object-position: 48% 40%; transform: translate(-15%, -15%);">
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center;'>⛈️ تطبيق طقس روصو الذكي</h1>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #aaa; font-size: 14px;'>محلل ومبسط الطقس الاحترافي - الخلاصة والخرائط التنبؤية الحية</p>", unsafe_allow_html=True)
st.write("---")

# عنوان قسم الرادار
st.markdown("<h3 style='text-align: center; color: #4CAF50;'>🛰️ رادار طقس روصو التفاعلي لحركة الأمطار والسحب</h3>", unsafe_allow_html=True)

# الخدعة البرمجية: استخدام نفس الدائرة الصغيرة المقصوصة بدقة لتغطية علامة Windy تماماً
custom_map_html = f"""
<div style="position: relative; width: 100%; height: 450px; border: 2px solid #4CAF50; border-radius: 10px; overflow: hidden;">
    <!-- الدائرة الصغيرة الذكية التي تحجب علامة الموقع في الزاوية اليسرى العليا -->
    <div style="position: absolute; top: 8px; left: 8px; width: 55px; height: 55px; z-index: 999; border-radius: 50%; overflow: hidden; border: 2px solid #4CAF50; box-shadow: 0px 2px 5px rgba(0,0,0,0.5); background-color: #1a1a1a;">
        <img src="./app/static/{LOGO_FILE}" style="width: 145%; height: 145%; object-fit: cover; object-position: 48% 40%; transform: translate(-15%, -15%);" onerror="this.src='https://via.placeholder.com/55/1a1a1a/4CAF50?text=R';">
    </div>
    
    <!-- الخريطة التفاعلية الحية -->
    <iframe 
        src="https://embed.windy.com/embed2.html?lat=16.51&lon=-15.81&zoom=8&level=surface&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default&radarRange=-1" 
        width="100%" 
        height="100%" 
        frameborder="0">
    </iframe>
</div>
"""

st.components.v1.html(custom_map_html, height=460)

st.write("---")

# 2. قسم التحليل الرقمي واستخلاص المؤشرات
st.subheader("📊 التحليل الرقمي واستخلاص المؤشرات")
location = st.text_input("📍 اكتب اسم المنطقة المراد تحليلها:", "روصو")

if "روصو" in location:
    lat, lon = 16.51, -15.81
else:
    lat, lon = 20.0, -12.0

period = st.selectbox("📆 اختر الفترة الزمنية التي تريد تحليلها:", [
    "اليوم القادم (24 ساعة)", 
    "الأيام الـ 3 القادمة", 
    "أسبوع قادم (7 أيام)", 
    "16 يوماً القادمة"
])

if st.button("🚀 بدء التحليل الرقمي السائل"):
    with st.spinner("جاري جلب البيانات وتحليل الخرائط العالمية..."):
        try:
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_700hPa,precipitation_probability,precipitation&forecast_days=16&timezone=auto"
            weather_res = requests.get(weather_url).json()
            
            if "hourly" in weather_res:
                hourly_data = weather_res["hourly"]
                
                if period == "اليوم القادم (24 ساعة)":
                    hours = 24
                elif period == "الأيام الـ 3 القادمة":
                    hours = 72
                elif period == "أسبوع قادم (7 أيام)":
                    hours = 168
                else:
                    hours = 384
                
                clean_prob = [x if x is not None else 0 for x in hourly_data["precipitation_probability"][:hours]]
                clean_precip = [x if x is not None else 0.0 for x in hourly_data["precipitation"][:hours]]
                clean_rh = [x if x is not None else 0 for x in hourly_data["relative_humidity_700hPa"][:hours]]
                
                max_prob = max(clean_prob) if clean_prob else 0
                total_precip = sum(clean_precip) if clean_precip else 0.0
                avg_rh_700 = (sum(clean_rh) / len(clean_rh)) if clean_rh else 0
                
                st.success("🎯 تم الانتهاء من تحليل البيانات بنجاح!")
                
                analysis_text = f"""
                *   **احتمالية الأمطار:** أعلى نسبة لاحتمالية هطول الأمطار في هذه الفترة تصل إلى **{max_prob}%**، بمجموع تساقطات متوقع **{total_precip:.1f} ملم**.
                *   **الرطوبة البنائية (700hPa):** معدل الرطوبة في طبقة الجو المتوسطة هو **{avg_rh_700:.1f}%**، وهو المؤشر الأساسي لتطور السحب الركامية المحلية الرعدية.
                """
                st.markdown(analysis_text)
            else:
                st.error("عذراً، لم نتمكن من جلب هيكلية البيانات.")
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
