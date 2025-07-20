#!/usr/bin/env python3
"""
Script para testar os endpoints de drift detection da API
"""

import requests
import json
import time
import sys

def test_drift_endpoints():
    """Teste dos endpoints de drift detection"""
    
    print("🔧 Testando endpoints de Drift Detection...")
    base_url = "http://localhost:8080"
    
    # 1. Testar status do drift detection
    print("\n1️⃣ Testando GET /drift/status")
    try:
        response = requests.get(f"{base_url}/drift/status")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Drift monitoring habilitado: {data.get('drift_monitoring_enabled')}")
            print(f"📊 Summary: {data.get('summary', {})}")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False
    
    # 2. Inicializar dados de referência
    print("\n2️⃣ Testando POST /drift/initialize")
    try:
        response = requests.post(f"{base_url}/drift/initialize")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Inicializado: {data.get('success')}")
            print(f"📊 Features: {data.get('features_count')}")
            print(f"📊 Amostras por feature: {data.get('samples_per_feature')}")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    # 3. Fazer algumas predições para gerar dados
    print("\n3️⃣ Testando predições com drift monitoring")
    predictions = [
        {
            "candidate": {"skills": "python machine learning", "experience": "3 anos"},
            "vacancy": {"requirements": "python flask ml", "seniority": "pleno"}
        },
        {
            "candidate": {"skills": "java spring boot", "experience": "5 anos"},
            "vacancy": {"requirements": "java microservices", "seniority": "senior"}
        },
        {
            "candidate": {"skills": "react javascript", "experience": "2 anos"},
            "vacancy": {"requirements": "react node.js", "seniority": "junior"}
        }
    ]
    
    for i, prediction_data in enumerate(predictions):
        try:
            response = requests.post(f"{base_url}/predict", json=prediction_data)
            if response.status_code == 200:
                data = response.json()
                drift_alerts = data.get('drift_alerts', 0)
                print(f"✅ Predição {i+1}: {data.get('prediction'):.3f}, Drift alerts: {drift_alerts}")
            else:
                print(f"❌ Erro na predição {i+1}: {response.text}")
        except Exception as e:
            print(f"❌ Erro na predição {i+1}: {e}")
    
    # 4. Verificar alertas de drift
    print("\n4️⃣ Testando GET /drift/alerts")
    try:
        response = requests.get(f"{base_url}/drift/alerts")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total de alertas: {data.get('total_alerts', 0)}")
            alerts = data.get('alerts', [])
            for alert in alerts[:3]:  # Mostrar apenas 3 primeiros
                print(f"🚨 {alert.get('type')} drift - {alert.get('severity')} - {alert.get('metric')}")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    # 5. Verificar métricas Prometheus
    print("\n5️⃣ Testando GET /metrics (Prometheus)")
    try:
        response = requests.get(f"{base_url}/metrics")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            metrics = response.text
            # Verificar se métricas de drift estão presentes
            if "drift_detection_alerts_total" in metrics:
                print("✅ Métricas de drift detection encontradas")
            else:
                print("⚠️  Métricas de drift detection não encontradas")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n🎯 TESTE DOS ENDPOINTS CONCLUÍDO!")
    return True

def main():
    """Função principal"""
    print("🚀 TESTE DE ENDPOINTS - DRIFT DETECTION API")
    print("=" * 50)
    
    # Verificar se API está rodando
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            print("✅ API está rodando")
        else:
            print("❌ API não está respondendo corretamente")
            return
    except:
        print("❌ API não está rodando em http://localhost:5000")
        print("💡 Inicie a API com: cd src/app && python main.py")
        return
    
    # Executar testes
    test_drift_endpoints()

if __name__ == "__main__":
    main()
