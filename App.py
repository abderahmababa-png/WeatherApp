import streamlit as st
import requests
import os

st.set_page_config(page_title="طقس روصو الذكي", page_icon="⛈️", layout="centered")

# اسم ملف الصورة الرقمي الخاص بك في المستودع
LOGO_FILE = "1779505332712.jpg"

# إضافة كود CSS لعمل الدائرة بشكل آمن ومضمون 100% على السيرفر
st.markdown("""
<style>
    /* تعديل كافة الصور في واجهة التطبيق لتصبح دائرية وبحجم متناسق */
    .stImage img {
        border-radius: 50%;
        border: 3px solid #4CAF50;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        max-width: 160px;
        margin: 0 auto;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# عرض الشعار في الأعلى مقصوصاً كدائرة باحترافية عبر أداة Streamlit الرسمية
if os.path.exists(LOGO_FILE):
    st.image(LOGO_FILE, width=160)
else:
    st.markdown("<h1 style='text-align: center;'>⛈️ تطبيق طقس روصو الذكي</h1>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #aaa; font-size: 14px;'>محلل ومبسط الطقس الاحترافي - الخلاصة والخرائط التنبؤية الحية</p>", unsafe_allow_html=True)
st.write("---")

# عنوان قسم الرادار
st.markdown("<h3 style='text-align: center; color: #4CAF50;'>🛰️ رادار طقس روصو التفاعلي لحركة الأمطار والسحب</h3>", unsafe_allow_html=True)

# الخدعة البرمجية: إخفاء علامة Windy عبر شريط داكن صغير مخصص يحتوي على نص أنيق
custom_map_html = """
<div style="position: relative; width: 100%; height: 450px; border: 2px solid #4CAF50; border-radius: 10px; overflow: hidden;">
    <!-- غطاء علامة الموقع في الزاوية اليسرى العليا -->
    <div style="position: absolute; top: 0; left: 0; width: 150px; height: 45px; background-color: #222222; z-index: 999; display: flex; align-items: center; justify-content: center; border-bottom-right-radius: 8px; border-right: 1px solid #4CAF50; border-bottom: 1px solid #4CAF50;">
        <span style="color: #4CAF50; font-family: Arial, sans-serif; font-size: 14px; font-weight: bold;">⛈️ رادار روصو</span>
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
