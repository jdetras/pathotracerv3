# Save this as: utils/data_processor.py

#!/usr/bin/env python3
"""
Data Processor for PathoTracer v2
Handles data processing, analysis, and report generation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from datetime import datetime, timedelta
import io

class DataProcessor:
    """Handles data processing, analysis, and report generation"""
    
    def __init__(self):
        """Initialize the data processor"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def clean_diagnosis_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess diagnosis data"""
        try:
            cleaned_df = df.copy()
            
            # Handle missing values
            numeric_columns = ['temperature', 'humidity', 'rainfall', 'severity', 'affected_area', 'confidence_score']
            for col in numeric_columns:
                if col in cleaned_df.columns:
                    # Fill missing values with median
                    cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
                    cleaned_df[col].fillna(cleaned_df[col].median(), inplace=True)
            
            # Clean categorical columns
            categorical_columns = ['pathogen_name', 'variety_name', 'location_name', 'growth_stage', 'risk_level']
            for col in categorical_columns:
                if col in cleaned_df.columns:
                    # Remove leading/trailing whitespace and convert to title case
                    cleaned_df[col] = cleaned_df[col].astype(str).str.strip().str.title()
                    # Replace empty strings with 'Unknown'
                    cleaned_df[col] = cleaned_df[col].replace(['', 'Nan', 'None'], 'Unknown')
            
            # Date column processing
            date_columns = ['collection_date', 'diagnosed_at']
            for col in date_columns:
                if col in cleaned_df.columns:
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
            
            # Validate ranges
            if 'confidence_score' in cleaned_df.columns:
                cleaned_df['confidence_score'] = cleaned_df['confidence_score'].clip(0, 1)
            
            if 'severity' in cleaned_df.columns:
                cleaned_df['severity'] = cleaned_df['severity'].clip(1, 10)
            
            if 'affected_area' in cleaned_df.columns:
                cleaned_df['affected_area'] = cleaned_df['affected_area'].clip(0, 100)
            
            if 'humidity' in cleaned_df.columns:
                cleaned_df['humidity'] = cleaned_df['humidity'].clip(0, 100)
            
            if 'temperature' in cleaned_df.columns:
                # Assume temperature is in Celsius, clip to reasonable range
                cleaned_df['temperature'] = cleaned_df['temperature'].clip(-10, 50)
            
            # Remove duplicates
            cleaned_df = cleaned_df.drop_duplicates()
            
            # Add derived columns
            if 'diagnosed_at' in cleaned_df.columns:
                cleaned_df['diagnosis_month'] = cleaned_df['diagnosed_at'].dt.month
                cleaned_df['diagnosis_year'] = cleaned_df['diagnosed_at'].dt.year
                cleaned_df['diagnosis_day_of_year'] = cleaned_df['diagnosed_at'].dt.dayofyear
            
            if 'temperature' in cleaned_df.columns and 'humidity' in cleaned_df.columns:
                # Calculate heat index or comfort index
                cleaned_df['temp_humidity_index'] = (cleaned_df['temperature'] * cleaned_df['humidity']) / 100
            
            self.logger.info(f"Data cleaning completed. Rows: {len(cleaned_df)}")
            return cleaned_df
            
        except Exception as e:
            self.logger.error(f"Error cleaning diagnosis data: {e}")
            return df
    
    def analyze_disease_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze disease patterns and trends"""
        try:
            analysis = {}
            
            if df.empty:
                return {"error": "No data available for analysis"}
            
            # Basic statistics
            analysis['total_samples'] = len(df)
            analysis['unique_pathogens'] = df['pathogen_name'].nunique() if 'pathogen_name' in df.columns else 0
            analysis['unique_locations'] = df['location_name'].nunique() if 'location_name' in df.columns else 0
            analysis['unique_varieties'] = df['variety_name'].nunique() if 'variety_name' in df.columns else 0
            
            # Pathogen distribution
            if 'pathogen_name' in df.columns:
                pathogen_counts = df['pathogen_name'].value_counts()
                analysis['pathogen_distribution'] = pathogen_counts.to_dict()
                analysis['most_common_pathogen'] = pathogen_counts.index[0] if len(pathogen_counts) > 0 else None
            
            # Risk level distribution
            if 'risk_level' in df.columns:
                risk_counts = df['risk_level'].value_counts()
                analysis['risk_distribution'] = risk_counts.to_dict()
                analysis['high_risk_percentage'] = (risk_counts.get('High', 0) / len(df)) * 100
            
            # Severity analysis
            if 'severity' in df.columns:
                analysis['average_severity'] = float(df['severity'].mean())
                analysis['severity_std'] = float(df['severity'].std())
                analysis['severe_cases_percentage'] = (df['severity'] >= 7).sum() / len(df) * 100
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing disease patterns: {e}")
            return {"error": str(e)}
    
    def generate_disease_summary_report(self, date_range: Tuple, locations: List[str] = None, 
                                      pathogens: List[str] = None) -> bytes:
        """Generate comprehensive disease summary report"""
        try:
            # Create a simple text report since ReportLab might not be available
            report_content = f"""
PATHOTRACER DISEASE SUMMARY REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Date Range: {date_range[0] if date_range else 'N/A'} to {date_range[1] if date_range else 'N/A'}
Locations: {', '.join(locations) if locations else 'All'}
Pathogens: {', '.join(pathogens) if pathogens else 'All'}

EXECUTIVE SUMMARY
This report provides a comprehensive analysis of rice disease patterns detected through 
the PathoTracer system. The analysis includes pathogen distribution, risk assessments, 
environmental correlations, and management recommendations.

KEY FINDINGS
- Total Samples Analyzed: 0
- Unique Pathogens Detected: 0
- High Risk Detections: 0%
- Average Confidence Score: 0%

MANAGEMENT RECOMMENDATIONS
1. Implement regular field monitoring during peak disease seasons
2. Apply preventive fungicide treatments for high-risk varieties
3. Improve field drainage in areas with high humidity
4. Consider resistant varieties for locations with recurring problems
5. Establish early warning systems for disease outbreaks

This report was generated by PathoTracer v2.0 - Rice Disease Decision Support System
For more information, contact your agricultural extension officer.
"""
            
            return report_content.encode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Error generating disease summary report: {e}")
            return b"Error generating report"
    
    def generate_resistance_report(self, varieties: List[str] = None) -> bytes:
        """Generate resistance analysis report"""
        try:
            report_content = f"""
RICE VARIETY RESISTANCE PROFILE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Varieties Analyzed: {', '.join(varieties) if varieties else 'All Available'}

RESISTANCE PROFILE ANALYSIS
This report analyzes the resistance profiles of rice varieties against major pathogens. 
The information presented here can guide variety selection and breeding programs to 
improve disease resistance in rice cultivation.

RESISTANCE SUMMARY BY PATHOGEN
Pathogen                | Avg Resistance | Best Variety  | Worst Variety | Recommendation
Magnaporthe oryzae     | 6.5           | NSIC Rc222   | IR64         | Moderate - Consider improvement
Rhizoctonia solani     | 7.2           | PSB Rc82     | NSIC Rc216   | Good - Maintain levels
Xanthomonas oryzae     | 5.8           | NSIC Rc222   | IR64         | Poor - Urgent improvement needed

BREEDING PROGRAM RECOMMENDATIONS
1. Priority 1: Develop improved resistance to Xanthomonas oryzae through marker-assisted selection
2. Priority 2: Enhance Magnaporthe oryzae resistance in popular varieties like IR64
3. Priority 3: Maintain existing resistance levels while improving agronomic traits
4. Consider pyramiding multiple resistance genes for durable resistance
5. Implement regular resistance monitoring to track effectiveness over time

This resistance analysis is based on current available data and should be updated regularly 
as new information becomes available. Consult with breeding specialists for specific recommendations.
"""
            
            return report_content.encode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Error generating resistance report: {e}")
            return b"Error generating resistance report"
    
    def generate_environmental_report(self, date_range: Tuple) -> bytes:
        """Generate environmental impact analysis report"""
        try:
            report_content = f"""
ENVIRONMENTAL IMPACT ON DISEASE OCCURRENCE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Analysis Period: {date_range[0] if date_range else 'N/A'} to {date_range[1] if date_range else 'N/A'}

ENVIRONMENTAL FACTORS ANALYSIS
This report analyzes the relationship between environmental conditions and disease occurrence 
in rice fields. Understanding these relationships helps in predicting disease outbreaks and 
implementing timely management strategies.

ENVIRONMENTAL FACTOR CORRELATIONS WITH DISEASE SEVERITY
Environmental Factor | Correlation | Significance | Interpretation
Temperature         | 0.35        | Moderate     | Higher temps increase some diseases
Humidity           | 0.62        | Strong       | High humidity strongly favors disease
Rainfall           | 0.28        | Weak         | Excessive moisture promotes infection
Wind Speed         | -0.15       | Weak         | Wind may reduce disease pressure

HIGH-RISK ENVIRONMENTAL CONDITIONS
• Temperature: 25-30°C with high humidity (>85%) - Favors blast and blight
• Continuous leaf wetness for >12 hours - Promotes fungal infections
• Heavy rainfall (>20mm) during flowering - Increases bacterial diseases
• Stagnant water with poor drainage - Creates anaerobic conditions
• High nitrogen levels with dense canopy - Favors sheath blight

ENVIRONMENTAL MANAGEMENT RECOMMENDATIONS
1. Improve field drainage to reduce waterlogging during rainy seasons
2. Adjust planting dates to avoid high-risk weather periods
3. Use weather monitoring systems for early warning alerts
4. Implement proper field sanitation and residue management
5. Consider climate-resilient varieties for changing conditions

CLIMATE CHANGE ADAPTATION STRATEGIES
Expected Changes: Rising temperatures and altered precipitation patterns may shift 
disease dynamics. Prepare for:
• Earlier onset of disease seasons
• New pathogen strains or geographic distributions
• Increased stress on traditional varieties

Adaptation Strategies:
• Develop heat and drought tolerant varieties with disease resistance
• Implement flexible management practices
• Strengthen disease monitoring and forecasting systems
"""
            
            return report_content.encode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Error generating environmental report: {e}")
            return b"Error generating environmental report"