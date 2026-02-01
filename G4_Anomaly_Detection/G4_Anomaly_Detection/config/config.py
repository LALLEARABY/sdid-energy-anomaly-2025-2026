"""
G4 - Configuration Module
Loads environment variables and model parameters
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for anomaly detection system"""
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'power_consumption_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    
    # Model Configuration
    ANOMALY_THRESHOLD = float(os.getenv('ANOMALY_THRESHOLD', -0.5))
    CONTAMINATION = float(os.getenv('CONTAMINATION', 0.01))
    N_ESTIMATORS = int(os.getenv('N_ESTIMATORS', 100))
    MAX_SAMPLES = int(os.getenv('MAX_SAMPLES', 256))
    RANDOM_STATE = 42
    
    # ROI Configuration
    COST_PREVENTED_FAILURE = float(os.getenv('COST_PREVENTED_FAILURE', 5000))
    COST_FALSE_ALARM = float(os.getenv('COST_FALSE_ALARM', 50))
    ENERGY_COST_PER_KWH = float(os.getenv('ENERGY_COST_PER_KWH', 0.15))
    
    # Scoring Configuration
    SCORING_INTERVAL = int(os.getenv('SCORING_INTERVAL', 60))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))
    
    @classmethod
    def get_db_connection_string(cls):
        """Returns PostgreSQL connection string"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def display_config(cls):
        """Display current configuration (hide sensitive data)"""
        print("=" * 50)
        print("G4 - Anomaly Detection Configuration")
        print("=" * 50)
        print(f"Database: {cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}")
        print(f"User: {cls.DB_USER}")
        print(f"Anomaly Threshold: {cls.ANOMALY_THRESHOLD}")
        print(f"Contamination: {cls.CONTAMINATION}")
        print(f"N Estimators: {cls.N_ESTIMATORS}")
        print(f"Scoring Interval: {cls.SCORING_INTERVAL}s")
        print("=" * 50)
