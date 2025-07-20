import os
import sys
# Adiciona o diretório raiz do projeto (onde está 'src/') ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import logging
import time
import math
import random
import numpy as np
from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from src.models.predict import PredictionPipeline
from src.services.prediction_service import PredictionService

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar drift detection
try:
    from src.monitoring.drift_detection import DriftMonitor
    DRIFT_MONITORING_ENABLED = True
    logger.info("Drift detection module loaded successfully")
except ImportError as e:
    logger.warning(f"Drift detection not available: {e}")
    DRIFT_MONITORING_ENABLED = False

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

# Novas métricas críticas para ML em produção
model_prediction_confidence = Histogram(
    'model_prediction_confidence',
    'Distribuição de confiança das predições',
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    registry=REGISTRY
)

model_prediction_value_distribution = Histogram(
    'model_prediction_value_distribution',
    'Distribuição dos valores de predição',
    buckets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    registry=REGISTRY
)

model_high_confidence_predictions = Counter(
    'model_high_confidence_predictions_total',
    'Predições com alta confiança (>0.8 ou <0.2)',
    registry=REGISTRY
)

api_health_check_total = Counter(
    'api_health_check_total',
    'Total de verificações de saúde da API',
    registry=REGISTRY
)

# Métricas para contar erros de aplicação
api_errors_total = Counter(
    'api_errors_total',
    'Total de erros na API (HTTP 4xx/5xx)',
    ['method', 'status_code'],
    registry=REGISTRY
)

api_prediction_errors_total = Counter(
    'api_prediction_errors_total',
    'Total de erros específicos de predição',
    ['error_type'],
    registry=REGISTRY
)

# Métricas para Drift Detection
drift_detection_alerts_total = Counter(
    'drift_detection_alerts_total',
    'Total de alertas de drift detectados',
    ['alert_type'],
    registry=REGISTRY
)

# Limpar métricas existentes para evitar labels antigos
drift_detection_alerts_total.clear()

drift_data_features_analyzed = Gauge(
    'drift_data_features_analyzed',
    'Número de features analisadas para data drift',
    registry=REGISTRY
)

drift_data_features_with_drift = Gauge(
    'drift_data_features_with_drift',
    'Número de features com data drift detectado',
    registry=REGISTRY
)

drift_concept_performance_accuracy = Gauge(
    'drift_concept_performance_accuracy',
    'Accuracy atual do modelo para concept drift detection',
    registry=REGISTRY
)

drift_concept_performance_degradation = Gauge(
    'drift_concept_performance_degradation',
    'Percentual de degradação de performance detectado',
    registry=REGISTRY
)

drift_monitoring_executions_total = Counter(
    'drift_monitoring_executions_total',
    'Total de execuções de monitoramento de drift',
    registry=REGISTRY
)

# Inicializar o serviço de predição
try:
    prediction_service = PredictionService()
    logger.info("Serviço de predição inicializado com sucesso")
except Exception as e:
    logger.error(f"Erro ao inicializar serviço de predição: {e}")
    prediction_service = None

# Inicializar o monitor de drift detection
drift_monitor = None
if DRIFT_MONITORING_ENABLED:
    try:
        # Configuração baseline para o modelo (deve ser ajustada com dados reais)
        baseline_performance = {
            'accuracy': 0.85,
            'precision': 0.82,
            'recall': 0.80
        }
        
        drift_monitor = DriftMonitor(
            baseline_performance=baseline_performance,
            config={
                'data_drift': {
                    'significance_level': 0.05,
                    'reference_window_size': 500,
                    'detection_window_size': 50
                },
                'concept_drift': {
                    'degradation_threshold': 0.1,
                    'window_size': 50
                }
            }
        )
        logger.info("Drift monitor inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar drift monitor: {e}")
        drift_monitor = None

# Inicializar métricas com valores padrão para aparecerem no Prometheus
model_prediction_error.set(0)  # Inicializa com 0
logger.info("Métricas customizadas inicializadas")

# Lista para manter histórico de erros para cálculo do MAE
prediction_errors = []

@app.route('/health', methods=['GET'])
def health():
    api_health_check_total.inc()
    try:
        # Verificar se o serviço de predição está funcionando
        if prediction_service:
            return jsonify({
                'status': 'ok',
                'service': 'healthy',
                'model_loaded': True,
                'timestamp': time.time()
            })
        else:
            api_errors_total.labels(method='GET', status_code='503').inc()
            return jsonify({
                'status': 'degraded',
                'service': 'prediction_service_unavailable',
                'model_loaded': False,
                'timestamp': time.time()
            }), 503
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        api_errors_total.labels(method='GET', status_code='500').inc()
        return jsonify({
            'status': 'error',
            'service': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/drift/status')
def drift_status():
    """Endpoint para verificar status do drift monitoring"""
    if not drift_monitor:
        return jsonify({
            'drift_monitoring_enabled': False,
            'message': 'Drift monitoring not available'
        }), 404
        
    try:
        summary = drift_monitor.get_drift_summary()
        return jsonify({
            'drift_monitoring_enabled': True,
            'summary': summary,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Erro ao obter status de drift: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/drift/alerts')
def drift_alerts():
    """Endpoint para listar alertas de drift recentes"""
    if not drift_monitor:
        return jsonify({
            'drift_monitoring_enabled': False,
            'alerts': []
        }), 404
        
    try:
        summary = drift_monitor.get_drift_summary()
        
        # Formatar alertas para JSON
        recent_alerts = []
        
        # Data drift alerts
        for alert in summary.get('last_data_drift_alerts', []):
            recent_alerts.append({
                'timestamp': alert.timestamp.isoformat(),
                'type': alert.drift_type,
                'severity': alert.severity,
                'metric': alert.metric,
                'value': alert.value,
                'threshold': alert.threshold,
                'message': alert.message
            })
            
        # Concept drift alerts  
        for alert in summary.get('last_concept_drift_alerts', []):
            recent_alerts.append({
                'timestamp': alert.timestamp.isoformat(),
                'type': alert.drift_type,
                'severity': alert.severity,
                'metric': alert.metric,
                'value': alert.value,
                'threshold': alert.threshold,
                'message': alert.message
            })
            
        # Ordenar por timestamp
        recent_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'drift_monitoring_enabled': True,
            'total_alerts': len(recent_alerts),
            'alerts': recent_alerts[:10],  # Últimos 10 alertas
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter alertas de drift: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/drift/initialize', methods=['POST'])
def initialize_drift_reference():
    """Endpoint para inicializar dados de referência para drift detection"""
    if not drift_monitor:
        return jsonify({
            'success': False,
            'message': 'Drift monitoring not available'
        }), 404
        
    try:
        # Gerar dados de referência simulados (em produção, usar dados históricos reais)
        import numpy as np
        
        reference_data = {
            'candidate_skills_length': np.random.normal(50, 15, 1000),
            'candidate_experience_length': np.random.normal(30, 10, 1000),
            'vacancy_requirements_length': np.random.normal(40, 12, 1000),
            'vacancy_seniority_encoded': np.random.randint(0, 100, 1000),
            'prediction_value': np.random.beta(2, 2, 1000),  # Distribuição realista para predições
            'prediction_confidence': np.random.beta(3, 2, 1000)
        }
        
        drift_monitor.initialize_reference_data(reference_data)
        
        return jsonify({
            'success': True,
            'message': 'Reference data initialized for drift detection',
            'features_count': len(reference_data),
            'samples_per_feature': len(next(iter(reference_data.values()))),
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Erro ao inicializar dados de referência: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()
    try:
        if not prediction_service:
            return jsonify({'error': 'Serviço de predição não inicializado'}), 500
            
        data = request.get_json()
        candidate_data = data.get('candidate', {})
        vacancy_data = data.get('vacancy', {})
        
        # Usar o serviço de predição
        prediction, additional_data = prediction_service.predict(candidate_data, vacancy_data)
        
        # Criar resultado final
        result = {
            'prediction': float(prediction)
        }
        
        # Adicionar SHAP values se disponível, convertendo para lista
        if additional_data is not None:
            try:
                # Converter numpy array para lista para serialização JSON
                if isinstance(additional_data, np.ndarray):
                    result['shap_values'] = additional_data.tolist()
                else:
                    result['shap_values'] = additional_data
            except Exception as e:
                logger.warning(f"Erro ao processar SHAP values: {e}")
                result['shap_values'] = None
        
        # Registrar métricas avançadas de ML
        prediction_value = float(prediction)
        
        # Monitoramento de Drift Detection
        if drift_monitor:
            try:
                # Extrair features para drift detection
                features = {}
                
                # Features do candidato
                if 'skills' in candidate_data:
                    features['candidate_skills_length'] = len(str(candidate_data['skills']))
                if 'experience' in candidate_data:
                    features['candidate_experience_length'] = len(str(candidate_data['experience']))
                    
                # Features da vaga
                if 'requirements' in vacancy_data:
                    features['vacancy_requirements_length'] = len(str(vacancy_data['requirements']))
                if 'seniority' in vacancy_data:
                    features['vacancy_seniority_encoded'] = hash(str(vacancy_data['seniority'])) % 100
                    
                # Adicionar valor de predição como feature
                features['prediction_value'] = prediction_value
                features['prediction_confidence'] = 1 - abs(0.5 - prediction_value) * 2
                
                # Monitorar drift (sem labels verdadeiros neste exemplo)
                drift_results = drift_monitor.monitor_prediction(
                    features=features,
                    y_true=None,  # Seria fornecido se houvesse feedback
                    y_pred=int(prediction_value > 0.5),
                    y_pred_proba=prediction_value
                )
                
                # Incrementar contador de execuções do monitoramento
                drift_monitoring_executions_total.inc()
                
                # Atualizar métricas de drift
                if drift_results.get('data_drift'):
                    data_drift = drift_results['data_drift']
                    drift_data_features_analyzed.set(data_drift.get('features_analyzed', 0))
                    drift_data_features_with_drift.set(data_drift.get('features_with_drift', 0))
                    
                    # Contar alertas de data drift
                    for alert in data_drift.get('alerts', []):
                        drift_detection_alerts_total.labels(
                            alert_type='data_drift'
                        ).inc()
                        
                if drift_results.get('concept_drift'):
                    concept_drift = drift_results['concept_drift']
                    
                    # Contar alertas de concept drift
                    if 'drift_results' in concept_drift:
                        for alert in concept_drift['drift_results'].get('alerts', []):
                            drift_detection_alerts_total.labels(
                                alert_type='concept_drift'
                            ).inc()
                            
                    # Atualizar métricas de performance
                    if 'rolling_metrics' in concept_drift:
                        rolling_metrics = concept_drift['rolling_metrics']
                        if 'accuracy' in rolling_metrics:
                            drift_concept_performance_accuracy.set(rolling_metrics['accuracy'])
                
                # SIMULAÇÃO PARA DEMONSTRAÇÃO: Atualizar performance baseada no número de execuções
                # Isso é apenas para fins de demonstração do dashboard
                current_time = time.time()
                # Simular performance que varia com o tempo e número de predições
                simulated_accuracy = 0.75 + 0.15 * math.sin(current_time / 100) + 0.05 * random.random()
                simulated_accuracy = max(0.5, min(0.95, simulated_accuracy))  # Manter entre 50% e 95%
                drift_concept_performance_accuracy.set(simulated_accuracy)
                            
                # Adicionar informações de drift na resposta (opcional)
                if drift_results.get('alerts'):
                    result['drift_alerts'] = len(drift_results['alerts'])
                    
            except Exception as e:
                logger.warning(f"Erro no monitoramento de drift: {e}")
        
        # Métrica de distribuição de valores de predição
        model_prediction_value_distribution.observe(prediction_value)
        
        # Métrica de confiança (baseada na distância de 0.5)
        confidence = 1 - abs(0.5 - prediction_value) * 2  # Normalizar para 0-1
        model_prediction_confidence.observe(confidence)
        
        # Contador de predições de alta confiança
        if prediction_value > 0.8 or prediction_value < 0.2:
            model_high_confidence_predictions.inc()
        
        # Simular erro baseado na confiança da predição
        simulated_error = abs(0.5 - prediction_value)  # Erro simulado
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
        
        logger.info(f'/predict → {result}')
        return jsonify(result)
        
    except Exception as e:
        logger.error(f'/predict error: {e}')
        
        # Contar erro de predição
        api_prediction_errors_total.labels(error_type='prediction_failure').inc()
        api_errors_total.labels(method='POST', status_code='400').inc()
        
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # Verificar se a porta está configurada corretamente
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Iniciando aplicação na porta {port}")
    app.run(host='0.0.0.0', port=port)