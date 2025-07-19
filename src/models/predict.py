# predict.py

import pandas as pd
import numpy as np
import joblib
import re
import unicodedata
from gensim.models import KeyedVectors
from pathlib import Path
from typing import Dict, Any

# Importa as funções de pré-processamento do seu arquivo de utilitários
import utils

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
        self.model = joblib.load(model_path)

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
        # 1. Normalização dos dicionários
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

        # ---
        # 2. Filtragem de features
        # ---
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
        for lang, encoder in self.ordinal_encoders.get('idioma_encoders', {}).items():
            df_applicants[lang] = df_applicants[lang].fillna('Nenhum')
            df_vagas[lang] = df_vagas[lang].fillna('Nenhum')
            df_applicants[f'{lang}_encoded_cand'] = encoder.transform(df_applicants[[lang]])
            df_vagas[f'{lang}_encoded_vaga'] = encoder.transform(df_vagas[[lang]])

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
            df_applicants['nivel_academico_encoded_cand'] = educ_encoder.transform(df_applicants[['nivel_academico']])
            df_vagas['nivel_academico_encoded_vaga'] = educ_encoder.transform(df_vagas[['nivel_academico']])

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
            df_final['nivel_ingles_encoded_cand_cand']
            - df_final['nivel_ingles_encoded_vaga_vaga']
        )

        df_final['espanhol'] = (
            df_final['nivel_espanhol_encoded_cand_cand']
            - df_final['nivel_espanhol_encoded_vaga_vaga']
        )

        df_final['gap_senioridade'] = (
            df_final['senioridade_cand'] - df_final['senioridade_vaga']
        )

        df_final['possui_senioridade_minima'] = (
            df_final['senioridade_cand'] >= df_final['senioridade_vaga']
        ).astype(int)

        df_final['possui_nivel_academico_minimo'] = (
            df_final['nivel_academico_encoded_cand_cand']
            >= df_final['nivel_academico_encoded_vaga_vaga']
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
        
        # Retorna o score (o [0] pega o primeiro valor do array de predição)
        return prediction[0]

# --- Bloco de Execução Principal (Exemplo de como usar a classe) ---
if __name__ == '__main__':
    # Define os caminhos de forma robusta a partir da localização do script
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    
    # Caminhos para os artefatos salvos na pasta 'artifacts'
    MODEL_PATH = PROJECT_ROOT / 'artifacts' / 'model.joblib'
    ARTIFACTS_PATH = PROJECT_ROOT / 'artifacts' / 'preprocessing_artifacts.joblib'
    W2V_MODEL_PATH = PROJECT_ROOT / 'src' / 'word2vec' / 'cbow_s100.txt'

    # 1. Inicializa a pipeline (carrega os modelos e artefatos em memória)
    pipeline = PredictionPipeline(
        model_path=MODEL_PATH,
        artifacts_path=ARTIFACTS_PATH,
        w2v_model_path=W2V_MODEL_PATH
    )

    # 2. Define os dados de entrada (exemplo)
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
            "titulo_profissional": "Analista de Dados Sênior",
            "area_atuacao": "Tecnologia da Informação",
            "conhecimentos_tecnicos": "python, SQL, Power BI, Machine Learning, Git",
            "certificacoes": "Certificação React Developer",
            "outras_certificacoes": "Scrum Master",
            "remuneracao": "A combinar",
            "nivel_profissional": "Sênior"
            },
            "formacao_e_idiomas": {
            "nivel_academico": "Pós Graduação Completo",
            "instituicao_ensino_superior": "Universidade Paulista",
            "cursos": "Ciência da Computação",
            "ano_conclusao": "0",
            "nivel_ingles": "Fluente",
            "nivel_espanhol": "Intermediário",
            "outro_idioma": "Francês - Básico",
            "outro_curso": "Outro Curso:"
            },
            "cargo_atual":  {
            "id_ibrati": "51819",
            "email_corporativo": "",
            "cargo_atual": "Analista de Dados II",
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

    nova_vaga = {
        "5186": {
            "informacoes_basicas": {
            "data_requicisao": "10-07-2024",
            "limite_esperado_para_contratacao": "30-09-2024",
            "titulo_vaga": "Analista de Dados Sênior",
            "vaga_sap": "Sim",
            "cliente": "Global Analytics Inc.",
            "solicitante_cliente": "Dr. Lucas Martins",
            "empresa_divisao": "Insights Solutions Brasil",
            "requisitante": "Fernanda Costa",
            "analista_responsavel": "Sr. Gabriel Mendes",
            "tipo_contratacao": "PJ",
            "prazo_contratacao": "1 ano",
            "objetivo_vaga": "Fortalecer a equipe de dados com expertise em análise avançada.",
            "prioridade_vaga": "Alta",
            "origem_vaga": "Website Corporativo",
            "superior_imediato": "Gerente de Análise de Dados",
            "nome": "Sofia Almeida",
            "telefone": "(11) 99876-5432"
            },
            "perfil_vaga": {
            "pais": "Brasil",
            "estado": "São Paulo",
            "cidade": "São Paulo",
            "bairro": "Pinheiros",
            "regiao": "Zona Oeste",
            "local_trabalho": "Híbrido (3 dias presencial)",
            "vaga_especifica_para_pcd": "Não",
            "faixa_etaria": "De: 28 Até: 45",
            "horario_trabalho": "Comercial (09h - 18h)",
            "nivel profissional": "Sênior",
            "nivel_academico": "Pós graduação Completo",
            "nivel_ingles": "Fluente",
            "nivel_espanhol": "Intermediário",
            "outro_idioma": "Alemão - Básico",
            "areas_atuacao": "Tecnologia - Análise de Dados",
            "principais_atividades": "• Desenvolver e implementar modelos de dados complexos.\n• Realizar análises estatísticas e preditivas para identificar tendências e padrões.\n• Criar dashboards e relatórios interativos utilizando ferramentas de BI.\n• Colaborar com equipes de produto e engenharia para definir requisitos de dados.\n• Apresentar insights e recomendações para stakeholders.\n• Otimizar pipelines de dados e garantir a qualidade dos dados.",
            "competencia_tecnicas_e_comportamentais": "Required Skills:\n• Experiência comprovada com SQL, Python (bibliotecas Pandas, NumPy, Scikit-learn) e R.\n• Proficiência em ferramentas de BI como Tableau, Power BI ou Looker.\n• Conhecimento em bancos de dados relacionais e não relacionais (SQL Server, PostgreSQL, MongoDB).\n• Familiaridade com ambientes de nuvem (AWS, Azure, GCP) e big data (Spark, Hadoop).\n• Habilidades analíticas e de resolução de problemas.\n• Forte comunicação e capacidade de trabalhar em equipe.",
            "demais_observacoes": "Ambiente de trabalho dinâmico e focado em inovação. Oportunidade de atuação em projetos estratégicos com impacto global.",
            "viagens_requeridas": "Ocasionais para eventos ou reuniões de equipe.",
            "equipamentos_necessarios": "Notebook de alta performance fornecido pela empresa."
            },
            "beneficios": {
            "valor_venda": "15000",
            "valor_compra_1": "R$ 12000",
            "valor_compra_2": "R$ 13000"
            }
        }
    }

    # 3. Faz a predição
    score = pipeline.predict(candidate_data=novo_candidato, vacancy_data=nova_vaga)

    print("\n" + "="*30)
    print(f"  Score de Match Predito: {score:.4f}")
    print("="*30)