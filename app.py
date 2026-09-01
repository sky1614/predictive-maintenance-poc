"""
Predictive Maintenance POC — Dashboard
Run locally with:  streamlit run app.py
Expects these CSVs in the same folder (exported from the Colab notebook):
  - classifier_results.csv
  - classifier_threshold_sweep.csv
  - feature_importance.csv
  - unsupervised_threshold_sweep.csv
"""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Predictive Maintenance POC", layout="wide")

# ---------- Theme (industrial: graphite + amber alert accent) ----------
st.markdown("""
<style>
    .stApp { background-color: #1C1F24; color: #E8E6E1; }
    .metric-box {
        background-color: #262B33; border: 1px solid #3A4149;
        border-radius: 4px; padding: 16px 20px; text-align: left;
    }
    .metric-label { font-size: 0.75rem; letter-spacing: 0.06em; text-transform: uppercase;
        color: #9AA3AD; margin-bottom: 4px; }
    .metric-value { font-size: 1.9rem; font-weight: 600; color: #F0A93B; }
    .metric-sub { font-size: 0.8rem; color: #7C858E; }
</style>
""", unsafe_allow_html=True)

# ---------- Load data ----------
@st.cache_data
def load_data():
    results = pd.read_csv("classifier_results.csv")
    sweep = pd.read_csv("classifier_threshold_sweep.csv")
    unsup_sweep = pd.read_csv("unsupervised_threshold_sweep.csv")
    importance = pd.read_csv("feature_importance.csv", index_col=0)
    importance.columns = ["importance"]
    return results, sweep, unsup_sweep, importance

results, sweep, unsup_sweep, importance = load_data()

st.title("Predictive Maintenance — Capability Demo")
st.caption("Built on public data (AI4I 2020) to demonstrate the method. Swap in a plant's own maintenance history to get real, defensible results.")

# ---------- Sidebar controls ----------
st.sidebar.header("Detection settings")
mode = st.sidebar.radio(
    "Model",
    ["Supervised classifier (has labeled failure history)", "Unsupervised — no labels yet"],
)

if mode.startswith("Supervised"):
    threshold = st.sidebar.slider("Classification threshold", 0.05, 0.90, 0.35, 0.05)
    row = sweep.iloc[(sweep["threshold"] - threshold).abs().idxmin()]
else:
    lo, hi = float(unsup_sweep["iso_threshold"].min()), float(unsup_sweep["iso_threshold"].max())
    threshold = st.sidebar.slider("Anomaly score threshold", lo, hi, (lo + hi) / 2)
    row = unsup_sweep.iloc[(unsup_sweep["iso_threshold"] - threshold).abs().idxmin()]

st.sidebar.markdown("---")
st.sidebar.caption("Move the slider to trade off false alarms against catching more failures — this is the exact dial we'd tune together on your data.")

# ---------- KPI row ----------
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class="metric-box"><div class="metric-label">Precision</div>
    <div class="metric-value">{row['precision']:.0%}</div>
    <div class="metric-sub">of flagged failures, how many were real</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-box"><div class="metric-label">Recall</div>
    <div class="metric-value">{row['recall']:.0%}</div>
    <div class="metric-sub">of real failures, how many were caught</div></div>""", unsafe_allow_html=True)
with col3:
    if "tp" in row:
        sub = f"{int(row['tp'])} caught / {int(row['fp'])} false alarms"
    else:
        sub = "based on anomaly score"
    f1 = row.get("f1", 2 * row['precision'] * row['recall'] / (row['precision'] + row['recall'] + 1e-9))
    st.markdown(f"""<div class="metric-box"><div class="metric-label">F1 Score</div>
    <div class="metric-value">{f1:.0%}</div>
    <div class="metric-sub">{sub}</div></div>""", unsafe_allow_html=True)

st.markdown("###")

# ---------- Precision/Recall curve ----------
left, right = st.columns([2, 1])
with left:
    st.subheader("Precision vs. Recall — the tunable tradeoff")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sweep["recall"], y=sweep["precision"], mode="lines+markers",
                              name="Supervised classifier", line=dict(color="#F0A93B", width=3)))
    fig.add_trace(go.Scatter(x=unsup_sweep["recall"], y=unsup_sweep["precision"], mode="lines+markers",
                              name="Unsupervised (no labels)", line=dict(color="#5B93C5", width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=[row["recall"]], y=[row["precision"]], mode="markers",
                              marker=dict(size=14, color="#E8E6E1", symbol="x"),
                              name="Current setting"))
    fig.update_layout(
        plot_bgcolor="#1C1F24", paper_bgcolor="#1C1F24", font_color="#E8E6E1",
        xaxis_title="Recall (failures caught)", yaxis_title="Precision (alarms that were real)",
        xaxis=dict(range=[0, 1], gridcolor="#3A4149"), yaxis=dict(range=[0, 1], gridcolor="#3A4149"),
        legend=dict(orientation="h", y=-0.2), margin=dict(t=10),
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("What drives a flag")
    imp_sorted = importance.sort_values("importance", ascending=True)
    fig2 = go.Figure(go.Bar(
        x=imp_sorted["importance"], y=imp_sorted.index, orientation="h",
        marker_color="#F0A93B"
    ))
    fig2.update_layout(
        plot_bgcolor="#1C1F24", paper_bgcolor="#1C1F24", font_color="#E8E6E1",
        margin=dict(l=10, t=10), xaxis=dict(gridcolor="#3A4149"),
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Flagged cases table ----------
st.subheader("Sample flagged cases at current threshold")
if mode.startswith("Supervised"):
    flagged = results[results["predicted_probability"] >= threshold].copy()
    flagged["status"] = flagged["actual_failure"].map({1: "✅ Real failure — caught", 0: "⚠️ False alarm"})
    show_cols = ["Air temperature [K]", "Process temperature [K]", "Torque [Nm]",
                 "Tool wear [min]", "predicted_probability", "status"]
    st.dataframe(flagged[show_cols].sort_values("predicted_probability", ascending=False).head(20),
                 use_container_width=True)
else:
    st.caption("Switch to the supervised classifier view to see individual flagged cases with outcomes.")

st.markdown("---")
st.caption(
    "This demo runs on the public AI4I 2020 dataset. On a prospect's own machine data, "
    "the same pipeline produces a retroactive backtest: which of their real past failures "
    "this would have caught, and how many days in advance."
)