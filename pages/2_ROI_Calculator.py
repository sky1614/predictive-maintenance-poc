import streamlit as st
import plotly.graph_objects as go
from branding import inject_theme, sidebar_brand, metric_card, badge, COLORS

st.set_page_config(page_title="NSAI — ROI Calculator", layout="wide", page_icon="📊")
inject_theme()
sidebar_brand()

st.markdown(f'{badge("MANUFACTURING")}', unsafe_allow_html=True)
st.title("Downtime ROI Calculator")
st.caption("Estimate based on typical catch rates from our predictive maintenance model. Real numbers are confirmed by running a backtest on your own maintenance data.")

col1, col2, col3 = st.columns(3)
with col1:
    machines = st.number_input("Number of machines", min_value=1, value=5)
with col2:
    downtime_hours = st.number_input("Avg downtime hours/month (per machine)", min_value=0.0, value=10.0)
with col3:
    cost_per_hour = st.number_input("Cost per hour of downtime (₹)", min_value=0, value=15000, step=1000)

RECALL = 0.80
HOURS_SAVED_PCT = 0.60

current_monthly_loss = machines * downtime_hours * cost_per_hour
potential_savings = current_monthly_loss * RECALL * HOURS_SAVED_PCT

st.markdown("###")
c1, c2 = st.columns(2)
with c1:
    st.markdown(metric_card("Current estimated monthly loss", f"₹{current_monthly_loss:,.0f}"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("Potential monthly savings", f"₹{potential_savings:,.0f}"), unsafe_allow_html=True)

st.markdown("###")
fig = go.Figure(go.Bar(
    x=["Current loss", "Loss after early detection"],
    y=[current_monthly_loss, current_monthly_loss - potential_savings],
    marker_color=[COLORS["text_muted"], COLORS["accent"]]
))
fig.update_layout(plot_bgcolor=COLORS["surface"], paper_bgcolor=COLORS["surface"], font_color=COLORS["text"],
                   yaxis_title="₹ / month", margin=dict(t=20), yaxis=dict(gridcolor=COLORS["border"]))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("This is an estimate, not a guarantee. Send us your last 6 months of maintenance logs and we'll run this on your real numbers, free.")