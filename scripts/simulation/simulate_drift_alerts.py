#!/usr/bin/env python3
"""
Script para Simular Alertas de Drift para Demonstração
=====================================================

Este script acessa diretamente as métricas Prometheus e simula alertas
para demonstrar o funcionamento do dashboard.
"""

import requests
import time
import random

API_URL = "http://localhost:8080"

def trigger_manual_alerts():
    """Trigger manual drift alerts by calling internal metrics endpoint"""
    print("🔧 SIMULANDO ALERTAS DE DRIFT DIRETAMENTE NAS MÉTRICAS")
    print("=" * 60)
    
    # Simular incremento manual das métricas
    # Como não podemos acessar diretamente as métricas Prometheus de fora,
    # vamos fazer várias chamadas de predição para tentar disparar alertas
    
    print("📊 Enviando dados específicos para disparar alertas...")
    
    # Dados que podem causar drift
    extreme_data_samples = [
        {
            "candidate": {
                "skills": "cobol assembly mainframe fortran legacy systems vintage computing",
                "experience": "40 anos de experiência em sistemas legados mainframe"
            },
            "vacancy": {
                "requirements": "python react javascript nodejs modern web development",
                "seniority": "junior"
            }
        },
        {
            "candidate": {
                "skills": "ai artificial intelligence machine learning deep learning neural networks",
                "experience": "1 ano de experiência"
            },
            "vacancy": {
                "requirements": "microsoft excel word powerpoint office",
                "seniority": "especialista"
            }
        },
        {
            "candidate": {
                "skills": "blockchain cryptocurrency bitcoin ethereum smart contracts defi",
                "experience": "6 meses de experiência"
            },
            "vacancy": {
                "requirements": "accounting finance traditional banking",
                "seniority": "senior"
            }
        }
    ]
    
    # Enviar amostras extremas múltiplas vezes
    for round_num in range(5):
        print(f"\n🔄 Rodada {round_num + 1}/5 - Enviando amostras extremas...")
        
        for i, data in enumerate(extreme_data_samples * 3):  # 9 amostras por rodada
            try:
                response = requests.post(f"{API_URL}/predict", json=data, timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ Amostra {i + 1} processada")
                else:
                    print(f"  ⚠️ Erro na amostra {i + 1}: {response.status_code}")
            except Exception as e:
                print(f"  ❌ Erro: {e}")
            
            time.sleep(0.1)  # Delay menor para processar mais rápido
        
        # Verificar se alertas foram gerados
        try:
            response = requests.get(f"{API_URL}/drift/alerts")
            if response.status_code == 200:
                alerts = response.json()
                total_alerts = alerts.get('total_alerts', 0)
                print(f"    📊 Alertas detectados após rodada {round_num + 1}: {total_alerts}")
            else:
                print(f"    ⚠️ Erro ao verificar alertas: {response.status_code}")
        except Exception as e:
            print(f"    ❌ Erro ao verificar alertas: {e}")
        
        time.sleep(2)
    
    print("\n🔍 VERIFICANDO ESTADO FINAL...")
    
    # Verificar métricas finais
    try:
        print("\n📈 Métricas de Drift:")
        response = requests.get(f"{API_URL}/metrics")
        if response.status_code == 200:
            metrics_text = response.text
            
            # Extrair métricas relevantes
            lines = metrics_text.split('\n')
            for line in lines:
                if 'drift_' in line and not line.startswith('#') and line.strip():
                    print(f"  {line}")
        
        print("\n🚨 Alertas:")
        response = requests.get(f"{API_URL}/drift/alerts")
        if response.status_code == 200:
            alerts = response.json()
            print(f"  Total de alertas: {alerts.get('total_alerts', 0)}")
            if alerts.get('alerts'):
                for alert in alerts['alerts'][-3:]:  # Últimos 3 alertas
                    print(f"    - {alert.get('type', 'N/A')}: {alert.get('message', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar estado final: {e}")
    
    print("\n🎯 RESULTADO:")
    print("1. Verifique o dashboard em http://localhost:3000")
    print("2. Navegue até 'Fase5 - Dashboard'")
    print("3. Role até a seção '6. Drift Detection'")
    print("4. As métricas de execução devem estar aumentando")
    print("5. Se os alertas ainda não aparecerem, o problema está na lógica de detecção")

if __name__ == "__main__":
    trigger_manual_alerts()
