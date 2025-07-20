#!/usr/bin/env python3
"""
Script Corrigido para Testar Drift Detection
"""

import requests
import json
import time
import random

API_URL = "http://localhost:8080"

def test_prediction_simple():
    """Teste simples de predição para drift detection"""
    
    print("🎯 TESTE SIMPLES DE DRIFT DETECTION")
    print("=" * 50)
    
    # Verificar API
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print("✅ API está ativa")
    except:
        print("❌ API não está ativa")
        return
    
    # Inicializar drift detection
    try:
        response = requests.post(f"{API_URL}/drift/initialize")
        print("✅ Drift detection inicializado")
    except:
        print("⚠️ Erro ao inicializar drift detection")
    
    print("\n📊 INSTRUÇÕES:")
    print("1. Abra http://localhost:3000")
    print("2. Vá para 'Fase5 - Dashboard'")
    print("3. Role até '6. Drift Detection'")
    print("4. Observe os painéis")
    
    input("\n⏱️ Pressione ENTER para continuar...")
    
    # Função para enviar predições
    def send_predictions(data_list, name, color):
        print(f"\n{color} Enviando {len(data_list)} amostras {name}...")
        success = 0
        for i, candidate_data in enumerate(data_list):
            data = {
                "candidate": candidate_data,
                "vacancy": {"description": f"{name}_test"}
            }
            try:
                response = requests.post(f"{API_URL}/predict", json=data, timeout=10)
                if response.status_code == 200:
                    success += 1
                    if (i + 1) % 5 == 0:
                        print(f"  📊 {i + 1}/{len(data_list)} processadas")
                else:
                    print(f"  ⚠️ Erro {response.status_code} na amostra {i + 1}")
            except Exception as e:
                print(f"  ❌ Erro na amostra {i + 1}: {e}")
            time.sleep(0.3)
        print(f"✅ {name} concluído: {success}/{len(data_list)} sucessos")
    
    # 1. Dados normais (baseline)
    normal_data = []
    for _ in range(15):
        normal_data.append({
            "idade": random.uniform(25, 45),
            "salario": random.uniform(40000, 60000),
            "experiencia": random.uniform(3, 12),
            "score_credito": random.uniform(650, 750),
            "educacao": random.choice([1, 2, 3])
        })
    
    send_predictions(normal_data, "NORMAIS", "🟢")
    
    time.sleep(3)
    
    # 2. Dados com drift
    drift_data = []
    for _ in range(12):
        drift_data.append({
            "idade": random.uniform(50, 70),        # Mais velhos
            "salario": random.uniform(80000, 120000), # Salários maiores
            "experiencia": random.uniform(15, 25),   # Mais experiência
            "score_credito": random.uniform(550, 650), # Score menor
            "educacao": random.choice([2, 3, 3])     # Mais educação
        })
    
    send_predictions(drift_data, "COM DRIFT", "🟡")
    
    time.sleep(3)
    
    # 3. Dados extremos
    extreme_data = []
    for _ in range(8):
        extreme_data.append({
            "idade": random.uniform(18, 25),        # Muito jovens
            "salario": random.uniform(20000, 35000), # Salários baixos
            "experiencia": random.uniform(0, 2),     # Pouca experiência
            "score_credito": random.uniform(400, 550), # Score muito baixo
            "educacao": random.choice([0, 0, 1])     # Baixa educação
        })
    
    send_predictions(extreme_data, "EXTREMOS", "🔴")
    
    # Status final
    print("\n📊 VERIFICANDO RESULTADOS...")
    time.sleep(2)
    
    try:
        # Status drift
        response = requests.get(f"{API_URL}/drift/status")
        if response.status_code == 200:
            status = response.json()
            print(f"🔍 Features monitoradas: {status.get('features_monitored', 'N/A')}")
            print(f"⚡ Total execuções: {status.get('total_executions', 'N/A')}")
        
        # Alertas
        response = requests.get(f"{API_URL}/drift/alerts")
        if response.status_code == 200:
            alerts = response.json()
            print(f"🚨 Total de alertas: {len(alerts)}")
            if alerts:
                for alert in alerts[-3:]:  # Últimos 3
                    print(f"  - {alert.get('type', 'N/A')}: {alert.get('message', 'N/A')}")
    except Exception as e:
        print(f"⚠️ Erro ao verificar status: {e}")
    
    print("\n🎉 TESTE CONCLUÍDO!")
    print("📊 Verifique o dashboard para ver os resultados!")
    print("🌐 Dashboard: http://localhost:3000")

if __name__ == "__main__":
    test_prediction_simple()
