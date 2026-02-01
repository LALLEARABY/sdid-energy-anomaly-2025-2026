"""
G4 - Data Preprocessing Module
Synchronizes with G3 normalization parameters and PCA axes
UPDATED: Matches actual database schema with _kw, _v, _a, _wh suffixes
"""

import numpy as np
import pandas as pd
import pickle
import logging
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """
    Handles data preprocessing using G3's normalization parameters
    """
    
    def __init__(self):
        self.scaler = None
        self.pca = None
        # Noms de colonnes EXACTS de la base de données
        self.feature_columns = [
            'global_active_power_kw',
            'global_reactive_power_kw',
            'voltage_v',
            'global_intensity_a',
            'sub_metering_1_wh',
            'sub_metering_2_wh',
            'sub_metering_3_wh'
        ]
        self.g3_params_loaded = False
    
    def load_g3_parameters(self, scaler_path='models/g3_scaler.pkl', pca_path='models/g3_pca.pkl'):
        """
        Load normalization parameters and PCA from G3
        
        Args:
            scaler_path (str): Path to G3's scaler pickle file
            pca_path (str): Path to G3's PCA pickle file
        """
        try:
            # Load scaler
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info(f"✓ Loaded G3 scaler from {scaler_path}")
            
            # Load PCA
            with open(pca_path, 'rb') as f:
                self.pca = pickle.load(f)
            logger.info(f"✓ Loaded G3 PCA from {pca_path}")
            
            self.g3_params_loaded = True
            return True
            
        except FileNotFoundError as e:
            logger.error(f"✗ G3 parameter files not found: {e}")
            logger.warning("Creating default scaler and PCA for development...")
            self._create_default_parameters()
            return False
        
        except Exception as e:
            logger.error(f"✗ Error loading G3 parameters: {e}")
            return False
    
    def _create_default_parameters(self):
        """
        Create default parameters for development/testing
        WARNING: This should only be used when G3 files are not available
        """
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=3, random_state=42)
        logger.warning("⚠ Using default parameters - synchronize with G3 for production!")
    
    def fit_default(self, data):
        """
        Fit default parameters on training data (only if G3 params not available)
        
        Args:
            data (pd.DataFrame): Training data
        """
        if self.g3_params_loaded:
            logger.warning("G3 parameters already loaded. Skipping fit.")
            return
        
        # Select features - gestion des NaN
        X = data[self.feature_columns].fillna(0)
        
        # Fit scaler
        self.scaler.fit(X)
        logger.info("✓ Fitted default scaler")
        
        # Fit PCA
        X_scaled = self.scaler.transform(X)
        self.pca.fit(X_scaled)
        logger.info(f"✓ Fitted default PCA (explained variance: {sum(self.pca.explained_variance_ratio_):.2%})")
    
    def transform(self, data):
        """
        Transform data using G3's normalization and PCA
        
        Args:
            data (pd.DataFrame): Raw data to transform
            
        Returns:
            np.ndarray: Transformed data (PCA components)
        """
        if self.scaler is None or self.pca is None:
            raise ValueError("Preprocessor not initialized. Load G3 parameters first.")
        
        # Select features and handle missing values
        X = data[self.feature_columns].fillna(0)
        
        # Apply normalization
        X_scaled = self.scaler.transform(X)
        
        # Apply PCA transformation
        X_pca = self.pca.transform(X_scaled)
        
        return X_pca
    
    def save_parameters(self, scaler_path='models/g4_scaler.pkl', pca_path='models/g4_pca.pkl'):
        """
        Save current parameters (for backup or if G4 needs to create them)
        
        Args:
            scaler_path (str): Path to save scaler
            pca_path (str): Path to save PCA
        """
        try:
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            with open(pca_path, 'wb') as f:
                pickle.dump(self.pca, f)
            
            logger.info(f"✓ Saved parameters to {scaler_path} and {pca_path}")
        
        except Exception as e:
            logger.error(f"✗ Error saving parameters: {e}")
    
    def get_feature_importance(self):
        """
        Get feature importance from PCA components
        
        Returns:
            pd.DataFrame: Feature importance for each component
        """
        if self.pca is None or self.feature_columns is None:
            return None
        
        components_df = pd.DataFrame(
            self.pca.components_,
            columns=self.feature_columns,
            index=[f'PC{i+1}' for i in range(self.pca.n_components_)]
        )
        
        return components_df


# Test function
if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    
    # Try to load G3 parameters
    if not preprocessor.load_g3_parameters():
        logger.info("Testing with default parameters...")
        
        # Create sample data for testing with EXACT column names
        sample_data = pd.DataFrame({
            'global_active_power_kw': np.random.rand(100) * 5,
            'global_reactive_power_kw': np.random.rand(100) * 0.5,
            'voltage_v': 240 + np.random.rand(100) * 10,
            'global_intensity_a': np.random.rand(100) * 20,
            'sub_metering_1_wh': np.random.rand(100) * 30,
            'sub_metering_2_wh': np.random.rand(100) * 30,
            'sub_metering_3_wh': np.random.rand(100) * 20
        })
        
        preprocessor.fit_default(sample_data)
        transformed = preprocessor.transform(sample_data)
        
        print(f"\nTransformed shape: {transformed.shape}")
        print(f"PCA components: {preprocessor.pca.n_components_}")
        print("\nFeature importance:")
        print(preprocessor.get_feature_importance())
