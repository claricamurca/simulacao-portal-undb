def md1_analytical(lambda_hour, service_mean_seconds):
    mu_hour = 3600 / service_mean_seconds
    rho = lambda_hour / mu_hour

    if rho >= 1:
        return {"rho_analitico": rho, "status_analitico": "INSTAVEL"}

    # Formula M/D/1: Lq = rho^2 / [2(1-rho)]
    lq = (rho**2) / (2 * (1 - rho))

    # Como lambda e mu estao por hora,
    # Wq e W primeiro saem em horas.
    wq_hour = lq / lambda_hour
    w_hour = wq_hour + (1 / mu_hour)

    return {
        "rho_analitico": rho,
        "Lq_analitico": lambda_hour * wq_hour,
        "L_analitico": lambda_hour * w_hour,
        "Wq_analitico_seg": wq_hour * 3600,
        "W_analitico_seg": w_hour * 3600,
        "status_analitico": "ESTAVEL",
    }
