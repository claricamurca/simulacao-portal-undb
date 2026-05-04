from __future__ import annotations

import math
from collections import Counter
from statistics import mean, stdev


SECONDS_PER_HOUR = 3600


def percentile(values: list[float], q: float) -> float:
    if not values:
        return math.nan

    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]

    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[int(position)]

    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def safe_mean(values: list[float]) -> float:
    return mean(values) if values else math.nan


def safe_stdev(values: list[float]) -> float:
    return stdev(values) if len(values) > 1 else 0.0


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0 or math.isnan(denominator):
        return math.nan
    return numerator / denominator


def percent_error(observed: float, expected: float) -> float:
    if expected == 0 or math.isnan(expected):
        return math.nan
    return abs(observed - expected) / abs(expected) * 100


def little_law_population(lambda_hour: float, time_seconds: float) -> float:
    """Aplica Little com lambda em chegadas/hora e tempo em segundos.

    L = lambda_segundo * W_seg
    Lq = lambda_segundo * Wq_seg
    """
    if math.isnan(time_seconds):
        return math.nan
    lambda_second = lambda_hour / SECONDS_PER_HOUR
    return lambda_second * time_seconds


def predominant_status(values) -> str:
    clean_values = [value for value in values if isinstance(value, str) and value]
    if not clean_values:
        return ""
    return Counter(clean_values).most_common(1)[0][0]
