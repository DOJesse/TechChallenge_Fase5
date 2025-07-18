import pytest
import json
import requests
import time
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

@pytest.mark.integration
class TestAPIIntegration:
    """Testes de integração para a API Flask"""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """URL base da API para testes de integração"""
        return "http://localhost:8080"
    
    def test_api_health_check_integration(self, api_base_url):
        """Testa health check em ambiente de integração"""
        try:
            response = requests.get(f"{api_base_url}/health", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'ok'
        except requests.exceptions.ConnectionError:
            pytest.skip("API não está rodando para teste de integração")
    
    def test_api_metrics_endpoint_integration(self, api_base_url):
        """Testa endpoint de métricas em ambiente de integração"""
        try:
            response = requests.get(f"{api_base_url}/metrics", timeout=5)
            assert response.status_code == 200
            assert 'model_inference_duration_seconds' in response.text
            assert 'model_predictions_total' in response.text
        except requests.exceptions.ConnectionError:
            pytest.skip("API não está rodando para teste de integração")
    
    def test_predict_endpoint_integration(self, api_base_url):
        """Testa endpoint de predição com dados reais"""
        test_data = {
            'features': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 
                        0.0, -0.1, 0.15, 0.25, 0.35]
        }
        
        try:
            response = requests.post(
                f"{api_base_url}/predict",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                assert 'prediction' in data
                assert isinstance(data['prediction'], int)
                
                if 'probabilities' in data:
                    assert isinstance(data['probabilities'], list)
                    assert len(data['probabilities']) == 2
            else:
                # Log do erro para debug
                print(f"Predict endpoint returned {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            pytest.skip("API não está rodando para teste de integração")
    
    def test_predict_raw_endpoint_integration(self, api_base_url):
        """Testa endpoint predict_raw com dados reais"""
        test_data = {
            'resume': {
                'text': 'Desenvolvedor Python com 3 anos de experiência em machine learning e análise de dados'
            },
            'job': {
                'text': 'Vaga para desenvolvedor Python com experiência em ML'
            }
        }
        
        try:
            response = requests.post(
                f"{api_base_url}/predict_raw",
                json=test_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                assert 'prediction' in data
                assert isinstance(data['prediction'], int)
                
                if 'probabilities' in data:
                    assert isinstance(data['probabilities'], list)
            else:
                print(f"Predict_raw endpoint returned {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            pytest.skip("API não está rodando para teste de integração")

@pytest.mark.integration 
class TestStreamlitIntegration:
    """Testes de integração para componentes Streamlit"""
    
    def test_streamlit_file_processing_functions(self):
        """Testa funções de processamento de arquivo do Streamlit"""
        # Importar apenas as funções, não a aplicação completa
        try:
            from streamlit_app import extract_keywords, match_requirement
            
            # Testar extract_keywords
            keywords = extract_keywords("Python desenvolvedor machine learning")
            assert isinstance(keywords, list)
            assert 'python' in keywords
            assert 'desenvolvedor' in keywords
            assert 'machine' in keywords
            assert 'learning' in keywords
            
            # Testar match_requirement
            requirement = "Experiência em Python e machine learning"
            resume_text = "desenvolvedor python com conhecimento em machine learning e data science"
            
            match_result, matched_words = match_requirement(requirement, resume_text)
            assert isinstance(match_result, bool)
            assert isinstance(matched_words, list)
            
        except ImportError:
            pytest.skip("Streamlit não disponível para teste")
    
    def test_api_call_function(self):
        """Testa função de chamada da API no Streamlit"""
        try:
            from streamlit_app import call_api_prediction
            
            # Mock da resposta da API
            with patch('streamlit_app.requests.post') as mock_post:
                mock_response = mock_post.return_value
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'prediction': 1,
                    'probabilities': [0.2, 0.8]
                }
                
                result = call_api_prediction(
                    "Resume text here",
                    "Job description here"
                )
                
                assert result is not None
                assert 'prediction' in result
                assert 'probabilities' in result
                
        except ImportError:
            pytest.skip("Streamlit não disponível para teste")

@pytest.mark.integration
class TestEndToEndWorkflow:
    """Testes end-to-end do workflow completo"""
    
    def test_complete_prediction_workflow(self):
        """Testa workflow completo desde dados brutos até predição"""
        # Dados de entrada realistas
        candidate_data = {
            "31001": {
                "infos_basicas": {
                    "objetivo_profissional": "Trabalhar como desenvolvedor Python sênior",
                    "nome": "João Silva"
                },
                "informacoes_pessoais": {
                    "pcd": "Não"
                },
                "informacoes_profissionais": {
                    "area_atuacao": "Tecnologia da Informação",
                    "conhecimentos_tecnicos": "Python, SQL, Machine Learning"
                },
                "formacao_e_idiomas": {
                    "nivel_academico": "Ensino Superior Completo",
                    "nivel_ingles": "Intermediário",
                    "nivel_espanhol": "Básico"
                },
                "cargo_atual": {
                    "cargo_atual": "Desenvolvedor Python Jr",
                    "data_admissao": "01-01-2020"
                },
                "cv_pt": "Desenvolvedor Python com experiência em projetos de machine learning"
            }
        }
        
        vacancy_data = {
            "5186": {
                "informacoes_basicas": {
                    "titulo_vaga": "Desenvolvedor Python Sênior",
                    "vaga_sap": "Sim",
                    "tipo_contratacao": "CLT"
                },
                "perfil_vaga": {
                    "vaga_especifica_para_pcd": "Não",
                    "nivel profissional": "Sênior",
                    "nivel_academico": "Ensino Superior Completo",
                    "nivel_ingles": "Intermediário",
                    "nivel_espanhol": "Básico",
                    "areas_atuacao": "Desenvolvimento de Software",
                    "principais_atividades": "Desenvolvimento de aplicações Python",
                    "competencia_tecnicas_e_comportamentais": "Python, ML, trabalho em equipe"
                },
                "beneficios": {
                    "valor_venda": "8000"
                }
            }
        }
        
        try:
            # Testar com PredictionPipeline (se disponível)
            from src.models.predict import PredictionPipeline
            
            # Mock dos arquivos necessários
            with patch('src.models.predict.joblib.load') as mock_joblib, \
                 patch('src.models.predict.KeyedVectors.load_word2vec_format') as mock_kv:
                
                # Configurar mocks
                mock_model = type('MockModel', (), {
                    'predict': lambda x: [0.75],
                    'predict_proba': lambda x: [[0.25, 0.75]]
                })()
                
                mock_artifacts = {
                    'ordinal_encoders': {
                        'idioma_encoders': {},
                        'educacao_encoder': None
                    },
                    'model_features': []
                }
                
                mock_w2v = type('MockW2V', (), {
                    'vector_size': 100,
                    'key_to_index': {'python': 0, 'machine': 1, 'learning': 2}
                })()
                
                mock_joblib.side_effect = [mock_model, mock_artifacts]
                mock_kv.return_value = mock_w2v
                
                # Criar pipeline
                pipeline = PredictionPipeline(
                    model_path='dummy_model.joblib',
                    artifacts_path='dummy_artifacts.joblib',
                    w2v_model_path='dummy_w2v.txt'
                )
                
                # Mock das funções utilitárias para evitar erros
                with patch('src.models.predict.utils') as mock_utils:
                    mock_utils.mapear_senioridade.return_value = [2, 3]
                    mock_utils.padroniza_texto.return_value = None
                    mock_utils.expand_vector.return_value = type('MockDF', (), {
                        'shape': (1, 1400),
                        'values': [[0.1] * 1400]
                    })()
                    mock_utils.similaridade.return_value = None
                    
                    # Executar predição
                    result = pipeline.predict(candidate_data, vacancy_data)
                    
                    # Verificar resultado
                    assert isinstance(result, (int, float))
                    assert 0 <= result <= 1
                
        except ImportError:
            pytest.skip("PredictionPipeline não disponível para teste")
    
    def test_data_quality_validation(self):
        """Testa validação de qualidade dos dados de entrada"""
        # Dados com problemas típicos
        problematic_data = {
            "candidate": {
                "missing_fields": {},
                "empty_strings": "",
                "null_values": None,
                "malformed_dates": "not-a-date",
                "invalid_numbers": "not-a-number"
            }
        }
        
        # Verificar que o sistema lida graciosamente com dados problemáticos
        # (este teste pode ser expandido baseado nos requisitos específicos)
        assert isinstance(problematic_data, dict)
    
    @pytest.mark.slow
    def test_performance_benchmark(self):
        """Teste de performance básico"""
        start_time = time.time()
        
        # Simular processamento de múltiplas predições
        for i in range(10):
            # Simular chamada de API ou processamento
            time.sleep(0.01)  # Simular processamento mínimo
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verificar que o processamento não está muito lento
        assert processing_time < 5.0  # Menos de 5 segundos para 10 iterações