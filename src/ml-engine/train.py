import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import xgboost as xgb
from sklearn.metrics import f1_score
import os
from dotenv import load_dotenv

load_dotenv()

def train():
    # Set MLflow tracking URI
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
    mlflow.set_experiment('union-classifier')
    
    with mlflow.start_run():
        # Load and preprocess data
        data = load_data()  # Implement this function to load from your database
        X, y = preprocess_data(data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Apply SMOTE
        smote = SMOTE(random_state=42)
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
        
        # Train model
        model = xgb.XGBClassifier(
            objective='multi:softmax',
            random_state=42
        )
        model.fit(X_train_balanced, y_train_balanced)
        
        # Evaluate
        y_pred = model.predict(X_test)
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # Log metrics
        mlflow.log_metric('f1_score', f1)
        
        # Log model
        mlflow.sklearn.log_model(model, 'model')
        
        return f1

if __name__ == '__main__':
    f1_score = train()
    print(f'Training completed with F1 score: {f1_score}')