import pytest
import pandas as pd
import numpy as np

import src.models.train as train_module


def test_main(monkeypatch):
    # Setup dummy processed data
    dummy_data = pd.DataFrame({
        'dias_para_candidatura': [1, 2, 3],
        'cv_word_count': [5, 6, 7],
        'num_tech_skills': [1, 2, 3],
        'feature1_enc': [0, 1, 2],
        'situacao_candidado_enc': [0, 1, 0]
    })

    # Monkeypatch pandas.read_csv to return dummy_data
    monkeypatch.setattr(train_module.pd, 'read_csv', lambda path: dummy_data)

    # Monkeypatch create_features to return features and dummy encoders
    monkeypatch.setattr(train_module, 'create_features', lambda df: (dummy_data, {}))

    # Dummy RandomForestClassifier
    class DummyRF:
        def __init__(self, n_estimators, random_state): pass
        def fit(self, X, y): return self
        def predict(self, X): return np.array([0] * len(X))
    monkeypatch.setattr(train_module, 'RandomForestClassifier', DummyRF)

    # Capture joblib.dump calls
    dumps = []
    monkeypatch.setattr(train_module.joblib, 'dump', lambda obj, path: dumps.append(path))

    # Run training pipeline
    train_module.main()

    # Check that model and encoders were saved
    assert any('model.joblib' in p for p in dumps)
    assert any('encoders.joblib' in p for p in dumps)
