"""
G4 - Database Connection Module
Handles PostgreSQL connection and data retrieval
"""

import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import logging
from config.config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Manages database connections and queries"""
    
    def __init__(self):
        self.config = Config()
        self.engine = None
        self.connection = None
        
    def connect(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.engine = create_engine(Config.get_db_connection_string())
            self.connection = self.engine.connect()
            logger.info("✓ Successfully connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def get_historical_data(self, limit=None):
        """
        Retrieve historical data for model training
        
        Args:
            limit (int): Maximum number of records to retrieve
            
        Returns:
            pd.DataFrame: Historical power consumption data
        """
        try:
            query = "SELECT * FROM power_consumption WHERE is_anomaly IS NULL OR is_anomaly = FALSE"
            
            if limit:
                query += f" LIMIT {limit}"
            
            df = pd.read_sql(query, self.engine)
            logger.info(f"✓ Retrieved {len(df)} historical records")
            return df
        
        except Exception as e:
            logger.error(f"✗ Error retrieving historical data: {e}")
            return pd.DataFrame()
    
    def get_unscored_data(self, batch_size=100):
        """
        Retrieve data that hasn't been scored yet
        
        Args:
            batch_size (int): Number of records to retrieve
            
        Returns:
            pd.DataFrame: Unscored power consumption data
        """
        try:
            query = f"""
            SELECT * FROM power_consumption 
            WHERE anomaly_score IS NULL 
            ORDER BY timestamp ASC 
            LIMIT {batch_size}
            """
            
            df = pd.read_sql(query, self.engine)
            
            if len(df) > 0:
                logger.info(f"✓ Retrieved {len(df)} unscored records")
            
            return df
        
        except Exception as e:
            logger.error(f"✗ Error retrieving unscored data: {e}")
            return pd.DataFrame()
    
    def update_anomaly_scores(self, updates):
        """
        Update anomaly scores and flags in database
        
        Args:
            updates (list): List of tuples (id, anomaly_score, is_anomaly)
        """
        try:
            conn = psycopg2.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )
            cursor = conn.cursor()
            
            update_query = """
            UPDATE power_consumption 
            SET anomaly_score = %s, is_anomaly = %s 
            WHERE id = %s
            """
            
            for record_id, score, is_anomaly in updates:
                cursor.execute(update_query, (score, is_anomaly, record_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"✓ Updated {len(updates)} records with anomaly scores")
            
        except Exception as e:
            logger.error(f"✗ Error updating anomaly scores: {e}")
    
    def get_anomaly_statistics(self):
        """
        Get statistics about detected anomalies
        
        Returns:
            dict: Statistics about anomalies
        """
        try:
            query = """
            SELECT 
                COUNT(*) as total_records,
                SUM(CASE WHEN is_anomaly = TRUE THEN 1 ELSE 0 END) as total_anomalies,
                AVG(CASE WHEN is_anomaly = TRUE THEN 1.0 ELSE 0.0 END) * 100 as anomaly_rate,
                MIN(timestamp) as first_record,
                MAX(timestamp) as last_record
            FROM power_consumption
            WHERE anomaly_score IS NOT NULL
            """
            
            df = pd.read_sql(query, self.engine)
            return df.to_dict('records')[0]
        
        except Exception as e:
            logger.error(f"✗ Error retrieving statistics: {e}")
            return {}
    
    def test_connection(self):
        """Test database connection"""
        try:
            query = "SELECT COUNT(*) as count FROM power_consumption"
            df = pd.read_sql(query, self.engine)
            count = df['count'][0]
            logger.info(f"✓ Connection test successful. Total records: {count}")
            return True
        except Exception as e:
            logger.error(f"✗ Connection test failed: {e}")
            return False


# Test function
if __name__ == "__main__":
    db = DatabaseConnection()
    if db.connect():
        db.test_connection()
        stats = db.get_anomaly_statistics()
        print("\nDatabase Statistics:")
        print(stats)
        db.disconnect()
