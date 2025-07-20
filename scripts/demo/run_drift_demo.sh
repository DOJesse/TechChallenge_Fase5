#!/bin/bash

# Script de Demonstração do Drift Detection Dashboard
# ===================================================

echo "🎯 DEMONSTRAÇÃO DE DRIFT DETECTION NO DASHBOARD"
echo "================================================"

# Verificar se estamos no diretório correto
if [ ! -f "demo_drift_dashboard.py" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto"
    exit 1
fi

# Função para verificar se um comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar dependências
echo "🔍 Verificando dependências..."

if ! command_exists python3; then
    echo "❌ Python3 não encontrado. Instale o Python 3.7+"
    exit 1
fi

if ! command_exists docker; then
    echo "❌ Docker não encontrado. Instale o Docker"
    exit 1
fi

if ! command_exists docker-compose; then
    echo "❌ Docker Compose não encontrado. Instale o docker-compose"
    exit 1
fi

echo "✅ Dependências verificadas"

# Instalar dependências Python se necessário
echo "📦 Instalando dependências Python..."
pip3 install requests numpy pandas > /dev/null 2>&1 || {
    echo "⚠️ Aviso: Não foi possível instalar algumas dependências"
    echo "Execute manualmente: pip install requests numpy pandas"
}

# Verificar se os serviços estão rodando
echo "🐳 Verificando serviços Docker..."

if ! docker ps | grep -q "prometheus\|grafana"; then
    echo "🚀 Iniciando serviços Docker..."
    cd docker && docker-compose up -d
    cd ..
    echo "⏱️ Aguardando serviços iniciarem (30 segundos)..."
    sleep 30
else
    echo "✅ Serviços Docker já estão rodando"
fi

# Verificar se a API está rodando
echo "🔍 Verificando API..."
if ! curl -s http://localhost:8080/health > /dev/null; then
    echo "🚀 Iniciando API..."
    python3 src/app/main.py &
    API_PID=$!
    echo "⏱️ Aguardando API iniciar (15 segundos)..."
    sleep 15
    
    if ! curl -s http://localhost:8080/health > /dev/null; then
        echo "❌ Erro: API não está respondendo"
        kill $API_PID 2>/dev/null
        exit 1
    fi
    echo "✅ API iniciada (PID: $API_PID)"
else
    echo "✅ API já está rodando"
fi

echo ""
echo "🎭 INICIANDO DEMONSTRAÇÃO"
echo "========================="

# Menu de opções
echo "Escolha o cenário para demonstração:"
echo "1) Demo Completa (recomendado)"
echo "2) Apenas Baseline (sem drift)"
echo "3) Apenas Data Drift"
echo "4) Apenas Concept Drift"
echo "5) Apenas Drift Extremo"
echo ""
read -p "Digite sua escolha (1-5): " choice

case $choice in
    1)
        scenario="demo_completa"
        echo "🎯 Executando demonstração completa..."
        ;;
    2)
        scenario="baseline"
        echo "🟢 Executando cenário baseline..."
        ;;
    3)
        scenario="data_drift"
        echo "🟡 Executando cenário de data drift..."
        ;;
    4)
        scenario="concept_drift"
        echo "🟠 Executando cenário de concept drift..."
        ;;
    5)
        scenario="extreme_drift"
        echo "🔴 Executando cenário de drift extremo..."
        ;;
    *)
        echo "❌ Opção inválida. Executando demo completa..."
        scenario="demo_completa"
        ;;
esac

echo ""
echo "📊 INSTRUÇÕES PARA OBSERVAR O DASHBOARD:"
echo "========================================"
echo "1. Abra http://localhost:3000 no seu navegador"
echo "2. Faça login (admin/admin se for a primeira vez)"
echo "3. Navegue até o dashboard 'Fase5 - Dashboard'"
echo "4. Role até a seção '6. Drift Detection'"
echo "5. Observe os painéis enquanto a demonstração executa"
echo ""
echo "⏱️ A demonstração iniciará em 10 segundos..."
sleep 10

# Executar a demonstração
python3 demo_drift_dashboard.py "$scenario"

echo ""
echo "🎉 DEMONSTRAÇÃO CONCLUÍDA!"
echo "========================="
echo ""
echo "📊 LINKS IMPORTANTES:"
echo "- Dashboard: http://localhost:3000"
echo "- Prometheus: http://localhost:9090"
echo "- API Health: http://localhost:8080/health"
echo "- Drift Status: http://localhost:8080/drift/status"
echo "- Drift Alerts: http://localhost:8080/drift/alerts"
echo ""
echo "🔍 MÉTRICAS NO DASHBOARD:"
echo "- Alertas de Drift Detection (5m)"
echo "- Total de Alertas de Drift"
echo "- Features Analisadas para Drift"
echo "- Performance do Modelo - Accuracy"
echo "- Execuções de Monitoramento de Drift"
echo ""
echo "💡 DICA: Execute novamente com diferentes cenários para ver"
echo "   como o dashboard reage a diferentes tipos de drift!"

# Opção para manter serviços rodando
echo ""
read -p "Deseja parar os serviços Docker? (y/N): " stop_services

if [[ $stop_services =~ ^[Yy]$ ]]; then
    echo "🛑 Parando serviços..."
    cd docker && docker-compose down
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
    fi
    echo "✅ Serviços parados"
else
    echo "✅ Serviços mantidos rodando"
    echo "   Para parar depois: cd docker && docker-compose down"
fi
