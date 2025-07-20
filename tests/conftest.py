import pytest
import sys
import os
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock

# Adicionar o diretório raiz ao path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

@pytest.fixture
def mock_word2vec_model():
    """Fixture para mock do modelo Word2Vec."""
    mock_model = MagicMock()
    mock_model.vector_size = 50
    
    # Configura o mock para o acesso `wv[palavra]`
    wv_mock = MagicMock()
    wv_mock.__getitem__.return_value = np.random.rand(50)
    mock_model.wv = wv_mock
    
    # Mock para document_vector
    mock_model.get_document_vector = MagicMock(return_value=np.random.rand(50))
    
    return mock_model

@pytest.fixture
def mock_prediction_pipeline(mock_word2vec_model):
    """Fixture para mock da PredictionPipeline."""
    with patch('src.models.predict.PredictionPipeline') as mock_pipeline:
        mock_instance = mock_pipeline.return_value
        mock_instance.model_w2v = mock_word2vec_model
        mock_instance.predict.return_value = (0.85, [0.1, 0.2, 0.3])  # Retorno mais realista
        
        # Mock de _prepare_data para retornar um DataFrame com colunas esperadas
        prepared_data = pd.DataFrame({
            'idade': [30],
            'anos_experiencia': [5],
            'similaridade_descricao': [0.8],
            'similaridade_requisitos': [0.9],
            'similaridade_experiencia': [0.7],
            'senioridade_cand': [2],
            'senioridade_vaga': [3],
            'nivel_educacao_cand': [4],
            'nivel_idioma_cand': [3]
        })
        # Adiciona colunas de embedding mockadas
        for i in range(50):
            prepared_data[f'embedding_{i}'] = np.random.rand()

        mock_instance._prepare_data.return_value = prepared_data
        yield mock_instance

@pytest.fixture
def sample_candidate_data():
    """Dados de candidato para testes"""
    return {
        "31001": {
            "infos_basicas": {
                "telefone": "(21) 98765-4321",
                "objetivo_profissional": "Desenvolver soluções inovadoras na área de tecnologia.",
                "email": "ana.silva@email.com",
                "nome": "Ana Silva"
            },
            "informacoes_pessoais": {
                "pcd": "Não"
            },
            "informacoes_profissionais": {
                "area_atuacao": "Tecnologia da Informação",
                "conhecimentos_tecnicos": "python, SQL, Power BI"
            },
            "formacao_e_idiomas": {
                "nivel_academico": "Ensino Superior Completo",
                "nivel_ingles": "Fluente",
                "nivel_espanhol": "Intermediário"
            },
            "cargo_atual": {
                "cargo_atual": "Analista de Dados II",
                "data_admissao": "24-05-2018"
            },
            "cv_pt": "Desenvolvedora com experiência em Python e SQL"
        }
    }

@pytest.fixture
def sample_vacancy_data():
    """Dados de vaga para testes"""
    return {
        "5186": {
            "informacoes_basicas": {
                "titulo_vaga": "Analista de Dados Sênior",
                "vaga_sap": "Sim",
                "cliente": "Global Analytics Inc.",
                "tipo_contratacao": "PJ"
            },
            "perfil_vaga": {
                "vaga_especifica_para_pcd": "Não",
                "nivel profissional": "Sênior",
                "nivel_academico": "Pós graduação Completo",
                "nivel_ingles": "Fluente",
                "nivel_espanhol": "Intermediário",
                "areas_atuacao": "Tecnologia - Análise de Dados",
                "principais_atividades": "Desenvolver modelos de dados",
                "competencia_tecnicas_e_comportamentais": "Python, SQL, BI"
            },
            "beneficios": {
                "valor_venda": "15000"
            }
        }
    }

@pytest.fixture
def sample_text_features():
    """Features de texto para testes"""
    return ['titulo', 'modalidade', 'nome', 'comentario']