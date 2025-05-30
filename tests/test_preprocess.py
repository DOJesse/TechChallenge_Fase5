import pytest
import json
import pandas as pd
from src.data_processing.preprocess import (
    load_json, process_jobs, process_prospects,
    process_applicants, merge_data
)


def write_json(tmp_path, filename, data):
    path = tmp_path / filename
    path.write_text(json.dumps(data))
    return str(path)


def test_process_jobs(tmp_path):
    sample = {
        "job1": {
            "informacoes_basicas": {"title": "Dev"},
            "perfil_vaga": {"level": "Junior"},
            "beneficios": {"health": "Yes"}
        }
    }
    path = write_json(tmp_path, "jobs.json", sample)
    df = process_jobs(path)
    assert isinstance(df, pd.DataFrame)
    assert df.loc[0, 'job_code'] == "job1"
    assert df.loc[0, 'title'] == "Dev"
    assert df.loc[0, 'level'] == "Junior"
    assert df.loc[0, 'health'] == "Yes"


def test_process_prospects(tmp_path):
    sample = {"job1": {"prospects": [{"codigo": "c1", "situacao_candidado": "applied"}]}}
    path = write_json(tmp_path, "prospects.json", sample)
    df = process_prospects(path)
    assert list(df.columns) == ["job_code", "codigo", "situacao_candidado"]
    assert df.loc[0, 'job_code'] == "job1"
    assert df.loc[0, 'codigo'] == "c1"


def test_process_applicants(tmp_path):
    sample = {
        "c1": {
            "informacoes_pessoais": {"nome": "Alice"},
            "informacoes_profissionais": {"empresa": "X"},
            "formacao_e_idiomas": {"nivel_academico": "Master"},
            "cv_pt": "My CV"
        }
    }
    path = write_json(tmp_path, "applicants.json", sample)
    df = process_applicants(path)
    assert 'nome' in df.columns
    assert df.loc[0, 'candidate_code'] == "c1"
    assert df.loc[0, 'nivel_academico'] == "Master"
    assert df.loc[0, 'cv_pt'] == "My CV"


def test_merge_data():
    jobs = pd.DataFrame([{'job_code': 'job1', 'title': 'Dev'}])
    prospects = pd.DataFrame([{'job_code': 'job1', 'codigo': 'c1'}])
    applicants = pd.DataFrame([{'candidate_code': 'c1', 'nome': 'Alice'}])
    df = merge_data(jobs, prospects, applicants)
    assert df.loc[0, 'title'] == 'Dev'
    assert df.loc[0, 'nome'] == 'Alice'
