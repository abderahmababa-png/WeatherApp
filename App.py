import streamlit as st
import requests
import os
import streamlit.components.v1 as components
import urllib.parse

# كود يمنع تداخل اللمس والسحب وضبط الهوية البصرية الزرقاء المتناسقة مع الشعار
st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        overscroll-behavior-y: contain !important;
        touch-action: pan-x pan-y !important;
    }
    /* جعل أزرار التحكم متناسقة مع اللون الأزرق للشعار */
    .stButton>button {
        background-color: #1E88E5 !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
    }
    iframe {
        pointer-events: auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="طقس روصو Rosso weather", page_icon="🌤️", layout="centered")

# الشعار (دائري مع إطار أزرق متناسق)
LOGO_FILE = "1779505332712.jpg"
st.markdown("<style>.stImage img {border-radius: 50%; border: 3px solid #1E88E5; max-width: 140px; margin: 0 auto; display: block;}</style>", unsafe_allow_html=True)
if os.path.exists(LOGO_FILE): 
    st.image(LOGO_FILE)

# عنوان منسق ومناسب تماماً على سطر واحد
st.markdown("<h2 style='text-align: center; color: #1E88E5; font-family: Arial; font-size: 24px; direction: rtl; margin-top: 10px;'>طقس روصو | Rosso weather</h2>", unsafe_allow_html=True)
st.write("---")

# 1. قسم تحديد الموقع والمدى الزمني
st.markdown("### 📍 الإعدادات الجغرافية والزمنية")
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

col_city, col_time = st.columns(2)
with col_city:
    selected_city = st.selectbox("اختر المقاطعة:", list(locations_map.keys()))
with col_time:
    period_map = {"24 ساعة": 24, "5 أيام": 120, "10 أيام": 240, "16 يوماً": 384}
    period = st.selectbox("المدى الزمني للتحليل:", list(period_map.keys()))

lat = locations_map[selected_city]["lat"]
lon = locations_map[selected_city]["lon"]

# التحكم في الخريطة بشكل جانبي وصغير
st.write("")
col_btn, col_empty = st.columns([1, 2])
with col_btn:
    show_radar = st.checkbox("🛰️ رادار الأمطار الحية", value=False)

# عرض الرادار النظيف والمحمي من مشاكل التحريك العشوائي برابط أزرق متناسق
if show_radar:
    st.markdown(f"<p style='color:#1E88E5; font-weight:bold; margin-bottom:5px;'>🗺️ رادار الأمطار الحية (النموذج الأوروبي ECMWF) - نطاق {selected_city}</p>", unsafe_allow_html=True)
    
    custom_map_html = f"""
    <div style="width: 100%; height: 380px; border-radius: 10px; overflow: hidden; border: 2px solid #1E88E5; position: relative; background-color: #1a1a1a; touch-action: auto;">
        <div style="width: 100%; height: 100%; top: -45px; position: absolute;">
            <iframe src="https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&zoom=8&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=true&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default" 
                    width="100%" 
                    height="470px" 
                    frameborder="0" 
                    style="border:0; clip-path: inset(45px 0px 45px 0px); pointer-events: auto;">
            </iframe>
        </div>
        <div style="position: absolute; top: 10px; right: 10px; background-color: rgba(26, 26, 26, 0.9); color: #1E88E5; padding: 6px 14px; font-family: Arial; font-size: 12px; font-weight: bold; border-radius: 5px; z-index: 9999; direction: rtl; border: 1px solid #1E88E5;">
            🛰️ التوقع الأوروبي الحـي
        </div>
    </div>
    """
    components.html(custom_map_html, height=390)

st.write("---")

# 2. زر معالجة البيانات وتوليد النتائج والمرئيات
if st.button("📊 توليد وتحليل التدوينة الجوية", use_container_width=True):
    with st.spinner(f"جاري معالجة خرائط ونماذج {selected_city}..."):
        try:
            h = period_map[period]
            # اختيار الخادم المناسب بناءً على المدة الزمنية المطلوبة
            if h > 120:
                url = f"https://api.open-meteo.com/v1/gfs?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_700hPa,precipitation_probability,precipitation,wind_speed_10m,wind_direction_10m&forecast_days=16"
            else:
                url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_700hPa,precipitation_probability,precipitation,wind_speed_10m,wind_direction_10m&forecast_days=7"
                
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()["hourly"]
                
                # تحديد عدد الساعات المتاحة فعلياً لتجنب خطأ أبعاد المصفوفة
                actual_h = min(h, len(data["temperature_2m"]))
                
                # معالجة وتنظيف البيانات من أي قيم فارغة (NoneType) لقطع دابر الخطأ تماماً
                raw_temps = data.get("temperature_2m", [])[:actual_h]
                temps = [float(x) if x is not None else 0.0 for x in raw_temps]
                
                raw_precip = data.get("precipitation", [])[:actual_h]
                precip_list = [float(x) if x is not None else 0.0 for x in raw_precip]
                precip = sum(precip_list)
                
                raw_prob = data.get("precipitation_probability", [])[:actual_h]
                prob_list = [int(x) if x is not None else 0 for x in raw_prob]
                prob = max(prob_list) if prob_list else 0
                
                raw_rh = data.get("relative_humidity_700hPa", [])[:actual_h]
                rh_list = [float(x) if x is not None else 0.0 for x in raw_rh]
                avg_rh = sum(rh_list) / len(rh_list) if rh_list else 0
                
                raw_wind = data.get("wind_speed_10m", [])[:actual_h]
                wind_list = [float(x) if x is not None else 0.0 for x in raw_wind]
                max_wind = max(wind_list) if wind_list else 0
                
                max_t = max(temps) if temps else 0.0
                min_t = min(temps) if temps else 0.0
                
                # عرض المؤشرات الأساسية
                c1, c2 = st.columns(2)
                c1.metric(f"🌡️ العظمى المتوقعة ({selected_city})", f"{max_t:.1f}°C")
                c2.metric("🌧️ إجمالي الأمطار المرتقب", f"{precip:.1f} ملم")
                
                st.write("")
                
                # 🔘 أولاً: تدوينة الخبير الأرصادي
                st.markdown(f"### 📝 تدوينة الخبير الأرصادي لـ ({selected_city}):")
                
                if h == 24:
                    time_context = "خلال الأربع وعشرين ساعة القادمة"
                    trend_context = f"تستقر قراءات الحرارة اللحظية لتسجل عظمى تلامس {max_t:.1f}°C مع أجواء تميل للاعتدال النسبي خلال ساعات الفجر عند {min_t:.1f}°C."
                else:
                    time_context = f"خلال الفترة الممتدة للمدى المتوسط والبعيد ({period})"
                    trend_context = f"تشير حركة المحاكاة لتذبذب حراري مستمر، حيث تبلغ ذروة الاحترار {max_t:.1f}°C، بينما تنخفض الصغرى في فترات التبريد الإشعاعي الليلي لتلامس {min_t:.1f}°C."

                if avg_rh > 45:
                    moisture_influence = "مع رصد تدفقات ممتازة للرطوبة الجوية في الطبقات البنائية المتوسطة (700hPa) ممهدة لتكاثف حملي محلي."
                else:
                    moisture_influence = "برغم سيطرة كتل هوائية جافة نسبياً في طبقات الجو المتوسطة تحد من الامتداد الشاقولي للسحب السريعة."

                if precip > 0:
                    blog = f"""توضح تحديثات النماذج العددية لنطاق **{selected_city}** {time_context} مؤشرات على اضطرابات جوية محتملة. {trend_context}
                    
{moisture_influence} وبناءً عليه، تضع النماذج فرصة هطول مطري تصل ذروة احتماليتها إلى **{prob}%**، بتراكم إجمالي مرتقب يبلغ **{precip:.1f} ملم**، مما يعزز من فرص نشوء سحب ركامية رعدية على فترات."""
                else:
                    blog = f"""تُشير التنبؤات الجوية لنطاق **{selected_city}** {time_context} إلى سيطرة أجواء مستقرة بوجه عام. {trend_context}
                    
{moisture_influence} وبالتالي تبقى فرص الهطول الفعلي منعدمة عند **0.0 ملم** مع تراجع احتمالية الأمطار لـ **{prob}%**، مع نشاط معتدل للرياح السطحية قد يثير بعض الأتربة العالقة في المناطق المكشوفة."""
                
                st.info(blog)
                
                # 🔘 ثانياً: الإرشادات والنصائح الذكية
                st.markdown("### 💡 الإرشادات والنصائح اليومية:")
                if precip > 2:
                    st.warning("⚠️ **تنبيه الخريف والأمطار:** يُتوقع هطول أمطار معتبرة. يرجى من السائقين توخي الحذر من المستنقعات على محاور الطرق، وللمزارعين أخذ الاحتياطات اللازمة.")
                elif max_wind > 25:
                    st.info("💨 **تنبيه نشاط الرياح:** الرياح السطحية نشطة وقد تثير الأتربة؛ يُنصح بحماية محركات السيارات وإغلاق النوافذ لمنع دخول الغبار العالق.")
                elif max_t > 38:
                    st.error("☀️ **تنبيه موجة حر:** الأجواء شديدة الحرارة؛ يرجى تجنب التعرض المباشر لأشعة الشمس في أوقات الذروة والإكثار من شرب السوائل.")
                else:
                    st.success("🌱 **أجواء مستقرة:** الطقس معتدل ومستقر بوجه عام ومناسب للأنشطة الخارجية المختلفة.")
                
                # 🔘 ثالثاً: زر مشاركة الطقس في الأسفل
                st.write("---")
                share_text = f"🌤️ طقس {selected_city} اليوم:\n- الحرارة العظمى: {max_t:.1f}°C\n- الأمطار: {precip:.1f} ملم\n\n👇 لمتابعة رادار السحب والأمطار في موريتانيا، حمل تطبيقنا برابط مباشر APK من هنا:\nhttps://github.com/abderahmababa-png/WeatherApp/releases/download/v9.8/app4051699-2gznhx.1.apk"
                encoded_text = urllib.parse.quote(share_text)
                whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
                
                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
                            <button style="
                                background-color: #25D366; 
                                color: white; 
                                border: none; 
                                padding: 12px 24px; 
                                font-size: 15px; 
                                font-weight: bold; 
                                border-radius: 8px; 
                                cursor: pointer;
                                box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
                                width: 100%;
                            ">
                                🟢 إرسال ملخص الطقس ورابط التطبيق عبر WhatsApp
                            </button>
                        </a>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.error(f"استجابة غير صالحة من خادم النماذج الجوية (رمز الخطأ: {response.status_code})")
            
        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة البيانات: {str(e)}")
