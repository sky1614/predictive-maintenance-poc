import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from branding import inject_theme, sidebar_brand, metric_card, badge, COLORS

st.set_page_config(page_title="NSAI — Work Orders", layout="wide", page_icon="🛠️")
inject_theme()
sidebar_brand()

st.title("Work Orders")
st.caption("Every flagged case becomes a trackable task automatically — no manual re-entry into a maintenance log. This is the record that would sync to your CMMS/EAM system via API.")

if "work_orders" not in st.session_state:
    st.session_state.work_orders = []

def priority_from_prob(p):
    if p >= 0.7: return "🔴 Critical"
    if p >= 0.4: return "🟠 High"
    return "🟡 Medium"

def make_wo_id(prefix, n):
    return f"{prefix}-{datetime.now().strftime('%y%m')}-{n:04d}"

tab1, tab2 = st.tabs(["🏭 Manufacturing", "💧 Water Leakage"])

# ---------------- MANUFACTURING ----------------
with tab1:
    results = pd.read_csv("classifier_results.csv")
    threshold = 0.35
    flagged = results[results["predicted_probability"] >= threshold].copy()
    flagged = flagged.sort_values("predicted_probability", ascending=False).head(10).reset_index(drop=True)

    st.markdown('<div class="section-title">Open items ready for a work order</div>', unsafe_allow_html=True)

    for i, row in flagged.iterrows():
        wo_id = make_wo_id("WO-MFG", i+1)
        ftype = row.get("predicted_failure_type", "") or "Anomaly"
        explanation = row.get("explanation", "Model-flagged deviation")
        with st.container():
            c1, c2, c3, c4 = st.columns([2, 3, 2, 2])
            c1.markdown(f"**{wo_id}**<br><span style='font-size:12px;color:{COLORS['text_muted']}'>{row.get('machine_id','—')}</span>", unsafe_allow_html=True)
            c2.markdown(f"**{ftype}**<br><span style='font-size:12px;color:{COLORS['text_muted']}'>{explanation}</span>", unsafe_allow_html=True)
            c3.markdown(priority_from_prob(row["predicted_probability"]))
            if c4.button("Create Work Order", key=f"mfg_wo_{i}"):
                due = (datetime.now() + timedelta(days=3 if row["predicted_probability"]>=0.7 else 7)).strftime("%d %b %Y")
                st.session_state.work_orders.append({
                    "Work Order ID": wo_id, "Vertical": "Manufacturing", "Asset": row.get("machine_id","—"),
                    "Issue": ftype, "Reason": explanation, "Priority": priority_from_prob(row["predicted_probability"]),
                    "Status": "Open", "Due Date": due, "Created": datetime.now().strftime("%d %b %Y %H:%M")
                })
                st.success(f"{wo_id} created")
            st.markdown("<hr style='margin:4px 0; border-color:#E4E7EC'>", unsafe_allow_html=True)

# ---------------- WATER LEAKAGE ----------------
with tab2:
    leak_results = pd.read_csv("leak_classifier_results.csv")
    threshold = 0.25
    lflagged = leak_results[leak_results["predicted_probability"] >= threshold].copy()
    lflagged = lflagged.sort_values("predicted_probability", ascending=False).head(10).reset_index(drop=True)

    st.markdown('<div class="section-title">Open items ready for a work order</div>', unsafe_allow_html=True)

    for i, row in lflagged.iterrows():
        wo_id = make_wo_id("WO-H2O", i+1)
        cause = row.get("likely_cause", "") or "Unclassified"
        explanation = row.get("explanation", "Model-flagged deviation")
        with st.container():
            c1, c2, c3, c4 = st.columns([2, 3, 2, 2])
            c1.markdown(f"**{wo_id}**<br><span style='font-size:12px;color:{COLORS['text_muted']}'>{row['zone_id']}</span>", unsafe_allow_html=True)
            c2.markdown(f"**{cause}**<br><span style='font-size:12px;color:{COLORS['text_muted']}'>{explanation}</span>", unsafe_allow_html=True)
            c3.markdown(priority_from_prob(row["predicted_probability"]))
            if c4.button("Create Work Order", key=f"h2o_wo_{i}"):
                due = (datetime.now() + timedelta(days=3 if row["predicted_probability"]>=0.7 else 7)).strftime("%d %b %Y")
                st.session_state.work_orders.append({
                    "Work Order ID": wo_id, "Vertical": "Water Leakage", "Asset": row["zone_id"],
                    "Issue": cause, "Reason": explanation, "Priority": priority_from_prob(row["predicted_probability"]),
                    "Status": "Open", "Due Date": due, "Created": datetime.now().strftime("%d %b %Y %H:%M")
                })
                st.success(f"{wo_id} created")
            st.markdown("<hr style='margin:4px 0; border-color:#E4E7EC'>", unsafe_allow_html=True)

# ---------------- TRACKER ----------------
st.markdown("###")
st.markdown('<div class="section-title">Work Order Tracker</div>', unsafe_allow_html=True)

if not st.session_state.work_orders:
    st.caption("No work orders created yet — click \"Create Work Order\" above on any flagged item.")
else:
    wo_df = pd.DataFrame(st.session_state.work_orders)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(metric_card("Total open work orders", f"{(wo_df['Status']=='Open').sum()}"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Critical priority", f"{(wo_df['Priority'].str.contains('Critical')).sum()}"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("Total tracked", f"{len(wo_df)}"), unsafe_allow_html=True)

    st.markdown("###")
    for i in wo_df.index:
        current_status = wo_df.loc[i, "Status"]
        new_status = st.selectbox(f"{wo_df.loc[i,'Work Order ID']} — {wo_df.loc[i,'Asset']} — {wo_df.loc[i,'Issue']}",
                                   ["Open", "In Progress", "Resolved"],
                                   index=["Open","In Progress","Resolved"].index(current_status),
                                   key=f"status_{i}")
        st.session_state.work_orders[i]["Status"] = new_status

    st.markdown("###")
    st.dataframe(pd.DataFrame(st.session_state.work_orders), use_container_width=True, hide_index=True)

    csv = pd.DataFrame(st.session_state.work_orders).to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export to CMMS/EAM (CSV)", csv, "nsai_work_orders.csv", "text/csv")
    st.caption("This export mirrors the format a real CMMS/EAM integration would receive via API — same structure, automated instead of manual.")