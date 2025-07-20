#!/usr/bin/env python3
"""
Script para Forçar Dados de Latência com Timestamps Distribuídos
===============================================================

Este script gera dados de latência com intervalos maiores para
garantir que o rate() do Prometheus funcione corretamente.
"""

import requests
import time
import random

API_URL = "http://localhost:8080"

def generate_spaced_requests():
    """Gera requisições com espaçamento específico para o rate() funcionar"""
    print("🔄 Gerando dados de latência com timestamps distribuídos...")
    
    scenarios = [
        {"candidate": {"skills": "python", "experience": "3 anos"}, 
         "vacancy": {"requirements": "python", "seniority": "pleno"}},
        {"candidate": {"skills": "java", "experience": "5 anos"}, 
         "vacancy": {"requirements": "java", "seniority": "senior"}},
        {"candidate": {"skills": "javascript", "experience": "2 anos"}, 
         "vacancy": {"requirements": "react", "seniority": "junior"}}
    ]
    
    # Fazer 3 lotes de requisições com 1 minuto de intervalo
    for lote in range(3):
        print(f"\n📊 Lote {lote + 1}/3:")
        
        # 20 requisições rápidas
        for i in range(20):
            data = random.choice(scenarios)
            try:
                response = requests.post(f"{API_URL}/predict", json=data, timeout=10)
                if response.status_code == 200:
                    if (i + 1) % 5 == 0:
                        print(f"  ✅ {i + 1}/20 processadas")
                else:
                    print(f"  ⚠️ Erro: {response.status_code}")
            except Exception as e:
                print(f"  ❌ Erro: {e}")
            
            time.sleep(0.1)  # 100ms entre requisições
        
        if lote < 2:  # Não esperar após o último lote
            print(f"  ⏱️ Aguardando 70 segundos antes do próximo lote...")
            time.sleep(70)  # 70 segundos para garantir timestamps diferentes
    
    print("\n✅ Dados de latência gerados com timestamps distribuídos!")

if __name__ == "__main__":
    print("🎯 GERADOR DE LATÊNCIA COM TIMESTAMPS DISTRIBUÍDOS")
    print("=" * 60)
    print("Este script gerará dados em lotes espaçados para ativar o rate().")
    print("Tempo total estimado: ~3 minutos")
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
    generate_spaced_requests()
    
    print("\n🎉 CONCLUÍDO!")
    print("=" * 60)
    print("Agora aguarde 2-3 minutos e verifique o painel de latência.")
    print("O Prometheus precisa de alguns pontos de dados para calcular o rate().")
