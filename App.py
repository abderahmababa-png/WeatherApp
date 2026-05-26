import streamlit as st
import requests
import os
import streamlit.components.v1 as components
import urllib.parse
from datetime import datetime, timedelta

# 1. كود الحقن التجميلي وتنسيق الهوية البصرية الزرقاء ومنع مشاكل اللمس
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
        padding: 15px;
        text-align: center;
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
    .weather-card {
        background-color: #f0f7ff;
        border: 1px solid #d0e4ff;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        margin: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. شريط الإعدادات الجانبي (Sidebar) لتخصيص التجربة
st.sidebar.markdown("## ⚙️ الإعدادات / Settings")
lang = st.sidebar.selectbox("🌐 لغة العرض / Language", ["العربية", "English"])
unit = st.sidebar.selectbox("🌡️ وحدة قياس الحرارة", ["الدرجة المئوية (°C)", "الفهرنهايت (°F)"])
display_style = st.sidebar.selectbox("📊 شكل عرض التوقعات الأسبوعية", ["بطاقات صغيرة لكل يوم", "جدول منظم"])

# قاموس المصطلحات المترجمة للتبديل الفوري بين اللغتين
strings = {
    "العربية": {
        "title": "طقس روصو | Rosso weather",
        "geo_settings": "📍 الإعدادات الجغرافية والزمنية",
        "select_city": "اختر المقاطعة:",
        "select_period": "المدى الزمني للتحليل:",
        "radar": "🛰️ رادار الأمطار الحية",
        "generate_btn": "📊 توليد وتحليل التدوينة الجوية",
        "current_status": "🌤️ الحالة الجوية اللحظية الحالية",
        "temp_label": "درجة الحرارة الحالية",
        "sky_label": "حالة السماء",
        "wind_label": "سرعة الرياح",
        "max_temp": "الحرارة العظمى",
        "tot_rain": "إجمالي الأمطار",
        "peak_wind": "ذروة الرياح",
        "expert_blog": "📝 تدوينة الخبير الأرصادي:",
        "advices": "💡 الإرشادات والنصائح الوقائية العامة:",
        "prayer_title": "🕌 مواقيت الصلاة اليوم في",
        "fajr": "الفجر", "dhuhr": "الظهر", "asr": "العصر", "maghrib": "المغرب", "isha": "العشاء",
        "whatsapp_btn": "🟢 إرسال ملخص الطقس والمواقيت ورابط التطبيق عبر WhatsApp",
        "weekly_title": "📅 التوقعات اليومية للمدى القادم"
    },
    "English": {
        "title": "Rosso Weather | طقس روصو",
        "geo_settings": "📍 Geographic & Time Settings",
        "select_city": "Select District:",
        "select_period": "Analysis Timeframe:",
        "radar": "🛰️ Live Rain Radar",
        "generate_btn": "📊 Generate & Analyze Weather Report",
        "current_status": "🌤️ Current Real-time Weather Status",
        "temp_label": "Current Temperature",
        "sky_label": "Sky Condition",
        "wind_label": "Wind Speed",
        "max_temp": "Max Temp",
        "tot_rain": "Total Rain",
        "peak_wind": "Peak Wind",
        "expert_blog": "📝 Meteorologist Analysis Blog:",
        "advices": "💡 Public Safety & Preventive Guidelines:",
        "prayer_title": "🕌 Prayer Times Today in",
        "fajr": "Fajr", "dhuhr": "Dhuhr", "asr": "Asr", "maghrib": "Maghrib", "isha": "Isha",
        "whatsapp_btn": "🟢 Send Weather Summary & App Link via WhatsApp",
        "weekly_title": "📅 Daily Forecast for the Coming Period"
    }
}

txt = strings[lang]
is_rtl = "direction: rtl; text-align: right;" if lang == "العربية" else "direction: ltr; text-align: left;"

st.set_page_config(page_title="طقس روصو Rosso weather", page_icon="🌤️", layout="centered")

# دالة تحويل درجات الحرارة بناءً على الإعدادات المحددة
def format_temp(celsius_val):
    if "الفهرنهايت" in unit:
        return f"{(celsius_val * 9/5) + 32:.1f}°F"
    return f"{celsius_val:.1f}°C"

# 3. إدارة عرض شعار التطبيق الدائري
LOGO_FILE = "1779505332712.jpg"
st.markdown("<style>.stImage img {border-radius: 50%; border: 3px solid #1E88E5; max-width: 140px; margin: 0 auto; display: block;}</style>", unsafe_allow_html=True)
if os.path.exists(LOGO_FILE): 
    st.image(LOGO_FILE)

st.markdown(f"<h2 style='text-align: center; color: #1E88E5; font-family: Arial; font-size: 24px; {is_rtl}'>{txt['title']}</h2>", unsafe_allow_html=True)
st.write("---")

# 4. النطاق الجغرافي للبلديات والمقاطعات
st.markdown(f"<h3 style='{is_rtl}'>{txt['geo_settings']}</h3>", unsafe_allow_html=True)
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
    selected_city = st.selectbox(txt["select_city"], list(locations_map.keys()))
with col_time:
    period_map = {"24 ساعة": 24, "5 أيام": 120, "10 أيام": 240, "16 يوماً": 384}
    period = st.selectbox(txt["select_period"], list(period_map.keys()))

lat = locations_map[selected_city]["lat"]
lon = locations_map[selected_city]["lon"]

st.write("")
col_btn, col_empty = st.columns([1, 2])
with col_btn:
    show_radar = st.checkbox(txt["radar"], value=False)

if show_radar:
    custom_map_html = f"""
    <div style="width: 100%; height: 380px; border-radius: 10px; overflow: hidden; border: 2px solid #1E88E5; position: relative; background-color: #1a1a1a;">
        <div style="width: 100%; height: 100%; top: -45px; position: absolute;">
            <iframe src="https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&zoom=8&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=true&type=map&location=coordinates" 
                    width="100%" height="470px" frameborder="0" style="border:0; clip-path: inset(45px 0px 45px 0px);">
            </iframe>
        </div>
    </div>
    """
    components.html(custom_map_html, height=390)

st.write("---")

# 5. معالجة وحساب المؤشرات، التدوينات، الإرشادات ومواقيت الصلاة
if st.button(txt["generate_btn"], use_container_width=True):
    with st.spinner("Processing..."):
        try:
            h = period_map[period]
            urls = []
            if h > 120:
                urls.append(f"https://api.open-meteo.com/v1/gfs?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability,precipitation,wind_speed_10m&forecast_days=16")
            urls.append(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_700hPa,precipitation_probability,precipitation,wind_speed_10m&forecast_days=7")
            
            prayer_url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=3"
            
            data = None
            # نظام التراجع والتحويل التلقائي لحماية إحداثيات انجاكو من الأصفار والأخطاء
            for url in urls:
                try:
                    res = requests.get(url, timeout=10)
                    if res.status_code == 200:
                        potential_data = res.json().get("hourly", {})
                        if potential_data and "temperature_2m" in potential_data:
                            test_temps = [x for x in potential_data["temperature_2m"] if x is not None]
                            if test_temps and any(v != 0.0 for v in test_temps):
                                data = potential_data
                                if "gfs" not in url:
                                    h = min(h, len(data["temperature_2m"]))
                                break
                except Exception:
                    continue

            prayer_res = requests.get(prayer_url, timeout=10)
            
            if not data:
                st.error("⚠️ Error fetching weather data.")
            else:
                actual_h = min(h, len(data["temperature_2m"]))
                
                temps = [float(x) if x is not None else 0.0 for x in data.get("temperature_2m", [])[:actual_h]]
                precip_list = [float(x) if x is not None else 0.0 for x in data.get("precipitation", [])[:actual_h]]
                precip = sum(precip_list)
                
                prob_list = [int(x) if x is not None else 0 for x in data.get("precipitation_probability", [])[:actual_h]]
                prob = max(prob_list) if prob_list else 0
                
                wind_speeds = [float(x) if x is not None else 0.0 for x in data.get("wind_speed_10m", [])[:actual_h]]
                max_wind = max(wind_speeds) if wind_speeds else 0.0
                
                max_t, min_t = max(temps), min(temps)
                
                # حساب القراءات الحالية المباشرة (الساعة الأولى من المصفوفة)
                current_temp_c = temps[0] if temps else 0.0
                current_wind = wind_speeds[0] if wind_speeds else 0.0
                current_rain = precip_list[0] if precip_list else 0.0
                
                # تحديد أيقونة وحالة السماء الحالية ذكياً
                if current_rain > 0.1:
                    sky_status = "ممطر 🌧️" if lang == "العربية" else "Rainy 🌧️"
                elif prob > 40:
                    sky_status = "غائم ☁️" if lang == "العربية" else "Cloudy ☁️"
                else:
                    sky_status = "مشمس ☀️" if lang == "العربية" else "Sunny ☀️"

                timings = prayer_res.json().get("data", {}).get("timings", {}) if prayer_res.status_code == 200 else {}

                # 🌟 عرض الواجهة الرئيسية البسيطة اللحظية (المطلوبة)
                st.markdown(f"<h3 style='color:#1E88E5; {is_rtl}'>{txt['current_status']}</h3>", unsafe_allow_html=True)
                w_col1, w_col2, w_col3 = st.columns(3)
                w_col1.metric(txt["temp_label"], format_temp(current_temp_c))
                w_col2.metric(txt["sky_label"], sky_status)
                w_col3.metric(txt["wind_label"], f"{current_wind:.1f} كم/س")
                
                st.write("---")

                # عرض بطاقات التحليل الكلي
                c1, c2, c3 = st.columns(3)
                c1.metric(f"🌡️ {txt['max_temp']} ({selected_city})", format_temp(max_t))
                c2.metric(f"🌧️ {txt['tot_rain']}", f"{precip:.1f} ملم")
                c3.metric(f"💨 {txt['peak_wind']}", f"{max_wind:.1f} كم/س")
                
                # 📅 معالجة وعرض التوقعات الأسبوعية / اليومية (المطلوبة)
                st.write("")
                st.markdown(f"<h3 style='{is_rtl}'>{txt['weekly_title']}</h3>", unsafe_allow_html=True)
                
                daily_forecasts = []
                steps = 24
                today = datetime.now()
                
                for idx in range(0, actual_h, steps):
                    day_chunk_t = temps[idx:idx+steps]
                    day_chunk_p = precip_list[idx:idx+steps]
                    day_chunk_w = wind_speeds[idx:idx+steps]
                    
                    if day_chunk_t:
                        day_date = (today + timedelta(days=idx//24)).strftime('%Y-%m-%d')
                        day_max = max(day_chunk_t)
                        day_rain = sum(day_chunk_p)
                        day_wind = max(day_chunk_w)
                        
                        icon = "☀️"
                        if day_rain > 0.2: icon = "🌧️"
                        elif day_wind > 25: icon = "💨"
                        
                        daily_forecasts.append({
                            "date": day_date, "max": day_max, "rain": day_rain, "wind": day_wind, "icon": icon
                        })

                if display_style == "بطاقات صغيرة لكل يوم" or display_style == "Small Cards":
                    cols = st.columns(min(len(daily_forecasts), 4))
                    for i, df in enumerate(daily_forecasts):
                        with cols[i % 4]:
                            st.markdown(f"""
                            <div class="weather-card">
                                <strong>{df['date']}</strong><br>
                                <span style='font-size:24px;'>{df['icon']}</span><br>
                                <span>{format_temp(df['max'])}</span><br>
                                <span style='font-size:11px; color:#555;'>🌧️ {df['rain']:.1f}mm | 💨 {df['wind']:.0f}kph</span>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    import pandas as pd
                    df_table = pd.DataFrame(daily_forecasts)
                    df_table.columns = ['التاريخ', 'العظمى', 'الأمطار', 'الرياح', 'الحالة'] if lang == "العربية" else ['Date', 'Max Temp', 'Rain', 'Wind', 'Status']
                    st.dataframe(df_table, use_container_width=True)

                # تدوينة الخبير الأرصادي التحليلية
                st.write("---")
                st.markdown(f"<h3 style='{is_rtl}'>{txt['expert_blog']}</h3>", unsafe_allow_html=True)
                
                trend_context = f"تسجل القراءات تذبذباً حرارياً تبلغ ذروته {format_temp(max_t)}."
                blog = f"تشير النماذج الاستشعارية لنطاق **{selected_city}** إلى استقرار جوي نسبي. {trend_context} مع احتمالية أمطار تبلغ {prob}% بتراكم إجمالي {precip:.1f} ملم."
                st.info(blog)
                
                # قسم النصائح والإرشادات
                st.markdown(f"<h3 style='{is_rtl}'>{txt['advices']}</h3>", unsafe_allow_html=True)
                if precip > 2:
                    st.warning("⚠️ الابتعاد تماماً عن مجاري السيول وتجمعات المياه المكشوفة.")
                else:
                    st.success("🌱 الأجواء مستقرة ومناسبة للأنشطة والتحركات الخارجية المعتادة.")

                # مواقيت الصلاة المربوطة والمدمجة بحالة الطقس
                if timings:
                    st.write("---")
                    prayer_alert = "<p style='color:#388e3c; font-size:13px; font-weight:bold;'>🌤️ الأجواء مستقرة وملائمة للذهاب إلى المساجد بأمان تام.</p>"
                    st.markdown(
                        f"""
                        <div class="prayer-box" style="{is_rtl}">
                            <strong>{txt['prayer_title']} {selected_city}:</strong>
                            <hr style="margin: 5px 0; border-top: 1px solid #ddd;">
                            <div class="prayer-item">{txt['fajr']}: <span class="prayer-time">{timings.get('Fajr', '--:--')}</span></div> |
                            <div class="prayer-item">{txt['dhuhr']}: <span class="prayer-time">{timings.get('Dhuhr', '--:--')}</span></div> |
                            <div class="prayer-item">{txt['asr']}: <span class="prayer-time">{timings.get('Asr', '--:--')}</span></div> |
                            <div class="prayer-item">{txt['maghrib']}: <span class="prayer-time">{timings.get('Maghrib', '--:--')}</span></div> |
                            <div class="prayer-item">{txt['isha']}: <span class="prayer-time">{timings.get('Isha', '--:--')}</span></div>
                            {prayer_alert}
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                
                # زر مشاركة ملخص الطقس عبر الواتساب
                st.write("---")
                share_text = f"🌤️ طقس {selected_city}:\n- الحرارة: {format_temp(max_t)}\n- الأمطار: {precip:.1f} ملم\n\n👇 حمل تطبيقنا برابط مباشر APK من هنا:\nhttps://github.com/abderahmababa-png/WeatherApp/releases/download/v9.8/app4051699-2gznhx.1.apk"
                encoded_text = urllib.parse.quote(share_text)
                whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
                
                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
                            <button style="background-color: #25D366; color: white; border: none; padding: 12px 24px; font-size: 15px; font-weight: bold; border-radius: 8px; width: 100%; cursor: pointer;">
                                {txt['whatsapp_btn']}
                            </button>
                        </a>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة وحساب البيانات: {str(e)}")
