#!/usr/bin/env python3
"""
Simulador de Ambiente de Produção - 5 Minutos
=============================================

Este script simula um ambiente de produção real com:
- Requisições contínuas por 5 minutos
- 1% de taxa de drift de modelo
- 1% de taxa de erro
- Distribuição realista de dados
"""

import requests
import time
import random
import json
from datetime import datetime, timedelta

# Configuração
API_URL = "http://localhost:8080"
SIMULATION_DURATION = 5 * 60  # 5 minutos em segundos
REQUESTS_PER_MINUTE = 30  # 30 requisições por minuto (produção moderada)
DRIFT_RATE = 0.01  # 1% de drift
ERROR_RATE = 0.03  # 3% de erro (aumentado para garantir erros HTTP visíveis)
HTTP_ERROR_RATE = 0.02  # 2% especificamente para erros HTTP (4xx/5xx)

class ProductionSimulator:
    def __init__(self):
        self.start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.drift_requests = 0
        self.error_requests = 0
        self.http_error_requests = 0  # Contador específico para erros HTTP
        self.forced_http_errors = 0  # Contador para erros HTTP forçados
        self.min_http_errors = 2  # Mínimo de erros HTTP garantidos
        
        # Dados normais de produção (98% dos casos)
        self.normal_scenarios = [
            {
                "candidate": {
                    "skills": "python machine learning pandas numpy scikit-learn",
                    "experience": f"{random.randint(2, 8)} anos de experiência em ciência de dados"
                },
                "vacancy": {
                    "requirements": "python machine learning data science pandas",
                    "seniority": random.choice(["junior", "pleno", "senior"])
                }
            },
            {
                "candidate": {
                    "skills": "java spring boot microservices docker kubernetes",
                    "experience": f"{random.randint(3, 10)} anos como desenvolvedor backend"
                },
                "vacancy": {
                    "requirements": "java spring backend microservices",
                    "seniority": random.choice(["pleno", "senior"])
                }
            },
            {
                "candidate": {
                    "skills": "javascript react nodejs typescript frontend",
                    "experience": f"{random.randint(1, 6)} anos em desenvolvimento frontend"
                },
                "vacancy": {
                    "requirements": "react javascript frontend typescript",
                    "seniority": random.choice(["junior", "pleno"])
                }
            },
            {
                "candidate": {
                    "skills": "python django flask postgresql api rest",
                    "experience": f"{random.randint(2, 7)} anos em desenvolvimento web"
                },
                "vacancy": {
                    "requirements": "python django api rest postgresql",
                    "seniority": random.choice(["pleno", "senior"])
                }
            },
            {
                "candidate": {
                    "skills": "devops aws docker kubernetes terraform ansible",
                    "experience": f"{random.randint(3, 12)} anos em infraestrutura e devops"
                },
                "vacancy": {
                    "requirements": "devops aws kubernetes docker",
                    "seniority": random.choice(["senior", "especialista"])
                }
            }
        ]
        
        # Dados com drift (1% dos casos) - perfis desalinhados
        self.drift_scenarios = [
            {
                "candidate": {
                    "skills": "photoshop illustrator design gráfico marketing digital",
                    "experience": f"{random.randint(1, 4)} anos em design gráfico"
                },
                "vacancy": {
                    "requirements": "python programming machine learning data science",
                    "seniority": "senior"
                }
            },
            {
                "candidate": {
                    "skills": "cobol mainframe legacy systems fortran assembler",
                    "experience": f"{random.randint(15, 30)} anos em sistemas mainframe"
                },
                "vacancy": {
                    "requirements": "react javascript modern frontend frameworks",
                    "seniority": "junior"
                }
            },
            {
                "candidate": {
                    "skills": "vendas telemarketing atendimento cliente call center",
                    "experience": f"{random.randint(1, 5)} anos em vendas"
                },
                "vacancy": {
                    "requirements": "kubernetes devops cloud infrastructure",
                    "seniority": "especialista"
                }
            }
        ]
        
        # Dados que podem causar erro (JSON malformado, campos faltando, etc.)
        self.error_scenarios = [
            # Campo skills vazio
            {
                "candidate": {
                    "skills": "",
                    "experience": "5 anos"
                },
                "vacancy": {
                    "requirements": "python",
                    "seniority": "pleno"
                }
            },
            # Campo experience muito longo (pode causar timeout)
            {
                "candidate": {
                    "skills": "python",
                    "experience": "x" * 1000  # String muito longa
                },
                "vacancy": {
                    "requirements": "python",
                    "seniority": "senior"
                }
            },
            # Seniority inválido
            {
                "candidate": {
                    "skills": "java spring",
                    "experience": "3 anos"
                },
                "vacancy": {
                    "requirements": "java",
                    "seniority": "INVALID_LEVEL"
                }
            }
        ]
        
        # Cenários específicos para erros HTTP (4xx/5xx)
        self.http_error_scenarios = [
            # JSON malformado (400 Bad Request) - GARANTIDO
            {"type": "malformed_json", "data": '{"candidate": {"skills": "python"'},
            {"type": "malformed_json", "data": '{"vacancy": {"requirements": "java"}'},
            {"type": "malformed_json", "data": '{"incomplete": true,'},
            # Dados completamente vazios (400 Bad Request) - GARANTIDO
            {"type": "incomplete_data", "data": {}},
            {"type": "incomplete_data", "data": {"candidate": {}}},
            {"type": "incomplete_data", "data": {"vacancy": {}}},
            # Endpoint inexistente (404 Not Found) - GARANTIDO
            {"type": "wrong_endpoint", "endpoint": "/invalid"},
            {"type": "wrong_endpoint", "endpoint": "/api/predict"},
            {"type": "wrong_endpoint", "endpoint": "/predict/test"},
            {"type": "wrong_endpoint", "endpoint": "/nonexistent"},
            # Método incorreto (405 Method Not Allowed) - GARANTIDO
            {"type": "wrong_method", "method": "DELETE"},
            {"type": "wrong_method", "method": "PUT"},
            {"type": "wrong_method", "method": "PATCH"}
        ]
        
        # Cenários especiais garantidos para forçar erros HTTP
        self.guaranteed_http_errors = [
            # Erro 400 garantido - JSON completamente malformado
            {"type": "malformed_json", "data": '{invalid json syntax'},
            # Erro 404 garantido - endpoint que não existe
            {"type": "wrong_endpoint", "endpoint": "/guaranteed_404_error"}
        ]

    def get_request_data(self):
        """Seleciona o tipo de dados baseado nas taxas configuradas"""
        rand = random.random()
        
        # Forçar erros HTTP se ainda não atingiu o mínimo
        if (self.http_error_requests < self.min_http_errors and 
            self.total_requests > 10):  # Após 10 requisições, começar a forçar
            
            # Se é a 25ª ou 75ª requisição, forçar erro garantido
            if self.total_requests == 25 or self.total_requests == 75:
                self.http_error_requests += 1
                self.forced_http_errors += 1
                return random.choice(self.guaranteed_http_errors), "http_error"
        
        if rand < HTTP_ERROR_RATE:
            # 2% chance de erro HTTP específico (4xx/5xx)
            self.http_error_requests += 1
            return random.choice(self.http_error_scenarios), "http_error"
        elif rand < HTTP_ERROR_RATE + ERROR_RATE:
            # 3% chance de erro de dados/validação
            self.error_requests += 1
            return random.choice(self.error_scenarios), "error"
        elif rand < HTTP_ERROR_RATE + ERROR_RATE + DRIFT_RATE:
            # 1% chance de drift
            self.drift_requests += 1
            return random.choice(self.drift_scenarios), "drift"
        else:
            # ~94% dados normais
            return random.choice(self.normal_scenarios), "normal"

    def send_request(self, data, data_type):
        """Envia uma requisição para a API"""
        try:
            if data_type == "http_error":
                # Cenários específicos para erros HTTP
                error_scenario = data
                
                if error_scenario["type"] == "malformed_json":
                    # JSON malformado (400)
                    response = requests.post(
                        f"{API_URL}/predict", 
                        data=error_scenario["data"],  # String malformada
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                elif error_scenario["type"] == "incomplete_data":
                    # Dados incompletos (400)
                    response = requests.post(f"{API_URL}/predict", json=error_scenario["data"], timeout=10)
                elif error_scenario["type"] == "wrong_endpoint":
                    # Endpoint inexistente (404)
                    response = requests.get(f"{API_URL}{error_scenario['endpoint']}", timeout=10)
                elif error_scenario["type"] == "wrong_method":
                    # Método incorreto (405)
                    response = requests.request(error_scenario["method"], f"{API_URL}/predict", timeout=10)
                elif error_scenario["type"] == "problematic_data":
                    # Dados problemáticos (pode causar 500)
                    response = requests.post(f"{API_URL}/predict", json=error_scenario["data"], timeout=10)
                
                # Para erros HTTP, consideramos sucesso se geramos o erro esperado
                if response.status_code >= 400:
                    return True  # Erro HTTP gerado com sucesso
                else:
                    # Se não gerou erro, conta como requisição normal bem-sucedida
                    self.successful_requests += 1
                    return True
                    
            else:
                # Requisições normais, drift ou erro de dados
                response = requests.post(f"{API_URL}/predict", json=data, timeout=10)
                if response.status_code == 200:
                    self.successful_requests += 1
                    return True
                else:
                    # Erro de servidor/validação - também conta para api_errors_total
                    return False
        except Exception as e:
            # Erro de rede/timeout - também pode gerar métricas de erro
            return False

    def print_statistics(self):
        """Imprime estatísticas em tempo real"""
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
        drift_rate = (self.drift_requests / self.total_requests * 100) if self.total_requests > 0 else 0
        error_rate = (self.error_requests / self.total_requests * 100) if self.total_requests > 0 else 0
        http_error_rate = (self.http_error_requests / self.total_requests * 100) if self.total_requests > 0 else 0
        
        print(f"\r⏱️ {minutes:02d}:{seconds:02d} | "
              f"📊 {self.total_requests} req | "
              f"✅ {success_rate:.1f}% | "
              f"🔄 {drift_rate:.1f}% drift | "
              f"❌ {error_rate:.1f}% erro | "
              f"🚨 {http_error_rate:.1f}% HTTP err", end="", flush=True)

    def run_simulation(self):
        """Executa a simulação completa"""
        print("🎯 SIMULADOR DE AMBIENTE DE PRODUÇÃO")
        print("=" * 60)
        print(f"⏱️ Duração: 5 minutos")
        print(f"📊 Taxa: {REQUESTS_PER_MINUTE} req/min")
        print(f"🔄 Taxa de drift: {DRIFT_RATE*100}%")
        print(f"❌ Taxa de erro de dados: {ERROR_RATE*100}%")
        print(f"🚨 Taxa de erro HTTP: {HTTP_ERROR_RATE*100}%")
        print("")
        
        # Verificar API
        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            if response.status_code != 200:
                print("❌ API não está respondendo")
                return
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return
        
        # Inicializar drift detection
        try:
            requests.post(f"{API_URL}/drift/initialize")
        except:
            pass
        
        print("🚀 Iniciando simulação...")
        print("")
        
        # Intervalo entre requisições (em segundos)
        request_interval = 60.0 / REQUESTS_PER_MINUTE
        
        end_time = self.start_time + SIMULATION_DURATION
        next_request_time = self.start_time
        
        while time.time() < end_time:
            current_time = time.time()
            
            # Verificar se é hora da próxima requisição
            if current_time >= next_request_time:
                self.total_requests += 1
                
                # Selecionar tipo de dados
                data, data_type = self.get_request_data()
                
                # Enviar requisição
                self.send_request(data, data_type)
                
                # Programar próxima requisição
                next_request_time += request_interval
                
                # Mostrar estatísticas a cada 10 requisições
                if self.total_requests % 10 == 0:
                    self.print_statistics()
            
            # Pequena pausa para não sobrecarregar a CPU
            time.sleep(0.1)
        
        # Estatísticas finais
        print("\n")
        print("\n🎉 SIMULAÇÃO CONCLUÍDA!")
        print("=" * 60)
        print(f"📊 Total de requisições: {self.total_requests}")
        print(f"✅ Requisições bem-sucedidas: {self.successful_requests}")
        print(f"🔄 Requisições com drift: {self.drift_requests}")
        print(f"❌ Requisições com erro de dados: {self.error_requests}")
        print(f"� Requisições com erro HTTP: {self.http_error_requests}")
        print(f"�📈 Taxa de sucesso: {(self.successful_requests/self.total_requests*100):.1f}%")
        print(f"📈 Taxa de drift real: {(self.drift_requests/self.total_requests*100):.2f}%")
        print(f"📈 Taxa de erro de dados real: {(self.error_requests/self.total_requests*100):.2f}%")
        print(f"📈 Taxa de erro HTTP real: {(self.http_error_requests/self.total_requests*100):.2f}%")
        print(f"📈 Taxa total de erro: {((self.error_requests + self.http_error_requests)/self.total_requests*100):.2f}%")
        if self.forced_http_errors > 0:
            print(f"🎯 Erros HTTP forçados: {self.forced_http_errors} (garantia mínima)")
        print("")
        print("🎯 Resultados esperados no dashboard:")
        print("  - Alertas de drift: Alguns alertas detectados")
        print("  - Performance do modelo: Variação entre 60-80%")
        print("  - Latência ML: Distribuição realista (100-500ms)")
        print(f"  - Taxa de Erros da API: Deve mostrar ~{HTTP_ERROR_RATE*100}% de erros HTTP")
        print("  - Execuções: ~150 amostras processadas")
        print("")
        print("💡 Para verificar:")
        print("  1. Acesse http://localhost:3000")
        print("  2. Vá para 'Fase5 - Dashboard'")
        print("  3. Seção '6. Drift Detection' - todos os 5 painéis devem ter dados")
        print("  4. Painel 'Taxa de Erros da API' deve mostrar dados consistentes agora")

def main():
    simulator = ProductionSimulator()
    simulator.run_simulation()

if __name__ == "__main__":
    main()
