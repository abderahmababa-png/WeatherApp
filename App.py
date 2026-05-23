import streamlit as st
import requests
import os

st.set_page_config(page_title="طقس روصو Rosso weather", page_icon="🌤️", layout="centered")

# الشعار
LOGO_FILE = "1779505332712.jpg"
st.markdown("<style>.stImage img {border-radius: 50%; border: 3px solid #4CAF50; max-width: 150px; margin: 0 auto; display: block;}</style>", unsafe_allow_html=True)
if os.path.exists(LOGO_FILE): st.image(LOGO_FILE)

st.markdown("<h1 style='text-align: center;'>طقس روصو Rosso weather</h1>", unsafe_allow_html=True)
st.write("---")

# 1. قائمة تحديد الموقع الجغرافي (مقاطعات الترارزة)
st.markdown("### 📍 تحديد الموقع الجغرافي")
locations_map = {
    "روصو": {"lat": 16.51, "lon": -15.81},
    "اركيز": {"lat": 16.91, "lon": -15.28},
    "المذرذرة": {"lat": 16.92, "lon": -15.80},
    "بوتلميت": {"lat": 17.54, "lon": -14.77},
    "واد الناقة": {"lat": 17.98, "lon": -15.49},
    "كرمسين": {"lat": 16.49, "lon": -16.20},
    "تكنت": {"lat": 17.24, "lon": -16.14},
    "انجاكو": {"lat": 16.29, "lon": -16.45}
}

selected_city = st.selectbox("اختر النطاق المراد تحليله:", list(locations_map.keys()))
lat = locations_map[selected_city]["lat"]
lon = locations_map[selected_city]["lon"]

st.write("---")

# 2. رادار الأمطار التفاعلي الجديد (خريطة حرة وبدون شعارات تجارية)
st.markdown("### 🛰️ رادار الأمطار التفاعلي")
with st.expander("🗺️ اضغط هنا لفتح/إغلاق الخريطة الحية لرادار السحب والأمطار"):
    st.write(f"عرض الرادار المباشر لنطاق: **{selected_city}**")
    
    # خريطة رادار متطورة تعتمد على الرصد المفتوح لتجنب الشعارات الإجبارية
    custom_map_html = f"""
    <div style="width: 100%; height: 450px; border-radius: 10px; overflow: hidden; border: 2px solid #4CAF50; position: relative;">
        <iframe src="https://www.rainviewer.com/map.html?loc={lat},{lon},8&oRa=1&sm=1&sn=1&co=1&bl=1&hz=0&v=0&vcr=0&vt=1&re=1&cre=1&prm=1&tz=auto" width="100%" height="100%" frameborder="0" style="border:0;"></iframe>
        
        <!-- غطاء هوية التطبيق الاحترافي -->
        <div style="
            position: absolute; 
            bottom: 0; 
            left: 0; 
            background-color: #111111; 
            color: #4CAF50; 
            padding: 8px 15px; 
            font-family: Arial, sans-serif; 
            font-size: 14px; 
            font-weight: bold; 
            border-top-right-radius: 8px; 
            z-index: 99999;
            box-shadow: 2px -2px 5px rgba(0,0,0,0.4);
        ">
            🌤️ Rosso weather
        </div>
    </div>
    """
    st.components.v1.html(custom_map_html, height=450)

st.write("---")

# 3. قسم معالجة النماذج العددية وتوليد التدوينة
st.subheader("📊 ملخص التوقعات وتحليل المنظومة")
period_map = {
    "24 ساعة": 24,
    "5 أيام": 120,
    "10 أيام": 240,
    "16 يوماً": 384
}
period = st.selectbox("المدى الزمني:", list(period_map.keys()))

if st.button("توليد التدوينة الجوية"):
    with st.spinner(f"جاري معالجة خرائط {selected_city}..."):
        try:
            # جلب البيانات الحية بناءً على إحداثيات الموقع المختار
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_700hPa,precipitation_probability,precipitation,wind_speed_10m,wind_direction_10m&forecast_days=16"
            data = requests.get(url).json()["hourly"]
            h = period_map[period]
            
            # حساب المتوسطات والقيم المتغيرة
            temps = data["temperature_2m"][:h]
            precip = sum([x for x in data["precipitation"][:h] if x])
            prob = max(data["precipitation_probability"][:h])
            max_t = max(temps)
            min_t = min(temps)
            avg_rh = sum(data["relative_humidity_700hPa"][:h]) / h
            
            # واجهة نظيفة جداً تركز على الحرارة والأمطار
            c1, c2 = st.columns(2)
            c1.metric(f"العظمى في {selected_city}", f"{max_t:.1f}°C")
            c2.metric("إجمالي الأمطار المرتقب", f"{precip:.1f} ملم")
            
            st.markdown("### 📝 تدوينة الخبير الأرصادي:")
            
            # محرك صياغة تدوينة ذكي ومتغير كلياً حسب المدى الزمني
            if h == 24:
                time_context = "خلال الأربع وعشرين ساعة القادمة"
                trend_context = f"تستقر قراءات الحرارة اللحظية لتسجل عظمى تلامس {max_t:.1f}°C مع أجواء تميل للاعتدال النسبي خلال ساعات الفجر عند {min_t:.1f}°C."
            else:
                time_context = f"خلال الفترة الممتدة للمدى المتوسط ({period})"
                trend_context = f"تشير حركة المحاكاة لتذبذب حراري مستمر، حيث تبلغ ذروة الاحترار {max_t:.1f}°C، بينما تنخفض الصغرى في فترات التبريد الإشعاعي الليلي لتلامس {min_t:.1f}°C."

            # فرز رطوبة طبقات الجو العليا والرياح الموسمية في الخلفية
            if avg_rh > 45:
                moisture_influence = "مع رصد تدفقات ممتازة للرطوبة البنائية الجوية في الطبقات البنائية (700hPa) ممهدة لتكاثف حملي محلي."
            else:
                moisture_influence = "برغم سيطرة كتل هوائية جافة نسبياً في طبقات الجو المتوسطة تحد من الامتداد الشاقولي للسحب."

            # دمج مخرجات المطر في صياغة فصيحة ومتكاملة
            if precip > 0:
                blog = f"""
                توضح تحديثات النماذج العددية لنطاق **{selected_city}** {time_context} مؤشرات على اضطرابات جوية محتملة. {trend_context}
                
                {moisture_influence} وبناءً عليه، تضع النماذج فرصة هطول مطري تصل ذروة احتماليتها إلى **{prob}%**، بتراكم إجمالي مرتقب يبلغ **{precip:.1f} ملم**، مما يعزز من فرص نشوء سحب ركامية رعدية على فترات.
                """
            else:
                blog = f"""
                تُشير التنبؤات الجوية لنطاق **{selected_city}** {time_context} إلى سيطرة أجواء مستقرة بوجه عام. {trend_context}
                
                {moisture_influence} وبالتالي تبقى فرص الهطول الفعلي منعدمة عند **0.0 ملم** مع تراجع احتمالية الأمطار لـ **{prob}%**، مع نشاط معتدل للرياح السطحية قد يثير بعض الأتربة العالقة في المناطق المكشوفة.
                """
            
            st.info(blog)
            
        except Exception as e:
            st.error("حدث خطأ أثناء معالجة بيانات النموذج الرقمي.")
