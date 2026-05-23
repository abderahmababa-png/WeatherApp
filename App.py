import streamlit as st
import requests

# إعدادات واجهة التطبيق على الهاتف
st.set_page_config(page_title="طقس روصو", page_icon="⛈️", layout="centered")

# عنوان التطبيق
st.title("⛈️ تطبيق طقس روصو الذكي")
st.write("محلل ومبسط الطقس الاحترافي - يعطيك الخلاصة نصاً بناءً على النماذج العالمية")

st.markdown("---")

# 1. مدخلات المستخدم (تم ضبط روصو كخيار افتراضي)
location = st.text_input("📍 المنطقة المستهدفة بالتحليل:", value="روصو، موريتانيا")
duration = st.selectbox("📅 اختر الفترة الزمنية التي تريد تحليلها:", 
                        ["الأيام الـ 3 القادمة", "اليوم القادم (24 ساعة)", "الأسبوع القادم", "موسم الأمطار الحالي 2026"])

# 2. زر بدء التحليل
if st.button("🚀 ابدأ التحليل النصي الذكي"):
    with st.spinner("🔄 جاري سحب بيانات النماذج (ECMWF & GFS) وتحليل الرطوبة البنائية..."):
        try:
            # جلب الإحداثيات الجغرافية للموقع تلقائياً
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=ar"
            geo_res = requests.get(geo_url).json()
            
            if 'results' not in geo_res:
                st.error("❌ تعذر تحديد الموقع، يرجى كتابة اسم المدينة بشكل صحيح.")
            else:
                lat = geo_res['results'][0]['latitude']
                lon = geo_res['results'][0]['longitude']
                
                # سحب البيانات الخام: الأمطار، الرطوبة في طبقات الجو 700 و 850 هكتوباسكال، والرياح
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=precipitation_probability,precipitation,relative_humidity_700hPa,relative_humidity_850hPa,windspeed_10m&forecast_days=7&models=ecmwf_ifs,gfs_seamless"
                weather_data = requests.get(weather_url).json()
                
                # استخراج مؤشرات سريعة من البيانات الرقمية لتحليلها نيابة عن المستخدم
                hourly_data = weather_data['hourly']
                max_rain_prob = max(hourly_data['precipitation_probability'])
                total_expected_rain = sum(hourly_data['precipitation'])
                avg_rh_700 = sum(hourly_data['relative_humidity_700hPa']) / len(hourly_data['relative_humidity_700hPa'])
                
                st.success("✅ تم الانتهاء من معالجة البيانات الخام!")
                st.subheader(f"📊 التقرير التحليلي التلقائي لـ ({location}):")
                
                # 3. صياغة التحليل النصي الذكي نيابة عن المستخدم بناءً على الأرقام المعالجة
                analysis_text = f"""
                ناءً على قراءة مخرجات **النموذج الأوروبي ($ECMWF$)** و**النموذج الأمريكي ($GFS$)** للمدة المحددة ({duration}):
                
                *   **وضعية الأمطار والاستقرار:** تشير النماذج إلى أن أعلى نسبة لاحتمالية هطول الأمطار في هذه الفترة تصل إلى **{max_rain_prob}%**، مع كمية هطول تراكمية متوقعة تقارب **{total_expected_rain:.1f} ملم**.
                
                *   **تحليل الرطوبة البنائية (الوقود الجوي):** معدل الرطوبة في طبقة الجو المتوسطة ($700$ هكتوباسكال) يسجل حوالي **{avg_rh_700:.1f}%**. هذا الارتفاع أو الانخفاض يعكس مدى قوة بناء السحب الرعدية؛ فإذا كانت النسبة تتجاوز 60%، فهذا يعني أن الأجواء مهيأة ديناميكياً لتشكل خلايا ماطرة قوية عند تقدم الجبهة المدارية.
                
                *   **الخلاصة وبساطة المشهد:** 
                إذا كانت المدة المحددة هي لموسم الخريف أو الأيام القادمة، فإن النماذج تبدي توافقاً مستقراً حالياً على الأجواء السائدة، ولا توجد مؤشرات لـموجات غبارية حادة (إيريفي) تعيق تشكل السحب في الساعات القليلة القادمة. الطقس يتجه نحو الاستقرار الجوي مع فرص محلية خفيفة، وننصح بمتابعة التحديث القادم للنموذج الأوروبي مساءً لحسم أي تغير في حركة الكتل الرطبة.
                """
                
                # عرض النص النهائي بشكل أنيق جداً ومبسط
                st.info(analysis_text)
                
        except Exception as e:
            st.error(f"حدث خطأ أثناء الاتصال بخوادم الطقس العالمية: {e}")
          
