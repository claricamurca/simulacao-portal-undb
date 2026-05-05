# Simulacao e Avaliação de Software - Portal do Aluno UNDB

Projeto de simulação e avaliacao do fluxo de Requerimento de Horas Complementares do Portal do Aluno UNDB.

A versao final separa tres etapas:

- Analise empirica de tempos coletados anteriormente via Selenium.
- Simulacao de eventos discretos com SimPy e modelos de filas.
- Dashboard Streamlit para apresentacao dos resultados.

Selenium nao e mais o motor do projeto. Os scripts antigos foram arquivados em `_archive_selenium/`; os dados brutos usados pela calibracao permanecem em `data/raw/selenium/`.

## Modelo de Filas

O modelo principal da simulacao e:

```text
M/D/c/infinito/infinito/FIFO
```

Ele usa `tempo_solicitacao` como tempo de servico da entidade solicitacao. A decisao vem do coeficiente de variacao observado: quando `CV < 0.10`, o servico e tratado como quase deterministico.

O modelo complementar para sensibilidade e:

```text
M/G/c/infinito/infinito/FIFO
```

Esse modelo representa servico generico com variabilidade, usando distribuicao empirica ou triangular.

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

Arquivos Selenium, testes antigos, dashboard Dash e metricas antigas em `results/metrics_*.csv` foram movidos para `_archive_selenium/`.

## Instalar Dependencias

```bash
pip install -r requirements.txt
```

## Rodar Analise Empirica

```bash
python -m src.analysis.empirical_metrics
python -m src.analysis.model_selection
```

A analise empirica le:

```text
data/raw/selenium/metrics_fluxo.csv
```

E gera:

```text
data/processed/resumo_tempos_observados.csv
data/processed/modelo_sugerido.csv
```

## Rodar Simulacao

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

O dashboard apresenta calibracao empirica, estabilidade, capacidade, desempenho de filas, degradacao e comparacao analitica M/D/1.

## Observacao Sobre Dados

Arquivos brutos de coleta, usuarios, PDFs e o arquivo `_archive_selenium/` devem permanecer fora do versionamento quando contiverem dados reais ou sensiveis.
