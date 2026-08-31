import streamlit as st
import json
from app.ai.controller import FinanceController

def render_ai_analyst(controller: FinanceController):
    st.title("🤖 Tool-Using Finance Controller Agent")
    st.caption("Natural language financial assistant powered by database tool execution and local structured reasoning.")

    st.markdown("""
        **Example Tool Queries:**
        - *Which unresolved invoice has the largest financial exposure and why?*
        - *What is the current 30-day cash forecast?*
        - *Which gateway has the worst settlement delay rate?*
        - *Show customer billing history for CUST-1000*
        - *Check GST tax reconciliation status*
    """)

    q = st.text_input("Enter your financial query:", placeholder="e.g. Which unresolved invoice has the largest exposure?")

    if st.button("Run AI Finance Agent", type="primary") and q:
        with st.spinner("Analyzing query, selecting DB tool, and synthesizing evidence..."):
            agent_res = controller.agent.process_query(q)
            
            st.markdown(f"**Selected Tool:** `{agent_res['selected_tool']}`")
            if agent_res["tool_args"]:
                st.caption(f"Tool Arguments: `{json.dumps(agent_res['tool_args'])}`")

            st.success(f"**Agent Answer:**\n{agent_res['answer']}")

            with st.expander("🔍 View Database Tool Output"):
                st.json(agent_res["tool_output"])
