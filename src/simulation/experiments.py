from __future__ import annotations

import math

import pandas as pd

from src.simulation import config
from src.simulation.analytical_md1 import md1_analytical
from src.simulation.distributions import (
    load_empirical_service_samples,
    load_service_stats,
)
from src.simulation.metrics import percent_error, predominant_status, safe_stdev
from src.simulation.models.mdc_fifo import simulate_mdc_fifo
from src.simulation.models.mgc_fifo import simulate_mgc_fifo


def scenario_seed(model_index: int, lambda_hora: float, c: int, replica: int) -> int:
    return (
        config.BASE_SEED
        + model_index * 1_000_000
        + int(lambda_hora) * 1_000
        + c * 100
        + replica
    )


def run_all_replicas() -> pd.DataFrame:
    service_stats = load_service_stats()
    empirical_samples = load_empirical_service_samples()

    rows = []

    for model_index, variant in enumerate(config.MODEL_VARIANTS):
        for periodo, lambdas_hora in config.ARRIVAL_SCENARIOS.items():
            for lambda_hora in lambdas_hora:
                for c in config.SERVER_CAPACITIES:
                    for replica in range(1, config.REPLICAS + 1):
                        seed = scenario_seed(model_index, lambda_hora, c, replica)

                        if variant == "mdc":
                            result = simulate_mdc_fifo(
                                periodo=periodo,
                                lambda_hora=lambda_hora,
                                c=c,
                                replica=replica,
                                seed=seed,
                                service_stats=service_stats,
                            )
                        elif variant == "mgc_triangular":
                            result = simulate_mgc_fifo(
                                periodo=periodo,
                                lambda_hora=lambda_hora,
                                c=c,
                                replica=replica,
                                seed=seed,
                                service_stats=service_stats,
                                service_mode="triangular",
                            )
                        elif variant == "mgc_empirical":
                            result = simulate_mgc_fifo(
                                periodo=periodo,
                                lambda_hora=lambda_hora,
                                c=c,
                                replica=replica,
                                seed=seed,
                                service_stats=service_stats,
                                service_mode="empirical",
                                empirical_samples=empirical_samples,
                            )
                        else:
                            raise ValueError(f"Variante de modelo desconhecida: {variant}")

                        rows.append(result)

    df = pd.DataFrame(rows)
    return apply_degradation_factor(df)


def apply_degradation_factor(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula fator de degradacao usando baseline estavel por modelo."""
    df = df.copy()
    df["fator_degradacao"] = math.nan

    for modelo in df["modelo"].dropna().unique():
        model_rows = df[df["modelo"] == modelo]
        stable_offpeak = model_rows[
            (model_rows["periodo"] == "fora_pico")
            & (model_rows["status_estabilidade"] == "ESTAVEL")
        ]

        if stable_offpeak.empty:
            continue

        min_lambda = stable_offpeak["lambda_hora"].min()
        baseline_candidates = stable_offpeak[stable_offpeak["lambda_hora"] == min_lambda]
        baseline_w = baseline_candidates["W_seg"].mean()

        if baseline_w and not math.isnan(baseline_w):
            mask = df["modelo"] == modelo
            df.loc[mask, "fator_degradacao"] = df.loc[mask, "W_seg"] / baseline_w

    return df


def consolidate_scenarios(df: pd.DataFrame) -> pd.DataFrame:
    group_columns = ["modelo", "notacao_kendall", "periodo", "lambda_hora", "c"]
    rows = []

    for keys, group in df.groupby(group_columns, dropna=False):
        row = dict(zip(group_columns, keys))

        # Wq: tempo medio de espera na fila.
        # W: tempo medio no sistema, isto e, espera + servico.
        # Lq e L sao derivados por Little no arquivo de replicas.
        row.update(
            {
                "tempo_medio_servico_seg": group["tempo_medio_servico_seg"].mean(),
                "mu_estimado_hora": group["mu_estimado_hora"].mean(),
                "rho_medio": group["rho"].mean(),
                "Wq_media_seg": group["Wq_seg"].mean(),
                "Wq_desvio_padrao_seg": safe_stdev(group["Wq_seg"].dropna().tolist()),
                "W_media_seg": group["W_seg"].mean(),
                "W_desvio_padrao_seg": safe_stdev(group["W_seg"].dropna().tolist()),
                "Lq_media": group["Lq"].mean(),
                "L_media": group["L"].mean(),
                "utilizacao_media": group["utilizacao_empirica"].mean(),
                "P95_W_medio_seg": group["P95_W_seg"].mean(),
                "throughput_medio_hora": group["throughput_hora"].mean(),
                "taxa_fila_media": group["taxa_fila"].mean(),
                "quantidade_replicas": len(group),
                "status_predominante": predominant_status(group["status_estabilidade"]),
                "fator_degradacao_medio": group["fator_degradacao"].mean(),
                "erro_little_L_medio": group["erro_little_L"].mean(),
                "erro_little_Lq_medio": group["erro_little_Lq"].mean(),
            }
        )

        rows.append(row)

    return pd.DataFrame(rows).sort_values(
        ["modelo", "periodo", "lambda_hora", "c"],
        ignore_index=True,
    )


def build_analytical_comparison(summary_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    md1_rows = summary_df[(summary_df["modelo"] == "M/D/c") & (summary_df["c"] == 1)]

    for _, row in md1_rows.iterrows():
        analytical = md1_analytical(
            lambda_hour=float(row["lambda_hora"]),
            service_mean_seconds=float(row["tempo_medio_servico_seg"]),
        )

        comparison = {
            "periodo": row["periodo"],
            "lambda_hora": row["lambda_hora"],
            "c": row["c"],
            "rho_simulado": row["rho_medio"],
            "status_simulado": row["status_predominante"],
            "Wq_simulado_seg": row["Wq_media_seg"],
            "W_simulado_seg": row["W_media_seg"],
            "Lq_simulado": row["Lq_media"],
            "L_simulado": row["L_media"],
        }
        comparison.update(analytical)

        if analytical["status_analitico"] == "ESTAVEL":
            erro_percentual_wq = percent_error(
                row["Wq_media_seg"],
                analytical["Wq_analitico_seg"],
            )
            erro_percentual_w = percent_error(
                row["W_media_seg"],
                analytical["W_analitico_seg"],
            )
            comparison.update(
                {
                    "diferenca_Wq_seg": row["Wq_media_seg"]
                    - analytical["Wq_analitico_seg"],
                    "diferenca_W_seg": row["W_media_seg"]
                    - analytical["W_analitico_seg"],
                    "diferenca_Lq": row["Lq_media"] - analytical["Lq_analitico"],
                    "diferenca_L": row["L_media"] - analytical["L_analitico"],
                    "erro_percentual_Wq": erro_percentual_wq,
                    "erro_percentual_W": erro_percentual_w,
                }
            )
        else:
            comparison.update(
                {
                    "diferenca_Wq_seg": math.nan,
                    "diferenca_W_seg": math.nan,
                    "diferenca_Lq": math.nan,
                    "diferenca_L": math.nan,
                    "erro_percentual_Wq": math.nan,
                    "erro_percentual_W": math.nan,
                }
            )

        rows.append(comparison)

    return pd.DataFrame(rows)


def save_outputs(
    replicas_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    analytical_df: pd.DataFrame,
) -> None:
    config.SIMULATION_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    replicas_df.to_csv(config.SIMULATION_REPLICAS_FILE, index=False, encoding="utf-8")
    summary_df.to_csv(config.SIMULATION_SUMMARY_FILE, index=False, encoding="utf-8")
    analytical_df.to_csv(
        config.ANALYTICAL_COMPARISON_FILE,
        index=False,
        encoding="utf-8",
    )


def main() -> None:
    print("Iniciando simulacoes SimPy...")
    print(f"Modelos: {', '.join(config.MODEL_VARIANTS)}")
    print(f"Replicas por cenario: {config.REPLICAS}")

    replicas_df = run_all_replicas()
    summary_df = consolidate_scenarios(replicas_df)
    analytical_df = build_analytical_comparison(summary_df)

    save_outputs(replicas_df, summary_df, analytical_df)

    print(f"Resultados por replica: {config.SIMULATION_REPLICAS_FILE}")
    print(f"Resumo por cenario: {config.SIMULATION_SUMMARY_FILE}")
    print(f"Comparacao M/D/1 analitica: {config.ANALYTICAL_COMPARISON_FILE}")


if __name__ == "__main__":
    main()
