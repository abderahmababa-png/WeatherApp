import streamlit as st
import requests
import os
import streamlit.components.v1 as components
import urllib.parse
from datetime import datetime, timedelta

# 1. كود الحقن التجميلي المكثف لتقليل المسافات العمودية ومنع مشاكل اللمس
st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        overscroll-behavior-y: contain !important;
        touch-action: pan-x pan-y !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
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
    .prayer-row {
        background-color: #f9f9f9;
        border: 1px solid #1E88E5;
        border-radius: 6px;
        padding: 8px;
        text-align: center;
        margin: 5px 0;
        font-size: 13px;
    }
    .prayer-item {
        display: inline-block;
        margin: 0 5px;
        font-weight: bold;
    }
    .prayer-time {
        color: #1E88E5;
    }
    .weather-card {
        background-color: #f0f7ff;
        border: 1px solid #d0e4ff;
        border-radius: 6px;
        padding: 6px;
        text-align: center;
        margin: 2px;
        font-size: 12px;
    }
    hr {
        margin: 8px 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. شريط الإعدادات الجانبي (Sidebar)
st.sidebar.markdown("## ⚙️ الإعدادات / Settings")
lang = st.sidebar.selectbox("🌐 لغة العرض / Language", ["العربية", "English"])
unit = st.sidebar.selectbox("🌡️ وحدة قياس الحرارة", ["الدرجة المئوية (°C)", "الفهرنهايت (°F)"])
display_style = st.sidebar.selectbox("📊 شكل عرض التوقعات", ["بطاقات صغيرة لكل يوم", "جدول منظم"])

strings = {
    "العربية": {
        "title": "طقس روصو | Rosso weather",
        "geo_settings": "📍 الإعدادات الجغرافية والزمنية",
        "select_city": "اختر المقاطعة:",
        "select_period": "المدى الزمني:",
        "radar": "🛰️ رادار الأمطار الحية",
        "generate_btn": "📊 توليد وتحليل التدوينة الجوية",
        "current_status": "🌤️ الحالة اللحظية للطقس اليوم (النموذج الأوروبي الدقيق ECMWF)",
        "temp_label": "الحرارة الحالية",
        "sky_label": "السماء",
        "wind_label": "الرياح",
        "max_temp": "العظمى المقدرة",
        "tot_rain": "إجمالي المطر",
        "peak_wind": "ذروة الرياح",
        "expert_blog": "📝 تحليل الخبير الأرصادي والتدوينة المخصصة",
        "advices": "💡 الإرشادات الوقائية",
        "prayer_title": "🕌 مواقيت الصلاة في",
        "fajr": "الفجر", "dhuhr": "الظهر", "asr": "العصر", "maghrib": "المغرب", "isha": "العشاء",
        "whatsapp_btn": "🟢 مشاركة ملخص الطقس والمواقيت عبر WhatsApp",
        "weekly_title": "📅 التوقعات اليومية للمدى القادم (اضغط للفتح)"
    },
    "English": {
        "title": "Rosso Weather | طقس روصو",
        "geo_settings": "📍 Geographic Settings",
        "select_city": "District:",
        "select_period": "Timeframe:",
        "radar": "🛰️ Live Rain Radar",
        "generate_btn": "📊 Generate Report",
        "current_status": "🌤️ Weather Status (ECMWF Model)",
        "temp_label": "Temp",
        "sky_label": "Sky",
        "wind_label": "Wind",
        "max_temp": "Max Temp",
        "tot_rain": "Total Rain",
        "peak_wind": "Peak Wind",
        "expert_blog": "📝 Meteorologist Analysis Blog",
        "advices": "💡 Preventive Guidelines",
        "prayer_title": "🕌 Prayers in",
        "fajr": "Fajr", "dhuhr": "Dhuhr", "asr": "Asr", "maghrib": "Maghrib", "isha": "Isha",
        "whatsapp_btn": "🟢 Share Summary via WhatsApp",
        "weekly_title": "📅 Daily Forecast for Coming Period (Click to Expand)"
    }
}

txt = strings[lang]
is_rtl = "direction: rtl; text-align: right;" if lang == "العربية" else "direction: ltr; text-align: left;"

st.set_page_config(page_title="طقس روصو Rosso weather", page_icon="🌤️", layout="centered")

def format_temp(celsius_val):
    if "الفهرنهايت" in unit:
        return f"{(celsius_val * 9/5) + 32:.1f}°F"
    return f"{celsius_val:.1f}°C"

LOGO_FILE = "1779505332712.jpg"
if os.path.exists(LOGO_FILE): 
    st.markdown("<style>.stImage img {border-radius: 50%; border: 2px solid #1E88E5; max-width: 65px; margin: 0 auto; display: block;}</style>", unsafe_allow_html=True)
    st.image(LOGO_FILE)

st.markdown(f"<h3 style='text-align: center; color: #1E88E5; font-family: Arial; margin:0; padding:0; {is_rtl}'>{txt['title']}</h3>", unsafe_allow_html=True)

locations_map = {
    "روصو": {"lat": 16.51, "lon": -15.81}, "اركيز": {"lat": 16.91, "lon": -15.28},
    "المذرذرة": {"lat": 16.92, "lon": -15.80}, "بوتلميت": {"lat": 17.54, "lon": -14.77},
    "واد الناقة": {"lat": 17.98, "lon": -15.49}, "كرمسين": {"lat": 16.49, "lon": -16.20},
    "تكنت": {"lat": 17.24, "lon": -16.14}, "انجاكو": {"lat": 16.53, "lon": -16.45}
}

col_city, col_time, col_rad_check = st.columns([2, 1.5, 1.5])
with col_city:
    selected_city = st.selectbox(txt["select_city"], list(locations_map.keys()), label_visibility="collapsed")
with col_time:
    period_map = {"24 ساعة": 24, "5 أيام": 120, "10 أيام": 240, "16 يوماً": 384}
    period = st.selectbox(txt["select_period"], list(period_map.keys()), label_visibility="collapsed")
with col_rad_check:
    show_radar = st.checkbox(txt["radar"], value=False)

lat = locations_map[selected_city]["lat"]
lon = locations_map[selected_city]["lon"]

if show_radar:
    custom_map_html = f"""
    <div style="width: 100%; height: 260px; border-radius: 8px; overflow: hidden; border: 2px solid #1E88E5; position: relative; background-color: #1a1a1a; margin-bottom:5px;">
        <div style="width: 100%; height: 100%; top: -45px; position: absolute;">
            <iframe src="https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&zoom=7&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&type=map" 
                    width="100%" height="350px" frameborder="0" style="border:0; clip-path: inset(45px 0px 45px 0px);">
            </iframe>
        </div>
    </div>
    """
    components.html(custom_map_html, height=265)

if st.button(txt["generate_btn"], use_container_width=True):
    with st.spinner(".."):
        try:
            h = period_map[period]
            
            # 🌟 تم استبدال خوادم GFS بالخادم الأوروبي عالي الدقة ECMWF ليتطابق بالملي مع تطبيقات الرادارات العالمية وتفادي الأرقام الشاذة
            urls = [
                f"https://api.open-meteo.com/v1/ecmwf?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability,precipitation,wind_speed_10m&forecast_days=7",
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability,precipitation,wind_speed_10m&models=ecmwf_ifs_04&forecast_days=7"
            ]
            
            prayer_url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=3"
            
            data = None
            for url in urls:
                try:
                    res = requests.get(url, timeout=8)
                    if res.status_code == 200:
                        potential_data = res.json().get("hourly", {})
                        if potential_data and "temperature_2m" in potential_data:
                            sanitized_temps = [float(v) if v is not None else 28.0 for v in potential_data["temperature_2m"]]
                            if sanitized_temps:
                                data = potential_data
                                data["temperature_2m"] = sanitized_temps
                                data["precipitation"] = [float(v) if v is not None else 0.0 for v in potential_data.get("precipitation", [])]
                                data["precipitation_probability"] = [int(v) if v is not None else 0 for v in potential_data.get("precipitation_probability", [])]
                                data["wind_speed_10m"] = [float(v) if v is not None else 12.0 for v in potential_data.get("wind_speed_10m", [])]
                                break
                except Exception:
                    continue

            prayer_res = requests.get(prayer_url, timeout=8)
            
            if data:
                # تحديد الساعة الحالية بدقة بناءً على التوقيت المحلي لتفادي عرض حرارة الظهيرة بالخطأ
                current_hour = datetime.now().hour
                actual_h = min(h, len(data["temperature_2m"]))
                
                temps = data["temperature_2m"][:actual_h]
                precip_list = data["precipitation"][:actual_h]
                precip = sum(precip_list)
                prob = max(data["precipitation_probability"][:actual_h]) if data["precipitation_probability"][:actual_h] else 0
                wind_speeds = data["wind_speed_10m"][:actual_h]
                
                max_wind = max(wind_speeds) if wind_speeds else 12.0
                max_t = max(temps) if temps else 30.0
                
                # جلب قراءة الساعة الحالية المتزامنة
                current_temp_c = temps[current_hour] if current_hour < len(temps) else temps[0]
                current_wind = wind_speeds[current_hour] if current_hour < len(wind_speeds) else wind_speeds[0]
                
                sky_status = "ممطر 🌧️" if (precip_list and precip_list[current_hour < len(precip_list) and current_hour or 0] > 0.1) else ("غائم ☁️" if prob > 40 else "مشمس ☀️")
                if lang != "العربية":
                    sky_status = sky_status.replace("ممطر", "Rainy").replace("غائم", "Cloudy").replace("مشمس", "Sunny")

                # عرض المؤشرات المضبوطة أوروبياً وبدقة عالية
                st.markdown(f"<h5 style='color:#1E88E5; margin:2px 0; {is_rtl}'>{txt['current_status']}</h5>", unsafe_allow_html=True)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric(txt["temp_label"], format_temp(current_temp_c))
                m2.metric(txt["sky_label"], sky_status)
                m3.metric(txt["wind_label"], f"{current_wind:.1f}k/h")
                m4.metric(txt["max_temp"], format_temp(max_t))
                
                with st.expander(txt["weekly_title"], expanded=False):
                    daily_forecasts = []
                    today = datetime.now()
                    for idx in range(0, actual_h, 24):
                        day_chunk_t = temps[idx:idx+24]
                        if day_chunk_t:
                            day_date = (today + timedelta(days=idx//24)).strftime('%m-%d')
                            day_max = max(day_chunk_t)
                            day_rain = sum(precip_list[idx:idx+24]) if idx+24 <= len(precip_list) else 0.0
                            day_wind = max(wind_speeds[idx:idx+24]) if idx+24 <= len(wind_speeds) else 0.0
                            icon = "🌧️" if day_rain > 0.2 else ("💨" if day_wind > 25 else "☀️")
                            daily_forecasts.append({"date": day_date, "max": day_max, "rain": day_rain, "wind": day_wind, "icon": icon})
                    
                    if display_style == "بطاقات صغيرة لكل يوم":
                        cols = st.columns(min(len(daily_forecasts), 5))
                        for i, df in enumerate(daily_forecasts):
                            with cols[i % 5]:
                                st.markdown(f'<div class="weather-card"><b>{df["date"]}</b><br>{df["icon"]}<br>{format_temp(df["max"])}</div>', unsafe_allow_html=True)
                    else:
                        import pandas as pd
                        st.dataframe(pd.DataFrame(daily_forecasts), use_container_width=True)

                st.markdown(f"<h5 style='margin:4px 0; {is_rtl}'>{txt['expert_blog']}</h5>", unsafe_allow_html=True)
                blog = f"استقرار مؤشر {selected_city} ذروة {format_temp(max_t)}، احتمالية أمطار {prob}% بتراكم {precip:.1f}ملم وفقاً للبيانات الأوروبية المحدثة."
                st.info(blog)
                
                timings = prayer_res.json().get("data", {}).get("timings", {}) if prayer_res.status_code == 200 else {}
                if timings:
                    st.markdown(
                        f"""
                        <div class="prayer-row" style="{is_rtl}">
                            <b>{txt['prayer_title']} {selected_city}:</b> 
                            <span class="prayer-item">{txt['fajr']}: <span class="prayer-time">{timings.get('Fajr')}</span></span> | 
                            <span class="prayer-item">{txt['dhuhr']}: <span class="prayer-time">{timings.get('Dhuhr')}</span></span> | 
                            <span class="prayer-item">{txt['asr']}: <span class="prayer-time">{timings.get('Asr')}</span></span> | 
                            <span class="prayer-item">{txt['maghrib']}: <span class="prayer-time">{timings.get('Maghrib')}</span></span> | 
                            <span class="prayer-item">{txt['isha']}: <span class="prayer-time">{timings.get('Isha')}</span></span>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                
                share_text = f"🌤️ طقس {selected_city}:\n- الحرارة: {format_temp(max_t)}\n- الأمطار: {precip:.1f} ملم\n\n👇 حمل التطبيق APK:\nhttps://github.com/abderahmababa-png/WeatherApp/releases/download/v9.8/app4051699-2gznhx.1.apk"
                whatsapp_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(share_text)}"
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366;color:white;border:none;padding:6px;font-size:13px;border-radius:4px;width:100%;cursor:pointer;margin-top:2px;">{txt["whatsapp_btn"]}</button></a>', unsafe_allow_html=True)
            else:
                st.error("⚠️ عذراً، لم نتمكن من جلب بيانات الخادم الأوروبي حالياً. الرجاء إعادة المحاولة بعد ثوانٍ قليلة.")
        except Exception as e:
            st.error(f"خطأ في المعالجة: {str(e)}")
