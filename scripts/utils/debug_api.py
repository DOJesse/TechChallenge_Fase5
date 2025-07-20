#!/usr/bin/env python3
"""
Debug Script - Verificar Status da API
"""

import requests
import time
import sys

def check_api_status():
    """Verifica detalhadamente o status da API"""
    
    print("🔍 DIAGNÓSTICO DA API")
    print("=" * 40)
    
    # Tentar diferentes portas
    ports = [5000, 8000, 8080, 3000]
    
    for port in ports:
        url = f"http://localhost:{port}/health"
        print(f"\n🌐 Testando porta {port}...")
        
        try:
            response = requests.get(url, timeout=3)
            print(f"✅ Porta {port}: ATIVA - Status {response.status_code}")
            print(f"   Resposta: {response.text}")
            return port
        except requests.exceptions.ConnectRefused:
            print(f"❌ Porta {port}: Conexão recusada")
        except requests.exceptions.Timeout:
            print(f"⏱️ Porta {port}: Timeout")
        except Exception as e:
            print(f"❌ Porta {port}: Erro - {e}")
    
    print("\n❌ Nenhuma API encontrada nas portas testadas")
    return None

def test_endpoints(port):
    """Testa endpoints específicos"""
    base_url = f"http://localhost:{port}"
    
    endpoints = [
        "/health",
        "/metrics", 
        "/drift/status",
        "/drift/alerts",
    ]
    
    print(f"\n🧪 TESTANDO ENDPOINTS NA PORTA {port}")
    print("=" * 50)
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

def test_predict_endpoint(port):
    """Testa o endpoint de predição"""
    url = f"http://localhost:{port}/predict"
    
    # Teste 1: Formato antigo (esperado pelo endpoint atual)
    test_data_old = {
        "candidate": {
            "idade": 30,
            "salario": 50000,
            "experiencia": 5,
            "score_credito": 700,
            "educacao": 2
        },
        "vacancy": {
            "some": "data"
        }
    }
    
    # Teste 2: Formato novo (para drift detection)
    test_data_new = {
        "idade": 30,
        "salario": 50000,
        "experiencia": 5,
        "score_credito": 700,
        "educacao": 2
    }
    
    print(f"\n🎯 TESTANDO ENDPOINT /predict NA PORTA {port}")
    print("=" * 55)
    
    # Teste formato antigo
    print("📝 Teste 1: Formato antigo (candidate/vacancy)")
    try:
        response = requests.post(url, json=test_data_old, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Teste formato novo
    print("\n📝 Teste 2: Formato novo (dados diretos)")
    try:
        response = requests.post(url, json=test_data_new, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def main():
    print("🚀 DIAGNÓSTICO COMPLETO DA API")
    print("=" * 50)
    
    # Encontrar a porta da API
    active_port = check_api_status()
    
    if active_port:
        test_endpoints(active_port)
        test_predict_endpoint(active_port)
        
        print(f"\n🎉 API ENCONTRADA NA PORTA {active_port}")
        print("=" * 50)
        print("💡 Use este comando para testar:")
        print(f"   curl http://localhost:{active_port}/health")
    else:
        print("\n💡 COMO INICIAR A API:")
        print("=" * 30)
        print("1. cd /home/diogo/Fase5/TechChallenge_Fase5")
        print("2. python src/app/main.py")
        print("3. Aguarde 'Running on http://0.0.0.0:5000'")

if __name__ == "__main__":
    main()
