import pandas as pd
import numpy as np
import re
import unicodedata
from typing import List
from sklearn.preprocessing import OrdinalEncoder
from gensim.models import KeyedVectors
from sklearn.metrics import mean_squared_error, mean_absolute_error

# ---
# Funções de processamento de texto
# ---


def padroniza_texto(df: pd.DataFrame, features_list: List[str]) -> None:
    '''Remove espaços, torna todas as letras minúsculas e
       remove caracteres especiais dos campos texto'''
    for feature in features_list:
        df[f'{feature}'] = df[f'{feature}'].str.lower().str.strip()
        df[feature] = df[feature].apply(
                lambda x: unicodedata.normalize('NFKD', str(x))
                .encode(
                    'ascii', 'ignore'
                )
                .decode(
                    'utf-8'
                ))
        df[feature] = df[feature].apply(lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', str(x)))

    return None


def document_vector(text: str, model: KeyedVectors, num_features: int) -> np.ndarray:
    # Divide o texto em palavras e filtra as que estão no vocabulário do modelo
    if not isinstance(text, str) or not text.strip():
        return np.zeros(num_features)  # Retorna um vetor de zeros para texto vazio ou não-string

    words = [word for word in text.split() if word in model.key_to_index]

    if not words:
        return np.zeros(num_features)
    # Calcula a média dos vetores das palavras no documento
    return np.mean([model[word] for word in words], axis=0)


def expand_vector(df: pd.DataFrame, feature_list: List[str], model: KeyedVectors, num_features: int) -> pd.DataFrame:
    df_embeddings = pd.DataFrame()
    # criação de nomes para as colunas
    for feature in feature_list:
        df[f'{feature}_embedding'] = df[f'{feature}'].apply(lambda x: document_vector(x, model, num_features))
        new_embedding_columns = [f'{feature}_emb_{i}' for i in range(num_features)]
        df_embeddings_expanded = pd.DataFrame(
            df[f'{feature}_embedding'].tolist(), # Converte a Series de arrays para uma lista de listas
            columns=new_embedding_columns,        # Atribui os nomes das colunas
            index=df.index                         # Alinha pelo índice
        )
        df.drop(columns=[f'{feature}', f'{feature}_embedding'], inplace=True)
        df_embeddings = pd.concat([df_embeddings, df_embeddings_expanded], axis=1)
    return df_embeddings
    # return pd.concat([df_embeddings, df_embeddings_expanded], axis=1)

# ---
# Funções de Feature Engineering
# ---


def nivel_idioma(df: pd.DataFrame, language_features: List[str]) -> None:
    '''Trata dados faltantes de idiomas e utiliza o Ordinal Encoder para categorizar os níveis de idiomas'''
    language_order = ['Nenhum', 'Básico', 'Intermediário', 'Avançado', 'Fluente']
    enc = OrdinalEncoder(categories=[language_order])
    encoders = {}

    for language in language_features:
        df[f'{language}'] = df[f'{language}'].fillna('Nenhum')
        df[f'{language}'] = df[f'{language}'].replace('', 'Nenhum')
        # para igualar com o nível dos candidatos
        df[f'{language}'] = df[f'{language}'].replace('Técnico', 'Avançado')

        df[f'{language}_encoded'] = enc.fit_transform(df[[f'{language}']])
        encoders[language] = enc

    #df[f'{language}'].drop(columns=language_features, inplace=True)

    return encoders


def nivel_educacao(df: pd.DataFrame) -> OrdinalEncoder:
    '''Trata dados faltantes de nível de educaão e utiliza o Ordinal Encoder para categorizar os níveis de educação'''
    education_order = ['', 'ensino fundamental incompleto', 'ensino fundamental completo',
                       'ensino medio incompleto', 'ensino medio completo',
                       'ensino tecnico incompleto', 'ensino tecnico completo',
                       'ensino superior incompleto', 'ensino superior completo',
                       'pos graduacao incompleto', 'pos graduacao completo',
                       'mestrado incompleto', 'mestrado completo',
                       'doutorado incompleto', 'doutorado completo']

    df['nivel_academico'] = df['nivel_academico'].astype(str).str.lower().str.strip().replace('nan', '')
    df['nivel_academico'] = df['nivel_academico'].apply(lambda x: re.sub(r'\bcursando\b', 'incompleto', x) if x else x)

    enc_ed = OrdinalEncoder(categories=[education_order])
    df['nivel_academico_encoded'] = enc_ed.fit_transform(df[['nivel_academico']])
    #df.drop(columns=['nivel_academico'], inplace=True)

    return enc_ed


def mapear_senioridade(serie: pd.Series) -> pd.Series:
    text = serie.astype(str).str.lower().fillna('')
    niveis_map = {
        'Liderança': {'valor': 5, 'padrao': r'\bgerente\b|\blíder\b|lider|\bsupervisor\b|\bcoordenador\b'},
        'Especialista': {'valor': 4, 'padrao': r'\bespecialista\b|\bexpert\b|\bconsultor\(a\)\b|consultor'},
        'Sênior': {'valor': 3, 'padrao': r'\bsênior\b|\bsenior\b|\bsr\b|\biii\b'},
        'Pleno': {'valor': 2, 'padrao': r'\bpleno\b|\bpl\b|\bii\b'},
        'Júnior': {'valor': 1, 'padrao': r'\bjúnior\b|\bjr\b|\bi\b'},
        'Entrada': {'valor': 0, 'padrao': r'\btrainee\b|\bauxiliar\b|\baprendiz\b|\bassistente\btecnico\btécnico\b'}
    }
    condicoes = []
    valores = []

    for nivel in niveis_map:
        info = niveis_map[nivel]
        condicoes.append(text.str.contains(info['padrao'], regex=True, na=False))
        valores.append(info['valor'])

    # np.select é uma forma vetorizada e eficiente de fazer um "if/elif/else"
    # O valor padrão -1 indica que nenhum termo de senioridade foi encontrado
    return pd.Series(np.select(condicoes, valores, default=-1), index=serie.index)


# função para obter similaridade por cosseno
def similaridade(df: pd.DataFrame, vaga_column: str, cand_column: str, return_column: str) -> None:
    '''Obtenção de similaridade por cosseno'''
    vaga_emb_cols = [column for column in df.columns if column.startswith(f'{vaga_column}_emb')]
    cand_emb_cols = [column for column in df.columns if column.startswith(f'{cand_column}_emb')]
    # conversão de colunas para arrays NumPy
    vec_vaga = df[vaga_emb_cols].to_numpy()
    vec_cand = df[cand_emb_cols].to_numpy()
    # calculo de similaridade apenas das diagonais
    dot_product = np.sum(vec_vaga * vec_cand, axis=1)
    # Calcular a norma (magnitude) de cada vetor
    # np.linalg.norm(A, axis=1) calcula a norma L2 para cada linha
    norm_titulo = np.linalg.norm(vec_vaga, axis=1)
    norm_resumo = np.linalg.norm(vec_cand, axis=1)

    # O produto das normas no denominador
    denominator = norm_titulo * norm_resumo

    # Evitar divisão por zero para vetores nulos (ou com norma zero)
    # Onde o denominador é zero, a similaridade é 0 (ou NaN, dependendo da sua regra)
    # np.where(condition, if_true, if_false)
    pair_similarity = np.where(denominator != 0, dot_product / denominator, 0.0)
    df[f'{return_column}'] = pair_similarity

    return


# ---
# Função de avaliação de modelo
# ---


def evaluation(model, x_train, y_train, x_test, y_test):
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)

    print(f'MSE: {mse}\nRMSE: {rmse}\nMAE: {mae}')
    return
