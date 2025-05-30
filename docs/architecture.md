# Arquitetura do Projeto

Este documento descreve a arquitetura da solução de Machine Learning para match candidato-vaga, cobrindo componentes, fluxo de dados e deploy.

## 1. Visão Geral

A arquitetura segue um pipeline modular com as seguintes etapas:

1. **Ingestão de Dados**: carregamento dos arquivos JSON originais (`vagas.json`, `prospects.json`, `applicants.json`).
2. **Pré-processamento**: desnormalização e união em um único dataset tabular (`preprocess.py`).
3. **Feature Engineering**: transformação de datas, extração de métricas de texto e codificação de categorias (`feature_engineering.py`).
4. **Treinamento e Avaliação**: treinamento de um modelo de Random Forest, avaliação e geração de artefatos (`train.py`, `evaluate.py`, `save_model.py`).
5. **Empacotamento do Modelo**: criação de pipeline de inferência com modelo e encoders (`pipeline.joblib`).
6. **Serviço de Inferência**: API Flask expondo endpoint `/predict` para receber requisições e retornar previsões (`api.py`).
7. **Monitoramento de Drift**: cálculo de PSI e KS-test entre dataset de referência e novos batches (`drift_monitor.py`).
8. **Containerização e Deploy**: Dockerfile e docker-compose para orquestração do serviço.
9. **Logging e Observabilidade**: configuração de logger para uniformizar logs em console e arquivo (`logger.py`).

## 2. Diagrama de Arquitetura

> **\[Insira aqui um diagrama de fluxo (ex.: Draw\.io, Lucidchart) mostrando as relações entre componentes]**

```text
        +--------------+        +----------------+        +-------------+
        | JSON Brutos  | -----> | preprocess.py  | -----> | dataset.csv |
        +--------------+        +----------------+        +-------------+
                                       |
                                       v
                              +----------------------+
                              | feature_engineering.py|
                              +----------------------+
                                       |
                      +----------------v--------------+
                      | train.py / evaluate.py / save_model.py|
                      +----------------+--------------+
                                       |
                                       v
                          +---------------------------+
                          | pipeline.joblib (artefato)|
                          +---------------------------+
                                       |
                                       v
                               +---------------+
                               | api.py (Flask)|
                               +---------------+
                                       |
                              Requests over HTTP
                                       |
                          +----------------------+         +----------------------+  
                          | Docker Container API | <-----> | docker-compose (orquestração) |
                          +----------------------+         +----------------------+  

                                      +-----+
                                      | drift_monitor.py |
                                      +-----+

```

## 3. Fluxo de Dados

1. **Extração**: `preprocess.py` lê os JSON em `/data/raw`.
2. **Transformação**:

   * `feature_engineering.py` converte datas, extrai contagens de texto e codifica categóricas.
3. **Modelagem**:

   * `train.py` treina e gera `model.joblib` e `encoders.joblib`.
   * `evaluate.py` avalia e gera relatórios em JSON e CSV.
   * `save_model.py` empacota todos os artefatos em `pipeline.joblib`.
4. **Carga**:

   * `api.py` carrega `pipeline.joblib` e disponibiliza `/predict`.
5. **Monitoramento**:

   * `drift_monitor.py` compara distribuições entre datasets e salva relatório.

## 4. Deploy e Escalonamento

* **Local / Desenvolvimento**: usar `docker-compose up --build` dentro da pasta `docker/`.
* **Produção**: hospedar container Docker em orquestrador (Kubernetes, ECS, etc.).
* **Escalonamento**: replicação do serviço API e uso de filas (ex.: RabbitMQ) se necessário.

---

*Este documento pode ser expandido com detalhes de infraestrutura (rede, segurança, CI/CD) conforme necessidade.*
