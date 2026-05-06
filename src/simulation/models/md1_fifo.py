from src.simulation.models.mdc_fifo import run_fifo_simulation


def simulate_md1_fifo(
    *,
    periodo: str,
    lambda_hora: float,
    replica: int,
    seed: int,
    service_stats: dict,
) -> dict:
    return run_fifo_simulation(
        model_name="M/D/1",
        service_distribution_symbol="D",
        service_mode="deterministic",
        server_symbol=1,
        periodo=periodo,
        lambda_hora=lambda_hora,
        c=1,
        replica=replica,
        seed=seed,
        service_stats=service_stats,
    )
