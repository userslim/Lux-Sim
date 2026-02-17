# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="LuxSim Pro - Singapore Lighting Calculator",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #1E88E5;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# Singapore Standards for Illuminance (SS 531:2014)
SINGAPORE_STANDARDS = {
    "Residential": {
        "Living Room": 150,
        "Bedroom": 100,
        "Kitchen": 300,
        "Bathroom": 100,
        "Study Room": 300,
        "Corridor": 75
    },
    "Office": {
        "Open Plan Office": 400,
        "Private Office": 500,
        "Conference Room": 500,
        "Reception": 300,
        "Corridor": 100
    },
    "Commercial": {
        "Retail Shop": 500,
        "Supermarket": 750,
        "Restaurant": 200,
        "Lobby": 300,
        "Parking Lot": 75
    },
    "Industrial": {
        "Warehouse": 150,
        "Factory Floor": 300,
        "Laboratory": 500,
        "Control Room": 300
    },
    "Educational": {
        "Classroom": 300,
        "Library": 500,
        "Laboratory": 500,
        "Auditorium": 200
    }
}

# LED Light Specifications (based on common Singapore market options)
LED_LIGHTS = {
    "Residential": [
        {"wattage": 9, "lumens": 800, "cri": 80, "color_temp": "3000K", "type": "LED Bulb"},
        {"wattage": 12, "lumens": 1100, "cri": 80, "color_temp": "3000K", "type": "LED Bulb"},
        {"wattage": 15, "lumens": 1400, "cri": 80, "color_temp": "4000K", "type": "LED Downlight"},
        {"wattage": 18, "lumens": 1700, "cri": 85, "color_temp": "4000K", "type": "LED Downlight"}
    ],
    "Office": [
        {"wattage": 18, "lumens": 1800, "cri": 85, "color_temp": "4000K", "type": "LED Panel"},
        {"wattage": 24, "lumens": 2400, "cri": 85, "color_temp": "4000K", "type": "LED Panel"},
        {"wattage": 36, "lumens": 3600, "cri": 85, "color_temp": "4000K", "type": "LED Panel"},
        {"wattage": 48, "lumens": 4800, "cri": 85, "color_temp": "5000K", "type": "LED Panel"}
    ],
    "Commercial": [
        {"wattage": 20, "lumens": 2000, "cri": 85, "color_temp": "4000K", "type": "LED Track Light"},
        {"wattage": 30, "lumens": 3000, "cri": 85, "color_temp": "4000K", "type": "LED Track Light"},
        {"wattage": 40, "lumens": 4000, "cri": 90, "color_temp": "5000K", "type": "LED High Bay"},
        {"wattage": 50, "lumens": 5000, "cri": 90, "color_temp": "5000K", "type": "LED High Bay"}
    ],
    "Industrial": [
        {"wattage": 50, "lumens": 5000, "cri": 80, "color_temp": "5000K", "type": "LED High Bay"},
        {"wattage": 100, "lumens": 10000, "cri": 80, "color_temp": "5000K", "type": "LED High Bay"},
        {"wattage": 150, "lumens": 15000, "cri": 80, "color_temp": "5000K", "type": "LED High Bay"},
        {"wattage": 200, "lumens": 20000, "cri": 80, "color_temp": "5000K", "type": "LED High Bay"}
    ],
    "Educational": [
        {"wattage": 18, "lumens": 1800, "cri": 85, "color_temp": "4000K", "type": "LED Panel"},
        {"wattage": 24, "lumens": 2400, "cri": 85, "color_temp": "4000K", "type": "LED Panel"},
        {"wattage": 36, "lumens": 3600, "cri": 85, "color_temp": "4000K", "type": "LED Panel"}
    ]
}

def calculate_lights(area_length, area_width, room_height, required_lux, light_efficacy=100, maintenance_factor=0.8, utilization_factor=0.7):
    """
    Calculate number of lights required using Lumen Method
    
    Parameters:
    area_length, area_width (float): Room dimensions in meters
    room_height (float): Height of room in meters
    required_lux (float): Required illuminance in lux
    light_efficacy (float): Light output per watt (lumens/watt)
    maintenance_factor (float): MF (typically 0.8)
    utilization_factor (float): UF (typically 0.5-0.8)
    
    Returns:
    dict: Dictionary containing calculation results
    """
    area = area_length * area_width
    total_lumens_required = (required_lux * area) / (maintenance_factor * utilization_factor)
    
    # Calculate for different wattage options
    results = []
    for category, lights in LED_LIGHTS.items():
        for light in lights:
            lumens_per_light = light['lumens']
            num_lights = np.ceil(total_lumens_required / lumens_per_light)
            
            # Calculate spacing based on room dimensions
            max_spacing = room_height * 1.5  # Maximum recommended spacing
            area_per_light = area / num_lights
            spacing = np.sqrt(area_per_light)
            
            # Calculate actual lux achieved
            actual_lux = (num_lights * lumens_per_light * maintenance_factor * utilization_factor) / area
            
            results.append({
                'category': category,
                'light_type': light['type'],
                'wattage': light['wattage'],
                'lumens': lumens_per_light,
                'num_lights': int(num_lights),
                'total_wattage': int(num_lights * light['wattage']),
                'actual_lux': round(actual_lux, 1),
                'spacing': round(spacing, 2),
                'cri': light['cri'],
                'color_temp': light['color_temp']
            })
    
    # Sort by number of lights and total wattage
    results.sort(key=lambda x: (x['num_lights'], x['total_wattage']))
    
    return results, area

def calculate_energy_cost(total_wattage, hours_per_day=10, days_per_year=365, cost_per_kwh=0.25):
    """
    Calculate energy consumption and cost
    
    Parameters:
    total_wattage (float): Total wattage of all lights
    hours_per_day (float): Operating hours per day
    days_per_year (float): Operating days per year
    cost_per_kwh (float): Cost per kilowatt-hour in SGD
    
    Returns:
    dict: Energy cost calculations
    """
    daily_consumption = (total_wattage / 1000) * hours_per_day  # kWh
    monthly_consumption = daily_consumption * 30
    yearly_consumption = daily_consumption * days_per_year
    
    daily_cost = daily_consumption * cost_per_kwh
    monthly_cost = monthly_consumption * cost_per_kwh
    yearly_cost = yearly_consumption * cost_per_kwh
    
    return {
        'daily_consumption': round(daily_consumption, 2),
        'monthly_consumption': round(monthly_consumption, 2),
        'yearly_consumption': round(yearly_consumption, 2),
        'daily_cost': round(daily_cost, 2),
        'monthly_cost': round(monthly_cost, 2),
        'yearly_cost': round(yearly_cost, 2)
    }

def create_layout_visualization(area_length, area_width, num_lights, spacing):
    """
    Create a 2D visualization of light layout
    
    Parameters:
    area_length, area_width (float): Room dimensions
    num_lights (int): Number of lights
    spacing (float): Spacing between lights
    """
    # Calculate grid layout
    lights_per_row = int(np.ceil(np.sqrt(num_lights * area_length / area_width)))
    lights_per_col = int(np.ceil(num_lights / lights_per_row))
    
    x_positions = []
    y_positions = []
    
    x_spacing = area_length / (lights_per_row + 1)
    y_spacing = area_width / (lights_per_col + 1)
    
    for i in range(lights_per_row):
        for j in range(lights_per_col):
            if len(x_positions) < num_lights:
                x_positions.append((i + 1) * x_spacing)
                y_positions.append((j + 1) * y_spacing)
    
    # Create figure
    fig = go.Figure()
    
    # Add room boundary
    fig.add_shape(type="rect",
                  x0=0, y0=0,
                  x1=area_length, y1=area_width,
                  line=dict(color="RoyalBlue", width=2))
    
    # Add light positions
    fig.add_trace(go.Scatter(
        x=x_positions,
        y=y_positions,
        mode='markers',
        marker=dict(
            symbol='circle',
            size=20,
            color='yellow',
            line=dict(color='orange', width=2)
        ),
        name='Light Fixtures',
        text=[f'Light {i+1}' for i in range(len(x_positions))],
        hoverinfo='text'
    ))
    
    fig.update_layout(
        title="Recommended Light Layout",
        xaxis_title="Length (m)",
        yaxis_title="Width (m)",
        showlegend=True,
        height=500,
        xaxis=dict(range=[-1, area_length + 1]),
        yaxis=dict(range=[-1, area_width + 1]),
        hovermode='closest'
    )
    
    return fig

def main():
    # Header
    st.markdown("<h1 class='main-header'>💡 LuxSim Pro - Singapore Lighting Calculator</h1>", unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/light--v1.png", width=100)
        st.markdown("<h2 style='text-align: center;'>Input Parameters</h2>", unsafe_allow_html=True)
        
        # Building Type Selection
        building_type = st.selectbox(
            "Building Type",
            options=list(SINGAPORE_STANDARDS.keys()),
            index=0
        )
        
        # Room Type Selection based on building type
        room_type = st.selectbox(
            "Room Type",
            options=list(SINGAPORE_STANDARDS[building_type].keys()),
            index=0
        )
        
        # Get standard lux value
        standard_lux = SINGAPORE_STANDARDS[building_type][room_type]
        
        st.markdown(f"<div class='info-box'>📋 Singapore Standard (SS 531:2014) recommends <b>{standard_lux} lux</b> for {room_type}</div>", unsafe_allow_html=True)
        
        # Room Dimensions
        st.markdown("### 📏 Room Dimensions")
        col1, col2 = st.columns(2)
        with col1:
            area_length = st.number_input("Length (m)", min_value=1.0, max_value=100.0, value=5.0, step=0.5)
        with col2:
            area_width = st.number_input("Width (m)", min_value=1.0, max_value=100.0, value=4.0, step=0.5)
        
        room_height = st.number_input("Ceiling Height (m)", min_value=2.0, max_value=20.0, value=2.8, step=0.1)
        
        # Custom Lux Requirement
        use_custom_lux = st.checkbox("Use custom lux value")
        if use_custom_lux:
            required_lux = st.number_input("Custom Lux Requirement", min_value=50, max_value=2000, value=standard_lux, step=50)
        else:
            required_lux = standard_lux
        
        # Operating Parameters
        st.markdown("### ⚡ Operating Parameters")
        hours_per_day = st.slider("Operating Hours per Day", 1, 24, 10)
        days_per_year = st.slider("Operating Days per Year", 1, 365, 365)
        cost_per_kwh = st.number_input("Electricity Cost (SGD/kWh)", min_value=0.10, max_value=1.00, value=0.25, step=0.01)
        
        # Advanced Settings
        with st.expander("Advanced Settings"):
            maintenance_factor = st.slider("Maintenance Factor", 0.5, 1.0, 0.8, 0.05)
            utilization_factor = st.slider("Utilization Factor", 0.5, 1.0, 0.7, 0.05)
        
        # Calculate button
        calculate = st.button("Calculate Lighting Requirements", type="primary", use_container_width=True)
    
    # Main content area
    if calculate:
        # Perform calculations
        results, area = calculate_lights(
            area_length, area_width, room_height, required_lux,
            maintenance_factor=maintenance_factor,
            utilization_factor=utilization_factor
        )
        
        # Display results in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("<div class='success-box'>", unsafe_allow_html=True)
            st.metric("Room Area", f"{area:.1f} m²")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='success-box'>", unsafe_allow_html=True)
            st.metric("Required Lux", f"{required_lux} lux")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='success-box'>", unsafe_allow_html=True)
            # Find recommended option (first in list)
            if results:
                st.metric("Recommended Lights", f"{results[0]['num_lights']} fixtures")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Display recommendations table
        st.markdown("<h2 class='sub-header'>📊 Lighting Recommendations</h2>", unsafe_allow_html=True)
        
        df = pd.DataFrame(results)
        
        # Add energy cost calculations
        energy_costs = []
        for result in results:
            cost = calculate_energy_cost(result['total_wattage'], hours_per_day, days_per_year, cost_per_kwh)
            result['daily_cost'] = f"${cost['daily_cost']}"
            result['monthly_cost'] = f"${cost['monthly_cost']}"
            result['yearly_cost'] = f"${cost['yearly_cost']}"
        
        # Display table
        display_df = df[['category', 'light_type', 'wattage', 'lumens', 'num_lights', 
                        'total_wattage', 'actual_lux', 'spacing', 'cri', 'color_temp',
                        'daily_cost', 'monthly_cost', 'yearly_cost']]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Highlight best option
        st.markdown("<h3 class='sub-header'>✨ Recommended Option</h3>", unsafe_allow_html=True)
        best_option = results[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("<div class='info-box'>", unsafe_allow_html=True)
            st.markdown(f"**Light Type**<br>{best_option['light_type']}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='info-box'>", unsafe_allow_html=True)
            st.markdown(f"**Wattage**<br>{best_option['wattage']}W", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='info-box'>", unsafe_allow_html=True)
            st.markdown(f"**Number of Lights**<br>{best_option['num_lights']}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown("<div class='info-box'>", unsafe_allow_html=True)
            st.markdown(f"**Total Power**<br>{best_option['total_wattage']}W", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Layout Visualization
        st.markdown("<h2 class='sub-header'>🗺️ Layout Visualization</h2>", unsafe_allow_html=True)
        
        fig = create_layout_visualization(area_length, area_width, best_option['num_lights'], best_option['spacing'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Energy Cost Analysis
        st.markdown("<h2 class='sub-header'>💰 Energy Cost Analysis</h2>", unsafe_allow_html=True)
        
        cost_data = calculate_energy_cost(best_option['total_wattage'], hours_per_day, days_per_year, cost_per_kwh)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Daily Consumption", f"{cost_data['daily_consumption']} kWh", f"${cost_data['daily_cost']}")
        
        with col2:
            st.metric("Monthly Consumption", f"{cost_data['monthly_consumption']} kWh", f"${cost_data['monthly_cost']}")
        
        with col3:
            st.metric("Yearly Consumption", f"{cost_data['yearly_consumption']} kWh", f"${cost_data['yearly_cost']}")
        
        # Create energy cost chart
        periods = ['Daily', 'Monthly', 'Yearly']
        costs = [cost_data['daily_cost'], cost_data['monthly_cost'], cost_data['yearly_cost']]
        
        fig_cost = go.Figure(data=[
            go.Bar(name='Cost', x=periods, y=costs, marker_color='#1E88E5')
        ])
        
        fig_cost.update_layout(
            title="Energy Cost Overview",
            xaxis_title="Period",
            yaxis_title="Cost (SGD)",
            height=400
        )
        
        st.plotly_chart(fig_cost, use_container_width=True)
        
        # Comparison with alternatives
        st.markdown("<h2 class='sub-header'>📈 Option Comparison</h2>", unsafe_allow_html=True)
        
        # Create comparison chart
        fig_compare = go.Figure()
        
        # Add traces for different metrics
        fig_compare.add_trace(go.Bar(
            name='Number of Lights',
            x=[f"Option {i+1}" for i in range(min(5, len(results)))],
            y=[r['num_lights'] for r in results[:5]],
            marker_color='#1E88E5'
        ))
        
        fig_compare.add_trace(go.Bar(
            name='Total Wattage (W)',
            x=[f"Option {i+1}" for i in range(min(5, len(results)))],
            y=[r['total_wattage'] for r in results[:5]],
            marker_color='#FFA000'
        ))
        
        fig_compare.update_layout(
            title="Top 5 Options Comparison",
            xaxis_title="Options",
            yaxis_title="Value",
            barmode='group',
            height=500
        )
        
        st.plotly_chart(fig_compare, use_container_width=True)
        
        # Download Report
        st.markdown("<h2 class='sub-header'>📥 Download Report</h2>", unsafe_allow_html=True)
        
        # Prepare report data
        report_data = {
            "project_info": {
                "building_type": building_type,
                "room_type": room_type,
                "area": area,
                "required_lux": required_lux,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "dimensions": {
                "length": area_length,
                "width": area_width,
                "height": room_height
            },
            "recommended_option": best_option,
            "all_options": results,
            "energy_costs": cost_data
        }
        
        # Download buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CSV download
            csv = df.to_csv(index=False)
            st.download_button(
                label="📊 Download as CSV",
                data=csv,
                file_name=f"lighting_calculation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # JSON download
            json_str = json.dumps(report_data, indent=2)
            st.download_button(
                label="📄 Download as JSON",
                data=json_str,
                file_name=f"lighting_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col3:
            # HTML Report (simplified)
            html_report = f"""
            <html>
            <head><title>Lighting Report</title></head>
            <body>
                <h1>Lighting Calculation Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <h2>Project Information</h2>
                <ul>
                    <li>Building Type: {building_type}</li>
                    <li>Room Type: {room_type}</li>
                    <li>Area: {area:.1f} m²</li>
                    <li>Required Lux: {required_lux}</li>
                </ul>
                <h2>Recommended Solution</h2>
                <ul>
                    <li>Light Type: {best_option['light_type']}</li>
                    <li>Wattage: {best_option['wattage']}W</li>
                    <li>Number of Lights: {best_option['num_lights']}</li>
                    <li>Total Power: {best_option['total_wattage']}W</li>
                    <li>Actual Lux Achieved: {best_option['actual_lux']}</li>
                </ul>
            </body>
            </html>
            """
            st.download_button(
                label="🌐 Download as HTML",
                data=html_report,
                file_name=f"lighting_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )
    
    else:
        # Show welcome message and instructions
        st.markdown("""
        <div class='info-box'>
            <h3>👋 Welcome to LuxSim Pro!</h3>
            <p>This application helps you calculate lighting requirements based on Singapore Standards (SS 531:2014).</p>
            <p><b>How to use:</b></p>
            <ol>
                <li>Select your building and room type from the sidebar</li>
                <li>Enter your room dimensions</li>
                <li>Adjust operating parameters if needed</li>
                <li>Click "Calculate Lighting Requirements"</li>
            </ol>
            <p>The application will recommend the optimal number and type of lights, along with layout visualization and energy cost analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display Singapore Standards reference
        st.markdown("<h2 class='sub-header'>📚 Singapore Standards Reference (SS 531:2014)</h2>", unsafe_allow_html=True)
        
        # Create tabs for different building types
        tabs = st.tabs(list(SINGAPORE_STANDARDS.keys()))
        
        for i, (building_type, rooms) in enumerate(SINGAPORE_STANDARDS.items()):
            with tabs[i]:
                df_standards = pd.DataFrame([
                    {"Room Type": room, "Required Lux": lux}
                    for room, lux in rooms.items()
                ])
                st.dataframe(df_standards, use_container_width=True, hide_index=True)
        
        # Tips and best practices
        with st.expander("💡 Lighting Design Tips"):
            st.markdown("""
            **Best Practices for Singapore Buildings:**
            
            1. **Use LED Lighting** - Most energy-efficient option for tropical climate
            2. **Consider Natural Light** - Integrate with daylight harvesting systems
            3. **Maintenance Factor** - Account for dust accumulation (typically 0.8)
            4. **Color Temperature** - 3000K for residential, 4000K for offices, 5000K for industrial
            5. **CRI Requirements** - Minimum 80 for general areas, 90 for retail
            6. **Emergency Lighting** - Ensure compliance with fire safety codes
            7. **Energy Efficiency** - Consider motion sensors and daylight sensors
            """)

if __name__ == "__main__":
    main()