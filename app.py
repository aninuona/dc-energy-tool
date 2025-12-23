import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# --- CONFIG ---
st.set_page_config(page_title="NetZero DC Navigator", layout="wide")

# --- UI ---
st.markdown("""
    <style>

    /* Sidebar */
    [data-testid="stSidebarUserContent"] { padding-top: 1rem !important; }
    .stNumberInput, .stSlider { margin-bottom: -10px !important; }

    /* Metric Cards */
    [data-testid="stMetricValue"] { font-weight: 600; color: #00d2ff; }
    .metric-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Background */
    .stApp { background-color: #0b0e14; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: FACILITY INPUTS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2906/2906236.png", width=60)
    st.title("DC Configurator")
    
    with st.expander("🔌 Power Loads (kW)", expanded=True):
        it_load = st.number_input("IT Equipment Load", value=1000)
        cooling_load = st.number_input("Cooling System Load", value=400)
        lighting_misc = st.number_input("Misc (UPS/Lighting)", value=100)
        
    with st.expander("💧 Environmental", expanded=True):
        water_usage = st.number_input("Annual Water (Liters)", value=500000)
        emission_factor = st.slider("Grid Carbon (kg/kWh)", 0.1, 1.0, 0.45)
        
    with st.expander("📐 Physical Space", expanded=True):
        sq_ft = st.number_input("Facility Size (Sq Ft)", value=10000)
        num_racks = st.number_input("Number of Racks", value=50)

# --- LOGIC ENGINE ---
total_facility_power = it_load + cooling_load + lighting_misc
pue = total_facility_power / it_load if it_load > 0 else 0
dcie = (1 / pue) * 100 if pue > 0 else 0
wue = water_usage / (it_load * 8760) if it_load > 0 else 0 # L/kWh
cue = (total_facility_power * 8760 * emission_factor) / (it_load * 8760) # kgCO2/kWh
density = it_load / num_racks if num_racks > 0 else 0

# --- MAIN DASHBOARD ---
st.title("🌐 NetZero Data Center Navigator")
st.markdown("#### Real-time Efficiency & Intensity Analysis")

# Top Level KPI Row
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("PUE (Efficiency)", f"{pue:.2f}x", delta="-0.02" if pue < 1.6 else "0.05", delta_color="inverse")
with c2: st.metric("WUE (Water)", f"{wue:.3f} L/kWh")
with c3: st.metric("CUE (Carbon)", f"{cue:.2f} kg/kWh")
with c4: st.metric("Density", f"{density:.1f} kW/Rack")

# Tabs for progressive disclosure
tab1, tab2, tab3 = st.tabs(["📊 Energy Profile", "🌿 Sustainability", "📈 Capacity Planning"])

with tab1:
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("Power Usage Effectiveness (PUE)")
        fig_pue = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = pue,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Efficiency Score"},
            gauge = {
                'axis': {'range': [1, 3], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#00d2ff"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "#333",
                'steps': [
                    {'range': [1, 1.2], 'color': '#27ae60'},
                    {'range': [1.2, 1.5], 'color': '#f1c40f'},
                    {'range': [1.5, 3], 'color': '#e74c3c'}],
            }))
        fig_pue.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white", 'family': "Poppins"})
        st.plotly_chart(fig_pue, use_container_width=True)

    with col_right:
        st.subheader("Load Breakdown")
        labels = ['IT Load', 'Cooling', 'Misc']
        values = [it_load, cooling_load, lighting_misc]
        fig_pie = px.pie(names=labels, values=values, hole=0.6, 
                         color_discrete_sequence=['#00d2ff', '#004e92', '#333'])
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=True, font={'color': "white"})
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.subheader("Sustainability Benchmark")
    # Simulation for Monthly Carbon Footprint
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    carbon_data = np.random.normal(cue * 100, 10, 12)
    fig_line = px.line(x=months, y=carbon_data, title="Monthly CO2 Intensity (Simulated Trends)")
    fig_line.update_traces(line_color='#2ecc71', mode='lines+markers')
    fig_line.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_line, use_container_width=True)

with tab3:
    st.subheader("Capacity vs. PUE Heatmap")
    # Data Center PUE usually drops as Load Factor increases
    loads = np.linspace(20, 100, 10)
    pue_trend = 1.2 + (1 / (loads/50))
    fig_trend = px.area(x=loads, y=pue_trend, labels={'x': 'IT Load Factor (%)', 'y': 'PUE'}, 
                        title="Operational Efficiency Curve")
    fig_trend.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")
st.caption("v1.2 | Data Center Energy Intensity Tool | [GitHub: aninuona](https://github.com/aninuona/)")
