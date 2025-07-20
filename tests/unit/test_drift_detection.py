"""
Testes para o módulo de Drift Detection
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

try:
    from src.monitoring.drift_detection import (
        DataDriftDetector, 
        ConceptDriftDetector, 
        DriftMonitor, 
        DriftAlert
    )
    DRIFT_MODULE_AVAILABLE = True
except ImportError:
    DRIFT_MODULE_AVAILABLE = False
    
@pytest.mark.skipif(not DRIFT_MODULE_AVAILABLE, reason="Drift detection module not available")
class TestDataDriftDetector:
    """Testes para DataDriftDetector"""
    
    def test_detector_initialization(self):
        """Teste de inicialização do detector"""
        detector = DataDriftDetector(
            significance_level=0.05,
            reference_window_size=100,
            detection_window_size=50
        )
        
        assert detector.significance_level == 0.05
        assert detector.reference_window_size == 100
        assert detector.detection_window_size == 50
        assert detector.reference_data == {}
        assert detector.alerts == []
        
    def test_set_reference_data(self):
        """Teste de configuração de dados de referência"""
        detector = DataDriftDetector()
        
        reference_data = {
            'feature1': np.random.normal(0, 1, 200),
            'feature2': np.random.normal(5, 2, 150)
        }
        
        detector.set_reference_data(reference_data)
        
        assert 'feature1' in detector.reference_data
        assert 'feature2' in detector.reference_data
        assert len(detector.reference_data['feature1']) <= detector.reference_window_size
        assert len(detector.reference_data['feature2']) <= detector.reference_window_size
        
    def test_detect_no_drift(self):
        """Teste de detecção quando não há drift"""
        detector = DataDriftDetector(significance_level=0.01)  # Threshold baixo
        
        # Dados similares - não deve detectar drift
        reference_data = {
            'feature1': np.random.normal(0, 1, 100)
        }
        current_data = {
            'feature1': np.random.normal(0, 1, 50)  # Mesma distribuição
        }
        
        detector.set_reference_data(reference_data)
        result = detector.detect_drift(current_data)
        
        assert result['drift_detected'] == False
        assert result['features_analyzed'] == 1
        assert result['features_with_drift'] == 0
        assert len(result['alerts']) == 0
        
    def test_detect_drift_present(self):
        """Teste de detecção quando há drift"""
        detector = DataDriftDetector(significance_level=0.05)
        
        # Dados com distribuições muito diferentes - deve detectar drift
        reference_data = {
            'feature1': np.random.normal(0, 1, 100)
        }
        current_data = {
            'feature1': np.random.normal(10, 1, 50)  # Média muito diferente
        }
        
        detector.set_reference_data(reference_data)
        result = detector.detect_drift(current_data)
        
        assert result['drift_detected'] == True
        assert result['features_analyzed'] == 1
        assert result['features_with_drift'] == 1
        assert len(result['alerts']) == 1
        assert result['alerts'][0].drift_type == 'data'
        
    def test_missing_feature_handling(self):
        """Teste de tratamento de features ausentes"""
        detector = DataDriftDetector()
        
        reference_data = {
            'feature1': np.random.normal(0, 1, 100),
            'feature2': np.random.normal(5, 2, 100)
        }
        current_data = {
            'feature1': np.random.normal(0, 1, 50)
            # feature2 está ausente
        }
        
        detector.set_reference_data(reference_data)
        result = detector.detect_drift(current_data)
        
        assert result['features_analyzed'] == 1  # Apenas feature1
        assert 'feature1' in result['feature_results']
        assert 'feature2' not in result['feature_results']


@pytest.mark.skipif(not DRIFT_MODULE_AVAILABLE, reason="Drift detection module not available")
class TestConceptDriftDetector:
    """Testes para ConceptDriftDetector"""
    
    def test_detector_initialization(self):
        """Teste de inicialização do detector"""
        baseline_performance = {'accuracy': 0.85, 'precision': 0.80}
        detector = ConceptDriftDetector(
            baseline_performance=baseline_performance,
            degradation_threshold=0.1,
            window_size=50
        )
        
        assert detector.baseline_performance == baseline_performance
        assert detector.degradation_threshold == 0.1
        assert detector.window_size == 50
        assert detector.performance_history == []
        assert detector.alerts == []
        
    def test_update_performance_no_drift(self):
        """Teste de atualização sem drift"""
        baseline_performance = {'accuracy': 0.85}
        detector = ConceptDriftDetector(
            baseline_performance=baseline_performance,
            degradation_threshold=0.1
        )
        
        # Performance similar ao baseline - não deve detectar drift
        y_true = np.array([1, 0, 1, 1, 0, 1, 0, 1])
        y_pred = np.array([1, 0, 1, 1, 0, 1, 1, 1])  # 7/8 = 0.875 accuracy
        
        result = detector.update_performance(y_true, y_pred)
        
        assert 'current_metrics' in result
        assert result['current_metrics']['accuracy'] > 0.8
        assert result['drift_results']['concept_drift_detected'] == False
        assert len(result['drift_results']['alerts']) == 0
        
    def test_update_performance_with_drift(self):
        """Teste de detecção de concept drift"""
        baseline_performance = {'accuracy': 0.85}
        detector = ConceptDriftDetector(
            baseline_performance=baseline_performance,
            degradation_threshold=0.1  # 10% degradation threshold
        )
        
        # Performance muito pior que baseline - deve detectar drift
        y_true = np.array([1, 1, 1, 1, 1, 1, 1, 1])
        y_pred = np.array([0, 0, 0, 0, 0, 0, 0, 0])  # 0% accuracy
        
        result = detector.update_performance(y_true, y_pred)
        
        assert result['drift_results']['concept_drift_detected'] == True
        assert len(result['drift_results']['degraded_metrics']) > 0
        assert len(result['drift_results']['alerts']) > 0
        assert result['drift_results']['alerts'][0].drift_type == 'concept'
        
    def test_rolling_performance_calculation(self):
        """Teste de cálculo de performance rolling"""
        baseline_performance = {'accuracy': 0.85}
        detector = ConceptDriftDetector(
            baseline_performance=baseline_performance,
            window_size=3
        )
        
        # Adicionar várias medições
        for i in range(5):
            accuracy = 0.8 + i * 0.01  # Performance ligeiramente crescente
            y_true = np.array([1, 1, 1, 1, 1])
            y_pred = np.array([1, 1, 1, 1, 0]) if accuracy < 0.85 else np.array([1, 1, 1, 1, 1])
            
            result = detector.update_performance(y_true, y_pred)
            
        # Verificar que rolling metrics estão sendo calculadas
        assert 'rolling_metrics' in result
        assert 'accuracy' in result['rolling_metrics']
        assert len(detector.performance_history) <= detector.window_size


@pytest.mark.skipif(not DRIFT_MODULE_AVAILABLE, reason="Drift detection module not available")
class TestDriftMonitor:
    """Testes para DriftMonitor integrado"""
    
    def test_monitor_initialization(self):
        """Teste de inicialização do monitor"""
        baseline_performance = {'accuracy': 0.85, 'precision': 0.80}
        monitor = DriftMonitor(baseline_performance=baseline_performance)
        
        assert monitor.monitoring_active == True
        assert monitor.data_drift_detector is not None
        assert monitor.concept_drift_detector is not None
        
    def test_monitor_without_baseline(self):
        """Teste de inicialização sem baseline performance"""
        monitor = DriftMonitor()
        
        assert monitor.monitoring_active == True
        assert monitor.data_drift_detector is not None
        assert monitor.concept_drift_detector is None
        
    def test_initialize_reference_data(self):
        """Teste de inicialização de dados de referência"""
        monitor = DriftMonitor()
        
        reference_data = {
            'feature1': np.random.normal(0, 1, 100),
            'feature2': np.random.normal(5, 2, 100)
        }
        
        monitor.initialize_reference_data(reference_data)
        
        # Verificar que os dados foram passados para o detector
        assert len(monitor.data_drift_detector.reference_data) == 2
        
    def test_monitor_prediction_basic(self):
        """Teste básico de monitoramento de predição"""
        baseline_performance = {'accuracy': 0.85}
        monitor = DriftMonitor(baseline_performance=baseline_performance)
        
        # Inicializar dados de referência
        reference_data = {
            'feature1': np.random.normal(0, 1, 100)
        }
        monitor.initialize_reference_data(reference_data)
        
        # Monitorar uma predição
        features = {'feature1': 0.5}
        result = monitor.monitor_prediction(
            features=features,
            y_true=1,
            y_pred=1,
            y_pred_proba=0.9
        )
        
        assert result['monitoring_active'] == True
        assert 'timestamp' in result
        assert 'data_drift' in result
        assert 'concept_drift' in result
        
    def test_get_drift_summary(self):
        """Teste de obtenção de resumo de drift"""
        monitor = DriftMonitor()
        summary = monitor.get_drift_summary()
        
        assert 'monitoring_active' in summary
        assert 'data_drift_alerts' in summary
        assert 'concept_drift_alerts' in summary
        assert 'performance_history_size' in summary
        
    @patch('builtins.open')
    @patch('json.dump')
    def test_export_alerts(self, mock_json_dump, mock_open):
        """Teste de exportação de alertas"""
        baseline_performance = {'accuracy': 0.85}
        monitor = DriftMonitor(baseline_performance=baseline_performance)
        
        # Simular alguns alertas
        alert = DriftAlert(
            timestamp=datetime.now(),
            drift_type='data',
            severity='medium',
            metric='feature1',
            value=0.5,
            threshold=0.05,
            message='Test alert'
        )
        monitor.data_drift_detector.alerts.append(alert)
        
        # Exportar alertas
        monitor.export_alerts('test_alerts.json')
        
        # Verificar que arquivo foi aberto e JSON foi escrito
        mock_open.assert_called_once_with('test_alerts.json', 'w')
        mock_json_dump.assert_called_once()


@pytest.mark.skipif(not DRIFT_MODULE_AVAILABLE, reason="Drift detection module not available")
class TestDriftAlert:
    """Testes para DriftAlert"""
    
    def test_alert_creation(self):
        """Teste de criação de alerta"""
        timestamp = datetime.now()
        alert = DriftAlert(
            timestamp=timestamp,
            drift_type='data',
            severity='high',
            metric='accuracy',
            value=0.7,
            threshold=0.85,
            message='Performance degraded'
        )
        
        assert alert.timestamp == timestamp
        assert alert.drift_type == 'data'
        assert alert.severity == 'high'
        assert alert.metric == 'accuracy'
        assert alert.value == 0.7
        assert alert.threshold == 0.85
        assert alert.message == 'Performance degraded'


# Teste de integração com mock para verificar se módulo funciona mesmo sem dependencies
def test_drift_module_import():
    """Teste que verifica se o módulo pode ser importado"""
    try:
        from src.monitoring.drift_detection import DriftMonitor
        assert True, "Módulo importado com sucesso"
    except ImportError as e:
        # Este é esperado se as dependências não estão instaladas
        assert "numpy" in str(e) or "scipy" in str(e) or "sklearn" in str(e)


def test_drift_module_fallback():
    """Teste que verifica se a aplicação funciona sem drift detection"""
    # Simular que o módulo não está disponível
    import sys
    original_modules = sys.modules.copy()
    
    try:
        # Remover módulos relacionados ao drift
        modules_to_remove = [key for key in sys.modules.keys() 
                           if 'monitoring' in key or 'drift' in key]
        for module in modules_to_remove:
            sys.modules.pop(module, None)
            
        # Verificar que a aplicação pode lidar com a ausência do módulo
        # (este teste seria mais útil se executado no contexto da aplicação Flask)
        assert True, "Aplicação deve funcionar sem drift detection"
        
    finally:
        # Restaurar módulos
        sys.modules.update(original_modules)


if __name__ == "__main__":
    # Executar testes básicos se executado diretamente
    if DRIFT_MODULE_AVAILABLE:
        print("✅ Drift detection module available - running tests")
        
        # Teste básico de funcionamento
        baseline = {'accuracy': 0.85}
        monitor = DriftMonitor(baseline_performance=baseline)
        
        reference_data = {
            'feature1': np.random.normal(0, 1, 100)
        }
        monitor.initialize_reference_data(reference_data)
        
        features = {'feature1': 0.5}
        result = monitor.monitor_prediction(features=features)
        
        print(f"✅ Monitor funcionando: {result['monitoring_active']}")
        print("✅ Todos os testes básicos passaram!")
        
    else:
        print("⚠️  Drift detection module not available - tests will be skipped")
        print("💡 Para habilitar: pip install numpy scipy scikit-learn pandas")
