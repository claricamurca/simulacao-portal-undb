# Simulação e Avaliação de Software - Portal do Aluno UNDB

Projeto de simulação e avaliação do fluxo de Requerimento de Horas Complementares do Portal do Aluno UNDB.

## Equipe
- Anna Carolyna Almeida
- Artho Eduardo
- Clarissa Camurça
- Gabriel Muller
- Marcelo Augusto
- Marcos Santos
- Thiago Vasconcelos

A versão final separa três etapas:

- Análise empírica de tempos coletados anteriormente via Selenium.
- Simulação de eventos discretos com SimPy e modelos de filas.
- Dashboard Streamlit para apresentação dos resultados.

Selenium não é mais o motor do projeto. Os scripts antigos foram arquivados em `_archive_selenium/`; os dados brutos usados pela calibração permanecem em `data/raw/selenium/`.

## Modelo de Filas

O modelo principal da simulação é:

```text
M/D/c/infinito/infinito/FIFO
```

Ele usa `tempo_solicitacao` como tempo de serviço da entidade solicitação. A decisão vem do coeficiente de variação observado: quando `CV < 0.10`, o serviço é tratado como quase deterministico.

O modelo complementar para sensibilidade é:

```text
M/G/c/infinito/infinito/FIFO
```

Esse modelo representa serviço genérico com variabilidade, usando distribuição empírica ou triangular.

## Estrutura Atual

```text
assets/
data/
  raw/
    selenium/
      metrics_fluxo.csv
  processed/
    resumo_tempos_observados.csv
    modelo_sugerido.csv
results/
  simulation/
    simulacao_resultados.csv
    resumo_cenarios.csv
    comparacao_analitica_md1.csv
src/
  analysis/
  simulation/
  reporting/
    dashboard_streamlit.py
tests/
  unit/
  integration/
```

Arquivos Selenium, testes antigos, dashboard Dash e métricas antigas em `results/metrics_*.csv` foram movidos para `_archive_selenium/`.

## Instalar Dependências

```bash
pip install -r requirements.txt
```

## Rodar Análise Empirica

```bash
python -m src.analysis.empirical_metrics
python -m src.analysis.model_selection
```

A análise empirica lê:

```text
data/raw/selenium/metrics_fluxo.csv
```

E gera:

```text
data/processed/resumo_tempos_observados.csv
data/processed/modelo_sugerido.csv
```

## Rodar Simulação

```bash
python -m src.simulation.experiments
```

Saidas geradas:

```text
results/simulation/simulacao_resultados.csv
results/simulation/resumo_cenarios.csv
results/simulation/comparacao_analitica_md1.csv
```

## Rodar Dashboard

```bash
streamlit run src/reporting/dashboard_streamlit.py
```

O dashboard apresenta calibração empirica, estabilidade, capacidade, desempenho de filas, degradação e comparação analítica M/D/1.

## Observação Sobre Dados

Arquivos brutos de coleta, usuarios, PDFs e o arquivo `_archive_selenium/` devem permanecer fora do versionamento quando contiverem dados reais ou sensiveis.
