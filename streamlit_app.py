import os
import streamlit as st
from docx import Document
import PyPDF2
import requests

# Configurações da página
st.set_page_config(page_title="Recruitment Match", layout="wide")
st.title("Recruitment Match - Top 3 Candidatos")

# URL da API (pode ser override por variável de ambiente)
API_URL = os.getenv("API_URL", "http://localhost:8080")

# Sidebar para parâmetros adicionais
st.sidebar.header("Parâmetros adicionais")
anos_exp = st.sidebar.number_input("Anos de Experiência", min_value=0, max_value=50, value=3)
nivel_educacao = st.sidebar.selectbox(
    "Nível de Educação",
    ["Fundamental", "Médio", "Técnico", "Superior", "Pós-graduação", "Mestrado", "Doutorado"]
)
nivel_idioma = st.sidebar.selectbox(
    "Nível de Inglês",
    ["Básico", "Intermediário", "Avançado", "Fluente", "Nativo"]
)
# Funções de extração
@st.cache_data
def extract_job_text(uploaded_docx):
    doc = Document(uploaded_docx)
    return "\n".join([p.text for p in doc.paragraphs])

@st.cache_data
def extract_resume_text(uploaded_pdf):
    reader = PyPDF2.PdfReader(uploaded_pdf)
    texts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            texts.append(page_text)
    return "\n".join(texts)

# Upload de arquivos
job_file = st.file_uploader("Descrição da Vaga (.docx)", type=["docx"])
candidate_files = st.file_uploader(
    "Currículos (.pdf) - múltiplos",
    type=["pdf"],
    accept_multiple_files=True
)

if job_file and candidate_files:
    with st.spinner("Processando documentos e chamando a API..."):
        job_text = extract_job_text(job_file)
        results = []
        for pdf in candidate_files:
            resume_text = extract_resume_text(pdf)
            payload = {
                "resume": {
                    "cv_pt_cand": resume_text,
                    "tempo_exp": anos_exp,
                    "nivel_educacao": nivel_educacao,
                    "nivel_idioma": nivel_idioma
                },
                "job": {"principais_atividades_vaga": job_text}
            }
            try:
                response = requests.post(f"{API_URL}/predict_raw", json=payload)
                response.raise_for_status()
                data = response.json()
                score = data.get("probabilities", [None, None])[1]
                results.append({"candidate": pdf.name, "score": score})
            except Exception as e:
                results.append({"candidate": pdf.name, "error": str(e)})
        scored = [r for r in results if r.get("score") is not None]
        top3 = sorted(scored, key=lambda x: x["score"], reverse=True)[:3]
    if top3:
        st.header("Top 3 Candidatos")
        for i, cand in enumerate(top3, 1):
            st.subheader(f"{i}. {cand['candidate']}")
            st.progress(cand["score"])
            st.write(f"Score de adequação: {cand['score']:.2%}")
    else:
        st.warning("Nenhum candidato válido foi encontrado.")
    errors = [r for r in results if r.get("error")]
    if errors:
        st.error("Erros ao processar alguns currículos:")
        for err in errors:
            st.write(f"- {err['candidate']}: {err['error']}")
else:
    st.info("Carregue a descrição da vaga e pelo menos um currículo para iniciar a análise.")
