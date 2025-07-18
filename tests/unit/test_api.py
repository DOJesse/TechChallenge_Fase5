import pytest
import json
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

@pytest.mark.api
class TestFlaskAPI:
    
    @pytest.fixture
    def app(self):
        """Fixture para criar a aplicação Flask para testes"""
        with patch('src.app.main.joblib.load') as mock_joblib, \
             patch('src.app.main.KeyedVectors.load') as mock_kv:
            
            # Mock do pipeline e modelo Word2Vec
            mock_pipeline = Mock()
            mock_pipeline.predict.return_value = np.array([0.85])
            mock_pipeline.predict_proba.return_value = np.array([[0.15, 0.85]])
            mock_pipeline.named_steps = {'scaler': Mock()}
            mock_pipeline.named_steps['scaler'].mean_ = Mock()
            mock_pipeline.named_steps['scaler'].mean_.shape = (100,)
            
            mock_w2v = Mock()
            mock_w2v.vector_size = 50
            
            mock_joblib.return_value = mock_pipeline
            mock_kv.return_value = mock_w2v
            
            # Importar após os mocks estarem configurados
            from src.app.main import app
            app.config['TESTING'] = True
            
            with app.test_client() as client:
                yield client

    def test_health_endpoint(self, app):
        """Testa o endpoint de health check"""
        response = app.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'

    def test_metrics_endpoint(self, app):
        """Testa o endpoint de métricas Prometheus"""
        response = app.get('/metrics')
        
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/plain; version=0.0.4; charset=utf-8'

    @patch('src.app.main.pipeline')
    def test_predict_endpoint_success(self, mock_pipeline, app):
        """Testa endpoint /predict com dados válidos"""
        # Configurar mock
        mock_pipeline.predict.return_value = np.array([1])
        mock_pipeline.predict_proba.return_value = np.array([[0.2, 0.8]])
        
        # Dados de teste
        test_data = {
            'features': [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        
        response = app.post('/predict', 
                          data=json.dumps(test_data),
                          content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'prediction' in data
        assert 'probabilities' in data
        assert data['prediction'] == 1

    def test_predict_endpoint_missing_features(self, app):
        """Testa endpoint /predict sem features"""
        test_data = {}
        
        response = app.post('/predict',
                          data=json.dumps(test_data),
                          content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_predict_endpoint_invalid_json(self, app):
        """Testa endpoint /predict com JSON inválido"""
        response = app.post('/predict',
                          data='invalid json',
                          content_type='application/json')
        
        assert response.status_code == 400

    @patch('src.app.main.pipeline')
    @patch('src.app.main.expand_vector')
    def test_predict_raw_endpoint_success(self, mock_expand_vector, mock_pipeline, app):
        """Testa endpoint /predict_raw com dados válidos"""
        # Configurar mocks
        mock_pipeline.predict.return_value = np.array([0])
        mock_pipeline.predict_proba.return_value = np.array([[0.7, 0.3]])
        mock_pipeline.named_steps = {'scaler': Mock()}
        mock_pipeline.named_steps['scaler'].mean_ = Mock()
        mock_pipeline.named_steps['scaler'].mean_.shape = (100,)
        
        mock_expand_vector.return_value = Mock()
        mock_expand_vector.return_value.shape = (1, 50)
        mock_expand_vector.return_value.values = np.random.rand(1, 50)
        
        # Dados de teste
        test_data = {
            'resume': {
                'text': 'Desenvolvedor Python com experiência em machine learning'
            },
            'job': {
                'text': 'Vaga para desenvolvedor Python sênior'
            }
        }
        
        response = app.post('/predict_raw',
                          data=json.dumps(test_data),
                          content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'prediction' in data
        assert 'probabilities' in data

    def test_predict_raw_endpoint_missing_data(self, app):
        """Testa endpoint /predict_raw com dados faltando"""
        test_data = {
            'resume': {'text': 'Some resume text'}
            # 'job' is missing
        }
        
        response = app.post('/predict_raw',
                          data=json.dumps(test_data),
                          content_type='application/json')
        
        # Deve funcionar mesmo com dados faltando (usar defaults)
        assert response.status_code in [200, 400]

    @patch('src.app.main.pipeline')
    def test_predict_endpoint_model_error(self, mock_pipeline, app):
        """Testa comportamento quando o modelo gera erro"""
        # Configurar mock para gerar exceção
        mock_pipeline.predict.side_effect = Exception("Model prediction failed")
        
        test_data = {
            'features': [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        
        response = app.post('/predict',
                          data=json.dumps(test_data),
                          content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    @patch('src.app.main.pipeline')
    def test_predict_endpoint_without_proba(self, mock_pipeline, app):
        """Testa endpoint /predict quando modelo não tem predict_proba"""
        # Configurar mock sem predict_proba
        mock_pipeline.predict.return_value = np.array([1])
        mock_pipeline.predict_proba = None
        
        test_data = {
            'features': [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        
        response = app.post('/predict',
                          data=json.dumps(test_data),
                          content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'prediction' in data
        assert 'probabilities' not in data

    def test_predict_endpoint_empty_features_list(self, app):
        """Testa endpoint /predict com lista de features vazia"""
        test_data = {
            'features': []
        }
        
        response = app.post('/predict',
                          data=json.dumps(test_data),
                          content_type='application/json')
        
        assert response.status_code == 400

    def test_predict_endpoint_invalid_features_type(self, app):
        """Testa endpoint /predict com tipo inválido de features"""
        test_data = {
            'features': "not a list"
        }
        
        response = app.post('/predict',
                          data=json.dumps(test_data),
                          content_type='application/json')
        
        assert response.status_code == 400

@pytest.mark.api
class TestAPIMetrics:
    
    @pytest.fixture
    def app(self):
        """Fixture para criar a aplicação Flask para testes de métricas"""
        with patch('src.app.main.joblib.load') as mock_joblib, \
             patch('src.app.main.KeyedVectors.load') as mock_kv:
            
            mock_pipeline = Mock()
            mock_pipeline.predict.return_value = np.array([0.85])
            mock_pipeline.predict_proba.return_value = np.array([[0.15, 0.85]])
            mock_pipeline.named_steps = {'scaler': Mock()}
            mock_pipeline.named_steps['scaler'].mean_ = Mock()
            mock_pipeline.named_steps['scaler'].mean_.shape = (100,)
            
            mock_w2v = Mock()
            mock_w2v.vector_size = 50
            
            mock_joblib.return_value = mock_pipeline
            mock_kv.return_value = mock_w2v
            
            from src.app.main import app
            app.config['TESTING'] = True
            
            with app.test_client() as client:
                yield client

    @patch('src.app.main.model_predictions_total')
    @patch('src.app.main.model_inference_duration')
    @patch('src.app.main.pipeline')
    def test_metrics_are_recorded(self, mock_pipeline, mock_duration, mock_counter, app):
        """Testa se métricas são registradas corretamente"""
        # Configurar mocks
        mock_pipeline.predict.return_value = np.array([1])
        mock_pipeline.predict_proba.return_value = np.array([[0.3, 0.7]])
        
        test_data = {'features': [0.1, 0.2, 0.3, 0.4, 0.5]}
        
        response = app.post('/predict',
                          data=json.dumps(test_data),
                          content_type='application/json')
        
        assert response.status_code == 200
        
        # Verificar se métricas foram chamadas
        mock_counter.inc.assert_called_once()
        mock_duration.observe.assert_called_once()

    def test_metrics_endpoint_format(self, app):
        """Testa formato do endpoint de métricas"""
        response = app.get('/metrics')
        
        assert response.status_code == 200
        metrics_text = response.data.decode('utf-8')
        
        # Verificar presença de métricas específicas
        assert 'model_inference_duration_seconds' in metrics_text
        assert 'model_predictions_total' in metrics_text
        assert 'model_prediction_error_absolute' in metrics_text

@pytest.mark.api
class TestAPIIntegration:
    
    @pytest.fixture
    def app_with_real_dependencies(self):
        """Fixture que simula dependências mais realistas"""
        with patch('src.app.main.joblib.load') as mock_joblib, \
             patch('src.app.main.KeyedVectors.load') as mock_kv, \
             patch('src.app.main.expand_vector') as mock_expand:
            
            # Mock mais realista do pipeline
            mock_pipeline = Mock()
            mock_pipeline.predict.return_value = np.array([0.75])
            mock_pipeline.predict_proba.return_value = np.array([[0.25, 0.75]])
            mock_pipeline.named_steps = {
                'scaler': Mock(mean_=np.random.rand(150))
            }
            
            # Mock do Word2Vec
            mock_w2v = Mock()
            mock_w2v.vector_size = 50
            
            # Mock do expand_vector
            mock_expand_result = Mock()
            mock_expand_result.shape = (1, 100)
            mock_expand_result.values = np.random.rand(1, 100)
            mock_expand.return_value = mock_expand_result
            
            mock_joblib.return_value = mock_pipeline
            mock_kv.return_value = mock_w2v
            
            from src.app.main import app
            app.config['TESTING'] = True
            
            with app.test_client() as client:
                yield client

    def test_full_prediction_workflow(self, app_with_real_dependencies):
        """Testa workflow completo de predição"""
        # Dados mais realistas
        test_data = {
            'resume': {
                'text': 'Desenvolvedor Python sênior com 5 anos de experiência em machine learning, conhecimento em scikit-learn, pandas, numpy',
                'skills': 'Python, ML, Data Science',
                'experience': '5 years'
            },
            'job': {
                'text': 'Procuramos desenvolvedor Python sênior para trabalhar com projetos de ciência de dados e machine learning',
                'requirements': 'Python, ML, 3+ years experience',
                'level': 'Senior'
            }
        }
        
        response = app_with_real_dependencies.post('/predict_raw',
                                                 data=json.dumps(test_data),
                                                 content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verificar estrutura da resposta
        assert 'prediction' in data
        assert 'probabilities' in data
        assert isinstance(data['prediction'], int)
        assert isinstance(data['probabilities'], list)
        assert len(data['probabilities']) == 2  # Binário: 0 ou 1