# 🚀 GUIA RÁPIDO - TESTE DE DRIFT DETECTION

## ⚡ Execução Mais Simples

### 1. Iniciar Serviços
```bash
# Terminal 1 - Iniciar Docker
cd docker && docker-compose up -d

# Terminal 2 - Iniciar API
python src/app/main.py
```

### 2. Executar Teste
```bash
# Terminal 3 - Teste rápido
python test_drift_simple.py
```

### 3. Observar Dashboard
- Abra: http://localhost:3000
- Login: admin/admin
- Dashboard: "Fase5 - Dashboard"
- Seção: "6. Drift Detection"

## 📊 O que Esperar Ver

### Durante o Teste:

1. **Dados Normais** (20 amostras)
   - Poucos alertas
   - Métricas estáveis

2. **Dados com Drift** (15 amostras)
   - Alertas de "data_drift" aparecem
   - Gráficos mostram mudanças

3. **Dados Extremos** (10 amostras)
   - Múltiplos alertas
   - Painéis ficam vermelhos

### Painéis no Dashboard:

- **📈 Alertas de Drift Detection**: Gráfico de linha com picos
- **📊 Total de Alertas**: Contador crescente
- **🔍 Features Analisadas**: Deve mostrar "5"
- **📉 Performance do Modelo**: Accuracy variável
- **⚡ Execuções de Monitoramento**: Taxa de processamento

## 🛠️ Solução Rápida de Problemas

### API não responde:
```bash
# Verificar se está rodando
curl http://localhost:8080/health

# Se não estiver, iniciar:
python src/app/main.py
```

### Dashboard sem dados:
```bash
# Verificar Grafana
curl http://localhost:3000

# Reiniciar se necessário
cd docker && docker-compose restart grafana
```

### Dependências faltando:
```bash
pip install requests
```

## 🎯 Para Demonstrações

1. **Preparar** (30s): Iniciar serviços
2. **Mostrar** (1min): Dashboard limpo
3. **Executar** (2min): Script de teste
4. **Explicar** (2min): Resultados nos painéis

**Total: ~5 minutos para demo completa**

## 💡 Dicas

- Execute múltiplas vezes para acumular mais alertas
- Dashboard atualiza a cada 5 segundos
- Use dados extremos para efeito visual máximo
- Mostre diferença entre data drift vs concept drift
