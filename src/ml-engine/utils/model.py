from sklearn.ensemble import XGBClassifier
from sklearn.metrics import f1_score, precision_score, recall_score
import numpy as np

def train_model(X_train, y_train):
    """
    Train a new model using the provided data.
    """
    model = XGBClassifier(
        objective='multi:softmax',
        random_state=42,
        n_estimators=100,
        max_depth=6
    )
    
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    """
    Evaluate model performance using various metrics.
    """
    y_pred = model.predict(X_test)
    
    metrics = {
        'f1_score': f1_score(y_test, y_pred, average='weighted'),
        'precision': precision_score(y_test, y_pred, average='weighted'),
        'recall': recall_score(y_test, y_pred, average='weighted')
    }
    
    return metrics