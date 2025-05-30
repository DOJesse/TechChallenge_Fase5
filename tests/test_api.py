import pytest
from flask import json
import src.api.api as api_module

@pytest.fixture
def client():
    app = api_module.app
    app.config['TESTING'] = True
    return app.test_client()

class DummyModel:
    def predict(self, X):
        return [0]
    def predict_proba(self, X):
        return [[0.7, 0.3]]

class DummyLE:
    def transform(self, arr):
        # return zero for each element
        return [0 for _ in arr]
    def inverse_transform(self, arr):
        # return 'label' for each element
        return ['label' for _ in arr]


def setup_dummy_pipeline(monkeypatch):
    dummy_model = DummyModel()
    dummy_encoders = {'situacao_candidado': DummyLE()}
    dummy_feature_cols = ['situacao_candidado_enc']
    # Override pipeline and related variables in api module
    monkeypatch.setattr(api_module, 'pipeline', {'model': dummy_model, 'encoders': dummy_encoders, 'feature_cols': dummy_feature_cols})
    monkeypatch.setattr(api_module, 'model', dummy_model)
    monkeypatch.setattr(api_module, 'encoders', dummy_encoders)
    monkeypatch.setattr(api_module, 'feature_cols', dummy_feature_cols)
    # Bypass transformations
    monkeypatch.setattr(api_module, 'parse_dates', lambda df: df)
    monkeypatch.setattr(api_module, 'extract_text_features', lambda df: df)


def test_predict_no_data(client):
    response = client.post('/predict')
    assert response.status_code == 400
    body = response.get_json()
    assert 'error' in body


def test_predict_success(client, monkeypatch):
    setup_dummy_pipeline(monkeypatch)
    # Send minimal required JSON
    response = client.post('/predict', json={'situacao_candidado': 'any'})
    assert response.status_code == 200
    body = response.get_json()
    assert body['prediction'] == 'label'
    assert isinstance(body['probabilities'], list)
    assert body['probabilities'] == [0.7, 0.3]


def test_predict_error(monkeypatch, client):
    # Setup pipeline but force transform to fail
    setup_dummy_pipeline(monkeypatch)
    # Create encoder that raises
    class BadLE:
        def transform(self, arr):
            raise ValueError('transform error')
    monkeypatch.setitem(api_module.encoders, 'situacao_candidado', BadLE())
    response = client.post('/predict', json={'situacao_candidado': 'any'})
    assert response.status_code == 500
    body = response.get_json()
    assert 'error' in body
