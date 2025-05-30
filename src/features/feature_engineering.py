"""
feature_engineering.py

Módulo para geração de atributos (features) a partir do DataFrame de prospecção unificado.
Baseado na pipeline completa de treinamento que inclui feature engineering conforme especificado no Datathon fileciteturn5file3
e na estrutura dos JSONs detalhada no README fileciteturn6file1.

Funções:
 - parse_dates: converte colunas de data e calcula diferenças de dias
 - extract_text_features: extrai contagens e métricas de texto (CV, skills)
 - encode_categoricals: codifica variáveis categóricas em inteiros
 - create_features: orquestra todas as etapas acima
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte colunas de data do formato string ('dd-mm-YYYY') para datetime
    e calcula dias entre requisição e candidatura.
    """
    df = df.copy()
    df['data_requisicao'] = pd.to_datetime(df['data_requisicao'], format='%d-%m-%Y', errors='coerce')
    df['data_candidatura'] = pd.to_datetime(df['data_candidatura'], format='%d-%m-%Y', errors='coerce')
    df['ultima_atualizacao'] = pd.to_datetime(df['ultima_atualizacao'], format='%d-%m-%Y', errors='coerce')
    df['dias_para_candidatura'] = (df['data_candidatura'] - df['data_requisicao']).dt.days
    return df


def extract_text_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera atributos a partir de texto livre: contagem de palavras no CV e número de skills.
    """
    df = df.copy()
    df['cv_word_count'] = df['cv_pt'].apply(lambda x: len(str(x).split()))
    df['num_tech_skills'] = df['conhecimentos_tecnicos'].apply(
        lambda s: len(str(s).split(',')) if pd.notnull(s) and s.strip() else 0
    )
    return df


def encode_categoricals(df: pd.DataFrame) -> (pd.DataFrame, dict):
    """
    Codifica variáveis categóricas para uso em modelo:
    situacao_candidado, nivel_academico, nivel_ingles, nivel_espanhol,
    tipo_contratacao, nivel_profissional, prioridade_vaga, vaga_sap.
    Retorna DataFrame com novas colunas '<col>_enc' e dicionário de LabelEncoders.
    """
    df = df.copy()
    encoders = {}
    cols = [
        'situacao_candidado', 'nivel_academico', 'nivel_ingles', 'nivel_espanhol',
        'tipo_contratacao', 'nivel_profissional', 'prioridade_vaga', 'vaga_sap'
    ]
    for col in cols:
        le = LabelEncoder()
        filled = df[col].fillna('NA').astype(str)
        df[col + '_enc'] = le.fit_transform(filled)
        encoders[col] = le
    return df, encoders


def create_features(df: pd.DataFrame) -> (pd.DataFrame, dict):
    """
    Executa toda a pipeline de feature engineering:
    - parse_dates
    - extract_text_features
    - encode_categoricals
    Retorna DataFrame com atributos novos e dicionário de encoders.
    """
    df_dates = parse_dates(df)
    df_text = extract_text_features(df_dates)
    df_final, encoders = encode_categoricals(df_text)
    return df_final, encoders


if __name__ == '__main__':
    # Exemplo de uso após preprocess.py gerar 'data/processed/dataset.csv'
    import os
    base = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base, 'data', 'processed', 'dataset.csv')
    df = pd.read_csv(data_path)
    df_feat, encs = create_features(df)
    print('Feature engineering concluída. Exemplo de colunas geradas:', df_feat.columns.tolist())
