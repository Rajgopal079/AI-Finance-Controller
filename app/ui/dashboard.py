import streamlit as st
import plotly.express as px
import pandas as pd
from app.ai.controller import FinanceController
from app.data.loaders import DataLoader

def render_dashboard(controller: FinanceController):
    st.title("FINCTRL AI — Control Room")
    st.caption("Reconcile. Investigate. Forecast. Control.")

    if st.button("🚀 Run Finance Controller Loop", type="primary"):
        with st.spinner("Processing reconciliation, exception triage, forward forecast, and health metrics..."):
            pipeline_data = controller.run_controller_pipeline()
            st.session_state["pipeline_data"] = pipeline_data
            st.success("Finance Controller loop executed successfully!")

    pipeline = st.session_state.get("pipeline_data")
    if not pipeline:
        pipeline = controller.run_controller_pipeline()
        st.session_state["pipeline_data"] = pipeline

    health = pipeline["health_score"]
    recon = pipeline["recon_metrics"]
    exceptions = pipeline["exceptions"]
    settlements = pipeline["settlement_metrics"]
    cash = pipeline["cash_forecast"]

    # Top Health Score Banner
    st.markdown("---")
    col_score, col_subs = st.columns([1, 2])
    with col_score:
        score_val = health["overall_health_score"]
        score_color = "#10B981" if score_val >= 85 else ("#F59E0B" if score_val >= 70 else "#EF4444")
        st.markdown(f"""
            <div style="background-color: #1E293B; border-radius: 12px; padding: 24px; text-align: center; border-left: 8px solid {score_color};">
                <h3 style="color: #94A3B8; margin:0;">FINANCE HEALTH SCORE</h3>
                <h1 style="color: {score_color}; font-size: 54px; margin: 10px 0;">{score_val} <span style="font-size: 24px; color: #64748B;">/ 100</span></h1>
                <p style="color: #CBD5E1; margin:0; font-size: 13px;">{health['formula_explanation']}</p>
            </div>
        """, unsafe_allow_html=True)

    with col_subs:
        subs = health["sub_scores"]
        df_subs = pd.DataFrame(list(subs.items()), columns=["Category", "Score"])
        fig_bar = px.bar(df_subs, x="Category", y="Score", color="Score",
                         color_continuous_scale="Viridis", range_y=[0, 100],
                         title="Health Metric Breakdown")
        fig_bar.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)

    # Main KPI Cards
    st.markdown("---")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Total Records", recon["total_records"])
    m2.metric("Match Rate", f"{recon['match_rate_pct']}%", delta=f"{recon['matched_records']} Matched")
    m3.metric("Exceptions", len(exceptions), delta_color="inverse")
    m4.metric("Pending Settlements", f"₹{settlements['pending_amount'] + settlements['delayed_amount']:,.0f}")
    m5.metric("Current Cash", f"₹{cash['current_cash_position']:,.0f}")
    m6.metric("30-Day Proj Cash", f"₹{cash['forecasts']['30_day']['projected_cash']:,.0f}")

    # Attention Required Feed
    st.markdown("---")
    st.subheader("⚠️ Attention Required — Priority Exception Feed")
    
    criticals = [e for e in exceptions if e["severity"] == "CRITICAL"]
    highs = [e for e in exceptions if e["severity"] == "HIGH"]
    mediums = [e for e in exceptions if e["severity"] == "MEDIUM"]

    if criticals:
        for c in criticals:
            st.error(f"**[CRITICAL EXCEPTION]** {c['reason']} — Discrepancy Amount: **₹{c['financial_amount']:,.2f}** | Next Step: {c['suggested_next_step']}")
    if highs:
        for h in highs:
            st.warning(f"**[HIGH PRIORITY]** {h['reason']} — Amount: **₹{h['financial_amount']:,.2f}** | Next Step: {h['suggested_next_step']}")
    if not criticals and not highs:
        st.info("No critical or high severity exceptions detected. Operations are stable.")
