# Datathon Machine Learning Engineering

Este repositório contém a solução do Datathon de Machine Learning Engineering para otimizar o processo de "match" entre candidatos e vagas da Decision. Abaixo está a documentação de como configurar e executar cada etapa do projeto.

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
   git clone <URL-do-repositório>
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

---

## 4. Execução do App (Streamlit)

```bash
streamlit run streamlit_app.py
```

O app será iniciado em `http://localhost:8501`.

---

## 5. Testes

Para rodar os testes unitários:

```bash
pytest tests/
```

---

## 6. Contêiner Docker

### Build e Run

```bash
cd docker
# Para o app Streamlit:
docker-compose -f docker-compose.yaml up --build
```

O app estará disponível em `localhost:8502`.

---

## 7. Observações

- Certifique-se de que os dados estejam em `src/data/raw/`.
- Para executar scripts de engenharia de atributos ou manipulação de dados, utilize os módulos em `src/features/` e `src/app/`.
- O modelo treinado e artefatos ficam em `src/models/`.

