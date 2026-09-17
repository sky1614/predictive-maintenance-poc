import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from branding import inject_theme, sidebar_brand, metric_card, badge, whatsapp_mockup, COLORS

st.set_page_config(page_title="NSAI — Predictive Maintenance", layout="wide", page_icon="⚙️")
inject_theme()
sidebar_brand()

@st.cache_data
def load_data():
    results = pd.read_csv("classifier_results.csv")
    sweep = pd.read_csv("classifier_threshold_sweep.csv")
    unsup_sweep = pd.read_csv("unsupervised_threshold_sweep.csv")
    importance = pd.read_csv("feature_importance.csv", index_col=0)
    importance.columns = ["importance"]
    return results, sweep, unsup_sweep, importance

results, sweep, unsup_sweep, importance = load_data()

st.markdown(f'{badge("MANUFACTURING")} &nbsp; {badge("Public demo dataset", "warn")}', unsafe_allow_html=True)
st.title("Predictive Maintenance")
st.caption("Catch equipment failures before they happen, using data you already log — no new sensors required. Built on the public AI4I 2020 dataset to demonstrate the method; swap in your own maintenance history for real, defensible results.")

st.sidebar.markdown('<div class="section-title">Detection Settings</div>', unsafe_allow_html=True)
mode = st.sidebar.radio("Model", ["Supervised classifier (labeled history)", "Unsupervised (no labels yet)"])

if mode.startswith("Supervised"):
    threshold = st.sidebar.slider("Classification threshold", 0.05, 0.90, 0.35, 0.05)
    row = sweep.iloc[(sweep["threshold"] - threshold).abs().idxmin()]
else:
    lo, hi = float(unsup_sweep["iso_threshold"].min()), float(unsup_sweep["iso_threshold"].max())
    threshold = st.sidebar.slider("Anomaly score threshold", lo, hi, (lo + hi) / 2)
    row = unsup_sweep.iloc[(unsup_sweep["iso_threshold"] - threshold).abs().idxmin()]

st.sidebar.caption("Move the slider to trade off false alarms against catching more failures.")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(metric_card("Precision", f"{row['precision']:.0%}", "of flagged failures, how many were real"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("Recall", f"{row['recall']:.0%}", "of real failures, how many were caught"), unsafe_allow_html=True)
with c3:
    f1 = row.get("f1", 2*row['precision']*row['recall']/(row['precision']+row['recall']+1e-9))
    sub = f"{int(row['tp'])} caught / {int(row['fp'])} false alarms" if "tp" in row else "based on anomaly score"
    st.markdown(metric_card("F1 Score", f"{f1:.0%}", sub), unsafe_allow_html=True)

st.markdown("###")
left, right = st.columns([2, 1])
with left:
    st.markdown('<div class="section-title">Precision vs. Recall — the tunable tradeoff</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sweep["recall"], y=sweep["precision"], mode="lines+markers", name="Supervised", line=dict(color=COLORS["accent"], width=3)))
    fig.add_trace(go.Scatter(x=unsup_sweep["recall"], y=unsup_sweep["precision"], mode="lines+markers", name="Unsupervised", line=dict(color="#98A2B3", width=2, dash="dot")))
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

st.markdown('<div class="section-title">Sample flagged cases at current threshold</div>', unsafe_allow_html=True)
if mode.startswith("Supervised"):
    flagged = results[results["predicted_probability"] >= threshold].copy()
    flagged["status"] = flagged["actual_failure"].map({1: "✅ Real failure — caught", 0: "⚠️ False alarm"})
    has_explain = "explanation" in flagged.columns
    cols = ["Air temperature [K]", "Process temperature [K]", "Torque [Nm]", "Tool wear [min]", "predicted_probability"]
    if "predicted_failure_type" in flagged.columns:
        cols.append("predicted_failure_type")
    if has_explain:
        cols.append("explanation")
    cols.append("status")
    top_flagged = flagged.sort_values("predicted_probability", ascending=False)
    st.dataframe(top_flagged[cols].head(20), use_container_width=True)

    if len(top_flagged) > 0 and has_explain:
        st.markdown("###")
        st.markdown('<div class="section-title">Alert preview — what a floor manager would receive</div>', unsafe_allow_html=True)
        top = top_flagged.iloc[0]
        ftype = top.get("predicted_failure_type", "") or "Anomaly"
        body = (f"⚠️ Machine flagged: <b>{ftype}</b> risk at "
                f"{top['predicted_probability']:.0%} confidence.<br>Reason: {top['explanation']}.<br>"
                f"Recommend inspection before next shift.")
        st.markdown(whatsapp_mockup("Predictive Maintenance Alert", body), unsafe_allow_html=True)
else:
    st.caption("Switch to the supervised view to see individual flagged cases with outcomes.")

st.markdown("---")
st.caption("This demo runs on the public AI4I 2020 dataset. On your own machine data, the same pipeline produces a retroactive backtest: which of your real past failures this would have caught, and how many days in advance.")