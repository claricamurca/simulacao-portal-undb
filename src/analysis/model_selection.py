from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_FILE = BASE_DIR / "data" / "processed" / "resumo_tempos_observados.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "modelo_sugerido.csv"


def classify_variability(cv: float) -> str:
    if cv < 0.10:
        return "servico quase deterministico"
    if cv <= 0.50:
        return "servico generico com variabilidade moderada"
    return "servico generico com alta variabilidade"


def suggest_model(cv: float) -> str:
    if cv < 0.10:
        return "M/D/1 para validacao e M/D/c para capacidade"
    return "M/G/1 ou M/G/c como analise complementar"


def kendall_notation(model: str) -> str:
    if model.startswith("M/D/1"):
        return "M/D/1/∞/∞/FIFO + M/D/c/∞/∞/FIFO"
    if model.startswith("M/G/1"):
        return "M/G/1/∞/∞/FIFO ou M/G/c/∞/∞/FIFO"
    return f"{model}/∞/∞/FIFO"


def select_models(
    input_file: Path = INPUT_FILE,
    output_file: Path = OUTPUT_FILE,
) -> pd.DataFrame:
    if not input_file.exists():
        raise FileNotFoundError(
            "Resumo de tempos nao encontrado. Execute antes: "
            "python -m src.analysis.empirical_metrics"
        )

    df = pd.read_csv(input_file)
    df.columns = [str(column).strip() for column in df.columns]

    required_columns = {"metrica", "coeficiente_variacao"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(f"Colunas ausentes no resumo: {', '.join(sorted(missing_columns))}")

    df["coeficiente_variacao"] = pd.to_numeric(
        df["coeficiente_variacao"],
        errors="coerce",
    )

    df["classificacao_variabilidade"] = df["coeficiente_variacao"].apply(
        classify_variability
    )
    df["modelo_sugerido"] = df["coeficiente_variacao"].apply(suggest_model)
    df["notacao_kendall_base"] = df["modelo_sugerido"].apply(kendall_notation)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False, encoding="utf-8")
    return df


def main() -> None:
    selected = select_models()
    print(f"Selecao de modelo salva em: {OUTPUT_FILE}")
    print(selected.to_string(index=False))


if __name__ == "__main__":
    main()
