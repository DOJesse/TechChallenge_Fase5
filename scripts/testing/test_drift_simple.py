#!/usr/bin/env python3
"""
Script Simples para Testar Drift Detection no Dashboard
=======================================================

Este script envia dados simulados para testar o drift detection
e tornar os painéis visíveis no dashboard.
"""

import requests
import json
import time
import random

# Configuração
API_URL = "http://localhost:8080"
DELAY_BETWEEN_REQUESTS = 0.5  # segundos

def test_api_connection():
    """Testa se a API está respondendo"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API está ativa")
            return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        print("💡 Certifique-se de que a API está rodando: python src/app/main.py")
        return False

def initialize_drift_system():
    """Inicializa o sistema de drift detection"""
    try:
        response = requests.post(f"{API_URL}/drift/initialize")
        if response.status_code == 200:
            print("✅ Drift detection inicializado")
            return True
        else:
            print(f"⚠️ Erro ao inicializar: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def send_normal_data(count=20):
    """Envia dados normais (baseline)"""
    print(f"\n🟢 Enviando {count} amostras NORMAIS...")
    
    for i in range(count):
        # Dados normais para recruitment matching
        data = {
            "candidate": {
                "skills": f"python machine learning dados experiencia {random.randint(2, 12)} anos",
                "experience": f"{random.randint(2, 8)} anos de experiência"
            },
            "vacancy": {
                "requirements": "python machine learning dados sql",
                "seniority": random.choice(["junior", "pleno", "senior"])
            }
        }
        
        try:
            response = requests.post(f"{API_URL}/predict", json=data, timeout=10)
            if response.status_code == 200:
                if (i + 1) % 5 == 0:
                    print(f"  📊 {i + 1}/{count} processadas")
            else:
                print(f"  ⚠️ Erro na amostra {i + 1}")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
        
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    print("✅ Dados normais enviados")

def send_drift_data(count=15):
    """Envia dados com drift"""
    print(f"\n🟡 Enviando {count} amostras com DRIFT...")
    
    for i in range(count):
        # Dados com drift - perfis e vagas diferentes
        data = {
            "candidate": {
                "skills": f"javascript react frontend node {random.randint(1, 3)} anos",
                "experience": f"{random.randint(1, 4)} anos como desenvolvedor frontend"
            },
            "vacancy": {
                "requirements": "java spring backend microservices kubernetes",
                "seniority": random.choice(["senior", "especialista"])
            }
        }
        
        try:
            response = requests.post(f"{API_URL}/predict", json=data, timeout=10)
            if response.status_code == 200:
                if (i + 1) % 5 == 0:
                    print(f"  📊 {i + 1}/{count} processadas")
            else:
                print(f"  ⚠️ Erro na amostra {i + 1}")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
        
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    print("✅ Dados com drift enviados")

def send_extreme_drift_data(count=10):
    """Envia dados com drift extremo"""
    print(f"\n🔴 Enviando {count} amostras com DRIFT EXTREMO...")
    
    for i in range(count):
        # Dados com drift extremo - usando formato correto para recruitment matching
        data = {
            "candidate": {
                "skills": f"cobol assembly mainframe fortran legacy systems vintage computing {random.randint(1, 2)} anos",
                "experience": f"{random.randint(30, 40)} anos de experiência em sistemas legados mainframe"
            },
            "vacancy": {
                "requirements": "python react javascript nodejs modern web development",
                "seniority": random.choice(["junior", "estagiario"])
            }
        }
        
        try:
            response = requests.post(f"{API_URL}/predict", json=data, timeout=10)
            if response.status_code == 200:
                if (i + 1) % 3 == 0:
                    print(f"  📊 {i + 1}/{count} processadas")
            else:
                print(f"  ⚠️ Erro na amostra {i + 1}")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
        
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    print("✅ Dados extremos enviados")

def send_performance_data(count=15):
    """Envia dados para simular performance do modelo"""
    print(f"\n🎯 Enviando {count} amostras para PERFORMANCE DO MODELO...")
    
    # Simular diferentes cenários de performance
    performance_scenarios = [
        # Cenário 1: Match muito bom (accuracy alta)
        {
            "candidate": {
                "skills": "python machine learning data science tensorflow keras",
                "experience": "5 anos de experiência em machine learning"
            },
            "vacancy": {
                "requirements": "python machine learning data science tensorflow",
                "seniority": "pleno"
            }
        },
        # Cenário 2: Match moderado
        {
            "candidate": {
                "skills": "java spring boot backend microservices",
                "experience": "3 anos de experiência em desenvolvimento backend"
            },
            "vacancy": {
                "requirements": "java spring backend desenvolvimento",
                "seniority": "junior"
            }
        },
        # Cenário 3: Match ruim (para simular degradação)
        {
            "candidate": {
                "skills": "photoshop illustrator design gráfico marketing",
                "experience": "2 anos de experiência em design"
            },
            "vacancy": {
                "requirements": "python programming software development",
                "seniority": "senior"
            }
        }
    ]
    
    for i in range(count):
        # Alternar entre cenários para simular variação de performance
        scenario = performance_scenarios[i % len(performance_scenarios)]
        
        try:
            response = requests.post(f"{API_URL}/predict", json=scenario, timeout=10)
            if response.status_code == 200:
                if (i + 1) % 5 == 0:
                    print(f"  📊 {i + 1}/{count} processadas")
            else:
                print(f"  ⚠️ Erro na amostra {i + 1}")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
        
        time.sleep(DELAY_BETWEEN_REQUESTS * 0.5)  # Mais rápido para performance
    
    print("✅ Dados de performance enviados")

def check_drift_status():
    """Verifica o status atual do drift"""
    try:
        response = requests.get(f"{API_URL}/drift/status")
        if response.status_code == 200:
            status = response.json()
            print(f"\n📊 STATUS DO DRIFT DETECTION:")
            print(f"  - Features monitoradas: {status.get('features_monitored', 0)}")
            print(f"  - Total execuções: {status.get('total_executions', 0)}")
            print(f"  - Accuracy atual: {status.get('current_accuracy', 0):.3f}")
        
        # Verificar alertas
        response = requests.get(f"{API_URL}/drift/alerts")
        if response.status_code == 200:
            alerts = response.json()
            print(f"  - Total de alertas: {len(alerts)}")
            if alerts:
                last_alert = alerts[-1]
                print(f"  - Último alerta: {last_alert.get('type', 'N/A')} - {last_alert.get('message', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")

def main():
    """Função principal"""
    print("🎯 TESTE RÁPIDO DE DRIFT DETECTION")
    print("=" * 50)
    
    # Verificar conexão
    if not test_api_connection():
        return
    
    # Inicializar sistema
    initialize_drift_system()
    
    print("\n📊 INSTRUÇÕES:")
    print("1. Abra http://localhost:3000 no navegador")
    print("2. Navegue até 'Fase5 - Dashboard'")
    print("3. Role até a seção '6. Drift Detection'")
    print("4. Observe os painéis durante a execução")
    
    input("\n⏱️ Pressione ENTER para iniciar o teste...")
    
    # Executar cenários
    print("\n🚀 INICIANDO TESTE DE DRIFT...")
    
    # 1. Dados normais
    send_normal_data(20)
    print("\n⏱️ Aguarde 5 segundos para observar o dashboard...")
    time.sleep(5)
    
    # 2. Dados com drift
    send_drift_data(15)
    print("\n⏱️ Aguarde 5 segundos para observar o dashboard...")
    time.sleep(5)
    
    # 3. Dados de performance do modelo
    send_performance_data(15)
    print("\n⏱️ Aguarde 5 segundos para observar o dashboard...")
    time.sleep(5)
    
    # 4. Dados extremos
    send_extreme_drift_data(10)
    print("\n⏱️ Aguarde 5 segundos para observar o dashboard...")
    time.sleep(5)
    
    # Status final
    check_drift_status()
    
    print("\n🎉 TESTE CONCLUÍDO!")
    print("=" * 50)
    print("📊 Verifique o dashboard para ver:")
    print("  - Alertas de drift detection")
    print("  - Métricas de performance")
    print("  - Execuções de monitoramento")
    print("\n💡 Execute novamente para gerar mais dados!")

if __name__ == "__main__":
    main()
