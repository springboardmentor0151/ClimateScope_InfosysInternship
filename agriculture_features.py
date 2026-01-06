# 🌾 AGRICULTURE ANALYSIS FEATURES
# This file contains agriculture-specific analysis functions

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Crop Requirements Database
CROP_REQUIREMENTS = {
    'Wheat': {
        'temp_min': 15, 'temp_max': 25, 'temp_optimal': 20,
        'humidity_min': 50, 'humidity_max': 70,
        'rainfall_min': 300, 'rainfall_max': 600,
        'season': 'Winter',
        'growth_days': 120,
        'icon': '🌾'
    },
    'Rice': {
        'temp_min': 20, 'temp_max': 35, 'temp_optimal': 27,
        'humidity_min': 60, 'humidity_max': 90,
        'rainfall_min': 1000, 'rainfall_max': 2000,
        'season': 'Summer',
        'growth_days': 150,
        'icon': '🌾'
    },
    'Corn (Maize)': {
        'temp_min': 18, 'temp_max': 32, 'temp_optimal': 25,
        'humidity_min': 50, 'humidity_max': 70,
        'rainfall_min': 500, 'rainfall_max': 800,
        'season': 'Summer',
        'growth_days': 90,
        'icon': '🌽'
    },
    'Cotton': {
        'temp_min': 21, 'temp_max': 35, 'temp_optimal': 28,
        'humidity_min': 50, 'humidity_max': 80,
        'rainfall_min': 500, 'rainfall_max': 1000,
        'season': 'Summer',
        'growth_days': 180,
        'icon': '🌱'
    },
    'Sugarcane': {
        'temp_min': 20, 'temp_max': 35, 'temp_optimal': 27,
        'humidity_min': 60, 'humidity_max': 90,
        'rainfall_min': 1500, 'rainfall_max': 2500,
        'season': 'Summer',
        'growth_days': 365,
        'icon': '🎋'
    },
    'Potato': {
        'temp_min': 15, 'temp_max': 25, 'temp_optimal': 20,
        'humidity_min': 60, 'humidity_max': 80,
        'rainfall_min': 500, 'rainfall_max': 700,
        'season': 'Winter',
        'growth_days': 90,
        'icon': '🥔'
    },
    'Tomato': {
        'temp_min': 18, 'temp_max': 27, 'temp_optimal': 22,
        'humidity_min': 60, 'humidity_max': 85,
        'rainfall_min': 600, 'rainfall_max': 1000,
        'season': 'Spring',
        'growth_days': 75,
        'icon': '🍅'
    },
    'Soybean': {
        'temp_min': 20, 'temp_max': 30, 'temp_optimal': 25,
        'humidity_min': 50, 'humidity_max': 70,
        'rainfall_min': 450, 'rainfall_max': 700,
        'season': 'Summer',
        'growth_days': 120,
        'icon': '🫘'
    },
    'Barley': {
        'temp_min': 12, 'temp_max': 20, 'temp_optimal': 16,
        'humidity_min': 50, 'humidity_max': 70,
        'rainfall_min': 300, 'rainfall_max': 500,
        'season': 'Winter',
        'growth_days': 90,
        'icon': '🌾'
    },
    'Sunflower': {
        'temp_min': 20, 'temp_max': 30, 'temp_optimal': 25,
        'humidity_min': 40, 'humidity_max': 60,
        'rainfall_min': 400, 'rainfall_max': 600,
        'season': 'Summer',
        'growth_days': 100,
        'icon': '🌻'
    }
}


def calculate_crop_suitability(df, crop_name):
    """Calculate suitability score for a crop based on weather conditions"""
    crop = CROP_REQUIREMENTS[crop_name]
    
    # Temperature suitability (0-100)
    temp_score = np.where(
        (df['temperature_celsius'] >= crop['temp_min']) & (df['temperature_celsius'] <= crop['temp_max']),
        100 - abs(df['temperature_celsius'] - crop['temp_optimal']) * 5,
        0
    )
    temp_score = np.clip(temp_score, 0, 100)
    
    # Humidity suitability (0-100)
    humidity_score = np.where(
        (df['humidity'] >= crop['humidity_min']) & (df['humidity'] <= crop['humidity_max']),
        100,
        np.where(df['humidity'] < crop['humidity_min'], 
                (df['humidity'] / crop['humidity_min']) * 100,
                100 - ((df['humidity'] - crop['humidity_max']) / crop['humidity_max']) * 100)
    )
    humidity_score = np.clip(humidity_score, 0, 100)
    
    # Overall suitability (weighted average)
    suitability = (temp_score * 0.6 + humidity_score * 0.4)
    
    return suitability


def get_crop_recommendations(country_data, top_n=5):
    """Get top N crop recommendations for a country"""
    recommendations = []
    
    for crop_name, crop_info in CROP_REQUIREMENTS.items():
        suitability = calculate_crop_suitability(country_data, crop_name)
        avg_suitability = suitability.mean()
        
        recommendations.append({
            'Crop': f"{crop_info['icon']} {crop_name}",
            'Suitability Score': round(avg_suitability, 1),
            'Optimal Temp': f"{crop_info['temp_optimal']}°C",
            'Season': crop_info['season'],
            'Growth Days': crop_info['growth_days']
        })
    
    recommendations_df = pd.DataFrame(recommendations)
    recommendations_df = recommendations_df.sort_values('Suitability Score', ascending=False).head(top_n)
    
    return recommendations_df


def calculate_frost_risk(df):
    """Calculate frost risk days (temp < 0°C)"""
    return len(df[df['temperature_celsius'] < 0])


def calculate_heat_stress_days(df, threshold=35):
    """Calculate heat stress days (temp > threshold)"""
    return len(df[df['temperature_celsius'] > threshold])


def calculate_drought_risk(df, rainfall_threshold=10):
    """Calculate drought risk based on low rainfall days"""
    # Group by month and calculate monthly rainfall
    df_copy = df.copy()
    df_copy['year_month'] = df_copy['last_updated_dt'].dt.to_period('M')
    monthly_rain = df_copy.groupby('year_month')['precip_mm'].sum()
    
    drought_months = len(monthly_rain[monthly_rain < rainfall_threshold])
    return drought_months


def show_agriculture_dashboard(df, filters):
    """Main Agriculture Analysis Dashboard"""
    st.title("🌾 Agriculture Intelligence Dashboard")
    st.markdown("**Smart Farming Insights Based on Weather Data**")
    
    st.markdown("---")
    
    # Agriculture Overview Metrics
    st.header("📊 Agricultural Weather Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    avg_temp = df['temperature_celsius'].mean()
    avg_humidity = df['humidity'].mean()
    total_rainfall = df['precip_mm'].sum()
    frost_days = calculate_frost_risk(df)
    heat_stress_days = calculate_heat_stress_days(df)
    
    col1.metric("Avg Temperature", f"{avg_temp:.1f}°C", 
               delta="Optimal" if 15 <= avg_temp <= 30 else "Check")
    col2.metric("Avg Humidity", f"{avg_humidity:.0f}%",
               delta="Good" if 50 <= avg_humidity <= 80 else "Monitor")
    col3.metric("Total Rainfall", f"{total_rainfall:.0f} mm")
    col4.metric("Frost Risk Days", f"{frost_days}", 
               delta="Low" if frost_days < 10 else "High", delta_color="inverse")
    col5.metric("Heat Stress Days", f"{heat_stress_days}",
               delta="Low" if heat_stress_days < 20 else "High", delta_color="inverse")
    
    st.markdown("---")
    
    # Crop Suitability Analysis
    st.header("🌱 Crop Suitability Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Top 5 Recommended Crops")
        recommendations = get_crop_recommendations(df, top_n=5)
        
        # Color code suitability scores
        def color_suitability(val):
            if val >= 80:
                return 'background-color: #90EE90'  # Light green
            elif val >= 60:
                return 'background-color: #FFD700'  # Gold
            elif val >= 40:
                return 'background-color: #FFA500'  # Orange
            else:
                return 'background-color: #FF6B6B'  # Red
        
        styled_recommendations = recommendations.style.map(
            color_suitability, 
            subset=['Suitability Score']
        )
        
        st.dataframe(styled_recommendations, use_container_width=True, hide_index=True)
        
        # Suitability explanation
        st.info("""
        **Suitability Score Guide:**
        - 🟢 80-100: Excellent conditions
        - 🟡 60-79: Good conditions
        - 🟠 40-59: Moderate conditions
        - 🔴 0-39: Poor conditions
        """)
    
    with col2:
        st.subheader("Crop Suitability Chart")
        
        fig = px.bar(
            recommendations,
            y='Crop',
            x='Suitability Score',
            orientation='h',
            title='Crop Suitability Scores',
            color='Suitability Score',
            color_continuous_scale='RdYlGn',
            range_color=[0, 100]
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Seasonal Crop Planning
    st.header("📅 Seasonal Crop Planning Calendar")
    
    # Calculate monthly averages
    monthly_data = df.groupby('month').agg({
        'temperature_celsius': 'mean',
        'humidity': 'mean',
        'precip_mm': 'sum'
    }).reset_index()
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_data['month_name'] = monthly_data['month'].apply(lambda x: months[x-1] if 1 <= x <= 12 else f'M{x}')
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Temperature (°C)', 'Humidity (%)', 'Rainfall (mm)'),
        vertical_spacing=0.1
    )
    
    # Temperature
    fig.add_trace(
        go.Scatter(x=monthly_data['month_name'], y=monthly_data['temperature_celsius'],
                  mode='lines+markers', name='Temperature', line=dict(color='#FF6B6B', width=3)),
        row=1, col=1
    )
    
    # Humidity
    fig.add_trace(
        go.Scatter(x=monthly_data['month_name'], y=monthly_data['humidity'],
                  mode='lines+markers', name='Humidity', line=dict(color='#4ECDC4', width=3)),
        row=2, col=1
    )
    
    # Rainfall
    fig.add_trace(
        go.Bar(x=monthly_data['month_name'], y=monthly_data['precip_mm'],
              name='Rainfall', marker=dict(color='#45B7D1')),
        row=3, col=1
    )
    
    fig.update_layout(height=800, showlegend=False, title_text="Monthly Weather Patterns for Crop Planning")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Risk Assessment
    st.header("⚠️ Agricultural Risk Assessment")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🥶 Frost Risk")
        frost_days = calculate_frost_risk(df)
        frost_risk_pct = (frost_days / len(df)) * 100
        
        if frost_risk_pct < 5:
            st.success(f"✅ Low Risk: {frost_days} days ({frost_risk_pct:.1f}%)")
            st.info("Minimal frost damage expected. Safe for most crops.")
        elif frost_risk_pct < 15:
            st.warning(f"⚠️ Moderate Risk: {frost_days} days ({frost_risk_pct:.1f}%)")
            st.info("Consider frost-resistant varieties or protective measures.")
        else:
            st.error(f"🚨 High Risk: {frost_days} days ({frost_risk_pct:.1f}%)")
            st.info("Significant frost risk. Delay planting or use protection.")
    
    with col2:
        st.subheader("🔥 Heat Stress Risk")
        heat_days = calculate_heat_stress_days(df, threshold=35)
        heat_risk_pct = (heat_days / len(df)) * 100
        
        if heat_risk_pct < 10:
            st.success(f"✅ Low Risk: {heat_days} days ({heat_risk_pct:.1f}%)")
            st.info("Minimal heat stress. Good growing conditions.")
        elif heat_risk_pct < 25:
            st.warning(f"⚠️ Moderate Risk: {heat_days} days ({heat_risk_pct:.1f}%)")
            st.info("Ensure adequate irrigation during hot periods.")
        else:
            st.error(f"🚨 High Risk: {heat_days} days ({heat_risk_pct:.1f}%)")
            st.info("High heat stress. Consider heat-tolerant varieties.")
    
    with col3:
        st.subheader("💧 Drought Risk")
        drought_months = calculate_drought_risk(df, rainfall_threshold=50)
        total_months = df['last_updated_dt'].dt.to_period('M').nunique()
        drought_risk_pct = (drought_months / total_months) * 100 if total_months > 0 else 0
        
        if drought_risk_pct < 20:
            st.success(f"✅ Low Risk: {drought_months} months ({drought_risk_pct:.1f}%)")
            st.info("Adequate rainfall. Normal irrigation needed.")
        elif drought_risk_pct < 40:
            st.warning(f"⚠️ Moderate Risk: {drought_months} months ({drought_risk_pct:.1f}%)")
            st.info("Plan for supplemental irrigation systems.")
        else:
            st.error(f"🚨 High Risk: {drought_months} months ({drought_risk_pct:.1f}%)")
            st.info("Critical drought risk. Invest in irrigation infrastructure.")
    
    st.markdown("---")
    
    # Irrigation Planning
    st.header("💧 Irrigation Planning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Monthly Rainfall vs Crop Water Needs")
        
        # Calculate monthly rainfall
        monthly_rain = df.groupby('month')['precip_mm'].sum().reset_index()
        monthly_rain['month_name'] = monthly_rain['month'].apply(lambda x: months[x-1] if 1 <= x <= 12 else f'M{x}')
        
        # Add typical crop water needs (example: 100mm/month)
        monthly_rain['crop_water_need'] = 100
        monthly_rain['deficit'] = monthly_rain['crop_water_need'] - monthly_rain['precip_mm']
        monthly_rain['deficit'] = monthly_rain['deficit'].clip(lower=0)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly_rain['month_name'], y=monthly_rain['precip_mm'],
                            name='Rainfall', marker_color='#4ECDC4'))
        fig.add_trace(go.Scatter(x=monthly_rain['month_name'], y=monthly_rain['crop_water_need'],
                                mode='lines', name='Crop Water Need', line=dict(color='red', dash='dash', width=3)))
        
        fig.update_layout(
            title='Rainfall vs Crop Water Requirements',
            xaxis_title='Month',
            yaxis_title='Water (mm)',
            height=400,
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Irrigation Recommendations")
        
        total_deficit = monthly_rain['deficit'].sum()
        months_needing_irrigation = len(monthly_rain[monthly_rain['deficit'] > 0])
        
        st.metric("Total Water Deficit", f"{total_deficit:.0f} mm/year")
        st.metric("Months Needing Irrigation", f"{months_needing_irrigation}/12")
        
        if months_needing_irrigation == 0:
            st.success("✅ Rainfall sufficient for most crops. Minimal irrigation needed.")
        elif months_needing_irrigation <= 4:
            st.info("💧 Supplemental irrigation recommended for 4 months.")
            st.write("**Suggested Actions:**")
            st.write("- Install drip irrigation system")
            st.write("- Build small water storage")
            st.write("- Mulching to retain moisture")
        elif months_needing_irrigation <= 8:
            st.warning("⚠️ Significant irrigation needed for 5-8 months.")
            st.write("**Suggested Actions:**")
            st.write("- Install comprehensive irrigation system")
            st.write("- Build large water storage/reservoir")
            st.write("- Consider drought-resistant crops")
        else:
            st.error("🚨 Heavy irrigation required year-round.")
            st.write("**Suggested Actions:**")
            st.write("- Major irrigation infrastructure needed")
            st.write("- Groundwater or canal access essential")
            st.write("- Focus on drought-tolerant crops")
    
    st.markdown("---")
    
    # Growing Degree Days (GDD)
    st.header("🌡️ Growing Degree Days (GDD) Analysis")
    
    st.info("""
    **Growing Degree Days (GDD)** measure heat accumulation for crop development.
    Formula: GDD = (Tmax + Tmin)/2 - Base Temperature (typically 10°C)
    """)
    
    # Calculate GDD (simplified - using daily average temp)
    base_temp = 10
    df_gdd = df.copy()
    df_gdd['gdd'] = (df_gdd['temperature_celsius'] - base_temp).clip(lower=0)
    
    # Monthly GDD accumulation
    monthly_gdd = df_gdd.groupby('month')['gdd'].sum().reset_index()
    monthly_gdd['month_name'] = monthly_gdd['month'].apply(lambda x: months[x-1] if 1 <= x <= 12 else f'M{x}')
    
    fig = px.bar(
        monthly_gdd,
        x='month_name',
        y='gdd',
        title='Monthly Growing Degree Days Accumulation',
        labels={'gdd': 'GDD', 'month_name': 'Month'},
        color='gdd',
        color_continuous_scale='YlOrRd'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # GDD interpretation
    total_gdd = df_gdd['gdd'].sum()
    st.metric("Total Annual GDD", f"{total_gdd:.0f}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**Wheat:** Needs ~1500-2000 GDD")
        if total_gdd >= 1500:
            st.success("✅ Sufficient for wheat")
        else:
            st.warning("⚠️ May be insufficient")
    
    with col2:
        st.write("**Corn:** Needs ~2500-3000 GDD")
        if total_gdd >= 2500:
            st.success("✅ Sufficient for corn")
        else:
            st.warning("⚠️ May be insufficient")
    
    with col3:
        st.write("**Rice:** Needs ~3000-3500 GDD")
        if total_gdd >= 3000:
            st.success("✅ Sufficient for rice")
        else:
            st.warning("⚠️ May be insufficient")
    
    st.markdown("---")
    
    # Pest and Disease Risk
    st.header("🐛 Pest & Disease Risk Assessment")
    
    # High humidity + moderate temp = disease risk
    disease_risk_days = len(df[(df['humidity'] > 80) & (df['temperature_celsius'] > 20) & (df['temperature_celsius'] < 30)])
    disease_risk_pct = (disease_risk_days / len(df)) * 100
    
    # High temp + low humidity = pest risk
    pest_risk_days = len(df[(df['temperature_celsius'] > 30) & (df['humidity'] < 50)])
    pest_risk_pct = (pest_risk_days / len(df)) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🦠 Disease Risk")
        st.metric("High Risk Days", f"{disease_risk_days} ({disease_risk_pct:.1f}%)")
        
        if disease_risk_pct < 15:
            st.success("✅ Low disease pressure")
            st.info("Standard preventive measures sufficient.")
        elif disease_risk_pct < 30:
            st.warning("⚠️ Moderate disease risk")
            st.info("**Recommendations:**\n- Regular crop monitoring\n- Fungicide application as needed\n- Improve air circulation")
        else:
            st.error("🚨 High disease risk")
            st.info("**Recommendations:**\n- Intensive monitoring\n- Preventive fungicide program\n- Disease-resistant varieties\n- Proper spacing and drainage")
    
    with col2:
        st.subheader("🐛 Pest Risk")
        st.metric("High Risk Days", f"{pest_risk_days} ({pest_risk_pct:.1f}%)")
        
        if pest_risk_pct < 15:
            st.success("✅ Low pest pressure")
            st.info("Standard IPM practices sufficient.")
        elif pest_risk_pct < 30:
            st.warning("⚠️ Moderate pest risk")
            st.info("**Recommendations:**\n- Regular scouting\n- Pheromone traps\n- Targeted pesticide use")
        else:
            st.error("🚨 High pest risk")
            st.info("**Recommendations:**\n- Intensive pest monitoring\n- Integrated Pest Management (IPM)\n- Biological control agents\n- Timely pesticide application")
    
    st.markdown("---")
    
    # Actionable Insights
    st.header("💡 Actionable Farming Insights")
    
    insights = []
    
    # Temperature-based insights
    if avg_temp < 15:
        insights.append(("❄️", "Cool Climate", "Focus on cold-season crops like wheat, barley, and potatoes. Consider greenhouse farming for warm-season crops."))
    elif avg_temp > 30:
        insights.append(("🔥", "Hot Climate", "Prioritize heat-tolerant crops like sorghum, millet, and certain cotton varieties. Ensure adequate irrigation."))
    else:
        insights.append(("🌡️", "Moderate Climate", "Ideal for a wide variety of crops. Diversify your crop portfolio for risk management."))
    
    # Rainfall-based insights
    avg_monthly_rain = total_rainfall / 12
    if avg_monthly_rain < 50:
        insights.append(("💧", "Low Rainfall", "Invest in irrigation infrastructure. Consider drought-resistant crops and water conservation techniques."))
    elif avg_monthly_rain > 150:
        insights.append(("🌧️", "High Rainfall", "Ensure proper drainage systems. Watch for waterlogging and fungal diseases."))
    
    # Humidity-based insights
    if avg_humidity > 75:
        insights.append(("💨", "High Humidity", "Increase plant spacing for air circulation. Monitor closely for fungal diseases. Consider fungicide program."))
    elif avg_humidity < 50:
        insights.append(("🏜️", "Low Humidity", "Implement mulching to retain soil moisture. Consider drip irrigation for water efficiency."))
    
    # Display insights
    for icon, title, description in insights:
        st.markdown(f"### {icon} {title}")
        st.info(description)
    
    st.markdown("---")
    
    # Export Report
    st.header("📥 Export Agriculture Report")
    
    # Create summary report
    report_data = {
        'Metric': [
            'Average Temperature',
            'Average Humidity',
            'Total Annual Rainfall',
            'Frost Risk Days',
            'Heat Stress Days',
            'Drought Risk Months',
            'Disease Risk Days',
            'Pest Risk Days',
            'Total Growing Degree Days'
        ],
        'Value': [
            f"{avg_temp:.1f}°C",
            f"{avg_humidity:.0f}%",
            f"{total_rainfall:.0f} mm",
            f"{frost_days}",
            f"{heat_stress_days}",
            f"{drought_months}",
            f"{disease_risk_days}",
            f"{pest_risk_days}",
            f"{total_gdd:.0f}"
        ],
        'Status': [
            "Optimal" if 15 <= avg_temp <= 30 else "Monitor",
            "Good" if 50 <= avg_humidity <= 80 else "Monitor",
            "Adequate" if total_rainfall > 600 else "Low",
            "Low" if frost_days < 10 else "High",
            "Low" if heat_stress_days < 20 else "High",
            "Low" if drought_months < 3 else "High",
            "Low" if disease_risk_pct < 15 else "High",
            "Low" if pest_risk_pct < 15 else "High",
            "Good" if total_gdd > 2000 else "Limited"
        ]
    }
    
    report_df = pd.DataFrame(report_data)
    
    st.dataframe(report_df, use_container_width=True, hide_index=True)
    
    # Download button
    csv_report = report_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Agriculture Report (CSV)",
        data=csv_report,
        file_name="agriculture_weather_report.csv",
        mime="text/csv",
        help="Download comprehensive agriculture analysis report"
    )
    
    st.markdown("---")
    st.success("🌾 **Agriculture Dashboard Complete!** Use these insights to make data-driven farming decisions.")
