import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import joblib

# Adicionar o diretório raiz ao Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

try:
    from src.models.predict import PredictionPipeline
except ImportError:
    # Fallback para importação direta
    import importlib.util
    predict_path = os.path.join(project_root, 'src', 'models', 'predict.py')
    spec = importlib.util.spec_from_file_location("predict", predict_path)
    predict_module = importlib.util.module_from_spec(spec)
    
    # Mock do utils antes de carregar o módulo
    with patch.dict('sys.modules', {'models.utils': Mock()}):
        spec.loader.exec_module(predict_module)
    
    PredictionPipeline = predict_module.PredictionPipeline

@pytest.mark.unit
class TestPredictionPipeline:
    
    @patch('src.models.predict.joblib.load')
    @patch('src.models.predict.KeyedVectors.load_word2vec_format')
    def test_pipeline_initialization(self, mock_kv_load, mock_joblib_load):
        """Testa inicialização do pipeline"""
        # Mock do modelo de ML
        mock_model = Mock()
        mock_joblib_load.side_effect = [
            mock_model,  # Primeiro call: modelo
            {  # Segundo call: artefatos
                'ordinal_encoders': {
                    'idioma_encoders': {'nivel_ingles': Mock(), 'nivel_espanhol': Mock()},
                    'educacao_encoder': Mock()
                },
                'model_features': ['feature1', 'feature2']
            }
        ]
        
        # Mock do modelo Word2Vec
        mock_w2v = Mock()
        mock_w2v.vector_size = 100
        mock_kv_load.return_value = mock_w2v
        
        pipeline = PredictionPipeline(
            model_path='model.joblib',
            artifacts_path='artifacts.joblib',
            w2v_model_path='w2v.txt'
        )
        
        assert pipeline.model == mock_model
        assert pipeline.model_w2v == mock_w2v
        assert pipeline.NUM_FEATURES_W2V == 100
        assert 'idioma_encoders' in pipeline.ordinal_encoders
        assert pipeline.model_features_order == ['feature1', 'feature2']

    @patch('src.models.predict.joblib.load')
    @patch('src.models.predict.KeyedVectors.load_word2vec_format')
    def test_pipeline_initialization_missing_artifacts(self, mock_kv_load, mock_joblib_load):
        """Testa inicialização com artefatos faltando"""
        mock_model = Mock()
        mock_joblib_load.side_effect = [
            mock_model,
            {}  # Artefatos vazios
        ]
        
        mock_w2v = Mock()
        mock_w2v.vector_size = 50
        mock_kv_load.return_value = mock_w2v
        
        pipeline = PredictionPipeline(
            model_path='model.joblib',
            artifacts_path='artifacts.joblib',
            w2v_model_path='w2v.txt'
        )
        
        assert pipeline.ordinal_encoders == {}
        assert pipeline.model_features_order == []

    @patch('src.models.predict.joblib.load')
    @patch('src.models.predict.KeyedVectors.load_word2vec_format')
    @patch('src.models.predict.utils', create=True)
    def test_prepare_data_basic_flow(self, mock_utils, mock_kv_load, mock_joblib_load, 
                                   sample_candidate_data, sample_vacancy_data):
        """Testa fluxo básico do _prepare_data"""
        # Setup mocks
        mock_model = Mock()
        mock_encoders = {
            'idioma_encoders': {
                'nivel_ingles': Mock(),
                'nivel_espanhol': Mock()
            },
            'educacao_encoder': Mock()
        }
        
        for encoder in mock_encoders['idioma_encoders'].values():
            encoder.transform.return_value = np.array([[2], [3]])
        mock_encoders['educacao_encoder'].transform.return_value = np.array([[4], [5]])
        
        mock_joblib_load.side_effect = [
            mock_model,
            {
                'ordinal_encoders': mock_encoders,
                'model_features': ['feature1', 'feature2']
            }
        ]
        
        mock_w2v = Mock()
        mock_w2v.vector_size = 100
        mock_kv_load.return_value = mock_w2v
        
        # Mock das funções utilitárias
        mock_utils.mapear_senioridade.return_value = pd.Series([2, 3])
        mock_utils.padroniza_texto.return_value = None
        mock_utils.expand_vector.return_value = pd.DataFrame(np.random.rand(1, 1600))
        mock_utils.similaridade.return_value = None
        
        pipeline = PredictionPipeline(
            model_path='model.joblib',
            artifacts_path='artifacts.joblib',
            w2v_model_path='w2v.txt'
        )
        
        # Chamar o método
        result = pipeline._prepare_data(sample_candidate_data, sample_vacancy_data)
        
        # Verificações
        assert isinstance(result, pd.DataFrame)
        assert not result.empty

    @patch('src.models.predict.joblib.load')
    @patch('src.models.predict.KeyedVectors.load_word2vec_format')
    def test_predict_method(self, mock_kv_load, mock_joblib_load,
                          sample_candidate_data, sample_vacancy_data):
        """Testa o método predict"""
        # Setup mocks
        mock_model = Mock()
        mock_model.predict.return_value = np.array([0.85])
        
        mock_joblib_load.side_effect = [
            mock_model,
            {
                'ordinal_encoders': {
                    'idioma_encoders': {},
                    'educacao_encoder': Mock()
                },
                'model_features': []
            }
        ]
        
        mock_w2v = Mock()
        mock_w2v.vector_size = 100
        mock_kv_load.return_value = mock_w2v
        
        pipeline = PredictionPipeline(
            model_path='model.joblib',
            artifacts_path='artifacts.joblib',
            w2v_model_path='w2v.txt'
        )
        
        # Mock _prepare_data para retornar um DataFrame simples
        mock_df = pd.DataFrame([[1, 2, 3, 4, 5]], columns=['f1', 'f2', 'f3', 'f4', 'f5'])
        with patch.object(pipeline, '_prepare_data', return_value=mock_df):
            result = pipeline.predict(sample_candidate_data, sample_vacancy_data)
        
        assert result == 0.85
        mock_model.predict.assert_called_once()

    @patch('src.models.predict.joblib.load')
    @patch('src.models.predict.KeyedVectors.load_word2vec_format')
    @patch('src.models.predict.pd.to_datetime')
    def test_prepare_data_date_handling(self, mock_to_datetime, mock_kv_load, mock_joblib_load,
                                      sample_candidate_data, sample_vacancy_data):
        """Testa tratamento de datas no _prepare_data"""
        # Mock para as datas
        mock_to_datetime.side_effect = [
            pd.Timestamp('2025-07-01'),  # Data atual
            pd.Series([pd.Timestamp('2018-05-24')])  # Data de admissão
        ]
        
        mock_model = Mock()
        mock_joblib_load.side_effect = [
            mock_model,
            {
                'ordinal_encoders': {
                    'idioma_encoders': {},
                    'educacao_encoder': None
                },
                'model_features': []
            }
        ]
        
        mock_w2v = Mock()
        mock_w2v.vector_size = 100
        mock_kv_load.return_value = mock_w2v
        
        pipeline = PredictionPipeline(
            model_path='model.joblib',
            artifacts_path='artifacts.joblib',
            w2v_model_path='w2v.txt'
        )
        
        # Mock das funções utilitárias necessárias
        with patch('src.models.predict.utils', create=True) as mock_utils:
            mock_utils.mapear_senioridade.return_value = pd.Series([2])
            mock_utils.padroniza_texto.return_value = None
            mock_utils.expand_vector.return_value = pd.DataFrame(np.random.rand(1, 1400))
            mock_utils.similaridade.return_value = None
            
            result = pipeline._prepare_data(sample_candidate_data, sample_vacancy_data)
        
        # Verificar que não houve erros na execução
        assert isinstance(result, pd.DataFrame)

    @patch('src.models.predict.joblib.load')
    @patch('src.models.predict.KeyedVectors.load_word2vec_format')
    def test_prepare_data_missing_fields(self, mock_kv_load, mock_joblib_load):
        """Testa _prepare_data com campos faltando"""
        # Dados incompletos
        incomplete_candidate = {
            "31001": {
                "infos_basicas": {"nome": "Test"},
                "informacoes_pessoais": {},
                "informacoes_profissionais": {},
                "formacao_e_idiomas": {},
                "cargo_atual": {}
            }
        }
        
        incomplete_vacancy = {
            "5186": {
                "informacoes_basicas": {"titulo_vaga": "Test Job"},
                "perfil_vaga": {},
                "beneficios": {}
            }
        }
        
        mock_model = Mock()
        mock_joblib_load.side_effect = [
            mock_model,
            {
                'ordinal_encoders': {
                    'idioma_encoders': {},
                    'educacao_encoder': None
                },
                'model_features': []
            }
        ]
        
        mock_w2v = Mock()
        mock_w2v.vector_size = 100
        mock_kv_load.return_value = mock_w2v
        
        pipeline = PredictionPipeline(
            model_path='model.joblib',
            artifacts_path='artifacts.joblib',
            w2v_model_path='w2v.txt'
        )
        
        # Mock das funções utilitárias
        with patch('src.models.predict.utils', create=True) as mock_utils:
            mock_utils.mapear_senioridade.return_value = pd.Series([0])
            mock_utils.padroniza_texto.return_value = None
            mock_utils.expand_vector.return_value = pd.DataFrame(np.random.rand(1, 1400))
            mock_utils.similaridade.return_value = None
            
            # Não deve gerar exceção, mesmo com dados incompletos
            result = pipeline._prepare_data(incomplete_candidate, incomplete_vacancy)
        
        assert isinstance(result, pd.DataFrame)

@pytest.mark.unit
class TestPredictionPipelineEdgeCases:
    
    @patch('src.models.predict.joblib.load')
    @patch('src.models.predict.KeyedVectors.load_word2vec_format')
    def test_pipeline_with_file_errors(self, mock_kv_load, mock_joblib_load):
        """Testa comportamento com erros de arquivo"""
        mock_joblib_load.side_effect = FileNotFoundError("Model file not found")
        
        with pytest.raises(FileNotFoundError):
            PredictionPipeline(
                model_path='nonexistent.joblib',
                artifacts_path='artifacts.joblib',
                w2v_model_path='w2v.txt'
            )

    @patch('src.models.predict.joblib.load')
    @patch('src.models.predict.KeyedVectors.load_word2vec_format')
    def test_pipeline_with_corrupted_artifacts(self, mock_kv_load, mock_joblib_load):
        """Testa comportamento com artefatos corrompidos"""
        mock_model = Mock()
        mock_joblib_load.side_effect = [
            mock_model,
            "not_a_dict"  # Artefatos corrompidos
        ]
        
        mock_w2v = Mock()
        mock_w2v.vector_size = 50
        mock_kv_load.return_value = mock_w2v
        
        # Deve lidar graciosamente com artefatos corrompidos
        pipeline = PredictionPipeline(
            model_path='model.joblib',
            artifacts_path='artifacts.joblib',
            w2v_model_path='w2v.txt'
        )
        
        # Deve usar valores padrão
        assert pipeline.ordinal_encoders == {}
        assert pipeline.model_features_order == []