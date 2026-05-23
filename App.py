import streamlit as st
import requests
import os
import streamlit.components.v1 as components

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

# 2. رادار الأمطار النظيف كلياً بتقنية القص الرقمي لمنع ظهور أي شعارات أو مساحات بيضاء
st.markdown("### 🛰️ رادار الأمطار التفاعلي")
with st.expander("🗺️ اضغط هنا لفتح/إغلاق الخريطة الحية لرادار السحب والأمطار"):
    st.write(f"عرض الرادار المباشر لنطاق: **{selected_city}**")
    
    # استخدام حاوية بـ overflow مخفي وقص أطراف الـ iframe للتخلص من شريط الألوان العلوي وشعار Windy والقائمة البيضاء
    custom_map_html = f"""
    <div style="width: 100%; height: 400px; border-radius: 10px; overflow: hidden; border: 2px solid #4CAF50; position: relative; background-color: #1a1a1a;">
        <div style="width: 100%; height: 100%; top: -45px; position: absolute;">
            <iframe src="https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&zoom=9&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=true&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default&v={selected_city}" 
                    width="100%" 
                    height="490px" 
                    frameborder="0" 
                    style="border:0; clip-path: inset(45px 0px 45px 0px);">
            </iframe>
        </div>
        
        <!-- ملصق هوية تطبيقك الثابت والأنيق في أعلى اليمين بشكل مستقل -->
        <div style="
            position: absolute; 
            top: 10px; 
            right: 10px; 
            background-color: rgba(26, 26, 26, 0.85); 
            color: #4CAF50; 
            padding: 5px 12px; 
            font-family: Arial, sans-serif; 
            font-size: 12px; 
            font-weight: bold; 
            border-radius: 5px; 
            z-index: 999999;
            direction: rtl;
        ">
            🌤️ رادار طقس روصو
        </div>
    </div>
    """
    components.html(custom_map_html, height=400)

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
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_700hPa,precipitation_probability,precipitation,wind_speed_10m,wind_direction_10m&forecast_days=16"
            data = requests.get(url).json()["hourly"]
            h = period_map[period]
            
            temps = data["temperature_2m"][:h]
            precip = sum([x for x in data["precipitation"][:h] if x])
            prob = max(data["precipitation_probability"][:h])
            max_t = max(temps)
            min_t = min(temps)
            avg_rh = sum(data["relative_humidity_700hPa"][:h]) / h
            
            c1, c2 = st.columns(2)
            c1.metric(f"العظمى في {selected_city}", f"{max_t:.1f}°C")
            c2.metric("إجمالي الأمطار المرتقب", f"{precip:.1f} ملم")
            
            st.markdown("### 📝 تدوينة الخبير الأرصادي:")
            
            if h == 24:
                time_context = "خلال الأربع وعشرين ساعة القادمة"
                trend_context = f"تستقر قراءات الحرارة اللحظية لتسجل عظمى تلامس {max_t:.1f}°C مع أجواء تميل للاعتدال النسبي خلال ساعات الفجر عند {min_t:.1f}°C."
            else:
                time_context = f"خلال الفترة الممتدة للمدى المتوسط ({period})"
                trend_context = f"تشير حركة المحاكاة لتذبذب حراري مستمر، حيث تبلغ ذروة الاحترار {max_t:.1f}°C، بينما تنخفض الصغرى في فترات التبريد الإشعاعي الليلي لتلامس {min_t:.1f}°C."

            if avg_rh > 45:
                moisture_influence = "مع رصد تدفقات ممتازة للرطوبة البنائية الجوية في الطبقات البنائية (700hPa) ممهدة لتكاثف حملي محلي."
            else:
                moisture_influence = "برغم سيطرة كتل هوائية جافة نسبياً في طبقات الجو المتوسطة تحد من الامتداد الشاقولي للسحب."

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
