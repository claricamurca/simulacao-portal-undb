from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_SELENIUM_DIR = DATA_DIR / "raw" / "selenium"

RESULTS_DIR = BASE_DIR / "results"
SIMULATION_RESULTS_DIR = RESULTS_DIR / "simulation"

RESUMO_TEMPOS_FILE = PROCESSED_DIR / "resumo_tempos_observados.csv"
MODEL_INPUTS_FILE = PROCESSED_DIR / "model_inputs.json"
RAW_FLUXO_FILE = RAW_SELENIUM_DIR / "metrics_fluxo.csv"

SIMULATION_REPLICAS_FILE = SIMULATION_RESULTS_DIR / "simulacao_resultados.csv"
SIMULATION_SUMMARY_FILE = SIMULATION_RESULTS_DIR / "resumo_cenarios.csv"
ANALYTICAL_COMPARISON_FILE = SIMULATION_RESULTS_DIR / "comparacao_analitica_md1.csv"

# Unidade principal da simulacao: segundos.
SECONDS_PER_HOUR = 3600

# Janela simulada: 8 horas, com 30 minutos de warm-up.
SIMULATION_DURATION_SECONDS = 8 * SECONDS_PER_HOUR
WARMUP_SECONDS = 30 * 60

# Replicas independentes por cenario. Cada replica recebe uma seed propria.
REPLICAS = 30
BASE_SEED = 20260502

# O servico principal do requerimento e a etapa de solicitacao.
SERVICE_TIME_METRIC = "tempo_solicitacao"

# Lambda esta em chegadas por hora. O simulador converte para chegadas por segundo.
ARRIVAL_SCENARIOS = {
    "fora_pico": [60, 120, 180],
    "pico": [480, 720, 960, 1200],
}

# c representa a capacidade paralela efetiva do portal para processar solicitacoes.
SERVER_CAPACITIES = [1, 2, 3, 4, 5, 8, 10, 15]

# Modelos executados por padrao:
# - md1: M/D/1 para validacao contra o resultado analitico.
# - mdc: M/D/c como extensao para dimensionamento de capacidade.
MODEL_VARIANTS = ("md1", "mdc")
