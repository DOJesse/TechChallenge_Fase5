import pandas as pd
import numpy as np
from typing import List
from gensim.models import KeyedVectors

# Colunas textuais para gerar embeddings
text_features_list: List[str] = [
    'titulo', 'modalidade', 'nome', 'comentario', 'recrutador',
    'area_atuacao_cand', 'conhecimentos_tecnicos_cand',
    'certificacoes_cand', 'outras_certificacoes_cand',
    'qualificacoes_cand', 'experiencias_cand', 'cv_pt_cand',
    'titulo_vaga_vaga', 'cliente_vaga', 'solicitante_cliente_vaga',
    'nivel profissional_vaga', 'outro_idioma_vaga',
    'areas_atuacao_vaga', 'principais_atividades_vaga',
    'competencia_tecnicas_e_comportamentais_vaga'
]

def document_vector(text: str, model: KeyedVectors, num_features: int) -> np.ndarray:
    """Transforma um texto em um vetor médio de Word2Vec."""
    if not isinstance(text, str) or not text.strip():
        return np.zeros(num_features)
    words = [w for w in text.split() if w in model.key_to_index]
    if not words:
        return np.zeros(num_features)
    return np.mean([model[w] for w in words], axis=0)

def expand_vector(
    df: pd.DataFrame,
    feature_list: List[str],
    model: KeyedVectors,
    num_features: int
) -> pd.DataFrame:
    """
    Para cada coluna de feature_list em df, aplica document_vector e
    expande em num_features colunas (nome_0, nome_1, ..., nome_{N-1}).
    Remove a coluna original e retorna só o DataFrame de embeddings.
    """
    df_embeddings = pd.DataFrame(index=df.index)
    for feature in feature_list:
        emb = df[feature].apply(lambda x: document_vector(x, model, num_features))
        cols = [f"{feature}_{i}" for i in range(num_features)]
        expanded = pd.DataFrame(emb.tolist(), columns=cols, index=df.index)
        df_embeddings = pd.concat([df_embeddings, expanded], axis=1)
    return df_embeddings
