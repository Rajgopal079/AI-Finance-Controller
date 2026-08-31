import streamlit as st
import json
from app.ai.controller import FinanceController
from app.data.loaders import DataLoader
from app.core.config import SYNTHETIC_DATA_DIR

def render_data_management(controller: FinanceController):
    st.title("💾 Data Management & Demo Dataset Loader")
    st.caption("Load synthetic benchmark datasets (100 or 500 records) or reset data.")

    loader = DataLoader(controller.db)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📁 Load Demo Dataset (100 Records)", type="primary"):
            demo_path = SYNTHETIC_DATA_DIR / "demo_100.json"
            if demo_path.exists():
                loader.load_from_json(str(demo_path))
                st.success("Loaded 100-record Demo Dataset into SQLite!")
                st.rerun()
            else:
                loader.generate_and_load(count=100, seed=42)
                st.success("Generated and loaded 100-record Demo Dataset!")
                st.rerun()

    with c2:
        if st.button("⚡ Load Benchmark Dataset (500 Records)"):
            test_path = SYNTHETIC_DATA_DIR / "test_500.json"
            if test_path.exists():
                loader.load_from_json(str(test_path))
                st.success("Loaded 500-record Benchmark Dataset into SQLite!")
                st.rerun()
            else:
                loader.generate_and_load(count=500, seed=101)
                st.success("Generated and loaded 500-record Benchmark Dataset!")
                st.rerun()

    with c3:
        if st.button("🔄 Generate Custom Dataset"):
            count = st.number_input("Record Count", min_value=50, max_value=1000, value=150)
            loader.generate_and_load(count=int(count), seed=123)
            st.success(f"Generated and loaded custom {count}-record dataset!")
            st.rerun()

    st.markdown("---")
    st.subheader("Current Database Entity Counts")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Invoices", len(controller.db.get_table_df("invoices")))
    col2.metric("Bank Txns", len(controller.db.get_table_df("bank_transactions")))
    col3.metric("Payments", len(controller.db.get_table_df("payments")))
    col4.metric("Settlements", len(controller.db.get_table_df("settlements")))
    col5.metric("Tax Lines", len(controller.db.get_table_df("tax_lines")))
