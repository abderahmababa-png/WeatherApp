import streamlit as st
import requests
import os
import streamlit.components.v1 as components
import urllib.parse
from datetime import datetime

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
            
            # 1. جلب بيانات الطقس
            if h > 120:
                weather_url = f"https://api.open-meteo.com/v1/gfs?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability,precipitation,wind_speed_10m&forecast_days=16"
            else:
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_700hPa,precipitation_probability,precipitation,wind_speed_10m&forecast_days=7"
                
            # 2. جلب بيانات جودة الهواء والغبار (خاص بالترارزة والرياح المثيرة للأتربة)
            aq_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&hourly=pm10,pm2_5,dust&forecast_days=1"
            
            # 3. جلب مواقيت الصلاة بناءً على الإحداثيات
            prayer_url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=3" # طريقة جامعة أم القرى أو الهيئة العامة المصرية المناسبة لأفريقيا
            
            weather_res = requests.get(weather_url)
            aq_res = requests.get(aq_url)
            prayer_res = requests.get(prayer_url)
            
            if weather_res.status_code == 200:
                data = weather_res.json()["hourly"]
                actual_h = min(h, len(data["temperature_2m"]))
                
                # تنظيف ومعالجة بيانات الطقس الأساسية
                temps = [float(x) if x is not None else 0.0 for x in data.get("temperature_2m", [])[:actual_h]]
                precip_list = [float(x) if x is not None else 0.0 for x in data.get("precipitation", [])[:actual_h]]
                precip = sum(precip_list)
                prob = max([int(x) if x is not None else 0 for x in data.get("precipitation_probability", [])[:actual_h]]) if data.get("precipitation_probability") else 0
                max_wind = max([float(x) if x is not None else 0.0 for x in data.get("wind_speed_10m", [])[:actual_h]]) if data.get("wind_speed_10m") else 0
                max_t = max(temps) if temps else 0.0
                min_t = min(temps) if temps else 0.0
                
                # حساب الرطوبة المتوسطة
                raw_rh = data.get("relative_humidity_700hPa", [])[:actual_h] if "relative_humidity_700hPa" in data else []
                avg_rh = (sum([float(x) for x in raw_rh if x is not None]) / len(raw_rh)) if raw_rh else (55.0 if precip > 0 else 35.0)

                # قراءة بيانات جودة الهواء (الغبار العالق PM10)
                dust_value = 0
                air_quality_status = "جيد"
                if aq_res.status_code == 200:
                    aq_data = aq_res.json().get("hourly", {})
                    pm10_list = [float(x) for x in aq_data.get("pm10", []) if x is not None]
                    if pm10_list:
                        dust_value = pm10_list[0] # القيمة الحالية
                        if dust_value > 150: air_quality_status = "خطير / عاصفة رملية"
                        elif dust_value > 100: air_quality_status = "غير صحي"
                        elif dust_value > 50: air_quality_status = "متوسط"

                # قراءة مواقيت الصلاة اليومية
                timings = {}
                if prayer_res.status_code == 200:
                    timings = prayer_res.json().get("data", {}).get("timings", {})

                # عرض المؤشرات الأساسية
                c1, c2, c3 = st.columns(3)
                c1.metric(f"🌡️ العظمى ({selected_city})", f"{max_t:.1f}°C")
                c2.metric("🌧️ إجمالي الأمطار", f"{precip:.1f} ملم")
                c3.metric("🌪️ مؤشر الغبار الحالي", f"{dust_value:.0f} µg/m³", help="يقيس كمية الأتربة العالقة في الجو نتيجة الرياح")
                
                st.write("")
                
                # 🕌 قسم مواقيت الصلاة والربط الذكي مع الطقس
                if timings:
                    st.markdown(f"### 🕌 مواقيت الصلاة اليوم في مقاطعة {selected_city}:")
                    p_cols = st.columns(5)
                    p_names = {"Fajr": "الفجر", "Dhuhr": "الظهر", "Asr": "العصر", "Maghrib": "المغرب", "Isha": "العشاء"}
                    idx = 0
                    for eng, arb in p_names.items():
                        if eng in timings:
                            p_cols[idx].metric(arb, timings[eng])
                            idx += 1
                    
                    # الفحص الذكي للربط الجوي-الشرعي
                    st.markdown("#### 🔔 التنبيهات المرتبطة بالصلوات:")
                    current_precipitation_now = data.get("precipitation", [0])[0] # كمية المطر الحالية المتوقعة
                    
                    # سيناريو المطر وقت الصلوات (خاصة المغرب والعشاء لجمع التقديم والـتأخير في الفقه المالكي)
                    if precip > 0 and prob > 60:
                        st.info(f"⚠️ **تنبيه للمصلين:** هناك مؤشرات لهطول أمطار بنسبة {prob}% خلال الساعات القادمة. يرجى أخذ الحيطة عند الذهاب للمساجد خاصة لوقاية كبار السن، وتذكر الرخص الشرعية في حال اشتداد المطر ووحل الطرق.")
                    elif current_precipitation_now > 0.5:
                        st.warning(f"🌧️ **تنبيه مطري عاجل:** الأجواء ممطرة الآن بالتزامن مع فترات الصلاة؛ يرجى الحذر من الانزلاقات أو برك المياه المحيطة ببيوت الله.")
                    
                    # سيناريو العواصف الرملية وقت الصلاة (شائع جداً في الترارزة)
                    if dust_value > 100 or max_wind > 28:
                        st.warning(f"😷 **تنبيه عاصفة ترابية:** يرجى من المصلين (خصوصاً المصابين بالربو أو ضيق التنفس) وضع لثام أو كمامة واقية أثناء التوجه لأداء الصلاة في المسجد نظراً لارتفاع تركيز الغبار السطحي لـ {dust_value:.0f} وحدة.")
                    else:
                        st.success("🌤️ الأجواء مستقرة ومناسبة للذهاب إلى المساجد دون عوائق جوية مرصودة.")
                
                st.write("---")

                # 🔘 أولاً: تدوينة الخبير الأرصادي
                st.markdown(f"### 📝 تدوينة الخبير الأرصادي لـ ({selected_city}):")
                
                if h == 24:
                    time_context = "خلال الأربع وعشرين ساعة القادمة"
                    trend_context = f"تستقر قراءات الحرارة اللحظية لتسجل عظمى تلامس {max_t:.1f}°C مع أجواء تميل للاعتدال النسبي خلال ساعات الفجر عند {min_t:.1f}°C."
                else:
                    time_context = f"خلال الفترة الممتدة للمدى المتوسط والبعيد ({period})"
                    trend_context = f"تشير حركة المحاكاة لتذبذب حراري مستمر، حيث تبلغ ذروة الاحترار {max_t:.1f}°C، بينما تنخفض الصغرى في فترات التبريد الإشعاعي الليلي لتلامس {min_t:.1f}°C."

                if avg_rh > 45:
                    moisture_influence = "مع رصد تدفقات ممتازة للرطوبة الجوية في الطبقات البنائية المتوسطة ممهدة لتكاثف حملي محلي."
                else:
                    moisture_influence = "برغم سيطرة كتل هوائية جافة نسبياً في طبقات الجو المتوسطة تحد من الامتداد الشاقولي للسحب السريعة."

                # إضافة وضع الغبار للتدوينة
                dust_context = ""
                if dust_value > 100:
                    dust_context = f" متزامنة مع هبوب رياح نشطة ومثيرة للأتربة والغبار الناتجة عن التيارات الهابطة، حيث يسجل مؤشر نقاء الهواء جودة ({air_quality_status})."

                if precip > 0:
                    blog = f"""توضح تحديثات النماذج العددية لنطاق **{selected_city}** {time_context} مؤشرات على اضطرابات جوية محتملة{dust_context}. {trend_context}
                    
{moisture_influence} وبناءً عليه، تضع النماذج فرصة هطول مطري تصل ذروة احتماليتها إلى **{prob}%**، بتراكم إجمالي مرتقب يبلغ **{precip:.1f} ملم**، مما يعزز من فرص نشوء سحب ركامية رعدية على فترات."""
                else:
                    blog = f"""تُشير التنبؤات الجوية لنطاق **{selected_city}** {time_context} إلى سيطرة أجواء مستقرة بوجه عام{dust_context}. {trend_context}
                    
{moisture_influence} وبالتالي تبقى فرص الهطول الفعلي منعدمة عند **0.0 ملم** مع تراجع احتمالية الأمطار لـ **{prob}%**، مع نشاط معتدل للرياح السطحية قد يثير بعض الأتربة العالقة في المناطق المكشوفة."""
                
                st.info(blog)
                
                # 🔘 ثانياً: الإرشادات والنصائح الإنسانية الوقائية
                st.markdown("### 💡 الإرشادات والنصائح الوقائية العامة:")
                if precip > 2:
                    st.warning("⚠️ **تنبيه السلامة من الأمطار:** يُتوقع هطول أمطار معتبرة؛ يرجى الابتعاد تماماً عن مجاري السيول وتجمعات المياه الراكدة، وتجنب ملامسة أعمدة الكهرباء أو الأسلاك المكشوفة أثناء وبعد المطر حفاظاً على سلامتكم.")
                elif dust_value > 100 or max_wind > 25:
                    st.error("💨 **تنبيه الغبار الحاد (خاص بالترارزة):** مؤشر التلوث والغبار مرتفع حالياً؛ ينصح بشدة بإغلاق النوافذ، وارتداء الكمامات لحماية الجهاز التنفسي، وامتناع المصابين بالربو والجفاف عن الخروج إلا للضرورة القصوى.")
                elif max_t > 38:
                    st.error("☀️ **وقاية من الإجهاد الحراري:** الطقس شديد الحرارة؛ يُنصح بعدم التعرض المباشر لأشعة الشمس في أوقات الذروة، والحرص على شرب كميات كافية من المياه طوال اليوم لتفادي ضربات الشمس.")
                else:
                    st.success("🌱 **أجواء مستقرة:** الطقس معتدل ومناسب جداً للأنشطة الخارجية؛ ننصحك باستغلال هذه الأجواء الطيبة مع الحفاظ على شرب السوائل بانتظام لتنشيط الجسم.")
                
                # 🔘 ثالثاً: زر مشاركة الطقس في الأسفل
                st.write("---")
                share_text = f"🌤️ طقس {selected_city} اليوم:\n- الحرارة العظمى: {max_t:.1f}°C\n- الأمطار: {precip:.1f} ملم\n- الغبار: {dust_value:.0f} µg/m³\n\n👇 لمتابعة رادار السحب ومواقيت الصلاة في الترارزة، حمل تطبيقنا برابط مباشر APK من هنا:\nhttps://github.com/abderahmababa-png/WeatherApp/releases/download/v9.8/app4051699-2gznhx.1.apk"
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
                                🟢 إرسال ملخص الطقس والمواقيت ورابط التطبيق عبر WhatsApp
                            </button>
                        </a>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.error(f"استجابة غير صالحة من خادم النماذج الجوية (رمز الخطأ: {weather_res.status_code})")
            
        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة البيانات: {str(e)}")
