import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adicionar o diretório raiz ao Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

try:
    from src.models.utils import (
        padroniza_texto, 
        document_vector, 
        expand_vector,
        nivel_idioma,
        nivel_educacao,
        mapear_senioridade,
        similaridade,
        evaluation
    )
except ImportError:
    # Fallback para importação direta
    import importlib.util
    utils_path = os.path.join(project_root, 'src', 'models', 'utils.py')
    spec = importlib.util.spec_from_file_location("utils", utils_path)
    utils_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(utils_module)
    
    padroniza_texto = utils_module.padroniza_texto
    document_vector = utils_module.document_vector
    expand_vector = utils_module.expand_vector
    nivel_idioma = utils_module.nivel_idioma
    nivel_educacao = utils_module.nivel_educacao
    mapear_senioridade = utils_module.mapear_senioridade
    similaridade = utils_module.similaridade
    evaluation = utils_module.evaluation

@pytest.mark.unit
class TestPadronizaTexto:
    def test_padroniza_texto_normal_case(self):
        df = pd.DataFrame({
            'text1': ['  HELLO World!  ', 'Test@123'],
            'text2': ['Café  ', 'Açúcar#$']
        })
        features = ['text1', 'text2']
        
        padroniza_texto(df, features)
        
        assert df['text1'].iloc[0] == 'hello world'
        assert df['text1'].iloc[1] == 'test123'
        assert df['text2'].iloc[0] == 'cafe'
        assert df['text2'].iloc[1] == 'acucar'

    def test_padroniza_texto_empty_values(self):
        df = pd.DataFrame({
            'text1': ['', None, 'VALID'],
            'text2': [np.nan, '', 'test']
        })
        features = ['text1', 'text2']
        
        padroniza_texto(df, features)
        
        assert df['text1'].iloc[0] == ''
        assert df['text1'].iloc[2] == 'valid'

@pytest.mark.unit
class TestDocumentVector:
    def test_document_vector_valid_text(self, mock_word2vec_model):
        text = "python machine learning"
        result = document_vector(text, mock_word2vec_model, 50)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (50,)

    def test_document_vector_empty_text(self, mock_word2vec_model):
        result = document_vector("", mock_word2vec_model, 50)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (50,)
        assert np.all(result == 0)

    def test_document_vector_no_valid_words(self, mock_word2vec_model):
        text = "unknownword1 unknownword2"
        result = document_vector(text, mock_word2vec_model, 50)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (50,)
        assert np.all(result == 0)

    def test_document_vector_none_input(self, mock_word2vec_model):
        result = document_vector(None, mock_word2vec_model, 50)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (50,)
        assert np.all(result == 0)

@pytest.mark.unit
class TestExpandVector:
    def test_expand_vector_normal_case(self):
        """Testa a funcionalidade básica de expandir um vetor em colunas."""
        # Mock do modelo Word2Vec
        mock_model = MagicMock()
        mock_model.key_to_index = {'test': 0, 'word': 1}
        mock_model.__getitem__.side_effect = lambda x: np.array([1, 2, 3]) if x in ['test', 'word'] else np.zeros(3)
        
        df = pd.DataFrame({'text_feature': ['test word', 'another test']})
        result = expand_vector(df, ['text_feature'], mock_model, 3)
        
        # Verifica se as colunas esperadas foram criadas
        expected_columns = ['text_feature_emb_0', 'text_feature_emb_1', 'text_feature_emb_2']
        assert all(col in result.columns for col in expected_columns)
        assert len(result) == 2  # Duas linhas no resultado

class TestNivelIdioma:
    def test_nivel_idioma_encoding(self):
        df = pd.DataFrame({
            'nivel_ingles': ['Básico', 'Fluente', None, ''],
            'nivel_espanhol': ['Intermediário', 'Técnico', 'Avançado', 'Nenhum']
        })
        features = ['nivel_ingles', 'nivel_espanhol']
        
        encoders = nivel_idioma(df, features)
        
        assert 'nivel_ingles' in encoders
        assert 'nivel_espanhol' in encoders
        assert 'nivel_ingles_encoded' in df.columns
        assert 'nivel_espanhol_encoded' in df.columns
        
        # Verificar se os valores foram encodados corretamente
        assert df['nivel_ingles_encoded'].iloc[1] == 4  # Fluente = 4
        assert df['nivel_espanhol_encoded'].iloc[1] == 3  # Técnico->Avançado = 3

@pytest.mark.unit
class TestNivelEducacao:
    def test_nivel_educacao_encoding(self):
        df = pd.DataFrame({
            'nivel_academico': [
                'ensino superior completo',
                'pos graduacao cursando',
                'mestrado completo',
                '',
                'nan'
            ]
        })
        
        encoder = nivel_educacao(df)
        
        assert 'nivel_academico_encoded' in df.columns
        assert encoder is not None
        
        # Verificar se "cursando" foi substituído por "incompleto"
        assert any('incompleto' in str(val) for val in df['nivel_academico'])

@pytest.mark.unit
class TestMapearSenioridade:
    def test_mapear_senioridade_various_levels(self):
        series = pd.Series([
            'Desenvolvedor Júnior',
            'Analista Sênior',
            'Gerente de Projetos',
            'Especialista em Dados',
            'Desenvolvedor Pleno',
            'Trainee',
            'Cargo Desconhecido'
        ])
        
        result = mapear_senioridade(series)
        
        assert result.iloc[0] == 1  # Júnior
        assert result.iloc[1] == 3  # Sênior
        assert result.iloc[2] == 5  # Gerente
        assert result.iloc[3] == 4  # Especialista
        assert result.iloc[4] == 2  # Pleno
        assert result.iloc[5] == 0  # Trainee
        assert result.iloc[6] == -1  # Desconhecido

@pytest.mark.unit
class TestSimilaridade:
    def test_similaridade_calculation(self):
        # Criar um DataFrame com embeddings simulados
        df = pd.DataFrame({
            'feature1_emb_0': [1.0, 0.5],
            'feature1_emb_1': [0.0, 0.5],
            'feature2_emb_0': [1.0, 1.0],
            'feature2_emb_1': [0.0, 0.0]
        })
        
        similaridade(df, 'feature1_emb', 'feature2_emb', 'similarity')
        
        assert 'similarity' in df.columns
        assert len(df['similarity']) == 2
        # Valores devem estar entre -1 e 1 para similaridade cosseno
        assert all(-1 <= val <= 1 for val in df['similarity'])

@pytest.mark.unit
class TestEvaluation:
    @patch('src.models.utils.mean_squared_error')
    @patch('src.models.utils.mean_absolute_error')
    @patch('builtins.print')
    def test_evaluation_prints_metrics(self, mock_print, mock_mae, mock_mse):
        mock_model = Mock()
        mock_model.fit.return_value = None
        mock_model.predict.return_value = np.array([0.5, 0.6, 0.7])
        
        mock_mse.return_value = 0.1
        mock_mae.return_value = 0.2
        
        x_train = np.array([[1, 2], [3, 4]])
        y_train = np.array([0.5, 0.6])
        x_test = np.array([[5, 6]])
        y_test = np.array([0.7])
        
        evaluation(mock_model, x_train, y_train, x_test, y_test)
        
        mock_model.fit.assert_called_once_with(x_train, y_train)
        mock_model.predict.assert_called_once_with(x_test)
        mock_mse.assert_called_once()
        mock_mae.assert_called_once()
        mock_print.assert_called_once()