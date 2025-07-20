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

from tests.fixtures.sample_data import (
    SAMPLE_CANDIDATE_COMPLETE as VALID_CANDIDATE_DATA,
    SAMPLE_VACANCY_COMPLETE as VALID_VACANCY_DATA,
    INCOMPLETE_CANDIDATE_DATA,
    INCOMPLETE_VACANCY_DATA
)
from tests.fixtures.sample_data import sample_candidate_data, sample_vacancy_data

@pytest.mark.unit
class TestPredictionPipeline:
    """Testes para o pipeline de predição."""

    def test_pipeline_initialization(self, mock_prediction_pipeline, mock_word2vec_model):
        """Testa a inicialização correta do pipeline."""
        pipeline = mock_prediction_pipeline
        mock_w2v = mock_word2vec_model
        
        assert pipeline.model is not None
        assert pipeline.model_features_order is not None

    @patch('shap.save_html')
    @patch('shap.force_plot')
    @patch('shap.TreeExplainer')
    @patch('gensim.models.KeyedVectors.load_word2vec_format')
    @patch('src.models.predict.joblib.load')
    def test_predict_method(self, mock_joblib_load, mock_w2v_load, mock_shap, mock_force_plot, mock_save_html):
        """Testa o método de predição individualmente com mocks."""
        # Mocks para os artefatos carregados
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([0.85])
        mock_preprocessor = {'model_features_order': ['feature1', 'feature2']}
        mock_joblib_load.side_effect = [mock_model, mock_preprocessor]
        mock_w2v_load.return_value = MagicMock()
        
        # Mock do SHAP
        mock_explainer = MagicMock()
        mock_explainer.shap_values.return_value = [0.1, 0.2]
        mock_explainer.expected_value = 0.5
        mock_shap.return_value = mock_explainer
        mock_force_plot.return_value = MagicMock()
        mock_save_html.return_value = None

        # Criar pipeline com argumentos necessários
        pipeline = PredictionPipeline(
            model_path='mock/path/model.joblib',
            artifacts_path='mock/path/artifacts.joblib', 
            w2v_model_path='mock/path/word2vec.bin'
        )
        # Simula um DataFrame processado
        processed_df = pd.DataFrame([[1, 2]], columns=['feature1', 'feature2'])

        # Mock para _prepare_data para isolar o teste no método predict
        pipeline._prepare_data = MagicMock(return_value=processed_df)

        candidate_data = {"id": "c1"}
        vacancy_data = {"id": "v1"}
        prediction, shap_values = pipeline.predict(candidate_data, vacancy_data)

        pipeline._prepare_data.assert_called_once_with(candidate_data, vacancy_data)
        mock_model.predict.assert_called_once()
        assert prediction == 0.85

    @patch('shap.save_html')
    @patch('shap.force_plot')
    @patch('shap.TreeExplainer')
    @patch('gensim.models.KeyedVectors.load_word2vec_format')
    @patch('src.models.predict.joblib.load')
    def test_predict_flow(self, mock_joblib_load, mock_w2v_load, mock_shap, mock_force_plot, mock_save_html):
        """Testa o fluxo de predição, garantindo que _prepare_data seja chamado."""
        # Mocks para os artefatos carregados
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([0.9])
        mock_preprocessor = {'model_features_order': ['feature1', 'feature2']}
        mock_joblib_load.side_effect = [mock_model, mock_preprocessor]
        mock_w2v_load.return_value = MagicMock()
        
        # Mock do SHAP
        mock_explainer = MagicMock()
        mock_explainer.shap_values.return_value = [0.1, 0.2]
        mock_explainer.expected_value = 0.5
        mock_shap.return_value = mock_explainer
        mock_force_plot.return_value = MagicMock()
        mock_save_html.return_value = None
        
        # Criar pipeline com argumentos necessários
        pipeline = PredictionPipeline(
            model_path='mock/path/model.joblib',
            artifacts_path='mock/path/artifacts.joblib',
            w2v_model_path='mock/path/word2vec.bin'
        )
        
        # Mock para _prepare_data
        with patch.object(pipeline, '_prepare_data') as mock_prepare_data:
            mock_prepare_data.return_value = pd.DataFrame([[1, 2]], columns=['feature1', 'feature2'])
            
            candidate_data = sample_candidate_data()
            vacancy_data = sample_vacancy_data()

            # Chama o método predict
            pipeline.predict(candidate_data, vacancy_data)

            # Verifica se _prepare_data foi chamado
            mock_prepare_data.assert_called_once_with(candidate_data, vacancy_data)