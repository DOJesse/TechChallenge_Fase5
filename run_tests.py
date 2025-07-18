#!/usr/bin/env python3
"""
Script para executar testes unitários do projeto
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Executa um comando e exibe o resultado"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ SUCESSO")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ FALHOU")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
                
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT - Teste demorou mais que 60 segundos")
        return False
    except Exception as e:
        print(f"💥 ERRO: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando testes do TechChallenge Fase 5")
    
    # Verificar dependências
    print("\n📦 Verificando dependências...")
    dependencies = ['pytest', 'pandas', 'numpy', 'sklearn', 'gensim']
    
    for dep in dependencies:
        result = subprocess.run(f"python3 -c 'import {dep}'", shell=True, capture_output=True)
        if result.returncode == 0:
            print(f"✅ {dep}")
        else:
            print(f"❌ {dep} - NÃO ENCONTRADO")
            return False
    
    # Lista de testes para executar
    tests = [
        ("python3 -m pytest tests/unit/test_utils.py::TestPadronizaTexto -v", 
         "Testes de Padronização de Texto"),
        
        ("python3 -m pytest tests/unit/test_utils.py::TestDocumentVector -v", 
         "Testes de Document Vector"),
        
        ("python3 -m pytest tests/unit/test_utils.py::TestMapearSenioridade -v", 
         "Testes de Mapeamento de Senioridade"),
        
        ("python3 -m pytest tests/unit/test_feature_engineering.py::TestFeatureEngineering::test_text_features_list_exists -v", 
         "Teste de Features de Texto"),
         
        ("python3 -m pytest tests/unit/test_predict.py::TestPredictionPipeline::test_pipeline_initialization -v", 
         "Testes do Pipeline de Predição"),
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for cmd, description in tests:
        if run_command(cmd, description):
            success_count += 1
    
    # Resumo final
    print(f"\n{'='*60}")
    print(f"📊 RESUMO FINAL")
    print(f"{'='*60}")
    print(f"✅ Sucessos: {success_count}/{total_tests}")
    print(f"❌ Falhas: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 TODOS OS TESTES BÁSICOS PASSARAM!")
        return True
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)