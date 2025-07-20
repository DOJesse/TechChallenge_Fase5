#!/usr/bin/env python3
"""
Demo Script para Testar Drift Detection no Dashboard
====================================================

Este script demonstra o sistema de drift detection criando cenários
controlados de drift de dados e concept drift que serão visíveis
no dashboard do Grafana.

Uso:
    python demo_drift_dashboard.py [cenario]
    
Cenários disponíveis:
    - baseline: Dados normais sem drift
    - data_drift: Simula drift nos dados de entrada
    - concept_drift: Simula degradação na performance do modelo
    - extreme_drift: Cenário extremo com ambos os tipos de drift
    - demo_completa: Executa todos os cenários em sequência
"""

import requests
import numpy as np
import pandas as pd
import time
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import argparse


class DriftDemoController:
    """Controlador para demonstração de drift detection"""
    
    def __init__(self, api_base_url: str = "http://localhost:8080"):
        self.api_base_url = api_base_url
        self.session = requests.Session()
        
    def check_api_health(self) -> bool:
        """Verifica se a API está rodando"""
        try:
            response = self.session.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API está ativa e respondendo")
                return True
            else:
                print(f"❌ API retornou status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao conectar com a API: {e}")
            print("💡 Certifique-se de que a API está rodando em http://localhost:8080")
            return False
    
    def initialize_drift_detection(self) -> bool:
        """Inicializa o sistema de drift detection"""
        try:
            response = self.session.post(f"{self.api_base_url}/drift/initialize")
            if response.status_code == 200:
                print("✅ Sistema de drift detection inicializado")
                return True
            else:
                print(f"❌ Erro ao inicializar drift detection: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao inicializar drift detection: {e}")
            return False
    
    def generate_baseline_data(self, n_samples: int = 50) -> List[Dict[str, Any]]:
        """Gera dados baseline (sem drift)"""
        np.random.seed(42)
        data = []
        
        for i in range(n_samples):
            sample = {
                "idade": np.random.normal(35, 10),
                "salario": np.random.normal(50000, 15000),
                "experiencia": np.random.normal(8, 4),
                "score_credito": np.random.normal(700, 100),
                "educacao": np.random.choice([0, 1, 2, 3], p=[0.2, 0.3, 0.3, 0.2])
            }
            data.append(sample)
        
        return data
    
    def generate_data_drift_samples(self, n_samples: int = 30) -> List[Dict[str, Any]]:
        """Gera dados com drift (distribuições diferentes)"""
        data = []
        
        for i in range(n_samples):
            # Simula mudança nas distribuições
            sample = {
                "idade": np.random.normal(45, 15),  # Idade média maior
                "salario": np.random.normal(70000, 25000),  # Salários maiores
                "experiencia": np.random.normal(12, 6),  # Mais experiência
                "score_credito": np.random.normal(650, 120),  # Score menor
                "educacao": np.random.choice([0, 1, 2, 3], p=[0.1, 0.2, 0.4, 0.3])  # Mais educação
            }
            data.append(sample)
        
        return data
    
    def generate_extreme_drift_samples(self, n_samples: int = 20) -> List[Dict[str, Any]]:
        """Gera dados com drift extremo"""
        data = []
        
        for i in range(n_samples):
            # Drift muito acentuado
            sample = {
                "idade": np.random.normal(25, 5),  # Muito jovens
                "salario": np.random.normal(30000, 8000),  # Salários baixos
                "experiencia": np.random.normal(2, 1),  # Pouca experiência
                "score_credito": np.random.normal(550, 80),  # Score muito baixo
                "educacao": np.random.choice([0, 1, 2, 3], p=[0.6, 0.3, 0.1, 0.0])  # Baixa educação
            }
            data.append(sample)
        
        return data
    
    def send_prediction_requests(self, data_samples: List[Dict[str, Any]], 
                               scenario_name: str, delay: float = 0.5) -> None:
        """Envia requests de predição para a API"""
        print(f"\n🚀 Enviando {len(data_samples)} amostras para cenário: {scenario_name}")
        
        success_count = 0
        error_count = 0
        
        for i, sample in enumerate(data_samples):
            try:
                response = self.session.post(
                    f"{self.api_base_url}/predict",
                    json=sample,
                    timeout=10
                )
                
                if response.status_code == 200:
                    success_count += 1
                    if (i + 1) % 10 == 0:
                        print(f"  📊 Processadas {i + 1}/{len(data_samples)} amostras")
                else:
                    error_count += 1
                    print(f"  ⚠️ Erro na amostra {i + 1}: {response.status_code}")
                
                time.sleep(delay)
                
            except requests.exceptions.RequestException as e:
                error_count += 1
                print(f"  ❌ Erro de conexão na amostra {i + 1}: {e}")
        
        print(f"✅ Cenário '{scenario_name}' concluído:")
        print(f"  - Sucessos: {success_count}")
        print(f"  - Erros: {error_count}")
    
    def get_drift_status(self) -> Dict[str, Any]:
        """Obtém o status atual do drift detection"""
        try:
            response = self.session.get(f"{self.api_base_url}/drift/status")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao obter status: {response.status_code}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao obter status: {e}")
            return {}
    
    def get_drift_alerts(self) -> List[Dict[str, Any]]:
        """Obtém os alertas de drift"""
        try:
            response = self.session.get(f"{self.api_base_url}/drift/alerts")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao obter alertas: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao obter alertas: {e}")
            return []
    
    def print_drift_summary(self) -> None:
        """Imprime resumo do status de drift"""
        print("\n" + "="*60)
        print("📊 RESUMO DO STATUS DE DRIFT DETECTION")
        print("="*60)
        
        status = self.get_drift_status()
        if status:
            print(f"🔍 Features analisadas: {status.get('features_monitored', 0)}")
            print(f"⚡ Total de execuções: {status.get('total_executions', 0)}")
            print(f"📈 Última accuracy: {status.get('current_accuracy', 0):.3f}")
            
        alerts = self.get_drift_alerts()
        if alerts:
            print(f"\n🚨 ALERTAS DE DRIFT ({len(alerts)} total):")
            for alert in alerts[-5:]:  # Últimos 5 alertas
                timestamp = alert.get('timestamp', 'N/A')
                alert_type = alert.get('type', 'N/A')
                message = alert.get('message', 'N/A')
                print(f"  - [{timestamp}] {alert_type}: {message}")
        else:
            print("\n✅ Nenhum alerta de drift encontrado")
    
    def run_baseline_scenario(self) -> None:
        """Executa cenário baseline (sem drift)"""
        print("\n" + "="*60)
        print("🟢 CENÁRIO 1: BASELINE (SEM DRIFT)")
        print("="*60)
        print("Simulando condições normais de operação...")
        
        baseline_data = self.generate_baseline_data(50)
        self.send_prediction_requests(baseline_data, "Baseline", delay=0.3)
    
    def run_data_drift_scenario(self) -> None:
        """Executa cenário de data drift"""
        print("\n" + "="*60)
        print("🟡 CENÁRIO 2: DATA DRIFT")
        print("="*60)
        print("Simulando mudança na distribuição dos dados de entrada...")
        
        drift_data = self.generate_data_drift_samples(30)
        self.send_prediction_requests(drift_data, "Data Drift", delay=0.4)
    
    def run_concept_drift_scenario(self) -> None:
        """Executa cenário de concept drift"""
        print("\n" + "="*60)
        print("🟠 CENÁRIO 3: CONCEPT DRIFT")
        print("="*60)
        print("Simulando degradação na performance do modelo...")
        
        # Gera dados que causarão predições incorretas
        concept_drift_data = []
        for i in range(25):
            sample = {
                "idade": np.random.normal(40, 8),
                "salario": np.random.normal(45000, 12000),
                "experiencia": np.random.normal(6, 3),
                "score_credito": np.random.normal(600, 90),
                "educacao": np.random.choice([0, 1, 2, 3], p=[0.3, 0.4, 0.2, 0.1])
            }
            concept_drift_data.append(sample)
        
        self.send_prediction_requests(concept_drift_data, "Concept Drift", delay=0.5)
    
    def run_extreme_drift_scenario(self) -> None:
        """Executa cenário de drift extremo"""
        print("\n" + "="*60)
        print("🔴 CENÁRIO 4: DRIFT EXTREMO")
        print("="*60)
        print("Simulando drift severo nos dados...")
        
        extreme_data = self.generate_extreme_drift_samples(20)
        self.send_prediction_requests(extreme_data, "Drift Extremo", delay=0.6)
    
    def run_full_demo(self) -> None:
        """Executa demonstração completa"""
        print("\n" + "🎭"*20)
        print("🎯 DEMONSTRAÇÃO COMPLETA DE DRIFT DETECTION")
        print("🎭"*20)
        print(f"Iniciando demonstração às {datetime.now().strftime('%H:%M:%S')}")
        
        scenarios = [
            ("Baseline", self.run_baseline_scenario),
            ("Data Drift", self.run_data_drift_scenario),
            ("Concept Drift", self.run_concept_drift_scenario),
            ("Drift Extremo", self.run_extreme_drift_scenario)
        ]
        
        for i, (name, scenario_func) in enumerate(scenarios, 1):
            scenario_func()
            
            # Pausa entre cenários para observar mudanças no dashboard
            if i < len(scenarios):
                print(f"\n⏱️ Aguardando 10 segundos antes do próximo cenário...")
                print("💡 Observe as mudanças no dashboard durante este período!")
                time.sleep(10)
        
        # Resumo final
        time.sleep(5)
        self.print_drift_summary()
        
        print("\n" + "🎉"*20)
        print("✅ DEMONSTRAÇÃO CONCLUÍDA!")
        print("🎉"*20)
        print("📊 Verifique o dashboard do Grafana para ver:")
        print("  - Alertas de drift detection")
        print("  - Métricas de performance")
        print("  - Gráficos de execução de monitoramento")
        print("  - Features analisadas")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Demo de Drift Detection Dashboard")
    parser.add_argument(
        "cenario", 
        nargs="?", 
        default="demo_completa",
        choices=["baseline", "data_drift", "concept_drift", "extreme_drift", "demo_completa"],
        help="Cenário a ser executado"
    )
    parser.add_argument(
        "--api-url", 
        default="http://localhost:8080",
        help="URL da API (padrão: http://localhost:8080)"
    )
    
    args = parser.parse_args()
    
    print("🚀 DEMO DE DRIFT DETECTION DASHBOARD")
    print("="*50)
    
    # Inicializa o controlador
    demo = DriftDemoController(args.api_url)
    
    # Verifica se a API está ativa
    if not demo.check_api_health():
        print("\n💡 Para iniciar a API, execute:")
        print("   cd /caminho/para/projeto")
        print("   python src/app/main.py")
        sys.exit(1)
    
    # Inicializa o drift detection
    if not demo.initialize_drift_detection():
        print("❌ Falha ao inicializar drift detection")
        sys.exit(1)
    
    # Executa o cenário selecionado
    scenario_map = {
        "baseline": demo.run_baseline_scenario,
        "data_drift": demo.run_data_drift_scenario,
        "concept_drift": demo.run_concept_drift_scenario,
        "extreme_drift": demo.run_extreme_drift_scenario,
        "demo_completa": demo.run_full_demo
    }
    
    scenario_func = scenario_map[args.cenario]
    scenario_func()
    
    # Status final
    if args.cenario != "demo_completa":
        time.sleep(3)
        demo.print_drift_summary()
    
    print(f"\n🎯 Cenário '{args.cenario}' executado com sucesso!")
    print("📊 Verifique o dashboard em: http://localhost:3000")


if __name__ == "__main__":
    main()
