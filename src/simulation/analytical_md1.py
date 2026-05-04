import math

from src.simulation import config


def md1_analytical(lambda_hour: float, service_mean_seconds: float) -> dict:
    """Calcula metricas analiticas M/D/1 com tempos finais em segundos.

    Padrao de unidades:
    - lambda_hour: chegadas/hora
    - mu_hour: atendimentos/hora
    - rho, L e Lq: adimensionais ou quantidade media de solicitacoes
    - W e Wq: segundos
    """
    mu_hour = config.SECONDS_PER_HOUR / service_mean_seconds
    rho = lambda_hour / mu_hour

    result = {
        "lambda_hora": lambda_hour,
        "tempo_medio_servico_seg": service_mean_seconds,
        "mu_estimado_hora": mu_hour,
        "rho_analitico": rho,
        "status_analitico": "ESTAVEL" if rho < 1 else "INSTAVEL",
        "Wq_analitico_seg": math.nan,
        "W_analitico_seg": math.nan,
        "Lq_analitico": math.nan,
        "L_analitico": math.nan,
    }

    if lambda_hour <= 0 or rho >= 1:
        if lambda_hour <= 0:
            result["status_analitico"] = "LAMBDA_INVALIDO"
        return result

    # M/D/1:
    # Lq = rho^2 / [2(1-rho)]
    # Como lambda e mu estao por hora, Wq_hora e W_hora saem em horas.
    # Antes de salvar/comparar, convertemos Wq e W para segundos.
    lq = (rho**2) / (2 * (1 - rho))
    wq_hour = lq / lambda_hour
    w_hour = wq_hour + (1 / mu_hour)

    wq_seconds = wq_hour * config.SECONDS_PER_HOUR
    w_seconds = w_hour * config.SECONDS_PER_HOUR

    # Lei de Little em horas: L = lambda_hora * W_hora.
    l = lambda_hour * w_hour
    lq_from_little = lambda_hour * wq_hour

    result.update(
        {
            "Wq_analitico_seg": wq_seconds,
            "W_analitico_seg": w_seconds,
            "Lq_analitico": lq_from_little,
            "L_analitico": l,
        }
    )
    return result
