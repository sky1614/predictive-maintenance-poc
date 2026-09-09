import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="ROI Calculator", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #1C1F24; color: #E8E6E1; }
    .metric-box { background-color: #262B33; border: 1px solid #3A4149;
        border-radius: 4px; padding: 16px 20px; }
    .metric-label { font-size: 0.75rem; text-transform: uppercase; color: #9AA3AD; }
    .metric-value { font-size: 1.9rem; font-weight: 600; color: #F0A93B; }
</style>
""", unsafe_allow_html=True)

st.title("Downtime ROI Calculator")
st.caption("Estimate based on typical catch rates from our predictive maintenance model. Real numbers are confirmed by running a backtest on your own maintenance data.")

col1, col2, col3 = st.columns(3)
with col1:
    machines = st.number_input("Number of machines", min_value=1, value=5)
with col2:
    downtime_hours = st.number_input("Avg downtime hours/month (per machine)", min_value=0.0, value=10.0)
with col3:
    cost_per_hour = st.number_input("Cost per hour of downtime (₹)", min_value=0, value=15000, step=1000)

RECALL = 0.80       # from your backtest — % of failures caught early
HOURS_SAVED_PCT = 0.60  # assume early catch avoids ~60% of downtime for that event

current_monthly_loss = machines * downtime_hours * cost_per_hour
potential_savings = current_monthly_loss * RECALL * HOURS_SAVED_PCT

st.markdown("###")
c1, c2 = st.columns(2)
with c1:
    st.markdown(f"""<div class="metric-box"><div class="metric-label">Current estimated monthly loss</div>
    <div class="metric-value">₹{current_monthly_loss:,.0f}</div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-box"><div class="metric-label">Potential monthly savings</div>
    <div class="metric-value">₹{potential_savings:,.0f}</div></div>""", unsafe_allow_html=True)

fig = go.Figure(go.Bar(
    x=["Current loss", "Loss after early detection"],
    y=[current_monthly_loss, current_monthly_loss - potential_savings],
    marker_color=["#5B93C5", "#F0A93B"]
))
fig.update_layout(plot_bgcolor="#1C1F24", paper_bgcolor="#1C1F24", font_color="#E8E6E1",
                   yaxis_title="₹ / month", margin=dict(t=20))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("This is an estimate, not a guarantee. Send us your last 6 months of maintenance logs and we'll run this on your real numbers, free.")