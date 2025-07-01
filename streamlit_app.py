import os
import re
import streamlit as st
from docx import Document
import PyPDF2

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

# Funções utilitárias
@st.cache_data
def extract_docx(uploaded_docx):
    doc = Document(uploaded_docx)
    return "\n".join(p.text for p in doc.paragraphs)

@st.cache_data
def extract_pdf(uploaded_pdf):
    reader = PyPDF2.PdfReader(uploaded_pdf)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

# Stopwords e matching
STOPWORDS = set(['e','ou','com','para','dos','das','de','a','o','as','os','que','em','um','uma'])
def extract_keywords(req: str):
    return [w for w in re.findall(r"\w+", req.lower()) if len(w) > 3 and w not in STOPWORDS]

def match_requirement(req: str, resume: str):
    kws = extract_keywords(req)
    matched = [w for w in kws if w in resume]
    return (len(matched) >= len(kws) / 2 if kws else False, matched)

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

# CSS customizado para cores dos botões
st.markdown(
    """
    <style>
    div.stButton:nth-of-type(1) > button { background-color: green !important; color: white !important; }
    div.stButton:nth-of-type(2) > button { background-color: blue !important; color: white !important; }
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
                resume_text = extract_pdf(pdf).lower()
                matched_count = 0
                matched_details = []
                for req in requisitos:
                    ok, kws = match_requirement(req, resume_text)
                    if ok:
                        matched_count += 1
                        matched_details.append((req, kws))
                score = (matched_count / total_req * 100) if total_req else 0
                results.append({
                    'name': pdf.name,
                    'matched': matched_count,
                    'total': total_req,
                    'score': score,
                    'details': matched_details
                })
            top3 = sorted(results, key=lambda x: x['score'], reverse=True)[:3]

        # Mostrar cards
        cols = st.columns(3)
        for idx, cand in enumerate(top3):
            with cols[idx]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.subheader(f"{idx+1}. {cand['name']}")
                st.metric("Score", f"{cand['score']:.0f}%")
                st.write(f"Atendeu {cand['matched']}/{cand['total']} requisitos")
                exp = st.expander("Ver requisitos atendidos")
                for req, kws in cand['details']:
                    exp.write(f"- **{req}**")
                    exp.write(f"  - Keywords: {', '.join(kws)}")
                st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Use o menu lateral para enviar arquivos e iniciar a avaliação.")
