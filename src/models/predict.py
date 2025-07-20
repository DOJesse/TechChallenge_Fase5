import pandas as pd
import numpy as np
import joblib
import re
import unicodedata
from gensim.models import KeyedVectors
from pathlib import Path
from typing import Dict, Any
import shap

# Importa as funções de pré-processamento do seu arquivo de utilitários
from src.models import utils

class PredictionPipeline:
    """
    Classe para encapsular o pipeline de predição.
    Carrega os artefatos de treinamento e aplica a pipeline em novos dados.
    """
    def __init__(self, model_path: str, artifacts_path: str, w2v_model_path: str):
        """
        Inicializa o pipeline carregando todos os artefatos necessários.

        Args:
            model_path (str): Caminho para o arquivo do modelo treinado (ex: 'model.joblib').
            artifacts_path (str): Caminho para os artefatos de pré-processamento 
                                  (encoders, listas de colunas, etc.).
            w2v_model_path (str): Caminho para o modelo Word2Vec pré-treinado.
        """
        print("Inicializando o pipeline de predição...")

        # Carrega o modelo de machine learning
        try:
            self.model = joblib.load(model_path)
        except Exception as e:
            print(f"Erro ao carregar o modelo: {e}")
            raise

        # Carrega os artefatos de pré-processamento
        try:
            artifacts = joblib.load(artifacts_path)
            if isinstance(artifacts, dict):
                self.ordinal_encoders = artifacts.get('ordinal_encoders', {})
                self.model_features_order = artifacts.get('model_features', [])
                self.tipos_contratacao = artifacts.get('tipos_contratacao', [])
            else:
                print("Aviso: Artefatos corrompidos, usando valores padrão")
                self.ordinal_encoders = {}
                self.model_features_order = []
                self.tipos_contratacao = []
        except Exception as e:
            print(f"Erro ao carregar artefatos: {e}, usando valores padrão")
            self.ordinal_encoders = {}
            self.model_features_order = []

        # Carrega o modelo Word2Vec
        self.model_w2v = KeyedVectors.load_word2vec_format(w2v_model_path)
        self.NUM_FEATURES_W2V = self.model_w2v.vector_size

        print("Pipeline pronto para uso.")

    def _prepare_data(self, candidate_data: Dict[str, Any], vacancy_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Executa toda a pipeline de pré-processamento e feature engineering.
        """
        # Converte os dicionários de entrada em DataFrames
        df_applicants = pd.DataFrame.from_dict(candidate_data, orient='index')
        df_vagas = pd.DataFrame.from_dict(vacancy_data, orient='index')

        # ---
        # 1. Normalização dos dicionários (com tratamento de chaves ausentes)
        # ---
        def safe_json_normalize(df, key_or_keys):
            """Normaliza um campo JSON se a chave existir, senão retorna um DF vazio."""
            keys = [key_or_keys] if isinstance(key_or_keys, str) else key_or_keys
            
            key_to_use = None
            for key in keys:
                if key in df.columns:
                    key_to_use = key
                    break
            
            if key_to_use:
                # Garante que a coluna contenha dicionários, substituindo nulos/outros por dict vazio
                data_series = df[key_to_use].apply(lambda x: x if isinstance(x, dict) else {})
                return pd.json_normalize(data_series), key_to_use
            
            return pd.DataFrame(), None

        df_infos_basicas, used_key_infos = safe_json_normalize(df_applicants, ['infos_basicas', 'informacoes_basicas'])
        df_informacoes_pessoais, used_key_pessoais = safe_json_normalize(df_applicants, 'informacoes_pessoais')
        df_informacoes_profissionais, used_key_profissionais = safe_json_normalize(df_applicants, 'informacoes_profissionais')
        df_formacao_e_idiomas, used_key_formacao = safe_json_normalize(df_applicants, 'formacao_e_idiomas')
        df_cargo_atual, used_key_cargo = safe_json_normalize(df_applicants, 'cargo_atual')

        # Coleta as chaves que foram usadas para poder removê-las
        keys_to_drop_cand = [k for k in [used_key_infos, used_key_pessoais, used_key_profissionais, used_key_formacao, used_key_cargo] if k]

        df_applicants = pd.concat(
            [
                df_applicants.drop(columns=keys_to_drop_cand, errors='ignore'),
                df_infos_basicas,
                df_informacoes_pessoais,
                df_informacoes_profissionais,
                df_formacao_e_idiomas,
                df_cargo_atual
            ],
            axis=1
        )

        df_informacoes_basicas_vaga, used_key_vaga_basicas = safe_json_normalize(df_vagas, 'informacoes_basicas')
        df_perfil_vaga, used_key_vaga_perfil = safe_json_normalize(df_vagas, 'perfil_vaga')
        df_beneficios, used_key_vaga_beneficios = safe_json_normalize(df_vagas, 'beneficios')
        
        keys_to_drop_vaga = [k for k in [used_key_vaga_basicas, used_key_vaga_perfil, used_key_vaga_beneficios] if k]

        df_vagas = pd.concat(
            [
                df_vagas.drop(columns=keys_to_drop_vaga, errors='ignore'),
                df_informacoes_basicas_vaga,
                df_perfil_vaga,
                df_beneficios
            ],
            axis=1
        )

        # ---
        # 2. Filtragem de features
        # ---
        # Garante que todas as colunas esperadas existam, preenchendo com um valor padrão (vazio) se não existirem
        all_expected_cand_features = [
            'pcd', 'objetivo_profissional', 'area_atuacao', 'conhecimentos_tecnicos', 
            'certificacoes', 'outras_certificacoes', 'nivel_academico', 'nivel_ingles', 
            'nivel_espanhol', 'outro_idioma', 'cursos', 'cargo_atual', 'data_admissao', 
            'data_ultima_promocao', 'cv_pt'
        ]
        for col in all_expected_cand_features:
            if col not in df_applicants.columns:
                df_applicants[col] = '' # ou np.nan, dependendo do tratamento downstream

        all_expected_vaga_features = [
            'titulo_vaga', 'vaga_sap', 'cliente', 'solicitante_cliente',
            'tipo_contratacao', 'vaga_especifica_para_pcd', 'nivel profissional', 
            'nivel_academico', 'nivel_ingles', 'nivel_espanhol', 'outro_idioma', 
            'areas_atuacao', 'principais_atividades', 'competencia_tecnicas_e_comportamentais'
        ]
        for col in all_expected_vaga_features:
            if col not in df_vagas.columns:
                df_vagas[col] = '' # ou np.nan

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

        # ---
        # 3. Feature Engineering
        # ---
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
        idioma_encoders = self.ordinal_encoders.get('idioma_encoders', {})
        if not idioma_encoders:
            # Se não há encoders, criar colunas encodadas com valores padrão
            for lang in ['nivel_ingles', 'nivel_espanhol']:
                if lang in df_applicants.columns:
                    df_applicants[f'{lang}_encoded'] = 0
                    df_applicants = df_applicants.drop(columns=[lang])
                if lang in df_vagas.columns:
                    df_vagas[f'{lang}_encoded'] = 0
                    df_vagas = df_vagas.drop(columns=[lang])
        else:
            for lang, encoder in idioma_encoders.items():
                df_applicants[lang] = df_applicants[lang].fillna('Nenhum')
                df_vagas[lang] = df_vagas[lang].fillna('Nenhum')
                df_applicants[f'{lang}_encoded'] = encoder.transform(df_applicants[[lang]])
                df_vagas[f'{lang}_encoded'] = encoder.transform(df_vagas[[lang]])
                # Remove as colunas originais de string após o encoding
                df_applicants = df_applicants.drop(columns=[lang])
                df_vagas = df_vagas.drop(columns=[lang])

        # Educação
        educ_encoder = self.ordinal_encoders.get('educacao_encoder')
        if educ_encoder:
            df_applicants['nivel_academico'] = (
            df_applicants['nivel_academico']
            .replace([np.nan, None, 'nan', 'NaN'], '')
            .fillna('')
            )
            df_vagas['nivel_academico'] = (
                df_vagas['nivel_academico']
                .replace([np.nan, None, 'nan', 'NaN'], '')
                .fillna('')
            )
            df_applicants['nivel_academico_encoded'] = educ_encoder.transform(df_applicants[['nivel_academico']])
            df_vagas['nivel_academico_encoded'] = educ_encoder.transform(df_vagas[['nivel_academico']])
            # Remove as colunas originais de string após o encoding
            df_applicants = df_applicants.drop(columns=['nivel_academico'])
            df_vagas = df_vagas.drop(columns=['nivel_academico'])
        else:
            # Se não há encoder, criar colunas encodadas com valores padrão
            df_applicants['nivel_academico_encoded'] = 0
            df_vagas['nivel_academico_encoded'] = 0
            # Remove as colunas originais mesmo sem encoder
            if 'nivel_academico' in df_applicants.columns:
                df_applicants = df_applicants.drop(columns=['nivel_academico'])
            if 'nivel_academico' in df_vagas.columns:
                df_vagas = df_vagas.drop(columns=['nivel_academico'])

        # tratamento dos regimes de contratação
        # separação dos tipos de contratação que estavam como string única
        df_vagas['tipo_contratacao_cleaned'] = df_vagas['tipo_contratacao'].fillna('')
        df_vagas['tipo_contratacao_cleaned'] = (
            df_vagas['tipo_contratacao_cleaned']
            .apply(lambda x: [item.strip() for item in x.split(',') if item.strip()])
            )

        # CRÍTICO: Usa a lista de tipos de contratação salva do treinamento
        # para garantir que as colunas sejam consistentes.
        for tipo_contrato in self.tipos_contratacao:
            tipo_normalizado = tipo_contrato.lower()
            tipo_normalizado = (
                unicodedata
                .normalize('NFKD', str(tipo_normalizado))
                .encode('ascii', 'ignore')
                .decode('utf-8')
            )
            nome_coluna = f"contratacao_{re.sub(r'[^a-zA-Z0-9s]', '', tipo_normalizado).strip().replace(' ', '_')}"
            df_vagas[nome_coluna] = (
                df_vagas['tipo_contratacao_cleaned']
                .apply(lambda lista_tipos: 1 if tipo_contrato in lista_tipos else 0)
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

        # ---
        # 4. Merge dos dataframes
        # ---
        df_vagas_final = df_vagas.add_suffix('_vaga')
        df_applicants_final = df_applicants.add_suffix('_cand')

        df_applicants_final['key'] = 1
        df_vagas_final['key'] = 1
        df_merged = pd.merge(df_applicants_final, df_vagas_final, on='key').drop('key', axis=1)

        # ---
        # 5. Embeddings e Similaridades
        # ---
        text_features_list = ['objetivo_profissional_cand',
                            'outro_idioma_cand', 'area_atuacao_cand',
                            'conhecimentos_tecnicos_cand', 'certificacoes_cand',
                            'outras_certificacoes_cand', 'cargo_atual_cand',
                            'cv_pt_cand', 'titulo_vaga_vaga',
                            'nivel profissional_vaga', 'outro_idioma_vaga',
                            'areas_atuacao_vaga', 'principais_atividades_vaga',
                            'competencia_tecnicas_e_comportamentais_vaga']
        df_embeddings = utils.expand_vector(df=df_merged,
                                            feature_list=text_features_list,
                                            model=self.model_w2v,
                                            num_features=100)
        df_final = pd.concat([df_merged, df_embeddings], axis=1)
        df_final = df_final.dropna()

        utils.similaridade(
            df_final,
            'objetivo_profissional_cand',
            'titulo_vaga_vaga',
            'objetivo_sim'
        )
        utils.similaridade(
            df_final,
            'cargo_atual_cand',
            'titulo_vaga_vaga',
            'cargo_sim'
        )
        utils.similaridade(
            df_final,
            'area_atuacao_cand',
            'titulo_vaga_vaga',
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

        df_final['possui_nivel_ingles_minimo'] = (
            df_final['nivel_ingles_encoded_cand']
            >= df_final['nivel_ingles_encoded_vaga']
        ).astype(int)

        df_final['possui_nivel_espanhol_minimo'] = (
            df_final['nivel_espanhol_encoded_cand']
            >= df_final['nivel_espanhol_encoded_vaga']
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

        # ---
        # 6. Definição de Dataframe final para o modelo
        # ---
        # CRÍTICO: Garante que o dataframe final tenha exatamente as mesmas colunas
        # e na mesma ordem que o modelo foi treinado.
        final_features_df = pd.DataFrame(columns=self.model_features_order, index=df_final.index)

        # Copia os valores das colunas que existem
        for col in self.model_features_order:
            if col in df_final.columns:
                final_features_df[col] = df_final[col]

        # Preenche colunas faltantes (ex: tipos de contrato não presentes nesta vaga) com 0
        # Suprimir o warning de downcasting temporariamente
        with pd.option_context('future.no_silent_downcasting', True):
            final_features_df = final_features_df.fillna(0)

        return final_features_df

    def predict(self, candidate_data: Dict[str, Any], vacancy_data: Dict[str, Any]) -> float:
        """
        Recebe os dados brutos de um candidato e de uma vaga e retorna o score de match.
        """
        # Prepara os dados usando a pipeline interna
        processed_df = self._prepare_data(candidate_data, vacancy_data)
        # Faz a predição
        prediction = self.model.predict(processed_df)
        
        explainer = shap.TreeExplainer(self.model)

        # Pegue a linha de dados do candidato/vaga que você quer analisar
        # Supondo que 'processed_df' seja o DataFrame com os dados prontos para predição
        dados_para_explicar = processed_df.iloc[[0]] 

        # Calcule os valores SHAP
        shap_values = explainer.shap_values(dados_para_explicar)

        # Visualize a contribuição de cada feature
        plot = shap.force_plot(explainer.expected_value, shap_values[0], processed_df.iloc[0], show=False)
            
        # Salva o plot em um arquivo HTML
        shap.save_html('shap_plot.html', plot)
        # Retorna o score e os valores SHAP como tupla
        return prediction[0], shap_values

# --- Bloco de Execução Principal (Exemplo de como usar a classe) ---
if __name__ == '__main__':
    # Define os caminhos de forma robusta a partir da localização do script
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    
    # Caminhos para os artefatos salvos na pasta 'artifacts'
    MODEL_PATH = PROJECT_ROOT / 'src' / 'models' / 'artifacts' / 'model.joblib'
    ARTIFACTS_PATH = PROJECT_ROOT / 'src' / 'models' / 'artifacts' / 'preprocessing_artifacts.joblib'
    W2V_MODEL_PATH = PROJECT_ROOT / 'src' / 'word2vec' / 'cbow_s100.txt'

    # 1. Inicializa a pipeline (carrega os modelos e artefatos em memória)
    pipeline = PredictionPipeline(
        model_path=MODEL_PATH,
        artifacts_path=ARTIFACTS_PATH,
        w2v_model_path=W2V_MODEL_PATH
    )

    # 2. Define os dados de entrada (exemplo)
    nova_vaga = {
        "4546": {
        "informacoes_basicas": {
            "data_requicisao": "11-03-2021",
            "limite_esperado_para_contratacao": "00-00-0000",
            "titulo_vaga": "Java SR, PL -2021-2602800",
            "vaga_sap": "Não",
            "cliente": "Gonzalez and Sons",
            "solicitante_cliente": "Valentim Duarte",
            "empresa_divisao": "Decision São Paulo",
            "requisitante": "Vitória Melo",
            "analista_responsavel": "Ana Camargo",
            "tipo_contratacao": "PJ/Autônomo",
            "prazo_contratacao": "",
            "objetivo_vaga": "Contratação",
            "prioridade_vaga": "Média: Média complexidade 6 a 10 dias",
            "origem_vaga": "Nova Posição",
            "superior_imediato": "Superior Imediato:",
            "nome": "",
            "telefone": ""
        },
        "perfil_vaga": {
            "pais": "Brasil",
            "estado": "São Paulo",
            "cidade": "São Paulo",
            "bairro": "",
            "regiao": "",
            "local_trabalho": "2000",
            "vaga_especifica_para_pcd": "Não",
            "faixa_etaria": "De: Até:",
            "horario_trabalho": "",
            "nivel profissional": "Especialista",
            "nivel_academico": "Doutorado Completo",
            "nivel_ingles": "Avançado",
            "nivel_espanhol": "Nenhum",
            "outro_idioma": "",
            "areas_atuacao": "Financeira/Controladoria-",
            "principais_atividades": "Conhecimentos: Java, Spring boot, API Rest, AngularJs, Jquery, JavaScript, Css, Html5 , Jira, Confluence, Kafka, Cassandra, AWS, esteira devops (Jenkins).\nConhecimento em Metodologia Ágil.\nConhecimento Ambiente Itaú.\n\nKey skills required for the job are:\n\nCore Java-L3 (Mandatory)\nJavaScript-L3\nHTML 5-L3\n\nAs a Domain Consultant in one of the industry verticals, you are responsible for implementation of roadmaps for business process analysis, data analysis, diagnosis of gaps, business requirements and functional definitions, best practices application, meeting facilitation, and contributes to projectplanning. You are expected to contribute to solution building for the client and practice. Should be able to handle higher scale and complexity and proactive in client interactions.\n\nMinimum work experience:5 - 8 Years\n\nProficiency in English Language is Desirable",
            "competencia_tecnicas_e_comportamentais": "Conhecimentos: Java, Spring boot, API Rest, AngularJs, Jquery, JavaScript, Css, Html5 , Jira, Confluence, Kafka, Cassandra, AWS, esteira devops (Jenkins).\nConhecimento em Metodologia Ágil.\nConhecimento Ambiente Itaú.",
            "habilidades_comportamentais_necessarias": "Remoto,",
            "demais_observacoes": "",
            "viagens_requeridas": ""
        },
        "beneficios": {
            "valor_venda": "93,00 -",
            "valor_compra_1": "hora",
            "valor_compra_2": ""
        }
    }
    }

    novo_candidato = {
        "31001": {
            "infos_basicas": {
            "telefone_recado": "",
            "telefone": "(21) 98765-4321",
            "objetivo_profissional": "Desenvolver soluções inovadoras na área de tecnologia.",
            "data_criacao": "15-06-2023 10:30:00",
            "inserido_por": "Pedro Silva",
            "email": "ana.silva@email.com",
            "local": "Rio de Janeiro",
            "sabendo_de_nos_por": "Indicação",
            "data_atualizacao": "15-06-2023 10:30:00",
            "codigo_profissional": "31001",
            "nome": "Ana Silva"
            },
            "informacoes_pessoais": {
            "data_aceite": "2023-06-15",
            "nome": "Ana Silva",
            "cpf": "123.456.789-00",
            "fonte_indicacao": "Amigo",
            "email": "ana.silva@email.com",
            "email_secundario": "ana.contato@email.com",
            "data_nascimento": "1995-03-20",
            "telefone_celular": "(21) 98765-4321",
            "telefone_recado": "(21) 91234-5678",
            "sexo": "Feminino",
            "estado_civil": "Solteira",
            "pcd": "Não",
            "endereco": "Rua das Flores, 123, Centro, Rio de Janeiro - RJ",
            "skype": "ana.silva.skype",
            "url_linkedin": "https://www.linkedin.com/in/anasylva",
            "facebook": ""
            },
            "informacoes_profissionais": {
            "titulo_profissional": "Analista de Dados Júnior",
            "area_atuacao": "Tecnologia da Informação",
            "conhecimentos_tecnicos": "Javascript, React, SQL, Python, HTML, CSS, Metodologias Ágeis",
            "certificacoes": "Certificação React Developer",
            "outras_certificacoes": "Scrum Master",
            "remuneracao": "A combinar",
            "nivel_profissional": "Júnior"
            },
            "formacao_e_idiomas": {
            "nivel_academico": "Graduação Completo",
            "instituicao_ensino_superior": "Universidade Paulista",
            "cursos": "Ciência da Computação",
            "ano_conclusao": "0",
            "nivel_ingles": "Nenhum",
            "nivel_espanhol": "Básico",
            "outro_idioma": "Francês - Básico",
            "outro_curso": "Outro Curso:"
            },
            "cargo_atual":  {
            "id_ibrati": "51819",
            "email_corporativo": "",
            "cargo_atual": "Analista de Projetos I",
            "projeto_atual": "",
            "cliente": "DECISION IBM 15 07",
            "unidade": "Decision São Paulo",
            "data_admissao": "24-05-2018",
            "data_ultima_promocao": "24-05-2018",
            "nome_superior_imediato": "",
            "email_superior_imediato": ""
        },
            "cv_pt": "Desenvolvedora Frontend Sênior com 5 anos de experiência em criação de interfaces de usuário, sql avançado, python, responsivas e de alta performance. Proficiente em React, JavaScript, HTML, CSS e metodologias ágeis. Experiência em liderança de equipes e mentoria de desenvolvedores juniores. Apaixonada por tecnologia e sempre em busca de novos desafios. \n\n**Experiência Profissional:**\n\n* **Tech Solutions Ltda.** (Jan/2022 - Atualmente)\n    * Desenvolvedora Frontend Sênior\n    * Responsável pelo desenvolvimento e manutenção de aplicações web utilizando React e Redux.\n    * Liderança técnica de uma equipe de 3 desenvolvedores.\n    * Otimização de performance e experiência do usuário.\n\n* **Web Innovators S.A.** (Jul/2019 - Dez/2021)\n    * Desenvolvedora Frontend Pleno\n    * Desenvolvimento de componentes reutilizáveis em React.\n    * Colaboração com equipes de design e backend.\n\n**Formação Acadêmica:**\n\n* **Pós-graduação em Engenharia de Software**\n    * Universidade Federal do Rio de Janeiro (2021 - 2022)\n\n* **Bacharelado em Ciência da Computação**\n    * Universidade Estadual do Rio de Janeiro (2015 - 2019)\n\n**Idiomas:**\n\n* Português (Nativo)\n* Inglês (Fluente)\n* Espanhol (Intermediário)\n* Francês (Básico)\n\n**Certificações:**\n\n* React Developer Certification\n* Certified Scrum Master",
            "cv_en": "Senior Frontend Developer with 5 years of experience in creating responsive and high-performance user interfaces. Proficient in React, JavaScript, HTML, CSS, and agile methodologies. Experienced in team leadership and mentoring junior developers. Passionate about technology and always seeking new challenges.\n\n**Professional Experience:**\n\n* **Tech Solutions Ltda.** (Jan/2022 - Present)\n    * Senior Frontend Developer\n    * Responsible for the development and maintenance of web applications using React and Redux.\n    * Technical leadership of a team of 3 developers.\n    * Optimization of performance and user experience.\n\n* **Web Innovators S.A.** (Jul/2019 - Dec/2021)\n    * Frontend Developer\n    * Development of reusable components in React.\n    * Collaboration with design and backend teams.\n\n**Education:**\n\n* **Postgraduate in Software Engineering**\n    * Federal University of Rio de Janeiro (2021 - 2022)\n\n* **Bachelor's Degree in Computer Science**\n    * State University of Rio de Janeiro (2015 - 2019)\n\n**Languages:**\n\n* Portuguese (Native)\n* English (Fluent)\n* Spanish (Intermediate)\n* French (Basic)\n\n**Certifications:**\n\n* React Developer Certification\n* Certified Scrum Master"
        }
    }

    # 3. Faz a predição
    score, shap_values = pipeline.predict(candidate_data=novo_candidato, vacancy_data=nova_vaga)

    print("\n" + "="*30)
    print("\n" + "="*30)
    print(f"  Score de Match Predito: {score:.4f}")
    print("="*30)