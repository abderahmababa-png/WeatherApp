import streamlit as st
import requests
import os
import streamlit.components.v1 as components
import urllib.parse

# 1. كود الحقن لمنع تداخل اللمس وتنسيق الهوية البصرية الزرقاء
st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        overscroll-behavior-y: contain !important;
        touch-action: pan-x pan-y !important;
    }
    .stButton>button {
        background-color: #1E88E5 !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: bold !important;
    }
    iframe {
        pointer-events: auto !important;
    }
    .prayer-box {
        background-color: #f9f9f9;
        border: 1px solid #1E88E5;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        direction: rtl;
        margin-top: 15px;
    }
    .prayer-item {
        display: inline-block;
        margin: 0 8px;
        font-size: 14px;
        font-weight: bold;
    }
    .prayer-time {
        color: #1E88E5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="طقس روصو Rosso weather", page_icon="🌤️", layout="centered")

# 2. إدارة عرض شعار التطبيق الدائري
LOGO_FILE = "1779505332712.jpg"
st.markdown("<style>.stImage img {border-radius: 50%; border: 3px solid #1E88E5; max-width: 140px; margin: 0 auto; display: block;}</style>", unsafe_allow_html=True)
if os.path.exists(LOGO_FILE): 
    st.image(LOGO_FILE)

# عنوان واجهة المستخدم الرئيسية على سطر واحد
st.markdown("<h2 style='text-align: center; color: #1E88E5; font-family: Arial; font-size: 24px; direction: rtl; margin-top: 10px;'>طقس روصو | Rosso weather</h2>", unsafe_allow_html=True)
st.write("---")

# 3. قسم تحديد الموقع والمدى الزمني
st.markdown("### 📍 الإعدادات الجغرافية والزمنية")
locations_map = {
    "روصو": {"lat": 16.51, "lon": -15.81},
    "اركيز": {"lat": 16.91, "lon": -15.28},
    "المذرذرة": {"lat": 16.92, "lon": -15.80},
    "بوتلميت": {"lat": 17.54, "lon": -14.77},
    "واد الناقة": {"lat": 17.98, "lon": -15.49},
    "كرمسين": {"lat": 16.49, "lon": -16.20},
    "تكنت": {"lat": 17.24, "lon": -16.14},
    "انجاكو": {"lat": 16.53, "lon": -16.45}
}

col_city, col_time = st.columns(2)
with col_city:
    selected_city = st.selectbox("اختر المقاطعة:", list(locations_map.keys()))
with col_time:
    period_map = {"24 ساعة": 24, "5 أيام": 120, "10 أيام": 240, "16 يوماً": 384}
    period = st.selectbox("المدى الزمني للتحليل:", list(period_map.keys()))

lat = locations_map[selected_city]["lat"]
lon = locations_map[selected_city]["lon"]

st.write("")
col_btn, col_empty = st.columns([1, 2])
with col_btn:
    show_radar = st.checkbox("🛰️ رادار الأمطار الحية", value=False)

# 4. عرض رادار الطقس التفاعلي والآمن (النموذج الأوروبي ECMWF)
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

# 5. معالجة وحساب المؤشرات، التدوينات، الإرشادات ومواقيت الصلاة
if st.button("📊 توليد وتحليل التدوينة الجوية", use_container_width=True):
    with st.spinner(f"جاري معالجة خرائط ونماذج {selected_city}..."):
        try:
            h = period_map[period]
            
            # مصفوفة الروابط لتفعيل نظام "التراجع الذكي والتبديل التلقائي"
            urls = []
            if h > 120:
                # الرابط الأول (نموذج GFS للمدى الطويل)
                urls.append(f"https://api.open-meteo.com/v1/gfs?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability,precipitation,wind_speed_10m&forecast_days=16")
            
            # الرابط الثاني (النموذج القياسي عالي الدقة والمستقر على اليابسة)
            urls.append(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_700hPa,precipitation_probability,precipitation,wind_speed_10m&forecast_days=7")
            
            prayer_url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=3"
            
            data = None
            # الفحص الذكي: جرب الروابط بالترتيب وارفض الرابط الذي يُرجع أصفاراً أو أخطاء
            for url in urls:
                try:
                    res = requests.get(url, timeout=10)
                    if res.status_code == 200:
                        potential_data = res.json().get("hourly", {})
                        if potential_data and "temperature_2m" in potential_data:
                            # فلترة للتأكد أن درجات الحرارة المستلمة ليست كلها أصفار (مشكلة انجاكو بالمدى الطويل)
                            test_temps = [x for x in potential_data["temperature_2m"] if x is not None]
                            if test_temps and any(v != 0.0 for v in test_temps):
                                data = potential_data
                                if "gfs" not in url:
                                    h = min(h, len(data["temperature_2m"]))  # ضبط المدى إذا تراجعنا للنموذج القياسي
                                break
                except Exception:
                    continue

            prayer_res = requests.get(prayer_url, timeout=10)
            
            if not data:
                st.error("⚠️ عذراً، خادم النماذج الجوية غير مستقر أو لا توفر بيانات صحيحة حالياً لهذا النطاق. يرجى المحاولة مرة أخرى.")
            else:
                actual_h = min(h, len(data["temperature_2m"]))
                
                # الفلترة الشاملة والتنظيف لمنع قيم NoneType نهائياً واستبدالها بـ 0.0
                temps = [float(x) if x is not None else 0.0 for x in data.get("temperature_2m", [])[:actual_h]]
                precip_list = [float(x) if x is not None else 0.0 for x in data.get("precipitation", [])[:actual_h]]
                precip = sum(precip_list)
                
                prob_list = [int(x) if x is not None else 0 for x in data.get("precipitation_probability", [])[:actual_h]]
                prob = max(prob_list) if prob_list else 0
                
                wind_speeds = [float(x) if x is not None else 0.0 for x in data.get("wind_speed_10m", [])[:actual_h]]
                max_wind = max(wind_speeds) if wind_speeds else 0.0
                
                max_t = max(temps) if temps else 0.0
                min_t = min(temps) if temps else 0.0
                
                raw_rh = data.get("relative_humidity_700hPa", [])[:actual_h] if "relative_humidity_700hPa" in data else []
                avg_rh = (sum([float(x) for x in raw_rh if x is not None]) / len(raw_rh)) if raw_rh else (55.0 if precip > 0 else 35.0)

                timings = {}
                if prayer_res.status_code == 200:
                    timings = prayer_res.json().get("data", {}).get("timings", {})

                # 5.1 عرض البطاقات القياسية (Metrics) بوضوح
                c1, c2, c3 = st.columns(3)
                c1.metric(f"🌡️ العظمى ({selected_city})", f"{max_t:.1f}°C")
                c2.metric("🌧️ إجمالي الأمطار", f"{precip:.1f} ملم")
                c3.metric("💨 ذروة الرياح السطحية", f"{max_wind:.1f} كم/س")
                
                st.write("")
                
                # 5.2 بناء وصياغة تدوينة الخبير الأرصادي التحليلية الدقيقة
                st.markdown(f"### 📝 تدوينة الخبير الأرصادي لـ ({selected_city}):")
                
                if h <= 24:
                    time_context = "خلال الأربع وعشرين ساعة القادمة"
                    trend_context = f"تستقر قراءات الحرارة اللحظية لتسجل عظمى تلامس {max_t:.1f}°C مع أجواء تميل للاعتدال النسبي خلال ساعات الفجر عند {min_t:.1f}°C."
                else:
                    time_context = f"خلال الفترة الممتدة للمدى المتوسط والبعيد ({period})"
                    trend_context = f"تشير حركة المحاكاة لتذبذب حراري مستمر، حيث تبلغ ذروة الاحترار {max_t:.1f}°C، بينما تنخفض الصغرى في فترات التبريد الإشعاعي الليلي لتلامس {min_t:.1f}°C."

                if avg_rh > 45:
                    moisture_influence = "مع رصد تدفقات ممتازة للرطوبة الجوية في الطبقات البنائية المتوسطة ممهدة لتكاثف حملي محلي."
                else:
                    moisture_influence = "برغم سيطرة كتل هوائية جافة نسبياً في طبقات الجو المتوسطة تحد من الامتداد الشاقولي للسحب السريعة."

                dust_context = ""
                if max_wind > 24:
                    dust_context = " مع رصد نشاط ملحوظ في سرعة الرياح السطحية الجافة، مما يرفع من احتمالية إثارة الأتربة المحلية العالقة في المناطق المفتوحة والمكشوفة."

                if precip > 0:
                    blog = f"""توضح تحديثات النماذج العددية لنطاق **{selected_city}** {time_context} مؤشرات على اضطرابات جوية محتملة{dust_context}. {trend_context}
                    
{moisture_influence} وبناءً عليه، تضع النماذج فرصة هطول مطري تصل ذروة احتماليتها إلى **{prob}%**، بتراكم إجمالي مرتقب يبلغ **{precip:.1f} ملم**، مما يعزز من فرص نشوء سحب ركامية رعدية على فترات."""
                else:
                    blog = f"""تُشير التنبؤات الجوية لنطاق **{selected_city}** {time_context} إلى سيطرة أجواء مستقرة بوجه عام{dust_context}. {trend_context}
                    
{moisture_influence} وبالتالي تبقى فرص الهطول الفعلي منعدمة عند **0.0 ملم** مع تراجع احتمالية الأمطار لـ **{prob}%**."""
                
                st.info(blog)
                
                # 5.3 قسم النصائح والإرشادات الإنسانية العامة لحماية المستخدمين
                st.markdown("### 💡 الإرشادات والنصائح الوقائية العامة:")
                if precip > 2:
                    st.warning("⚠️ **تنبيه السلامة من الأمطار:** يُتوقع هطول أمطار معتبرة؛ يرجى الابتعاد تماماً عن مجاري السيول وتجمعات المياه الراكدة، وتجنب ملامسة أعمدة الكهرباء أو الأسلاك المكشوفة أثناء وبعد المطر حفاظاً على سلامتكم.")
                elif max_wind > 24:
                    st.info("💨 **تنبيه رياح وأتربة:** تنشط الرياح بشكل قد يثير بعض الغبار الخفيف العالق؛ ينصح لمرضى الجهاز التنفسي والعيون بالحذر عند الخروج في الأوقات التي تشتد فيها الهبات السطحية.")
                elif max_t > 38:
                    st.error("☀️ **وقاية من الإجهاد الحراري:** الطقس شديد الحرارة؛ يُنصح بعدم التعرض المباشر لأشعة الشمس في أوقات الذروة، والحرص على شرب كميات كافية من المياه طوال اليوم لتفادي ضربات الشمس.")
                else:
                    st.success("🌱 **أجواء مستقرة:** الطقس معتدل ومناسب جداً للأنشطة الخارجية؛ ننصحك باستغلال هذه الأجواء الطيبة مع الحفاظ على شرب السوائل بانتظام لتنشيط الجسم.")

                # 5.4 عرض مربع مواقيت الصلاة المصغر والمحمي والذكي والمدمج في الأسفل
                if timings:
                    st.write("---")
                    current_precipitation_now = data.get("precipitation", [0])[0] if data.get("precipitation") else 0
                    
                    prayer_alert = ""
                    if precip > 0 and prob > 60:
                        prayer_alert = f"<p style='color:#1E88E5; font-size:13px; margin-top:5px; font-weight:bold;'>📢 تنبيه: توقعات المطر الحالية ({prob}%) تتطلب الانتباه لسلامة المصلين وتجنب الأماكن الزلقة عند التوجه للمساجد.</p>"
                    elif current_precipitation_now > 0.5:
                        prayer_alert = "<p style='color:#d32f2f; font-size:13px; margin-top:5px; font-weight:bold;'>🌧️ تنبيه عاجل: هطول مطري الآن؛ يرجى أخذ الحيطة والحذر الشديد أثناء الذهاب لأداء الصلاة.</p>"
                    elif max_wind > 26:
                        prayer_alert = "<p style='color:#f57c00; font-size:13px; margin-top:5px; font-weight:bold;'>💨 تنبيه: الرياح نشطة ومثيرة للأتربة؛ ينصح بوضع لثام أو كمامة واقية عند الذهاب للمسجد لمرضى الصدر والربو.</p>"
                    else:
                        prayer_alert = "<p style='color:#388e3c; font-size:13px; margin-top:5px; font-weight:bold;'>🌤️ الأجواء مستقرة تماماً ومناسبة للذهاب إلى المساجد بأمان.</p>"

                    st.markdown(
                        f"""
                        <div class="prayer-box">
                            <strong style="color: #333;">🕌 مواقيت الصلاة اليوم في {selected_city}:</strong>
                            <hr style="margin: 5px 0; border: 0; border-top: 1px solid #ddd;">
                            <div class="prayer-item">الفجر: <span class="prayer-time">{timings.get('Fajr', '--:--')}</span></div> |
                            <div class="prayer-item">الظهر: <span class="prayer-time">{timings.get('Dhuhr', '--:--')}</span></div> |
                            <div class="prayer-item">العصر: <span class="prayer-time">{timings.get('Asr', '--:--')}</span></div> |
                            <div class="prayer-item">المغرب: <span class="prayer-time">{timings.get('Maghrib', '--:--')}</span></div> |
                            <div class="prayer-item">العشاء: <span class="prayer-time">{timings.get('Isha', '--:--')}</span></div>
                            {prayer_alert}
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                
                # 5.5 زر مشاركة ملخص الطقس مع رابط الـ APK الحصري والمباشر عبر الواتساب
                st.write("---")
                share_text = f"🌤️ طقس {selected_city} اليوم:\n- الحرارة العظمى: {max_t:.1f}°C\n- الأمطار: {precip:.1f} ملم\n- الرياح: {max_wind:.1f} كم/س\n\n👇 لمتابعة رادار السحب ومواقيت الصلاة في الترارزة, حمل تطبيقنا برابط مباشر APK من هنا:\nhttps://github.com/abderahmababa-png/WeatherApp/releases/download/v9.8/app4051699-2gznhx.1.apk"
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
            
        except requests.exceptions.ConnectionError:
            st.error("📡 **مشكلة في الاتصال:** يبدو أن الاتصال بالشبكة غير مستقر حالياً أو تم رفضه. يرجى الانتظار ثوانٍ قليلة والمحاولة مرة أخرى.")
        except requests.exceptions.Timeout:
            st.error("⏳ **انتهت مهلة الطلب:** استغرق الخادم وقتاً طويلاً للاستجابة والرد. يرجى التحقق من جودة الإنترنت وإعادة المحاولة.")
        except Exception as e:
            st.error(f"حدث خطأ غير متوقع أثناء معالجة البيانات: {str(e)}")
