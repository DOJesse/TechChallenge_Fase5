# 🎯 DEMONSTRAÇÃO DO DRIFT DETECTION DASHBOARD

Este documento explica como testar e demonstrar o sistema de drift detection implementado, visualizando os resultados em tempo real no dashboard do Grafana.

## 📋 Pré-requisitos

- **Python 3.7+** instalado
- **Docker** e **Docker Compose** instalados
- **Dependências Python**: requests, numpy, pandas
- **Portas livres**: 3000 (Grafana), 9090 (Prometheus), 5000 (API)

## 🚀 Execução Rápida

### Opção 1: Script Automatizado (Recomendado)

```bash
# Execute o script de demonstração
./run_drift_demo.sh
```

O script irá:
1. ✅ Verificar dependências
2. 🐳 Iniciar serviços Docker (Grafana + Prometheus)
3. 🚀 Iniciar a API Flask
4. 🎯 Executar cenários de drift
5. 📊 Mostrar resultados no dashboard

### Opção 2: Execução Manual

```bash
# 1. Iniciar serviços Docker
cd docker
docker-compose up -d
cd ..

# 2. Instalar dependências Python
pip install requests numpy pandas

# 3. Iniciar a API
python src/app/main.py &

# 4. Executar demonstração
python demo_drift_dashboard.py demo_completa
```

## 🎭 Cenários Disponíveis

### 1. **Demo Completa** (Recomendado)
```bash
python demo_drift_dashboard.py demo_completa
```
- Executa todos os cenários em sequência
- Mostra evolução completa do drift
- Duração: ~5-8 minutos

### 2. **Baseline** (Sem Drift)
```bash
python demo_drift_dashboard.py baseline
```
- Simula operação normal
- Estabelece linha de base
- 50 amostras normais

### 3. **Data Drift**
```bash
python demo_drift_dashboard.py data_drift
```
- Simula mudança na distribuição dos dados
- Idade, salário e educação diferentes
- 30 amostras com drift

### 4. **Concept Drift**
```bash
python demo_drift_dashboard.py concept_drift
```
- Simula degradação na performance
- Predições menos precisas
- 25 amostras problemáticas

### 5. **Drift Extremo**
```bash
python demo_drift_dashboard.py extreme_drift
```
- Simula drift severo
- Mudanças drásticas nas distribuições
- 20 amostras extremas

## 📊 Observando o Dashboard

### 1. **Acessar o Grafana**
- URL: http://localhost:3000
- Login: `admin` / `admin` (primeira vez)
- Dashboard: "Fase5 - Dashboard"

### 2. **Seção 6: Drift Detection**

#### Painéis Principais:

**🚨 Alertas de Drift Detection (5m)**
- Gráfico de linha com alertas de data drift e concept drift
- Mostra frequência de detecção em tempo real
- Verde = normal, Amarelo/Vermelho = drift detectado

**📊 Total de Alertas de Drift**
- Contador total de alertas
- Verde: 0 alertas
- Amarelo: 1-4 alertas  
- Vermelho: 5+ alertas

**🔍 Features Analisadas para Drift**
- Quantidade de features sendo monitoradas
- Deve mostrar 5 (idade, salário, experiência, score_credito, educação)

**📈 Performance do Modelo - Accuracy**
- Gráfico da accuracy em tempo real
- Verde: >85%, Amarelo: 75-85%, Vermelho: <75%
- Mostra degradação durante concept drift

**⚡ Execuções de Monitoramento de Drift**
- Taxa de execuções do sistema
- Total de execuções acumuladas

### 3. **O que Observar Durante a Demo**

#### Cenário Baseline:
- ✅ Poucos ou nenhum alerta
- ✅ Accuracy estável (~85-95%)
- ✅ Features sendo analisadas (5)

#### Cenário Data Drift:
- 🟡 Alertas de "data_drift" aparecem
- 📈 Gráfico de alertas mostra picos
- 🔍 Features analisadas mantém 5

#### Cenário Concept Drift:
- 🟠 Alertas de "concept_drift" aparecem  
- 📉 Accuracy diminui visivelmente
- ⚠️ Threshold amarelo/vermelho ativado

#### Cenário Extremo:
- 🔴 Ambos os tipos de alerta disparam
- 📊 Total de alertas aumenta rapidamente
- 🚨 Múltiplos painéis ficam vermelhos

## 🔧 Monitoramento Manual

### Endpoints da API:

```bash
# Verificar saúde da API
curl http://localhost:8080/health

# Status do drift detection
curl http://localhost:8080/drift/status

# Alertas de drift
curl http://localhost:8080/drift/alerts

# Fazer predição manual
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"idade": 35, "salario": 50000, "experiencia": 8, "score_credito": 700, "educacao": 2}'
```

### Métricas no Prometheus:

Acesse http://localhost:9090 e consulte:

```promql
# Alertas de drift por tipo
drift_detection_alerts_total

# Performance do modelo
drift_concept_performance_accuracy

# Features analisadas
drift_data_features_analyzed

# Execuções de monitoramento
drift_monitoring_executions_total
```

## 🎯 Demonstração Efetiva

### Para uma Apresentação:

1. **Preparação (2 min)**
   - Abra Grafana: http://localhost:3000
   - Navegue até "6. Drift Detection"
   - Mostre painéis zerados/normais

2. **Baseline (1 min)**
   - Execute: `python demo_drift_dashboard.py baseline`
   - Mostre operação normal
   - Aponte métricas estáveis

3. **Data Drift (2 min)**
   - Execute: `python demo_drift_dashboard.py data_drift`
   - Mostre alertas aparecendo
   - Explique detecção de mudança nos dados

4. **Concept Drift (2 min)**
   - Execute: `python demo_drift_dashboard.py concept_drift`
   - Mostre accuracy caindo
   - Explique degradação do modelo

5. **Resumo (1 min)**
   - Mostre total de alertas acumulados
   - Explique importância do monitoramento

### Pontos de Destaque:

- 🎯 **Detecção Automática**: Sistema detecta drift sem intervenção
- 📊 **Visualização em Tempo Real**: Dashboard atualiza a cada 5 segundos
- 🚨 **Alertas Específicos**: Diferencia data drift vs concept drift
- 📈 **Métricas Acionáveis**: Thresholds claros para tomada de decisão
- ⚡ **Performance**: Monitoramento com baixa latência

## 🛠️ Solução de Problemas

### API não responde:
```bash
# Verificar se está rodando
ps aux | grep python

# Iniciar manualmente
python src/app/main.py
```

### Dashboard não mostra dados:
```bash
# Verificar serviços Docker
docker ps

# Reiniciar se necessário
cd docker && docker-compose restart
```

### Dependências faltando:
```bash
# Instalar dependências
pip install -r src/app/requirements.txt
pip install requests numpy pandas
```

### Portas ocupadas:
```bash
# Verificar portas em uso
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :9090
sudo netstat -tulpn | grep :5000

# Parar processos se necessário
sudo kill -9 <PID>
```

## 📈 Interpretação dos Resultados

### Métricas Normais:
- **Alertas de Drift**: 0-1 por período
- **Accuracy**: >85%
- **Features Analisadas**: 5
- **Execuções**: Crescimento linear

### Indicadores de Drift:
- **Data Drift**: Alertas frequentes, distribuições diferentes
- **Concept Drift**: Accuracy em queda, performance degradada
- **Drift Extremo**: Múltiplos alertas, thresholds ultrapassados

### Ações Recomendadas:
- **Data Drift**: Retreinar com dados novos
- **Concept Drift**: Revisar arquitetura do modelo
- **Drift Extremo**: Investigação urgente, possível parada do sistema

---

## 🎉 Conclusão

Este sistema de drift detection oferece monitoramento completo e em tempo real da qualidade dos dados e performance do modelo ML, permitindo detecção precoce de problemas e ação proativa para manter a qualidade das predições.

Para mais informações, consulte a documentação técnica em `REPORTS.md`.
