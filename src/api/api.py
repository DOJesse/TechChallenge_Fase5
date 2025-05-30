"""
api.py

API de inferência para modelo match candidato-vaga.
- Carrega pipeline do modelo (pipeline.joblib).
- Expõe endpoint POST /predict para receber JSON com campos do dataframe.
- Retorna label previsto e probabilidades.
"""

from flask import Flask, request, jsonify
import os
import sys
import joblib
import pandas as pd

# Ajusta path para import de src
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(root_path)

# Carrega pipeline de inferência
pipeline_path = os.path.join(root_path, 'src', 'models', 'artifacts', 'pipeline.joblib')
pipeline = joblib.load(pipeline_path)
model = pipeline['model']
encoders = pipeline['encoders']
feature_cols = pipeline['feature_cols']

# Importa funções de engineering
from src.features.feature_engineering import parse_dates, extract_text_features

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Nenhum dado de entrada fornecido'}), 400
    try:
        # Cria DataFrame de um registro
        df = pd.DataFrame([data])
        # Aplica transformação de datas e texto
        df = parse_dates(df)
        df = extract_text_features(df)
        # Aplica encoding com encoders salvos
        for col, le in encoders.items():
            df[col + '_enc'] = le.transform(df[col].fillna('NA').astype(str))
        # Seleciona features
        X = df[feature_cols]
        # Predição e probabilidades
        pred = model.predict(X)[0]
        proba = model.predict_proba(X)[0].tolist()
        # Decodifica label
        label = encoders['situacao_candidado'].inverse_transform([pred])[0]
        return jsonify({'prediction': label, 'probabilities': proba})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)