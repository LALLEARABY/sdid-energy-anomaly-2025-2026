#!/usr/bin/env python3
"""
G4 - Quick Start Script
Tests all components and verifies the setup
"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        logger.warning("⚠ .env file not found")
        logger.info("Creating .env from .env.example...")
        
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            logger.info("✓ .env file created - please update with your credentials")
            return False
        else:
            logger.error("✗ .env.example not found")
            return False
    
    logger.info("✓ .env file found")
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    logger.info("\nChecking dependencies...")
    
    required_packages = [
        'pandas', 'numpy', 'scikit-learn', 'psycopg2',
        'sqlalchemy', 'matplotlib', 'python-dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"  ✓ {package}")
        except ImportError:
            logger.error(f"  ✗ {package}")
            missing.append(package)
    
    if missing:
        logger.error(f"\n✗ Missing packages: {', '.join(missing)}")
        logger.info("Install with: pip install -r requirements.txt")
        return False
    
    logger.info("\n✓ All dependencies installed")
    return True

def check_g3_files():
    """Check if G3 parameter files exist"""
    logger.info("\nChecking G3 parameter files...")
    
    files = ['models/g3_scaler.pkl', 'models/g3_pca.pkl']
    all_exist = True
    
    for filepath in files:
        if os.path.exists(filepath):
            logger.info(f"  ✓ {filepath}")
        else:
            logger.warning(f"  ⚠ {filepath} not found")
            all_exist = False
    
    if not all_exist:
        logger.warning("\n⚠ G3 files not found - system will use default parameters")
        logger.info("To synchronize with G3, copy their files to models/ directory")
    
    return True  # Not blocking

def test_database_connection():
    """Test database connection"""
    logger.info("\nTesting database connection...")
    
    try:
        from src.database import DatabaseConnection
        
        db = DatabaseConnection()
        if db.connect():
            if db.test_connection():
                logger.info("✓ Database connection successful")
                db.disconnect()
                return True
            else:
                logger.error("✗ Database connection failed")
                db.disconnect()
                return False
        else:
            logger.error("✗ Cannot connect to database")
            logger.info("Make sure PostgreSQL is running and credentials in .env are correct")
            return False
    
    except Exception as e:
        logger.error(f"✗ Database test error: {e}")
        return False

def test_preprocessor():
    """Test preprocessor"""
    logger.info("\nTesting preprocessor...")
    
    try:
        from src.preprocessor import DataPreprocessor
        import pandas as pd
        import numpy as np
        
        preprocessor = DataPreprocessor()
        
        # Try to load G3 parameters
        if not preprocessor.load_g3_parameters():
            # Create sample data and fit
            sample_data = pd.DataFrame({
                'global_active_power': np.random.rand(100),
                'global_reactive_power': np.random.rand(100),
                'voltage': 240 + np.random.rand(100) * 10,
                'global_intensity': np.random.rand(100) * 5,
                'sub_metering_1': np.random.rand(100),
                'sub_metering_2': np.random.rand(100),
                'sub_metering_3': np.random.rand(100)
            })
            preprocessor.fit_default(sample_data)
        
        # Test transformation
        test_data = pd.DataFrame({
            'global_active_power': [1.5],
            'global_reactive_power': [0.3],
            'voltage': [240],
            'global_intensity': [6.2],
            'sub_metering_1': [0.0],
            'sub_metering_2': [1.0],
            'sub_metering_3': [17.0]
        })
        
        transformed = preprocessor.transform(test_data)
        logger.info(f"  Transformed shape: {transformed.shape}")
        logger.info("✓ Preprocessor working correctly")
        return True
    
    except Exception as e:
        logger.error(f"✗ Preprocessor test error: {e}")
        return False

def display_next_steps():
    """Display next steps"""
    logger.info("\n" + "=" * 70)
    logger.info("SETUP COMPLETE - NEXT STEPS")
    logger.info("=" * 70)
    logger.info("\n1. Update .env file with your database credentials")
    logger.info("\n2. Get G3 parameter files and place them in models/:")
    logger.info("   - models/g3_scaler.pkl")
    logger.info("   - models/g3_pca.pkl")
    logger.info("\n3. Train the anomaly detection model:")
    logger.info("   python train_model.py")
    logger.info("\n4. Run the scoring engine:")
    logger.info("   python src/scoring_engine.py --mode continuous")
    logger.info("\n5. Calculate ROI:")
    logger.info("   python src/roi_calculator.py")
    logger.info("\n" + "=" * 70)

def main():
    """Main function"""
    logger.info("=" * 70)
    logger.info("G4 - ANOMALY DETECTION SYSTEM - QUICK START")
    logger.info("=" * 70)
    
    # Check environment
    env_ok = check_environment()
    
    # Check dependencies
    if not check_dependencies():
        logger.error("\n✗ Setup incomplete - install dependencies first")
        sys.exit(1)
    
    # Check G3 files (warning only)
    check_g3_files()
    
    # Test database (if env is configured)
    if env_ok:
        db_ok = test_database_connection()
        
        if db_ok:
            # Test preprocessor
            test_preprocessor()
    else:
        logger.warning("\n⚠ Skipping database tests - configure .env first")
    
    # Display next steps
    display_next_steps()

if __name__ == "__main__":
    main()
