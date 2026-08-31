import streamlit as st
import json
import pandas as pd
from app.ai.controller import FinanceController

def render_exceptions(controller: FinanceController):
    st.title("🚨 Exception Triage & AI Investigation")
    st.caption("Investigate financial exceptions with evidence-backed local AI and human-in-the-loop controls.")

    exc_df = controller.db.get_table_df("exceptions")
    if exc_df.empty:
        st.info("No open exceptions found. Re-run pipeline or load dataset.")
        return

    # Filters
    f1, f2 = st.columns(2)
    with f1:
        sev_filter = st.multiselect("Severity", options=["CRITICAL", "HIGH", "MEDIUM", "LOW"], default=["CRITICAL", "HIGH", "MEDIUM", "LOW"])
    with f2:
        status_filter = st.multiselect("Status", options=["OPEN", "UNDER_REVIEW", "RESOLVED", "REJECTED", "ESCALATED"], default=["OPEN", "UNDER_REVIEW", "ESCALATED"])

    filtered_exc = exc_df[exc_df["severity"].isin(sev_filter) & exc_df["status"].isin(status_filter)]

    st.markdown(f"**{len(filtered_exc)} Exception Records Displayed**")

    for _, exc in filtered_exc.iterrows():
        exc_id = exc["exception_id"]
        sev = exc["severity"]
        exc_type = exc["type"]
        amt = exc["financial_amount"]
        status = exc["status"]
        reason = exc["reason"]
        
        badge_color = "#EF4444" if sev == "CRITICAL" else ("#F59E0B" if sev == "HIGH" else "#3B82F6")
        
        st.markdown(f"""
            <div style="border-left: 6px solid {badge_color}; background: #0F172A; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <span style="background:{badge_color}; color:white; padding: 2px 8px; border-radius: 4px; font-weight:bold; font-size:12px;">{sev}</span>
                <span style="color:#94A3B8; margin-left: 10px; font-weight:bold;">{exc_id} | {exc_type}</span>
                <span style="float:right; color:#F8FAFC; font-weight:bold;">Status: {status} | Amt: ₹{amt:,.2f}</span>
                <p style="color:#CBD5E1; margin-top:8px;">{reason}</p>
            </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1])
        with col_left:
            if st.button(f"🔍 AI Investigation ({exc_id})", key=f"ai_{exc_id}"):
                with st.spinner("Analyzing evidence package via Local AI..."):
                    ai_result = controller.investigate_exception_by_id(exc_id)
                    st.session_state[f"ai_res_{exc_id}"] = ai_result

        with col_right:
            btn_app, btn_rej, btn_esc = st.columns(3)
            with btn_app:
                if st.button("✅ Approve", key=f"app_{exc_id}"):
                    controller.update_exception_status(exc_id, "RESOLVED", "HUMAN_APPROVAL")
                    st.success(f"Exception {exc_id} Approved & Persisted to DB!")
                    st.rerun()

            with btn_rej:
                if st.button("❌ Reject", key=f"rej_{exc_id}"):
                    controller.update_exception_status(exc_id, "REJECTED", "HUMAN_REJECTION")
                    st.warning(f"Exception {exc_id} Rejected & Persisted to DB!")
                    st.rerun()

            with btn_esc:
                if st.button("🚨 Escalate", key=f"esc_{exc_id}"):
                    controller.update_exception_status(exc_id, "ESCALATED", "HUMAN_ESCALATION")
                    st.error(f"Exception {exc_id} Escalated & Persisted to DB!")
                    st.rerun()

        ai_res = st.session_state.get(f"ai_res_{exc_id}")
        if ai_res:
            st.info(f"**AI Investigator Analysis:**\n- **Classification:** {ai_res.get('classification')}\n- **Confidence:** {ai_res.get('confidence')}\n- **Reasoning:** {ai_res.get('reason')}\n- **Risk:** {ai_res.get('risk_assessment')}\n- **Recommended Action:** {ai_res.get('recommended_action')}")

        st.markdown("---")
