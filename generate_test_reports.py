#!/usr/bin/env python3
"""
Script para executar testes e gerar relatórios completos
"""

import os
import sys
import subprocess
from datetime import datetime

def run_command(command, description):
    """Executa um comando e retorna o resultado"""
    print(f"\n🔄 {description}...")
    print(f"Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Sucesso")
            return True
        else:
            print(f"❌ {description} - Falhou")
            print(f"Erro: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Erro: {e}")
        return False

def main():
    """Função principal para gerar relatórios"""
    print("=" * 60)
    print("🧪 GERAÇÃO DE RELATÓRIOS DE TESTE")
    print("=" * 60)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Detectar se estamos em um ambiente virtual
    venv_python = sys.executable
    pytest_cmd = f"{venv_python} -m pytest"
    
    # Criar diretório de relatórios se não existir
    os.makedirs("reports", exist_ok=True)
    
    # 1. Executar testes com cobertura e relatório HTML
    success = run_command(
        f"{pytest_cmd} --html=reports/test_report.html --self-contained-html",
        "Executando testes e gerando relatório HTML"
    )
    
    if not success:
        print("\n❌ Falha na execução dos testes. Abortando...")
        sys.exit(1)
    
    # 2. Gerar relatório de cobertura simples no terminal
    run_command(
        f"{pytest_cmd} --cov=src --cov-report=term-missing --tb=no -q",
        "Gerando relatório de cobertura no terminal"
    )
    
    # 3. Gerar relatório de cobertura HTML
    run_command(
        f"{pytest_cmd} --cov=src --cov-report=html:reports/coverage --tb=no -q",
        "Gerando relatório de cobertura HTML"
    )
    
    # 4. Gerar relatório JUnit XML
    run_command(
        f"{pytest_cmd} --junit-xml=reports/junit.xml --tb=no -q",
        "Gerando relatório JUnit XML"
    )
    
    print("\n" + "=" * 60)
    print("📊 RELATÓRIOS GERADOS:")
    print("=" * 60)
    
    reports = [
        ("Relatório HTML dos Testes", "reports/test_report.html"),
        ("Cobertura HTML", "reports/coverage/index.html"),
        ("Relatório JUnit XML", "reports/junit.xml"),
        ("Cobertura XML", "reports/coverage.xml"),
    ]
    
    for name, path in reports:
        if os.path.exists(path):
            abs_path = os.path.abspath(path)
            print(f"✅ {name}: {abs_path}")
        else:
            print(f"❌ {name}: Não encontrado em {path}")
    
    print("\n🎉 Geração de relatórios concluída!")
    print("\nPara visualizar os relatórios HTML, abra os arquivos em um navegador.")

if __name__ == "__main__":
    main()
