#!/usr/bin/env python3
"""
Script para testar e demonstrar o Drift Detection da Decision

Este script executa testes básicos do sistema de drift detection
e simula cenários reais de uso na produção.
"""

import sys
import os
import time
import json
from datetime import datetime

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_functionality():
    """Teste básico de funcionalidade"""
    print("🧪 Testando funcionalidade básica do Drift Detection...")
    
    try:
        import numpy as np
        from src.monitoring.drift_detection import DriftMonitor
        
        # Configurar monitor
        baseline_performance = {
            'accuracy': 0.85,
            'precision': 0.82,
            'recall': 0.80
        }
        
        monitor = DriftMonitor(baseline_performance=baseline_performance)
        print("✅ DriftMonitor inicializado com sucesso")
        
        # Inicializar dados de referência
        reference_data = {
            'candidate_skills_length': np.random.normal(50, 15, 500),
            'candidate_experience_length': np.random.normal(30, 10, 500),
            'vacancy_requirements_length': np.random.normal(40, 12, 500),
            'prediction_value': np.random.beta(2, 2, 500),
            'prediction_confidence': np.random.beta(3, 2, 500)
        }
        
        monitor.initialize_reference_data(reference_data)
        print("✅ Dados de referência inicializados")
        
        return monitor
        
    except ImportError as e:
        print(f"⚠️  Dependências não instaladas: {e}")
        print("💡 Execute: pip install numpy pandas scikit-learn scipy")
        return None
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return None

def simulate_normal_operation(monitor, num_predictions=50):
    """Simula operação normal sem drift"""
    print(f"\n📊 Simulando {num_predictions} predições normais...")
    
    import numpy as np
    
    alerts_count = 0
    
    for i in range(num_predictions):
        # Simular features similares aos dados de referência
        features = {
            'candidate_skills_length': np.random.normal(50, 15),
            'candidate_experience_length': np.random.normal(30, 10),
            'vacancy_requirements_length': np.random.normal(40, 12),
            'prediction_value': np.random.beta(2, 2),
            'prediction_confidence': np.random.beta(3, 2)
        }
        
        # Simular labels para concept drift
        y_true = 1 if np.random.random() > 0.3 else 0
        y_pred = 1 if features['prediction_value'] > 0.5 else 0
        y_pred_proba = features['prediction_value']
        
        result = monitor.monitor_prediction(
            features=features,
            y_true=y_true,
            y_pred=y_pred,
            y_pred_proba=y_pred_proba
        )
        
        if result.get('alerts'):
            alerts_count += len(result['alerts'])
    
    print(f"✅ Operação normal concluída - {alerts_count} alertas gerados")
    return alerts_count

def simulate_data_drift(monitor, num_predictions=30):
    """Simula data drift (mudança na distribuição dos dados)"""
    print(f"\n🚨 Simulando data drift com {num_predictions} predições...")
    
    import numpy as np
    
    alerts_count = 0
    
    for i in range(num_predictions):
        # Simular features com distribuição alterada (data drift)
        features = {
            'candidate_skills_length': np.random.normal(80, 20),  # Média muito maior
            'candidate_experience_length': np.random.normal(15, 5),  # Média menor
            'vacancy_requirements_length': np.random.normal(70, 20),  # Média maior
            'prediction_value': np.random.beta(1, 4),  # Distribuição alterada
            'prediction_confidence': np.random.beta(1, 3)  # Distribuição alterada
        }
        
        y_true = 1 if np.random.random() > 0.3 else 0
        y_pred = 1 if features['prediction_value'] > 0.5 else 0
        y_pred_proba = features['prediction_value']
        
        result = monitor.monitor_prediction(
            features=features,
            y_true=y_true,
            y_pred=y_pred,
            y_pred_proba=y_pred_proba
        )
        
        if result.get('alerts'):
            alerts_count += len(result['alerts'])
            
        # Adicionar dados suficientes para detecção
        if i > 20:  # Após acumular dados suficientes
            try:
                # Forçar detecção de drift com dados acumulados
                current_data = {key: np.array([features[key]]) for key in features.keys()}
                drift_result = monitor.data_drift_detector.detect_drift(current_data)
                if drift_result.get('drift_detected'):
                    print(f"🔥 Data drift detectado! Features afetadas: {drift_result['features_with_drift']}")
            except:
                pass
    
    print(f"✅ Simulação de data drift concluída - {alerts_count} alertas gerados")
    return alerts_count

def simulate_concept_drift(monitor, num_predictions=30):
    """Simula concept drift (degradação da performance do modelo)"""
    print(f"\n📉 Simulando concept drift com {num_predictions} predições...")
    
    import numpy as np
    
    alerts_count = 0
    
    for i in range(num_predictions):
        # Simular features normais
        features = {
            'candidate_skills_length': np.random.normal(50, 15),
            'candidate_experience_length': np.random.normal(30, 10),
            'vacancy_requirements_length': np.random.normal(40, 12),
            'prediction_value': np.random.beta(2, 2),
            'prediction_confidence': np.random.beta(3, 2)
        }
        
        # Simular degradação da performance (predições erradas)
        y_true = 1 if np.random.random() > 0.3 else 0
        
        # Força predições erradas para simular concept drift
        if np.random.random() < 0.7:  # 70% de erro
            y_pred = 1 - y_true  # Predição oposta
        else:
            y_pred = y_true
        
        y_pred_proba = features['prediction_value']
        
        result = monitor.monitor_prediction(
            features=features,
            y_true=y_true,
            y_pred=y_pred,
            y_pred_proba=y_pred_proba
        )
        
        if result.get('alerts'):
            alerts_count += len(result['alerts'])
            
        # Verificar se concept drift foi detectado
        if result.get('concept_drift', {}).get('drift_results', {}).get('concept_drift_detected'):
            print(f"📊 Concept drift detectado! Performance degradada")
    
    print(f"✅ Simulação de concept drift concluída - {alerts_count} alertas gerados")
    return alerts_count

def generate_report(monitor):
    """Gera relatório final de drift detection"""
    print("\n📋 Gerando relatório de drift detection...")
    
    try:
        summary = monitor.get_drift_summary()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'monitoring_status': 'active' if summary['monitoring_active'] else 'inactive',
            'total_data_drift_alerts': summary['data_drift_alerts'],
            'total_concept_drift_alerts': summary['concept_drift_alerts'],
            'performance_history_size': summary['performance_history_size'],
            'recent_alerts': {
                'data_drift': [
                    {
                        'timestamp': alert.timestamp.isoformat(),
                        'severity': alert.severity,
                        'metric': alert.metric,
                        'message': alert.message
                    }
                    for alert in summary['last_data_drift_alerts']
                ],
                'concept_drift': [
                    {
                        'timestamp': alert.timestamp.isoformat(),
                        'severity': alert.severity,
                        'metric': alert.metric,
                        'message': alert.message
                    }
                    for alert in summary['last_concept_drift_alerts']
                ]
            }
        }
        
        # Salvar relatório
        report_file = 'drift_detection_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"✅ Relatório salvo em: {report_file}")
        
        # Exportar alertas
        monitor.export_alerts('drift_alerts.json')
        print("✅ Alertas exportados em: drift_alerts.json")
        
        # Resumo no console
        print(f"\n📊 RESUMO DO TESTE:")
        print(f"  • Status: {report['monitoring_status']}")
        print(f"  • Data Drift Alerts: {report['total_data_drift_alerts']}")
        print(f"  • Concept Drift Alerts: {report['total_concept_drift_alerts']}")
        print(f"  • Histórico de Performance: {report['performance_history_size']} entradas")
        
        return report
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        return None

def main():
    """Função principal do teste"""
    print("🚀 TESTE DE DRIFT DETECTION - DECISION ML SYSTEM")
    print("=" * 50)
    
    # Teste básico
    monitor = test_basic_functionality()
    if not monitor:
        return
    
    # Simular cenários
    normal_alerts = simulate_normal_operation(monitor, 50)
    data_drift_alerts = simulate_data_drift(monitor, 30)
    concept_drift_alerts = simulate_concept_drift(monitor, 30)
    
    # Relatório final
    report = generate_report(monitor)
    
    # Conclusão
    print(f"\n🎯 TESTE CONCLUÍDO!")
    print(f"  • Operação Normal: {normal_alerts} alertas")
    print(f"  • Data Drift: {data_drift_alerts} alertas")
    print(f"  • Concept Drift: {concept_drift_alerts} alertas")
    
    if report:
        total_alerts = report['total_data_drift_alerts'] + report['total_concept_drift_alerts']
        print(f"  • Total de Alertas: {total_alerts}")
        
        if total_alerts > 0:
            print("✅ Sistema de drift detection está funcionando!")
        else:
            print("⚠️  Poucos alertas gerados - ajustar thresholds se necessário")
    
    print("\n💡 Próximos passos:")
    print("  1. Integrar com Flask API (/drift/status, /drift/alerts)")
    print("  2. Configurar Grafana dashboard para visualizar alertas")
    print("  3. Ajustar thresholds baseado em dados de produção")
    print("  4. Implementar ações automáticas quando drift for detectado")

if __name__ == "__main__":
    main()
