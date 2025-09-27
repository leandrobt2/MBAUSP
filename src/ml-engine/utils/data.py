import pandas as pd
from sqlalchemy import create_engine
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
import os

def get_db_connection():
    """
    Create database connection using environment variables.
    """
    connection_string = os.getenv('DATABASE_URL')
    return create_engine(connection_string)

def load_training_data():
    """
    Load training data from the database.
    """
    engine = get_db_connection()
    
    query = """
    SELECT 
        c.classification_id,
        c.company_id,
        co.primary_cnae_id,
        co.city_id,
        c.union_id,
        c.status
    FROM union_classification.Classifications c
    JOIN union_classification.Companies co ON c.company_id = co.company_id
    WHERE c.status = 'APPROVED'
    """
    
    return pd.read_sql(query, engine)

def preprocess_data(data):
    """
    Preprocess data for model training.
    """
    # Prepare features
    features = data[[
        'primary_cnae_id',
        'city_id'
    ]].copy()
    
    # Get labels (union_id)
    labels = data['union_id']
    
    # Apply SMOTE for class balancing
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(features, labels)
    
    return X_resampled, y_resampled