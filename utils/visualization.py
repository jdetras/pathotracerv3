# Save this as: utils/visualization.py

#!/usr/bin/env python3
"""
Visualization Tools for PathoTracer v2
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class VisualizationTools:
    """Handles visualization creation for PathoTracer"""
    
    def __init__(self):
        """Initialize visualization tools"""
        self.color_scheme = {
            'primary': '#2E8B57',
            'secondary': '#4682B4', 
            'warning': '#FF8C00',
            'danger': '#DC143C',
            'success': '#32CD32'
        }
    
    def create_pathogen_distribution_chart(self, data: Dict) -> go.Figure:
        """Create pathogen distribution pie chart"""
        if not data:
            return go.Figure()
        
        fig = px.pie(
            values=list(data.values()),
            names=list(data.keys()),
            title="Pathogen Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )
        
        return fig
    
    def create_risk_level_chart(self, data: Dict) -> go.Figure:
        """Create risk level distribution chart"""
        if not data:
            return go.Figure()
        
        colors = {
            'High': self.color_scheme['danger'],
            'Medium': self.color_scheme['warning'],
            'Low': self.color_scheme['success']
        }
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(data.keys()),
                y=list(data.values()),
                marker_color=[colors.get(k, self.color_scheme['primary']) for k in data.keys()]
            )
        ])
        
        fig.update_layout(
            title="Risk Level Distribution",
            xaxis_title="Risk Level",
            yaxis_title="Count"
        )
        
        return fig
    
    def create_severity_trend_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create severity trend over time"""
        if df.empty:
            return go.Figure()
        
        fig = px.line(
            df,
            x='date',
            y='severity',
            title="Disease Severity Trend",
            color_discrete_sequence=[self.color_scheme['primary']]
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Severity Score"
        )
        
        return fig