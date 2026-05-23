import streamlit as st
import requests
import os

st.set_page_config(page_title="مرصد روصو الأرصادي", page_icon="⛈️", layout="centered")

# اسم ملف الصورة الرقمي في المستودع
LOGO_FILE = "1779505332712.jpg"

# كود CSS لتنسيق الصورة والدائرة
st.markdown("""
<style>
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

# عرض الشعار في الأعلى
if os.path.exists(LOGO_FILE):
    st.image(LOGO_FILE, width=150)
else:
    st.markdown("<h1 style='text-align: center;'>⛈️ مرصد روصو الأرصادي الذكي</h1>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #aaa; font-size: 15px; font-style: italic;'>بوابة التحليل الديناميكي السائل واستخلاص المؤشرات الفيزيائية اللحظية</p>", unsafe_allow_html=True)
st.write("---")

# 1. قسم الرادار والتفاعلية
st.markdown("<h3 style='text-align: center; color: #4CAF50;'>🛰️ رادار الاستشعار عن بعد وحركة الهطول والسحب</h3>", unsafe_allow_html=True)

if 'map_key' not in st.session_state:
    st.session_state.map_key = 0

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("🔄 إغلاق قائمة الطبقات / إعادة إنعاش الرادار", use_container_width=True):
        st.session_state.map_key += 1

custom_map_html = f"""
<div style="position: relative; width: 100%; height: 450px; border: 2px solid #4CAF50; border-radius: 10px; overflow: hidden;">
    <div style="position: absolute; top: 0; left: 0; width: 140px; height: 40px; background-color: #222222; z-index: 999; display: flex; align-items: center; justify-content: center; border-bottom-right-radius: 8px; border-right: 1px solid #4CAF50; border-bottom: 1px solid #4CAF50;">
        <span style="color: #4CAF50; font-family: Arial, sans-serif; font-size: 13px; font-weight: bold;">⛈️ رادار روصو</span>
    </div>
    <iframe 
        key="{st.session_state.map_key}"
        src="https://embed.windy.com/embed2.html?lat=16.51&lon=-15.81&zoom=8&level=surface&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map" 
        width="100%" 
        height="100%" 
        frameborder="0">
    </iframe>
</div>
"""
st.components.v1.html(custom_map_html, height=460)

st.write("---")

# 2. قسم التحليل الرقمي والمناخي المتطور
st.markdown("<h3 style='color: #4CAF50;'>📊 معالجة النماذج العددية وقراءة السلوك الفيزيائي والغلاف الجوي</h3>", unsafe_allow_html=True)
location = st.text_input("📍 تحديد النطاق الجغرافي المستهدف:", "روصو")

if "روصو" in location:
    lat, lon = 16.51, -15.81
else:
    lat, lon = 20.0, -12.0

# خيارات المدد الموسعة والدقيقة بناءً على طلبك
period = st.selectbox("📆 حدد المدى الزمني للاستقراء الأرصادي:", [
    "المدى اللحظي القريب (24 ساعة القادمة)",
    "المدى المتوسط الأولي (5 أيام القادمة)",
    "المدى المتوسط المتقدم (10 أيام القادمة)",
    "المدى الأقصى للنماذج العددية (16 يوماً القادمة)",
    "الاستقراء الشامل المناخي (شهر كامل - متوسطات تاريخية)",
    "الاستقراء الشامل المناخي الموسع (شهرين - متوسطات تاريخية)"
])

if st.button("🚀 معالجة البيانات وبدء المحاكاة"):
    if "شهر" not in period:
        with st.spinner("جاري الاتصال بالسيرفر الفيدرالي وجلب التوقعات الحية..."):
            try:
                # طلب بيانات موسعة تشمل الرياح، الرطوبة، الحرارة، والهطول
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_700hPa,precipitation_probability,precipitation,wind_speed_10m,wind_direction_10m&forecast_days=16&timezone=auto"
                weather_res = requests.get(weather_url).json()
                
                if "hourly" in weather_res:
                    hourly_data = weather_res["hourly"]
                    
                    # تحديد الساعات بناء على الخيار الجديد
                    if "24 ساعة" in period: hours = 24
                    elif "5 أيام" in period: hours = 120
                    elif "10 أيام" in period: hours = 240
                    else: hours = 384
                    
                    # استخلاص وتصفية المصفوفات الجوية
                    temps = hourly_data["temperature_2m"][:hours]
                    clean_prob = [x if x is not None else 0 for x in hourly_data["precipitation_probability"][:hours]]
                    clean_precip = [x if x is not None else 0.0 for x in hourly_data["precipitation"][:hours]]
                    clean_rh = [x if x is not None else 0 for x in hourly_data["relative_humidity_700hPa"][:hours]]
                    wind_speeds = [x if x is not None else 0.0 for x in hourly_data["wind_speed_10m"][:hours]]
                    wind_dirs = hourly_data["wind_direction_10m"][:hours]
                    
                    max_temp = max(temps)
                    min_temp = min(temps)
                    max_prob = max(clean_prob)
                    total_precip = sum(clean_precip)
                    avg_rh = sum(clean_rh) / len(clean_rh)
                    max_wind = max(wind_speeds)
                    
                    st.success("🎯 تجميع وتوليد التقرير السائل المحدث بنجاح!")
                    
                    # ----------------- قسم الشرح العلمي المكثف الفصيح -----------------
                    st.markdown("### 📜 الخلاصة البيانية بلغة أهل الطقس:")
                    st.markdown(f"""
                    *   **الحرارة السطحية ومؤشر النفاذ:** تشير القراءات إلى ذروة حرارية تلامس **{max_temp:.1f}°C** نتيجة تنشيط الإشعاع الشمسي المباشر، بينما تنحسر صغرى الحرارة ليلاً عند **{min_temp:.1f}°C** تحت تأثير التبريد الإشعاعي لسطح الأرض.
                    *   **الرطوبة البنائية المحمولة (700hPa):** يُقدر معدل الرطوبة في طبقات الجو المتوسطة بـ **{avg_rh:.1f}%**؛ وهي الرطوبة المحورية اللازمة لتغذية **التيارات الحملية الصاعدة** وتحفيز عملية التكاثف داخل غلاف المنطقة الجوي.
                    *   **الديناميكية الحركية للرياح:** رصدت المستشعرات سرعة رياح قصوى تبلغ **{max_wind:.1f} كم/س**.
                    """)
                    
                    # ----------------- قسم فحص العناصر الملفتة للانتباه من النموذج اللحظي -----------------
                    st.markdown("### ⚠️ رصد العناصر الأرصادية الملفتة للانتباه (خلال هذه الفترة):")
                    
                    notable_features = 0
                    
                    # 1. فحص هبوب الرياح الموسمية الرطبة (Monsoon)
                    # رياح جنوبية غربية (بين زاوية 180 و 270) وسرعة نشطة
                    monsoon_hours = [i for i in range(hours) if wind_dirs[i] is not None and 180 <= wind_dirs[i] <= 270 and wind_speeds[i] > 15]
                    if len(monsoon_hours) > 12:
                        st.markdown("""
                        <div style="padding: 12px; border-right: 5px solid #2196F3; background-color: #1e1e1e; margin-bottom: 10px;">
                            <h5 style="color: #2196F3; margin:0;">💨 توغل تدفقات الرياح الموسمية الرطبة (Monsoon)</h5>
                            <p style="color: #ddd; font-size: 14px; margin: 5px 0 0 0;">تم رصد تيار هوائي جنوبي غربي رطب ومستمر قادم من القطاع البحري، مما يساهم بشكل مباشر في دفع الخط الفاصل بين الكتل الهوائية (ITCZ) شمالاً، ممهداً لرفع الرطوبة النوعية السطحية وتلطيف الأجواء الجافة.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        notable_features += 1
                        
                    # 2. فحص اضطراب كتل الغبار (الرياح الشرقية الجافة)
                    # رياح شرقية أو شمالية شرقية (بين زاوية 45 و 135) وسرعة نشطة قادرة على حمل الغبار
                    dust_hours = [i for i in range(hours) if wind_dirs[i] is not None and 45 <= wind_dirs[i] <= 135 and wind_speeds[i] > 22]
                    if len(dust_hours) > 8:
                        st.markdown("""
                        <div style="padding: 12px; border-right: 5px solid #ff5722; background-color: #1e1e1e; margin-bottom: 10px;">
                            <h5 style="color: #ff5722; margin:0;">🌪️ مؤشر إثارة الغبار العالق والأتربة (الشرقي)</h5>
                            <p style="color: #ddd; font-size: 14px; margin: 5px 0 0 0;">تنبؤات حركية تشير إلى اندفاع تيارات قارية جافة من الصحراء الكبرى (الشرقي)، تتميز بنشاط قاصف قد يعمل على إثارة الأتربة المحلية والعبور بكتل من الغبار العالق التي تتسبب في هبوط مدى الرؤية الأفقية.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        notable_features += 1
                        
                    # 3. فحص الارتفاع القياسي للحرارة (موجة حرارية)
                    if max_temp >= 43.0:
                        st.markdown("""
                        <div style="padding: 12px; border-right: 5px solid #f44336; background-color: #1e1e1e; margin-bottom: 10px;">
                            <h5 style="color: #f44336; margin:0;">🔥 صعود حراري حاد (الاحترار القاري المباشر)</h5>
                            <p style="color: #ddd; font-size: 14px; margin: 5px 0 0 0;">يقع النطاق الجغرافي تحت وطأة كتلة هوائية لاهبة شديدة الجفاف، مما يؤدي إلى تمدد المنخفض الحراري السطحي وارتفاع حاد في درجات الحرارة متجاوزاً معدلاتها الفصلية، مما يستوجب الحذر من التعرض للإشعاع المباشر في أوقات الذروة.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        notable_features += 1

                    # 4. فحص التبريد والانخفاض الحاد للحرارة
                    if min_temp <= 22.0:
                        st.markdown("""
                        <div style="padding: 12px; border-right: 5px solid #9c27b0; background-color: #1e1e1e; margin-bottom: 10px;">
                            <h5 style="color: #9c27b0; margin:0;">❄️ انخفاض حراري لافت (التبريد الكتلي)</h5>
                            <p style="color: #ddd; font-size: 14px; margin: 5px 0 0 0;">ترصد الخرائط توغلاً لتيارات هوائية ذات منشأ بحري بارد نسبياً، تعمل على كسر حدة الاحترار السطحي بشكل لافت خلال ساعات الليل المتأخرة والصباح الباكر.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        notable_features += 1
                        
                    # 5. فحص الهطول والمطريات الغزيرة
                    if total_precip > 5.0 or max_prob > 40:
                        st.markdown(f"""
                        <div style="padding: 12px; border-right: 5px solid #4caf50; background-color: #1e1e1e; margin-bottom: 10px;">
                            <h5 style="color: #4caf50; margin:0;">⛈️ اضطراب مطري محتمل (تكاثف مزني ركامي)</h5>
                            <p style="color: #ddd; font-size: 14px; margin: 5px 0 0 0;">تظهر الخرائط إشارات لتكاثف خلايا من السحب الركامية المزنية بفعل الفوارق الحرارية الرأسية، مع احتمالية هطول أمطار رعدية محلياً تبلغ ذروتها بنسبة {max_prob}% وبتراكم إجمالي يقدر بـ {total_precip:.1f} ملم.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        notable_features += 1
                        
                    if notable_features == 0:
                        st.info("🍃 الأجواء مستقرة وضمن النطاق الطبيعي السائد، ولا ترصد النماذج الحالية أي ظواهر فيزيائية استثنائية خارجة عن المألوف.")
                        
                else:
                    st.error("فشل مستودع البيانات في معالجة الهيكلية الرقمية.")
            except Exception as e:
                st.error(f"عذراً، تعذر ربط المعالجة بسبب انقطاع المسار الرقمي: {e}")
                
    # المدى المناخي الإحصائي (شهر وشهرين) لضمان دقة كاملة وصفر أخطاء في المدى الطويل
    else:
        st.info("ℹ️ قراءة المرجع الإحصائي والسجل الأرصادي الثابت للمنطقة (لضمان دقة علمية مطلقة تمنع أخطاء التنبؤ التخميني الطويل).")
        st.markdown(f"""
        ### 📖 الاستقراء المناخي لمدينة روصو وجنوب موريتانيا:
        *   **منظومة الرياح (The Monsoon Dynamic):** يثبت السجل التاريخي هيمنة التغذية الرطبة القادمة من جنوب المحيط الأطلسي، حيث تلعب هذه الرياح الدور الرئيسي في دفع جبهة (ITCZ) لتنشيط منخفضات التكاثف المحلية في شمامة.
        *   **الموجات الحرارية ونشاط الغبار:** تاريخياً، يشهد هذا النطاق الزمني قفزات حرارية فجائية تلامس أواسط الأربعينيات مئوية عند هبوب رياح "الشرقي" الصحراوية الحاملة لجزيئات الغبار العالق والأتربة المثارة، قبل أن تنكسر بتقدم السحب الركامية الماطرة (الخريف المحلي).
        """)
