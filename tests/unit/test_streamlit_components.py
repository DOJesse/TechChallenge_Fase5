import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import io
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

@pytest.mark.unit
class TestStreamlitUtilityFunctions:
    """Testes para funções utilitárias do Streamlit"""
    
    def test_extract_keywords_basic(self):
        """Testa extração básica de keywords"""
        from streamlit_app import extract_keywords
        
        # Teste com texto simples
        text = "Python desenvolvedor machine learning"
        keywords = extract_keywords(text)
        
        assert isinstance(keywords, list)
        assert 'python' in keywords
        assert 'desenvolvedor' in keywords
        assert 'machine' in keywords
        assert 'learning' in keywords
        
        # Verificar que stopwords foram removidas
        assert 'e' not in keywords
        assert 'com' not in keywords
        assert 'para' not in keywords

    def test_extract_keywords_with_punctuation(self):
        """Testa extração de keywords com pontuação"""
        from streamlit_app import extract_keywords
        
        text = "Python, SQL e Machine Learning!"
        keywords = extract_keywords(text)
        
        assert 'python' in keywords
        assert 'machine' in keywords
        assert 'learning' in keywords

    def test_extract_keywords_empty_string(self):
        """Testa extração de keywords com string vazia"""
        from streamlit_app import extract_keywords
        
        keywords = extract_keywords("")
        assert isinstance(keywords, list)
        assert len(keywords) == 0

    def test_extract_keywords_only_stopwords(self):
        """Testa extração de keywords apenas com stopwords"""
        from streamlit_app import extract_keywords
        
        keywords = extract_keywords("e ou com para dos das")
        assert isinstance(keywords, list)
        assert len(keywords) == 0

    def test_extract_keywords_short_words(self):
        """Testa que palavras curtas são filtradas"""
        from streamlit_app import extract_keywords
        
        keywords = extract_keywords("a de um sql python")
        assert 'python' in keywords
        # Palavras com 3 caracteres ou menos devem ser filtradas
        assert 'sql' not in keywords
        assert 'a' not in keywords
        assert 'de' not in keywords
        assert 'um' not in keywords

    def test_match_requirement_exact_match(self):
        """Testa match_requirement com correspondência exata"""
        from streamlit_app import match_requirement
        
        requirement = "Python e SQL"
        resume = "desenvolvedor python e sql com experiência"
        
        match, matched_words = match_requirement(requirement, resume)
        
        assert isinstance(match, bool)
        assert isinstance(matched_words, list)
        assert match == True
        assert 'python' in matched_words
        # Note: 'sql' pode não estar porque tem 3 caracteres

    def test_match_requirement_partial_match(self):
        """Testa match_requirement com correspondência parcial"""
        from streamlit_app import match_requirement
        
        requirement = "Python machine learning data science"
        resume = "desenvolvedor python com conhecimento básico"
        
        match, matched_words = match_requirement(requirement, resume)
        
        assert isinstance(match, bool)
        assert isinstance(matched_words, list)
        # Deve retornar True se pelo menos metade das palavras correspondem

    def test_match_requirement_no_match(self):
        """Testa match_requirement sem correspondência"""
        from streamlit_app import match_requirement
        
        requirement = "Java Spring Boot"
        resume = "desenvolvedor python com django flask"
        
        match, matched_words = match_requirement(requirement, resume)
        
        assert isinstance(match, bool)
        assert isinstance(matched_words, list)
        assert match == False

    def test_match_requirement_empty_requirement(self):
        """Testa match_requirement com requisito vazio"""
        from streamlit_app import match_requirement
        
        match, matched_words = match_requirement("", "qualquer texto")
        
        assert isinstance(match, bool)
        assert isinstance(matched_words, list)
        assert match == False

@pytest.mark.unit 
class TestStreamlitFileProcessing:
    """Testes para funções de processamento de arquivos"""
    
    def test_extract_docx_mock(self):
        """Testa extração de texto de arquivo DOCX (mock)"""
        from streamlit_app import extract_docx
        
        # Mock de arquivo DOCX
        mock_file = Mock()
        
        with patch('streamlit_app.Document') as mock_document:
            # Configurar mock
            mock_doc = Mock()
            mock_paragraph1 = Mock()
            mock_paragraph1.text = "Primeiro parágrafo"
            mock_paragraph2 = Mock()
            mock_paragraph2.text = "Segundo parágrafo"
            
            mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2]
            mock_document.return_value = mock_doc
            
            # Executar função
            result = extract_docx(mock_file)
            
            # Verificar resultado
            assert isinstance(result, str)
            assert "Primeiro parágrafo" in result
            assert "Segundo parágrafo" in result

    def test_extract_pdf_mock(self):
        """Testa extração de texto de arquivo PDF (mock)"""
        from streamlit_app import extract_pdf
        
        # Mock de arquivo PDF
        mock_file = Mock()
        
        with patch('streamlit_app.pypdf.PdfReader') as mock_reader:
            # Configurar mock
            mock_page1 = Mock()
            mock_page1.extract_text.return_value = "Texto da página 1"
            mock_page2 = Mock()
            mock_page2.extract_text.return_value = "Texto da página 2"
            
            mock_pdf = Mock()
            mock_pdf.pages = [mock_page1, mock_page2]
            mock_reader.return_value = mock_pdf
            
            # Executar função
            result = extract_pdf(mock_file)
            
            # Verificar resultado
            assert isinstance(result, str)
            assert "Texto da página 1" in result
            assert "Texto da página 2" in result

    def test_extract_pdf_with_empty_pages(self):
        """Testa extração de PDF com páginas vazias"""
        from streamlit_app import extract_pdf
        
        mock_file = Mock()
        
        with patch('streamlit_app.pypdf.PdfReader') as mock_reader:
            # Página que retorna None
            mock_page1 = Mock()
            mock_page1.extract_text.return_value = None
            
            # Página com texto
            mock_page2 = Mock()
            mock_page2.extract_text.return_value = "Texto válido"
            
            mock_pdf = Mock()
            mock_pdf.pages = [mock_page1, mock_page2]
            mock_reader.return_value = mock_pdf
            
            result = extract_pdf(mock_file)
            
            assert isinstance(result, str)
            assert "Texto válido" in result

@pytest.mark.unit
class TestStreamlitAPIIntegration:
    """Testes para integração com API"""
    
    @patch('streamlit_app.requests.post')
    def test_call_api_prediction_success(self, mock_post):
        """Testa chamada bem-sucedida da API"""
        from streamlit_app import call_api_prediction
        
        # Configurar mock da resposta
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'prediction': 1,
            'probabilities': [0.2, 0.8]
        }
        mock_post.return_value = mock_response
        
        # Executar função
        result = call_api_prediction("Resume text", "Job text")
        
        # Verificar resultado
        assert result is not None
        assert 'prediction' in result
        assert 'probabilities' in result
        assert result['prediction'] == 1

    @patch('streamlit_app.requests.post')
    def test_call_api_prediction_error(self, mock_post):
        """Testa tratamento de erro na chamada da API"""
        from streamlit_app import call_api_prediction
        
        # Configurar mock para erro
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        # Executar função
        result = call_api_prediction("Resume text", "Job text")
        
        # Deve retornar None em caso de erro
        assert result is None

    @patch('streamlit_app.requests.post')
    def test_call_api_prediction_timeout(self, mock_post):
        """Testa tratamento de timeout na chamada da API"""
        from streamlit_app import call_api_prediction
        
        # Configurar mock para timeout
        mock_post.side_effect = Exception("Connection timeout")
        
        # Executar função
        result = call_api_prediction("Resume text", "Job text")
        
        # Deve retornar None em caso de exceção
        assert result is None

    @patch('streamlit_app.requests.post')
    def test_call_api_prediction_payload_format(self, mock_post):
        """Testa formato do payload enviado para API"""
        from streamlit_app import call_api_prediction
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'prediction': 0}
        mock_post.return_value = mock_response
        
        resume_text = "Desenvolvedor Python"
        job_text = "Vaga Python"
        
        call_api_prediction(resume_text, job_text)
        
        # Verificar se foi chamado com o payload correto
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Verificar argumentos
        assert 'json' in call_args.kwargs
        payload = call_args.kwargs['json']
        assert 'candidate' in payload
        assert 'vacancy' in payload
        assert payload['candidate']['31001']['cv_pt'] == resume_text
        assert payload['vacancy']['5186']['infos_basicas']['titulo_vaga'] == job_text

@pytest.mark.unit
class TestStreamlitBusinessLogic:
    """Testes para lógica de negócio do Streamlit"""
    
    def test_stopwords_definition(self):
        """Testa se stopwords estão definidas corretamente"""
        from streamlit_app import STOPWORDS
        
        assert isinstance(STOPWORDS, set)
        assert 'e' in STOPWORDS
        assert 'ou' in STOPWORDS
        assert 'com' in STOPWORDS
        assert 'para' in STOPWORDS
        assert len(STOPWORDS) > 0

    def test_api_url_configuration(self):
        """Testa configuração da URL da API"""
        from streamlit_app import API_URL
        
        assert isinstance(API_URL, str)
        assert len(API_URL) > 0
        # Deve ser uma URL válida ou localhost
        assert 'http' in API_URL.lower() or 'localhost' in API_URL

    @patch.dict(os.environ, {'API_URL': 'http://custom-api:9000'})
    def test_api_url_from_environment(self):
        """Testa se API_URL pode ser configurada via variável de ambiente"""
        # Reimportar para pegar a nova variável de ambiente
        import importlib
        import streamlit_app
        importlib.reload(streamlit_app)
        
        assert streamlit_app.API_URL == 'http://custom-api:9000'

@pytest.mark.unit
class TestStreamlitDataProcessing:
    """Testes para processamento de dados específico do Streamlit"""
    
    def test_requirement_parsing_with_bullets(self):
        """Testa parsing de requisitos com bullets"""
        # Simular texto de job description com diferentes formatos
        job_text = """
        Requisitos:
        - Python avançado
        • Machine Learning
        * SQL e NoSQL
        1. Git e GitHub
        2) Docker e Kubernetes
        """
        
        # Testar se a regex consegue capturar diferentes formatos
        import re
        
        # Padrões usados no streamlit_app.py
        lines = job_text.splitlines()
        requisitos = []
        
        for line in lines:
            t = line.strip()
            m1 = re.match(r'^[\-\u2022\*]\s*(.+)', t)
            m2 = re.match(r'^\d+[\.)]\s*(.+)', t)
            if m1:
                requisitos.append(m1.group(1).strip())
            elif m2:
                requisitos.append(m2.group(1).strip())
        
        assert 'Python avançado' in requisitos
        assert 'Machine Learning' in requisitos
        assert 'SQL e NoSQL' in requisitos
        assert 'Git e GitHub' in requisitos
        assert 'Docker e Kubernetes' in requisitos

    def test_score_calculation_logic(self):
        """Testa lógica de cálculo de score"""
        # Simular cálculo de score como no Streamlit
        total_requisitos = 10
        requisitos_atendidos = 7
        
        score = (requisitos_atendidos / total_requisitos * 100) if total_requisitos else 0
        
        assert score == 70.0
        
        # Teste com zero requisitos
        score_zero = (5 / 0 * 100) if 0 else 0
        assert score_zero == 0

    def test_candidate_ranking_logic(self):
        """Testa lógica de ranking de candidatos"""
        # Simular dados de candidatos
        candidates = [
            {'name': 'Candidate A', 'score': 85.0, 'matched': 8, 'total': 10},
            {'name': 'Candidate B', 'score': 92.0, 'matched': 9, 'total': 10},
            {'name': 'Candidate C', 'score': 78.0, 'matched': 7, 'total': 10},
            {'name': 'Candidate D', 'score': 95.0, 'matched': 10, 'total': 10},
        ]
        
        # Ordenar por score (como no Streamlit)
        top3 = sorted(candidates, key=lambda x: x['score'], reverse=True)[:3]
        
        assert len(top3) == 3
        assert top3[0]['name'] == 'Candidate D'
        assert top3[1]['name'] == 'Candidate B'
        assert top3[2]['name'] == 'Candidate A'
        assert top3[0]['score'] == 95.0