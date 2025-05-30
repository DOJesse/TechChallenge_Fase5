"""
save_model.py

Script para agrupar artefatos do modelo (modelo e encoders) em um único arquivo
para uso na API de inferência.
- Carrega modelo e encoders salvos em src/models/artifacts
- Empacota em um dicionário pipeline contendo:
    'model': o estimador treinado
    'encoders': o dicionário de LabelEncoders
    'feature_cols': lista de features usadas no treinamento
- Salva o pipeline com joblib em src/models/artifacts/pipeline.joblib

Atende ao requisito de salvar modelo para posterior utilização na API conforme o PDF: 
"Salve o modelo utilizando pickle ou joblib para posterior utilização na API." fileciteturn11file1
"""
import os
import sys
import joblib

# Ajusta path para imports relativos, se necessário
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
artifacts_dir = os.path.join(root_path, 'src', 'models', 'artifacts')

# Caminhos dos artefatos
model_path = os.path.join(artifacts_dir, 'model.joblib')
encoders_path = os.path.join(artifacts_dir, 'encoders.joblib')

# Carrega artefatos
model = joblib.load(model_path)
encoders = joblib.load(encoders_path)

# Define a lista de colunas de features (mesma usada em train.py)
feature_cols = [
    'dias_para_candidatura', 'cv_word_count', 'num_tech_skills'
] + [col for col in encoders.keys()]

# Empacota pipeline
pipeline = {
    'model': model,
    'encoders': encoders,
    'feature_cols': feature_cols
}

# Caminho de saída do pipeline
pipeline_path = os.path.join(artifacts_dir, 'pipeline.joblib')
joblib.dump(pipeline, pipeline_path)

print(f'Pipeline de inferência salvo em {pipeline_path}')
