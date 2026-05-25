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
    st.markdown(f"<p style='color:#1E88E5; font-weight:bold; margin-bottom:5px;'>🗺️ ر
