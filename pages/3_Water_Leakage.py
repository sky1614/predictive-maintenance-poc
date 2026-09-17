import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from branding import inject_theme, sidebar_brand, metric_card, badge, whatsapp_mockup, COLORS

st.set_page_config(page_title="NSAI — Water Leakage", layout="wide", page_icon="💧")
inject_theme()
sidebar_brand()

@st.cache_data
def load_data():
    results = pd.read_csv("leak_classifier_results.csv")
    sweep = pd.read_csv("leak_threshold_sweep.csv")
    importance = pd.read_csv("leak_feature_importance.csv", index_col=0)
    importance.columns = ["importance"]
    return results, sweep, importance

results, sweep, importance = load_data()

st.markdown(f'{badge("WATER / NRW")} &nbsp; {badge("Synthetic demo dataset", "warn")}', unsafe_allow_html=True)
st.title("Non-Revenue Water — Leak Zone Detection")
st.caption("Flag high-probability leak zones using data a utility already has — pipe age, pressure readings, night flow, complaints. No new sensors, no satellite survey required to start. Built on synthetic DMA-style data to demonstrate the method; real accuracy is established on your own network's records.")

st.sidebar.markdown('<div class="section-title">Detection Settings</div>', unsafe_allow_html=True)
threshold = st.sidebar.slider("Leak-risk threshold", 0.05, 0.90, 0.25, 0.05)
row = sweep.iloc[(sweep["threshold"] - threshold).abs().idxmin()]
st.sidebar.caption("Move the slider to trade off false alarms against catching more leak zones early.")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(metric_card("Precision", f"{row['precision']:.0%}", "of flagged zones, how many had a real leak"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("Recall", f"{row['recall']:.0%}", "of real leak zones, how many were caught"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("F1 Score", f"{row['f1']:.0%}", f"{int(row['tp'])} caught / {int(row['fp'])} false alarms"), unsafe_allow_html=True)

st.markdown("###")
left, right = st.columns([2, 1])
with left:
    st.markdown('<div class="section-title">Precision vs. Recall — the tunable tradeoff</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sweep["recall"], y=sweep["precision"], mode="lines+markers", name="Leak classifier", line=dict(color=COLORS["accent"], width=3)))
    fig.add_trace(go.Scatter(x=[row["recall"]], y=[row["precision"]], mode="markers", marker=dict(size=13, color=COLORS["danger"], symbol="x"), name="Current"))
    fig.update_layout(plot_bgcolor=COLORS["surface"], paper_bgcolor=COLORS["surface"], font_color=COLORS["text"],
                       xaxis_title="Recall", yaxis_title="Precision",
                       xaxis=dict(range=[0,1], gridcolor=COLORS["border"]), yaxis=dict(range=[0,1], gridcolor=COLORS["border"]),
                       legend=dict(orientation="h", y=-0.2), margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown('<div class="section-title">What drives a flag</div>', unsafe_allow_html=True)
    imp_sorted = importance.sort_values("importance", ascending=True)
    fig2 = go.Figure(go.Bar(x=imp_sorted["importance"], y=imp_sorted.index, orientation="h", marker_color=COLORS["accent"]))
    fig2.update_layout(plot_bgcolor=COLORS["surface"], paper_bgcolor=COLORS["surface"], font_color=COLORS["text"],
                        margin=dict(l=10, t=10), xaxis=dict(gridcolor=COLORS["border"]))
    st.plotly_chart(fig2, use_container_width=True)

st.markdown('<div class="section-title">Highest-risk zones at current threshold</div>', unsafe_allow_html=True)
flagged = results[results["predicted_probability"] >= threshold].copy()
flagged["status"] = flagged["actual_leak"].map({1: "✅ Real leak — caught", 0: "⚠️ False alarm"})
cols = ["zone_id", "pipe_age_years", "avg_pressure_bar", "night_flow_lps", "complaint_count_30d", "predicted_probability"]
if "likely_cause" in flagged.columns:
    cols.append("likely_cause")
if "explanation" in flagged.columns:
    cols.append("explanation")
cols.append("status")
top_flagged = flagged.sort_values("predicted_probability", ascending=False)
st.dataframe(top_flagged[cols].head(20), use_container_width=True)

if len(top_flagged) > 0 and "explanation" in top_flagged.columns:
    st.markdown("###")
    st.markdown('<div class="section-title">Alert preview — what a field crew supervisor would receive</div>', unsafe_allow_html=True)
    top = top_flagged.iloc[0]
    cause = top.get("likely_cause", "") or "Unclassified"
    body = (f"💧 Leak risk flagged: <b>{top['zone_id']}</b> at {top['predicted_probability']:.0%} confidence.<br>"
            f"Likely cause: {cause}.<br>Reason: {top['explanation']}.<br>Recommend field inspection this week.")
    st.markdown(whatsapp_mockup("Leak Detection Alert", body), unsafe_allow_html=True)

st.markdown("---")
st.caption("This demo runs on synthetic DMA-style data. On your utility's own pipeline network — meter readings, pressure logs, complaint records — the same pipeline produces a real backtest: which past leak zones this would have caught, and how early.")