#!/usr/bin/env python3
"""
Script para Forçar Atualização da Performance do Modelo
======================================================

Este script força a atualização da métrica drift_concept_performance_accuracy
para demonstração no dashboard.
"""

import requests
import time
import random

API_URL = "http://localhost:8080"

def force_performance_update():
    """Força atualização da métrica de performance do modelo"""
    print("🎯 FORÇANDO ATUALIZAÇÃO DA PERFORMANCE DO MODELO")
    print("=" * 55)
    
    # Precisamos modificar temporariamente a API para aceitar um endpoint de teste
    # Vamos enviar muitos dados para tentar ativar o concept drift
    
    print("📊 Enviando sequência de dados para ativar concept drift...")
    
    # Sequência de dados que pode disparar concept drift
    data_sequence = []
    
    # Primeira fase: dados "bons" (alta performance esperada)
    for i in range(20):
        data_sequence.append({
            "candidate": {
                "skills": f"python machine learning data science {random.randint(3, 8)} anos",
                "experience": f"{random.randint(3, 8)} anos de experiência em data science"
            },
            "vacancy": {
                "requirements": "python machine learning data science",
                "seniority": "pleno"
            }
        })
    
    # Segunda fase: dados "mistos" (performance média)
    for i in range(15):
        data_sequence.append({
            "candidate": {
                "skills": f"java javascript {random.choice(['python', 'react', 'node'])} {random.randint(2, 5)} anos",
                "experience": f"{random.randint(2, 5)} anos de experiência"
            },
            "vacancy": {
                "requirements": f"{random.choice(['python', 'java', 'javascript'])} desenvolvimento software",
                "seniority": random.choice(["junior", "pleno"])
            }
        })
    
    # Terceira fase: dados "ruins" (baixa performance esperada)
    for i in range(10):
        data_sequence.append({
            "candidate": {
                "skills": f"photoshop design gráfico marketing {random.randint(1, 3)} anos",
                "experience": f"{random.randint(1, 3)} anos de experiência em design"
            },
            "vacancy": {
                "requirements": "python programming software development backend",
                "seniority": "senior"
            }
        })
    
    print(f"📦 Processando {len(data_sequence)} amostras em sequência...")
    
    successful_predictions = 0
    for i, data in enumerate(data_sequence):
        try:
            response = requests.post(f"{API_URL}/predict", json=data, timeout=10)
            if response.status_code == 200:
                successful_predictions += 1
                if (i + 1) % 10 == 0:
                    print(f"  ✅ {i + 1}/{len(data_sequence)} processadas")
            else:
                print(f"  ⚠️ Erro na amostra {i + 1}: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Erro na amostra {i + 1}: {e}")
        
        # Delay muito pequeno para processar rapidamente
        time.sleep(0.05)
    
    print(f"\n✅ {successful_predictions}/{len(data_sequence)} predições bem-sucedidas")
    
    # Verificar se a métrica de performance foi atualizada
    print("\n🔍 Verificando métricas de performance...")
    try:
        response = requests.get(f"{API_URL}/metrics")
        if response.status_code == 200:
            metrics_text = response.text
            
            # Procurar pela métrica de performance
            for line in metrics_text.split('\n'):
                if 'drift_concept_performance_accuracy' in line and not line.startswith('#'):
                    print(f"  📈 {line}")
                elif 'drift_monitoring_executions_total' in line and not line.startswith('#'):
                    print(f"  🔄 {line}")
                elif 'drift_detection_alerts_total' in line and not line.startswith('#') and line.strip():
                    print(f"  🚨 {line}")
        
        # Verificar status do drift
        response = requests.get(f"{API_URL}/drift/status")
        if response.status_code == 200:
            status = response.json()
            print(f"\n📊 Status do sistema:")
            print(f"  - Features monitoradas: {status.get('features_monitored', 'N/A')}")
            print(f"  - Total execuções: {status.get('total_executions', 'N/A')}")
            print(f"  - Accuracy atual: {status.get('current_accuracy', 0):.3f}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar métricas: {e}")
    
    print(f"\n🎯 RESULTADO:")
    print("✅ Sequência de dados processada para ativar concept drift")
    print("✅ Verifique o dashboard em http://localhost:3000")
    print("✅ A métrica 'Performance do Modelo' deve mostrar valores > 0%")
    print("\n💡 Se ainda estiver em 0%, o sistema precisa de mais dados ou labels verdadeiros")

if __name__ == "__main__":
    force_performance_update()
