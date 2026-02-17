# app.py
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
    .outdoor-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #2e7d32;
    }
    .indoor-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #1565c0;
    }
</style>
""", unsafe_allow_html=True)

# Singapore Standards for Indoor Illuminance (SS 531:2014)
INDOOR_STANDARDS = {
    "Residential": {
        "Living Room": 150,
        "Bedroom": 100,
        "Kitchen": 300,
        "Bathroom": 100,
        "Study Room": 300,
        "Corridor": 75,
        "Staircase": 100,
        "Store Room": 100
    },
    "Office": {
        "Open Plan Office": 400,
        "Private Office": 500,
        "Conference Room": 500,
        "Reception": 300,
        "Corridor": 100,
        "Pantry": 200,
        "Lobby": 300,
        "Archive/Storage": 200
    },
    "Commercial": {
        "Retail Shop": 500,
        "Supermarket": 750,
        "Restaurant": 200,
        "Food Court": 300,
        "Lobby": 300,
        "Parking Lot (Indoor)": 75,
        "Staircase": 100
    },
    "Industrial": {
        "Warehouse": 150,
        "Factory Floor": 300,
        "Laboratory": 500,
        "Control Room": 300,
        "Loading Bay": 150,
        "Storage Area": 100
    },
    "Educational": {
        "Classroom": 300,
        "Library": 500,
        "Laboratory": 500,
        "Auditorium": 200,
        "Lecture Hall": 300,
        "Corridor": 100
    },
    "Healthcare": {
        "Patient Room": 100,
        "Examination Room": 500,
        "Operating Theatre": 1000,
        "Waiting Area": 200,
        "Corridor": 100,
        "Pharmacy": 500
    }
}

# Singapore Standards for Outdoor Illuminance (Based on BCA and LTA guidelines)
OUTDOOR_STANDARDS = {
    "Residential Estates": {
        "Linkway/Covered Walkway": 50,
        "Void Deck": 100,
        "Corridor (Open)": 30,
        "Staircase (External)": 50,
        "Bicycle Parking": 30,
        "Refuse Chamber": 100
    },
    "Parks & Recreation": {
        "Park Path": 20,
        "Park Seating Area": 30,
        "Fitness Corner": 100,
        "Playground": 50,
        "Exercise Station": 100,
        "Picnic Area": 30,
        "Reflective Area": 10,
        "Garden": 15
    },
    "Sports Facilities": {
        "Basketball Court": 300,
        "Tennis Court": 300,
        "Futsal Court": 200,
        "Outdoor Gym": 150,
        "Running Track": 100,
        "Multi-purpose Court": 200
    },
    "Pedestrian Infrastructure": {
        "Pedestrian Walkway": 20,
        "High Linkway/Bridge": 50,
        "Underpass": 100,
        "Staircase (Public)": 50,
        "Ramp": 30,
        "Bus Stop": 50,
        "MRT/LRT Entrance": 100
    },
    "Roads & Car Parks": {
        "Residential Road": 15,
        "Access Road": 20,
        "Car Park (Open)": 20,
        "Car Park Ramp": 50,
        "Drop-off Point": 50,
        "Roundabout": 30,
        "Pedestrian Crossing": 50
    },
    "Security & Safety": {
        "Security Post": 150,
        "Perimeter Fencing": 10,
        "CCTV Area": 30,
        "Emergency Exit": 50,
        "Fire Command Centre": 200
    },
    "Water Features": {
        "Drainage Channel": 10,
        "Pond Surround": 20,
        "Fountain Area": 30,
        "Swimming Pool (Outdoor)": 100
    }
}

# LED Light Specifications (including outdoor specific lights)
INDOOR_LIGHTS = {
    "Residential": [
        {"wattage": 9, "lumens": 800, "cri": 80, "color_temp": "3000K", "type": "LED Bulb", "ip_rating": "IP20", "beam_angle": 120},
        {"wattage": 12, "lumens": 1100, "cri": 80, "color_temp": "3000K", "type": "LED Bulb", "ip_rating": "IP20", "beam_angle": 120},
        {"wattage": 15, "lumens": 1400, "cri": 80, "color_temp": "4000K", "type": "LED Downlight", "ip_rating": "IP44", "beam_angle": 90},
        {"wattage": 18, "lumens": 1700, "cri": 85, "color_temp": "4000K", "type": "LED Downlight", "ip_rating": "IP44", "beam_angle": 90}
    ],
    "Office": [
        {"wattage": 18, "lumens": 1800, "cri": 85, "color_temp": "4000K", "type": "LED Panel", "ip_rating": "IP20", "beam_angle": 110},
        {"wattage": 24, "lumens": 2400, "cri": 85, "color_temp": "4000K", "type": "LED Panel", "ip_rating": "IP20", "beam_angle": 110},
        {"wattage": 36, "lumens": 3600, "cri": 85, "color_temp": "4000K", "type": "LED Panel", "ip_rating": "IP20", "beam_angle": 110},
        {"wattage": 48, "lumens": 4800, "cri": 85, "color_temp": "5000K", "type": "LED Panel", "ip_rating": "IP20", "beam_angle": 110}
    ],
    "Commercial": [
        {"wattage": 20, "lumens": 2000, "cri": 85, "color_temp": "4000K", "type": "LED Track Light", "ip_rating": "IP20", "beam_angle": 60},
        {"wattage": 30, "lumens": 3000, "cri": 85, "color_temp": "4000K", "type": "LED Track Light", "ip_rating": "IP20", "beam_angle": 60},
        {"wattage": 40, "lumens": 4000, "cri": 90, "color_temp": "5000K", "type": "LED Downlight", "ip_rating": "IP44", "beam_angle": 90},
        {"wattage": 50, "lumens": 5000, "cri": 90, "color_temp": "5000K", "type": "LED Downlight", "ip_rating": "IP44", "beam_angle": 90}
    ],
    "Industrial": [
        {"wattage": 50, "lumens": 5000, "cri": 80, "color_temp": "5000K", "type": "LED High Bay", "ip_rating": "IP65", "beam_angle": 90},
        {"wattage": 100, "lumens": 10000, "cri": 80, "color_temp": "5000K", "type": "LED High Bay", "ip_rating": "IP65", "beam_angle": 90},
        {"wattage": 150, "lumens": 15000, "cri": 80, "color_temp": "5000K", "type": "LED High Bay", "ip_rating": "IP65", "beam_angle": 90},
        {"wattage": 200, "lumens": 20000, "cri": 80, "color_temp": "5000K", "type": "LED High Bay", "ip_rating": "IP65", "beam_angle": 90}
    ],
    "Educational": [
        {"wattage": 18, "lumens": 1800, "cri": 85, "color_temp": "4000K", "type": "LED Panel", "ip_rating": "IP20", "beam_angle": 110},
        {"wattage": 24, "lumens": 2400, "cri": 85, "color_temp": "4000K", "type": "LED Panel", "ip_rating": "IP20", "beam_angle": 110},
        {"wattage": 36, "lumens": 3600, "cri": 85, "color_temp": "4000K", "type": "LED Panel", "ip_rating": "IP20", "beam_angle": 110}
    ],
    "Healthcare": [
        {"wattage": 18, "lumens": 1800, "cri": 90, "color_temp": "4000K", "type": "LED Panel", "ip_rating": "IP44", "beam_angle": 110},
        {"wattage": 24, "lumens": 2400, "cri": 90, "color_temp": "4000K", "type": "LED Panel", "ip_rating": "IP44", "beam_angle": 110},
        {"wattage": 36, "lumens": 3600, "cri": 90, "color_temp": "5000K", "type": "LED Panel", "ip_rating": "IP44", "beam_angle": 110}
    ]
}

OUTDOOR_LIGHTS = {
    "Residential Estates": [
        {"wattage": 18, "lumens": 1800, "cri": 80, "color_temp": "3000K", "type": "LED Wall Light", "ip_rating": "IP65", "beam_angle": 120, "mounting_height": 3},
        {"wattage": 24, "lumens": 2400, "cri": 80, "color_temp": "3000K", "type": "LED Bollard Light", "ip_rating": "IP65", "beam_angle": 360, "mounting_height": 1},
        {"wattage": 30, "lumens": 3000, "cri": 80, "color_temp": "4000K", "type": "LED Flood Light", "ip_rating": "IP65", "beam_angle": 120, "mounting_height": 4},
        {"wattage": 50, "lumens": 5000, "cri": 80, "color_temp": "4000K", "type": "LED Post Top", "ip_rating": "IP65", "beam_angle": 180, "mounting_height": 5}
    ],
    "Parks & Recreation": [
        {"wattage": 12, "lumens": 1200, "cri": 80, "color_temp": "3000K", "type": "LED Garden Light", "ip_rating": "IP65", "beam_angle": 360, "mounting_height": 0.8},
        {"wattage": 20, "lumens": 2000, "cri": 80, "color_temp": "3000K", "type": "LED Path Light", "ip_rating": "IP65", "beam_angle": 120, "mounting_height": 1},
        {"wattage": 30, "lumens": 3000, "cri": 80, "color_temp": "4000K", "type": "LED Flood Light", "ip_rating": "IP65", "beam_angle": 90, "mounting_height": 4},
        {"wattage": 50, "lumens": 5000, "cri": 80, "color_temp": "4000K", "type": "LED Area Light", "ip_rating": "IP65", "beam_angle": 120, "mounting_height": 6}
    ],
    "Sports Facilities": [
        {"wattage": 100, "lumens": 10000, "cri": 80, "color_temp": "5000K", "type": "LED Sports Flood", "ip_rating": "IP66", "beam_angle": 60, "mounting_height": 8},
        {"wattage": 150, "lumens": 15000, "cri": 80, "color_temp": "5000K", "type": "LED Sports Flood", "ip_rating": "IP66", "beam_angle": 60, "mounting_height": 8},
        {"wattage": 200, "lumens": 20000, "cri": 80, "color_temp": "5000K", "type": "LED Sports Flood", "ip_rating": "IP66", "beam_angle": 45, "mounting_height": 10},
        {"wattage": 300, "lumens": 30000, "cri": 80, "color_temp": "5700K", "type": "LED Sports Flood", "ip_rating": "IP66", "beam_angle": 45, "mounting_height": 12}
    ],
    "Pedestrian Infrastructure": [
        {"wattage": 18, "lumens": 1800, "cri": 70, "color_temp": "4000K", "type": "LED Street Light", "ip_rating": "IP65", "beam_angle": 120, "mounting_height": 6},
        {"wattage": 24, "lumens": 2400, "cri": 70, "color_temp": "4000K", "type": "LED Street Light", "ip_rating": "IP65", "beam_angle": 120, "mounting_height": 6},
        {"wattage": 36, "lumens": 3600, "cri": 70, "color_temp": "4000K", "type": "LED Street Light", "ip_rating": "IP65", "beam_angle": 120, "mounting_height": 8},
        {"wattage": 24, "lumens": 2400, "cri": 70, "color_temp": "4000K", "type": "LED Underpass Light", "ip_rating": "IP65", "beam_angle": 90, "mounting_height": 3}
    ],
    "Roads & Car Parks": [
        {"wattage": 30, "lumens": 3000, "cri": 70, "color_temp": "4000K", "type": "LED Street Light", "ip_rating": "IP65", "beam_angle": 120, "mounting_height": 8},
        {"wattage": 50, "lumens": 5000, "cri": 70, "color_temp": "4000K", "type": "LED Street Light", "ip_rating": "IP65", "beam_angle": 120, "mounting_height": 9},
        {"wattage": 70, "lumens": 7000, "cri": 70, "color_temp": "5000K", "type": "LED Street Light", "ip_rating": "IP65", "beam_angle": 120, "mounting_height": 10},
        {"wattage": 100, "lumens": 10000, "cri": 70, "color_temp": "5000K", "type": "LED Flood Light", "ip_rating": "IP65", "beam_angle": 90, "mounting_height": 12}
    ],
    "Security & Safety": [
        {"wattage": 20, "lumens": 2000, "cri": 80, "color_temp": "5000K", "type": "LED Security Light", "ip_rating": "IP65", "beam_angle": 110, "mounting_height": 4},
        {"wattage": 30, "lumens": 3000, "cri": 80, "color_temp": "5000K", "type": "LED Security Light", "ip_rating": "IP65", "beam_angle": 110, "mounting_height": 4},
        {"wattage": 50, "lumens": 5000, "cri": 80, "color_temp": "5000K", "type": "LED Flood Light", "ip_rating": "IP66", "beam_angle": 90, "mounting_height": 5},
        {"wattage": 15, "lumens": 1500, "cri": 80, "color_temp": "4000K", "type": "LED Bulkhead", "ip_rating": "IP65", "beam_angle": 120, "mounting_height": 3}
    ],
    "Water Features": [
        {"wattage": 9, "lumens": 800, "cri": 80, "color_temp": "3000K", "type": "LED Landscape Light", "ip_rating": "IP67", "beam_angle": 60, "mounting_height": 0.5},
        {"wattage": 12, "lumens": 1100, "cri": 80, "color_temp": "3000K", "type": "LED Landscape Light", "ip_rating": "IP67", "beam_angle": 60, "mounting_height": 0.5},
        {"wattage": 18, "lumens": 1700, "cri": 80, "color_temp": "4000K", "type": "LED Pond Light", "ip_rating": "IP68", "beam_angle": 120, "mounting_height": 0.2},
        {"wattage": 24, "lumens": 2400, "cri": 80, "color_temp": "4000K", "type": "LED Flood Light", "ip_rating": "IP66", "beam_angle": 90, "mounting_height": 2}
    ]
}

def calculate_indoor_lights(area_length, area_width, room_height, required_lux, 
                          maintenance_factor=0.8, utilization_factor=0.7):
    """
    Calculate number of indoor lights required using Lumen Method
    """
    area = area_length * area_width
    total_lumens_required = (required_lux * area) / (maintenance_factor * utilization_factor)
    
    results = []
    for category, lights in INDOOR_LIGHTS.items():
        for light in lights:
            lumens_per_light = light['lumens']
            num_lights = np.ceil(total_lumens_required / lumens_per_light)
            
            # Calculate spacing based on room dimensions and beam angle
            max_spacing = room_height * np.tan(np.radians(light['beam_angle']/2)) * 2
            area_per_light = area / num_lights
            spacing = min(np.sqrt(area_per_light), max_spacing)
            
            # Calculate actual lux achieved
            actual_lux = (num_lights * lumens_per_light * maintenance_factor * utilization_factor) / area
            
            results.append({
                'environment': 'Indoor',
                'category': category,
                'light_type': light['type'],
                'wattage': light['wattage'],
                'lumens': lumens_per_light,
                'num_lights': int(num_lights),
                'total_wattage': int(num_lights * light['wattage']),
                'actual_lux': round(actual_lux, 1),
                'spacing': round(spacing, 2),
                'cri': light['cri'],
                'color_temp': light['color_temp'],
                'ip_rating': light['ip_rating'],
                'beam_angle': light['beam_angle']
            })
    
    results.sort(key=lambda x: (x['num_lights'], x['total_wattage']))
    return results, area

def calculate_outdoor_lights(area_length, area_width, required_lux, area_type,
                           maintenance_factor=0.7, uniformity_requirement=0.4):
    """
    Calculate number of outdoor lights required
    Outdoor calculations consider uniformity and specific mounting heights
    """
    area = area_length * area_width
    # Outdoor typically has lower utilization factor due to wider spacing
    utilization_factor = 0.5
    
    total_lumens_required = (required_lux * area) / (maintenance_factor * utilization_factor)
    
    results = []
    for category, lights in OUTDOOR_LIGHTS.items():
        for light in lights:
            lumens_per_light = light['lumens']
            
            # Calculate based on mounting height and beam angle
            coverage_radius = light['mounting_height'] * np.tan(np.radians(light['beam_angle']/2))
            coverage_area = np.pi * coverage_radius**2 if light['beam_angle'] > 180 else 2 * coverage_radius * light['mounting_height']
            
            # Calculate number of lights needed
            num_lights_area = np.ceil(area / coverage_area)  # Based on coverage
            num_lights_lumens = np.ceil(total_lumens_required / lumens_per_light)
            num_lights = max(num_lights_area, num_lights_lumens)
            
            # Calculate spacing for uniform coverage
            if light['beam_angle'] >= 180:  # Omnidirectional
                spacing = min(2 * coverage_radius, 10)  # Max 10m spacing for uniformity
            else:  # Directional
                spacing = min(1.5 * coverage_radius, 15)
            
            # Calculate actual lux achieved
            actual_lux = (num_lights * lumens_per_light * maintenance_factor * utilization_factor) / area
            
            # Check uniformity
            uniformity = actual_lux / (num_lights * lumens_per_light / area) if num_lights > 0 else 0
            
            results.append({
                'environment': 'Outdoor',
                'category': category,
                'light_type': light['type'],
                'wattage': light['wattage'],
                'lumens': lumens_per_light,
                'num_lights': int(num_lights),
                'total_wattage': int(num_lights * light['wattage']),
                'actual_lux': round(actual_lux, 1),
                'spacing': round(spacing, 2),
                'mounting_height': light['mounting_height'],
                'cri': light['cri'],
                'color_temp': light['color_temp'],
                'ip_rating': light['ip_rating'],
                'beam_angle': light['beam_angle'],
                'coverage_area': round(coverage_area, 1),
                'uniformity': round(uniformity, 2)
            })
    
    # Sort by number of lights and then by total wattage
    results.sort(key=lambda x: (x['num_lights'], x['total_wattage']))
    return results, area

def calculate_energy_cost(total_wattage, hours_per_day=10, days_per_year=365, cost_per_kwh=0.25):
    """
    Calculate energy consumption and cost
    """
    daily_consumption = (total_wattage / 1000) * hours_per_day
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

def create_indoor_layout(area_length, area_width, num_lights, spacing):
    """
    Create a 2D visualization of indoor light layout
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
        mode='markers+text',
        marker=dict(
            symbol='circle',
            size=20,
            color='gold',
            line=dict(color='orange', width=2)
        ),
        text=[f'💡' for _ in range(len(x_positions))],
        textposition="middle center",
        name='Light Fixtures',
        hovertext=[f'Light {i+1}<br>Position: ({x:.1f}, {y:.1f})' 
                   for i, (x, y) in enumerate(zip(x_positions, y_positions))],
        hoverinfo='text'
    ))
    
    # Add light coverage indicators (simplified)
    for x, y in zip(x_positions, y_positions):
        fig.add_shape(type="circle",
                      xref="x", yref="y",
                      x0=x-1, y0=y-1,
                      x1=x+1, y1=y+1,
                      line=dict(color="rgba(255, 215, 0, 0.3)", width=1),
                      fillcolor="rgba(255, 215, 0, 0.1)")
    
    fig.update_layout(
        title="Indoor Light Layout",
        xaxis_title="Length (m)",
        yaxis_title="Width (m)",
        showlegend=True,
        height=500,
        xaxis=dict(range=[-1, area_length + 1], showgrid=True),
        yaxis=dict(range=[-1, area_width + 1], showgrid=True),
        hovermode='closest'
    )
    
    return fig

def create_outdoor_layout(area_length, area_width, results, best_option):
    """
    Create outdoor lighting layout with pole positions
    """
    num_lights = best_option['num_lights']
    mounting_height = best_option['mounting_height']
    beam_angle = best_option['beam_angle']
    
    # Calculate number of poles needed
    poles_needed = num_lights
    poles_per_row = int(np.ceil(np.sqrt(poles_needed * area_length / area_width)))
    poles_per_col = int(np.ceil(poles_needed / poles_per_row))
    
    x_positions = []
    y_positions = []
    
    x_spacing = area_length / (poles_per_row + 1)
    y_spacing = area_width / (poles_per_col + 1)
    
    for i in range(poles_per_row):
        for j in range(poles_per_col):
            if len(x_positions) < poles_needed:
                x_positions.append((i + 1) * x_spacing)
                y_positions.append((j + 1) * y_spacing)
    
    # Create figure
    fig = go.Figure()
    
    # Add area boundary
    fig.add_shape(type="rect",
                  x0=0, y0=0,
                  x1=area_length, y1=area_width,
                  line=dict(color="ForestGreen", width=2))
    
    # Calculate coverage radius
    coverage_radius = mounting_height * np.tan(np.radians(beam_angle/2))
    
    # Add light poles and coverage areas
    for x, y in zip(x_positions, y_positions):
        # Add pole
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(
                symbol='circle',
                size=15,
                color='darkgreen',
                line=dict(color='black', width=2)
            ),
            text=['⛓️'],
            textposition="middle center",
            showlegend=False,
            hovertext=f'Pole at ({x:.1f}, {y:.1f})<br>Height: {mounting_height}m',
            hoverinfo='text'
        ))
        
        # Add coverage area
        theta = np.linspace(0, 2*np.pi, 50)
        x_circle = x + coverage_radius * np.cos(theta)
        y_circle = y + coverage_radius * np.sin(theta)
        
        fig.add_trace(go.Scatter(
            x=x_circle, y=y_circle,
            mode='lines',
            line=dict(color="rgba(255, 215, 0, 0.5)", width=1),
            fill='toself',
            fillcolor="rgba(255, 215, 0, 0.1)",
            showlegend=False,
            hoverinfo='none'
        ))
    
    fig.update_layout(
        title=f"Outdoor Lighting Layout (Mounting Height: {mounting_height}m)",
        xaxis_title="Length (m)",
        yaxis_title="Width (m)",
        height=500,
        xaxis=dict(range=[-2, area_length + 2], showgrid=True),
        yaxis=dict(range=[-2, area_width + 2], showgrid=True),
        hovermode='closest'
    )
    
    return fig

def calculate_glare_index(light_intensity, distance, angle):
    """
    Calculate glare index for outdoor lighting
    Simplified TI (Glare Index) calculation
    """
    # Simplified glare calculation
    glare = (light_intensity * np.cos(np.radians(angle))) / (distance**2)
    return round(glare, 2)

def calculate_light_pollution(total_lumens, area, mounting_height):
    """
    Calculate light pollution risk
    """
    upward_light_ratio = 0.05  # Assume 5% upward light
    light_pollution_index = (total_lumens * upward_light_ratio) / (area * mounting_height)
    
    if light_pollution_index < 1:
        risk = "Low"
    elif light_pollution_index < 2:
        risk = "Medium"
    else:
        risk = "High"
    
    return {
        'index': round(light_pollution_index, 2),
        'risk': risk
    }

def main():
    # Header
    st.markdown("<h1 class='main-header'>💡 LuxSim Pro - Singapore Indoor & Outdoor Lighting Calculator</h1>", unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/light--v1.png", width=100)
        st.markdown("<h2 style='text-align: center;'>Input Parameters</h2>", unsafe_allow_html=True)
        
        # Environment Selection
        environment = st.radio(
            "Select Environment",
            options=["Indoor", "Outdoor"],
            horizontal=True
        )
        
        if environment == "Indoor":
            # Building Type Selection
            building_type = st.selectbox(
                "Building Type",
                options=list(INDOOR_STANDARDS.keys()),
                index=0
            )
            
            # Room Type Selection
            room_type = st.selectbox(
                "Room Type",
                options=list(INDOOR_STANDARDS[building_type].keys()),
                index=0
            )
            
            # Get standard lux value
            standard_lux = INDOOR_STANDARDS[building_type][room_type]
            st.markdown(f"<div class='indoor-box'>📋 Singapore Standard (SS 531:2014) recommends <b>{standard_lux} lux</b> for {room_type}</div>", unsafe_allow_html=True)
            
        else:  # Outdoor
            # Outdoor Category Selection
            outdoor_category = st.selectbox(
                "Outdoor Area Category",
                options=list(OUTDOOR_STANDARDS.keys()),
                index=0
            )
            
            # Specific Area Type Selection
            area_type = st.selectbox(
                "Specific Area Type",
                options=list(OUTDOOR_STANDARDS[outdoor_category].keys()),
                index=0
            )
            
            # Get standard lux value
            standard_lux = OUTDOOR_STANDARDS[outdoor_category][area_type]
            st.markdown(f"<div class='outdoor-box'>🌳 Singapore Outdoor Standard recommends <b>{standard_lux} lux</b> for {area_type}</div>", unsafe_allow_html=True)
            
            # Outdoor specific parameters
            st.markdown("### 🏗️ Installation Parameters")
            uniformity_requirement = st.slider("Uniformity Requirement (Min/Avg)", 0.2, 0.8, 0.4, 0.05)
            
            # Show light pollution warning for sensitive areas
            if area_type in ["Park", "Garden", "Reflective Area"]:
                st.warning("⚠️ Consider light pollution reduction measures for this area type")
        
        # Common Parameters
        st.markdown("### 📏 Area Dimensions")
        col1, col2 = st.columns(2)
        with col1:
            area_length = st.number_input("Length (m)", min_value=1.0, max_value=200.0, value=10.0, step=0.5)
        with col2:
            area_width = st.number_input("Width (m)", min_value=1.0, max_value=200.0, value=8.0, step=0.5)
        
        if environment == "Indoor":
            room_height = st.number_input("Ceiling Height (m)", min_value=2.0, max_value=20.0, value=2.8, step=0.1)
        else:
            # For outdoor, ask for pole height range preference
            pole_height_min = st.number_input("Minimum Pole Height (m)", min_value=2.0, max_value=20.0, value=4.0, step=0.5)
            pole_height_max = st.number_input("Maximum Pole Height (m)", min_value=2.0, max_value=30.0, value=8.0, step=0.5)
        
        # Lux Requirement
        use_custom_lux = st.checkbox("Use custom lux value")
        if use_custom_lux:
            if environment == "Indoor":
                required_lux = st.number_input("Custom Lux Requirement", min_value=20, max_value=2000, value=standard_lux, step=20)
            else:
                required_lux = st.number_input("Custom Lux Requirement", min_value=5, max_value=500, value=standard_lux, step=5)
        else:
            required_lux = standard_lux
        
        # Operating Parameters
        st.markdown("### ⚡ Operating Parameters")
        hours_per_day = st.slider("Operating Hours per Day", 1, 24, 12 if environment == "Outdoor" else 10)
        days_per_year = st.slider("Operating Days per Year", 1, 365, 365)
        cost_per_kwh = st.number_input("Electricity Cost (SGD/kWh)", min_value=0.10, max_value=1.00, value=0.25, step=0.01)
        
        # Advanced Settings
        with st.expander("Advanced Settings"):
            if environment == "Indoor":
                maintenance_factor = st.slider("Maintenance Factor", 0.5, 1.0, 0.8, 0.05)
                utilization_factor = st.slider("Utilization Factor", 0.5, 1.0, 0.7, 0.05)
            else:
                maintenance_factor = st.slider("Maintenance Factor (Outdoor)", 0.5, 1.0, 0.7, 0.05)
        
        # Calculate button
        calculate = st.button("Calculate Lighting Requirements", type="primary", use_container_width=True)
    
    # Main content area
    if calculate:
        # Perform calculations based on environment
        if environment == "Indoor":
            results, area = calculate_indoor_lights(
                area_length, area_width, room_height, required_lux,
                maintenance_factor=maintenance_factor,
                utilization_factor=utilization_factor
            )
        else:
            results, area = calculate_outdoor_lights(
                area_length, area_width, required_lux, area_type,
                maintenance_factor=maintenance_factor,
                uniformity_requirement=uniformity_requirement
            )
        
        # Display results summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("<div class='success-box'>", unsafe_allow_html=True)
            st.metric("Total Area", f"{area:.1f} m²")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='success-box'>", unsafe_allow_html=True)
            st.metric("Required Lux", f"{required_lux} lux")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='success-box'>", unsafe_allow_html=True)
            if results:
                st.metric("Recommended Fixtures", f"{results[0]['num_lights']} units")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown("<div class='success-box'>", unsafe_allow_html=True)
            if results:
                st.metric("Total Power", f"{results[0]['total_wattage']} W")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Display recommendations table
        st.markdown("<h2 class='sub-header'>📊 Lighting Recommendations</h2>", unsafe_allow_html=True)
        
        # Prepare display DataFrame
        display_cols = ['environment', 'category', 'light_type', 'wattage', 'lumens', 
                       'num_lights', 'total_wattage', 'actual_lux', 'spacing', 'ip_rating']
        
        if environment == "Outdoor":
            display_cols.extend(['mounting_height', 'beam_angle', 'uniformity'])
        
        display_cols.extend(['cri', 'color_temp'])
        
        df = pd.DataFrame(results)
        
        # Add energy cost calculations
        energy_costs = []
        for result in results[:10]:  # Calculate for top 10 options
            cost = calculate_energy_cost(result['total_wattage'], hours_per_day, days_per_year, cost_per_kwh)
            result['daily_cost'] = f"${cost['daily_cost']}"
            result['monthly_cost'] = f"${cost['monthly_cost']}"
            result['yearly_cost'] = f"${cost['yearly_cost']}"
        
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
        
        # Highlight best option
        st.markdown("<h3 class='sub-header'>✨ Recommended Option</h3>", unsafe_allow_html=True)
        best_option = results[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("<div class='info-box'>", unsafe_allow_html=True)
            st.markdown(f"**Light Type**<br>{best_option['light_type']}", unsafe_allow_html=True)
            st.markdown(f"**IP Rating**<br>{best_option['ip_rating']}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='info-box'>", unsafe_allow_html=True)
            st.markdown(f"**Wattage**<br>{best_option['wattage']}W", unsafe_allow_html=True)
            st.markdown(f"**Lumens**<br>{best_option['lumens']} lm", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='info-box'>", unsafe_allow_html=True)
            st.markdown(f"**Number of Lights**<br>{best_option['num_lights']}", unsafe_allow_html=True)
            if environment == "Outdoor":
                st.markdown(f"**Mounting Height**<br>{best_option['mounting_height']}m", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown("<div class='info-box'>", unsafe_allow_html=True)
            st.markdown(f"**Total Power**<br>{best_option['total_wattage']}W", unsafe_allow_html=True)
            st.markdown(f"**Color Temp**<br>{best_option['color_temp']}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Layout Visualization
        st.markdown("<h2 class='sub-header'>🗺️ Layout Visualization</h2>", unsafe_allow_html=True)
        
        if environment == "Indoor":
            fig = create_indoor_layout(area_length, area_width, best_option['num_lights'], best_option['spacing'])
        else:
            fig = create_outdoor_layout(area_length, area_width, results, best_option)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Outdoor specific analysis
        if environment == "Outdoor":
            st.markdown("<h2 class='sub-header'>🌙 Outdoor Lighting Analysis</h2>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Glare analysis
                st.markdown("**Glare Assessment**")
                glare_index = calculate_glare_index(best_option['lumens'], best_option['mounting_height'], 30)
                
                if glare_index < 10:
                    glare_status = "Low Glare ✓"
                    glare_color = "green"
                elif glare_index < 20:
                    glare_status = "Moderate Glare ⚠️"
                    glare_color = "orange"
                else:
                    glare_status = "High Glare ❌"
                    glare_color = "red"
                
                st.markdown(f"<p style='color: {glare_color}; font-weight: bold;'>Glare Index: {glare_index} - {glare_status}</p>", unsafe_allow_html=True)
                st.progress(min(glare_index/30, 1.0))
            
            with col2:
                # Light pollution analysis
                pollution = calculate_light_pollution(
                    best_option['total_wattage'] * 100,  # Approximate lumens
                    area,
                    best_option['mounting_height']
                )
                
                pollution_color = {
                    "Low": "green",
                    "Medium": "orange",
                    "High": "red"
                }[pollution['risk']]
                
                st.markdown("**Light Pollution Risk**")
                st.markdown(f"<p style='color: {pollution_color}; font-weight: bold;'>Index: {pollution['index']} - {pollution['risk']} Risk</p>", unsafe_allow_html=True)
                st.progress(pollution['index']/3 if pollution['index'] < 3 else 1.0)
            
            # Uniformity analysis
            st.markdown("**Lighting Uniformity**")
            if 'uniformity' in best_option:
                uniformity = best_option['uniformity']
                if uniformity >= uniformity_requirement:
                    st.success(f"✓ Uniformity meets requirement: {uniformity} (Required: {uniformity_requirement})")
                else:
                    st.warning(f"⚠️ Uniformity below requirement: {uniformity} (Required: {uniformity_requirement})")
        
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
        
        # Environmental Impact
        co2_emissions = cost_data['yearly_consumption'] * 0.4  # kg CO2 per kWh in Singapore
        st.info(f"🌱 Estimated Annual CO2 Emissions: {co2_emissions:.1f} kg (based on Singapore grid intensity)")
        
        # Comparison chart
        st.markdown("<h2 class='sub-header'>📈 Option Comparison</h2>", unsafe_allow_html=True)
        
        fig_compare = go.Figure()
        
        # Add traces for different metrics
        fig_compare.add_trace(go.Bar(
            name='Number of Lights',
            x=[f"Opt {i+1}" for i in range(min(5, len(results)))],
            y=[r['num_lights'] for r in results[:5]],
            marker_color='#1E88E5'
        ))
        
        fig_compare.add_trace(go.Bar(
            name='Total Wattage (W)',
            x=[f"Opt {i+1}" for i in range(min(5, len(results)))],
            y=[r['total_wattage'] for r in results[:5]],
            marker_color='#FFA000'
        ))
        
        if environment == "Outdoor":
            fig_compare.add_trace(go.Bar(
                name='Mounting Height (m)',
                x=[f"Opt {i+1}" for i in range(min(5, len(results)))],
                y=[r['mounting_height'] for r in results[:5]],
                marker_color='#2E7D32'
            ))
        
        fig_compare.update_layout(
            title=f"Top 5 {environment} Options Comparison",
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
                "environment": environment,
                "area_type": room_type if environment == "Indoor" else area_type,
                "category": building_type if environment == "Indoor" else outdoor_category,
                "area": area,
                "required_lux": required_lux,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "dimensions": {
                "length": area_length,
                "width": area_width,
                "height": room_height if environment == "Indoor" else None
            },
            "recommended_option": best_option,
            "energy_costs": cost_data,
            "environmental_impact": {
                "co2_emissions": co2_emissions
            }
        }
        
        if environment == "Outdoor":
            report_data["outdoor_analysis"] = {
                "glare_index": glare_index,
                "light_pollution": pollution,
                "uniformity": best_option.get('uniformity', 0)
            }
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📊 Download as CSV",
                data=csv,
                file_name=f"{environment.lower()}_lighting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            json_str = json.dumps(report_data, indent=2)
            st.download_button(
                label="📄 Download as JSON",
                data=json_str,
                file_name=f"{environment.lower()}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col3:
            html_report = f"""
            <html>
            <head>
                <title>Lighting Report - {environment}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #1E88E5; }}
                    h2 {{ color: #424242; }}
                    .info {{ background: #f0f8ff; padding: 10px; border-left: 4px solid #1E88E5; margin: 10px 0; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #1E88E5; color: white; }}
                </style>
            </head>
            <body>
                <h1>Lighting Calculation Report - {environment}</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>Project Information</h2>
                <div class="info">
                    <p><b>Area Type:</b> {room_type if environment == 'Indoor' else area_type}</p>
                    <p><b>Category:</b> {building_type if environment == 'Indoor' else outdoor_category}</p>
                    <p><b>Area:</b> {area:.1f} m²</p>
                    <p><b>Required Lux:</b> {required_lux}</p>
                </div>
                
                <h2>Recommended Solution</h2>
                <table>
                    <tr><th>Parameter</th><th>Value</th></tr>
                    <tr><td>Light Type</td><td>{best_option['light_type']}</td></tr>
                    <tr><td>Wattage</td><td>{best_option['wattage']}W</td></tr>
                    <tr><td>Number of Lights</td><td>{best_option['num_lights']}</td></tr>
                    <tr><td>Total Power</td><td>{best_option['total_wattage']}W</td></tr>
                    <tr><td>Actual Lux Achieved</td><td>{best_option['actual_lux']}</td></tr>
                    <tr><td>IP Rating</td><td>{best_option['ip_rating']}</td></tr>
                    <tr><td>Color Temperature</td><td>{best_option['color_temp']}</td></tr>
                </table>
                
                <h2>Energy Analysis</h2>
                <table>
                    <tr><th>Period</th><th>Consumption (kWh)</th><th>Cost (SGD)</th></tr>
                    <tr><td>Daily</td><td>{cost_data['daily_consumption']}</td><td>${cost_data['daily_cost']}</td></tr>
                    <tr><td>Monthly</td><td>{cost_data['monthly_consumption']}</td><td>${cost_data['monthly_cost']}</td></tr>
                    <tr><td>Yearly</td><td>{cost_data['yearly_consumption']}</td><td>${cost_data['yearly_cost']}</td></tr>
                </table>
                
                <p><i>Disclaimer: This report provides estimates based on standard calculations. 
                Always consult with a professional lighting designer for final specifications.</i></p>
            </body>
            </html>
            """
            st.download_button(
                label="🌐 Download as HTML",
                data=html_report,
                file_name=f"{environment.lower()}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )
    
    else:
        # Show welcome message and instructions
        st.markdown("""
        <div class='info-box'>
            <h3>👋 Welcome to LuxSim Pro!</h3>
            <p>This application helps you calculate lighting requirements for both INDOOR and OUTDOOR spaces 
            based on Singapore Standards (SS 531:2014 for indoor, BCA/LTA guidelines for outdoor).</p>
            
            <p><b>Key Features:</b></p>
            <ul>
                <li>🏠 <b>Indoor Spaces:</b> Residential, Office, Commercial, Industrial, Educational, Healthcare</li>
                <li>🌳 <b>Outdoor Spaces:</b> Linkways, Void Decks, Parks, Fitness Corners, Playgrounds, Walkways, 
                High Linkways, Sports Facilities, Car Parks, and more</li>
                <li>📊 Comprehensive calculations with lumen method</li>
                <li>🗺️ 2D layout visualization for both indoor and outdoor</li>
                <li>💰 Energy cost analysis and environmental impact</li>
                <li>📈 Option comparison and recommendations</li>
            </ul>
            
            <p><b>How to use:</b></p>
            <ol>
                <li>Select Indoor or Outdoor environment</li>
                <li>Choose your specific area type from the dropdown</li>
                <li>Enter area dimensions</li>
                <li>Adjust operating parameters as needed</li>
                <li>Click "Calculate Lighting Requirements"</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Display standards reference with tabs
        tab1, tab2 = st.tabs(["🏠 Indoor Standards (SS 531:2014)", "🌳 Outdoor Standards (BCA/LTA)"])
        
        with tab1:
            st.markdown("<h3>Indoor Illuminance Recommendations</h3>", unsafe_allow_html=True)
            for building_type, rooms in INDOOR_STANDARDS.items():
                with st.expander(f"{building_type}"):
                    df = pd.DataFrame([
                        {"Room Type": room, "Recommended Lux": lux}
                        for room, lux in rooms.items()
                    ])
                    st.dataframe(df, use_container_width=True, hide_index=True)
        
        with tab2:
            st.markdown("<h3>Outdoor Illuminance Recommendations</h3>", unsafe_allow_html=True)
            for category, areas in OUTDOOR_STANDARDS.items():
                with st.expander(f"{category}"):
                    df = pd.DataFrame([
                        {"Area Type": area, "Recommended Lux": lux}
                        for area, lux in areas.items()
                    ])
                    st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Tips and best practices
        with st.expander("💡 Lighting Design Tips for Singapore"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **Indoor Best Practices:**
                - Use LED lighting for energy efficiency
                - Consider daylight harvesting
                - Maintenance factor: 0.8 for clean environments
                - Color temperature: 3000K (warm) for residential, 4000K (neutral) for offices
                - CRI >80 for general areas, >90 for retail/healthcare
                """)
            
            with col2:
                st.markdown("""
                **Outdoor Best Practices:**
                - IP65 minimum for outdoor fixtures
                - Consider light pollution reduction
                - Uniformity ratio >0.4 for safety
                - Use shielded fixtures to reduce glare
                - Photocell sensors for automatic operation
                - Consider tropical climate (heat, rain, humidity)
                """)

if __name__ == "__main__":
    main()
