# %%
import pandas as pd
import numpy as np
import joblib
import re
import unicodedata
from pathlib import Path
import yaml
from gensim.models import KeyedVectors
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

import utils
# %%
# ---
# carrega de dados e modelo word2vec pré-treinado
# ---
# Define caminhos de forma robusta, independentemente de onde o script é executado
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

CONFIG_PATH = PROJECT_ROOT / 'config.yaml'
W2V_MODEL_PATH = PROJECT_ROOT / 'src' / 'word2vec' / 'cbow_s100.txt'
APPLICANTS_PATH = PROJECT_ROOT / 'src' / 'data' / 'applicants.json'
PROSPECTS_PATH = PROJECT_ROOT / 'src' / 'data' / 'prospects.json'
VAGAS_PATH = PROJECT_ROOT / 'src' / 'data' / 'vagas.json'

OUTPUT_DIR = PROJECT_ROOT / 'artifacts'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Carrega as configurações
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

model_word2vec = KeyedVectors.load_word2vec_format(W2V_MODEL_PATH)
df_applicants = pd.read_json(APPLICANTS_PATH, orient='index')
df_prospects = pd.read_json(PROSPECTS_PATH, orient='index')
df_vagas = pd.read_json(VAGAS_PATH, orient='index')

# %%
# ---
# Normalização dos dicionários
# ---
df_infos_basicas = pd.json_normalize(
    df_applicants['infos_basicas']
)
df_informacoes_pessoais = pd.json_normalize(
    df_applicants['informacoes_pessoais']
)
df_informacoes_profissionais = pd.json_normalize(
    df_applicants['informacoes_profissionais']
)
df_formacao_e_idiomas = pd.json_normalize(
    df_applicants['formacao_e_idiomas']
)
df_cargo_atual = pd.json_normalize(
    df_applicants['cargo_atual']
)

df_applicants = pd.concat(
    [
        df_applicants.drop('infos_basicas', axis=1),
        df_infos_basicas
    ],
    axis=1
)
df_applicants = pd.concat(
    [
        df_applicants.drop('informacoes_pessoais', axis=1),
        df_informacoes_pessoais
    ],
    axis=1
)
df_applicants = pd.concat(
    [
        df_applicants.drop('informacoes_profissionais', axis=1),
        df_informacoes_profissionais
    ],
    axis=1
)
df_applicants = pd.concat(
    [
        df_applicants.drop('formacao_e_idiomas', axis=1),
        df_formacao_e_idiomas
    ],
    axis=1
)
df_applicants = pd.concat(
    [
        df_applicants.drop('cargo_atual', axis=1),
        df_cargo_atual
    ],
    axis=1
)

df_prospects_exploded = df_prospects.explode('prospects')
df_prospects_normalized = pd.json_normalize(
    df_prospects_exploded['prospects']
)

df_prospects_exploded = df_prospects_exploded.drop(
    'prospects', axis=1).reset_index()
df_prospects = pd.concat(
    [
        df_prospects_exploded,
        df_prospects_normalized
    ],
    axis=1
)

# ajustando nomes das features
df_prospects.rename(columns={'index': 'id_vaga', 'codigo': 'id_cand'},
                    inplace=True)

df_informacoes_basicas = pd.json_normalize(
    df_vagas['informacoes_basicas']
)
df_perfil_vaga = pd.json_normalize(
    df_vagas['perfil_vaga']
)
df_beneficios = pd.json_normalize(
    df_vagas['beneficios']
)

df_vagas = pd.concat(
    [
        df_vagas.drop('informacoes_basicas', axis=1),
        df_informacoes_basicas
    ],
    axis=1
)
df_vagas = pd.concat(
    [
        df_vagas.drop('perfil_vaga', axis=1),
        df_perfil_vaga
    ],
    axis=1
)
df_vagas = pd.concat(
    [
        df_vagas.drop('beneficios', axis=1),
        df_beneficios
    ],
    axis=1
)

# %%
# ---
# Feature Engineering
# ---
# selecao de features relevantes para o problema a ser resolvido
features_vagas = ['titulo_vaga', 'vaga_sap', 'cliente', 'solicitante_cliente',
                  'tipo_contratacao', 'vaga_especifica_para_pcd',
                  'nivel profissional', 'nivel_academico', 'nivel_ingles',
                  'nivel_espanhol', 'outro_idioma', 'areas_atuacao',
                  'principais_atividades',
                  'competencia_tecnicas_e_comportamentais']
df_vagas = df_vagas[features_vagas]
df_vagas = df_vagas.reset_index()
df_vagas = df_vagas.rename(columns={'index': 'id'})
features_applicants = ['pcd', 'objetivo_profissional', 'area_atuacao',
                       'conhecimentos_tecnicos', 'certificacoes',
                       'outras_certificacoes', 'nivel_academico',
                       'nivel_ingles', 'nivel_espanhol', 'outro_idioma',
                       'cursos', 'cargo_atual', 'data_admissao',
                       'data_ultima_promocao', 'cv_pt']
df_applicants = df_applicants[features_applicants]
df_applicants = df_applicants.reset_index()
df_applicants = df_applicants.rename(columns={'index': 'id'})
# criacao de features de senioridade
df_applicants['senioridade'] = utils.mapear_senioridade(
    df_applicants['cargo_atual']
)

df_vagas['senioridade'] = utils.mapear_senioridade(
    df_vagas['nivel profissional']
)
# calculo de feature de experiência
df_applicants['tempo_exp'] = (pd.to_datetime('2025-07-01') -
                              pd.to_datetime(df_applicants['data_admissao'],
                                             dayfirst=True,
                                             errors='coerce')).dt.days/365.25
# considerando que valores faltantes são candidatos sem experiência
df_applicants['tempo_exp'] = df_applicants['tempo_exp'].fillna(0)

# tratamento das colunas de texto
features_applicants = ['area_atuacao', 'conhecimentos_tecnicos',
                       'objetivo_profissional', 'certificacoes',
                       'outras_certificacoes',
                       'nivel_academico', 'outro_idioma',
                       'cursos', 'cargo_atual', 'cv_pt']
utils.padroniza_texto(df_applicants, features_applicants)

features_vagas = ['titulo_vaga', 'vaga_sap',
                  'vaga_especifica_para_pcd',
                  'outro_idioma', 'areas_atuacao', 'principais_atividades',
                  'competencia_tecnicas_e_comportamentais', 'nivel_academico']
utils.padroniza_texto(df_vagas, features_vagas)

# tratamento das colunas de idiomas

# ---
# ENCODING DE IDIOMAS E EDUCAÇÃO (com nomes de colunas corretos)
# ---
from sklearn.preprocessing import OrdinalEncoder
language_features = ['nivel_ingles', 'nivel_espanhol']
idioma_encoders = {}
for lang in language_features:
    df_applicants[lang] = df_applicants[lang].fillna('desconhecido').replace('', 'desconhecido')
    df_vagas[lang] = df_vagas[lang].fillna('desconhecido').replace('', 'desconhecido')
    combined = pd.concat([df_applicants[[lang]], df_vagas[[lang]]], ignore_index=True)
    enc = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    enc.fit(combined[[lang]])
    idioma_encoders[lang] = enc
    df_applicants[f'{lang}_encoded'] = enc.transform(df_applicants[[lang]])
    df_vagas[f'{lang}_encoded'] = enc.transform(df_vagas[[lang]])

# Educação
# Preenche valores ausentes/vazios
df_applicants['nivel_academico'] = df_applicants['nivel_academico'].fillna('desconhecido').replace('', 'desconhecido')
df_vagas['nivel_academico'] = df_vagas['nivel_academico'].fillna('desconhecido').replace('', 'desconhecido')
combined_educ = pd.concat([df_applicants[['nivel_academico']], df_vagas[['nivel_academico']]], ignore_index=True)
educacao_encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
educacao_encoder.fit(combined_educ[['nivel_academico']])
df_applicants['nivel_academico_encoded'] = educacao_encoder.transform(df_applicants[['nivel_academico']])
df_vagas['nivel_academico_encoded'] = educacao_encoder.transform(df_vagas[['nivel_academico']])

# ---
# Salva modelo e artefatos
# ---
artifacts = {
    'ordinal_encoders': {
        'idioma_encoders': idioma_encoders,
        'educacao_encoder': educacao_encoder
    },
    # model_features will be set after X is defined
}

# tratamento dos regimes de contratação
# separação dos tipos de contratação que estavam como string única
df_vagas['tipo_contratacao_cleaned'] = df_vagas['tipo_contratacao'].fillna('')
df_vagas['tipo_contratacao_cleaned'] = (
    df_vagas['tipo_contratacao_cleaned']
    .apply(lambda x: [item.strip() for item in x.split(',') if item.strip()])
    )

# listando tipos únicos de contratação
tipos_contratacao = set()
for tipo in df_vagas['tipo_contratacao_cleaned']:
    for t in tipo:
        tipos_contratacao.add(t)

# coluna binária para cada categoria
for tipo in tipos_contratacao:
    # Limpa e normaliza o nome do tipo para criar um nome de coluna válido.
    # O 'tipo' original é preservado para a verificação na lista.
    tipo_normalizado = tipo.lower()
    tipo_normalizado = (
        unicodedata
        .normalize('NFKD', str(tipo_normalizado))
        .encode('ascii', 'ignore')
        .decode('utf-8')
    )
    tipo_normalizado = re.sub(r'[^a-zA-Z0-9\s]', '', str(tipo_normalizado))
    nome_coluna = f"contratacao_{tipo_normalizado.strip().replace(' ', '_')}"
    df_vagas[nome_coluna] = (
        df_vagas['tipo_contratacao_cleaned']
        .apply(lambda lista_tipos: 1 if tipo in lista_tipos else 0)
    )

df_vagas = df_vagas.drop(
    ['tipo_contratacao', 'tipo_contratacao_cleaned'],
    axis=1
    )

# tratamento de colunas binárias
df_applicants['pcd'] = (df_applicants['pcd'] == 'Sim').astype(int)
df_vagas['vaga_sap'] = (df_vagas['vaga_sap'] == 'Sim').astype(int)
df_vagas['vaga_especifica_para_pcd'] = (
    (df_vagas['vaga_especifica_para_pcd'] == 'Sim')
    .astype(int)
)

# criação de score para a variável target
mapeamento_situacao_candidato = {
        # Estágios Negativos / Sem Progresso
        '': 0.0,  # Para NaN ou vazio, representando sem informação/sem match
        'desistiu': 0.0,
        'recusado': 0.0,
        'nao aprovado pelo cliente': 0.0,
        'nao aprovado pelo rh': 0.0,
        'nao aprovado pelo requisitante': 0.0,
        'desistiu da contratacao': 0.0,
        'sem interesse nesta vaga': 0.0,

        # Estágios Iniciais / Baixo Progresso
        'prospect': 0.1,  # Estágio inicial, antes de 'Inscrito'
        'inscrito': 0.15,  # Candidato apenas aplicou
        'em avaliacao pelo rh': 0.2,  # Triagem inicial

        # Estágios Intermediários
        'encaminhado ao requisitante': 0.4,  # Passou da triagem inicial
        'entrevista tecnica': 0.5,
        'entrevista com cliente': 0.6,  # Ponto chave!

        # Estágios Finais / Alta Probabilidade de Match
        'aprovado': 0.7,  # Aprovado internamente ou em alguma etapa chave
        'encaminhar proposta': 0.8,
        'proposta aceita': 0.9,
        'documentacao clt': 0.92,  # Ultimos passos, quase lá
        'documentacao pj': 0.92,
        'documentacao cooperado': 0.92,

        # Estágios de Sucesso (match bem-sucedido)
        'contratado pela decision': 1.0,
        'contratado como hunting': 1.0,
    }

df_prospects['situacao_candidado'] = (
    df_prospects['situacao_candidado']
    .astype(str)
    .str.lower()
    .str.strip()
    .replace('nan', '')
)
df_prospects['target_var'] = (
    df_prospects['situacao_candidado']
    .map(mapeamento_situacao_candidato)
)
df_prospects.drop(columns=['situacao_candidado'], inplace=True)

# ---
# Merge dos dataframes
# ---
df_vagas_final = df_vagas.add_suffix('_vaga')
df_applicants_final = df_applicants.add_suffix('_cand')

df_prospects['id_cand'] = df_prospects['id_cand'].astype(str)
df_applicants_final['id_cand'] = df_applicants_final['id_cand'].astype(str)

df_merged = pd.merge(df_prospects,
                     df_applicants_final,
                     on='id_cand',
                     how='left'
                     )
df_merged = pd.merge(df_merged,
                     df_vagas_final,
                     on='id_vaga',
                     how='left'
                     )

# %%
# ---
# Criação dos embeddings dos campos texto
# ---
text_features_list = ['titulo', 'modalidade', 'objetivo_profissional_cand',
                      'outro_idioma_cand', 'area_atuacao_cand',
                      'conhecimentos_tecnicos_cand', 'certificacoes_cand',
                      'outras_certificacoes_cand', 'cargo_atual_cand',
                      'cv_pt_cand', 'titulo_vaga_vaga',
                      'nivel profissional_vaga', 'outro_idioma_vaga',
                      'areas_atuacao_vaga', 'principais_atividades_vaga',
                      'competencia_tecnicas_e_comportamentais_vaga']
df_embeddings = utils.expand_vector(df=df_merged,
                                    feature_list=text_features_list,
                                    model=model_word2vec,
                                    num_features=100)
df_final = pd.concat([df_merged, df_embeddings], axis=1)
to_cancel_list = ['nivel_ingles_cand', 'nivel_espanhol_cand',
                  'cursos_cand', 'data_admissao_cand',
                  'data_ultima_promocao_cand', 'nivel_ingles_vaga',
                  'nivel_espanhol_vaga', 'data_candidatura',
                  'ultima_atualizacao', 'nome', 'comentario',
                  'recrutador', 'cliente_vaga', 'solicitante_cliente_vaga']
df_final.drop(columns=to_cancel_list, inplace=True)
df_final = df_final.dropna()

# %%
# ---
# Cálculo das Features de Similaridade
# ---
utils.similaridade(
    df_final,
    'objetivo_profissional_cand',
    'titulo',
    'objetivo_sim'
)
utils.similaridade(
    df_final,
    'cargo_atual_cand',
    'titulo',
    'cargo_sim'
)
utils.similaridade(
    df_final,
    'area_atuacao_cand',
    'titulo',
    'exp_sim'
)
utils.similaridade(
    df_final,
    'outro_idioma_cand',
    'outro_idioma_vaga',
    'outro_idioma_sim'
)
utils.similaridade(
    df_final,
    'area_atuacao_cand',
    'areas_atuacao_vaga',
    'area_atuacao_sim'
)
utils.similaridade(
    df_final,
    'certificacoes_cand',
    'competencia_tecnicas_e_comportamentais_vaga',
    'certificacoes_sim'
)
utils.similaridade(
    df_final,
    'outras_certificacoes_cand',
    'competencia_tecnicas_e_comportamentais_vaga',
    'outras_certificacoes_sim'
)
utils.similaridade(
    df_final,
    'conhecimentos_tecnicos_cand',
    'competencia_tecnicas_e_comportamentais_vaga',
    'conhecimentos_tecnicos_sim'
)
utils.similaridade(
    df_final,
    'cv_pt_cand',
    'principais_atividades_vaga',
    'atividades_sim'
)
utils.similaridade(
    df_final,
    'cv_pt_cand',
    'competencia_tecnicas_e_comportamentais_vaga',
    'competencias_sim'
)

# %%
# similaridade para ordinal_encoder e para colunas binárias
df_final['ingles'] = (
    df_final['nivel_ingles_encoded_cand']
    - df_final['nivel_ingles_encoded_vaga']
)

df_final['espanhol'] = (
    df_final['nivel_espanhol_encoded_cand']
    - df_final['nivel_espanhol_encoded_vaga']
)

df_final['gap_senioridade'] = (
    df_final['senioridade_cand'] - df_final['senioridade_vaga']
)

df_final['possui_senioridade_minima'] = (
    df_final['senioridade_cand'] >= df_final['senioridade_vaga']
).astype(int)

df_final['possui_nivel_academico_minimo'] = (
    df_final['nivel_academico_encoded_cand']
    >= df_final['nivel_academico_encoded_vaga']
).astype(int)

# similaridade para features binárias
condicoes = [
    (
        df_final['vaga_especifica_para_pcd_vaga'] == 1)
    &
    (df_final['pcd_cand'] == 0),
    (df_final['vaga_especifica_para_pcd_vaga'] == 1)
    &
    (df_final['pcd_cand'] == 1)
]
valores = [0, 2]
df_final['compatibilidade_pcd'] = np.select(condicoes, valores, default=1)
# %%
# ---
# Definição de Dataframe final para o modelo
# ---
feature_list = config['feature_list'] + ['target_var']
df_final = df_final[feature_list]

# %%
# ---
# Treinamento do Modelo
# ---
X = df_final.drop(columns=['target_var'])
y = df_final['target_var']

X_train, X_test, y_train, y_test = train_test_split(X,
                                                    y,
                                                    test_size=0.2,
                                                    random_state=42
                                                    )

model = XGBRegressor(**config['model_params']['xgbregressor'])

utils.evaluation(model, X_train, y_train, X_test, y_test)

# %%
# Salvando Artefatos para Produção
MODEL_PATH = Path(__file__).resolve().parent / 'artifacts' / 'model.joblib'
ARTIFACTS_PATH = Path(__file__).resolve().parent / 'artifacts' / 'preprocessing_artifacts.joblib'
# Garante que o diretório existe antes de salvar
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
artifacts['model_features'] = X.columns.to_list()
artifacts['tipos_contratacao'] = list(tipos_contratacao)  # Salva a lista de tipos de contratação
joblib.dump(model, MODEL_PATH)
joblib.dump(artifacts, ARTIFACTS_PATH)