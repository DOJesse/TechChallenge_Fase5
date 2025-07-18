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
    
    def test_text_features_list_exists(self):
        """Testa se a lista de features de texto está definida"""
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
        """Testa document_vector com texto válido"""
        text = "python machine learning"
        result = document_vector(text, mock_word2vec_model, 50)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (50,)
        assert not np.all(result == 0)  # Não deve ser vetor zero para texto válido

    def test_document_vector_with_empty_text(self, mock_word2vec_model):
        """Testa document_vector com texto vazio"""
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
        """Testa funcionalidade básica do expand_vector"""
        df = pd.DataFrame({
            'titulo': ['python developer', 'data scientist'],
            'modalidade': ['remote work', 'on site'],
            'other_column': [1, 2]
        })
        features = ['titulo', 'modalidade']
        
        result = expand_vector(df, features, mock_word2vec_model, 5)
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (2, 10)  # 2 features × 5 dimensions
        
        # Verificar nomes das colunas
        expected_columns = []
        for feature in features:
            for i in range(5):
                expected_columns.append(f"{feature}_{i}")
        
        assert all(col in result.columns for col in expected_columns)

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
        
        result = expand_vector(df, features, mock_word2vec_model, 3)
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (3, 6)  # 3 linhas, 6 colunas (2 features × 3 dimensions)
        
        # Verificar se valores NaN resultaram em vetores zero
        assert not result.isna().any().any()  # Não deve haver NaN no resultado

    def test_expand_vector_preserves_index(self, mock_word2vec_model):
        """Testa se expand_vector preserva o índice original"""
        df = pd.DataFrame({
            'titulo': ['python developer', 'data scientist'],
            'modalidade': ['remote work', 'on site']
        }, index=[10, 20])
        features = ['titulo', 'modalidade']
        
        result = expand_vector(df, features, mock_word2vec_model, 3)
        
        assert list(result.index) == [10, 20]

    def test_expand_vector_single_feature(self, mock_word2vec_model):
        """Testa expand_vector com apenas uma feature"""
        df = pd.DataFrame({
            'titulo': ['python developer', 'data scientist', 'machine learning engineer']
        })
        features = ['titulo']
        
        result = expand_vector(df, features, mock_word2vec_model, 4)
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (3, 4)  # 3 linhas, 4 colunas
        assert all(col.startswith('titulo_') for col in result.columns)

    def test_expand_vector_different_num_features(self, mock_word2vec_model):
        """Testa expand_vector com diferentes números de features"""
        df = pd.DataFrame({
            'titulo': ['python developer'],
            'modalidade': ['remote work']
        })
        features = ['titulo', 'modalidade']
        
        # Testar com diferentes tamanhos de vetor
        for num_features in [1, 5, 10, 50]:
            result = expand_vector(df, features, mock_word2vec_model, num_features)
            expected_cols = len(features) * num_features
            assert result.shape == (1, expected_cols)

@pytest.mark.unit
class TestFeatureEngineeringIntegration:
    
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