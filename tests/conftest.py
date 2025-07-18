import pytest
import sys
import os
import numpy as np
from unittest.mock import Mock

# Adicionar o diretório raiz ao path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

@pytest.fixture
def mock_word2vec_model():
    """Mock do modelo Word2Vec para testes"""
    model = Mock()
    model.vector_size = 50
    model.key_to_index = {'python': 0, 'sql': 1, 'machine': 2, 'learning': 3}
    model.__getitem__ = lambda self, word: np.random.rand(50)
    return model

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