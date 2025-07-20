import os
import re
import streamlit as st
import requests
import json
from docx import Document
import pypdf

# Página e estilos
st.set_page_config(page_title="Recruitment Match", layout="wide")
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f2f6;
        color: #333;
    }
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 20px;
    }
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px;
    }
    </style>
    """, unsafe_allow_html=True
)
st.markdown("<div class='title'>Recruitment Match - Avaliação por Requisitos</div>", unsafe_allow_html=True)

# Estado inicial
if 'avaliar' not in st.session_state:
    st.session_state.avaliar = False
if 'reset' not in st.session_state:
    st.session_state.reset = 0

# Chaves dinâmicas para limpar uploads ao reiniciar
job_key = f"job_file_{st.session_state.reset}"
cand_key = f"candidate_files_{st.session_state.reset}"

def get_classification(score):
    """Retorna a classificação baseada no score"""
    if score >= 80:
        return "Ótimo", "#28a745"  # Verde
    elif score >= 60:
        return "Bom", "#007bff"     # Azul
    elif score >= 40:
        return "Médio", "#ffc107"   # Amarelo
    else:
        return "Ruim", "#dc3545"    # Vermelho

# Funções utilitárias
@st.cache_data
def extract_docx(uploaded_docx):
    doc = Document(uploaded_docx)
    return "\n".join(p.text for p in doc.paragraphs)

@st.cache_data
def extract_pdf(uploaded_pdf):
    reader = pypdf.PdfReader(uploaded_pdf)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

# API Configuration
API_URL = os.getenv("API_URL", "http://api:5000")

# Stopwords e matching
STOPWORDS = set(['e','ou','com','para','dos','das','de','a','o','as','os','que','em','um','uma'])
def extract_keywords(req: str):
    return [w for w in re.findall(r"\w+", req.lower()) if len(w) > 3 and w not in STOPWORDS]

def match_requirement(req: str, resume: str):
    kws = extract_keywords(req)
    matched = [w for w in kws if w in resume]
    return (len(matched) >= len(kws) / 2 if kws else False, matched)

def call_api_prediction(resume_text: str, job_text: str):
    """Chama a API Flask para gerar predição e métricas"""
    try:
        payload = {
            "candidate": {"31001": {"cv_pt": resume_text}},
            "vacancy": {"5186": {"infos_basicas": {"titulo_vaga": job_text}}}
        }
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro na API: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erro ao conectar com API: {e}")
        return None

# Sidebar Inputs
st.sidebar.header("Configuração")
job_file = st.sidebar.file_uploader("Descrição da Vaga (.docx)", type=["docx"], key=job_key)
candidate_files = st.sidebar.file_uploader(
    "Currículos (.pdf)", type=["pdf"], accept_multiple_files=True, key=cand_key
)

# Callbacks de botões
def start():
    st.session_state.avaliar = True

def reset():
    st.session_state.avaliar = False
    st.session_state.reset += 1

# Botões de ação
st.sidebar.button("Avaliar currículos", on_click=start)
st.sidebar.button("Fazer nova avaliação", on_click=reset)

# CSS customizado para cores dos botões e Score
st.markdown(
    """
    <style>
    div.stButton:nth-of-type(1) > button { background-color: green !important; color: white !important; }
    div.stButton:nth-of-type(2) > button { background-color: blue !important; color: white !important; }
    /* Score metric value e label em preto */
    div[data-testid="stMetric"] > div > div:nth-child(1) {
        color: #111 !important;
    }
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] > div > div:nth-child(2) {
        color: #111 !important;
    }
    </style>
    """, unsafe_allow_html=True
)

# Lógica de avaliação
if st.session_state.avaliar:
    if not job_file or not candidate_files:
        st.warning("Envie todos os arquivos no sidebar antes de avaliar.")
    else:
        with st.spinner("Analisando..."):
            job_text = extract_docx(job_file)
            requisitos = []
            for line in job_text.splitlines():
                t = line.strip()
                m1 = re.match(r'^[\-\u2022\*]\s*(.+)', t)
                m2 = re.match(r'^\d+[\.)]\s*(.+)', t)
                if m1:
                    requisitos.append(m1.group(1).strip())
                elif m2:
                    requisitos.append(m2.group(1).strip())
            total_req = len(requisitos)

            results = []
            for pdf in candidate_files:
                resume_text = extract_pdf(pdf)
                if not resume_text.strip() or not job_text.strip():
                    st.warning(f"Arquivo '{pdf.name}' ou descrição da vaga está vazia. Não foi possível avaliar este currículo.")
                    continue
                # Chama a API Flask para gerar métricas de inferência
                api_result = call_api_prediction(resume_text, job_text)
                # Continua com lógica original para interface
                resume_text_lower = resume_text.lower()
                matched_count = 0
                matched_details = []
                for req in requisitos:
                    ok, kws = match_requirement(req, resume_text_lower)
                    if ok:
                        matched_count += 1
                        matched_details.append((req, kws))
                score = (matched_count / total_req * 100) if total_req else 0
                result_data = {
                    'name': pdf.name,
                    'matched': matched_count,
                    'total': total_req,
                    'score': score,
                    'details': matched_details
                }
                # Adiciona predição da API se disponível
                if api_result:
                    result_data['api_prediction'] = api_result.get('prediction', 'N/A')
                    result_data['api_probabilities'] = api_result.get('probabilities', [])
                results.append(result_data)
            
            # Ordena todos os resultados por score (maior para menor)
            all_results = sorted(results, key=lambda x: x['score'], reverse=True)

        # Mostrar todos os resultados
        st.subheader(f"Resultados da Avaliação - {len(all_results)} candidato(s)")
        
        for idx, cand in enumerate(all_results):
            classification, color = get_classification(cand['score'])
            
            # Criar card para cada candidato
            st.markdown(f"""
                <div style='background-color: #ffffff; padding: 20px; border-radius: 10px; 
                           box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 15px 0;
                           border-left: 5px solid {color};'>
                    <h3 style='color: #2c3e50; margin-bottom: 10px;'>
                        {idx+1}. {cand['name']}
                    </h3>
                    <div style='display: flex; align-items: center; gap: 20px; margin-bottom: 15px;'>
                        <div style='background-color: {color}; color: white; padding: 8px 16px; 
                                   border-radius: 20px; font-weight: bold;'>
                            {classification}
                        </div>
                        <div style='font-size: 24px; font-weight: bold; color: {color};'>
                            {cand['score']:.0f}%
                        </div>
                        <div style='color: #666;'>
                            Atendeu {cand['matched']}/{cand['total']} requisitos
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Expandir para ver detalhes dos requisitos
            with st.expander(f"Ver requisitos atendidos - {cand['name']}"):
                if cand['details']:
                    for req, kws in cand['details']:
                        st.write(f"✅ **{req}**")
                        st.write(f"   📝 Keywords encontradas: {', '.join(kws)}")
                        st.write("")
                else:
                    st.write("❌ Nenhum requisito foi atendido completamente.")
else:
    st.markdown("""
        <div style='color:#0a2342; font-size:1.1em; font-weight:600; margin-top:2em;'>
            Use o menu lateral para enviar arquivos e iniciar a avaliação.
        </div>
    """, unsafe_allow_html=True)
