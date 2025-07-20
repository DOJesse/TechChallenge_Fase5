import pytest
from unittest.mock import patch, MagicMock
import numpy as np
from flask import Flask

# Adiciona o diretório raiz do projeto ao sys.path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.app.main import create_app
from src.models.predict import PredictionPipeline

@pytest.fixture
def app(sample_candidate_data, sample_vacancy_data):
    """Fixture da aplicação Flask para testes"""
    with patch('src.services.prediction_service.PredictionService') as mock_service_class:
        # Configurar mock do serviço
        mock_service = mock_service_class.return_value
        mock_service.predict.return_value = (0.85, None)
        mock_service.health_check.return_value = {"status": "healthy", "service": "prediction"}
        
        from src.app.main import create_app
        app = create_app()
        app.config['TESTING'] = True

@pytest.fixture
def client(app):
    """Um cliente de teste para o aplicativo Flask."""
    return app.test_client()

@pytest.fixture
def app_with_metrics(app):
    """Fixture que retorna o app já configurado com métricas."""
    return app

@pytest.fixture
def app_with_real_dependencies():
    """Fixture da aplicação Flask com dependências reais para testes de integração"""
    with patch('src.services.prediction_service.PredictionService') as mock_service_class:
        # Configurar mock do serviço para simular dependências reais
        mock_service = mock_service_class.return_value
        mock_service.predict.return_value = (0.75, {"additional": "data"})
        
        from src.app.main import create_app
        app = create_app()
        app.config['TESTING'] = True
        yield app

class TestFlaskAPI:
    """Testes para os endpoints básicos da API."""
    def test_health_endpoint(self, client):
        """Testa o endpoint de health check."""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.get_json() == {"status": "ok"}

    def test_metrics_endpoint(self, client):
        """Testa o endpoint de métricas."""
        response = client.get('/metrics')
        assert response.status_code == 200
        # Verifica a presença de uma métrica padrão do Flask para confirmar que o endpoint funciona
        assert 'flask_http_request_total' in response.data.decode('utf-8')

    def test_predict_endpoint_success(self, client):
        """Testa o endpoint de predição com sucesso."""
        candidate_data = {"job_description": "Engenheiro de Software", "candidate_resume": "Python, APIs"}
        vacancy_data = {"vacancy_title": "Engenheiro Sênior", "vacancy_description": "Desenvolvimento de APIs"}
        response = client.post('/predict', json={"candidate": candidate_data, "vacancy": vacancy_data})
        
        assert response.status_code == 200
        assert 'prediction' in response.get_json()

class TestAPIMetrics:
    """Testes para as métricas da API."""
    def test_metrics_are_recorded(self, client, sample_candidate_data, sample_vacancy_data):
        """Testa se as métricas do Prometheus são gravadas após uma chamada de predição."""
        # Chama o endpoint de predição para gerar métricas usando dados válidos
        client.post('/predict', json={"candidate": sample_candidate_data, "vacancy": sample_vacancy_data})

        # Em seguida, busca as métricas
        response = client.get('/metrics')
        assert response.status_code == 200
        metrics_text = response.data.decode('utf-8')
        assert 'model_predictions_total' in metrics_text
        assert 'model_prediction_score_sum' in metrics_text

class TestAPIIntegration:
    """Testes de integração para a API."""
    def test_full_prediction_workflow(self, app_with_real_dependencies):
        """Testa o fluxo completo de predição com dependências reais."""
        client = app_with_real_dependencies.test_client()
        
        candidate_data = {"job_description": "Engenheiro de Software", "candidate_resume": "Python, APIs, Docker"}
        vacancy_data = {"vacancy_title": "Engenheiro de Software Sênior", "vacancy_description": "Procuramos um engenheiro com experiência em Python."}
        
        response = client.post('/predict', json={"candidate": candidate_data, "vacancy": vacancy_data})
        data = response.get_json()

        assert response.status_code == 200
        assert 'prediction' in data
        assert isinstance(data['prediction'], float)