import streamlit as st
import plotly.express as px
import pandas as pd
from app.ai.controller import FinanceController

def render_settlements(controller: FinanceController):
    st.title("💳 Settlement Intelligence & Q&A")
    st.caption("Analyze gateway settlements, track delays, and ask evidence-backed questions.")

    metrics = controller.settlement_analyzer.get_settlement_metrics()

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Settlements", metrics["total_count"])
    s2.metric("Settled Amount", f"₹{metrics['total_settled_amount']:,.2f}")
    s3.metric("Pending/Delayed", f"₹{metrics['pending_amount'] + metrics['delayed_amount']:,.2f}")
    s4.metric("Success Rate", f"{metrics['success_rate_pct']}%")

    st.markdown("---")
    c_chart, c_qa = st.columns([1, 1])

    with c_chart:
        st.subheader("Gateway Delay Rate Breakdown")
        gw_data = metrics["gateway_breakdown"]
        if gw_data:
            df_gw = pd.DataFrame([
                {"Gateway": k, "Delay Rate %": v["delay_rate_pct"], "Total Amount": v["total_amount"]}
                for k, v in gw_data.items()
            ])
            fig = px.bar(df_gw, x="Gateway", y="Delay Rate %", color="Gateway", title="Gateway Delay Percentage")
            st.plotly_chart(fig, use_container_width=True)

    with c_qa:
        st.subheader("Settlement Q&A Agent")
        q_input = st.text_input("Ask about settlements...", value="Which gateway has the most delays?")
        if st.button("Ask Q&A Agent"):
            ans = controller.settlement_analyzer.answer_settlement_question(q_input)
            st.success(f"**Answer:** {ans['answer']}")
            with st.expander("View Grounding Evidence"):
                st.json(ans["evidence"])
