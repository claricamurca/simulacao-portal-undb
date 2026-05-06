# Snippets para slides

Material curto e sanitizado para comprovar a implementação do projeto. Os trechos foram adaptados para apresentação: sem usuários, senhas, RA, XPaths longos ou caminhos pessoais.

## 1. Coleta dos tempos reais com Selenium

**Arquivo de origem:** `_archive_selenium/tests/test_fluxo_requerimento.py`

**Legenda:** O Selenium executa o fluxo real no Portal UNDB e registra os tempos usados para calibrar o modelo.

**Sugestão de slide:** Use após explicar que o Selenium não simula a fila; ele mede o sistema real.

```python
def executar_fluxo(identificador, credenciais, arquivo_metrics):
    inicio_fluxo = time.time()
    tempo_login = tempo_solicitacao = tempo_total = 0.0
    status, erro = "ERRO", ""
    try:
        driver, wait = criar_driver()
        tempo_login, campo_solicitacao = preparar_fluxo_ate_tela_solicitacao(
            driver, wait, credenciais
        )
        inicio_solicitacao = time.time()
        preencher_solicitacao(campo_solicitacao)
        anexar_documento(driver, wait)
        enviar_solicitacao(driver, wait)
        tempo_solicitacao = round(time.time() - inicio_solicitacao, 2)
        status = "SUCESSO"
    except Exception as e:
        erro = formatar_erro_curto(e)
    finally:
        tempo_total = round(time.time() - inicio_fluxo, 2)
        salvar_metricas_fluxo(
            identificador, tempo_login, tempo_solicitacao,
            tempo_total, status, erro
        )
```

## 2. Conversão dos dados reais em parâmetros do modelo

**Arquivo de origem:** `src/analysis/selenium_metrics_loader.py`

**Legenda:** O tempo de solicitação coletado pelo Selenium é convertido em taxa de serviço μ.

**Sugestão de slide:** Use no slide “Calibração do modelo”, mostrando que μ não foi inventado manualmente.

```python
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
```

## 3. Simulação da fila no SimPy

**Arquivo de origem:** `src/simulation/models/mdc_fifo.py`

**Legenda:** O SimPy representa chegadas, fila FIFO, atendimento e tempo total no sistema.

**Sugestão de slide:** Use no slide “Simulação M/D/1 e M/D/c”, destacando `Environment`, `Resource` e `timeout`.

```python
def run_fifo_simulation(lambda_hora, c, service_stats, seed):
    rng = random.Random(seed)
    env = simpy.Environment()
    resource = simpy.Resource(env, capacity=c)
    waits, system_times = [], []
    arrival_process = ArrivalProcess(lambda_hora, rng)
    service_sampler = ServiceTimeSampler("deterministic", service_stats, rng)

    def handle_request(arrival_time):
        with resource.request() as request:
            yield request
            service_start = env.now
            wait_time = service_start - arrival_time
            service_time = service_sampler.sample_seconds()
            yield env.timeout(service_time)
            service_end = env.now
            waits.append(wait_time)
            system_times.append(service_end - arrival_time)

    def generate_arrivals():
        while env.now < SIMULATION_DURATION_SECONDS:
            yield env.timeout(arrival_process.next_interarrival_seconds())
            env.process(handle_request(env.now))
```

## 4. Cálculo analítico M/D/1

**Arquivo de origem:** `src/simulation/analytical_md1.py`

**Legenda:** As métricas calculadas foram usadas para validar a simulação nos cenários estáveis.

**Sugestão de slide:** Use no slide “Calculado x Simulado”, antes da tabela de erro percentual.

```python
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
```
