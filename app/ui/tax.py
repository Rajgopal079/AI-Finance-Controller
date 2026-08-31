import streamlit as st
import pandas as pd
from app.ai.controller import FinanceController

def render_tax(controller: FinanceController):
    st.title("🧾 Tax-Line Matcher")
    st.caption("Deterministic GST/CGST/SGST/IGST tax calculation verification comparing Recorded vs Expected Tax.")

    tax_res = controller.tax_matcher.run_tax_matching()

    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Total Tax Lines", tax_res["total_tax_lines"])
    t2.metric("Tax Matched Rate", f"{tax_res['match_rate_pct']}%")
    t3.metric("Discrepancies Count", tax_res["discrepancy_count"], delta_color="inverse")
    t4.metric("Total Discrepancy", f"₹{tax_res['total_discrepancy_amount']:,.2f}")

    st.markdown("---")
    details = tax_res.get("details", [])
    if details:
        df = pd.DataFrame(details)
        st.dataframe(df[["tax_line_id", "invoice_id", "customer_name", "tax_type", "taxable_amount", "expected_tax", "recorded_tax", "discrepancy_amount", "status"]], use_container_width=True)
    else:
        st.info("No tax records loaded.")
