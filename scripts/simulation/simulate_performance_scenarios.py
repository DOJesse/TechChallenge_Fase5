#!/usr/bin/env python3
"""
Script para Simular Performance do Modelo via Endpoint Direto
===========================================================

Este script simula valores de performance diretamente nas métricas.
"""

import requests
import time
import random

API_URL = "http://localhost:8080"

def simulate_performance_directly():
    """Simula performance do modelo usando endpoints da API"""
    print("🎯 SIMULANDO PERFORMANCE DO MODELO DIRETAMENTE")
    print("=" * 55)
    
    # Vamos tentar uma abordagem diferente: criar dados que realmente disparem concept drift
    # com uma simulação de feedback de labels
    
    print("📊 Criando cenário de performance variável...")
    
    # Cenário 1: Performance inicial boa (simular 85% accuracy)
    print("\n🟢 Fase 1: Enviando dados com alta correlação (performance alta)")
    good_performance_data = []
    for i in range(25):
        # Dados bem correlacionados - candidato e vaga combinam bem
        skills = random.choice([
            "python machine learning data science tensorflow",
            "java spring boot microservices backend",
            "javascript react frontend nodejs web",
            "python django flask web development"
        ])
        
        if "python" in skills:
            requirements = "python desenvolvimento software"
        elif "java" in skills:
            requirements = "java backend desenvolvimento"
        elif "javascript" in skills:
            requirements = "javascript frontend desenvolvimento"
        else:
            requirements = "python web desenvolvimento"
        
        data = {
            "candidate": {
                "skills": f"{skills} {random.randint(3, 7)} anos",
                "experience": f"{random.randint(3, 7)} anos de experiência"
            },
            "vacancy": {
                "requirements": requirements,
                "seniority": random.choice(["pleno", "senior"])
            }
        }
        good_performance_data.append(data)
    
    # Processar dados de boa performance
    for i, data in enumerate(good_performance_data):
        try:
            response = requests.post(f"{API_URL}/predict", json=data, timeout=10)
            if response.status_code == 200:
                if (i + 1) % 10 == 0:
                    print(f"  ✅ {i + 1}/{len(good_performance_data)} processadas")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
        time.sleep(0.1)
    
    print("\n⏳ Aguardando processamento...")
    time.sleep(3)
    
    # Cenário 2: Performance degradada (simular 60% accuracy)
    print("\n🟡 Fase 2: Enviando dados com baixa correlação (performance degradada)")
    poor_performance_data = []
    for i in range(20):
        # Dados mal correlacionados - candidato e vaga não combinam
        candidate_skills = random.choice([
            "photoshop design gráfico marketing",
            "excel word powerpoint office",
            "vendas atendimento cliente telemarketing",
            "contabilidade finanças administrativa"
        ])
        
        vacancy_requirements = random.choice([
            "python programming software development",
            "java backend microservices cloud",
            "react javascript frontend development",
            "machine learning data science AI"
        ])
        
        data = {
            "candidate": {
                "skills": f"{candidate_skills} {random.randint(1, 3)} anos",
                "experience": f"{random.randint(1, 3)} anos de experiência"
            },
            "vacancy": {
                "requirements": vacancy_requirements,
                "seniority": random.choice(["senior", "especialista"])
            }
        }
        poor_performance_data.append(data)
    
    # Processar dados de performance ruim
    for i, data in enumerate(poor_performance_data):
        try:
            response = requests.post(f"{API_URL}/predict", json=data, timeout=10)
            if response.status_code == 200:
                if (i + 1) % 10 == 0:
                    print(f"  ✅ {i + 1}/{len(poor_performance_data)} processadas")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
        time.sleep(0.1)
    
    print("\n⏳ Aguardando processamento final...")
    time.sleep(5)
    
    # Verificar métricas finais
    print("\n🔍 VERIFICANDO MÉTRICAS FINAIS...")
    try:
        response = requests.get(f"{API_URL}/metrics")
        if response.status_code == 200:
            metrics_text = response.text
            
            print("📈 Métricas de Drift e Performance:")
            for line in metrics_text.split('\n'):
                if any(metric in line for metric in [
                    'drift_concept_performance_accuracy',
                    'drift_monitoring_executions_total', 
                    'drift_detection_alerts_total'
                ]) and not line.startswith('#') and line.strip():
                    print(f"  {line}")
        
        # Verificar alertas
        response = requests.get(f"{API_URL}/drift/alerts")
        if response.status_code == 200:
            alerts = response.json()
            print(f"\n🚨 Alertas gerados: {alerts.get('total_alerts', 0)}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar métricas: {e}")
    
    print(f"\n🎯 RESULTADO:")
    print("✅ Cenários de performance variável processados")
    print("✅ Dados enviados para tentar ativar concept drift")
    print("📊 Verifique o dashboard em http://localhost:3000")
    print("🎯 Se a performance ainda estiver em 0%, o sistema precisa de labels verdadeiros")

if __name__ == "__main__":
    simulate_performance_directly()
