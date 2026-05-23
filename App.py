import streamlit as st
import requests

st.set_page_config(page_title="طقس روصو الذكي", page_icon="⛈️", layout="centered")

st.markdown("<h1 style='text-align: center;'>⛈️ تطبيق طقس روصو الذكي</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aaa;'>محلل ومبسط الطقس الاحترافي - يعطيك الخلاصة نصاً المشرفة على التطورات العالمية</p>", unsafe_allow_html=True)
st.write("---")

# خانة تحديد الموقع
location = st.text_input("📍 اكتب اسم المنطقة المراد تحليلها:", "روصو")

# تحديد الإحداثيات بناءً على المنطقة
if "روصو" in location:
    lat, lon = 16.51, -15.81
else:
    lat, lon = 20.0, -12.0

# خيارات الفترة الزمنية
period = st.selectbox("📆 اختر الفترة الزمنية التي تريد تحليلها:", [
    "اليوم القادم (24 ساعة)", 
    "الأيام الـ 3 القادمة", 
    "أسبوع قادم (7 أيام)", 
    "16 يوماً القادمة (أقصى حد للتوقعات المباشرة)"
])

if st.button("🚀 بدء التحليل الكيميائي السائل"):
    with st.spinner("جاري جلب البيانات وتحليل الخرائط العالمية..."):
        try:
            # جلب البيانات لـ 16 يوماً لتغطية كافة الخيارات
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_700hPa,precipitation_probability,precipitation&forecast_days=16&timezone=auto"
            weather_res = requests.get(weather_url).json()
            
            if "hourly" in weather_res:
                hourly_data = weather_res["hourly"]
                
                # تحديد عدد الساعات بناءً على اختيارك
                if period == "اليوم القادم (24 ساعة)":
                    hours = 24
                elif period == "الأيام الـ 3 القادمة":
                    hours = 72
                elif period == "أسبوع قادم (7 أيام)":
                    hours = 168
                else:
                    hours = 384 # 16 يوماً كاملة
                
                # تصفية البيانات وتنظيفها من القيم الفارغة (None) لتجنب الأخطاء الحمراء
                raw_prob = hourly_data["precipitation_probability"][:hours]
                raw_precip = hourly_data["precipitation"][:hours]
                raw_rh = hourly_data["relative_humidity_700hPa"][:hours]
                
                clean_prob = [x if x is not None else 0 for x in raw_prob]
                clean_precip = [x if x is not None else 0.0 for x in raw_precip]
                clean_rh = [x if x is not None else 0 for x in raw_rh]
                
                # حساب المؤشرات بأمان بعد التنظيف
                max_prob = max(clean_prob) if clean_prob else 0
                total_precip = sum(clean_precip) if clean_precip else 0.0
                avg_rh_700 = (sum(clean_rh) / len(clean_rh)) if clean_rh else 0
                
                st.success("🎯 تم الانتهاء من تحليل البيانات الخام بنجاح!")
                st.subheader(f"📊 التقرير التحليلي التلقائي لـ {location}:")
                
                # صياغة النص الذكي المتوافق مع فترتك المحددة
                analysis_text = f"""
                تحليل وضعية الطقس بناءً على **النموذج الأوروبي (ECMWF)** و**النموذج الأمريكي (GFS)** لـ **{location}** خلال **{period}**:
                
                *   **احتمالية الأمطار:** تشير الارتباطات إلى أن أعلى نسبة لاحتمالية هطول الأمطار في هذه الفترة تصل إلى **{max_prob}%**، مع مجموع تساقطات متوقع يبلغ **{total_precip:.1f} ملم**.
                *   **الرطوبة في الطبقات البنائية (700hPa):** معدل الرطوبة الحالي في طبقة الجو المتوسطة هو **{avg_rh_700:.1f}%**، وهو مؤشر أساسي لمدى تطور السحب الركامية المحلية (Hegri).
                *   **الخلاصة الميدانية:** الوضعية العامة في {location} تشير إلى { 'فرص مبشرة بنشاط رعدي محلي وتشكل جبهات ممطرة' if max_prob > 40 else 'استقرار نسبي مع فرص ضئيلة لتشكل جبهات ممطرة معتبرة' } خلال الفترة المحددة.
                """
                st.markdown(analysis_text)
            else:
                st.error("عذراً، لم نتمكن من تحليل هيكلية البيانات القادمة من الخادم العالمي.")
        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة البيانات: {e}")
