from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
RAW_SELENIUM_DIR = BASE_DIR / "data" / "raw" / "selenium"
RESULTS_DIR = BASE_DIR / "results"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

FLOW_CANDIDATES = [
    RAW_SELENIUM_DIR / "metrics_fluxo.csv",
    RESULTS_DIR / "metrics_fluxo.csv",
]

OPTIONAL_CANDIDATES = {
    "metrics_carga": [
        RAW_SELENIUM_DIR / "metrics_carga.csv",
        RESULTS_DIR / "metrics_carga.csv",
    ],
    "metrics_erros": [
        RAW_SELENIUM_DIR / "metrics_erros.csv",
        RESULTS_DIR / "metrics_erros.csv",
    ],
}

SUMMARY_FILE = PROCESSED_DIR / "resumo_tempos_observados.csv"
MODEL_INPUTS_FILE = PROCESSED_DIR / "model_inputs.json"

TIME_COLUMN_ALIASES = {
    "tempo_login": ["tempo_login", "login_time", "tempo_autenticacao"],
    "tempo_solicitacao": [
        "tempo_solicitacao",
        "tempo_cenario",
        "tempo_requerimento",
        "tempo_envio_solicitacao",
    ],
    "tempo_total": ["tempo_total", "tempo_fluxo", "duracao_total"],
}


def first_existing_path(candidates: list[Path]) -> Path | None:
    for path in candidates:
        if path.exists():
            return path
    return None


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(column).strip() for column in df.columns]
    for column in df.columns:
        if df[column].dtype == "object":
            df[column] = df[column].astype(str).str.strip()
            numeric = pd.to_numeric(df[column], errors="coerce")
            if len(df[column]) > 0 and numeric.notna().sum() >= len(df[column]) * 0.8:
                df[column] = numeric
        else:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    return clean_columns(df)


def resolve_time_columns(df: pd.DataFrame) -> dict[str, str]:
    normalized = {str(column).strip().lower(): column for column in df.columns}
    resolved: dict[str, str] = {}

    for canonical, aliases in TIME_COLUMN_ALIASES.items():
        for alias in aliases:
            if alias.lower() in normalized:
                resolved[canonical] = normalized[alias.lower()]
                break

    return resolved


def successful_flow_rows(df: pd.DataFrame) -> pd.DataFrame:
    if "status" not in df.columns:
        return df.copy()

    status = df["status"].astype(str).str.strip().str.upper()
    return df[status.eq("SUCESSO")].copy()


def coefficient_of_variation(values: pd.Series) -> float:
    mean_value = values.mean()
    if pd.isna(mean_value) or mean_value == 0:
        return 0.0
    return float(values.std(ddof=1) / mean_value)


def summarize_metric(df: pd.DataFrame, canonical_name: str, source_column: str) -> dict:
    values = pd.to_numeric(df[source_column], errors="coerce").dropna()
    values = values[values > 0]

    return {
        "metrica": canonical_name,
        "coluna_origem": source_column,
        "quantidade_amostras": int(values.count()),
        "media": values.mean(),
        "mediana": values.median(),
        "minimo": values.min(),
        "maximo": values.max(),
        "desvio_padrao": values.std(ddof=1),
        "p90": values.quantile(0.90),
        "p95": values.quantile(0.95),
        "coeficiente_variacao": coefficient_of_variation(values),
    }


def model_recommendation(cv: float) -> str:
    if cv < 0.10:
        return "M/D/1 para validacao e M/D/c para extensao de capacidade"
    return "M/G/1 ou M/G/c como analise complementar"


def build_model_inputs(
    summary: pd.DataFrame,
    source_file: Path,
    selected_service_column: str = "tempo_solicitacao",
) -> dict:
    row = summary[summary["metrica"] == selected_service_column]
    if row.empty:
        raise ValueError(
            f"Metrica de servico '{selected_service_column}' nao encontrada no resumo."
        )

    record = row.iloc[0]
    service_time_seconds = float(record["media"])
    cv_service = float(record["coeficiente_variacao"])
    mu_per_hour = 3600 / service_time_seconds

    return {
        "service_time_seconds": round(service_time_seconds, 6),
        "service_time_minutes": round(service_time_seconds / 60, 6),
        "mu_per_hour": round(mu_per_hour, 6),
        "cv_service": round(cv_service, 6),
        "selected_service_column": selected_service_column,
        "source_service_column": str(record.get("coluna_origem", selected_service_column)),
        "selenium_sample_size": int(record["quantidade_amostras"]),
        "source_file": str(source_file.relative_to(BASE_DIR)),
        "model_recommendation": model_recommendation(cv_service),
    }


def process_selenium_metrics(
    summary_file: Path = SUMMARY_FILE,
    model_inputs_file: Path = MODEL_INPUTS_FILE,
) -> tuple[pd.DataFrame, dict]:
    flow_file = first_existing_path(FLOW_CANDIDATES)
    if flow_file is None:
        candidates = ", ".join(str(path.relative_to(BASE_DIR)) for path in FLOW_CANDIDATES)
        raise FileNotFoundError(f"Nenhum CSV Selenium de fluxo encontrado. Procurado em: {candidates}")

    flow_df = load_csv(flow_file)
    optional_sources = {
        name: first_existing_path(candidates)
        for name, candidates in OPTIONAL_CANDIDATES.items()
    }
    # Os CSVs de carga/erros nao entram no tempo de servico principal,
    # mas sao lidos aqui para validar a presenca da coleta Selenium real.
    for optional_file in optional_sources.values():
        if optional_file is not None:
            load_csv(optional_file)

    successful_df = successful_flow_rows(flow_df)
    resolved_columns = resolve_time_columns(successful_df)

    required = ["tempo_login", "tempo_solicitacao", "tempo_total"]
    missing = [metric for metric in required if metric not in resolved_columns]
    if missing:
        raise ValueError(f"Colunas de tempo ausentes no CSV Selenium: {', '.join(missing)}")

    summary = pd.DataFrame(
        [
            summarize_metric(successful_df, metric, resolved_columns[metric])
            for metric in required
        ]
    )

    numeric_columns = [
        "media",
        "mediana",
        "minimo",
        "maximo",
        "desvio_padrao",
        "p90",
        "p95",
        "coeficiente_variacao",
    ]
    summary[numeric_columns] = summary[numeric_columns].round(4)

    model_inputs = build_model_inputs(summary, flow_file)
    model_inputs["source_files"] = [
        str(path.relative_to(BASE_DIR))
        for path in [flow_file, *[path for path in optional_sources.values() if path is not None]]
    ]

    summary_file.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_file, index=False, encoding="utf-8")
    model_inputs_file.write_text(
        json.dumps(model_inputs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return summary, model_inputs


def main() -> None:
    summary, model_inputs = process_selenium_metrics()
    print(f"Resumo salvo em: {SUMMARY_FILE}")
    print(f"Parametros do modelo salvos em: {MODEL_INPUTS_FILE}")
    print(summary.to_string(index=False))
    print(json.dumps(model_inputs, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
