import streamlit as st
import plotly.express as px
import pandas as pd
from app.ai.controller import FinanceController

def render_cash(controller: FinanceController):
    st.title("📈 Forward Cash Forecaster")
    st.caption("Transparent rule-based forward liquidity projections based on bank deposits, expected receivables, and pending settlements.")

    forecast_data = controller.cash_forecaster.generate_forecast()

    c1, c2, c3 = st.columns(3)
    c1.metric("Current Cash", f"₹{forecast_data['current_cash_position']:,.2f}")
    c2.metric("Pending Settlements", f"₹{forecast_data['pending_settlements']:,.2f}")
    c3.metric("30-Day Inflows", f"₹{forecast_data['forecasts']['30_day']['expected_inflow']:,.2f}")

    st.markdown("---")
    
    # Forecast chart
    f_dict = forecast_data["forecasts"]
    chart_df = pd.DataFrame([
        {"Horizon": "Current", "Cash": forecast_data["current_cash_position"]},
        {"Horizon": "7-Day", "Cash": f_dict["7_day"]["projected_cash"]},
        {"Horizon": "14-Day", "Cash": f_dict["14_day"]["projected_cash"]},
        {"Horizon": "30-Day", "Cash": f_dict["30_day"]["projected_cash"]}
    ])
    fig = px.line(chart_df, x="Horizon", y="Cash", markers=True, title="Projected Cash Trajectory (INR)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Major Expected Cash Drivers")
    drivers = forecast_data.get("major_drivers", [])
    if drivers:
        st.dataframe(pd.DataFrame(drivers))
    else:
        st.info("No unpaid receivables driving cash forecasts.")
