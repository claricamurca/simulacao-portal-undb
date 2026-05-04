# Simulacao e Avaliacao de Software - Portal do Aluno UNDB

Este projeto organiza uma base para estudar o fluxo de Requerimento de Horas Complementares do Portal do Aluno UNDB usando coleta empirica e simulacao baseada em modelos de filas.

O objetivo da migracao e separar claramente duas responsabilidades:

- Selenium coleta tempos reais observados no portal.
- SimPy sera o motor principal da simulacao.

## Papel do Selenium

Selenium nao deve ser tratado como mecanismo principal de simulacao. Ele interage com o sistema real, abre navegador, executa o fluxo do usuario e registra tempos observados, como:

- tempo de login
- tempo de preenchimento/envio da solicitacao
- tempo total do fluxo
- status da execucao
- erro observado, quando existir

Esses dados sao empiricos. Eles servem para calibrar o modelo de filas, estimar tempos de servico e avaliar a variabilidade real do sistema.

## Papel do SimPy

SimPy sera usado para simular o comportamento do sistema sem depender do navegador nem do portal real a cada execucao. A simulacao deve representar chegadas, fila, servidores, atendimento e metricas de desempenho.

Nesta primeira fase, a simulacao completa ainda nao foi implementada. Foram criadas apenas a estrutura de pastas, a analise empirica e a selecao inicial do modelo.

## Modelo Inicial

O modelo candidato inicial e:

```text
M/G/c/∞/∞/FIFO
```

Na Notacao de Kendall:

- `M`: processo de chegada Markoviano, normalmente associado a chegadas Poisson.
- `G`: distribuicao geral do tempo de servico.
- `c`: numero de servidores ou canais de atendimento.
- `∞`: capacidade infinita da fila.
- `∞`: populacao fonte infinita.
- `FIFO`: disciplina de atendimento por ordem de chegada.

Esse modelo e adequado como ponto de partida porque os tempos coletados podem apresentar variabilidade. Caso o coeficiente de variacao do tempo de servico escolhido seja baixo, o modelo pode ser simplificado para:

```text
M/D/c/∞/∞/FIFO
```

## Decisao pelo Coeficiente de Variacao

A selecao inicial segue esta regra:

- `CV < 0.10`: servico quase deterministico, sugerindo `M/D/c`.
- `0.10 <= CV <= 0.50`: servico generico com variabilidade moderada, sugerindo `M/G/c`.
- `CV > 0.50`: servico generico com alta variabilidade, sugerindo `M/G/c`.

## Estrutura Criada

```text
data/
  fixtures/
  raw/
    selenium/
  processed/

src/
  collection/
    selenium/
      flows/
      collectors/
      pages/
  analysis/
  simulation/
    models/
  reporting/

results/
  empirical/
  simulation/
  figures/

tests/
  unit/
  integration/
```

## Como Rodar a Analise Empirica

```bash
python -m src.analysis.empirical_metrics
```

Esse comando le `data/raw/selenium/metrics_fluxo.csv`, considera apenas execucoes com status `SUCESSO` e salva:

```text
data/processed/resumo_tempos_observados.csv
```

## Como Rodar a Selecao do Modelo

```bash
python -m src.analysis.model_selection
```

Esse comando le o resumo empirico, classifica a variabilidade pelo coeficiente de variacao e salva:

```text
data/processed/modelo_sugerido.csv
```

## Como Rodar a Simulacao

```bash
python -m src.simulation.experiments
```

Esse comando executa a simulacao de eventos discretos com SimPy para solicitacoes chegando ao portal, aguardando em fila FIFO e sendo processadas por `c` servidores paralelos.

As saidas sao:

```text
results/simulation/simulacao_resultados.csv
results/simulation/resumo_cenarios.csv
results/simulation/comparacao_analitica_md1.csv
```

O modelo principal e `M/D/c/∞/∞/FIFO`, usando `tempo_solicitacao` como tempo de servico deterministico. O modelo complementar `M/G/c/∞/∞/FIFO` fica disponivel para analise de sensibilidade usando distribuicao triangular ou empirica.

## Como Rodar o Dashboard Dash

```bash
python -m src.reporting.dashboard_dash
```

Este dashboard usa Dash, Plotly e Dash Bootstrap Components para visualizar calibracao empirica, estabilidade, capacidade, desempenho de filas, degradacao e comparacao analitica M/D/1.

## Como Rodar o Dashboard Streamlit

```bash
streamlit run src/reporting/dashboard_streamlit.py
```

Este dashboard usa Streamlit e Plotly em uma interface dark neon premium para apresentar os resultados da simulacao, a calibracao empirica, estabilidade, filas, degradacao e comparacao analitica.

## Proxima Fase

Na proxima etapa, os resultados simulados podem ser incorporados ao dashboard e comparados visualmente aos dados empiricos coletados via Selenium.
