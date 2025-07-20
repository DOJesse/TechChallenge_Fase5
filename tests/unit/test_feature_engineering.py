import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.features.feature_engineering import (
    document_vector,
    expand_vector,
    text_features_list
)

@pytest.mark.unit
class TestFeatureEngineering:
    """Testes para as funções de engenharia de features."""
    
    def test_text_features_list_exists(self):
        """Verifica se a lista de features de texto está definida."""
        assert isinstance(text_features_list, list)
        assert len(text_features_list) > 0
        
        # Verificar algumas features específicas importantes
        expected_features = [
            'titulo', 'modalidade', 'nome', 'comentario',
            'area_atuacao_cand', 'conhecimentos_tecnicos_cand'
        ]
        for feature in expected_features:
            assert feature in text_features_list

    def test_document_vector_with_valid_text(self, mock_word2vec_model):
        """Testa se um vetor não nulo é retornado para um texto válido."""
        # Configura o mock para retornar um vetor não-zero para palavras conhecidas
        mock_word2vec_model.key_to_index = {'palavra': 0, 'teste': 1}
        mock_word2vec_model.__getitem__.side_effect = lambda x: np.ones(50) if x in ['palavra', 'teste'] else np.zeros(50)
        
        text = "palavra de teste"
        result = document_vector(text, mock_word2vec_model, 50)
        assert not np.all(result == 0)
        assert result.shape == (50,)

    def test_document_vector_with_empty_text(self, mock_word2vec_model):
        """Testa se um vetor de zeros é retornado para um texto vazio."""
        result = document_vector("", mock_word2vec_model, 50)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (50,)
        assert np.all(result == 0)

    def test_document_vector_with_whitespace_only(self, mock_word2vec_model):
        """Testa document_vector com apenas espaços em branco"""
        result = document_vector("   ", mock_word2vec_model, 50)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (50,)
        assert np.all(result == 0)

    def test_document_vector_with_none(self, mock_word2vec_model):
        """Testa document_vector com None"""
        result = document_vector(None, mock_word2vec_model, 50)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (50,)
        assert np.all(result == 0)

    def test_document_vector_with_unknown_words(self, mock_word2vec_model):
        """Testa document_vector com palavras não conhecidas"""
        text = "palavradesconhecida1 palavradesconhecida2"
        result = document_vector(text, mock_word2vec_model, 50)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (50,)
        assert np.all(result == 0)

    def test_document_vector_mixed_known_unknown_words(self, mock_word2vec_model):
        """Testa document_vector com mistura de palavras conhecidas e desconhecidas"""
        text = "python palavradesconhecida sql"
        result = document_vector(text, mock_word2vec_model, 50)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (50,)
        # Deve retornar a média das palavras conhecidas (python, sql)

    def test_expand_vector_basic_functionality(self, mock_word2vec_model):
        """Testa a funcionalidade básica de expand_vector."""
        data = {'text_column': ['this is a test', 'another test']}
        df = pd.DataFrame(data)
        features = ['text_column']
        result = expand_vector(df, features, mock_word2vec_model, 50)
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape[1] == 50
        assert all(f'text_column_{i}' in result.columns for i in range(50))

    def test_expand_vector_with_empty_dataframe(self, mock_word2vec_model):
        """Testa expand_vector com DataFrame vazio"""
        df = pd.DataFrame(columns=['titulo', 'modalidade'])
        features = ['titulo', 'modalidade']
        
        result = expand_vector(df, features, mock_word2vec_model, 5)
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (0, 10)  # 0 linhas, 10 colunas

    def test_expand_vector_with_nan_values(self, mock_word2vec_model):
        """Testa expand_vector com valores NaN"""
        df = pd.DataFrame({
            'titulo': ['python developer', np.nan, ''],
            'modalidade': [np.nan, 'remote work', 'on site']
        })
        features = ['titulo', 'modalidade']
        
        result = expand_vector(df, features, mock_word2vec_model, 50)
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (3, 100)  # 3 linhas, 100 colunas (2 features × 50 dimensions)
        
        # Verificar se valores NaN resultaram em vetores zero
        assert not result.isna().any().any()  # Não deve haver NaN no resultado

    def test_expand_vector_preserves_index(self, mock_word2vec_model):
        """Testa se o índice do DataFrame é preservado."""
        data = {'text_column': ['test one', 'test two']}
        df = pd.DataFrame(data, index=['A', 'B'])
        features = ['text_column']
        result = expand_vector(df, features, mock_word2vec_model, 50)
        
        pd.testing.assert_index_equal(df.index, result.index)

    def test_expand_vector_single_feature(self, mock_word2vec_model):
        """Testa a expansão com uma única característica de texto."""
        data = {'feature1': ['text one'], 'feature2': ['text two']}
        df = pd.DataFrame(data)
        features = ['feature1']
        result = expand_vector(df, features, mock_word2vec_model, 50)
        
        assert 'feature1_0' in result.columns
        assert 'feature2_0' not in result.columns

    @pytest.mark.parametrize("num_features", [1, 10, 50])
    def test_expand_vector_different_num_features(self, mock_word2vec_model, num_features):
        """Testa a expansão com diferentes números de features."""
        data = {'text_column': ['a sample text']}
        df = pd.DataFrame(data)
        features = ['text_column']
        
        # Ajusta o mock para o tamanho do vetor esperado
        mock_word2vec_model.vector_size = num_features
        mock_word2vec_model.wv.__getitem__.return_value = np.random.rand(num_features)
        
        result = expand_vector(df, features, mock_word2vec_model, num_features)
        
        assert result.shape[1] == num_features
        assert all(f'text_column_{i}' in result.columns for i in range(num_features))

class TestFeatureEngineeringIntegration:
    """Testes de integração para feature engineering."""
    
    def test_full_pipeline_simulation(self, mock_word2vec_model):
        """Testa uma simulação do pipeline completo de feature engineering"""
        # Simular dados como viriam do pipeline real
        df = pd.DataFrame({
            'titulo': ['Desenvolvedor Python Senior', 'Analista de Dados Junior'],
            'modalidade': ['Presencial', 'Remoto'],
            'nome': ['João Silva', 'Maria Santos'],
            'comentario': ['Excelente candidato', 'Boa comunicação'],
            'area_atuacao_cand': ['Tecnologia', 'Dados'],
            'conhecimentos_tecnicos_cand': ['Python, SQL, Git', 'R, Excel, Power BI']
        })
        
        # Usar algumas features da lista real
        features_to_test = [
            'titulo', 'modalidade', 'nome', 'comentario',
            'area_atuacao_cand', 'conhecimentos_tecnicos_cand'
        ]
        
        result = expand_vector(df, features_to_test, mock_word2vec_model, 10)
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (2, 60)  # 6 features × 10 dimensions
        
        # Verificar que todos os valores são numéricos
        assert result.dtypes.apply(lambda x: np.issubdtype(x, np.number)).all()
        
        # Verificar que não há valores infinitos ou NaN
        assert not result.isna().any().any()
        assert not np.isinf(result.values).any()