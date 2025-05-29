# Datathon Machine Learning Engineering

Este repositório contém a solução do Datathon de Machine Learning Engineering para otimizar o processo de "match" entre candidatos e vagas da Decision, conforme descrito no material do curso fileciteturn12file2. Abaixo está a documentação de como configurar e executar cada etapa do projeto.

---

## 1. Estrutura do Projeto

```text
├── data/
│   ├── raw/                    # Dados originais (JSON completos)
│   │   ├── vagas.json          # Informações sobre vagas
│   │   ├── prospects.json      # Lista de prospecções por vaga
│   │   └── applicants.json     # Perfis completos dos candidatos
│   └── processed/              # Dados tabulares pós-pré-processamento
│       └── dataset.csv         # Dataset unificado
│
├── docs/                       # Documentação adicional (ex.: arquitetura)
│   └── architecture.md
│
├── src/                        # Código-fonte
│   ├── data_processing/        # Pré-processamento de JSONs
│   │   └── preprocess.py       # Carrega e une dados brutos
│   │
│   ├── features/               # Engenharia de atributos
│   │   └── feature_engineering.py  # Cria features para o modelo
│   │
│   ├── models/                 # Treino, avaliação e artefatos
│   │   ├── train.py            # Pipeline de treinamento
│   │   ├── evaluate.py         # Avaliação de performance
│   │   ├── save_model.py       # Agrupa modelo e encoders
│   │   └── artifacts/          # Modelos salvos (joblib/pipeline)
│   │
│   ├── api/                    # Serviço de inferência
│   │   ├── api.py              # Endpoint `/predict` (Flask)
│   │   └── requirements.txt    # Dependências da API
│   │
│   ├── monitoring/             # Monitoramento de drift
│   │   └── drift_monitor.py    # PSI e KS para features
│   │
│   └── utils/                  # Funcionalidades auxiliares
│       └── logger.py           # Configuração de logs
│
├── tests/                      # Testes unitários (pytest)
│   ├── test_preprocess.py
│   ├── test_feature_engineering.py
│   ├── test_train.py
│   └── test_api.py
│
├── docker/                     # Contêinerização
│   ├── Dockerfile              # Imagem da API
│   └── docker-compose.yml      # Orquestração do serviço
│
├── .gitignore
└── README.md                   # Esta documentação
```

---

## 2. Dados

Os dados estão em formato JSON e foram anonimizados. A estrutura dos arquivos brutos segue:

* **vagas.json**: chaveado pelo código da vaga, contém informações básicas, perfil e benefícios.
* **prospects.json**: lista de prospecções (código, nome, comentário, situação) por vaga.
* **applicants.json**: dados pessoais, profissionais, formação e CV de cada candidato.

Para mais detalhes sobre os campos, consulte `READ.ME.txt` fileciteturn12file1.

---

## 3. Instalação

1. Clone o repositório:

   ```bash
   git clone <URL-do-repositório>
   cd decision-datathon
   ```
2. Crie e ative um ambiente virtual (venv):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

---

## 4. Fluxo de Execução

### 4.1 Pré-processamento

```bash
python src/data_processing/preprocess.py
```

* Carrega JSON brutos e gera `data/processed/dataset.csv`.

### 4.2 Engenharia de Features

A etapa é automaticamente chamada em `train.py`, mas você pode testar isoladamente:

```bash
python - <<EOF
from src.features.feature_engineering import create_features
import pandas as pd

df = pd.read_csv('data/processed/dataset.csv')
df_feat, encs = create_features(df)
print(df_feat.head())
EOF
```

### 4.3 Treinamento

```bash
python src/models/train.py
```

* Divide treino/teste, ajusta `RandomForestClassifier` e salva `model.joblib` e `encoders.joblib` em `src/models/artifacts/`.

### 4.4 Avaliação

```bash
python src/models/evaluate.py
```

* Gera `classification_report.json` e `confusion_matrix.csv` em `src/models/artifacts/`.

### 4.5 Empacotamento do Modelo

```bash
python src/models/save_model.py
```

* Cria `pipeline.joblib` contendo modelo, encoders e lista de features para a API.

### 4.6 Execução da API

```bash
# Com venv ativo
python src/api/api.py
```

* Servidor Flask disponível em `http://localhost:5000/predict`.
* Envie POST com JSON contendo campos necessários e receba `prediction` + `probabilities`.

---

## 5. Contêiner Docker

### 5.1 Build e Run

```bash
cd docker
docker-compose up --build
```

* API exposta em `localhost:5000`.

---

## 6. Monitoramento de Drift

Execute periodicamente:

```bash
python src/monitoring/drift_monitor.py
```

* Compara distribuições de features entre `dataset.csv` e `new_data.csv`, salvando `drift_report.csv` em `src/monitoring/`.

---

## 7. Testes

Para garantir qualidade de código e funcionalidade:

```bash
pytest
```

* Testes cobrem pré-processamento, engenharia de features, pipeline de treino e endpoint da API.

---

## 8. Deploy

Você pode optar por:

* Serviços de nuvem (Heroku, AWS, GCP).
* Deploy local com Docker.

### 8.1 Exemplos de cURL

```bash
curl -X POST http://localhost:5000/predict \
  -H 'Content-Type: application/json' \
  -d '{"data_requisicao":"01-01-2025", "data_candidatura":"03-01-2025", … }'
```

