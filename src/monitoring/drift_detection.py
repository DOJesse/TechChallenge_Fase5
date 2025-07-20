"""
Drift Detection Module for Decision ML System

This module implements data drift and concept drift detection
to monitor model performance degradation in production.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score
import logging
from datetime import datetime, timedelta
import json
import warnings
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DriftAlert:
    """Data class for drift alerts"""
    timestamp: datetime
    drift_type: str  # 'data' or 'concept'
    severity: str   # 'low', 'medium', 'high'
    metric: str
    value: float
    threshold: float
    message: str
    
class DataDriftDetector:
    """
    Detects data drift using statistical tests
    
    Monitors changes in feature distributions that could affect model performance
    """
    
    def __init__(self, 
                 significance_level: float = 0.05,
                 reference_window_size: int = 1000,
                 detection_window_size: int = 100):
        """
        Initialize Data Drift Detector
        
        Args:
            significance_level: P-value threshold for statistical tests
            reference_window_size: Size of reference data window  
            detection_window_size: Size of current data window
        """
        self.significance_level = significance_level
        self.reference_window_size = reference_window_size
        self.detection_window_size = detection_window_size
        self.reference_data = {}
        self.alerts = []
        
    def set_reference_data(self, data: Dict[str, np.ndarray]) -> None:
        """
        Set reference data for drift comparison
        
        Args:
            data: Dictionary with feature names as keys and arrays as values
        """
        self.reference_data = {}
        for feature, values in data.items():
            if len(values) > self.reference_window_size:
                # Use most recent reference_window_size samples
                self.reference_data[feature] = values[-self.reference_window_size:]
            else:
                self.reference_data[feature] = values
                
        logger.info(f"Reference data set for {len(self.reference_data)} features")
        
    def detect_drift(self, current_data: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Detect data drift using Kolmogorov-Smirnov test
        
        Args:
            current_data: Current data to compare against reference
            
        Returns:
            Dictionary with drift detection results
        """
        if not self.reference_data:
            raise ValueError("Reference data not set. Call set_reference_data() first.")
            
        drift_results = {
            'timestamp': datetime.now(),
            'features_analyzed': 0,
            'features_with_drift': 0,
            'drift_detected': False,
            'feature_results': {},
            'alerts': []
        }
        
        for feature in self.reference_data.keys():
            if feature not in current_data:
                logger.warning(f"Feature {feature} not found in current data")
                continue
                
            # Limit current data to detection window size
            current_values = current_data[feature]
            if len(current_values) > self.detection_window_size:
                current_values = current_values[-self.detection_window_size:]
                
            # Perform Kolmogorov-Smirnov test
            try:
                ks_statistic, p_value = stats.ks_2samp(
                    self.reference_data[feature], 
                    current_values
                )
                
                drift_detected = p_value < self.significance_level
                
                # Calculate effect size (practical significance)
                effect_size = self._calculate_effect_size(
                    self.reference_data[feature], 
                    current_values
                )
                
                feature_result = {
                    'ks_statistic': ks_statistic,
                    'p_value': p_value,
                    'drift_detected': drift_detected,
                    'effect_size': effect_size,
                    'severity': self._classify_severity(ks_statistic, effect_size)
                }
                
                drift_results['feature_results'][feature] = feature_result
                drift_results['features_analyzed'] += 1
                
                if drift_detected:
                    drift_results['features_with_drift'] += 1
                    drift_results['drift_detected'] = True
                    
                    # Create alert
                    alert = DriftAlert(
                        timestamp=datetime.now(),
                        drift_type='data',
                        severity=feature_result['severity'],
                        metric=f'ks_test_{feature}',
                        value=ks_statistic,
                        threshold=self.significance_level,
                        message=f"Data drift detected in feature '{feature}' "
                               f"(KS={ks_statistic:.4f}, p={p_value:.4f})"
                    )
                    
                    self.alerts.append(alert)
                    drift_results['alerts'].append(alert)
                    
                    logger.warning(f"Data drift detected in {feature}: "
                                 f"KS={ks_statistic:.4f}, p={p_value:.4f}")
                    
            except Exception as e:
                logger.error(f"Error detecting drift for feature {feature}: {e}")
                
        drift_results['drift_percentage'] = (
            drift_results['features_with_drift'] / 
            max(drift_results['features_analyzed'], 1) * 100
        )
        
        return drift_results
        
    def _calculate_effect_size(self, reference: np.ndarray, current: np.ndarray) -> float:
        """Calculate Cohen's d effect size"""
        try:
            pooled_std = np.sqrt(
                ((len(reference) - 1) * np.var(reference, ddof=1) + 
                 (len(current) - 1) * np.var(current, ddof=1)) / 
                (len(reference) + len(current) - 2)
            )
            
            if pooled_std == 0:
                return 0.0
                
            effect_size = abs(np.mean(reference) - np.mean(current)) / pooled_std
            return effect_size
        except:
            return 0.0
            
    def _classify_severity(self, ks_statistic: float, effect_size: float) -> str:
        """Classify drift severity based on statistical measures"""
        if ks_statistic > 0.5 or effect_size > 0.8:
            return 'high'
        elif ks_statistic > 0.3 or effect_size > 0.5:
            return 'medium'
        else:
            return 'low'


class ConceptDriftDetector:
    """
    Detects concept drift by monitoring model performance metrics
    
    Tracks degradation in prediction accuracy, precision, recall
    """
    
    def __init__(self, 
                 baseline_performance: Dict[str, float],
                 degradation_threshold: float = 0.1,
                 window_size: int = 100):
        """
        Initialize Concept Drift Detector
        
        Args:
            baseline_performance: Expected performance metrics
            degradation_threshold: Acceptable performance degradation (0.1 = 10%)
            window_size: Size of sliding window for performance calculation
        """
        self.baseline_performance = baseline_performance
        self.degradation_threshold = degradation_threshold
        self.window_size = window_size
        self.performance_history = []
        self.alerts = []
        
    def update_performance(self, 
                         y_true: np.ndarray, 
                         y_pred: np.ndarray, 
                         y_pred_proba: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Update performance metrics and detect concept drift
        
        Args:
            y_true: True labels
            y_pred: Predicted labels  
            y_pred_proba: Prediction probabilities (optional)
            
        Returns:
            Dictionary with performance metrics and drift status
        """
        # Calculate current performance metrics
        try:
            current_metrics = {
                'timestamp': datetime.now(),
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
                'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
                'sample_size': len(y_true)
            }
            
            # Add to history
            self.performance_history.append(current_metrics)
            
            # Keep only recent window
            if len(self.performance_history) > self.window_size:
                self.performance_history = self.performance_history[-self.window_size:]
                
            # Calculate rolling averages
            recent_performance = self._calculate_rolling_performance()
            
            # Detect concept drift
            drift_results = self._detect_concept_drift(recent_performance)
            
            return {
                'current_metrics': current_metrics,
                'rolling_metrics': recent_performance,
                'drift_results': drift_results,
                'performance_history_size': len(self.performance_history)
            }
            
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
            return {'error': str(e)}
            
    def _calculate_rolling_performance(self) -> Dict[str, float]:
        """Calculate rolling average performance metrics"""
        if not self.performance_history:
            return {}
            
        metrics = ['accuracy', 'precision', 'recall']
        rolling_performance = {}
        
        for metric in metrics:
            values = [entry[metric] for entry in self.performance_history if metric in entry]
            if values:
                rolling_performance[metric] = np.mean(values)
                rolling_performance[f'{metric}_std'] = np.std(values)
                
        return rolling_performance
        
    def _detect_concept_drift(self, current_performance: Dict[str, float]) -> Dict[str, Any]:
        """Detect concept drift based on performance degradation"""
        drift_results = {
            'concept_drift_detected': False,
            'degraded_metrics': [],
            'alerts': []
        }
        
        for metric, baseline_value in self.baseline_performance.items():
            if metric in current_performance:
                current_value = current_performance[metric]
                degradation = (baseline_value - current_value) / baseline_value
                
                if degradation > self.degradation_threshold:
                    drift_results['concept_drift_detected'] = True
                    drift_results['degraded_metrics'].append({
                        'metric': metric,
                        'baseline': baseline_value,
                        'current': current_value,
                        'degradation': degradation
                    })
                    
                    # Create alert
                    severity = 'high' if degradation > 0.2 else 'medium'
                    alert = DriftAlert(
                        timestamp=datetime.now(),
                        drift_type='concept',
                        severity=severity,
                        metric=metric,
                        value=current_value,
                        threshold=baseline_value * (1 - self.degradation_threshold),
                        message=f"Concept drift detected: {metric} degraded by "
                               f"{degradation:.1%} (from {baseline_value:.3f} to {current_value:.3f})"
                    )
                    
                    self.alerts.append(alert)
                    drift_results['alerts'].append(alert)
                    
                    logger.warning(f"Concept drift detected: {metric} degraded by "
                                 f"{degradation:.1%}")
                    
        return drift_results


class DriftMonitor:
    """
    Unified drift monitoring system for the Decision ML pipeline
    
    Combines data drift and concept drift detection with alerting
    """
    
    def __init__(self, 
                 baseline_performance: Optional[Dict[str, float]] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize Drift Monitor
        
        Args:
            baseline_performance: Expected model performance metrics
            config: Configuration dictionary for detectors
        """
        # Default configuration
        default_config = {
            'data_drift': {
                'significance_level': 0.05,
                'reference_window_size': 1000,
                'detection_window_size': 100
            },
            'concept_drift': {
                'degradation_threshold': 0.1,
                'window_size': 100
            }
        }
        
        self.config = {**default_config, **(config or {})}
        
        # Initialize detectors
        self.data_drift_detector = DataDriftDetector(**self.config['data_drift'])
        
        if baseline_performance:
            self.concept_drift_detector = ConceptDriftDetector(
                baseline_performance=baseline_performance,
                **self.config['concept_drift']
            )
        else:
            self.concept_drift_detector = None
            logger.warning("Concept drift detector not initialized - baseline performance not provided")
            
        self.monitoring_active = True
        
    def initialize_reference_data(self, reference_data: Dict[str, np.ndarray]) -> None:
        """Initialize reference data for data drift detection"""
        self.data_drift_detector.set_reference_data(reference_data)
        logger.info("Reference data initialized for drift monitoring")
        
    def monitor_prediction(self, 
                         features: Dict[str, Any],
                         y_true: Optional[int] = None,
                         y_pred: Optional[int] = None,
                         y_pred_proba: Optional[float] = None) -> Dict[str, Any]:
        """
        Monitor a single prediction for drift
        
        Args:
            features: Feature values for the prediction
            y_true: True label (if available)
            y_pred: Predicted label (if available)
            y_pred_proba: Prediction probability (if available)
            
        Returns:
            Monitoring results dictionary
        """
        if not self.monitoring_active:
            return {'monitoring_active': False}
            
        results = {
            'timestamp': datetime.now(),
            'monitoring_active': True,
            'data_drift': None,
            'concept_drift': None,
            'alerts': []
        }
        
        # Convert features to arrays for drift detection
        feature_arrays = {}
        for key, value in features.items():
            if isinstance(value, (int, float)):
                feature_arrays[key] = np.array([value])
            elif isinstance(value, (list, np.ndarray)):
                feature_arrays[key] = np.array(value)
                
        # Monitor data drift (requires accumulated data)
        try:
            if len(feature_arrays) > 0:
                # Note: In practice, you'd accumulate features over time
                # This is a simplified version for demonstration
                drift_result = self.data_drift_detector.detect_drift(feature_arrays)
                results['data_drift'] = drift_result
                results['alerts'].extend(drift_result.get('alerts', []))
        except Exception as e:
            logger.error(f"Data drift detection failed: {e}")
            
        # Monitor concept drift (requires labels)
        if (self.concept_drift_detector and 
            y_true is not None and 
            y_pred is not None):
            try:
                concept_result = self.concept_drift_detector.update_performance(
                    np.array([y_true]), 
                    np.array([y_pred]),
                    np.array([y_pred_proba]) if y_pred_proba else None
                )
                results['concept_drift'] = concept_result
                if 'drift_results' in concept_result:
                    results['alerts'].extend(
                        concept_result['drift_results'].get('alerts', [])
                    )
            except Exception as e:
                logger.error(f"Concept drift detection failed: {e}")
                
        return results
        
    def get_drift_summary(self) -> Dict[str, Any]:
        """Get comprehensive drift monitoring summary"""
        return {
            'monitoring_active': self.monitoring_active,
            'data_drift_alerts': len(self.data_drift_detector.alerts),
            'concept_drift_alerts': (
                len(self.concept_drift_detector.alerts) 
                if self.concept_drift_detector else 0
            ),
            'last_data_drift_alerts': self.data_drift_detector.alerts[-5:],
            'last_concept_drift_alerts': (
                self.concept_drift_detector.alerts[-5:] 
                if self.concept_drift_detector else []
            ),
            'performance_history_size': (
                len(self.concept_drift_detector.performance_history)
                if self.concept_drift_detector else 0
            )
        }
        
    def export_alerts(self, filepath: str) -> None:
        """Export all alerts to JSON file"""
        all_alerts = []
        
        # Data drift alerts
        for alert in self.data_drift_detector.alerts:
            all_alerts.append({
                'timestamp': alert.timestamp.isoformat(),
                'type': alert.drift_type,
                'severity': alert.severity,
                'metric': alert.metric,
                'value': alert.value,
                'threshold': alert.threshold,
                'message': alert.message
            })
            
        # Concept drift alerts
        if self.concept_drift_detector:
            for alert in self.concept_drift_detector.alerts:
                all_alerts.append({
                    'timestamp': alert.timestamp.isoformat(),
                    'type': alert.drift_type,
                    'severity': alert.severity,
                    'metric': alert.metric,
                    'value': alert.value,
                    'threshold': alert.threshold,
                    'message': alert.message
                })
                
        with open(filepath, 'w') as f:
            json.dump(all_alerts, f, indent=2)
            
        logger.info(f"Exported {len(all_alerts)} alerts to {filepath}")
