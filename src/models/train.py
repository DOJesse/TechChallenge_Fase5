"""
train.py

Pipeline de treinamento do modelo preditivo para match candidato-vaga.
- Carrega dados processados.
- Aplica feature engineering.
- Separa treino/teste.
- Treina e avalia o modelo.
- Salva modelo e encoders.

Atende ao requisito de pipeline completa para treinamento do modelo, incluindo
feature engineering, pré-processamento, treinamento e validação, e salvamento
usando joblib. fileciteturn7file11
"""

import os
import sys
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Ajusta path para permitir imports de módulos src
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(root_path)

from src.features.feature_engineering import create_features


def main():
    # Definição de caminhos
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    data_path = os.path.join(base_dir, 'data', 'processed', 'dataset.csv')
    model_dir = os.path.join(base_dir, 'src', 'models', 'artifacts')
    os.makedirs(model_dir, exist_ok=True)

    # 1. Carregar dados processados
    df = pd.read_csv(data_path)

    # 2. Gerar features
    df_feat, encoders = create_features(df)

    # 3. Selecionar colunas de features e target
    feature_cols = [
        'dias_para_candidatura', 'cv_word_count', 'num_tech_skills'
    ] + [
        col for col in df_feat.columns
        if col.endswith('_enc') and col != 'situacao_candidado_enc'
    ]
    X = df_feat[feature_cols]
    y = df_feat['situacao_candidado_enc']

    # 4. Divisão treino/teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # 5. Treinamento do modelo
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 6. Avaliação
    y_pred = model.predict(X_test)
    print("Relatório de Classificação:\n", classification_report(y_test, y_pred))

    # 7. Salvamento de artefatos
    joblib.dump(model, os.path.join(model_dir, 'model.joblib'))
    joblib.dump(encoders, os.path.join(model_dir, 'encoders.joblib'))
    print(f'Modelo e encoders salvos em {model_dir}')


if __name__ == '__main__':
    main()
