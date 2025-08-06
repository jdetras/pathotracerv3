# Save this as: config/settings.py

#!/usr/bin/env python3
"""
Configuration Settings for PathoTracer v2
Manages application configuration and settings
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

class Config:
    """Main configuration manager for PathoTracer"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager"""
        self.config_dir = Path('config')
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = config_file or self.config_dir / 'pathotracer_config.json'
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self.default_config = {
            'database': {
                'host': 'localhost',
                'port': 5432,
                'database': 'pathotracer',
                'user': 'postgres',
                'password': ''
            },
            'application': {
                'app_name': 'PathoTracer v2',
                'version': '2.0.0',
                'debug_mode': False,
                'log_level': 'INFO',
                'data_dir': 'data',
                'models_dir': 'models',
                'backup_dir': 'backups'
            },
            'model': {
                'confidence_threshold': 0.8,
                'symptom_weight': 0.4,
                'environmental_weight': 0.3,
                'historical_weight': 0.2,
                'variety_weight': 0.1
            },
            'notifications': {
                'email_alerts': False,
                'alert_threshold': 7
            }
        }
        
        # Load configuration from file or environment
        self._load_config()
        
        # Ensure directories exist
        self._create_directories()
    
    def _load_config(self):
        """Load configuration from JSON file or environment variables"""
        try:
            # Start with default configuration
            self.config = self.default_config.copy()
            
            # Load from file if exists
            if Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self._merge_config(self.config, file_config)
                self.logger.info(f"Configuration loaded from {self.config_file}")
            
            # Override with environment variables
            self._load_from_environment()
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.logger.info("Using default configuration")
            self.config = self.default_config.copy()
    
    def _merge_config(self, base_config: Dict, new_config: Dict):
        """Recursively merge configuration dictionaries"""
        for key, value in new_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        try:
            # Database configuration from environment
            if os.getenv('POSTGRES_HOST'):
                self.config['database']['host'] = os.getenv('POSTGRES_HOST')
            if os.getenv('POSTGRES_PORT'):
                self.config['database']['port'] = int(os.getenv('POSTGRES_PORT'))
            if os.getenv('POSTGRES_DB'):
                self.config['database']['database'] = os.getenv('POSTGRES_DB')
            if os.getenv('POSTGRES_USER'):
                self.config['database']['user'] = os.getenv('POSTGRES_USER')
            if os.getenv('POSTGRES_PASSWORD'):
                self.config['database']['password'] = os.getenv('POSTGRES_PASSWORD')
            
            # Application configuration from environment
            if os.getenv('PATHOTRACER_DEBUG'):
                self.config['application']['debug_mode'] = os.getenv('PATHOTRACER_DEBUG').lower() == 'true'
            if os.getenv('PATHOTRACER_LOG_LEVEL'):
                self.config['application']['log_level'] = os.getenv('PATHOTRACER_LOG_LEVEL')
            
            self.logger.info("Configuration updated from environment variables")
            
        except Exception as e:
            self.logger.error(f"Error loading from environment variables: {e}")
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            self.config['application']['data_dir'],
            self.config['application']['models_dir'],
            self.config['application']['backup_dir'],
            'logs'
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        try:
            keys = key.split('.')
            value = self.config
            
            for key_part in keys:
                if isinstance(value, dict) and key_part in value:
                    value = value[key_part]
                else:
                    return default
            
            return value
            
        except Exception:
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value by key"""
        try:
            keys = key.split('.')
            config_ref = self.config
            
            # Navigate to the parent dictionary
            for key_part in keys[:-1]:
                if key_part not in config_ref:
                    config_ref[key_part] = {}
                config_ref = config_ref[key_part]
            
            # Set the value
            config_ref[keys[-1]] = value
            
            # Auto-save configuration
            self._save_config()
            
        except Exception as e:
            self.logger.error(f"Error setting configuration value {key}: {e}")
            raise
    
    def _save_config(self):
        """Save current configuration to JSON file"""
        try:
            config_to_save = self.config.copy()
            config_to_save['last_updated'] = datetime.now().isoformat()
            
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
            
            self.logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def save_settings(self, settings: Dict[str, Any]):
        """Save general application settings"""
        try:
            for key, value in settings.items():
                self.set(f'application.{key}', value)
            
            self.logger.info("General settings saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving general settings: {e}")
            raise
    
    def save_db_settings(self, db_settings: Dict[str, Any]):
        """Save database settings"""
        try:
            for key, value in db_settings.items():
                clean_key = key.replace('db_', '')
                self.set(f'database.{clean_key}', value)
            
            self.logger.info("Database settings saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving database settings: {e}")
            raise
    
    def save_model_settings(self, model_settings: Dict[str, Any]):
        """Save model configuration settings"""
        try:
            for key, value in model_settings.items():
                self.set(f'model.{key}', value)
            
            self.logger.info("Model settings saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving model settings: {e}")
            raise
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration as dictionary"""
        return self.config.get('database', {})
    
    def validate_config(self) -> Dict[str, list]:
        """Validate configuration and return any issues"""
        issues = {
            'errors': [],
            'warnings': []
        }
        
        # Validate database configuration
        db_config = self.config.get('database', {})
        if not db_config.get('host'):
            issues['errors'].append("Database host is required")
        
        if not db_config.get('database'):
            issues['errors'].append("Database name is required")
        
        if not db_config.get('user'):
            issues['errors'].append("Database user is required")
        
        # Validate model configuration
        model_config = self.config.get('model', {})
        confidence_threshold = model_config.get('confidence_threshold', 0.8)
        if not (0 < confidence_threshold <= 1):
            issues['errors'].append("Confidence threshold must be between 0 and 1")
        
        return issues
    
    def __str__(self) -> str:
        """String representation of configuration"""
        db_config = self.config.get('database', {})
        return f"PathoTracer Configuration - DB: {db_config.get('host', 'localhost')}:{db_config.get('port', 5432)}"