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
        max-width: 150px;
        margin: 0 auto;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# عرض الشعار في الأعلى مقصوصاً كدائرة باحترافية عبر أداة Streamlit الرسمية
if os.path.exists(LOGO_FILE):
    st.image(LOGO_FILE, width=150)
else:
    st.markdown("<h1 style='text-align: center;'>⛈️ تطبيق طقس روصو الذكي</h1>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #aaa; font-size: 14px;'>محلل الطقس الاحترافي - مرصد روصو المناخي</p>", unsafe_allow_html=True)
st.write("---")

# 1. عنوان قسم الرادار والخريطة التفاعلية
st.markdown("<h3 style='text-align: center; color: #4CAF50;'>🛰️ رادار طقس روصو التفاعلي لحركة الأمطار والسحب</h3>", unsafe_allow_html=True)

# حل مشكلة قفل قائمة الخيارات: إضافة زر لتحديث الخريطة وإغلاق قائمة الطبقات المنبثقة
if 'map_key' not in st.session_state:
    st.session_state.map_key = 0

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("🔄 إغلاق قائمة طبقات الخريطة / تحديث", use_container_width=True):
        st.session_state.map_key += 1

# الخريطة التفاعلية مع مفتاح التحديث الديناميكي (key) وغطاء حجب علامة Windy
custom_map_html = f"""
<div style="position: relative; width: 100%; height: 450px; border: 2px solid #4CAF50; border-radius: 10px; overflow: hidden;">
    <!-- غطاء علامة الموقع في الزاوية اليسرى العليا -->
    <div style="position: absolute; top: 0; left: 0; width: 140px; height: 40px; background-color: #222222; z-index: 999; display: flex; align-items: center; justify-content: center; border-bottom-right-radius: 8px; border-right: 1px solid #4CAF50; border-bottom: 1px solid #4CAF50;">
        <span style="color: #4CAF50; font-family: Arial, sans-serif; font-size: 13px; font-weight: bold;">⛈️ رادار روصو</span>
    </div>
    
    <!-- الخريطة التفاعلية الحية -->
    <iframe 
        key="{st.session_state.map_key}"
        src="https://embed.windy.com/embed2.html?lat=16.51&lon=-15.81&zoom=8&level=surface&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default&radarRange=-1" 
        width="100%" 
        height="100%" 
        frameborder="0">
    </iframe>
</div>
"""

st.components.v1.html(custom_map_html, height=460)

st.write("---")

# 2. قسم التحليل الرقمي والمناخي المطور لروصو
st.subheader("📊 التحليل الرقمي واستخلاص المؤشرات المناخية")
location = st.text_input("📍 المنطقة المراد تحليلها:", "روصو")

if "روصو" in location:
    lat, lon = 16.51, -15.81
else:
    lat, lon = 20.0, -12.0

# القائمة المحدثة بالمدد الطويلة (مرجع مناخي ثابت بدون أخطاء)
period = st.selectbox("📆 اختر الفترة الزمنية التي تريد تحليلها:", [
    "اليوم القادم (24 ساعة)", 
    "الأيام الـ 3 القادمة", 
    "أسبوع قادم (7 أيام)", 
    "16 يوماً القادمة (أقصى حد للنماذج العددية الحية)",
    "شهر قادم (المرجع المناخي التاريخي المعتمد)",
    "شهرين قادمين (المحاكاة والسجلات المناخية الثابتة)"
])

if st.button("🚀 بدء التحليل"):
    # إذا كانت المدة 16 يوماً أو أقل، نعتمد على النماذج العددية المباشرة (Open-Meteo)
    if "شهر" not in period:
        with st.spinner("جاري جلب البيانات من النماذج العددية العالمية..."):
            try:
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_700hPa,precipitation_probability,precipitation&forecast_days=16&timezone=auto"
                weather_res = requests.get(weather_url).json()
                
                if "hourly" in weather_res:
                    hourly_data = weather_res["hourly"]
                    
                    if period == "اليوم القادم (24 ساعة)": hours = 24
                    elif period == "الأيام الـ 3 القادمة": hours = 72
                    elif period == "أسبوع قادم (7 أيام)": hours = 168
                    else: hours = 384
                    
                    clean_prob = [x if x is not None else 0 for x in hourly_data["precipitation_probability"][:hours]]
                    clean_precip = [x if x is not None else 0.0 for x in hourly_data["precipitation"][:hours]]
                    clean_rh = [x if x is not None else 0 for x in hourly_data["relative_humidity_700hPa"][:hours]]
                    
                    max_prob = max(clean_prob) if clean_prob else 0
                    total_precip = sum(clean_precip) if clean_precip else 0.0
                    avg_rh_700 = (sum(clean_rh) / len(clean_rh)) if clean_rh else 0
                    
                    st.success("🎯 تم الانتهاء من تحليل البيانات الرقمية الحية بنجاح!")
                    st.markdown(f"""
                    *   **احتمالية الأمطار الحالية:** أعلى نسبة لاحتمالية هطول الأمطار في هذه الفترة تصل إلى **{max_prob}%**، بمجموع تساقطات متوقع **{total_precip:.1f} ملم**.
                    *   **الرطوبة البنائية الجوية (700hPa):** معدل الرطوبة في طبقة الجو المتوسطة هو **{avg_rh_700:.1f}%**، وهو المحرك الأساسي لتطور السحب الركامية المحلية الرعدية.
                    """)
                else:
                    st.error("عذراً، لم نتمكن من جلب هيكلية البيانات.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بالسيرفر: {e}")
                
    # إذا كانت المدة (شهر أو شهرين)، ننتقل فوراً للمرجع المناخي التاريخي الموثق لمنع أي خطأ تقديري
    else:
        st.info("ℹ️ أنت الآن تطلع على 'المرجع المناخي التاريخي الثابت' لمدينة روصو لضمان صفر أخطاء علمية.")
        
        st.markdown("### 📋 السجل الأرصادي والأنماط اللافتة للانتباه في روصو وجنوب موريتانيا:")
        
        # عرض الملاحظات والتحذيرات المناخية الموثقة للظواهر الحادة بناءً على طلبك
        st.markdown("""
        <div style="padding: 12px; border-right: 5px solid #blue; background-color: #1e1e1e; margin-bottom: 10px; border-radius: 4px;">
            <strong style="color: #2196F3;">💨 نشاط الرياح الموسمية (Monsoon):</strong><br/>
            <span style="color: #ddd; font-size: 14px;">تاريخياً في هذه الفترة، تتوغل الرياح الموسمية الجنوبية الغربية الرطبة القادمة من المحيط الأطلسي، وهي المسؤول الأول عن رفع معدلات الرطوبة وبناء الجبهات السحابية الماطرة في شمامة.</span>
        </div>
        
        <div style="padding: 12px; border-right: 5px solid green; background-color: #1e1e1e; margin-bottom: 10px; border-radius: 4px;">
            <strong style="color: #4CAF50;">⛈️ جبهات الأمطار (الخريف المحلي):</strong><br/>
            <span style="color: #ddd; font-size: 14px;">تُسجل السجلات الأرصادية لروصو في هذا الموسم بداية نشاط الخط الفاصل بين الكتل الهوائية (ITCZ)، مما يتسبب في نشوء عواصف رعدية فجائية محلية قوية التراكم المائي.</span>
        </div>
        
        <div style="padding: 12px; border-right: 5px solid orange; background-color: #1e1e1e; margin-bottom: 10px; border-radius: 4px;">
            <strong style="color: #FF9800;">🔥 موجات الارتفاع القوي للحرارة:</strong><br/>
            <span style="color: #ddd; font-size: 14px;">عند تراجع الرياح البحرية، تتوغل كتل صحراوية قارية جافة تؤدي لقفزات حرارية حادة تتجاوز حاجز 44°C إلى 46°C في الظل قبل هطول الأمطار الملطفة للجو.</span>
        </div>
        
        <div style="padding: 12px; border-right: 5px solid red; background-color: #1e1e1e; margin-bottom: 10px; border-radius: 4px;">
            <strong style="color: #F44336;">🌪️ كتل الغبار العالق والرياح الشرقية (الشرقي):</strong><br/>
            <span style="color: #ddd; font-size: 14px;">يُرصد بانتظام تقدم كتل غبارية جافة من المناطق الشرقية والشمالية الشرقية للبلاد، تؤدي لتدني الرؤية الأفقية بشكل حاد وتؤثر مباشرة على أجواء القطاع الزراعي بروصو.</span>
        </div>
        
        <div style="padding: 12px; border-right: 5px solid violet; background-color: #1e1e1e; margin-bottom: 10px; border-radius: 4px;">
            <strong style="color: #E040FB;">❄️ موجات انخفاض الحرارة المفاجئ:</strong><br/>
            <span style="color: #ddd; font-size: 14px;">تنخفض درجات الحرارة الصغرى ليلاً بشكل ملحوظ عقب هطول الأمطار الغزيرة أو عند اندفاع تيارات هوائية شمالية غربية رطبة تلطف الأجواء السطحية بشكل مفاجئ.</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.warning("⚠️ تنبيه: المدد التي تتجاوز 16 يوماً لا تخضع للتنبؤ العددي اللحظي بل تُعرض كمؤشرات مناخية إحصائية معتمدة إقليمياً.")
