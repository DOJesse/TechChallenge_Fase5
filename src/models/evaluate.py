"""
evaluate.py

Script para avaliação do modelo treinado de match candidato-vaga.
- Carrega dataset processado.
- Gera features com pipeline idêntica ao treino.
- Realiza split treino/teste (mesma configuração do train.py).
- Carrega modelo salvo e faz previsões.
- Exibe relatório de classificação e matriz de confusão.
- Salva métricas em JSON e CSV no diretório de artefatos.

Atende ao requisito de avaliação da pipeline conforme especificado no Datathon (pipeline completa de treinamento e avaliação). fileciteturn7file11
"""

import os
import sys
import pandas as pd
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# Ajuste de path para imports
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(root_path)
from src.features.feature_engineering import create_features


def main():
    # Definição de caminhos
    base_dir = root_path
    data_path = os.path.join(base_dir, 'data', 'processed', 'dataset.csv')
    artifacts_dir = os.path.join(base_dir, 'src', 'models', 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)

    # 1. Carregar dados
    df = pd.read_csv(data_path)

    # 2. Gerar features
    df_feat, _ = create_features(df)

    # 3. Seleção de colunas de features e target (mesmo do train.py)
    feature_cols = [
        'dias_para_candidatura', 'cv_word_count', 'num_tech_skills'
    ] + [c for c in df_feat.columns if c.endswith('_enc') and c != 'situacao_candidado_enc']
    X = df_feat[feature_cols]
    y = df_feat['situacao_candidado_enc']

    # 4. Split treino/teste
    _, X_test, _, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # 5. Carregar modelo
    model = joblib.load(os.path.join(artifacts_dir, 'model.joblib'))

    # 6. Previsões e métricas
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)

    # Exibição
    print("Relatório de Classificação:")
    print(classification_report(y_test, y_pred))
    print("Matriz de Confusão:")
    print(cm)

    # 7. Salvamento de métricas
    with open(os.path.join(artifacts_dir, 'classification_report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    cm_df = pd.DataFrame(cm)
    cm_df.to_csv(os.path.join(artifacts_dir, 'confusion_matrix.csv'), index=False)
    print(f'Métricas salvas em {artifacts_dir}')


if __name__ == '__main__':
    main()
