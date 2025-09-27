import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

def prepare_features(data):
    """
    Prepare features for model prediction.
    """
    # Create DataFrame from input data
    df = pd.DataFrame([data])
    
    # Extract features
    features = {
        'primary_cnae': df['primary_cnae_id'],
        'city_id': df['city_id']
    }
    
    # Add secondary CNAEs if present
    if 'secondary_cnaes' in data:
        features['has_secondary_cnaes'] = 1
        features['secondary_cnae_count'] = len(data['secondary_cnaes'])
    else:
        features['has_secondary_cnaes'] = 0
        features['secondary_cnae_count'] = 0
    
    return pd.DataFrame(features)

def get_prediction_confidence(model, features):
    """
    Calculate confidence score for the prediction.
    """
    # Get probability scores for all classes
    probabilities = model.predict_proba(features)
    
    # Return the highest probability as confidence score
    return np.max(probabilities, axis=1)[0]

def encode_labels(df, column):
    """
    Encode categorical labels.
    """
    le = LabelEncoder()
    return le.fit_transform(df[column])