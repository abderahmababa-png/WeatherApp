import streamlit as st
import requests

st.set_page_config(page_title="طقس روصو الذكي", page_icon="⛈️", layout="centered")

st.markdown("<h1 style='text-align: center;'>⛈️ تطبيق طقس روصو الذكي</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aaa;'>محلل ومبسط الطقس الاحترافي - يعطيك الخلاصة نصاً المشرفة على التطورات العالمية</p>", unsafe_allow_html=True)
st.write("---")

# الإعدادات الافتراضية لمدينة روصو
location = "روصو"
lat, lon = 16.51, -15.81

period = st.selectbox("📆 اختر الفترة الزمنية التي تريد تحليلها:", ["اليوم القادم (24 ساعة)", "الأيام الـ 3 القادمة"])

if st.button("🚀 بدء التحليل الكيميائي السائل"):
    with st.spinner("جاري جلب البيانات وتحليل الخرائط العالمية..."):
        try:
            # جلب بيانات الطقس (بما في ذلك احتمالية الأمطار الساعية والرطوبة عند 700 هكتوباسكال)
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_700hPa,precipitation_probability,precipitation&wind_speed_10m_max=850hPa&timezone=auto"
            weather_res = requests.get(weather_url).json()
            
            if "hourly" in weather_res:
                hourly_data = weather_res["hourly"]
                
                # تحديد عدد الساعات بناءً على اختيار المستخدم
                hours = 24 if period == "اليوم القادم (24 ساعة)" else 72
                
                # حساب المؤشرات
                max_prob = max(hourly_data["precipitation_probability"][:hours])
                total_precip = sum(hourly_data["precipitation"][:hours])
                avg_rh_700 = sum(hourly_data["relative_humidity_700hPa"][:hours]) / hours
                
                st.success("🎯 تم الانتهاء من تحليل البيانات الخام بنجاح!")
                st.subheader(f"📊 التقرير التحليلي التلقائي لـ {location}:")
                
                # صياغة النص الذكي بناءً على النماذج العالمية
                analysis_text = f"""
                تحليل وضعية الطقس بناءً على **النموذج الأوروبي (ECMWF)** و**النموذج الأمريكي (GFS)** للفترة المحددة:
                
                *   **احتمالية الأمطار:** تشير الارتباطات إلى أن أعلى نسبة لاحتمالية هطول الأمطار في هذه الفترة تصل إلى **{max_prob}%**، مع مجموع تساقطات متوقع يبلغ **{total_precip:.1f} ملم**.
                *   **الرطوبة في الطبقات البنائية (700hPa):** معدل الرطوبة الحالي في طبقة الجو المتوسطة هو **{avg_rh_700:.1f}%**، وهو مؤشر أساسي لمدى تطور السحب الركامية المحلية (Hegri).
                *   **الخلاصة الميدانية:** الوضعية العامة تشير إلى استقرار نسبي مع فرص { 'مبشرة بنشاط رعدي محلي' if max_prob > 40 else 'ضعيفة لتشكل جبهات ممطرة معتبرة خلال الساعات القادمة' }.
                """
                st.markdown(analysis_text)
            else:
                st.error("عذراً، لم نتمكن من تحليل هيكلية البيانات القادمة من الخادم العالمي.")
        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة البيانات: {e}")
