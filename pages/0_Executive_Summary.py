import pandas as pd
import streamlit as st
from branding import inject_theme, sidebar_brand, metric_card, badge, COLORS

st.set_page_config(page_title="NSAI — Executive Summary", layout="wide", page_icon="📋")
inject_theme()
sidebar_brand()

st.title("Executive Summary")
st.caption("The 10-second answer — no model jargon. Details are one click away on the other pages.")

tab1, tab2 = st.tabs(["🏭 Manufacturing", "💧 Water Leakage"])

# ---------------- MANUFACTURING ----------------
with tab1:
    results = pd.read_csv("classifier_results.csv")
    threshold = 0.35
    flagged = results[results["predicted_probability"] >= threshold].copy()

    st.markdown('<div class="section-title">Set your numbers</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        cost_per_hour = st.number_input("Cost per hour of downtime (₹)", min_value=0, value=15000, step=1000, key="m_cost")
    with c2:
        avg_downtime_hrs = st.number_input("Avg hours of downtime per failure event", min_value=1.0, value=6.0, key="m_hrs")

    n_machines_at_risk = 0
    if "machine_id" in results.columns:
        machine_avg_risk = results.groupby("machine_id")["predicted_probability"].mean()
        high_cut = machine_avg_risk.quantile(0.80)
        n_machines_at_risk = (machine_avg_risk >= high_cut).sum()
    n_events_caught = len(flagged[flagged["actual_failure"]==1]) if "actual_failure" in flagged.columns else len(flagged)
    avoidable_loss = n_events_caught * avg_downtime_hrs * cost_per_hour * 0.6  # 60% of downtime avoidable via early catch

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(metric_card("Machines needing attention", f"{n_machines_at_risk}", "high-risk tier, out of 20 tracked"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Failures catchable early", f"{n_events_caught}", "based on backtest on this dataset"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("Estimated avoidable loss", f"₹{avoidable_loss:,.0f}", "this period, if acted on"), unsafe_allow_html=True)

    st.markdown("###")
    st.markdown('<div class="section-title">Machine Health Ranking</div>', unsafe_allow_html=True)
    st.caption("Illustrative grouping for this public dataset — on your real machines, this ranks your actual equipment over time.")

    if "machine_id" in results.columns:
        ranking = results.groupby("machine_id").agg(
            avg_risk=("predicted_probability", "mean"),
            max_risk=("predicted_probability", "max"),
            flagged_readings=("predicted_probability", lambda x: (x >= threshold).sum()),
        ).reset_index().sort_values("avg_risk", ascending=False)

        def risk_light(v, hi, med):
            if v >= hi: return "🔴 High"
            if v >= med: return "🟡 Medium"
            return "🟢 Low"
        hi_cut, med_cut = ranking["avg_risk"].quantile(0.80), ranking["avg_risk"].quantile(0.50)
        ranking["status"] = ranking["avg_risk"].apply(lambda v: risk_light(v, hi_cut, med_cut))
        ranking["avg_risk"] = (ranking["avg_risk"]*100).round(1).astype(str) + "%"
        ranking["max_risk"] = (ranking["max_risk"]*100).round(1).astype(str) + "%"
        st.dataframe(ranking[["machine_id","status","avg_risk","max_risk","flagged_readings"]].head(10),
                     use_container_width=True, hide_index=True)

# ---------------- WATER LEAKAGE ----------------
with tab2:
    leak_results = pd.read_csv("leak_classifier_results.csv")
    threshold = 0.25
    leak_flagged = leak_results[leak_results["predicted_probability"] >= threshold].copy()

    st.markdown('<div class="section-title">Set your numbers</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        tariff = st.number_input("Water tariff (₹ per kilolitre)", min_value=0.0, value=25.0, key="w_tariff")
    with c2:
        avg_loss_kl_day = st.number_input("Avg water lost per leak (KL/day, undetected)", min_value=1.0, value=15.0, key="w_kl")

    zone_avg_risk = leak_results.groupby("zone_id")["predicted_probability"].mean()
    zone_high_cut = zone_avg_risk.quantile(0.80)
    n_zones_at_risk = (zone_avg_risk >= zone_high_cut).sum()
    n_real_leaks_caught = len(leak_flagged[leak_flagged["actual_leak"]==1])
    days_undetected_avoided = 20  # assume catching a leak ~20 days earlier on average
    avoidable_water_loss_value = n_real_leaks_caught * avg_loss_kl_day * days_undetected_avoided * tariff

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(metric_card("Zones needing inspection", f"{n_zones_at_risk}", "high-risk tier, out of 30 tracked"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Leaks catchable early", f"{n_real_leaks_caught}", "based on backtest on this dataset"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("Estimated avoidable water loss value", f"₹{avoidable_water_loss_value:,.0f}", "this period, if acted on"), unsafe_allow_html=True)

    st.markdown("###")
    st.markdown('<div class="section-title">Zone Risk Ranking</div>', unsafe_allow_html=True)
    zone_ranking = leak_results.groupby("zone_id").agg(
        avg_risk=("predicted_probability", "mean"),
        max_risk=("predicted_probability", "max"),
        flagged_readings=("predicted_probability", lambda x: (x >= threshold).sum()),
    ).reset_index().sort_values("avg_risk", ascending=False)

    def risk_light(v, hi, med):
        if v >= hi: return "🔴 High"
        if v >= med: return "🟡 Medium"
        return "🟢 Low"
    zhi_cut, zmed_cut = zone_ranking["avg_risk"].quantile(0.80), zone_ranking["avg_risk"].quantile(0.50)
    zone_ranking["status"] = zone_ranking["avg_risk"].apply(lambda v: risk_light(v, zhi_cut, zmed_cut))
    zone_ranking["avg_risk"] = (zone_ranking["avg_risk"]*100).round(1).astype(str) + "%"
    zone_ranking["max_risk"] = (zone_ranking["max_risk"]*100).round(1).astype(str) + "%"
    st.dataframe(zone_ranking[["zone_id","status","avg_risk","max_risk","flagged_readings"]].head(10),
                 use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("All figures on this page are estimates based on public/synthetic demo data. Real figures are established by running this pipeline on your own historical records — free, before any commitment.")