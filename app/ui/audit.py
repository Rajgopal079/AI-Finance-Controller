import streamlit as st
import pandas as pd
from app.ai.controller import FinanceController

def render_audit(controller: FinanceController):
    st.title("📜 Tamper-Evident Audit Trail & Cryptographic Verification")
    st.caption("Immutable system log tracking all automated decisions, AI investigations, and human approvals secured with SHA-256 hash chaining.")

    if st.button("🛡️ Verify Audit Chain Integrity", type="primary"):
        res = controller.audit_logger.verify_audit_chain()
        if res["is_valid"]:
            st.success(f"✓ Cryptographic Audit Chain Valid — {res['total_events']} events verified. 0 integrity violations detected.")
        else:
            st.error(f"❌ AUDIT TAMPERING DETECTED! Found {len(res['violations'])} integrity violations:\n" + "\n".join(res["violations"]))

    audit_logs = controller.audit_logger.get_audit_logs(limit=200)

    if not audit_logs:
        st.info("No audit logs recorded yet.")
        return

    df = pd.DataFrame(audit_logs)
    
    st.markdown(f"**Total Logged Events: {len(df)}**")

    # CSV Download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Audit Trail (CSV)", data=csv, file_name="finctrl_audit_trail.csv", mime="text/csv")

    st.dataframe(df[["audit_id", "timestamp", "user_action", "record_id", "agent_action", "decision", "human_approval", "previous_hash", "current_hash"]], use_container_width=True)
