"""
G4 - Real-Time Scoring Engine
Consumer script that scores new data and updates the database
UPDATED: Matches actual database schema
"""

import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from src.database_updated import DatabaseConnection
from src.preprocessor_updated import DataPreprocessor
from src.anomaly_detector import AnomalyDetector
from config.config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScoringEngine:
    """
    Real-time scoring engine that processes unscored data
    and updates the database with anomaly scores
    """
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.preprocessor = DataPreprocessor()
        self.detector = AnomalyDetector(algorithm='isolation_forest')
        self.is_initialized = False
        
        # Statistics
        self.total_processed = 0
        self.total_anomalies = 0
        self.start_time = None
    
    def initialize(self):
        """
        Initialize all components:
        1. Connect to database
        2. Load G3 preprocessing parameters
        3. Load trained anomaly detection model
        """
        logger.info("=" * 60)
        logger.info("G4 - Initializing Real-Time Scoring Engine")
        logger.info("=" * 60)
        
        # Connect to database
        if not self.db.connect():
            logger.error("Failed to connect to database")
            return False
        
        # Load G3 parameters
        logger.info("\n[1/3] Loading G3 preprocessing parameters...")
        if not self.preprocessor.load_g3_parameters():
            logger.warning("Using default parameters - please synchronize with G3!")
        
        # Load trained model
        logger.info("\n[2/3] Loading trained anomaly detection model...")
        try:
            self.detector.load_model('models/anomaly_detector.pkl')
        except:
            logger.error("Model not found. Please train the model first.")
            return False
        
        # Test database connection
        logger.info("\n[3/3] Testing database connection...")
        if not self.db.test_connection():
            return False
        
        self.is_initialized = True
        self.start_time = datetime.now()
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Scoring Engine Initialized Successfully")
        logger.info("=" * 60)
        
        return True
    
    def score_batch(self):
        """
        Score a batch of unscored records
        
        Returns:
            int: Number of records processed
        """
        # Get unscored data
        df = self.db.get_unscored_data(batch_size=Config.BATCH_SIZE)
        
        if len(df) == 0:
            return 0
        
        try:
            # Transform data using G3 parameters
            X_transformed = self.preprocessor.transform(df)
            
            # Predict anomaly scores
            anomaly_scores, is_anomaly = self.detector.predict(X_transformed)
            
            # Prepare updates for database
            updates = []
            for idx, (score, flag) in enumerate(zip(anomaly_scores, is_anomaly)):
                record_id = df.iloc[idx]['id']
                updates.append((record_id, float(score), bool(flag)))
            
            # Update database
            self.db.update_anomaly_scores(updates)
            
            # Update statistics
            self.total_processed += len(df)
            self.total_anomalies += sum(is_anomaly)
            
            # Log anomalies
            if sum(is_anomaly) > 0:
                logger.warning(f"⚠ ANOMALIES DETECTED: {sum(is_anomaly)}/{len(df)} records")
                anomaly_records = df[is_anomaly]
                for _, record in anomaly_records.iterrows():
                    logger.warning(
                        f"  → ID {record['id']}: "
                        f"ts={record['ts']}, "
                        f"power={record.get('global_active_power_kw', 'N/A'):.2f} kW, "
                        f"voltage={record.get('voltage_v', 'N/A'):.1f} V"
                    )
            
            return len(df)
        
        except Exception as e:
            logger.error(f"Error scoring batch: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def run_continuous(self, interval=None):
        """
        Run scoring engine continuously
        
        Args:
            interval (int): Seconds between scoring runs (default: from config)
        """
        if not self.is_initialized:
            logger.error("Engine not initialized. Call initialize() first.")
            return
        
        if interval is None:
            interval = Config.SCORING_INTERVAL
        
        logger.info(f"\n▶ Starting continuous scoring (interval: {interval}s)")
        logger.info("Press Ctrl+C to stop\n")
        
        try:
            while True:
                processed = self.score_batch()
                
                if processed > 0:
                    self._print_statistics()
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("\n\n⏸ Stopping scoring engine...")
            self._print_final_statistics()
            self.db.disconnect()
    
    def run_once(self):
        """
        Run a single scoring iteration (useful for testing or cron jobs)
        """
        if not self.is_initialized:
            logger.error("Engine not initialized. Call initialize() first.")
            return
        
        logger.info("Running single scoring iteration...")
        processed = self.score_batch()
        
        if processed > 0:
            self._print_statistics()
        else:
            logger.info("No unscored records found")
        
        self.db.disconnect()
    
    def _print_statistics(self):
        """Print current statistics"""
        if self.total_processed > 0:
            anomaly_rate = (self.total_anomalies / self.total_processed) * 100
            logger.info(f"📊 Processed: {self.total_processed} | "
                       f"Anomalies: {self.total_anomalies} ({anomaly_rate:.2f}%)")
    
    def _print_final_statistics(self):
        """Print final statistics"""
        logger.info("\n" + "=" * 60)
        logger.info("FINAL STATISTICS")
        logger.info("=" * 60)
        
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            logger.info(f"Runtime: {elapsed}")
        
        logger.info(f"Total records processed: {self.total_processed}")
        logger.info(f"Total anomalies detected: {self.total_anomalies}")
        
        if self.total_processed > 0:
            anomaly_rate = (self.total_anomalies / self.total_processed) * 100
            logger.info(f"Anomaly rate: {anomaly_rate:.2f}%")
        
        # Get database statistics
        db_stats = self.db.get_anomaly_statistics()
        logger.info("\nDatabase Statistics:")
        for key, value in db_stats.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("=" * 60)


def main():
    """Main function to run the scoring engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description='G4 - Real-Time Anomaly Scoring Engine')
    parser.add_argument('--mode', choices=['continuous', 'once'], default='continuous',
                       help='Run mode: continuous or once')
    parser.add_argument('--interval', type=int, default=None,
                       help='Scoring interval in seconds (continuous mode only)')
    
    args = parser.parse_args()
    
    # Create and initialize engine
    engine = ScoringEngine()
    
    if not engine.initialize():
        logger.error("Failed to initialize scoring engine")
        return
    
    # Run based on mode
    if args.mode == 'continuous':
        engine.run_continuous(interval=args.interval)
    else:
        engine.run_once()


if __name__ == "__main__":
    main()
