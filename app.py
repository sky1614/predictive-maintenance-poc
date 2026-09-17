import streamlit as st
from branding import inject_theme, sidebar_brand, hero, feature_card_html, COLORS

st.set_page_config(page_title="NSAI — Data Intelligence for Industry & Infrastructure", layout="wide", page_icon="⚡")
inject_theme()
sidebar_brand()

hero(
    "Data Intelligence for Industry & Infrastructure",
    "Catch failures before they happen, using data you already have. No new sensors, "
    "no long deployment — proof on your own historical records before any commitment."
)

c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    st.page_link("pages/1_Predictive_Maintenance.py", label="Explore the platform  →", icon="⚙️", use_container_width=True)

st.markdown("###")
st.markdown("###")

st.markdown(f'<div class="section-title" style="text-align:center; font-size:14px;">Modules</div>', unsafe_allow_html=True)

row1 = st.columns(3)
with row1[0]:
    st.markdown(feature_card_html("⚙️", "Predictive Maintenance",
        "Flag equipment failures before they happen using maintenance logs you already keep. Tunable precision/recall, explainable flags.",
        "Manufacturing"), unsafe_allow_html=True)
    st.page_link("pages/1_Predictive_Maintenance.py", label="Open →")

with row1[1]:
    st.markdown(feature_card_html("💧", "Leak Zone Detection",
        "Flag high-probability leak zones from pipe age, pressure and flow data — no satellite survey or new metering required to start.",
        "Water / NRW"), unsafe_allow_html=True)
    st.page_link("pages/3_Water_Leakage.py", label="Open →")

with row1[2]:
    st.markdown(feature_card_html("📋", "Executive Summary",
        "The 10-second answer for a plant or utility owner — plain-₹ numbers and a traffic-light risk ranking, no model jargon.",
        "Both"), unsafe_allow_html=True)
    st.page_link("pages/0_Executive_Summary.py", label="Open →")

row2 = st.columns(3)
with row2[0]:
    st.markdown(feature_card_html("💰", "ROI Calculator",
        "Enter your own machine count and downtime cost, see potential savings live — no data upload required.",
        "Manufacturing"), unsafe_allow_html=True)
    st.page_link("pages/2_ROI_Calculator.py", label="Open →")

with row2[1]:
    st.markdown(feature_card_html("🛠️", "Work Orders",
        "Every flagged case becomes a trackable task automatically — status tracking and a CMMS/EAM-ready export.",
        "Both"), unsafe_allow_html=True)
    st.page_link("pages/4_Work_Orders.py", label="Open →")

with row2[2]:
    st.markdown(feature_card_html("🔎", "How it works",
        "Zero-hardware, backtest-on-existing-data method: prove it on your own history first, retainer only once value is shown.",
        ""), unsafe_allow_html=True)

st.markdown("###")
st.markdown("---")
st.caption("All figures shown in these modules are estimates based on public or synthetic demo data unless otherwise noted. Real figures are established by running this pipeline on your own historical records — free, before any commitment.")