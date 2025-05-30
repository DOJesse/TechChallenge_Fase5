import pytest
import pandas as pd
from src.features.feature_engineering import (
    parse_dates,
    extract_text_features,
    encode_categoricals,
    create_features
)


def test_parse_dates():
    data = {
        'data_requisicao': ['01-01-2025'],
        'data_candidatura': ['05-01-2025'],
        'ultima_atualizacao': ['10-01-2025']
    }
    df = pd.DataFrame(data)
    df_processed = parse_dates(df)
    assert pd.api.types.is_datetime64_any_dtype(df_processed['data_requisicao'])
    assert pd.api.types.is_datetime64_any_dtype(df_processed['data_candidatura'])
    assert pd.api.types.is_datetime64_any_dtype(df_processed['ultima_atualizacao'])
    assert df_processed.loc[0, 'dias_para_candidatura'] == 4


def test_extract_text_features():
    data = {
        'cv_pt': ['word1 word2 word3'],
        'conhecimentos_tecnicos': ['skill1,skill2,skill3']
    }
    df = pd.DataFrame(data)
    df_feats = extract_text_features(df)
    assert df_feats.loc[0, 'cv_word_count'] == 3
    assert df_feats.loc[0, 'num_tech_skills'] == 3


def test_encode_categoricals():
    cols = {
        'situacao_candidado': ['applied', 'hired'],
        'nivel_academico': ['Bachelor', 'Master'],
        'nivel_ingles': ['Basic', 'Fluent'],
        'nivel_espanhol': ['None', 'Intermediate'],
        'tipo_contratacao': ['Full-time', 'Part-time'],
        'nivel_profissional': ['Junior', 'Senior'],
        'prioridade_vaga': ['High', 'Low'],
        'vaga_sap': ['Yes', 'No']
    }
    df = pd.DataFrame({k: v for k, v in cols.items()})
    df_enc, encoders = encode_categoricals(df)
    # Check that encoded columns exist
    for col in cols.keys():
        assert col + '_enc' in df_enc.columns
    # Check encoders keys
    assert set(encoders.keys()) == set(cols.keys())
    # Check that encoding is integer
    assert pd.api.types.is_integer_dtype(df_enc['situacao_candidado_enc'])


def test_create_features_combines_all():
    
    # Create minimal DataFrame with required columns
    data = {
        'data_requisicao': ['01-01-2025'],
        'data_candidatura': ['02-01-2025'],
        'ultima_atualizacao': ['03-01-2025'],
        'cv_pt': ['a b c'],
        'conhecimentos_tecnicos': ['x,y'],
        'situacao_candidado': ['applied'],
        'nivel_academico': ['Bachelor'],
        'nivel_ingles': ['Basic'],
        'nivel_espanhol': ['None'],
        'tipo_contratacao': ['Full-time'],
        'nivel_profissional': ['Junior'],
        'prioridade_vaga': ['High'],
        'vaga_sap': ['Yes']
    }
    df = pd.DataFrame(data)
    df_final, encs = create_features(df)
    # Check that new features are present
    expected_feats = ['dias_para_candidatura', 'cv_word_count', 'num_tech_skills']
    for feat in expected_feats:
        assert feat in df_final.columns
    # Check that encoders dict contains expected keys
    assert 'situacao_candidado' in encs
    assert all(col + '_enc' in df_final.columns for col in encs)
