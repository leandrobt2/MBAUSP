from flask import Flask, request, jsonify
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
from .utils.features import prepare_features, get_prediction_confidence
from .utils.data import load_training_data, preprocess_data
from .utils.model import train_model, evaluate_model

load_dotenv()

app = Flask(__name__)
mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
client = MlflowClient()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/predict/<company_id>', methods=['POST'])
def predict(company_id):
    try:
        # Get company data from request
        data = request.get_json()
        
        # Load latest production model
        model = mlflow.pyfunc.load_model(
            model_uri=f"models:/union-classifier/Production"
        )
        
        # Prepare features
        features = prepare_features(data)
        
        # Make prediction
        prediction = model.predict(features)
        confidence = get_prediction_confidence(model, features)
        
        app.logger.info(f'Prediction made for company {company_id}: {prediction[0]}')
        
        return jsonify({
            'company_id': company_id,
            'suggested_union_id': int(prediction[0]),
            'confidence_score': float(confidence)
        })
    except Exception as e:
        app.logger.error(f'Prediction error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/retrain', methods=['POST'])
def retrain():
    try:
        # Start MLflow run
        with mlflow.start_run() as run:
            app.logger.info('Starting model retraining')
            
            # Load training data
            data = load_training_data()
            
            # Preprocess data
            X_train, y_train = preprocess_data(data)
            
            # Train model
            model = train_model(X_train, y_train)
            
            # Evaluate model
            metrics = evaluate_model(model, X_train, y_train)
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            app.logger.info(f'Model training completed. Metrics: {metrics}')
            
            # If model meets criteria, register as production
            if metrics['f1_score'] >= 0.82:
                mlflow.sklearn.log_model(
                    model,
                    "model",
                    registered_model_name="union-classifier"
                )
                
                client.transition_model_version_stage(
                    name="union-classifier",
                    version=run.info.run_id,
                    stage="Production"
                )
                
                app.logger.info('New model registered in production')
                
                return jsonify({
                    'status': 'success',
                    'message': 'New model registered in production',
                    'metrics': metrics
                })
            else:
                app.logger.warning('Model did not meet performance criteria')
                
                return jsonify({
                    'status': 'warning',
                    'message': 'Model did not meet performance criteria',
                    'metrics': metrics
                })
                
    except Exception as e:
        app.logger.error(f'Retraining error: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)