#!/usr/bin/env python3
"""
Script para validar a nova estrutura do projeto
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any


def check_file_exists(filepath: str) -> bool:
    """Verifica se um arquivo existe"""
    return Path(filepath).exists()


def check_directory_exists(dirpath: str) -> bool:
    """Verifica se um diretório existe"""
    return Path(dirpath).is_dir()


def validate_project_structure() -> Dict[str, Any]:
    """Valida a estrutura do projeto"""
    
    base_dir = Path(__file__).parent
    results = {
        "directories": {},
        "files": {},
        "imports": {},
        "overall_status": "unknown"
    }
    
    # Diretórios essenciais
    essential_dirs = [
        "src",
        "src/core",
        "src/services", 
        "src/models",
        "src/features",
        "src/app",
        "tests",
        "tests/unit",
        "tests/integration",
        "reports",
        "docker"
    ]
    
    # Arquivos essenciais
    essential_files = [
        "src/core/config.py",
        "src/core/exceptions.py",
        "src/core/constants.py",
        "src/services/prediction_service.py",
        "src/app/main.py",
        "tests/conftest.py",
        "pytest.ini",
        "generate_test_reports.py",
        "REPORTS.md",
        "RESTRUCTURE_PROPOSAL.md"
    ]
    
    print("🔍 VALIDAÇÃO DA ESTRUTURA DO PROJETO")
    print("=" * 50)
    
    # Verificar diretórios
    print("\n📁 Verificando Diretórios:")
    missing_dirs = []
    for dir_path in essential_dirs:
        full_path = base_dir / dir_path
        exists = check_directory_exists(full_path)
        results["directories"][dir_path] = exists
        status = "✅" if exists else "❌"
        print(f"  {status} {dir_path}")
        if not exists:
            missing_dirs.append(dir_path)
    
    # Verificar arquivos
    print("\n📄 Verificando Arquivos:")
    missing_files = []
    for file_path in essential_files:
        full_path = base_dir / file_path
        exists = check_file_exists(full_path)
        results["files"][file_path] = exists
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
        if not exists:
            missing_files.append(file_path)
    
    # Verificar imports críticos
    print("\n🔄 Verificando Imports:")
    critical_imports = [
        ("src.core.config", "config"),
        ("src.core.exceptions", "TechChallengeException"),
        ("src.services.prediction_service", "PredictionService")
    ]
    
    import_errors = []
    for module_name, object_name in critical_imports:
        try:
            module = __import__(module_name, fromlist=[object_name])
            getattr(module, object_name)
            results["imports"][module_name] = True
            print(f"  ✅ {module_name}.{object_name}")
        except (ImportError, AttributeError) as e:
            results["imports"][module_name] = False
            print(f"  ❌ {module_name}.{object_name} - {e}")
            import_errors.append(f"{module_name}.{object_name}")
    
    # Status geral
    print("\n📊 RESUMO:")
    print(f"  Diretórios: {len(essential_dirs) - len(missing_dirs)}/{len(essential_dirs)}")
    print(f"  Arquivos: {len(essential_files) - len(missing_files)}/{len(essential_files)}")
    print(f"  Imports: {len(critical_imports) - len(import_errors)}/{len(critical_imports)}")
    
    # Determinar status geral
    if not missing_dirs and not missing_files and not import_errors:
        results["overall_status"] = "excellent"
        print(f"\n🎉 Status: EXCELENTE - Estrutura totalmente validada!")
    elif len(missing_dirs) <= 2 and len(missing_files) <= 3 and len(import_errors) <= 1:
        results["overall_status"] = "good"
        print(f"\n✅ Status: BOM - Estrutura funcional com pequenos ajustes necessários")
    elif len(missing_dirs) <= 5 and len(missing_files) <= 7 and len(import_errors) <= 3:
        results["overall_status"] = "needs_work"
        print(f"\n⚠️ Status: PRECISA DE TRABALHO - Algumas melhorias necessárias")
    else:
        results["overall_status"] = "critical"
        print(f"\n❌ Status: CRÍTICO - Reestruturação significativa necessária")
    
    # Sugestões
    if missing_dirs or missing_files or import_errors:
        print("\n🔧 SUGESTÕES DE MELHORIAS:")
        if missing_dirs:
            print("  📁 Criar diretórios faltantes:")
            for dir_path in missing_dirs[:3]:  # Mostrar apenas os 3 primeiros
                print(f"    mkdir -p {dir_path}")
        
        if missing_files:
            print("  📄 Criar arquivos faltantes:")
            for file_path in missing_files[:3]:  # Mostrar apenas os 3 primeiros
                print(f"    touch {file_path}")
        
        if import_errors:
            print("  🔄 Corrigir imports faltantes:")
            for import_error in import_errors[:3]:  # Mostrar apenas os 3 primeiros
                print(f"    Implementar: {import_error}")
    
    return results


def main():
    """Função principal"""
    try:
        # Adicionar diretório src ao path para imports
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        results = validate_project_structure()
        
        # Exit code baseado no status
        exit_codes = {
            "excellent": 0,
            "good": 0, 
            "needs_work": 1,
            "critical": 2
        }
        
        sys.exit(exit_codes.get(results["overall_status"], 1))
        
    except Exception as e:
        print(f"\n💥 ERRO DURANTE VALIDAÇÃO: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
