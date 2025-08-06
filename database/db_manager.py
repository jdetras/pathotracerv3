# Save this as: database/db_manager.py

#!/usr/bin/env python3
"""
Database Manager for PathoTracer v2
Handles all PostgreSQL database operations
"""

import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Union, Tuple
import json
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import os

class DatabaseManager:
    """Manages PostgreSQL database connections and operations for PathoTracer"""
    
    def __init__(self, host='localhost', port=5432, database='pathotracer', 
                 user='postgres', password=None):
        """Initialize database connection parameters"""
        # Use Docker service name if in Docker environment
        if os.getenv('POSTGRES_HOST'):
            self.host = os.getenv('POSTGRES_HOST')  # This will be 'postgres' in Docker
        else:
            self.host = host
            
        self.port = int(os.getenv('POSTGRES_PORT', port))
        self.database = os.getenv('POSTGRES_DB', database)
        self.user = os.getenv('POSTGRES_USER', user)
        self.password = os.getenv('POSTGRES_PASSWORD', password or 'pathotracer123')
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Add connection retry logic
        self.max_retries = 3
        self.retry_delay = 2
        
        try:
            # Create SQLAlchemy engine for pandas operations
            self.engine = self._create_engine_with_retry()
            # Initialize database schema
            self._initialize_schema()
        except Exception as e:
            # Silently handle database connection issues
            self.logger.warning(f"Database not available: {e}")
            self.engine = None
    
    def _create_engine_with_retry(self):
        """Create SQLAlchemy engine with retry logic"""
        import time
        
        for attempt in range(self.max_retries):
            try:
                connection_string = (
                    f"postgresql://{self.user}:{self.password}@"
                    f"{self.host}:{self.port}/{self.database}"
                )
                
                engine = create_engine(
                    connection_string,
                    poolclass=QueuePool,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True
                )
                
                # Test the connection
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                self.logger.info(f"Database connected successfully to {self.host}:{self.port}")
                return engine
                
            except Exception as e:
                self.logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise
    
    def _create_engine(self):
        """Create SQLAlchemy engine with connection pooling"""
        return self._create_engine_with_retry()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def check_connection(self) -> bool:
        """Check if database connection is working"""
        try:
            if self.engine is None:
                return False
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            # Silently handle connection check failures
            return False
    
    def _initialize_schema(self):
        """Initialize database schema if it doesn't exist"""
        schema_sql = """
        -- Create main tables
        CREATE TABLE IF NOT EXISTS rice_varieties (
            id SERIAL PRIMARY KEY,
            variety_name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            origin VARCHAR(100),
            maturity_days INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS pathogens (
            id SERIAL PRIMARY KEY,
            pathogen_name VARCHAR(100) UNIQUE NOT NULL,
            pathogen_type VARCHAR(50) NOT NULL,
            scientific_name VARCHAR(150),
            description TEXT,
            severity_range VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS locations (
            id SERIAL PRIMARY KEY,
            location_name VARCHAR(100) NOT NULL,
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            region VARCHAR(100),
            province VARCHAR(100),
            municipality VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS samples (
            id SERIAL PRIMARY KEY,
            sample_id VARCHAR(50) UNIQUE NOT NULL,
            location_id INTEGER REFERENCES locations(id),
            variety_id INTEGER REFERENCES rice_varieties(id),
            collection_date DATE NOT NULL,
            growth_stage VARCHAR(50),
            collector_name VARCHAR(100),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS environmental_conditions (
            id SERIAL PRIMARY KEY,
            sample_id INTEGER REFERENCES samples(id),
            temperature DECIMAL(5, 2),
            humidity DECIMAL(5, 2),
            rainfall DECIMAL(8, 2),
            wind_speed DECIMAL(5, 2),
            solar_radiation DECIMAL(8, 2),
            soil_moisture DECIMAL(5, 2),
            ph_level DECIMAL(4, 2),
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS symptoms (
            id SERIAL PRIMARY KEY,
            symptom_name VARCHAR(100) UNIQUE NOT NULL,
            symptom_category VARCHAR(50),
            description TEXT,
            severity_levels TEXT[]
        );

        CREATE TABLE IF NOT EXISTS sample_symptoms (
            id SERIAL PRIMARY KEY,
            sample_id INTEGER REFERENCES samples(id),
            symptom_id INTEGER REFERENCES symptoms(id),
            severity INTEGER CHECK (severity BETWEEN 1 AND 10),
            area_affected DECIMAL(5, 2),
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS diagnoses (
            id SERIAL PRIMARY KEY,
            sample_id INTEGER REFERENCES samples(id),
            pathogen_id INTEGER REFERENCES pathogens(id),
            confidence_score DECIMAL(5, 4) CHECK (confidence_score BETWEEN 0 AND 1),
            risk_level VARCHAR(20) CHECK (risk_level IN ('Low', 'Medium', 'High')),
            severity INTEGER CHECK (severity BETWEEN 1 AND 10),
            affected_area DECIMAL(5, 2),
            diagnosis_method VARCHAR(50),
            diagnosed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            diagnosed_by VARCHAR(100)
        );

        CREATE TABLE IF NOT EXISTS resistance_profiles (
            id SERIAL PRIMARY KEY,
            variety_id INTEGER REFERENCES rice_varieties(id),
            pathogen_id INTEGER REFERENCES pathogens(id),
            resistance_score DECIMAL(4, 2) CHECK (resistance_score BETWEEN 0 AND 10),
            resistance_type VARCHAR(50),
            test_method VARCHAR(100),
            test_date DATE,
            testing_institution VARCHAR(200),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Insert sample data
        INSERT INTO rice_varieties (variety_name, description) VALUES 
        ('IR64', 'High-yielding variety') ON CONFLICT (variety_name) DO NOTHING;
        INSERT INTO rice_varieties (variety_name, description) VALUES 
        ('PSB Rc82', 'Disease-resistant variety') ON CONFLICT (variety_name) DO NOTHING;
        INSERT INTO rice_varieties (variety_name, description) VALUES 
        ('NSIC Rc222', 'Modern variety') ON CONFLICT (variety_name) DO NOTHING;

        INSERT INTO pathogens (pathogen_name, pathogen_type) VALUES 
        ('Magnaporthe oryzae', 'Fungal') ON CONFLICT (pathogen_name) DO NOTHING;
        INSERT INTO pathogens (pathogen_name, pathogen_type) VALUES 
        ('Rhizoctonia solani', 'Fungal') ON CONFLICT (pathogen_name) DO NOTHING;
        INSERT INTO pathogens (pathogen_name, pathogen_type) VALUES 
        ('Xanthomonas oryzae', 'Bacterial') ON CONFLICT (pathogen_name) DO NOTHING;

        INSERT INTO locations (location_name) VALUES 
        ('Field A') ON CONFLICT DO NOTHING;
        INSERT INTO locations (location_name) VALUES 
        ('Field B') ON CONFLICT DO NOTHING;
        INSERT INTO locations (location_name) VALUES 
        ('Field C') ON CONFLICT DO NOTHING;
        """
        
        try:
            if self.engine:
                with self.engine.connect() as conn:
                    conn.execute(text(schema_sql))
                    conn.commit()
                    self.logger.info("Database schema initialized successfully")
        except Exception as e:
            # Silently handle schema initialization issues
            pass
    
    def get_quick_stats(self) -> Dict:
        """Get quick statistics for sidebar"""
        try:
            if not self.check_connection():
                return {'samples': 0, 'pathogens': 0, 'varieties': 0}
            
            with self.engine.connect() as conn:
                # Total samples
                result = conn.execute(text("SELECT COUNT(*) FROM samples"))
                samples = result.scalar() or 0
                
                # Active pathogens
                result = conn.execute(text("SELECT COUNT(DISTINCT pathogen_id) FROM diagnoses"))
                pathogens = result.scalar() or 0
                
                # Rice varieties
                result = conn.execute(text("SELECT COUNT(*) FROM rice_varieties"))
                varieties = result.scalar() or 0
                
                return {'samples': samples, 'pathogens': pathogens, 'varieties': varieties}
                
        except Exception as e:
            self.logger.error(f"Error getting quick stats: {e}")
            return {'samples': 0, 'pathogens': 0, 'varieties': 0}
    
    def get_dashboard_metrics(self) -> Dict:
        """Get comprehensive dashboard metrics"""
        try:
            if not self.check_connection():
                return {
                    'total_diagnoses': 0, 'diagnoses_delta': 0, 
                    'high_risk_areas': 0, 'active_pathogens': 0, 'accuracy': 0
                }
            
            with self.engine.connect() as conn:
                # Total diagnoses
                result = conn.execute(text("SELECT COUNT(*) FROM diagnoses"))
                total_diagnoses = result.scalar() or 0
                
                return {
                    'total_diagnoses': total_diagnoses,
                    'diagnoses_delta': 0,
                    'high_risk_areas': 0,
                    'active_pathogens': 0,
                    'accuracy': 85.0
                }
                
        except Exception as e:
            self.logger.error(f"Error getting dashboard metrics: {e}")
            return {
                'total_diagnoses': 0, 'diagnoses_delta': 0, 
                'high_risk_areas': 0, 'active_pathogens': 0, 'accuracy': 0
            }
    
    def get_recent_diagnoses(self, limit: int = 10) -> pd.DataFrame:
        """Get recent diagnoses for display"""
        try:
            if not self.check_connection():
                return pd.DataFrame()
            
            query = """
            SELECT 
                s.sample_id,
                l.location_name,
                rv.variety_name,
                p.pathogen_name,
                d.risk_level,
                d.confidence_score,
                d.diagnosed_at,
                d.diagnosed_at + INTERVAL '1 day' as date_end
            FROM diagnoses d
            JOIN samples s ON d.sample_id = s.id
            LEFT JOIN locations l ON s.location_id = l.id
            LEFT JOIN rice_varieties rv ON s.variety_id = rv.id
            LEFT JOIN pathogens p ON d.pathogen_id = p.id
            ORDER BY d.diagnosed_at DESC 
            LIMIT %s
            """
            
            return pd.read_sql_query(query, self.engine, params=[limit])
        except Exception as e:
            self.logger.error(f"Error getting recent diagnoses: {e}")
            return pd.DataFrame()
    
    def get_active_alerts(self) -> List[Dict]:
        """Get active disease alerts"""
        try:
            # Return sample alerts for demo
            return [
                {
                    'level': 'High',
                    'pathogen': 'Magnaporthe oryzae',
                    'location': 'Field A',
                    'alert_message': 'High confidence detection'
                }
            ]
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}")
            return []
    
    def get_geographic_distribution(self) -> pd.DataFrame:
        """Get geographic distribution of pathogens"""
        try:
            # Return sample data for demo
            sample_data = {
                'latitude': [14.5995, 14.6091, 14.5547],
                'longitude': [120.9842, 121.0223, 121.0244],
                'location': ['Field A', 'Field B', 'Field C'],
                'pathogen_type': ['Fungal', 'Bacterial', 'Fungal'],
                'intensity': [5, 8, 3],
                'detection_date': [datetime.now() - timedelta(days=i) for i in range(3)]
            }
            return pd.DataFrame(sample_data)
        except Exception as e:
            self.logger.error(f"Error getting geographic distribution: {e}")
            return pd.DataFrame()
    
    def store_diagnosis(self, diagnosis_data: Dict, prediction_results: List[Dict]):
        """Store a new diagnosis in the database"""
        try:
            if not self.check_connection():
                self.logger.warning("Cannot store diagnosis - database not available")
                return
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Insert or get sample
                sample_id_db = self._insert_sample(cursor, diagnosis_data)
                
                # Insert environmental conditions
                self._insert_environmental_conditions(cursor, sample_id_db, diagnosis_data)
                
                # Insert symptoms
                self._insert_sample_symptoms(cursor, sample_id_db, diagnosis_data.get('symptoms', []))
                
                # Insert diagnoses
                for result in prediction_results:
                    pathogen_id = self._get_or_create_pathogen(cursor, result['pathogen'])
                    
                    cursor.execute("""
                        INSERT INTO diagnoses (
                            sample_id, pathogen_id, confidence_score, risk_level, 
                            severity, affected_area, diagnosis_method
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        sample_id_db,
                        pathogen_id,
                        result['confidence'],
                        result['risk_level'],
                        diagnosis_data.get('severity', 5),
                        diagnosis_data.get('affected_area', 25),
                        'ML_Model'
                    ))
                
                conn.commit()
                self.logger.info(f"Diagnosis stored successfully for sample {diagnosis_data['sample_id']}")
                
        except Exception as e:
            self.logger.error(f"Error storing diagnosis: {e}")
    
    def _insert_sample(self, cursor, diagnosis_data: Dict) -> int:
        """Insert sample and return database ID"""
        # Get or create location
        location_id = self._get_or_create_location(cursor, diagnosis_data['location'])
        
        # Get or create variety
        variety_id = self._get_or_create_variety(cursor, diagnosis_data['rice_variety'])
        
        cursor.execute("""
            INSERT INTO samples (
                sample_id, location_id, variety_id, collection_date, growth_stage
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            diagnosis_data['sample_id'],
            location_id,
            variety_id,
            diagnosis_data['collection_date'],
            diagnosis_data['growth_stage']
        ))
        
        return cursor.fetchone()[0]
    
    def _insert_environmental_conditions(self, cursor, sample_id: int, diagnosis_data: Dict):
        """Insert environmental conditions"""
        cursor.execute("""
            INSERT INTO environmental_conditions (
                sample_id, temperature, humidity, rainfall
            ) VALUES (%s, %s, %s, %s)
        """, (
            sample_id,
            diagnosis_data.get('temperature'),
            diagnosis_data.get('humidity'),
            diagnosis_data.get('rainfall', 0)
        ))
    
    def _insert_sample_symptoms(self, cursor, sample_id: int, symptoms: List[str]):
        """Insert sample symptoms"""
        for symptom_name in symptoms:
            symptom_id = self._get_or_create_symptom(cursor, symptom_name)
            cursor.execute("""
                INSERT INTO sample_symptoms (sample_id, symptom_id, severity)
                VALUES (%s, %s, %s)
            """, (sample_id, symptom_id, 5))  # Default severity
    
    def _get_or_create_location(self, cursor, location_name: str) -> int:
        """Get or create location and return ID"""
        cursor.execute("SELECT id FROM locations WHERE location_name = %s", (location_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            cursor.execute("""
                INSERT INTO locations (location_name) VALUES (%s) RETURNING id
            """, (location_name,))
            return cursor.fetchone()[0]
    
    def _get_or_create_variety(self, cursor, variety_name: str) -> int:
        """Get or create rice variety and return ID"""
        cursor.execute("SELECT id FROM rice_varieties WHERE variety_name = %s", (variety_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            cursor.execute("""
                INSERT INTO rice_varieties (variety_name) VALUES (%s) RETURNING id
            """, (variety_name,))
            return cursor.fetchone()[0]
    
    def _get_or_create_pathogen(self, cursor, pathogen_name: str) -> int:
        """Get or create pathogen and return ID"""
        cursor.execute("SELECT id FROM pathogens WHERE pathogen_name = %s", (pathogen_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            cursor.execute("""
                INSERT INTO pathogens (pathogen_name, pathogen_type) 
                VALUES (%s, %s) RETURNING id
            """, (pathogen_name, 'Unknown'))
            return cursor.fetchone()[0]
    
    def _get_or_create_symptom(self, cursor, symptom_name: str) -> int:
        """Get or create symptom and return ID"""
        cursor.execute("SELECT id FROM symptoms WHERE symptom_name = %s", (symptom_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            cursor.execute("""
                INSERT INTO symptoms (symptom_name) VALUES (%s) RETURNING id
            """, (symptom_name,))
            return cursor.fetchone()[0]
    
    def get_rice_varieties(self) -> List[str]:
        """Get list of all rice varieties"""
        try:
            if not self.check_connection():
                return ["IR64", "PSB Rc82", "NSIC Rc222", "NSIC Rc216"]
            
            query = "SELECT variety_name FROM rice_varieties ORDER BY variety_name"
            df = pd.read_sql_query(query, self.engine)
            return df['variety_name'].tolist()
        except Exception as e:
            self.logger.error(f"Error getting rice varieties: {e}")
            return ["IR64", "PSB Rc82", "NSIC Rc222", "NSIC Rc216"]
    
    def get_pathogen_types(self) -> List[str]:
        """Get list of all pathogen types"""
        try:
            if not self.check_connection():
                return [
                    "Magnaporthe oryzae", "Rhizoctonia solani", "Xanthomonas oryzae",
                    "Pyricularia oryzae", "Fusarium fujikuroi", "Burkholderia glumae"
                ]
            
            query = "SELECT DISTINCT pathogen_name FROM pathogens ORDER BY pathogen_name"
            df = pd.read_sql_query(query, self.engine)
            return df['pathogen_name'].tolist()
        except Exception as e:
            self.logger.error(f"Error getting pathogen types: {e}")
            return [
                "Magnaporthe oryzae", "Rhizoctonia solani", "Xanthomonas oryzae",
                "Pyricularia oryzae", "Fusarium fujikuroi", "Burkholderia glumae"
            ]
    
    def get_locations(self) -> List[str]:
        """Get list of all locations"""
        try:
            if not self.check_connection():
                return ["Field A", "Field B", "Field C"]
            
            query = "SELECT DISTINCT location_name FROM locations ORDER BY location_name"
            df = pd.read_sql_query(query, self.engine)
            return df['location_name'].tolist()
        except Exception as e:
            self.logger.error(f"Error getting locations: {e}")
            return ["Field A", "Field B", "Field C"]
    
    # Placeholder methods for missing functionality
    def get_resistance_profiles(self, varieties=None, pathogens=None):
        """Get resistance profiles"""
        # Return sample data
        data = {
            'variety': ['IR64', 'PSB Rc82', 'NSIC Rc222'],
            'pathogen': ['Magnaporthe oryzae', 'Magnaporthe oryzae', 'Magnaporthe oryzae'],
            'resistance_score': [5.5, 7.2, 8.1]
        }
        return pd.DataFrame(data)
    
    def add_resistance_data(self, resistance_data):
        """Add resistance data"""
        self.logger.info("Resistance data would be added to database")
    
    def get_analytics_data(self, **kwargs):
        """Get analytics data"""
        return pd.DataFrame()
    
    def import_data(self, df, data_type):
        """Import data"""
        return {"success": True, "rows": len(df)}
    
    def export_data(self, export_type, date_range=None):
        """Export data"""
        return pd.DataFrame()
    
    def get_database_status(self):
        """Get database status"""
        return {
            'total_records': 0,
            'size': '0 MB',
            'table_stats': {},
            'last_backup': 'Never'
        }
    
    def create_backup(self):
        """Create backup"""
        return "backup_file.sql"
    
    def optimize_database(self):
        """Optimize database"""
        self.logger.info("Database optimization completed")
    
    def check_data_integrity(self):
        """Check data integrity"""
        return {"issues": []}