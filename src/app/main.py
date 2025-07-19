import os
import sys
# Adiciona o diretório raiz do projeto (onde está 'src/') ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import joblib
import numpy as np
import pandas as pd
import logging
import time
from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from src.features.feature_engineering import expand_vector, text_features_list
from src.models.predict import PredictionPipeline

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Inicializar métricas do Prometheus
metrics = PrometheusMetrics(app)

# Métricas customizadas de inferência - registrar no registry padrão
from prometheus_client import REGISTRY

model_inference_duration = Histogram(
    'model_inference_duration_seconds',
    'Tempo de inferência do modelo em segundos',
    registry=REGISTRY
)

model_predictions_total = Counter(
    'model_predictions_total',
    'Total de predições realizadas pelo modelo',
    registry=REGISTRY
)

model_prediction_error = Gauge(
    'model_prediction_error_absolute',
    'Erro absoluto médio das predições do modelo',
    registry=REGISTRY
)


# Carregar modelos serializados e pipeline customizado
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
artifacts_dir = os.path.join(project_root, 'src', 'models', 'artifacts')
model_path = os.path.join(artifacts_dir, 'model.joblib')
artifacts_path = os.path.join(artifacts_dir, 'preprocessing_artifacts.joblib')
w2v_path = os.path.join(project_root, 'src', 'word2vec', 'cbow_s100.txt')

# Inicializa o pipeline customizado
prediction_pipeline = PredictionPipeline(
    model_path=model_path,
    artifacts_path=artifacts_path,
    w2v_model_path=w2v_path
)

# Inicializar métricas com valores padrão para aparecerem no Prometheus
model_prediction_error.set(0)  # Inicializa com 0
logger.info("Métricas customizadas inicializadas")

# Lista para manter histórico de erros para cálculo do MAE
prediction_errors = []

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    start_time = time.time()
    try:
        # Espera-se que o payload tenha 'candidate' e 'vacancy' (dicionários)
        candidate = data.get('candidate')
        vacancy = data.get('vacancy')
        if candidate is None or vacancy is None:
            return jsonify({'error': 'Payload deve conter "candidate" e "vacancy"'}), 400

        pred = prediction_pipeline.predict(candidate, vacancy)
        response = {'prediction': float(pred)}

        # Registrar métricas
        inference_time = time.time() - start_time
        model_inference_duration.observe(inference_time)
        model_predictions_total.inc()

        logger.info(f'/predict → {response}')
        return jsonify(response)
    except Exception as e:
        logger.error(f'/predict error: {e}')
        return jsonify({'error': str(e)}), 400

# A rota /predict_raw pode ser removida ou adaptada conforme a nova estrutura de entrada/saída


if __name__ == '__main__':
    # Rode a partir da raiz do projeto:
    # export PYTHONPATH=$(pwd)
    # python -m src.app.main
    app.run(host='0.0.0.0', port=8080)