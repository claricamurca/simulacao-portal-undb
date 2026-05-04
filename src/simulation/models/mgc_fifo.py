from src.simulation.models.mdc_fifo import run_fifo_simulation


def simulate_mgc_fifo(
    *,
    periodo: str,
    lambda_hora: float,
    c: int,
    replica: int,
    seed: int,
    service_stats: dict,
    service_mode: str = "triangular",
    empirical_samples: list[float] | None = None,
) -> dict:
    if service_mode not in {"triangular", "empirical"}:
        raise ValueError("M/G/c aceita apenas service_mode triangular ou empirical.")

    model_name = "M/G/c_triangular" if service_mode == "triangular" else "M/G/c_empirical"

    return run_fifo_simulation(
        model_name=model_name,
        service_distribution_symbol="G",
        service_mode=service_mode,
        periodo=periodo,
        lambda_hora=lambda_hora,
        c=c,
        replica=replica,
        seed=seed,
        service_stats=service_stats,
        empirical_samples=empirical_samples,
    )
