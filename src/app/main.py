import os
import sys
import logging
import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Adiciona o diretório do projeto ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import config
from src.core.exceptions import ModelLoadError, PredictionError, DataValidationError
from src.services.prediction_service import PredictionService
from prometheus_client import REGISTRY

# Desregistrar métricas padrão do coletor do Windows, se existirem
for collector in list(REGISTRY._collector_to_names.keys()):
    if hasattr(collector, '_collector') and 'Windows' in str(type(collector._collector)):
        REGISTRY.unregister(collector)

# Métricas globais para evitar duplicação
_model_predictions_total = None
_model_prediction_score_sum = None

def create_app():
    """Cria e configura uma instância do aplicativo Flask."""
    global _model_predictions_total, _model_prediction_score_sum
    
    app = Flask(__name__)
    
    # Inicializa o exportador de métricas
    metrics = PrometheusMetrics(app)
    
    # Métricas customizadas - usar variáveis globais para evitar duplicação
    if _model_predictions_total is None:
        _model_predictions_total = Counter('model_predictions_total', 'Total number of model predictions made')
    if _model_prediction_score_sum is None:
        _model_prediction_score_sum = Histogram('model_prediction_score', 'Model prediction scores')
    
    model_predictions_total = _model_predictions_total
    model_prediction_score_sum = _model_prediction_score_sum
    
    # Carregar o serviço de predição ao iniciar o aplicativo
    try:
        prediction_service = PredictionService()
        logging.info("Serviço de predição carregado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao carregar o serviço de predição: {e}")
        prediction_service = None

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route('/metrics', methods=['GET'])
    def main_metrics():
        return metrics.export()

    @app.route('/predict', methods=['POST'])
    def predict():
        if not prediction_service:
            return jsonify({"error": "Serviço de predição não carregado"}), 500
            
        try:
            data = request.get_json()
            candidate_data = data['candidate']
            vacancy_data = data['vacancy']
            
            prediction, _ = prediction_service.predict(candidate_data, vacancy_data)
            
            # Registrar métricas
            model_predictions_total.inc()
            model_prediction_score_sum.observe(prediction)
            
            return jsonify({'prediction': prediction})
        except (DataValidationError, PredictionError) as e:
            logging.error(f"/predict validation/prediction error: {e}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logging.error(f"/predict error: {e}")
            return jsonify({'error': str(e)}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)