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
from gensim.models import KeyedVectors
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from src.features.feature_engineering import expand_vector, text_features_list

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

# Carregar modelos serializados
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
model_dir = os.path.join(project_root, 'models')
if not os.path.exists(model_dir):
    # fallback caso models esteja em src/models
    model_dir = os.path.join(project_root, 'src', 'models')
pipeline_path = os.path.join(model_dir, 'artifacts', 'pipeline.joblib')
pipeline = joblib.load(pipeline_path)
w2v_path = os.path.join(model_dir, 'word2vec_model.kv')
if not os.path.exists(w2v_path):
    # Arquivo está em src/models
    w2v_path = os.path.join(project_root, 'src', 'models', 'word2vec_model.kv')
w2v_model = KeyedVectors.load(w2v_path, mmap='r')
num_features = 50  # conforme treinamento do Word2Vec = 50  # conforme treinamento do Word2Vec

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
        # recebe vetor pronto
        features = np.array([data['features']])
        pred = pipeline.predict(features)
        response = {'prediction': int(pred[0])}
        if hasattr(pipeline, 'predict_proba'):
            probs = pipeline.predict_proba(features)[0]
            response['probabilities'] = probs.tolist()
            
            # Simular erro baseado na confiança da predição
            max_prob = max(probs)
            simulated_error = 1.0 - max_prob  # Erro simulado baseado na confiança
            prediction_errors.append(simulated_error)
            
            # Manter apenas últimas 100 predições para calcular MAE
            if len(prediction_errors) > 100:
                prediction_errors.pop(0)
            
            # Atualizar MAE médio
            mae = sum(prediction_errors) / len(prediction_errors)
            model_prediction_error.set(mae)
        
        # Registrar métricas
        inference_time = time.time() - start_time
        model_inference_duration.observe(inference_time)
        model_predictions_total.inc()
        
        logger.info(f'/predict → {response}')
        return jsonify(response)
    except Exception as e:
        logger.error(f'/predict error: {e}')
        return jsonify({'error': str(e)}), 400

@app.route('/predict_raw', methods=['POST'])
def predict_raw():
    data = request.get_json()
    start_time = time.time()
    try:
        resume  = data.get('resume', {})
        job_desc = data.get('job', {})

        # 1) Preenche todas as colunas textuais com '' ou com o texto fornecido
        raw = {}
        for feat in text_features_list:
            raw[feat] = resume.get(feat, '') or job_desc.get(feat, '')

        df_raw = pd.DataFrame([raw])

        # 2) Gera embeddings para cada coluna textual
        df_emb = expand_vector(df_raw, text_features_list, w2v_model, num_features)

        # 3) Calcula quantas features numéricas o pipeline espera
        total_dim = pipeline.named_steps['scaler'].mean_.shape[0]
        emb_dim   = df_emb.shape[1]
        num_numeric = total_dim - emb_dim

        # 4) Cria zeros para essas features numéricas que não temos aqui
        numeric_feats = np.zeros((1, num_numeric))

        # 5) Concatena [zeros numéricos | embeddings]
        features = np.hstack([numeric_feats, df_emb.values])

        # 6) Prediz e retorna
        pred = pipeline.predict(features)[0]
        result = {'prediction': int(pred)}
        if hasattr(pipeline, 'predict_proba'):
            probs = pipeline.predict_proba(features)[0]
            result['probabilities'] = probs.tolist()
            
            # Simular erro baseado na confiança da predição
            max_prob = max(probs)
            simulated_error = 1.0 - max_prob  # Erro simulado baseado na confiança
            prediction_errors.append(simulated_error)
            
            # Manter apenas últimas 100 predições para calcular MAE
            if len(prediction_errors) > 100:
                prediction_errors.pop(0)
            
            # Atualizar MAE médio
            mae = sum(prediction_errors) / len(prediction_errors)
            model_prediction_error.set(mae)

        # Registrar métricas
        inference_time = time.time() - start_time
        model_inference_duration.observe(inference_time)
        model_predictions_total.inc()

        logger.info(f'/predict_raw → {result}')
        return jsonify(result)

    except Exception as e:
        logger.error(f'/predict_raw error: {e}')
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    # Rode a partir da raiz do projeto:
    # export PYTHONPATH=$(pwd)
    # python -m src.app.main
    app.run(host='0.0.0.0', port=8080)