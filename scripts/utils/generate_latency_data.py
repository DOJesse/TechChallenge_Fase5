#!/usr/bin/env python3
"""
Script para Gerar Dados de Latência Contínuos
==============================================

Este script gera dados de forma contínua para garantir que
o painel de latência ML funcione corretamente no Grafana.
"""

import requests
import time
import random

API_URL = "http://localhost:8080"

def send_continuous_requests(duration_minutes=2):
    """Envia requisições de forma contínua por alguns minutos"""
    print(f"🔄 Enviando requisições contínuas por {duration_minutes} minutos...")
    
    end_time = time.time() + (duration_minutes * 60)
    count = 0
    
    scenarios = [
        {
            "candidate": {
                "skills": "python machine learning",
                "experience": "3 anos"
            },
            "vacancy": {
                "requirements": "python machine learning",
                "seniority": "pleno"
            }
        },
        {
            "candidate": {
                "skills": "java spring boot",
                "experience": "5 anos"
            },
            "vacancy": {
                "requirements": "java backend",
                "seniority": "senior"
            }
        }
    ]
    
    while time.time() < end_time:
        data = random.choice(scenarios)
        
        try:
            response = requests.post(f"{API_URL}/predict", json=data, timeout=10)
            if response.status_code == 200:
                count += 1
                if count % 10 == 0:
                    print(f"  📊 {count} requisições processadas")
            else:
                print(f"  ⚠️ Erro: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
        
        # Intervalo pequeno entre requisições
        time.sleep(0.5)
    
    print(f"✅ Total processadas: {count}")
    return count

if __name__ == "__main__":
    print("🎯 GERADOR DE DADOS DE LATÊNCIA ML")
    print("=" * 50)
    print("Este script gerará dados contínuos para ativar o painel de latência.")
    print("Mantenha o dashboard aberto em: http://localhost:3000")
    print("")
    
    # Verificar API
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API está ativa")
        else:
            print("❌ API não está respondendo")
            exit(1)
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        exit(1)
    
    # Gerar dados
    total = send_continuous_requests(2)
    
    print("\n🎉 DADOS GERADOS!")
    print("=" * 50)
    print(f"Total de requisições: {total}")
    print("Agora o painel 'Distribuição de Latência ML' deve mostrar dados.")
    print("\n💡 Se ainda não apareceu, aguarde 1-2 minutos e atualize o dashboard.")
