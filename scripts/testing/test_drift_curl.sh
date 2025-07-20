#!/bin/bash

# Script para testar drift detection usando apenas curl
# ====================================================

API_URL="http://localhost:8080"

echo "🎯 TESTE DE DRIFT DETECTION COM CURL"
echo "====================================="

# Verificar se API está rodando
echo "🔍 Verificando API..."
if ! curl -s "$API_URL/health" > /dev/null; then
    echo "❌ API não está respondendo"
    echo "💡 Inicie a API: python src/app/main.py"
    exit 1
fi
echo "✅ API está ativa"

# Inicializar drift detection
echo "🚀 Inicializando drift detection..."
curl -s -X POST "$API_URL/drift/initialize" > /dev/null

echo ""
echo "📊 INSTRUÇÕES:"
echo "1. Abra http://localhost:3000"
echo "2. Vá para 'Fase5 - Dashboard'"
echo "3. Role até '6. Drift Detection'"
echo "4. Observe os painéis durante o teste"
echo ""
read -p "Pressione ENTER para continuar..."

# Função para enviar dados
send_data() {
    local idade=$1
    local salario=$2
    local experiencia=$3
    local score_credito=$4
    local educacao=$5
    
    curl -s -X POST "$API_URL/predict" \
        -H "Content-Type: application/json" \
        -d "{\"idade\": $idade, \"salario\": $salario, \"experiencia\": $experiencia, \"score_credito\": $score_credito, \"educacao\": $educacao}" \
        > /dev/null
}

echo ""
echo "🟢 FASE 1: Enviando dados NORMAIS (20 amostras)..."
for i in {1..20}; do
    # Dados normais
    idade=$((30 + RANDOM % 20))
    salario=$((40000 + RANDOM % 20000))
    experiencia=$((5 + RANDOM % 10))
    score_credito=$((650 + RANDOM % 100))
    educacao=$((RANDOM % 4))
    
    send_data $idade $salario $experiencia $score_credito $educacao
    
    if [ $((i % 5)) -eq 0 ]; then
        echo "  📊 $i/20 amostras processadas"
    fi
    
    sleep 0.3
done
echo "✅ Dados normais enviados"

echo ""
echo "⏱️ Aguarde 5 segundos para observar o dashboard..."
sleep 5

echo ""
echo "🟡 FASE 2: Enviando dados com DRIFT (15 amostras)..."
for i in {1..15}; do
    # Dados com drift
    idade=$((50 + RANDOM % 20))        # Mais velhos
    salario=$((80000 + RANDOM % 40000)) # Salários maiores
    experiencia=$((15 + RANDOM % 10))   # Mais experiência
    score_credito=$((550 + RANDOM % 100)) # Score menor
    educacao=3                          # Mais educação
    
    send_data $idade $salario $experiencia $score_credito $educacao
    
    if [ $((i % 5)) -eq 0 ]; then
        echo "  📊 $i/15 amostras processadas"
    fi
    
    sleep 0.4
done
echo "✅ Dados com drift enviados"

echo ""
echo "⏱️ Aguarde 5 segundos para observar o dashboard..."
sleep 5

echo ""
echo "🔴 FASE 3: Enviando dados com DRIFT EXTREMO (10 amostras)..."
for i in {1..10}; do
    # Drift extremo
    idade=$((18 + RANDOM % 7))          # Muito jovens
    salario=$((20000 + RANDOM % 15000)) # Salários baixos
    experiencia=$((RANDOM % 3))         # Pouca experiência
    score_credito=$((400 + RANDOM % 150)) # Score muito baixo
    educacao=0                          # Baixa educação
    
    send_data $idade $salario $experiencia $score_credito $educacao
    
    if [ $((i % 3)) -eq 0 ]; then
        echo "  📊 $i/10 amostras processadas"
    fi
    
    sleep 0.5
done
echo "✅ Dados extremos enviados"

echo ""
echo "⏱️ Processando resultados..."
sleep 3

# Mostrar status
echo ""
echo "📊 STATUS FINAL:"
echo "================"
echo "🔍 Status do drift detection:"
curl -s "$API_URL/drift/status" | python -m json.tool 2>/dev/null || echo "Dados processados com sucesso"

echo ""
echo "🚨 Alertas de drift:"
curl -s "$API_URL/drift/alerts" | python -m json.tool 2>/dev/null | tail -20 || echo "Verifique alertas no dashboard"

echo ""
echo "🎉 TESTE CONCLUÍDO!"
echo "=================="
echo "📊 Verifique o dashboard em:"
echo "   http://localhost:3000"
echo ""
echo "🎯 Painéis para observar:"
echo "   - Alertas de Drift Detection (5m)"
echo "   - Total de Alertas de Drift"
echo "   - Features Analisadas para Drift"
echo "   - Performance do Modelo - Accuracy"
echo "   - Execuções de Monitoramento de Drift"
echo ""
echo "💡 Execute novamente para gerar mais dados!"
