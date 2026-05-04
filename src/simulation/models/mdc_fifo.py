from __future__ import annotations

import random

import simpy

from src.simulation import config
from src.simulation.distributions import (
    ArrivalProcess,
    ServiceTimeSampler,
    service_mean_to_mu_hour,
)
from src.simulation.kendall import KendallNotation
from src.simulation.metrics import percent_error, percentile, safe_mean
from src.simulation.metrics import little_law_population


def run_fifo_simulation(
    *,
    model_name: str,
    service_distribution_symbol: str,
    service_mode: str,
    periodo: str,
    lambda_hora: float,
    c: int,
    replica: int,
    seed: int,
    service_stats: dict,
    empirical_samples: list[float] | None = None,
    duration_seconds: float = config.SIMULATION_DURATION_SECONDS,
    warmup_seconds: float = config.WARMUP_SECONDS,
) -> dict:
    rng = random.Random(seed)
    env = simpy.Environment()
    resource = simpy.Resource(env, capacity=c)

    arrival_process = ArrivalProcess(lambda_hora, rng)
    service_sampler = ServiceTimeSampler(
        mode=service_mode,
        stats=service_stats,
        rng=rng,
        empirical_samples=empirical_samples,
    )

    observation_time = duration_seconds - warmup_seconds
    service_mean = service_stats["media"]
    mu_hora = service_mean_to_mu_hour(service_mean)
    rho = lambda_hora / (c * mu_hora)

    # Estado usado para estimar L e Lq por area no tempo.
    state = {
        "last_event_time": 0.0,
        "number_in_system": 0,
        "queue_length": 0,
        "busy_count": 0,
        "area_system": 0.0,
        "area_queue": 0.0,
        "area_busy": 0.0,
        "total_arrivals": 0,
        "total_completed": 0,
        "queued_completed": 0,
        "waits": [],
        "system_times": [],
    }

    def update_areas(now: float) -> None:
        start = max(state["last_event_time"], warmup_seconds)
        end = min(now, duration_seconds)
        if end > start:
            elapsed = end - start
            state["area_system"] += state["number_in_system"] * elapsed
            state["area_queue"] += state["queue_length"] * elapsed
            state["area_busy"] += state["busy_count"] * elapsed
        state["last_event_time"] = now

    def handle_request(arrival_time: float) -> simpy.events.Event:
        update_areas(env.now)
        state["number_in_system"] += 1

        counted_after_warmup = arrival_time >= warmup_seconds
        if counted_after_warmup:
            state["total_arrivals"] += 1

        queued = resource.count >= resource.capacity
        if queued:
            update_areas(env.now)
            state["queue_length"] += 1

        with resource.request() as request:
            yield request

            if queued:
                update_areas(env.now)
                state["queue_length"] -= 1

            service_start = env.now
            wait_time = service_start - arrival_time

            update_areas(env.now)
            state["busy_count"] += 1

            service_time = service_sampler.sample_seconds()
            yield env.timeout(service_time)

            service_end = env.now

            update_areas(env.now)
            state["busy_count"] -= 1
            state["number_in_system"] -= 1

            if counted_after_warmup and service_end <= duration_seconds:
                state["total_completed"] += 1
                state["waits"].append(wait_time)
                state["system_times"].append(service_end - arrival_time)
                if wait_time > 1e-9:
                    state["queued_completed"] += 1

    def generate_arrivals() -> simpy.events.Event:
        while True:
            interarrival = arrival_process.next_interarrival_seconds()
            yield env.timeout(interarrival)
            if env.now > duration_seconds:
                break
            env.process(handle_request(env.now))

    env.process(generate_arrivals())
    env.run(until=duration_seconds)
    update_areas(duration_seconds)

    wq = safe_mean(state["waits"])
    w = safe_mean(state["system_times"])

    # Lei de Little com W/Wq em segundos:
    # L = lambda_segundo * W_seg
    # Lq = lambda_segundo * Wq_seg
    lq_little = little_law_population(lambda_hora, wq)
    l_little = little_law_population(lambda_hora, w)

    # Medidas por area no tempo ajudam a validar a Lei de Little.
    lq_area = state["area_queue"] / observation_time
    l_area = state["area_system"] / observation_time

    notation = KendallNotation(
        arrival_process="M",
        service_distribution=service_distribution_symbol,
        servers="c",
        queue_capacity="∞",
        population="∞",
        discipline="FIFO",
    ).as_string()

    return {
        "modelo": model_name,
        "notacao_kendall": notation,
        "periodo": periodo,
        "lambda_hora": lambda_hora,
        "c": c,
        "replica": replica,
        "seed": seed,
        "tempo_medio_servico_seg": service_mean,
        "mu_estimado_hora": mu_hora,
        "rho": rho,
        "status_estabilidade": "ESTAVEL" if rho < 1 else "INSTAVEL",
        "total_chegadas": state["total_arrivals"],
        "total_atendidas": state["total_completed"],
        "Wq_seg": wq,
        "W_seg": w,
        "Lq": lq_little,
        "L": l_little,
        "Lq_observado_area": lq_area,
        "L_observado_area": l_area,
        "erro_little_L": percent_error(l_area, l_little),
        "erro_little_Lq": percent_error(lq_area, lq_little),
        "P50_W_seg": percentile(state["system_times"], 0.50),
        "P90_W_seg": percentile(state["system_times"], 0.90),
        "P95_W_seg": percentile(state["system_times"], 0.95),
        "utilizacao_empirica": state["area_busy"] / (c * observation_time),
        "throughput_hora": state["total_completed"] / (observation_time / config.SECONDS_PER_HOUR),
        "taxa_fila": state["queued_completed"] / state["total_completed"]
        if state["total_completed"] > 0
        else 0.0,
        "fator_degradacao": float("nan"),
    }


def simulate_mdc_fifo(
    *,
    periodo: str,
    lambda_hora: float,
    c: int,
    replica: int,
    seed: int,
    service_stats: dict,
) -> dict:
    return run_fifo_simulation(
        model_name="M/D/c",
        service_distribution_symbol="D",
        service_mode="deterministic",
        periodo=periodo,
        lambda_hora=lambda_hora,
        c=c,
        replica=replica,
        seed=seed,
        service_stats=service_stats,
    )
