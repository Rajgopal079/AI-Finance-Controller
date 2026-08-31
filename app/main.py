git add .import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from app.ai.controller import FinanceController
from app.ui.dashboard import render_dashboard
from app.ui.reconciliation import render_reconciliation
from app.ui.exceptions import render_exceptions
from app.ui.settlements import render_settlements
from app.ui.cash import render_cash
from app.ui.tax import render_tax
from app.ui.ai_analyst import render_ai_analyst
from app.ui.audit import render_audit
from app.ui.data_management import render_data_management

st.set_page_config(
    page_title="FINCTRL AI — Finance Operations Controller",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #0B0F19;
        color: #F8FAFC;
    }
    .stMetric {
        background-color: #1E293B;
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #334155;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_controller():
    return FinanceController()

def main():
    controller = get_controller()

    st.sidebar.title("FINCTRL AI")
    st.sidebar.caption("Finance Operations Controller")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        options=[
            "🎯 Control Room",
            "🔄 Reconciliation",
            "🚨 Exception Triage",
            "💳 Settlements",
            "📈 Forward Cash",
            "🧾 Tax Matching",
            "🤖 AI Analyst",
            "📜 Audit Trail",
            "💾 Data Management"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Local AI Model:** `{controller.investigator.provider.model_name if hasattr(controller.investigator.provider, 'model_name') else 'Fallback'}`")
    st.sidebar.markdown(f"**AI Online:** `{'YES' if controller.investigator.provider.is_available() else 'NO (Deterministic)'}`")

    if page == "🎯 Control Room":
        render_dashboard(controller)
    elif page == "🔄 Reconciliation":
        render_reconciliation(controller)
    elif page == "🚨 Exception Triage":
        render_exceptions(controller)
    elif page == "💳 Settlements":
        render_settlements(controller)
    elif page == "📈 Forward Cash":
        render_cash(controller)
    elif page == "🧾 Tax Matching":
        render_tax(controller)
    elif page == "🤖 AI Analyst":
        render_ai_analyst(controller)
    elif page == "📜 Audit Trail":
        render_audit(controller)
    elif page == "💾 Data Management":
        render_data_management(controller)

if __name__ == "__main__":
    main()
