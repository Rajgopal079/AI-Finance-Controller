import streamlit as st
import pandas as pd
from app.ai.controller import FinanceController

def render_reconciliation(controller: FinanceController):
    st.title("🔄 Multi-Source Reconciliation Engine")
    st.caption("Deterministic match scoring comparing Invoices against Bank Transactions & Payments.")

    recon_df = controller.db.get_table_df("reconciliations")
    invoices_df = controller.db.get_table_df("invoices")
    txns_df = controller.db.get_table_df("bank_transactions")

    if recon_df.empty:
        st.warning("No reconciliation results available. Run the controller pipeline from the Control Room.")
        return

    # Filter controls
    col1, col2 = st.columns([1, 2])
    with col1:
        status_filter = st.multiselect("Filter by Status", options=list(recon_df["status"].unique()), default=list(recon_df["status"].unique()))

    filtered_df = recon_df[recon_df["status"].isin(status_filter)] if status_filter else recon_df

    st.markdown(f"**Showing {len(filtered_df)} of {len(recon_df)} Reconciled Records**")

    for _, row in filtered_df.iterrows():
        status = row["status"]
        score = row["match_score"]
        inv_id = row["invoice_id"]
        txn_id = row["transaction_id"]
        notes = row["notes"]

        color = "green" if status == "MATCHED" else ("orange" if status == "PARTIAL_MATCH" else "red")
        
        with st.expander(f"{status} | Invoice: {inv_id} <---> Txn: {txn_id} | Score: {score:.2f}"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Invoice ID:** {inv_id}")
                if not invoices_df.empty and inv_id:
                    inv_match = invoices_df[invoices_df["invoice_id"] == inv_id]
                    if not inv_match.empty:
                        st.json(inv_match.iloc[0].to_dict())
            with c2:
                st.write(f"**Bank Txn ID:** {txn_id}")
                if not txns_df.empty and txn_id:
                    txn_match = txns_df[txns_df["transaction_id"] == txn_id]
                    if not txn_match.empty:
                        st.json(txn_match.iloc[0].to_dict())
            st.info(f"**Calculated Evidence Notes:** {notes}")
