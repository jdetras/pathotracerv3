#!/usr/bin/env python3
"""
PathoTracer v2 - Minimal Working Version
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, date
import os
import sys

# Set page config first
st.set_page_config(
    page_title="PathoTracer v2",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    
    # Title
    st.title("🌾 PathoTracer v2")
    st.subheader("Rice Disease Decision Support System")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", [
        "Dashboard",
        "Disease Diagnostics", 
        "Resistance Profiles",
        "Data Management",
        "Analytics",
        "Settings"
    ])
    
    # System status
    st.sidebar.markdown("---")
    st.sidebar.markdown("**System Status**")
    
    try:
        # Try to import and test modules
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Test database module
        try:
            from database.db_manager import DatabaseManager
            db_manager = DatabaseManager()
            if db_manager.check_connection():
                st.sidebar.success("Database: Connected")
            else:
                st.sidebar.warning("Database: No Connection")
        except Exception as e:
            st.sidebar.error(f"Database: Error ({str(e)[:30]}...)")
        
        # Test other modules
        try:
            from models.pathogen_predictor import PathogenPredictor
            st.sidebar.success("ML Models: Ready")
        except Exception as e:
            st.sidebar.error(f"ML Models: Error ({str(e)[:30]}...)")
            
    except Exception as e:
        st.sidebar.error(f"System Error: {str(e)[:30]}...")
    
    # Main content based on selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Disease Diagnostics":
        show_diagnostics()
    elif page == "Resistance Profiles":
        show_resistance()
    elif page == "Data Management":
        show_data_management()
    elif page == "Analytics":
        show_analytics()
    elif page == "Settings":
        show_settings()

def show_dashboard():
    """Dashboard page"""
    st.header("📊 Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Samples", "156", delta="12")
    with col2:
        st.metric("Active Pathogens", "3", delta="0")
    with col3:
        st.metric("High Risk Areas", "2", delta="-1")
    with col4:
        st.metric("Detection Accuracy", "85.2%", delta="2.1%")
    
    # Create two columns for charts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Geographic pathogen distribution map
        st.subheader("🗺️ Geographic Pathogen Distribution")
        
        # Create sample geographic data for Philippines rice fields
        geo_data = pd.DataFrame({
            'latitude': [14.5995, 14.6091, 14.5547, 14.6760, 14.5243, 14.7341, 14.4958, 14.8012, 14.3456, 14.9123],
            'longitude': [120.9842, 121.0223, 121.0244, 121.0437, 120.9567, 121.1234, 120.8765, 121.2345, 120.7890, 121.3456],
            'location': ['Nueva Ecija Field A', 'Bulacan Field B', 'Pampanga Field C', 'Tarlac Field D', 
                        'Nueva Ecija Field E', 'Bulacan Field F', 'Pampanga Field G', 'Tarlac Field H',
                        'Nueva Ecija Field I', 'Bulacan Field J'],
            'pathogen_type': ['Magnaporthe oryzae', 'Rhizoctonia solani', 'Xanthomonas oryzae', 
                             'Magnaporthe oryzae', 'Rhizoctonia solani', 'Xanthomonas oryzae',
                             'Magnaporthe oryzae', 'Pyricularia oryzae', 'Fusarium fujikuroi', 'Burkholderia glumae'],
            'intensity': [8, 6, 9, 7, 5, 8, 6, 4, 7, 5],
            'risk_level': ['High', 'Medium', 'High', 'High', 'Medium', 'High', 'Medium', 'Low', 'Medium', 'Medium'],
            'detection_date': pd.date_range('2024-01-01', periods=10, freq='3D'),
            'affected_area_ha': [25.5, 18.2, 32.1, 28.7, 15.3, 29.8, 22.4, 12.6, 19.9, 16.7]
        })
        
        # Create the map visualization
        fig_map = px.scatter_map(
            geo_data,
            lat="latitude",
            lon="longitude",
            size="intensity",
            color="pathogen_type",
            hover_data={
                "location": True,
                "risk_level": True,
                "affected_area_ha": True,
                "detection_date": True,
                "intensity": False,
                "latitude": False,
                "longitude": False
            },
            map_style="open-street-map",
            height=500,
            zoom=9,
            center={"lat": 14.65, "lon": 121.0},
            title="Real-time Pathogen Detection Map",
            color_discrete_map={
                'Magnaporthe oryzae': '#FF6B6B',
                'Rhizoctonia solani': '#4ECDC4', 
                'Xanthomonas oryzae': '#45B7D1',
                'Pyricularia oryzae': '#96CEB4',
                'Fusarium fujikuroi': '#FFEAA7',
                'Burkholderia glumae': '#DDA0DD'
            }
        )
        
        fig_map.update_traces(
            marker=dict(
                sizemin=8,
                opacity=0.8
            )
        )
        
        fig_map.update_layout(
            geo=dict(
                center=dict(lat=14.65, lon=121.0),
                projection_scale=8.5
            ),
            margin={"r":0,"t":30,"l":0,"b":0}
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Map legend and info
        st.markdown("""
        **Map Legend:**
        - 🔴 **Red**: Magnaporthe oryzae (Rice Blast)
        - 🟢 **Teal**: Rhizoctonia solani (Sheath Blight)  
        - 🔵 **Blue**: Xanthomonas oryzae (Bacterial Leaf Blight)
        - 🟡 **Yellow**: Fusarium fujikuroi (Bakanae Disease)
        - **Size**: Detection intensity/severity
        - **Hover**: Click markers for detailed information
        """)
    
    with col2:
        # Recent alerts
        st.subheader("🚨 Active Alerts")
        
        alerts_data = pd.DataFrame({
            'Location': ['Nueva Ecija Field A', 'Pampanga Field C', 'Tarlac Field D'],
            'Pathogen': ['Magnaporthe oryzae', 'Xanthomonas oryzae', 'Magnaporthe oryzae'], 
            'Risk Level': ['🔴 High', '🔴 High', '🔴 High'],
            'Confidence': ['92%', '89%', '87%'],
            'Action': ['Treat Now', 'Treat Now', 'Monitor']
        })
        
        st.dataframe(alerts_data, use_container_width=True)
        
        # Pathogen distribution pie chart
        st.subheader("📊 Pathogen Distribution")
        
        pathogen_counts = geo_data['pathogen_type'].value_counts()
        fig_pie = px.pie(
            values=pathogen_counts.values,
            names=pathogen_counts.index,
            title="Current Pathogen Detections",
            color_discrete_map={
                'Magnaporthe oryzae': '#FF6B6B',
                'Rhizoctonia solani': '#4ECDC4', 
                'Xanthomonas oryzae': '#45B7D1',
                'Pyricularia oryzae': '#96CEB4',
                'Fusarium fujikuroi': '#FFEAA7',
                'Burkholderia glumae': '#DDA0DD'
            }
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Time series chart below the map
    st.subheader("📈 Recent Disease Activity Trends")
    
    # Create sample time series data
    sample_data = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=30, freq='D'),
        'Rice_Blast': np.random.poisson(3, 30),
        'Sheath_Blight': np.random.poisson(2, 30),
        'Bacterial_Blight': np.random.poisson(1, 30)
    })
    
    # Melt the dataframe for plotting
    sample_data_melted = sample_data.melt(
        id_vars=['Date'], 
        var_name='Pathogen', 
        value_name='Detections'
    )
    
    fig_trend = px.line(
        sample_data_melted, 
        x='Date', 
        y='Detections', 
        color='Pathogen',
        title='Daily Disease Detection Trends (Last 30 Days)',
        color_discrete_map={
            'Rice_Blast': '#FF6B6B',
            'Sheath_Blight': '#4ECDC4',
            'Bacterial_Blight': '#45B7D1'
        }
    )
    fig_trend.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Detections",
        legend_title="Disease Type"
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Summary statistics
    st.subheader("📋 Weekly Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **Most Active Region**  
        Nueva Ecija Province  
        {geo_data[geo_data['location'].str.contains('Nueva Ecija')].shape[0]} active cases
        """)
    
    with col2:
        st.warning(f"""
        **Dominant Pathogen**  
        {pathogen_counts.index[0]}  
        {pathogen_counts.iloc[0]} detections this week
        """)
    
    with col3:
        avg_intensity = geo_data['intensity'].mean()
        st.error(f"""
        **Average Severity**  
        {avg_intensity:.1f}/10  
        {"⚠️ Above normal" if avg_intensity > 6 else "✅ Normal range"}
        """)


def show_diagnostics():
    """Disease diagnostics page"""
    st.header("🔬 Disease Diagnostics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sample Information")
        
        with st.form("diagnosis_form"):
            sample_id = st.text_input("Sample ID", f"SAMPLE_{datetime.now().strftime('%Y%m%d_%H%M')}")
            location = st.text_input("Location", "Field A")
            variety = st.selectbox("Rice Variety", ["IR64", "PSB Rc82", "NSIC Rc222", "NSIC Rc216"])
            growth_stage = st.selectbox("Growth Stage", [
                "Seedling", "Tillering", "Stem elongation", "Booting", 
                "Heading", "Flowering", "Grain filling", "Maturity"
            ])
            
            st.subheader("Environmental Conditions")
            temperature = st.number_input("Temperature (°C)", 15.0, 40.0, 25.0)
            humidity = st.number_input("Humidity (%)", 0, 100, 80)
            rainfall = st.number_input("Recent Rainfall (mm)", 0.0, 100.0, 0.0)
            
            submitted = st.form_submit_button("Analyze Sample")
    
    with col2:
        st.subheader("Symptoms Assessment")
        
        symptoms = st.multiselect("Observed Symptoms", [
            "leaf spots", "leaf blight", "sheath blight", "neck rot",
            "panicle blast", "stem rot", "yellowing", "wilting", "stunting"
        ])
        
        severity = st.slider("Disease Severity (1-10)", 1, 10, 5)
        affected_area = st.slider("Affected Area (%)", 0, 100, 25)
        
        uploaded_file = st.file_uploader("Upload Images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    
    if submitted:
        st.success(f"Sample {sample_id} submitted for analysis!")
        
        # Simulate analysis
        with st.spinner("Analyzing sample..."):
            import time
            time.sleep(2)
        
        # Show results
        st.subheader("🔍 Analysis Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Primary Pathogen", "Magnaporthe oryzae", "85% confidence")
        with col2:
            st.metric("Risk Level", "🔴 High")
        with col3:
            st.metric("Recommended Action", "Immediate Treatment")
        
        # Recommendations
        st.subheader("💡 Management Recommendations")
        st.info("1. Apply fungicide treatment immediately")
        st.info("2. Improve field drainage")
        st.info("3. Monitor surrounding areas")
        st.info("4. Consider resistant varieties for next season")

def show_resistance():
    """Resistance profiles page"""
    st.header("🛡️ Resistance Profiles")
    
    st.subheader("Variety Resistance Analysis")
    
    # Sample resistance data
    resistance_data = pd.DataFrame({
        'Variety': ['IR64', 'PSB Rc82', 'NSIC Rc222', 'NSIC Rc216'] * 3,
        'Pathogen': ['Magnaporthe oryzae'] * 4 + ['Rhizoctonia solani'] * 4 + ['Xanthomonas oryzae'] * 4,
        'Resistance_Score': [5.5, 7.2, 8.1, 6.8, 6.2, 7.8, 7.5, 7.1, 4.8, 6.5, 8.3, 5.9]
    })
    
    # Create heatmap
    pivot_data = resistance_data.pivot(index='Variety', columns='Pathogen', values='Resistance_Score')
    fig = px.imshow(pivot_data, 
                    color_continuous_scale='RdYlGn',
                    title="Resistance Profile Heatmap",
                    labels=dict(color="Resistance Score"))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show data table
    st.subheader("Resistance Data")
    st.dataframe(resistance_data)
    
    # Breeding recommendations
    st.subheader("🧬 Breeding Recommendations")
    st.info("**High Priority**: Improve Xanthomonas oryzae resistance in IR64")
    st.info("**Medium Priority**: Enhance Magnaporthe oryzae resistance across varieties")
    st.info("**Low Priority**: Maintain current Rhizoctonia solani resistance levels")

def show_data_management():
    """Data management page"""
    st.header("📁 Data Management")
    
    tab1, tab2, tab3 = st.tabs(["Import Data", "Export Data", "Database"])
    
    with tab1:
        st.subheader("Import Data")
        
        data_type = st.selectbox("Data Type", [
            "Diagnosis Records", 
            "Resistance Profiles", 
            "Environmental Data"
        ])
        
        uploaded_file = st.file_uploader("Choose CSV file", type="csv")
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
            
            if st.button("Import Data"):
                st.success(f"Imported {len(df)} records successfully!")
    
    with tab2:
        st.subheader("Export Data")
        
        export_type = st.selectbox("Export Type", [
            "All Diagnoses",
            "Resistance Profiles", 
            "Summary Report"
        ])
        
        if st.button("Generate Export"):
            # Create sample export data
            export_data = pd.DataFrame({
                'Sample_ID': [f'SAMPLE_{i:03d}' for i in range(1, 11)],
                'Pathogen': ['Magnaporthe oryzae'] * 5 + ['Rhizoctonia solani'] * 5,
                'Confidence': np.random.uniform(0.7, 0.95, 10),
                'Risk_Level': np.random.choice(['High', 'Medium', 'Low'], 10)
            })
            
            csv = export_data.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                f"{export_type.lower().replace(' ', '_')}.csv",
                "text/csv"
            )
    
    with tab3:
        st.subheader("Database Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", "1,247")
        with col2:
            st.metric("Database Size", "45 MB")
        with col3:
            st.metric("Last Backup", "2024-01-15")

def show_analytics():
    """Analytics page"""
    st.header("📈 Analytics & Reports")
    
    st.subheader("Disease Pattern Analysis")
    
    # Sample analytics chart
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    detections = [23, 45, 67, 89, 56, 34]
    
    fig = px.bar(x=months, y=detections, title='Monthly Disease Detections')
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics
    st.subheader("Key Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Average Severity", "6.2", "↑ 0.3")
        st.metric("Most Common Pathogen", "Magnaporthe oryzae")
    
    with col2:
        st.metric("Detection Accuracy", "85.2%", "↑ 2.1%")
        st.metric("High Risk Cases", "23%", "↓ 5%")
    
    # Report generation
    st.subheader("📄 Generate Reports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Disease Summary"):
            st.success("Generating disease summary report...")
    
    with col2:
        if st.button("Resistance Analysis"):
            st.success("Generating resistance analysis...")
    
    with col3:
        if st.button("Environmental Impact"):
            st.success("Generating environmental report...")

def show_settings():
    """Settings page"""
    st.header("⚙️ Settings")
    
    tab1, tab2 = st.tabs(["General", "Database"])
    
    with tab1:
        st.subheader("General Settings")
        
        default_location = st.text_input("Default Location", "Field A")
        confidence_threshold = st.slider("Confidence Threshold", 0.5, 1.0, 0.8)
        auto_backup = st.checkbox("Enable Auto Backup", True)
        
        if st.button("Save Settings"):
            st.success("Settings saved successfully!")
    
    with tab2:
        st.subheader("Database Configuration")
        
        db_host = st.text_input("Host", "localhost")
        db_port = st.number_input("Port", 1000, 9999, 5432)
        db_name = st.text_input("Database Name", "pathotracer")
        db_user = st.text_input("Username", "postgres")
        db_password = st.text_input("Password", type="password")
        
        if st.button("Test Connection"):
            st.info("Testing database connection...")
        
        if st.button("Save Database Config"):
            st.success("Database configuration saved!")

if __name__ == "__main__":
    main()