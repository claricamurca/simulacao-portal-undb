# Simulação e Avaliação de Software - Portal do Aluno UNDB

Projeto de simulação e avaliação do fluxo de Requerimento de Horas Complementares do Portal do Aluno UNDB.

## Objetivo

O projeto usa uma pipeline reprodutível:

```text
Selenium real -> CSV bruto -> análise empírica -> parâmetros do modelo -> SimPy -> CSVs de simulação -> dashboard Streamlit
```

O Selenium não é o motor da simulação. Ele é usado como instrumento de coleta empírica dos tempos reais do fluxo. A simulação principal é executada com SimPy.

## Modelo de Filas

A apresentação principal usa o modelo:

```text
M/D/1/infinito/infinito/FIFO
```

Ele valida o comportamento inicial do sistema com um único canal. O tempo de serviço vem de `tempo_solicitacao`, calculado a partir dos CSVs reais do Selenium.

Como extensão de capacidade, o projeto usa:

```text
M/D/c/infinito/infinito/FIFO
```

Essa extensão varia `c` para identificar a menor capacidade estável em cada cenário de chegada.

## Estrutura Principal

```text
assets/
data/
  raw/
    selenium/
      metrics_fluxo.csv
      metrics_carga.csv
      metrics_erros.csv
  processed/
    resumo_tempos_observados.csv
    modelo_sugerido.csv
    model_inputs.json
results/
  simulation/
    simulacao_resultados.csv
    resumo_cenarios.csv
    comparacao_analitica_md1.csv
src/
  analysis/
    selenium_metrics_loader.py
    empirical_metrics.py
    model_selection.py
  simulation/
  reporting/
    dashboard_streamlit.py
```

Arquivos antigos de Selenium foram preservados em `_archive_selenium/` quando não fazem parte da versão final.

## Instalar Dependências

```bash
pip install -r requirements.txt
```

## Pipeline Recomendada

1. Processar dados reais do Selenium:

```bash
python -m src.analysis.selenium_metrics_loader
```

Esse comando procura os CSVs primeiro em `data/raw/selenium/` e, se necessário, usa fallback em `results/`. Ele gera:

```text
data/processed/resumo_tempos_observados.csv
data/processed/model_inputs.json
```

2. Rodar seleção inicial de modelo, se desejar atualizar o CSV de classificação:

```bash
python -m src.analysis.model_selection
```

3. Rodar simulação SimPy:

```bash
python -m src.simulation.experiments
```

Esse comando usa `data/processed/model_inputs.json` para calibrar o tempo de serviço e gera:

```text
results/simulation/simulacao_resultados.csv
results/simulation/resumo_cenarios.csv
results/simulation/comparacao_analitica_md1.csv
```

4. Abrir dashboard Streamlit:

```bash
streamlit run src/reporting/dashboard_streamlit.py
```

## Observação Sobre Dados

Arquivos brutos de coleta, usuários, PDFs e dados sensíveis devem permanecer fora do versionamento quando contiverem informações reais.