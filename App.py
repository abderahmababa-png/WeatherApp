import streamlit as st
import requests
import os
import streamlit.components.v1 as components
import urllib.parse
from datetime import datetime, timedelta

# 1. كود الحقن التجميلي المكثف لتقليل المسافات العمودية، منع مشاكل اللمس وإخفاء أزرار GitHub الافتراضية
st.markdown(
    """
    <style>
    /* إخفاء شريط الأدوات العلوية والأزرار الافتراضية (Fork, GitHub icon, Menu) */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    footer {
        visibility: hidden !important;
    }
    
    /* ضبط الهيكل والتجاوب لمنع مشاكل اللمس */
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
        "fajr":
