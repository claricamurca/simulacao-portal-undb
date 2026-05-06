def build_model_inputs(summary, source_file, selected_service_column="tempo_solicitacao"):
    row = summary[summary["metrica"] == selected_service_column]
    record = row.iloc[0]

    service_time_seconds = float(record["media"])
    cv_service = float(record["coeficiente_variacao"])
    mu_per_hour = 3600 / service_time_seconds

    return {
        "service_time_seconds": round(service_time_seconds, 6),
        "service_time_minutes": round(service_time_seconds / 60, 6),
        "mu_per_hour": round(mu_per_hour, 6),
        "cv_service": round(cv_service, 6),
        "selected_service_column": selected_service_column,
        "selenium_sample_size": int(record["quantidade_amostras"]),
        "source_file": str(source_file.relative_to(BASE_DIR)),
        "model_recommendation": model_recommendation(cv_service),
    }


model_inputs = build_model_inputs(summary, flow_file)
MODEL_INPUTS_FILE.write_text(json.dumps(model_inputs, indent=2), encoding="utf-8")
