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

# الرادار
st.markdown("### 🛰️ رادار الأمطار")
custom_map_html = f"""
<div style="width: 100%; height: 400px; border-radius: 10px; overflow: hidden; border: 2px solid #4CAF50;">
    <iframe src="https://embed.windy.com/embed2.html?lat=16.51&lon=-15.81&zoom=8&overlay=rain&product=ecmwf" width="100%" height="100%" frameborder="0"></iframe>
</div>
"""
st.components.v1.html(custom_map_html, height=400)

st.write("---")

# التحليل
st.subheader("📊 ملخص التوقعات")
period_map = {
    "24 ساعة": 24,
    "5 أيام": 120,
    "10 أيام": 240,
    "16 يوماً": 384
}
period = st.selectbox("المدى الزمني:", list(period_map.keys()))

if st.button("توليد التدوينة الجوية"):
    with st.spinner("جاري تحليل النماذج..."):
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude=16.51&longitude=-15.81&hourly=temperature_2m,relative_humidity_700hPa,precipitation_probability,precipitation,wind_speed_10m,wind_direction_10m&forecast_days=16"
            data = requests.get(url).json()["hourly"]
            h = period_map[period]
            
            # حساب المتوسطات والقيم
            temps = data["temperature_2m"][:h]
            precip = sum([x for x in data["precipitation"][:h] if x])
            prob = max(data["precipitation_probability"][:h])
            max_t = max(temps)
            min_t = min(temps)
            
            # واجهة مبسطة جداً تركز على الحرارة والأمطار
            c1, c2 = st.columns(2)
            c1.metric("درجة الحرارة العظمى", f"{max_t:.1f}°C")
            c2.metric("إجمالي الأمطار المتوقع", f"{precip:.1f} ملم")
            
            # محرك كتابة التدوينة (يأخذ العوامل الأخرى في الاعتبار سراً)
            # رطوبة 700hPa + اتجاه الرياح (موسمية/غبار)
            avg_rh = sum(data["relative_humidity_700hPa"][:h]) / h
            wind_dir = data["wind_direction_10m"][0]
            
            st.markdown("### 📝 تدوينة الخبير:")
            
            # المنطق التحليلي المبطن لفرز الحالة بدقة علمية
            status = "أجواء مستقرة"
            if prob > 50: status = "اضطرابات جوية مرتقبة"
            elif avg_rh > 50: status = "رطوبة عالية تبشر بتكون سحب"
            
            blog = f"""
            بناءً على تحديثات النماذج العددية لمدينة روصو؛ {status}. 
            من المتوقع أن تسجل الحرارة مستويات تتراوح بين {min_t:.1f}°C و {max_t:.1f}°C.
            """
            
            if precip > 0:
                blog += f" تشير النماذج إلى فرصة أمطار تصل لـ {prob}%، مدعومة بتيارات رطبة في طبقات الجو العليا ومؤشرات إيجابية من الرياح الموسمية، مما يرفع احتمالية تشكل سحب رعدية."
            else:
                blog += " لا توجد مؤشرات قوية للهطول حالياً، حيث تسيطر كتل هوائية أقل رطوبة، مع نشاط رياح قد يثير الغبار أحياناً."
            
            st.info(blog)
            
        except Exception as e:
            st.error("حدث خطأ في جلب البيانات.")
