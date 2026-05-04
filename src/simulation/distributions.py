import random
from pathlib import Path

import pandas as pd

from src.simulation import config


def lambda_hour_to_second(lambda_hour: float) -> float:
    return lambda_hour / config.SECONDS_PER_HOUR


def service_mean_to_mu_hour(service_mean_seconds: float) -> float:
    if service_mean_seconds <= 0:
        raise ValueError("O tempo medio de servico deve ser maior que zero.")
    return config.SECONDS_PER_HOUR / service_mean_seconds


def load_service_stats(
    metric: str = config.SERVICE_TIME_METRIC,
    path: Path = config.RESUMO_TEMPOS_FILE,
) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            "Resumo empirico nao encontrado. Execute antes: "
            "python -m src.analysis.empirical_metrics"
        )

    df = pd.read_csv(path)
    df.columns = [str(column).strip() for column in df.columns]

    row = df[df["metrica"].astype(str).str.strip() == metric]
    if row.empty:
        raise ValueError(f"Metrica de servico nao encontrada no resumo: {metric}")

    record = row.iloc[0].to_dict()
    return {
        "metrica": metric,
        "quantidade_amostras": int(record["quantidade_amostras"]),
        "media": float(record["media"]),
        "mediana": float(record["mediana"]),
        "minimo": float(record["minimo"]),
        "maximo": float(record["maximo"]),
        "desvio_padrao": float(record["desvio_padrao"]),
        "p90": float(record["p90"]),
        "p95": float(record["p95"]),
        "coeficiente_variacao": float(record["coeficiente_variacao"]),
    }


def load_empirical_service_samples(
    metric: str = config.SERVICE_TIME_METRIC,
    path: Path = config.RAW_FLUXO_FILE,
) -> list[float]:
    if not path.exists():
        return []

    df = pd.read_csv(path)
    df.columns = [str(column).strip() for column in df.columns]

    if "status" not in df.columns or metric not in df.columns:
        return []

    successful = df[df["status"].astype(str).str.strip().str.upper() == "SUCESSO"]
    values = pd.to_numeric(successful[metric], errors="coerce").dropna()
    return [float(value) for value in values if value > 0]


class ArrivalProcess:
    def __init__(self, lambda_hour: float, rng: random.Random):
        self.lambda_hour = lambda_hour
        self.lambda_second = lambda_hour_to_second(lambda_hour)
        self.rng = rng

    def next_interarrival_seconds(self) -> float:
        # Chegadas Poisson implicam tempos entre chegadas exponenciais.
        return self.rng.expovariate(self.lambda_second)


class ServiceTimeSampler:
    def __init__(
        self,
        mode: str,
        stats: dict,
        rng: random.Random,
        empirical_samples: list[float] | None = None,
    ):
        self.mode = mode
        self.stats = stats
        self.rng = rng
        self.empirical_samples = empirical_samples or []

    def sample_seconds(self) -> float:
        if self.mode == "deterministic":
            # M/D/c: D significa servico deterministico.
            return self.stats["media"]

        if self.mode == "empirical":
            # M/G/c empirico: reamostra os tempos reais coletados via Selenium.
            if self.empirical_samples:
                return self.rng.choice(self.empirical_samples)
            return self._sample_triangular()

        if self.mode == "triangular":
            return self._sample_triangular()

        raise ValueError(f"Modo de servico desconhecido: {self.mode}")

    def _sample_triangular(self) -> float:
        # M/G/c triangular: usa minimo, media como modo, e maximo observados.
        low = self.stats["minimo"]
        mode = self.stats["media"]
        high = self.stats["maximo"]
        return self.rng.triangular(low, high, mode)
