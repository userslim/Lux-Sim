import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import math

# Page configuration
st.set_page_config(
    page_title="LuxSim Pro - Singapore Indoor & Outdoor Lighting Calculator",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the PayPal Button and Headers
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #1E88E5; text-align: center; margin-bottom: 1rem; }
    .sub-header { font-size: 1.5rem; color: #424242; margin-bottom: 1rem; }
    .success-box { background-color: #d4edda; padding: 1rem; border-radius: 0.5rem; border-left: 0.5rem solid #28a745; }
    
    /* PayPal Button Styling */
    .paypal-button {
        display: inline-block;
        background-color: #FFC439;
        color: #003087;
        padding: 10px 20px;
        text-decoration: none;
        font-weight: bold;
        border-radius: 5px;
        text-align: center;
        width: 100%;
    }
    .paypal-button:hover {
        background-color: #f2ba36;
        color: #003087;
    }
</style>
""", unsafe_allow_html=True)

# --- STANDARDS DATA ---
INDOOR_STANDARDS = {
    "Residential": {"Living Room": 150, "Bedroom": 100, "Kitchen": 300, "Bathroom": 100, "Study Room": 300},
    "Office": {"Open Plan Office": 400, "Private Office": 500, "Conference Room": 500, "Reception": 300},
    "Commercial": {"Retail Shop": 500, "Supermarket": 750, "Restaurant": 200, "Parking Lot (Indoor)": 75}
}

OUTDOOR_STANDARDS = {
    "Residential Estates": {"Linkway": 50, "Void Deck": 100, "Corridor (Open)": 30},
    "Parks & Recreation": {"Park Path": 20, "Fitness Corner": 100, "Playground": 50},
    "Sports Facilities": {"Basketball Court": 300, "Tennis Court": 300, "Futsal Court": 200}
}

# --- LIGHT SPECIFICATIONS ---
INDOOR_LIGHTS = {
    "Residential": [
        {"wattage": 9, "lumens": 800, "cri": 80, "color_temp": "3000K", "type": "LED Bulb", "ip_rating": "IP20", "beam_angle": 120},
        {"wattage": 15, "lumens": 1400, "cri": 80, "color_temp": "4000K", "type": "LED Downlight", "ip_rating": "IP44", "beam_angle": 90}
    ],
    "Office": [
        {"wattage": 18, "lumens": 1800, "cri": 85, "color_temp": "4000K", "type": "LED Panel", "ip_rating": "IP20", "beam_angle": 110},
        {"wattage": 36, "lumens": 3600, "cri": 85, "color_temp": "4000K", "type": "LED Panel", "ip_rating": "IP20", "beam_angle": 110}
    ]
}

OUTDOOR_LIGHTS = {
    "Residential Estates": [
        {"wattage": 24, "lumens": 2400, "cri": 80, "color_temp": "3000K", "type": "LED Bollard", "ip_rating": "IP65", "beam_angle": 360, "mounting_height": 1},
        {"wattage": 50, "lumens": 5000, "cri": 80, "color_temp": "4000K", "type": "LED Post Top", "ip_rating": "IP65", "beam_angle": 180, "mounting_height": 5}
    ],
    "Sports Facilities": [
        {"wattage": 200, "lumens": 20000, "cri": 80, "color_temp": "5000K", "type": "LED Sports Flood", "ip_rating": "IP66", "beam_angle": 45, "mounting_height": 10}
    ]
}

# --- LOGIC FUNCTIONS ---
def calculate_energy_cost(total_wattage, hours, days, rate):
    kwh_year = (total_wattage / 1000) * hours * days
    return {'yearly_cost': round(kwh_year * rate, 2), 'daily_cost': round((total_wattage/1000)*hours*rate, 2)}

def calculate_indoor_lights(L, W, H, req_lux, mf=0.8, uf=0.7):
    area = L * W
    total_lumens = (req_lux * area) / (mf * uf)
    results = []
    for cat, lights in INDOOR_LIGHTS.items():
        for light in lights:
            num = math.ceil(total_lumens / light['lumens'])
            actual = (num * light['lumens'] * mf * uf) / area
            results.append({**light, 'num_lights': num, 'total_wattage': num * light['wattage'], 'actual_lux': round(actual, 1), 'environment': 'Indoor', 'category': cat, 'spacing': round(math.sqrt(area/num), 2)})
    return sorted(results, key=lambda x: x['total_wattage']), area

def calculate_outdoor_lights(L, W, req_lux, area_type, mf=0.7):
    area = L * W
    uf = 0.5
    total_lumens = (req_lux * area) / (mf * uf)
    results = []
    for cat, lights in OUTDOOR_LIGHTS.items():
        for light in lights:
            cov_rad = max(0.1, light['mounting_height'] * math.tan(math.radians(light['beam_angle']/4)))
            cov_area = math.pi * (cov_rad**2)
            num = max(math.ceil(area / cov_area), math.ceil(total_lumens / light['lumens']))
            actual = (num * light['lumens'] * mf * uf) / area
            results.append({**light, 'num_lights': num, 'total_wattage': num * light['wattage'], 'actual_lux': round(actual, 1), 'environment': 'Outdoor', 'category': cat, 'spacing': round(math.sqrt(area/num), 2), 'uniformity': 0.4})
    return sorted(results, key=lambda x: x['total_wattage']), area

# --- MAIN APP ---
def main():
    st.markdown("<h1 class='main-header'>💡 LuxSim Pro</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        env = st.radio("Environment", ["Indoor", "Outdoor"])
        L = st.number_input("Length (m)", 1.0, 200.0, 10.0)
        W = st.number_input("Width (m)", 1.0, 200.0, 8.0)
        
        if env == "Indoor":
            H = st.number_input("Ceiling Height (m)", 2.0, 10.0, 2.8)
            cat = st.selectbox("Category", list(INDOOR_STANDARDS.keys()))
            room = st.selectbox("Room", list(INDOOR_STANDARDS[cat].keys()))
            lux = INDOOR_STANDARDS[cat][room]
        else:
            cat = st.selectbox("Category", list(OUTDOOR_STANDARDS.keys()))
            room = st.selectbox("Area", list(OUTDOOR_STANDARDS[cat].keys()))
            lux = OUTDOOR_STANDARDS[cat][room]

        cost_rate = st.number_input("SGD/kWh", 0.1, 1.0, 0.25)
        run_calc = st.button("Calculate", type="primary", use_container_width=True)
        
        st.write("---")
        # --- PAYPAL SECTION ---
        st.markdown("### ☕ Support this Project")
        st.markdown("""
            <a href="https://www.paypal.com/ncp/payment/RUPD9EAL4MPFA" class="paypal-button" target="_blank">
                Donate via PayPal
            </a>
        """, unsafe_allow_html=True)
        st.caption("Help keep the servers running!")

    if run_calc:
        if env == "Indoor":
            results, area = calculate_indoor_lights(L, W, H, lux)
        else:
            results, area = calculate_outdoor_lights(L, W, lux, room)

        if results:
            best = results[0]
            costs = calculate_energy_cost(best['total_wattage'], 10, 365, cost_rate)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Area", f"{area} m²")
            c2.metric("Target Lux", f"{lux}")
            c3.metric("Fixtures", f"{best['num_lights']}")
            c4.metric("Est. Annual Cost", f"S${costs['yearly_cost']}")

            df = pd.DataFrame(results).replace([np.inf, -np.inf], 0).fillna(0)
            st.markdown("### 📊 All Options")
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.info(f"💡 Pro-tip: Spacing for these fixtures should be approximately {best['spacing']}m apart.")

if __name__ == "__main__":
    main()

