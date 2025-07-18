"""
Fixtures e dados de exemplo para testes
"""

import numpy as np
import pandas as pd

# Dados de candidato para testes
SAMPLE_CANDIDATE_COMPLETE = {
    "31001": {
        "infos_basicas": {
            "telefone_recado": "",
            "telefone": "(21) 98765-4321",
            "objetivo_profissional": "Desenvolver soluções inovadoras na área de tecnologia.",
            "data_criacao": "15-06-2023 10:30:00",
            "inserido_por": "Pedro Silva",
            "email": "ana.silva@email.com",
            "local": "Rio de Janeiro",
            "sabendo_de_nos_por": "Indicação",
            "data_atualizacao": "15-06-2023 10:30:00",
            "codigo_profissional": "31001",
            "nome": "Ana Silva"
        },
        "informacoes_pessoais": {
            "data_aceite": "2023-06-15",
            "nome": "Ana Silva",
            "cpf": "123.456.789-00",
            "fonte_indicacao": "Amigo",
            "email": "ana.silva@email.com",
            "email_secundario": "ana.contato@email.com",
            "data_nascimento": "1995-03-20",
            "telefone_celular": "(21) 98765-4321",
            "telefone_recado": "(21) 91234-5678",
            "sexo": "Feminino",
            "estado_civil": "Solteira",
            "pcd": "Não",
            "endereco": "Rua das Flores, 123, Centro, Rio de Janeiro - RJ",
            "skype": "ana.silva.skype",
            "url_linkedin": "https://www.linkedin.com/in/anasylva",
            "facebook": ""
        },
        "informacoes_profissionais": {
            "titulo_profissional": "Analista de Dados Sênior",
            "area_atuacao": "Tecnologia da Informação",
            "conhecimentos_tecnicos": "python, SQL, Power BI, Machine Learning, Git",
            "certificacoes": "Certificação React Developer",
            "outras_certificacoes": "Scrum Master",
            "remuneracao": "A combinar",
            "nivel_profissional": "Sênior"
        },
        "formacao_e_idiomas": {
            "nivel_academico": "Ensino Superior Completo",
            "instituicao_ensino_superior": "Universidade Paulista",
            "cursos": "Ciência da Computação",
            "ano_conclusao": "0",
            "nivel_ingles": "Fluente",
            "nivel_espanhol": "Intermediário",
            "outro_idioma": "Francês - Básico",
            "outro_curso": "Outro Curso:"
        },
        "cargo_atual": {
            "id_ibrati": "51819",
            "email_corporativo": "",
            "cargo_atual": "Analista de Dados II",
            "projeto_atual": "",
            "cliente": "DECISION IBM 15 07",
            "unidade": "Decision São Paulo",
            "data_admissao": "24-05-2018",
            "data_ultima_promocao": "24-05-2018",
            "nome_superior_imediato": "",
            "email_superior_imediato": ""
        },
        "cv_pt": "Desenvolvedora com 5 anos de experiência em criação de interfaces e análise de dados."
    }
}

# Dados de vaga para testes
SAMPLE_VACANCY_COMPLETE = {
    "5186": {
        "informacoes_basicas": {
            "data_requicisao": "10-07-2024",
            "limite_esperado_para_contratacao": "30-09-2024",
            "titulo_vaga": "Analista de Dados Sênior",
            "vaga_sap": "Sim",
            "cliente": "Global Analytics Inc.",
            "solicitante_cliente": "Dr. Lucas Martins",
            "empresa_divisao": "Insights Solutions Brasil",
            "requisitante": "Fernanda Costa",
            "analista_responsavel": "Sr. Gabriel Mendes",
            "tipo_contratacao": "PJ",
            "prazo_contratacao": "1 ano",
            "objetivo_vaga": "Fortalecer a equipe de dados com expertise em análise avançada.",
            "prioridade_vaga": "Alta",
            "origem_vaga": "Website Corporativo",
            "superior_imediato": "Gerente de Análise de Dados",
            "nome": "Sofia Almeida",
            "telefone": "(11) 99876-5432"
        },
        "perfil_vaga": {
            "pais": "Brasil",
            "estado": "São Paulo",
            "cidade": "São Paulo",
            "bairro": "Pinheiros",
            "regiao": "Zona Oeste",
            "local_trabalho": "Híbrido (3 dias presencial)",
            "vaga_especifica_para_pcd": "Não",
            "faixa_etaria": "De: 28 Até: 45",
            "horario_trabalho": "Comercial (09h - 18h)",
            "nivel profissional": "Sênior",
            "nivel_academico": "Pós graduação Completo",
            "nivel_ingles": "Fluente",
            "nivel_espanhol": "Intermediário",
            "outro_idioma": "Alemão - Básico",
            "areas_atuacao": "Tecnologia - Análise de Dados",
            "principais_atividades": "Desenvolver e implementar modelos de dados complexos.",
            "competencia_tecnicas_e_comportamentais": "Python, SQL, BI, trabalho em equipe",
            "demais_observacoes": "Ambiente dinâmico e inovador.",
            "viagens_requeridas": "Ocasionais para eventos.",
            "equipamentos_necessarios": "Notebook de alta performance."
        },
        "beneficios": {
            "valor_venda": "15000",
            "valor_compra_1": "R$ 12000",
            "valor_compra_2": "R$ 13000"
        }
    }
}

# Dados de candidato simplificado para testes rápidos
SAMPLE_CANDIDATE_MINIMAL = {
    "12345": {
        "infos_basicas": {
            "nome": "João Test",
            "objetivo_profissional": "Desenvolvedor Python"
        },
        "informacoes_pessoais": {
            "pcd": "Não"
        },
        "informacoes_profissionais": {
            "area_atuacao": "TI",
            "conhecimentos_tecnicos": "Python, SQL"
        },
        "formacao_e_idiomas": {
            "nivel_academico": "Superior Completo",
            "nivel_ingles": "Intermediário",
            "nivel_espanhol": "Básico"
        },
        "cargo_atual": {
            "cargo_atual": "Desenvolvedor Jr",
            "data_admissao": "01-01-2020"
        },
        "cv_pt": "Desenvolvedor Python junior"
    }
}

# Dados de vaga simplificada para testes rápidos
SAMPLE_VACANCY_MINIMAL = {
    "67890": {
        "informacoes_basicas": {
            "titulo_vaga": "Desenvolvedor Python",
            "vaga_sap": "Não",
            "tipo_contratacao": "CLT"
        },
        "perfil_vaga": {
            "vaga_especifica_para_pcd": "Não",
            "nivel profissional": "Junior",
            "nivel_academico": "Superior Completo",
            "nivel_ingles": "Básico",
            "nivel_espanhol": "Nenhum",
            "areas_atuacao": "Desenvolvimento",
            "principais_atividades": "Desenvolvimento Python",
            "competencia_tecnicas_e_comportamentais": "Python, Git"
        },
        "beneficios": {
            "valor_venda": "5000"
        }
    }
}

# DataFrame de exemplo para testes de feature engineering
SAMPLE_DATAFRAME = pd.DataFrame({
    'titulo': ['Python Developer', 'Data Scientist', 'ML Engineer'],
    'modalidade': ['Remote', 'Hybrid', 'Onsite'],
    'nome': ['João Silva', 'Maria Santos', 'Pedro Costa'],
    'comentario': ['Excelente', 'Muito bom', 'Adequado'],
    'area_atuacao_cand': ['TI', 'Dados', 'IA'],
    'conhecimentos_tecnicos_cand': ['Python, SQL', 'R, Python', 'TensorFlow, PyTorch']
})

# Features de texto comuns para testes
SAMPLE_TEXT_FEATURES = [
    'titulo', 'modalidade', 'nome', 'comentario',
    'area_atuacao_cand', 'conhecimentos_tecnicos_cand'
]

# Dados para testes de API
API_PREDICT_PAYLOAD = {
    'features': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
}

API_PREDICT_RAW_PAYLOAD = {
    'resume': {
        'text': 'Desenvolvedor Python com 3 anos de experiência'
    },
    'job': {
        'text': 'Vaga para desenvolvedor Python sênior'
    }
}

# Respostas esperadas da API
API_SUCCESS_RESPONSE = {
    'prediction': 1,
    'probabilities': [0.3, 0.7]
}

API_ERROR_RESPONSE = {
    'error': 'Invalid input data'
}

# Dados para testes do Streamlit
STREAMLIT_JOB_DESCRIPTION = """
Vaga: Desenvolvedor Python Sênior

Requisitos:
- Python avançado
• Machine Learning
* SQL e NoSQL
1. Git e GitHub
2) Docker e Kubernetes
3. Experiência com APIs REST
- Conhecimento em cloud (AWS/Azure)

Diferenciais:
• Conhecimento em React
• Experiência com microserviços
"""

STREAMLIT_RESUME_TEXT = """
João Silva
Desenvolvedor Python Sênior

Experiência:
- 5 anos com Python
- Machine Learning com scikit-learn
- Bancos SQL e MongoDB
- Git, GitHub, GitLab
- Docker, Kubernetes
- APIs REST com Flask e FastAPI
- AWS (EC2, S3, Lambda)

Formação:
- Ciência da Computação
- Pós-graduação em IA
"""

# Configurações de teste
TEST_CONFIG = {
    'api_timeout': 5,
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'supported_file_types': ['.pdf', '.docx'],
    'word2vec_dimensions': 50,
    'max_candidates': 100
}

# Métricas esperadas para validação
EXPECTED_METRICS = {
    'model_inference_duration_seconds': {'type': 'histogram', 'min': 0},
    'model_predictions_total': {'type': 'counter', 'min': 0},
    'model_prediction_error_absolute': {'type': 'gauge', 'min': 0, 'max': 1}
}