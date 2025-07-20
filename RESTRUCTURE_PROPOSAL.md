# 🏗️ Proposta de Reestruturação do Projeto

## 📁 **Nova Estrutura Proposta:**

```
TechChallenge_Fase5/
├── 📁 src/
│   ├── 📁 api/                    # API Flask separada
│   │   ├── __init__.py
│   │   ├── app.py                 # Aplicação Flask principal
│   │   ├── routes/                # Rotas organizadas
│   │   │   ├── __init__.py
│   │   │   ├── health.py          # Endpoints de saúde
│   │   │   ├── prediction.py      # Endpoints de predição
│   │   │   └── metrics.py         # Endpoints de métricas
│   │   └── middleware/            # Middlewares
│   │       ├── __init__.py
│   │       ├── logging.py         # Logging
│   │       └── validation.py     # Validação de entrada
│   ├── 📁 core/                   # Lógica de negócio central
│   │   ├── __init__.py
│   │   ├── config.py              # Configurações centralizadas
│   │   ├── exceptions.py          # Exceções customizadas
│   │   └── constants.py           # Constantes do projeto
│   ├── 📁 data/                   # Camada de dados
│   │   ├── __init__.py
│   │   ├── loaders.py             # Carregadores de dados
│   │   ├── validators.py          # Validadores de dados
│   │   └── preprocessors.py       # Pré-processadores
│   ├── 📁 features/               # ✅ Mantém atual (100% cobertura)
│   │   ├── __init__.py
│   │   └── feature_engineering.py
│   ├── 📁 models/
│   │   ├── __init__.py
│   │   ├── base.py                # Classe base para modelos
│   │   ├── prediction_pipeline.py # Pipeline de predição
│   │   ├── training_pipeline.py   # Pipeline de treinamento
│   │   ├── utils.py               # ✅ Mantém atual (100% cobertura)
│   │   └── artifacts/             # Artefatos salvos
│   ├── 📁 services/               # Serviços de negócio
│   │   ├── __init__.py
│   │   ├── prediction_service.py  # Serviço de predição
│   │   ├── matching_service.py    # Serviço de matching
│   │   └── metrics_service.py     # Serviço de métricas
│   └── 📁 utils/                  # Utilitários gerais
│       ├── __init__.py
│       ├── text_processing.py     # Processamento de texto
│       ├── file_handlers.py       # Manipulação de arquivos
│       └── decorators.py          # Decoradores utilitários
├── 📁 frontend/                   # Interface separada
│   ├── streamlit_app.py           # App Streamlit principal
│   ├── components/                # Componentes reutilizáveis
│   │   ├── __init__.py
│   │   ├── file_upload.py         # Upload de arquivos
│   │   ├── results_display.py     # Exibição de resultados
│   │   └── metrics_display.py     # Exibição de métricas
│   └── styles/                    # Estilos CSS
│       └── main.css
├── 📁 config/                     # Configurações
│   ├── development.yaml
│   ├── production.yaml
│   └── testing.yaml
├── 📁 scripts/                    # Scripts utilitários
│   ├── setup_project.py           # Setup inicial
│   ├── train_model.py             # Treinamento de modelo
│   ├── generate_reports.py        # Geração de relatórios
│   └── data_validation.py         # Validação de dados
├── 📁 docs/                       # Documentação
│   ├── api/                       # Documentação da API
│   ├── deployment/                # Guias de deployment
│   └── development/               # Guias de desenvolvimento
├── 📁 tests/                      # ✅ Estrutura atual boa
│   ├── unit/
│   ├── integration/
│   ├── fixtures/
│   └── conftest.py
├── 📁 docker/                     # ✅ Mantém atual
├── 📁 artifacts/                  # Artefatos do modelo
└── 📁 data/                       # Dados do projeto
    ├── raw/
    ├── processed/
    └── external/
```

## 🎯 **Benefícios da Reestruturação:**

### ✅ **Separação de Responsabilidades**
- API Flask isolada da interface Streamlit
- Serviços de negócio separados da lógica de apresentação
- Configurações centralizadas

### ✅ **Melhora na Testabilidade**
- Componentes menores e mais focados
- Facilita mocking e testes unitários
- Separação clara entre camadas

### ✅ **Escalabilidade**
- Cada serviço pode evoluir independentemente
- Facilita adição de novos endpoints
- Suporte a múltiplos frontends

### ✅ **Manutenibilidade**
- Código mais organizado e legível
- Facilita onboarding de novos desenvolvedores
- Reduz acoplamento entre componentes

## 🚀 **Próximos Passos Sugeridos:**

### 1. **Prioridade Alta:**
- [ ] Separar API Flask do Streamlit
- [ ] Criar testes para `predict.py` e `train.py`
- [ ] Implementar configurações centralizadas
- [ ] Adicionar validação de entrada robusta

### 2. **Prioridade Média:**
- [ ] Reestruturar em serviços
- [ ] Melhorar documentação da API
- [ ] Implementar logging estruturado
- [ ] Adicionar monitoramento de performance

### 3. **Prioridade Baixa:**
- [ ] Criar componentes Streamlit reutilizáveis
- [ ] Implementar cache inteligente
- [ ] Adicionar testes de carga
- [ ] Criar pipeline de CI/CD

## 📊 **Metas de Cobertura:**

| Módulo | Atual | Meta | Prioridade |
|--------|-------|------|------------|
| `train.py` | 0% | 80% | 🔴 Crítica |
| `predict.py` | 21% | 85% | 🟡 Alta |
| `api/` | - | 90% | 🟡 Alta |
| `services/` | - | 85% | 🟢 Média |
| **Total** | 38% | 80% | 🎯 **Meta** |
