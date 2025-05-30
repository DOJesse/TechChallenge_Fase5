"""
Drift Monitor (drift_monitor.py)

Script para monitorar drift de dados do modelo de match candidato-vaga.
- Carrega dataset de referência e novo batch de dados processados.
- Utiliza pipeline savado para obter features.
- Calcula Population Stability Index (PSI) e teste de Kolmogorov-Smirnov (KS) para cada feature.
- Gera relatório de drift em CSV.

Requisitos:
- joblib, pandas, numpy, scipy
"""
import os
import sys
import pandas as pd
import numpy as np
import joblib
from scipy.stats import ks_2samp


def calculate_psi(expected, actual, buckets=10):
    """
    Calcula o Population Stability Index (PSI) entre duas distribuições.
    """
    expected = expected.dropna()
    actual = actual.dropna()
    # define bins pelo esperado
    breakpoints = np.percentile(expected, np.linspace(0, 100, buckets + 1))
    expected_percents = np.histogram(expected, bins=breakpoints)[0] / len(expected)
    actual_percents = np.histogram(actual, bins=breakpoints)[0] / len(actual)

    # evita divisão por zero
    def psi_term(e, a):
        if e == 0:
            return 0
        if a == 0:
            a = 1e-8
        return (e - a) * np.log(e / a)

    psi_values = [psi_term(e, a) for e, a in zip(expected_percents, actual_percents)]
    return np.sum(psi_values)


def monitor_drift(reference_df, new_df, feature_list):
    """
    Para cada feature na lista, calcula PSI e KS-test
    Retorna DataFrame com métricas.
    """
    records = []
    for col in feature_list:
        ref_col = reference_df[col]
        new_col = new_df[col]
        psi = calculate_psi(ref_col, new_col)
        ks_stat, ks_p = ks_2samp(ref_col.dropna(), new_col.dropna())
        records.append({
            'feature': col,
            'psi': psi,
            'ks_statistic': ks_stat,
            'ks_p_value': ks_p
        })
    return pd.DataFrame(records)


def main():
    # Ajuste de path
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    processed_dir = os.path.join(root, 'data', 'processed')
    artifacts_dir = os.path.join(root, 'src', 'models', 'artifacts')

    # Carrega datasets
    ref_df = pd.read_csv(os.path.join(processed_dir, 'dataset.csv'))
    # Novo batch: altere o nome conforme necessário
    new_data_path = os.path.join(processed_dir, 'new_data.csv')
    if not os.path.exists(new_data_path):
        print(f"Arquivo de novo batch não encontrado em {new_data_path}")
        sys.exit(1)
    new_df = pd.read_csv(new_data_path)

    # Carrega pipeline para obter features
    pipeline = joblib.load(os.path.join(artifacts_dir, 'pipeline.joblib'))
    feature_cols = pipeline['feature_cols']

    # Executa monitoramento
    drift_report = monitor_drift(ref_df, new_df, feature_cols)

    # Salva relatório
    report_path = os.path.join(root, 'src', 'monitoring', 'drift_report.csv')
    drift_report.to_csv(report_path, index=False)
    print(f"Relatório de drift salvo em {report_path}")


if __name__ == '__main__':
    main()
