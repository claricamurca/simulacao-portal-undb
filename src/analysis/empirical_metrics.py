from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_FILE = BASE_DIR / "data" / "raw" / "selenium" / "metrics_fluxo.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "resumo_tempos_observados.csv"

TIME_COLUMNS = ["tempo_login", "tempo_solicitacao", "tempo_total"]


def coefficient_of_variation(series: pd.Series) -> float:
    mean_value = series.mean()
    if pd.isna(mean_value) or mean_value == 0:
        return 0.0
    return series.std(ddof=1) / mean_value


def summarize_time_column(df: pd.DataFrame, column: str) -> dict:
    values = pd.to_numeric(df[column], errors="coerce").dropna()

    return {
        "metrica": column,
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


def load_successful_flow_metrics(input_file: Path = INPUT_FILE) -> pd.DataFrame:
    if not input_file.exists():
        raise FileNotFoundError(f"Arquivo de metricas nao encontrado: {input_file}")

    df = pd.read_csv(input_file)
    df.columns = [str(column).strip() for column in df.columns]

    if "status" not in df.columns:
        raise ValueError("A coluna 'status' nao foi encontrada no CSV de fluxo.")

    missing_columns = [column for column in TIME_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Colunas de tempo ausentes: {', '.join(missing_columns)}")

    return df[df["status"].astype(str).str.strip().str.upper() == "SUCESSO"].copy()


def generate_empirical_summary(
    input_file: Path = INPUT_FILE,
    output_file: Path = OUTPUT_FILE,
) -> pd.DataFrame:
    df = load_successful_flow_metrics(input_file)
    summary = pd.DataFrame([summarize_time_column(df, column) for column in TIME_COLUMNS])

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

    output_file.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_file, index=False, encoding="utf-8")
    return summary


def main() -> None:
    summary = generate_empirical_summary()
    print(f"Resumo salvo em: {OUTPUT_FILE}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
