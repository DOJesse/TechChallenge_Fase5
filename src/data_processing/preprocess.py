"""
preprocess.py

Script para carregar e pré-processar os dados brutos (JSON) gerados no Datathon.
Inputs:
 - data/raw/vagas.json      # Jobs.json
 - data/raw/prospects.json  # Prospects.json
 - data/raw/applicants.json # Applicants.json

Outputs:
 - data/processed/dataset.csv
"""

import os
import json
import pandas as pd


def load_json(path):
    """Carrega um arquivo JSON a partir do caminho informado."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def process_jobs(path):
    """Lê e desnormaliza o JSON de vagas em um DataFrame."""
    raw = load_json(path)
    records = []
    for job_code, info in raw.items():
        base = {'job_code': job_code}
        base.update(info.get('informacoes_basicas', {}))
        base.update(info.get('perfil_vaga', {}))
        base.update(info.get('beneficios', {}))
        records.append(base)
    return pd.DataFrame(records)


def process_prospects(path):
    """Lê e desnormaliza o JSON de prospecções em um DataFrame."""
    raw = load_json(path)
    records = []
    for job_code, job in raw.items():
        for p in job.get('prospects', []):
            rec = {'job_code': job_code}
            rec.update(p)
            records.append(rec)
    return pd.DataFrame(records)


def process_applicants(path):
    """Lê e desnormaliza o JSON de candidatos em um DataFrame."""
    raw = load_json(path)
    records = []
    for candidate_code, info in raw.items():
        rec = {'candidate_code': candidate_code}
        if 'informacoes_pessoais' in info:
            rec.update(info['informacoes_pessoais'])
        if 'informacoes_profissionais' in info:
            rec.update(info['informacoes_profissionais'])
        if 'formacao_e_idiomas' in info:
            rec.update(info['formacao_e_idiomas'])
        rec['cv_pt'] = info.get('cv_pt')
        records.append(rec)
    return pd.DataFrame(records)


def merge_data(jobs_df, prospects_df, applicants_df):
    """Realiza o merge das três fontes em um único DataFrame."""
    df = prospects_df.merge(jobs_df, on='job_code', how='left')
    df = df.merge(applicants_df, left_on='codigo', right_on='candidate_code', how='left')
    return df


def main():
    base = os.path.dirname(os.path.dirname(__file__))
    raw_dir = os.path.join(base, 'data', 'raw')
    processed_dir = os.path.join(base, 'data', 'processed')
    os.makedirs(processed_dir, exist_ok=True)

    jobs_df = process_jobs(os.path.join(raw_dir, 'vagas.json'))
    prospects_df = process_prospects(os.path.join(raw_dir, 'prospects.json'))
    applicants_df = process_applicants(os.path.join(raw_dir, 'applicants.json'))

    df = merge_data(jobs_df, prospects_df, applicants_df)
    output_path = os.path.join(processed_dir, 'dataset.csv')
    df.to_csv(output_path, index=False)
    print(f'Dataset salvo em {output_path}')


if __name__ == '__main__':
    main()
