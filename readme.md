# Datathon Machine Learning Engineering

Este repositório contém a solução do Datathon de Machine Learning Engineering para otimizar o processo de "match" entre candidatos e vagas da Decision. O aplicativo utiliza processamento de linguagem natural, engenharia de atributos e modelos de machine learning para sugerir o melhor encaixe entre perfis e oportunidades.

---

## 1. Estrutura do Projeto

```text
TechChallenge_Fase5/
├── src/
│   ├── app/
│   │   ├── main.py                # Script principal (Streamlit)
│   │   └── requirements.txt       # Dependências do app
│   ├── features/
│   │   └── feature_engineering.py # Engenharia de atributos
│   ├── models/
│   │   ├── pipeline.joblib        # Pipeline treinado
│   │   ├── word2vec_model.kv      # Modelo Word2Vec
│   │   └── artifacts/             # Artefatos do modelo
│   └── data/
│       └── raw/                   # Dados brutos (JSON)
│           ├── applicants.json
│           ├── prospects.json
│           └── vagas.json
├── src/word2vec/
│   └── cbow_s50.txt               # Embeddings Word2Vec (baixar manualmente)
├── docker/
│   ├── Dockerfile.api             # Dockerfile para API
│   ├── Dockerfile.streamlit       # Dockerfile para Streamlit
│   └── docker-compose.yaml        # Orquestração
├── streamlit_app.py               # App principal (Streamlit)
├── readme.md                      # Esta documentação
```

---

## 2. Dados

Os dados de treinamento em JSON **não são replicados neste repositório** devido ao tamanho dos arquivos. Para executar o projeto, é necessário baixá-los manualmente pelo link:

[Google Drive - Dados de Treinamento](https://drive.google.com/drive/folders/1f3jtTRyOK-PBvND3JTPTAxHpnSrH7rFR?usp=sharing)

Após o download, coloque os arquivos `applicants.json`, `prospects.json` e `vagas.json` na pasta:

```
TechChallenge_Fase5/src/data/raw/
```

* **vagas.json**: informações sobre vagas
* **prospects.json**: lista de prospecções por vaga
* **applicants.json**: perfis completos dos candidatos

O arquivo de embeddings Word2Vec `cbow_s50.txt` **também não está no repositório** devido ao tamanho. Baixe pelo link:

[cbow_s50.txt - Word2Vec (zip)](http://143.107.183.175:22980/download.php?file=embeddings/word2vec/cbow_s50.zip)

Após extrair, salve o arquivo `cbow_s50.txt` em:

```
TechChallenge_Fase5/src/word2vec/
```

* **cbow_s50.txt**: arquivo de embeddings Word2Vec utilizado no projeto

---

## 3. Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/DOJesse/TechChallenge_Fase5
   cd TechChallenge_Fase5
   ```
2. Crie e ative um ambiente virtual (venv):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Instale as dependências:

   ```bash
   pip install -r src/app/requirements.txt
   ```

4. Execute o aplicativo via Docker:

   ```bash
   docker-compose -f docker-compose.yaml up --build
   ```

   O app estará disponível em `localhost:8502`.

---

## 4. Testes Unitários

Este projeto inclui uma suite completa de testes unitários e de integração para garantir a qualidade e confiabilidade do código.

### Estrutura dos Testes

```
tests/
├── unit/                          # Testes unitários
│   ├── test_utils.py             # Funções utilitárias (✅ Funcional)
│   ├── test_feature_engineering.py # Feature engineering (✅ Funcional)
│   ├── test_predict.py           # Pipeline de predição (✅ Funcional)
│   ├── test_api.py               # API Flask (✅ Funcional)
│   └── test_streamlit_components.py # Componentes Streamlit (✅ Funcional)
├── integration/                   # Testes de integração
│   └── test_api_integration.py   # Testes end-to-end (✅ Funcional)
├── fixtures/                      # Dados de teste
│   └── sample_data.py            # Dados de exemplo (✅ Funcional)
├── conftest.py                   # Configurações pytest (✅ Funcional)
└── run_tests.py                  # Script automatizado de execução
```

### 🚀 Execução Rápida (Recomendado)

```bash
# Script automatizado com verificações de dependências
python3 run_tests.py

# Resultado esperado:
# 🎉 TODOS OS TESTES BÁSICOS PASSARAM!
# ✅ Sucessos: 5/5
```

### Pré-requisitos para Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-mock

# As dependências principais já estão no requirements.txt
pip install -r src/app/requirements.txt
```

### Executar Todos os Testes

```bash
# A partir da raiz do projeto
python3 -m pytest tests/

# Com detalhes
python3 -m pytest tests/ -v
```

### Executar Testes Específicos

```bash
# Por categoria
python3 -m pytest tests/unit/ -v                    # Testes unitários
python3 -m pytest tests/integration/ -v             # Testes de integração

# Por componente específico
python3 -m pytest tests/unit/test_utils.py -v                     # Funções utilitárias
python3 -m pytest tests/unit/test_feature_engineering.py -v       # Feature engineering
python3 -m pytest tests/unit/test_predict.py -v                   # Pipeline ML
python3 -m pytest tests/unit/test_api.py -v                       # API Flask
python3 -m pytest tests/unit/test_streamlit_components.py -v      # Streamlit

# Por marcadores (tags)
python3 -m pytest -m unit           # Todos os testes unitários
python3 -m pytest -m api            # Testes específicos da API
python3 -m pytest -m integration    # Testes de integração
```

### Cobertura dos Testes

Os testes cobrem:
- ✅ **72 testes** em 6 arquivos funcionais
- ✅ Funções de processamento de texto e feature engineering
- ✅ Pipeline completo de predição ML
- ✅ Endpoints da API Flask com métricas Prometheus
- ✅ Componentes do Streamlit
- ✅ Tratamento de erros e casos edge
- ✅ Testes de integração end-to-end

### Troubleshooting

```bash
# Problemas de importação - usar python3 explicitamente
python3 -m pytest tests/

# Debug de teste específico
python3 -m pytest tests/unit/test_utils.py::TestPadronizaTexto::test_padroniza_texto_normal_case -v -s

# Parar na primeira falha
python3 -m pytest tests/ -x
```

---

## 5. Como o aplicativo funciona

O aplicativo Streamlit permite:
- Executar o modelo de machine learning para sugerir o melhor match entre candidatos e vagas, considerando informações do currículo, experiências, habilidades e requisitos das vagas.
- Visualizar a lista de candidatos mais aderentes a cada vaga, com scores de compatibilidade.

### Interpretação dos resultados
- **Ranking de candidatos**: Os candidatos são ordenados do mais ao menos compatível para cada vaga.
- **Detalhes do match**: O app pode exibir os principais fatores que contribuíram para o score (ex: experiência, formação, habilidades técnicas).

Esses resultados auxiliam o RH a priorizar candidatos e entender os motivos do match sugerido pelo modelo.

---

## 6. Observações

- Certifique-se de que os dados estejam em `src/data/raw/`.
- O arquivo de embeddings deve estar em `src/word2vec/`.
- Para executar scripts de engenharia de atributos ou manipulação de dados, utilize os módulos em `src/features/` e `src/app/`.
- O modelo treinado e artefatos ficam em `src/models/`.

