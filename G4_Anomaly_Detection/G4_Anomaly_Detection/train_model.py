"""
G4 - Model Training Script
Trains the anomaly detection model on historical data
"""

import sys
import logging
import pandas as pd
import numpy as np
from src.database import DatabaseConnection
from src.preprocessor import DataPreprocessor
from src.anomaly_detector import AnomalyDetector
from config.config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def train_model(sample_size=None, algorithm='isolation_forest'):
    """
    Complete training pipeline for anomaly detection
    
    Args:
        sample_size (int): Number of records to use for training (None = all)
        algorithm (str): 'isolation_forest' or 'lof'
    """
    logger.info("=" * 70)
    logger.info("G4 - ANOMALY DETECTION MODEL TRAINING")
    logger.info("=" * 70)
    
    # Step 1: Connect to database
    logger.info("\n[STEP 1/6] Connecting to database...")
    db = DatabaseConnection()
    if not db.connect():
        logger.error("Failed to connect to database")
        return False
    
    # Step 2: Retrieve historical data
    logger.info("\n[STEP 2/6] Retrieving historical training data...")
    df = db.get_historical_data(limit=sample_size)
    
    if len(df) == 0:
        logger.error("No historical data available")
        db.disconnect()
        return False
    
    logger.info(f"✓ Retrieved {len(df)} records")
    logger.info(f"  Columns: {list(df.columns)}")
    logger.info(f"  Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # Step 3: Load G3 preprocessing parameters
    logger.info("\n[STEP 3/6] Loading G3 preprocessing parameters...")
    preprocessor = DataPreprocessor()
    
    if not preprocessor.load_g3_parameters():
        logger.warning("G3 parameters not found - using defaults")
        logger.info("Fitting preprocessor on training data...")
        preprocessor.fit_default(df)
        preprocessor.save_parameters()
    
    # Display feature importance
    feature_importance = preprocessor.get_feature_importance()
    if feature_importance is not None:
        logger.info("\nPCA Feature Importance:")
        print(feature_importance)
    
    # Step 4: Transform data
    logger.info("\n[STEP 4/6] Transforming data with G3 parameters...")
    X_train = preprocessor.transform(df)
    logger.info(f"✓ Transformed data shape: {X_train.shape}")
    
    # Step 5: Train anomaly detector
    logger.info(f"\n[STEP 5/6] Training {algorithm} model...")
    detector = AnomalyDetector(algorithm=algorithm)
    detector.train(X_train)
    
    # Analyze on training data
    scores, predictions = detector.predict(X_train)
    anomaly_count = sum(predictions)
    logger.info(f"\nTraining set analysis:")
    logger.info(f"  Anomalies in training: {anomaly_count}/{len(predictions)} ({anomaly_count/len(predictions)*100:.2f}%)")
    
    # Plot score distribution
    detector.plot_score_distribution(scores)
    
    # Step 6: Save model
    logger.info("\n[STEP 6/6] Saving trained model...")
    detector.save_model('models/anomaly_detector.pkl')
    
    # Display model info
    logger.info("\nModel Information:")
    info = detector.get_model_info()
    for key, value in info.items():
        logger.info(f"  {key}: {value}")
    
    # Cleanup
    db.disconnect()
    
    logger.info("\n" + "=" * 70)
    logger.info("✓ TRAINING COMPLETED SUCCESSFULLY")
    logger.info("=" * 70)
    logger.info("\nNext steps:")
    logger.info("1. Review the score distribution plot in docs/score_distribution.png")
    logger.info("2. Adjust threshold if needed in .env file")
    logger.info("3. Run the scoring engine: python src/scoring_engine.py")
    logger.info("=" * 70)
    
    return True


def validate_model():
    """
    Validate the trained model on a test set
    """
    logger.info("=" * 70)
    logger.info("MODEL VALIDATION")
    logger.info("=" * 70)
    
    # Load model
    detector = AnomalyDetector()
    try:
        detector.load_model('models/anomaly_detector.pkl')
    except:
        logger.error("Model not found. Train the model first.")
        return False
    
    # Load preprocessor
    preprocessor = DataPreprocessor()
    if not preprocessor.load_g3_parameters():
        logger.error("G3 parameters not found")
        return False
    
    # Get test data
    db = DatabaseConnection()
    if not db.connect():
        return False
    
    df_test = db.get_historical_data(limit=1000)
    db.disconnect()
    
    if len(df_test) == 0:
        logger.error("No test data available")
        return False
    
    # Transform and predict
    X_test = preprocessor.transform(df_test)
    scores, predictions = detector.predict(X_test)
    
    # Statistics
    logger.info(f"\nValidation Results:")
    logger.info(f"  Test samples: {len(predictions)}")
    logger.info(f"  Anomalies detected: {sum(predictions)}")
    logger.info(f"  Anomaly rate: {sum(predictions)/len(predictions)*100:.2f}%")
    logger.info(f"  Score range: [{scores.min():.4f}, {scores.max():.4f}]")
    
    return True


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='G4 - Train Anomaly Detection Model')
    parser.add_argument('--samples', type=int, default=None,
                       help='Number of samples to use for training (default: all)')
    parser.add_argument('--algorithm', choices=['isolation_forest', 'lof'],
                       default='isolation_forest',
                       help='Algorithm to use')
    parser.add_argument('--validate', action='store_true',
                       help='Validate the model after training')
    
    args = parser.parse_args()
    
    # Display configuration
    Config.display_config()
    
    # Train model
    success = train_model(sample_size=args.samples, algorithm=args.algorithm)
    
    if success and args.validate:
        validate_model()


if __name__ == "__main__":
    main()
