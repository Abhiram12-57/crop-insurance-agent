import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from data.weather_generator import generate_mock_weather_data
from core.drought_logic import check_drought
from core.payout_engine import PayoutEngine
from core.notification import generate_sms
from ai.rainfall_predictor import RainfallPredictor
from utils.logger import get_logger

logger = get_logger(__name__)

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Crop Insurance Payout Agent",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZATION ---
if 'df' not in st.session_state:
    st.session_state.df = None
if 'payout_engine' not in st.session_state:
    st.session_state.payout_engine = PayoutEngine()
if 'predictor' not in st.session_state:
    st.session_state.predictor = RainfallPredictor()
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = []
if 'notifications' not in st.session_state:
    st.session_state.notifications = []

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3060/3060377.png", width=100)
    st.title("Admin Configuration")
    
    st.header("1. Data Generation")
    num_days = st.slider("Historical Days", 30, 90, 60, help="Number of days for mock data")
    num_farmers = st.slider("Number of Farmers", 5, 50, 10)
    
    if st.button("Generate Weather Data"):
        with st.spinner("Generating Satellite & Weather Data..."):
            st.session_state.df = generate_mock_weather_data(days=num_days, num_farmers=num_farmers)
            st.session_state.predictor.train(st.session_state.df)
            st.success("Data Generated & AI Model Trained!")
            
    st.header("2. Drought Thresholds")
    rain_threshold = st.slider("Rainfall Threshold (mm)", 0.0, 20.0, 5.0, 0.5, help="Minimum daily rainfall required")
    consecutive_days_threshold = st.slider("Consecutive Dry Days", 3, 14, 5)
    moisture_threshold = st.slider("Critical Soil Moisture (%)", 10.0, 40.0, 20.0, 1.0)

# --- MAIN DASHBOARD ---
st.title("🌾 Autonomous Crop Insurance Payout Agent")
st.markdown("""
This AI agent monitors mock satellite/weather data in real-time. 
When drought conditions are detected (based on adjustable thresholds), it automatically triggers insurance payouts to affected farmers via Smart Contracts.
""")

if st.session_state.df is None:
    st.info("👈 Please generate weather data from the sidebar to start the simulation.")
    st.stop()

# Layout: Main metrics
col1, col2, col3, col4 = st.columns(4)
total_farmers = len(st.session_state.df['Farmer ID'].unique())
ledger_df = st.session_state.payout_engine.get_ledger()
total_payouts_made = len(ledger_df)
total_amount_disbursed = ledger_df['Amount (INR)'].sum() if total_payouts_made > 0 else 0

col1.metric("Monitored Farmers", total_farmers)
col2.metric("Total Payouts Made", total_payouts_made)
col3.metric("Total Disbursed (₹)", f"₹{total_amount_disbursed:,.2f}")
if 'latest_risk' in st.session_state:
    col4.metric("Avg Drought Risk", f"{st.session_state.latest_risk}%")
else:
    col4.metric("Avg Drought Risk", "N/A")

st.divider()

# Select a farmer to monitor
farmers = st.session_state.df['Farmer ID'].unique()
selected_farmer = st.selectbox("Select Farmer to Monitor:", farmers)

farmer_data = st.session_state.df[st.session_state.df['Farmer ID'] == selected_farmer].sort_values('Date')

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Weather & Satellite Data", "🤖 AI Forecast", "⚙️ Run Payout Agent", "📜 Payout Ledger"])

with tab1:
    st.subheader(f"Historical Weather Data for {selected_farmer}")
    
    col_graph1, col_graph2 = st.columns(2)
    with col_graph1:
        chart_rain = alt.Chart(farmer_data).mark_bar(color='#1E88E5').encode(
            x='Date:T',
            y='Rainfall (mm):Q',
            tooltip=['Date', 'Rainfall (mm)']
        ).properties(title="Daily Rainfall (mm)", height=300)
        
        rule = alt.Chart(pd.DataFrame({'threshold': [rain_threshold]})).mark_rule(color='red', strokeDash=[5, 5]).encode(y='threshold:Q')
        st.altair_chart(chart_rain + rule, use_container_width=True)
        
    with col_graph2:
        chart_moist = alt.Chart(farmer_data).mark_line(color='#43A047').encode(
            x='Date:T',
            y='Soil Moisture (%):Q',
            tooltip=['Date', 'Soil Moisture (%)']
        ).properties(title="Soil Moisture (%)", height=300)
        
        rule_moist = alt.Chart(pd.DataFrame({'threshold': [moisture_threshold]})).mark_rule(color='red', strokeDash=[5, 5]).encode(y='threshold:Q')
        st.altair_chart(chart_moist + rule_moist, use_container_width=True)

with tab2:
    st.subheader("AI Rainfall Forecast (Next 5 Days)")
    st.markdown("Uses a trained Linear Regression model to predict upcoming rainfall based on current temperature and soil moisture trends.")
    
    latest_temp = farmer_data.iloc[-1]['Temperature (°C)']
    latest_moist = farmer_data.iloc[-1]['Soil Moisture (%)']
    
    predictions = st.session_state.predictor.predict_next_days(
        current_temp=latest_temp, 
        current_moisture=latest_moist, 
        days=5
    )
    
    if predictions:
        future_dates = [pd.Timestamp.now().date() + pd.Timedelta(days=i+1) for i in range(5)]
        pred_df = pd.DataFrame({"Date": future_dates, "Predicted Rainfall (mm)": predictions})
        
        risk = st.session_state.predictor.calculate_drought_risk(predictions, rain_threshold)
        st.session_state.latest_risk = risk
        
        col_risk1, col_risk2 = st.columns([1, 2])
        with col_risk1:
            st.metric("Drought Risk Level", f"{risk}%")
            if risk > 60:
                st.error("High Risk of Drought in coming days.")
            elif risk > 30:
                st.warning("Moderate Risk of Drought.")
            else:
                st.success("Low Risk. Normal conditions expected.")
                
        with col_risk2:
            st.bar_chart(pred_df.set_index('Date')['Predicted Rainfall (mm)'])
    else:
        st.warning("AI Model not trained. Please generate data first.")

with tab3:
    st.subheader("Autonomous Payout Simulation")
    st.write("Run the agent to check thresholds for the selected farmer and trigger smart contracts if necessary.")
    
    if st.button("▶️ Run Agent for Selected Farmer", type="primary"):
        with st.spinner("Agent analyzing satellite and weather endpoints..."):
            import time
            time.sleep(1) # Simulate API delay
            
            is_drought, reason = check_drought(
                st.session_state.df, 
                selected_farmer, 
                rain_threshold, 
                moisture_threshold, 
                consecutive_days_threshold
            )
            
            if is_drought:
                st.error(f"🚨 DROUGHT DETECTED: {reason}")
                
                success, result = st.session_state.payout_engine.trigger_payout(selected_farmer, reason)
                
                if success:
                    st.success(f"💸 PAYOUT TRIGGERED SUCCESSFULY! Transaction ID: {result}")
                    sms = generate_sms(selected_farmer, result, 5000)
                    st.info(f"📱 Automated Notification Sent:\n\n{sms}")
                    st.session_state.notifications.append(sms)
                else:
                    st.warning(f"⚠️ PAYOUT BLOCKED: {result}")
            else:
                st.success(f"✅ NO DROUGHT DETECTED: {reason}")
                st.info("No payout required.")

with tab4:
    st.subheader("Smart Contract / Payout Ledger")
    ledger = st.session_state.payout_engine.get_ledger()
    if not ledger.empty:
        st.dataframe(ledger, use_container_width=True)
    else:
        st.info("No payouts triggered yet.")

if st.session_state.notifications:
    with st.expander("Recent Automated Notifications", expanded=False):
        for notif in reversed(st.session_state.notifications[-5:]):
            st.toast(notif)
            st.text(notif)
            st.divider()
