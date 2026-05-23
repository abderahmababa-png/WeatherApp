import streamlit as st
import requests

st.set_page_config(page_title="طقس روصو الذكي", page_icon="⛈️", layout="centered")

st.markdown("<h1 style='text-align: center;'>⛈️ تطبيق طقس روصو الذكي</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aaa;'>محلل ومبسط الطقس الاحترافي - الخلاصة والخرائط التنبؤية الحية</p>", unsafe_allow_html=True)
st.write("---")

# 1. الخريطة التنبؤية الحية المباشرة (رادار حركة الأمطار والسحب من Windy)
st.subheader("🗺️ رادار ومؤشرات الطقس الحية (توقعات الأمطار والسحب)")

# تضمين خريطة Windy التفاعلية التنبؤية الممركزة على موريتانيا وروصو بدقة
windy_iframe = """
<iframe 
    src="https://embed.windy.com/embed2.html?lat=16.51&lon=-15.81&zoom=6&level=surface&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default&radarRange=-1" 
    width="100%" 
    height="400" 
    frameborder="0">
</iframe>
"""
st.components.v1.html(windy_iframe, height=410)

st.write("---")

# 2. قسم التحليل الرقمي الذكي للبيانات الخام
st.subheader("📊 التحليل الرقمي واستخلاص المؤشرات")
location = st.text_input("📍 اكتب اسم المنطقة المراد تحليلها:", "روصو")

# تحديد الإحداثيات بدقة لمدينة روصو
if "روصو" in location:
    lat, lon = 16.51, -15.81
else:
    lat, lon = 20.0, -12.0

period = st.selectbox("📆 اختر الفترة الزمنية التي تريد تحليلها:", [
    "اليوم القادم (24 ساعة)", 
    "الأيام الـ 3 القادمة", 
    "أسبوع قادم (7 أيام)", 
    "16 يوماً القادمة (أقصى حد للتوقعات المباشرة)"
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
