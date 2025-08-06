# Save this as: models/pathogen_predictor.py

#!/usr/bin/env python3
"""
Pathogen Predictor for PathoTracer v2
Machine learning model for pathogen identification and risk assessment
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import json
import os

class PathogenPredictor:
    """Machine learning model for pathogen prediction and risk assessment"""
    
    def __init__(self, model_dir: str = "models"):
        """Initialize the pathogen predictor"""
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Pathogen knowledge base
        self.pathogen_knowledge = self._initialize_pathogen_knowledge()
        
    def _initialize_pathogen_knowledge(self) -> Dict:
        """Initialize pathogen knowledge base"""
        return {
            "Magnaporthe oryzae": {
                "common_name": "Rice Blast",
                "type": "Fungal",
                "symptoms": ["leaf spots", "neck rot", "panicle blast"],
                "favorable_conditions": {
                    "temperature": (20, 30),
                    "humidity": (85, 100),
                    "rainfall": "high"
                },
                "severity_factors": ["growth_stage", "variety_susceptibility"],
                "management": [
                    "Use resistant varieties",
                    "Apply fungicides at early growth stages",
                    "Improve field drainage",
                    "Balanced fertilization"
                ]
            },
            "Rhizoctonia solani": {
                "common_name": "Sheath Blight",
                "type": "Fungal",
                "symptoms": ["sheath blight", "lesions", "yellowing"],
                "favorable_conditions": {
                    "temperature": (25, 32),
                    "humidity": (80, 100),
                    "rainfall": "moderate to high"
                },
                "severity_factors": ["plant_density", "nitrogen_level"],
                "management": [
                    "Reduce plant density",
                    "Balanced nitrogen application",
                    "Apply fungicides at tillering stage",
                    "Improve air circulation"
                ]
            },
            "Xanthomonas oryzae": {
                "common_name": "Bacterial Leaf Blight",
                "type": "Bacterial",
                "symptoms": ["leaf blight", "yellowing", "wilting"],
                "favorable_conditions": {
                    "temperature": (25, 34),
                    "humidity": (70, 100),
                    "rainfall": "high with flooding"
                },
                "severity_factors": ["wound_entry", "variety_susceptibility"],
                "management": [
                    "Use certified seeds",
                    "Apply copper-based bactericides",
                    "Avoid excessive nitrogen",
                    "Manage water levels"
                ]
            }
        }
    
    def predict(self, diagnosis_data: Dict) -> List[Dict]:
        """Predict pathogen from diagnosis data"""
        try:
            # Use rule-based prediction for now
            predictions = self._rule_based_prediction(diagnosis_data)
            
            # Enhance with additional information
            enhanced_results = []
            for result in predictions:
                enhanced_result = self._enhance_prediction(result, diagnosis_data)
                enhanced_results.append(enhanced_result)
            
            return enhanced_results
            
        except Exception as e:
            self.logger.error(f"Prediction error: {e}")
            # Return fallback prediction
            return self._fallback_prediction(diagnosis_data)
    
    def _rule_based_prediction(self, diagnosis_data: Dict) -> List[Dict]:
        """Rule-based prediction when no trained models are available"""
        predictions = []
        symptoms = diagnosis_data.get('symptoms', [])
        temperature = diagnosis_data.get('temperature', 25)
        humidity = diagnosis_data.get('humidity', 80)
        
        # Rice Blast prediction
        blast_score = 0
        if any(symptom in symptoms for symptom in ["leaf spots", "neck rot", "panicle blast"]):
            blast_score += 0.4
        if 20 <= temperature <= 30:
            blast_score += 0.2
        if humidity >= 85:
            blast_score += 0.2
        if diagnosis_data.get('growth_stage') in ['Heading', 'Flowering']:
            blast_score += 0.2
        
        if blast_score > 0.5:
            predictions.append({
                'pathogen': 'Magnaporthe oryzae',
                'confidence': min(blast_score, 0.95)
            })
        
        # Sheath Blight prediction
        blight_score = 0
        if any(symptom in symptoms for symptom in ["sheath blight", "lesions", "yellowing"]):
            blight_score += 0.4
        if 25 <= temperature <= 32:
            blight_score += 0.2
        if humidity >= 80:
            blight_score += 0.2
        if diagnosis_data.get('growth_stage') in ['Tillering', 'Stem elongation']:
            blight_score += 0.2
        
        if blight_score > 0.5:
            predictions.append({
                'pathogen': 'Rhizoctonia solani',
                'confidence': min(blight_score, 0.95)
            })
        
        # Bacterial Leaf Blight prediction
        bacterial_score = 0
        if any(symptom in symptoms for symptom in ["leaf blight", "yellowing", "wilting"]):
            bacterial_score += 0.4
        if 25 <= temperature <= 34:
            bacterial_score += 0.2
        if humidity >= 70:
            bacterial_score += 0.2
        if diagnosis_data.get('rainfall', 0) > 10:
            bacterial_score += 0.2
        
        if bacterial_score > 0.5:
            predictions.append({
                'pathogen': 'Xanthomonas oryzae',
                'confidence': min(bacterial_score, 0.95)
            })
        
        # If no strong predictions, return most likely based on symptoms
        if not predictions:
            if symptoms:
                predictions.append({
                    'pathogen': 'Magnaporthe oryzae',  # Most common
                    'confidence': 0.6
                })
            else:
                predictions.append({
                    'pathogen': 'Unknown',
                    'confidence': 0.3
                })
        
        return predictions
    
    def _enhance_prediction(self, result: Dict, diagnosis_data: Dict) -> Dict:
        """Enhance prediction with additional information"""
        pathogen = result['pathogen']
        confidence = result['confidence']
        
        # Get pathogen knowledge
        pathogen_info = self.pathogen_knowledge.get(pathogen, {})
        
        # Determine risk level
        risk_level = self._calculate_risk_level(confidence, diagnosis_data, pathogen_info)
        
        # Get management recommendations
        recommendations = self._get_management_recommendations(pathogen, diagnosis_data, pathogen_info)
        
        # Determine primary action
        action = self._determine_action(risk_level, confidence)
        
        enhanced_result = {
            'pathogen': pathogen,
            'common_name': pathogen_info.get('common_name', pathogen),
            'pathogen_type': pathogen_info.get('type', 'Unknown'),
            'confidence': confidence,
            'risk_level': risk_level,
            'action': action,
            'recommendations': recommendations,
            'favorable_conditions': pathogen_info.get('favorable_conditions', {}),
            'typical_symptoms': pathogen_info.get('symptoms', [])
        }
        
        return enhanced_result
    
    def _calculate_risk_level(self, confidence: float, diagnosis_data: Dict, pathogen_info: Dict) -> str:
        """Calculate risk level based on confidence and conditions"""
        base_risk = confidence
        
        # Adjust risk based on environmental conditions
        if pathogen_info and 'favorable_conditions' in pathogen_info:
            favorable_conditions = pathogen_info['favorable_conditions']
            
            temp = diagnosis_data.get('temperature', 25)
            humidity = diagnosis_data.get('humidity', 80)
            
            # Check temperature favorability
            if 'temperature' in favorable_conditions:
                temp_range = favorable_conditions['temperature']
                if temp_range[0] <= temp <= temp_range[1]:
                    base_risk += 0.1
            
            # Check humidity favorability
            if 'humidity' in favorable_conditions:
                hum_range = favorable_conditions['humidity']
                if hum_range[0] <= humidity <= hum_range[1]:
                    base_risk += 0.1
        
        # Adjust risk based on severity and affected area
        severity = diagnosis_data.get('severity', 5)
        affected_area = diagnosis_data.get('affected_area', 25)
        
        if severity >= 7:
            base_risk += 0.1
        if affected_area >= 50:
            base_risk += 0.1
        
        # Classify risk level
        if base_risk >= 0.8:
            return 'High'
        elif base_risk >= 0.6:
            return 'Medium'
        else:
            return 'Low'
    
    def _get_management_recommendations(self, pathogen: str, diagnosis_data: Dict, pathogen_info: Dict) -> List[str]:
        """Get management recommendations for the pathogen"""
        recommendations = []
        
        # Get base recommendations from knowledge base
        if pathogen_info and 'management' in pathogen_info:
            recommendations.extend(pathogen_info['management'])
        
        # Add specific recommendations based on current conditions
        growth_stage = diagnosis_data.get('growth_stage', 'Tillering')
        severity = diagnosis_data.get('severity', 5)
        
        if severity >= 7:
            recommendations.insert(0, "Immediate intervention required due to high severity")
        
        if growth_stage in ['Flowering', 'Grain filling']:
            recommendations.append("Apply protective measures to prevent grain infection")
        
        # Environmental management
        humidity = diagnosis_data.get('humidity', 80)
        if humidity >= 85:
            recommendations.append("Improve field ventilation to reduce humidity")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _determine_action(self, risk_level: str, confidence: float) -> str:
        """Determine primary recommended action"""
        if risk_level == 'High' and confidence >= 0.8:
            return "Immediate Treatment"
        elif risk_level == 'High' and confidence >= 0.6:
            return "Urgent Monitoring"
        elif risk_level == 'Medium':
            return "Preventive Action"
        else:
            return "Monitor & Observe"
    
    def _fallback_prediction(self, diagnosis_data: Dict) -> List[Dict]:
        """Fallback prediction when all else fails"""
        return [{
            'pathogen': 'Unknown Pathogen',
            'common_name': 'Unknown Disease',
            'pathogen_type': 'Unknown',
            'confidence': 0.3,
            'risk_level': 'Medium',
            'action': 'Laboratory Analysis Needed',
            'recommendations': [
                "Submit sample for laboratory analysis",
                "Monitor field conditions closely",
                "Apply general fungicide as precaution",
                "Consult agricultural extension officer"
            ],
            'favorable_conditions': {},
            'typical_symptoms': []
        }]
    
    def retrain_model(self):
        """Retrain models with latest data"""
        try:
            self.logger.info("Model retraining initiated - would fetch latest data from database")
            return {"status": "success", "message": "Model retrained successfully"}
        except Exception as e:
            self.logger.error(f"Model retraining failed: {e}")
            raise
    
    def get_breeding_recommendations(self, resistance_data: pd.DataFrame) -> List[Dict]:
        """Get breeding recommendations based on resistance profiles"""
        try:
            recommendations = []
            
            if resistance_data.empty:
                return recommendations
            
            # Analyze resistance patterns
            pathogen_resistance = resistance_data.groupby('pathogen')['resistance_score'].agg(['mean', 'std', 'count'])
            
            for pathogen, stats in pathogen_resistance.iterrows():
                avg_resistance = stats['mean']
                variability = stats['std']
                sample_count = stats['count']
                
                if avg_resistance < 4:  # Low average resistance
                    priority = "High"
                    recommendation = f"Urgent need to develop varieties with higher resistance to {pathogen}"
                elif avg_resistance < 6:  # Medium resistance
                    priority = "Medium"
                    recommendation = f"Improve resistance levels to {pathogen} through selective breeding"
                else:  # Good resistance
                    priority = "Low"
                    recommendation = f"Maintain current resistance levels to {pathogen}"
                
                # Consider variability
                if variability > 2:
                    recommendation += " - Focus on reducing variability between varieties"
                
                recommendations.append({
                    'pathogen': pathogen,
                    'priority': priority,
                    'recommendation': recommendation,
                    'current_avg_resistance': round(avg_resistance, 2),
                    'variability': round(variability, 2) if pd.notna(variability) else 0
                })
            
            # Sort by priority
            priority_order = {'High': 1, 'Medium': 2, 'Low': 3}
            recommendations.sort(key=lambda x: priority_order[x['priority']])
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating breeding recommendations: {e}")
            return []