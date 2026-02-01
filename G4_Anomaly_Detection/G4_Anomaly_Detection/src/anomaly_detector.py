"""
G4 - Anomaly Detection Model
Implements Isolation Forest for anomaly detection
"""

import numpy as np
import pandas as pd
import pickle
import logging
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
import matplotlib.pyplot as plt
from config.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Anomaly detection using Isolation Forest or Local Outlier Factor
    """
    
    def __init__(self, algorithm='isolation_forest'):
        """
        Initialize anomaly detector
        
        Args:
            algorithm (str): 'isolation_forest' or 'lof'
        """
        self.algorithm = algorithm
        self.model = None
        self.threshold = Config.ANOMALY_THRESHOLD
        self.is_fitted = False
        
    def train(self, X_train):
        """
        Train the anomaly detection model on clean historical data
        
        Args:
            X_train (np.ndarray): Training data (PCA-transformed)
        """
        logger.info(f"Training {self.algorithm} model...")
        
        if self.algorithm == 'isolation_forest':
            self.model = IsolationForest(
                contamination=Config.CONTAMINATION,
                n_estimators=Config.N_ESTIMATORS,
                max_samples=Config.MAX_SAMPLES,
                random_state=Config.RANDOM_STATE,
                n_jobs=-1
            )
        elif self.algorithm == 'lof':
            self.model = LocalOutlierFactor(
                contamination=Config.CONTAMINATION,
                novelty=True,  # Enable prediction on new data
                n_jobs=-1
            )
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
        
        # Fit the model
        self.model.fit(X_train)
        self.is_fitted = True
        
        logger.info(f"✓ Model trained on {len(X_train)} samples")
        
        # Analyze score distribution on training data
        self._analyze_score_distribution(X_train)
    
    def _analyze_score_distribution(self, X):
        """
        Analyze anomaly score distribution to help set threshold
        
        Args:
            X (np.ndarray): Data to analyze
        """
        scores = self.model.score_samples(X)
        
        logger.info("\nAnomaly Score Distribution:")
        logger.info(f"  Mean: {np.mean(scores):.4f}")
        logger.info(f"  Std:  {np.std(scores):.4f}")
        logger.info(f"  Min:  {np.min(scores):.4f}")
        logger.info(f"  Max:  {np.max(scores):.4f}")
        logger.info(f"  1st percentile:  {np.percentile(scores, 1):.4f}")
        logger.info(f"  5th percentile:  {np.percentile(scores, 5):.4f}")
        logger.info(f"  10th percentile: {np.percentile(scores, 10):.4f}")
        
        # Recommend threshold
        recommended_threshold = np.percentile(scores, 5)
        logger.info(f"\n✓ Recommended threshold (5th percentile): {recommended_threshold:.4f}")
        logger.info(f"  Current threshold: {self.threshold:.4f}")
        
        return scores
    
    def set_threshold(self, threshold):
        """
        Set custom anomaly threshold
        
        Args:
            threshold (float): Anomaly score threshold
        """
        self.threshold = threshold
        logger.info(f"Threshold set to: {threshold}")
    
    def predict(self, X):
        """
        Predict anomaly scores and flags for new data
        
        Args:
            X (np.ndarray): New data (PCA-transformed)
            
        Returns:
            tuple: (anomaly_scores, is_anomaly_flags)
        """
        if not self.is_fitted:
            raise ValueError("Model not trained. Call train() first.")
        
        # Calculate anomaly scores
        anomaly_scores = self.model.score_samples(X)
        
        # Determine if anomaly based on threshold
        is_anomaly = anomaly_scores < self.threshold
        
        return anomaly_scores, is_anomaly
    
    def predict_single(self, x):
        """
        Predict anomaly for a single sample
        
        Args:
            x (np.ndarray): Single sample (PCA-transformed)
            
        Returns:
            tuple: (anomaly_score, is_anomaly)
        """
        x_reshaped = x.reshape(1, -1)
        scores, flags = self.predict(x_reshaped)
        return scores[0], flags[0]
    
    def save_model(self, filepath='models/anomaly_detector.pkl'):
        """
        Save trained model to file
        
        Args:
            filepath (str): Path to save the model
        """
        try:
            model_data = {
                'model': self.model,
                'algorithm': self.algorithm,
                'threshold': self.threshold,
                'is_fitted': self.is_fitted
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"✓ Model saved to {filepath}")
        
        except Exception as e:
            logger.error(f"✗ Error saving model: {e}")
    
    def load_model(self, filepath='models/anomaly_detector.pkl'):
        """
        Load trained model from file
        
        Args:
            filepath (str): Path to load the model from
        """
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.algorithm = model_data['algorithm']
            self.threshold = model_data['threshold']
            self.is_fitted = model_data['is_fitted']
            
            logger.info(f"✓ Model loaded from {filepath}")
            logger.info(f"  Algorithm: {self.algorithm}")
            logger.info(f"  Threshold: {self.threshold}")
        
        except FileNotFoundError:
            logger.error(f"✗ Model file not found: {filepath}")
        except Exception as e:
            logger.error(f"✗ Error loading model: {e}")
    
    def plot_score_distribution(self, scores, save_path='docs/score_distribution.png'):
        """
        Plot anomaly score distribution
        
        Args:
            scores (np.ndarray): Anomaly scores
            save_path (str): Path to save the plot
        """
        plt.figure(figsize=(10, 6))
        plt.hist(scores, bins=50, alpha=0.7, color='blue', edgecolor='black')
        plt.axvline(self.threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold: {self.threshold:.4f}')
        plt.xlabel('Anomaly Score')
        plt.ylabel('Frequency')
        plt.title('Distribution of Anomaly Scores')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()
        logger.info(f"✓ Score distribution plot saved to {save_path}")
    
    def get_model_info(self):
        """
        Get information about the trained model
        
        Returns:
            dict: Model information
        """
        info = {
            'algorithm': self.algorithm,
            'threshold': self.threshold,
            'is_fitted': self.is_fitted
        }
        
        if self.is_fitted and self.algorithm == 'isolation_forest':
            info['n_estimators'] = self.model.n_estimators
            info['max_samples'] = self.model.max_samples
            info['contamination'] = self.model.contamination
        
        return info


# Test function
if __name__ == "__main__":
    # Generate sample data for testing
    np.random.seed(42)
    
    # Normal data (3 PCA components)
    X_normal = np.random.randn(1000, 3)
    
    # Anomalous data (far from normal)
    X_anomaly = np.random.randn(50, 3) * 3 + 5
    
    # Create and train detector
    detector = AnomalyDetector(algorithm='isolation_forest')
    detector.train(X_normal)
    
    # Test on anomalies
    scores, flags = detector.predict(X_anomaly)
    
    print(f"\nAnomalies detected: {sum(flags)}/{len(flags)}")
    print(f"Detection rate: {sum(flags)/len(flags)*100:.1f}%")
    
    # Plot distribution
    all_scores = detector.model.score_samples(np.vstack([X_normal, X_anomaly]))
    detector.plot_score_distribution(all_scores)
    
    # Save model
    detector.save_model()
    
    print("\n✓ Model test completed")
