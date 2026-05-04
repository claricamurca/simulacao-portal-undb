from pathlib import Path
from functools import wraps

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dash_table, dcc, html


BASE_DIR = Path(__file__).resolve().parents[2]

FILES = {
    "replicas": BASE_DIR / "results" / "simulation" / "simulacao_resultados.csv",
    "resumo": BASE_DIR / "results" / "simulation" / "resumo_cenarios.csv",
    "analitico": BASE_DIR / "results" / "simulation" / "comparacao_analitica_md1.csv",
    "empirico": BASE_DIR / "data" / "processed" / "resumo_tempos_observados.csv",
    "modelo": BASE_DIR / "data" / "processed" / "modelo_sugerido.csv",
}

EXPECTED_COLUMNS = {
    "replicas": [
        "modelo",
        "notacao_kendall",
        "periodo",
        "lambda_hora",
        "c",
        "replica",
        "seed",
        "tempo_medio_servico_seg",
        "mu_estimado_hora",
        "rho",
        "status_estabilidade",
        "total_chegadas",
        "total_atendidas",
        "Wq_seg",
        "W_seg",
        "Lq",
        "L",
        "P50_W_seg",
        "P90_W_seg",
        "P95_W_seg",
        "utilizacao_empirica",
        "throughput_hora",
        "taxa_fila",
        "fator_degradacao",
    ],
    "resumo": [
        "modelo",
        "notacao_kendall",
        "periodo",
        "lambda_hora",
        "c",
        "tempo_medio_servico_seg",
        "mu_estimado_hora",
        "rho_medio",
        "Wq_media_seg",
        "W_media_seg",
        "Lq_media",
        "L_media",
        "utilizacao_media",
        "P95_W_medio_seg",
        "throughput_medio_hora",
        "taxa_fila_media",
        "quantidade_replicas",
        "status_predominante",
        "fator_degradacao_medio",
    ],
    "analitico": [
        "periodo",
        "lambda_hora",
        "c",
        "rho_simulado",
        "status_simulado",
        "Wq_simulado_seg",
        "W_simulado_seg",
        "Lq_simulado",
        "L_simulado",
        "rho_analitico",
        "status_analitico",
        "Wq_analitico_seg",
        "W_analitico_seg",
        "Lq_analitico",
        "L_analitico",
        "erro_percentual_Wq",
        "erro_percentual_W",
    ],
    "empirico": [
        "metrica",
        "quantidade_amostras",
        "media",
        "mediana",
        "minimo",
        "maximo",
        "desvio_padrao",
        "p90",
        "p95",
        "coeficiente_variacao",
    ],
    "modelo": [
        "metrica",
        "coeficiente_variacao",
        "classificacao_variabilidade",
        "modelo_sugerido",
        "notacao_kendall_base",
    ],
}

NUMERIC_COLUMNS = {
    "lambda_hora",
    "c",
    "replica",
    "seed",
    "tempo_medio_servico_seg",
    "mu_estimado_hora",
    "rho",
    "rho_medio",
    "rho_simulado",
    "rho_analitico",
    "total_chegadas",
    "total_atendidas",
    "Wq_seg",
    "W_seg",
    "Wq_media_seg",
    "W_media_seg",
    "Wq_desvio_padrao_seg",
    "W_desvio_padrao_seg",
    "Lq",
    "L",
    "Lq_media",
    "L_media",
    "P50_W_seg",
    "P90_W_seg",
    "P95_W_seg",
    "P95_W_medio_seg",
    "utilizacao_empirica",
    "utilizacao_media",
    "throughput_hora",
    "throughput_medio_hora",
    "taxa_fila",
    "taxa_fila_media",
    "fator_degradacao",
    "fator_degradacao_medio",
    "quantidade_replicas",
    "quantidade_amostras",
    "media",
    "mediana",
    "minimo",
    "maximo",
    "desvio_padrao",
    "p90",
    "p95",
    "coeficiente_variacao",
    "Wq_simulado_seg",
    "W_simulado_seg",
    "Wq_analitico_seg",
    "W_analitico_seg",
    "Lq_simulado",
    "L_simulado",
    "Lq_analitico",
    "L_analitico",
    "diferenca_Wq_seg",
    "diferenca_W_seg",
    "diferenca_Lq",
    "diferenca_L",
    "erro_percentual_Wq",
    "erro_percentual_W",
}

BRAND_MAGENTA = "#FF2DAA"
OFFPEAK_BLUE = "#22D3EE"
PEAK_ORANGE = "#F59E0B"
STABLE_GREEN = "#22C55E"
UNSTABLE_RED = "#EF4444"
DEGRADATION_PURPLE = "#8B5CF6"
STRONG_BLUE = "#2563EB"
TEXT_DARK = "#F4F7FB"
TEXT_MUTED = "#AAB4D6"
CARD_BG = "#11182D"
PAGE_BG = "#0B1020"
BORDER_SOFT = "#1F2A44"


def load_csv_robust(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(path)
    except Exception:
        try:
            df = pd.read_csv(path, engine="python", on_bad_lines="skip")
        except Exception:
            return pd.DataFrame()

    df.columns = [str(col).strip() for col in df.columns]

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()

        if col in NUMERIC_COLUMNS:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        elif df[col].dtype == "object":
            numeric = pd.to_numeric(df[col], errors="coerce")
            if len(df[col]) > 0 and numeric.notna().sum() >= len(df[col]) * 0.8:
                df[col] = numeric

    return df


def missing_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    return [column for column in columns if column not in df.columns]


def has_columns(df: pd.DataFrame, columns: list[str]) -> bool:
    return not df.empty and not missing_columns(df, columns)


def alert_missing_columns(source: str, columns: list[str]) -> dbc.Alert:
    return dbc.Alert(
        [
            html.Strong(f"Colunas ausentes em {source}: "),
            ", ".join(columns),
        ],
        color="warning",
        className="mb-0",
    )


def service_distribution(modelo: str) -> str:
    text = str(modelo).lower()
    if "triangular" in text:
        return "Triangular"
    if "empirical" in text or "empiric" in text:
        return "Empirica"
    if "m/d/c" in text:
        return "Deterministica"
    if "m/g/c" in text:
        return "Geral"
    return "Nao informado"


def prepare_data() -> dict[str, pd.DataFrame]:
    data = {name: load_csv_robust(path) for name, path in FILES.items()}

    for name in ["resumo", "replicas"]:
        if not data[name].empty and "modelo" in data[name].columns:
            data[name]["distribuicao_servico"] = data[name]["modelo"].apply(
                service_distribution
            )

    return data


DATA = prepare_data()


def available_options(df: pd.DataFrame, column: str) -> list[dict]:
    if df.empty or column not in df.columns:
        return []
    values = sorted(df[column].dropna().unique().tolist())
    normalized = []
    for value in values:
        if hasattr(value, "item"):
            value = value.item()
        normalized.append({"label": str(value), "value": value})
    return normalized


def number(value, digits: int = 2, suffix: str = "") -> str:
    if pd.isna(value):
        return "N/D"
    if isinstance(value, str):
        return value
    return f"{float(value):,.{digits}f}{suffix}".replace(",", "X").replace(".", ",").replace("X", ".")


def empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"size": 16, "color": TEXT_MUTED},
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        xaxis={"visible": False},
        yaxis={"visible": False},
        height=360,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
    )
    return fig


def style_figure(fig: go.Figure, height: int = 390) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font={"family": "Inter, Segoe UI, Arial", "color": TEXT_DARK},
        title={"font": {"size": 16, "color": TEXT_DARK}, "x": 0.01, "xanchor": "left"},
        margin={"l": 42, "r": 24, "t": 62, "b": 48},
        legend_title_text="",
        hoverlabel={"bgcolor": "#0B1020", "bordercolor": BRAND_MAGENTA, "font_size": 12},
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        title_font={"size": 12, "color": TEXT_MUTED},
        tickfont={"color": TEXT_MUTED},
        linecolor=BORDER_SOFT,
    )
    fig.update_yaxes(
        gridcolor="rgba(170, 180, 214, 0.12)",
        zeroline=False,
        title_font={"size": 12, "color": TEXT_MUTED},
        tickfont={"color": TEXT_MUTED},
        linecolor=BORDER_SOFT,
    )
    fig.update_traces(line={"width": 3}, selector={"type": "scatter"})
    fig.update_traces(marker={"size": 8}, selector={"type": "scatter"})
    fig.update_traces(marker_line_width=0, selector={"type": "bar"})
    return fig


def kpi_card(title: str, value: str, subtitle: str = "", accent: str = BRAND_MAGENTA) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(title, className="kpi-title"),
                                html.Div(value, className="kpi-value"),
                                html.Div(subtitle, className="kpi-subtitle"),
                            ],
                            className="kpi-copy",
                        ),
                        html.Div(value, className="kpi-ring"),
                    ],
                    className="kpi-inner",
                ),
            ]
        ),
        className="kpi-card",
        style={"--accent": accent},
    )


def insight_card(title: str, text: str, color: str = BRAND_MAGENTA) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(title, className="insight-title", style={"color": color}),
                html.Div(text, className="insight-text"),
            ]
        ),
        className="insight-card",
        style={"borderLeft": f"5px solid {color}"},
    )


def data_table(df: pd.DataFrame, page_size: int = 12) -> dash_table.DataTable:
    if df.empty:
        df = pd.DataFrame({"mensagem": ["Arquivo nao encontrado ou sem dados."]})
    else:
        df = df.copy()

    df = df.replace([float("inf"), float("-inf")], pd.NA)
    df = df.astype(object).where(pd.notna(df), None)

    style_data_conditional = []
    if "status_predominante" in df.columns:
        style_data_conditional.extend(
            [
                {
                    "if": {"filter_query": '{status_predominante} = "ESTAVEL"'},
                    "backgroundColor": "rgba(34, 197, 94, 0.13)",
                    "color": TEXT_DARK,
                },
                {
                    "if": {"filter_query": '{status_predominante} = "INSTAVEL"'},
                    "backgroundColor": "rgba(239, 68, 68, 0.13)",
                    "color": TEXT_DARK,
                },
            ]
        )
    if "status_estabilidade" in df.columns:
        style_data_conditional.extend(
            [
                {
                    "if": {"filter_query": '{status_estabilidade} = "ESTAVEL"'},
                    "backgroundColor": "rgba(34, 197, 94, 0.13)",
                    "color": TEXT_DARK,
                },
                {
                    "if": {"filter_query": '{status_estabilidade} = "INSTAVEL"'},
                    "backgroundColor": "rgba(239, 68, 68, 0.13)",
                    "color": TEXT_DARK,
                },
            ]
        )

    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in df.columns],
        page_size=page_size,
        filter_action="native",
        sort_action="native",
        page_action="native",
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": "#0F172A",
            "color": TEXT_DARK,
            "fontWeight": "700",
            "border": f"1px solid {BORDER_SOFT}",
        },
        style_cell={
            "fontFamily": "Inter, Segoe UI, Arial",
            "fontSize": 13,
            "padding": "8px",
            "textAlign": "left",
            "minWidth": "110px",
            "maxWidth": "260px",
            "whiteSpace": "normal",
            "backgroundColor": CARD_BG,
            "color": TEXT_MUTED,
            "border": f"1px solid {BORDER_SOFT}",
        },
        style_filter={
            "backgroundColor": "#0B1020",
            "color": TEXT_DARK,
            "border": f"1px solid {BORDER_SOFT}",
        },
        style_data_conditional=style_data_conditional,
    )


def filter_df(
    df: pd.DataFrame,
    modelos,
    periodos,
    lambdas,
    capacities,
    statuses,
    distributions,
    status_column: str,
) -> pd.DataFrame:
    if df.empty:
        return df

    modelos = as_list(modelos)
    periodos = as_list(periodos)
    lambdas = as_list(lambdas)
    capacities = as_list(capacities)
    statuses = as_list(statuses)
    distributions = as_list(distributions)

    filtered = df.copy()

    if modelos and "modelo" in filtered.columns:
        filtered = filtered[filtered["modelo"].isin(modelos)]
    if periodos and "periodo" in filtered.columns:
        filtered = filtered[filtered["periodo"].isin(periodos)]
    if lambdas and "lambda_hora" in filtered.columns:
        filtered = filtered[filtered["lambda_hora"].isin(lambdas)]
    if capacities and "c" in filtered.columns:
        filtered = filtered[filtered["c"].isin(capacities)]
    if statuses and status_column in filtered.columns:
        filtered = filtered[filtered[status_column].isin(statuses)]
    if distributions and "distribuicao_servico" in filtered.columns:
        filtered = filtered[filtered["distribuicao_servico"].isin(distributions)]

    return filtered


def as_list(value) -> list:
    if value is None or value == "":
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def min_stable_c(summary: pd.DataFrame, lambda_hora: float):
    required = ["lambda_hora", "status_predominante", "c"]
    if not has_columns(summary, required):
        return None
    stable = summary[
        (summary["lambda_hora"] == lambda_hora)
        & (summary["status_predominante"] == "ESTAVEL")
    ]
    if stable.empty:
        return None
    return int(stable["c"].min())


def min_stable_table(summary: pd.DataFrame) -> pd.DataFrame:
    required = ["lambda_hora", "status_predominante", "c"]
    if not has_columns(summary, required):
        return pd.DataFrame(columns=["lambda_hora", "menor_c_estavel"])

    rows = []
    for lambda_hora, group in summary.groupby("lambda_hora"):
        stable = group[group["status_predominante"] == "ESTAVEL"]
        rows.append(
            {
                "lambda_hora": lambda_hora,
                "menor_c_estavel": int(stable["c"].min()) if not stable.empty else None,
            }
        )
    return pd.DataFrame(rows).sort_values("lambda_hora")


def make_period_comparison(summary: pd.DataFrame) -> go.Figure:
    required = ["periodo", "W_media_seg", "Wq_media_seg"]
    if not has_columns(summary, required):
        return empty_figure("Sem dados para comparar fora do pico e pico.")

    grouped = (
        summary.groupby("periodo", as_index=False)
        .agg(W_media_seg=("W_media_seg", "mean"), Wq_media_seg=("Wq_media_seg", "mean"))
    )
    fig = px.bar(
        grouped,
        x="periodo",
        y=["W_media_seg", "Wq_media_seg"],
        barmode="group",
        color_discrete_sequence=[OFFPEAK_BLUE, BRAND_MAGENTA],
        title="Fora do pico x pico: W e Wq em segundos",
        labels={"value": "Tempo (s)", "periodo": "Período", "variable": "Métrica"},
    )
    fig.update_traces(texttemplate="%{y:.1f}", textposition="outside", cliponaxis=False)
    return style_figure(fig)


def make_w_by_model(summary: pd.DataFrame) -> go.Figure:
    required = ["modelo", "W_media_seg"]
    if not has_columns(summary, required):
        return empty_figure("Sem dados de modelos ou coluna W_media_seg.")
    grouped = summary.groupby("modelo", as_index=False)["W_media_seg"].mean()
    fig = px.bar(
        grouped,
        x="modelo",
        y="W_media_seg",
        color="modelo",
        color_discrete_sequence=[BRAND_MAGENTA, DEGRADATION_PURPLE, OFFPEAK_BLUE],
        title="W — tempo médio no sistema (s) por modelo",
        labels={"W_media_seg": "W — tempo médio no sistema (s)", "modelo": "Modelo"},
    )
    fig.update_traces(texttemplate="%{y:.1f}", textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False)
    return style_figure(fig)


def make_stability_by_model(summary: pd.DataFrame) -> go.Figure:
    required = ["modelo", "status_predominante"]
    if not has_columns(summary, required):
        return empty_figure("Sem dados de estabilidade por modelo.")
    grouped = (
        summary.assign(estavel=summary["status_predominante"].eq("ESTAVEL").astype(int))
        .groupby("modelo", as_index=False)["estavel"]
        .mean()
    )
    grouped["taxa_estabilidade"] = grouped["estavel"] * 100
    fig = px.bar(
        grouped,
        x="modelo",
        y="taxa_estabilidade",
        color="modelo",
        color_discrete_sequence=[STABLE_GREEN, BRAND_MAGENTA, OFFPEAK_BLUE],
        title="Percentual de cenários estáveis por modelo",
        labels={"taxa_estabilidade": "Cenários estáveis (%)", "modelo": "Modelo"},
    )
    fig.update_yaxes(range=[0, 100])
    fig.update_traces(texttemplate="%{y:.0f}%", textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False)
    return style_figure(fig)


def make_cv_bar(empirical: pd.DataFrame) -> go.Figure:
    required = ["metrica", "coeficiente_variacao"]
    if not has_columns(empirical, required):
        return empty_figure("Sem dados empiricos de coeficiente de variacao.")
    fig = px.bar(
        empirical,
        x="metrica",
        y="coeficiente_variacao",
        color="metrica",
        color_discrete_sequence=[DEGRADATION_PURPLE, BRAND_MAGENTA, OFFPEAK_BLUE],
        title="Variabilidade empírica: coeficiente de variação por tempo",
        labels={"coeficiente_variacao": "Coeficiente de variação (CV)", "metrica": "Métrica"},
    )
    fig.add_hline(y=0.10, line_dash="dash", line_color=STABLE_GREEN, annotation_text="CV = 0,10")
    fig.add_hline(y=0.50, line_dash="dash", line_color=UNSTABLE_RED, annotation_text="CV = 0,50")
    fig.update_layout(showlegend=False)
    return style_figure(fig)


def make_empirical_time_bar(empirical: pd.DataFrame) -> go.Figure:
    required = ["metrica", "media", "p90", "p95"]
    if not has_columns(empirical, required):
        return empty_figure("Sem dados empiricos de media, P90 e P95.")
    fig = px.bar(
        empirical,
        x="metrica",
        y=["media", "p90", "p95"],
        barmode="group",
        color_discrete_sequence=[OFFPEAK_BLUE, BRAND_MAGENTA, DEGRADATION_PURPLE],
        title="Tempos observados usados na calibração",
        labels={"value": "Tempo (s)", "metrica": "Métrica", "variable": "Estatística"},
    )
    fig.update_traces(texttemplate="%{y:.1f}", textposition="outside", cliponaxis=False)
    return style_figure(fig)


def make_stability_heatmap(summary: pd.DataFrame) -> go.Figure:
    required = ["status_predominante", "c", "lambda_hora"]
    if not has_columns(summary, required):
        return empty_figure("Sem dados de estabilidade.")
    matrix = summary.assign(
        estabilidade=summary["status_predominante"].eq("ESTAVEL").astype(int)
    ).pivot_table(index="c", columns="lambda_hora", values="estabilidade", aggfunc="mean")
    fig = px.imshow(
        matrix,
        color_continuous_scale=[[0, UNSTABLE_RED], [1, STABLE_GREEN]],
        zmin=0,
        zmax=1,
        aspect="auto",
        title="Mapa de estabilidade por λ e capacidade",
        labels={"x": "λ — chegadas/hora", "y": "Capacidade paralela (c)", "color": "Estabilidade"},
    )
    fig.update_coloraxes(colorbar_tickvals=[0, 1], colorbar_ticktext=["Instável", "Estável"])
    return style_figure(fig)


def make_rho_line(summary: pd.DataFrame) -> go.Figure:
    required = ["c", "lambda_hora", "rho_medio"]
    if not has_columns(summary, required):
        return empty_figure("Sem dados de rho.")
    plot_df = summary.sort_values(["c", "lambda_hora"]).copy()
    plot_df["c_label"] = "c=" + plot_df["c"].astype(str)
    fig = px.line(
        plot_df,
        x="lambda_hora",
        y="rho_medio",
        color="c_label",
        markers=True,
        title="ρ — utilização do sistema por λ e capacidade",
        labels={"lambda_hora": "λ — chegadas/hora", "rho_medio": "ρ — utilização do sistema", "c_label": "Capacidade paralela (c)"},
    )
    fig.add_hline(y=1, line_dash="dash", line_color=UNSTABLE_RED, annotation_text="ρ = 1")
    return style_figure(fig)


def make_min_c_bar(summary: pd.DataFrame) -> go.Figure:
    table = min_stable_table(summary)
    if table.empty:
        return empty_figure("Sem capacidade estavel encontrada.")
    fig = px.bar(
        table,
        x="lambda_hora",
        y="menor_c_estavel",
        color="lambda_hora",
        color_continuous_scale=[OFFPEAK_BLUE, PEAK_ORANGE],
        title="Capacidade mínima estável por λ",
        labels={"lambda_hora": "λ — chegadas/hora", "menor_c_estavel": "Menor c estável"},
    )
    fig.update_traces(texttemplate="%{y:.0f}", textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False)
    return style_figure(fig)


def make_metric_heatmap(summary: pd.DataFrame, metric: str, title: str) -> go.Figure:
    required = ["c", "lambda_hora", metric]
    if not has_columns(summary, required):
        return empty_figure(f"Sem dados de {metric}.")
    matrix = summary.pivot_table(index="c", columns="lambda_hora", values=metric, aggfunc="mean")
    fig = px.imshow(
        matrix,
        color_continuous_scale=[[0, "#17203A"], [0.45, DEGRADATION_PURPLE], [1, BRAND_MAGENTA]],
        aspect="auto",
        title=title,
        labels={"x": "λ — chegadas/hora", "y": "Capacidade paralela (c)", "color": metric},
    )
    return style_figure(fig)


def make_line_metric(summary: pd.DataFrame, metric: str, title: str, y_label: str) -> go.Figure:
    required = ["c", "lambda_hora", metric]
    if not has_columns(summary, required):
        return empty_figure(f"Sem dados de {metric}.")
    plot_df = summary.sort_values(["c", "lambda_hora"]).copy()
    plot_df["c_label"] = "c=" + plot_df["c"].astype(str)
    fig = px.line(
        plot_df,
        x="lambda_hora",
        y=metric,
        color="c_label",
        markers=True,
        title=title,
        labels={"lambda_hora": "λ — chegadas/hora", metric: y_label, "c_label": "Capacidade paralela (c)"},
        color_discrete_sequence=[DEGRADATION_PURPLE, BRAND_MAGENTA, OFFPEAK_BLUE, STRONG_BLUE, PEAK_ORANGE, STABLE_GREEN]
        if metric == "fator_degradacao_medio"
        else None,
    )
    return style_figure(fig)


def make_degradation_heatmap(summary: pd.DataFrame) -> go.Figure:
    required = ["c", "lambda_hora", "fator_degradacao_medio"]
    if not has_columns(summary, required):
        return empty_figure("Sem dados de fator de degradacao.")
    matrix = summary.pivot_table(
        index="c",
        columns="lambda_hora",
        values="fator_degradacao_medio",
        aggfunc="mean",
    )
    fig = px.imshow(
        matrix,
        color_continuous_scale=[[0, "#151B33"], [0.4, DEGRADATION_PURPLE], [1, BRAND_MAGENTA]],
        aspect="auto",
        title="Fator de degradação por chegada e capacidade",
        labels={
            "x": "λ — chegadas/hora",
            "y": "Capacidade paralela (c)",
            "color": "Degradação",
        },
    )
    return style_figure(fig)


def make_degradation_period(summary: pd.DataFrame) -> go.Figure:
    required = ["periodo", "fator_degradacao_medio"]
    if not has_columns(summary, required):
        return empty_figure("Sem dados de degradacao.")
    grouped = summary.groupby("periodo", as_index=False)["fator_degradacao_medio"].mean()
    fig = px.bar(
        grouped,
        x="periodo",
        y="fator_degradacao_medio",
        color="periodo",
        color_discrete_map={"fora_pico": OFFPEAK_BLUE, "pico": PEAK_ORANGE},
        title="Fator de degradação médio por período",
        labels={"fator_degradacao_medio": "Fator de degradação", "periodo": "Período"},
    )
    fig.update_traces(texttemplate="%{y:.2f}x", textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False)
    return style_figure(fig)


def make_analytical_comparison(analytical: pd.DataFrame, sim_metric: str, ana_metric: str, title: str) -> go.Figure:
    required = ["lambda_hora", sim_metric, ana_metric]
    if not has_columns(analytical, required):
        return empty_figure("Sem dados analiticos.")
    plot_df = analytical[["lambda_hora", sim_metric, ana_metric]].melt(
        id_vars="lambda_hora",
        var_name="origem",
        value_name="valor",
    )
    plot_df["valor"] = plot_df["valor"].round(2)
    plot_df["origem"] = plot_df["origem"].replace(
        {
            "Wq_simulado_seg": "Wq simulado (s)",
            "Wq_analitico_seg": "Wq analítico (s)",
            "W_simulado_seg": "W simulado (s)",
            "W_analitico_seg": "W analítico (s)",
        }
    )
    fig = px.line(
        plot_df,
        x="lambda_hora",
        y="valor",
        color="origem",
        markers=True,
        color_discrete_sequence=[BRAND_MAGENTA, OFFPEAK_BLUE],
        title=title,
        labels={"lambda_hora": "λ — chegadas/hora", "valor": "Tempo (s)", "origem": ""},
    )
    return style_figure(fig)


def add_error_percentages(analytical: pd.DataFrame) -> pd.DataFrame:
    df = analytical.copy()
    if df.empty:
        return df

    if "Wq_analitico_seg" in df.columns and "diferenca_Wq_seg" in df.columns:
        df["erro_percentual_Wq"] = (
            df["diferenca_Wq_seg"].abs() / df["Wq_analitico_seg"].abs() * 100
        )
    if "W_analitico_seg" in df.columns and "diferenca_W_seg" in df.columns:
        df["erro_percentual_W"] = (
            df["diferenca_W_seg"].abs() / df["W_analitico_seg"].abs() * 100
        )
    return df


def diagnostic_dataframe() -> pd.DataFrame:
    rows = []
    for name, path in FILES.items():
        df = DATA.get(name, pd.DataFrame())
        expected = EXPECTED_COLUMNS.get(name, [])
        missing = missing_columns(df, expected) if not df.empty else expected
        rows.append(
            {
                "arquivo": name,
                "caminho": str(path.relative_to(BASE_DIR)),
                "encontrado": path.exists(),
                "linhas_carregadas": len(df),
                "colunas_disponiveis": ", ".join(map(str, df.columns.tolist())),
                "colunas_ausentes_esperadas": ", ".join(missing),
            }
        )
    return pd.DataFrame(rows)


def column_alerts() -> list:
    alerts = []
    for name, expected in EXPECTED_COLUMNS.items():
        df = DATA.get(name, pd.DataFrame())
        if df.empty:
            alerts.append(
                dbc.Alert(
                    f"{name}: arquivo ausente ou sem dados carregados.",
                    color="warning",
                    className="mb-2",
                )
            )
            continue

        missing = missing_columns(df, expected)
        if missing:
            alerts.append(alert_missing_columns(name, missing))

    if not alerts:
        alerts.append(
            dbc.Alert(
                "Todos os CSVs esperados foram encontrados com as colunas principais disponíveis.",
                color="success",
                className="mb-2",
            )
        )
    return alerts


def callback_error_outputs(error: Exception) -> tuple:
    message = f"O callback encontrou um erro, mas a interface foi preservada: {type(error).__name__}: {error}"
    error_fig = empty_figure(message)
    alert = dbc.Alert(message, color="danger", className="mt-3")
    error_table = data_table(pd.DataFrame({"erro": [message]}))

    # A quantidade retornada precisa permanecer igual aos Outputs declarados.
    return (
        alert,
        error_fig,
        error_fig,
        error_fig,
        alert,
        error_fig,
        error_fig,
        alert,
        error_table,
        error_table,
        error_fig,
        error_fig,
        error_table,
        error_fig,
        error_fig,
        error_fig,
        error_fig,
        error_fig,
        error_fig,
        error_fig,
        error_fig,
        error_fig,
        alert,
        error_fig,
        error_fig,
        alert,
        error_table,
        error_table,
        error_table,
        error_table,
    )


def safe_dashboard_callback(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if not isinstance(result, tuple) or len(result) != 30:
                raise ValueError(
                    f"Callback retornou {len(result) if isinstance(result, tuple) else 'valor nao-tupla'} valores; esperado: 30."
                )
            return result
        except Exception as error:
            return callback_error_outputs(error)

    return wrapper


summary_options = DATA["resumo"]
replica_options = DATA["replicas"]

status_values = []
if not summary_options.empty and "status_predominante" in summary_options.columns:
    status_values = sorted(summary_options["status_predominante"].dropna().unique().tolist())
elif not replica_options.empty and "status_estabilidade" in replica_options.columns:
    status_values = sorted(replica_options["status_estabilidade"].dropna().unique().tolist())

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
server = app.server

app.layout = html.Div(
    [
        dcc.Store(id="data-refresh", data=0),
        html.Div(
            [
                html.H1("Dashboard de Simulação — Portal do Aluno UNDB", className="header-title"),
                html.Div(
                    "Análise do fluxo de Requerimento de Horas Complementares com modelos M/D/c e M/G/c",
                    className="header-subtitle",
                ),
                html.Div(
                    "Simulação de Eventos Discretos · Notação de Kendall · SimPy",
                    className="header-badge",
                ),
            ],
            className="app-header",
        ),
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H5("Filtros", className="fw-bold mb-2"),
                                html.Div("Modelo", className="filter-label"),
                                dcc.Dropdown(
                                    id="filter-modelo",
                                    options=available_options(summary_options, "modelo"),
                                    multi=True,
                                    placeholder="Todos",
                                ),
                                html.Div("Período", className="filter-label"),
                                dcc.Dropdown(
                                    id="filter-periodo",
                                    options=available_options(summary_options, "periodo"),
                                    multi=True,
                                    placeholder="Todos",
                                ),
                                html.Div("λ chegadas/hora", className="filter-label"),
                                dcc.Dropdown(
                                    id="filter-lambda",
                                    options=available_options(summary_options, "lambda_hora"),
                                    multi=True,
                                    placeholder="Todos",
                                ),
                                html.Div("Capacidade c", className="filter-label"),
                                dcc.Dropdown(
                                    id="filter-c",
                                    options=available_options(summary_options, "c"),
                                    multi=True,
                                    placeholder="Todos",
                                ),
                                html.Div("Status", className="filter-label"),
                                dcc.Dropdown(
                                    id="filter-status",
                                    options=[{"label": s, "value": s} for s in status_values],
                                    multi=True,
                                    placeholder="Todos",
                                ),
                                html.Div("Distribuição de serviço", className="filter-label"),
                                dcc.Dropdown(
                                    id="filter-distribution",
                                    options=available_options(summary_options, "distribuicao_servico"),
                                    multi=True,
                                    placeholder="Todas",
                                ),
                                dbc.Button(
                                    "Limpar filtros",
                                    id="clear-filters",
                                    color="secondary",
                                    outline=True,
                                    className="clear-filters-btn mt-3 w-100",
                                ),
                            ],
                            className="sidebar",
                        ),
                        width=12,
                        lg=3,
                    ),
                    dbc.Col(
                        dcc.Tabs(
                            id="tabs",
                            className="dash-tabs",
                            children=[
                                dcc.Tab(label="Visão Geral", children=[
                                    html.Div(id="overview-kpis", className="mt-4"),
                                    html.Div(id="overview-insights", className="mt-3"),
                                    dbc.Row(
                                        [
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-period-comparison")), className="graph-card"), lg=4),
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-w-model")), className="graph-card"), lg=4),
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-stability-model")), className="graph-card"), lg=4),
                                        ],
                                        className="g-3 mt-3",
                                    ),
                                ]),
                                dcc.Tab(label="Calibração", children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(html.Div(id="calibration-explain"), lg=12),
                                        ],
                                        className="g-3 mt-4",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-cv")), className="graph-card"), lg=6),
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-empirical-times")), className="graph-card"), lg=6),
                                        ],
                                        className="g-3 mt-2",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(dbc.Card(dbc.CardBody(html.Div(id="table-empirical")), className="table-card"), lg=7),
                                            dbc.Col(dbc.Card(dbc.CardBody(html.Div(id="table-model-selection")), className="table-card"), lg=5),
                                        ],
                                        className="g-3 mt-2",
                                    ),
                                ]),
                                dcc.Tab(label="Estabilidade", children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-stability-heatmap")), className="graph-card"), lg=6),
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-rho")), className="graph-card"), lg=6),
                                        ],
                                        className="g-3 mt-4",
                                    ),
                                    html.Div(
                                        "ρ < 1 indica estabilidade; ρ ≥ 1 indica saturação e crescimento da fila.",
                                        className="section-note mt-2",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(dbc.Card(dbc.CardBody(html.Div(id="table-min-c")), className="table-card"), lg=5),
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-min-c")), className="graph-card"), lg=7),
                                        ],
                                        className="g-3 mt-2",
                                    ),
                                ]),
                                dcc.Tab(label="Filas", children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-wq-heatmap")), className="graph-card"), lg=6),
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-lq-heatmap")), className="graph-card"), lg=6),
                                        ],
                                        className="g-3 mt-4",
                                    ),
                                    html.Div(
                                        "Quanto mais escuro, maior a formação de fila e maior a pressão sobre a capacidade do portal.",
                                        className="section-note mt-2",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-w-line")), className="graph-card"), lg=6),
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-p95-line")), className="graph-card"), lg=6),
                                        ],
                                        className="g-3 mt-2",
                                    ),
                                    dbc.Card(dbc.CardBody(dcc.Graph(id="fig-throughput")), className="graph-card mt-2"),
                                ]),
                                dcc.Tab(label="Degradação", children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-deg-heatmap")), className="graph-card"), lg=6),
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-deg-period")), className="graph-card"), lg=6),
                                        ],
                                        className="g-3 mt-4",
                                    ),
                                    dbc.Card(dbc.CardBody(dcc.Graph(id="fig-deg-line")), className="graph-card mt-2"),
                                    html.Div(id="degradation-text", className="mt-3"),
                                ]),
                                dcc.Tab(label="Comparação Analítica", children=[
                                    html.Div(
                                        "Comparação entre fórmulas M/D/1 e simulação: esta aba serve como validação do simulador no caso c=1 estável.",
                                        className="section-note mt-4",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-analytical-wq")), className="graph-card"), lg=6),
                                            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="fig-analytical-w")), className="graph-card"), lg=6),
                                        ],
                                        className="g-3 mt-2",
                                    ),
                                    html.Div(id="analytical-explain", className="mt-3"),
                                    dbc.Card(dbc.CardBody(html.Div(id="table-analytical-errors")), className="table-card mt-3"),
                                ]),
                                dcc.Tab(label="Dados", children=[
                                    dbc.Accordion(
                                        [
                                            dbc.AccordionItem(html.Div(id="table-summary-data"), title="Resumo de cenários consolidados"),
                                            dbc.AccordionItem(html.Div(id="table-replica-data"), title="Resultados por réplica"),
                                            dbc.AccordionItem(html.Div(id="table-analytical-data"), title="Comparação analítica M/D/1"),
                                        ],
                                        start_collapsed=True,
                                        className="mt-4 mb-4",
                                    ),
                                ]),
                                dcc.Tab(label="Diagnóstico", children=[
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H5("Diagnóstico de carga dos CSVs"),
                                                html.P(
                                                    "Esta seção ajuda a identificar arquivos ausentes, linhas carregadas e colunas disponíveis.",
                                                    className="text-muted",
                                                ),
                                                html.Div(column_alerts()),
                                                data_table(diagnostic_dataframe(), page_size=10),
                                            ]
                                        ),
                                        className="table-card mt-4 mb-4",
                                    ),
                                ]),
                            ],
                        ),
                        width=12,
                        lg=9,
                    ),
                ],
                className="g-4 mt-2",
            ),
            fluid=True,
        ),
    ],
    style={"backgroundColor": PAGE_BG, "minHeight": "100vh"},
)


@app.callback(
    Output("overview-kpis", "children"),
    Output("fig-period-comparison", "figure"),
    Output("fig-w-model", "figure"),
    Output("fig-stability-model", "figure"),
    Output("overview-insights", "children"),
    Output("fig-cv", "figure"),
    Output("fig-empirical-times", "figure"),
    Output("calibration-explain", "children"),
    Output("table-empirical", "children"),
    Output("table-model-selection", "children"),
    Output("fig-stability-heatmap", "figure"),
    Output("fig-rho", "figure"),
    Output("table-min-c", "children"),
    Output("fig-min-c", "figure"),
    Output("fig-wq-heatmap", "figure"),
    Output("fig-lq-heatmap", "figure"),
    Output("fig-w-line", "figure"),
    Output("fig-p95-line", "figure"),
    Output("fig-throughput", "figure"),
    Output("fig-deg-heatmap", "figure"),
    Output("fig-deg-period", "figure"),
    Output("fig-deg-line", "figure"),
    Output("degradation-text", "children"),
    Output("fig-analytical-wq", "figure"),
    Output("fig-analytical-w", "figure"),
    Output("analytical-explain", "children"),
    Output("table-analytical-errors", "children"),
    Output("table-summary-data", "children"),
    Output("table-replica-data", "children"),
    Output("table-analytical-data", "children"),
    Input("filter-modelo", "value"),
    Input("filter-periodo", "value"),
    Input("filter-lambda", "value"),
    Input("filter-c", "value"),
    Input("filter-status", "value"),
    Input("filter-distribution", "value"),
)
@safe_dashboard_callback
def update_dashboard(modelos, periodos, lambdas, capacities, statuses, distributions):
    modelos = as_list(modelos)
    periodos = as_list(periodos)
    lambdas = as_list(lambdas)
    capacities = as_list(capacities)
    statuses = as_list(statuses)
    distributions = as_list(distributions)

    summary = filter_df(
        DATA["resumo"],
        modelos,
        periodos,
        lambdas,
        capacities,
        statuses,
        distributions,
        "status_predominante",
    )
    replicas = filter_df(
        DATA["replicas"],
        modelos,
        periodos,
        lambdas,
        capacities,
        statuses,
        distributions,
        "status_estabilidade",
    )

    analytical = DATA["analitico"].copy()
    if not analytical.empty:
        if periodos and "periodo" in analytical.columns:
            analytical = analytical[analytical["periodo"].isin(periodos)]
        if lambdas and "lambda_hora" in analytical.columns:
            analytical = analytical[analytical["lambda_hora"].isin(lambdas)]
        if capacities and "c" in analytical.columns:
            analytical = analytical[analytical["c"].isin(capacities)]

    empirical = DATA["empirico"]
    model_selection = DATA["modelo"]

    total_scenarios = len(summary)
    total_replicas = int(summary["quantidade_replicas"].sum()) if "quantidade_replicas" in summary else len(replicas)
    max_degradation = summary["fator_degradacao_medio"].max() if "fator_degradacao_medio" in summary else pd.NA
    max_p95 = summary["P95_W_medio_seg"].max() if "P95_W_medio_seg" in summary else pd.NA

    suggested_model = "N/D"
    service_mean = "N/D"
    service_cv = "N/D"
    login_cv = "N/D"
    if not model_selection.empty and "metrica" in model_selection.columns:
        service_row = model_selection[model_selection["metrica"] == "tempo_solicitacao"]
        if not service_row.empty and "modelo_sugerido" in service_row.columns:
            suggested_model = str(service_row.iloc[0]["modelo_sugerido"])
    if not empirical.empty and "metrica" in empirical.columns:
        service_row = empirical[empirical["metrica"] == "tempo_solicitacao"]
        if not service_row.empty and "media" in service_row.columns:
            service_mean = f"{number(service_row.iloc[0]['media'], 2)} s"
        if not service_row.empty and "coeficiente_variacao" in service_row.columns:
            service_cv = number(service_row.iloc[0]["coeficiente_variacao"], 4)
        login_row = empirical[empirical["metrica"] == "tempo_login"]
        if not login_row.empty and "coeficiente_variacao" in login_row.columns:
            login_cv = number(login_row.iloc[0]["coeficiente_variacao"], 4)

    degradation_kpi = "N/D" if pd.isna(max_degradation) else f"{number(max_degradation, 2)}x"

    kpis = dbc.Row(
        [
            dbc.Col(kpi_card("Cenários simulados", str(total_scenarios), "combinações de λ, c e modelo", OFFPEAK_BLUE), md=6, xl=2),
            dbc.Col(kpi_card("Réplicas", str(total_replicas), "execuções independentes", STRONG_BLUE), md=6, xl=2),
            dbc.Col(kpi_card("Menor c estável λ=480", str(min_stable_c(summary, 480) or "N/D"), "capacidade mínima no início do pico", STABLE_GREEN), md=6, xl=2),
            dbc.Col(kpi_card("Menor c estável λ=720", str(min_stable_c(summary, 720) or "N/D"), "capacidade mínima em pico médio", STABLE_GREEN), md=6, xl=2),
            dbc.Col(kpi_card("Menor c estável λ=960", str(min_stable_c(summary, 960) or "N/D"), "capacidade mínima em pico alto", PEAK_ORANGE), md=6, xl=2),
            dbc.Col(kpi_card("Menor c estável λ=1200", str(min_stable_c(summary, 1200) or "N/D"), "capacidade mínima no pico máximo", BRAND_MAGENTA), md=6, xl=2),
            dbc.Col(kpi_card("Maior degradação", degradation_kpi, "pior relação contra o baseline", DEGRADATION_PURPLE), md=6, xl=2),
            dbc.Col(kpi_card("Maior P95 observado", number(max_p95, 2, " s"), "cauda de tempo no sistema", PEAK_ORANGE), md=6, xl=2),
            dbc.Col(kpi_card("Modelo calibrado", suggested_model, "decisão baseada no CV", BRAND_MAGENTA), md=6, xl=2),
            dbc.Col(kpi_card("Serviço calibrado", service_mean, "média de tempo_solicitacao", OFFPEAK_BLUE), md=6, xl=2),
        ],
        className="g-3",
    )

    if has_columns(summary, ["periodo", "c", "status_predominante"]):
        c1_offpeak = summary[
            (summary["periodo"] == "fora_pico")
            & (summary["c"] == 1)
        ]
    else:
        c1_offpeak = pd.DataFrame()
    c1_sufficient = (
        not c1_offpeak.empty
        and "status_predominante" in c1_offpeak.columns
        and c1_offpeak["status_predominante"].eq("ESTAVEL").all()
    )
    c_peak_max = min_stable_c(summary, 1200)

    insights = dbc.Row(
        [
            dbc.Col(
                insight_card(
                    "Capacidade fora do pico",
                    "c=1 foi suficiente nos cenários fora do pico filtrados."
                    if c1_sufficient
                    else "c=1 não cobre todos os cenários fora do pico filtrados ou não há dados suficientes.",
                    STABLE_GREEN if c1_sufficient else PEAK_ORANGE,
                ),
                lg=4,
            ),
            dbc.Col(
                insight_card(
                    "Pico máximo",
                    f"No maior pico λ=1200, o menor c estável observado foi {c_peak_max}."
                    if c_peak_max
                    else "Não há c estável visível para λ=1200 com os filtros atuais.",
                    DEGRADATION_PURPLE,
                ),
                lg=4,
            ),
            dbc.Col(
                insight_card(
                    "Leitura de ρ",
                    "ρ >= 1 indica instabilidade: a fila tende a crescer e as métricas deixam de representar regime estacionário.",
                    UNSTABLE_RED,
                ),
                lg=4,
            ),
        ],
        className="g-3",
    )

    calibration_explain = dbc.Row(
        [
            dbc.Col(
                insight_card(
                    "Serviço principal escolhido",
                    f"tempo_solicitacao foi usado como serviço porque o CV é {service_cv}, indicando baixa variabilidade e justificando M/D/c.",
                    BRAND_MAGENTA,
                ),
                lg=4,
            ),
            dbc.Col(
                insight_card(
                    "Login fora do serviço",
                    f"tempo_login não foi usado como serviço principal porque o CV é {login_cv}, refletindo autenticação e variação de sessão.",
                    PEAK_ORANGE,
                ),
                lg=4,
            ),
            dbc.Col(
                insight_card(
                    "Fluxo completo",
                    "tempo_total representa navegação, login e solicitação; por isso é melhor como análise complementar M/G/c.",
                    DEGRADATION_PURPLE,
                ),
                lg=4,
            ),
        ],
        className="g-3",
    )

    min_c_df = min_stable_table(summary)
    analytical_with_errors = add_error_percentages(analytical)
    error_columns = [
        col
        for col in [
            "periodo",
            "lambda_hora",
            "c",
            "status_analitico",
            "erro_percentual_Wq",
            "erro_percentual_W",
        ]
        if col in analytical_with_errors.columns
    ]

    worst_degradation = max_degradation
    degradation_text = dbc.Row(
        [
            dbc.Col(
                insight_card(
                    "Pior cenário",
                    f"O pior cenário apresentou degradação de {number(worst_degradation, 2)} vezes em relação ao baseline."
                    if not pd.isna(worst_degradation)
                    else "Não há fator de degradação disponível para os filtros atuais.",
                    DEGRADATION_PURPLE,
                ),
                lg=6,
            ),
            dbc.Col(
                insight_card(
                    "Efeito de c",
                    "O aumento de c reduz a degradação, diminui o tempo de espera e melhora a estabilidade do sistema.",
                    STABLE_GREEN,
                ),
                lg=6,
            ),
        ],
        className="g-3",
    )

    analytical_explain = insight_card(
        "Validação M/D/1",
        "Esta comparação valida o simulador no caso M/D/1 estável. Quando ρ >= 1, as métricas analíticas ficam indefinidas porque o sistema é instável.",
        BRAND_MAGENTA,
    )

    return (
        kpis,
        make_period_comparison(summary),
        make_w_by_model(summary),
        make_stability_by_model(summary),
        insights,
        make_cv_bar(empirical),
        make_empirical_time_bar(empirical),
        calibration_explain,
        data_table(empirical),
        data_table(model_selection),
        make_stability_heatmap(summary),
        make_rho_line(summary),
        data_table(min_c_df),
        make_min_c_bar(summary),
        make_metric_heatmap(summary, "Wq_media_seg", "Wq — tempo médio em fila (s) por λ e c"),
        make_metric_heatmap(summary, "Lq_media", "Lq — solicitações médias na fila por λ e c"),
        make_line_metric(summary, "W_media_seg", "W — tempo médio no sistema (s) conforme λ", "W — tempo médio no sistema (s)"),
        make_line_metric(summary, "P95_W_medio_seg", "P95 de W (s) conforme λ", "P95 de W (s)"),
        make_line_metric(summary, "throughput_medio_hora", "Throughput médio por λ e c", "Throughput — atendimentos/hora"),
        make_degradation_heatmap(summary),
        make_degradation_period(summary),
        make_line_metric(summary, "fator_degradacao_medio", "Fator de degradação conforme aumento de λ", "Fator de degradação"),
        degradation_text,
        make_analytical_comparison(analytical, "Wq_simulado_seg", "Wq_analitico_seg", "M/D/1: Wq analítico (s) vs Wq simulado (s)"),
        make_analytical_comparison(analytical, "W_simulado_seg", "W_analitico_seg", "M/D/1: W analítico (s) vs W simulado (s)"),
        analytical_explain,
        data_table(analytical_with_errors[error_columns] if error_columns else analytical_with_errors),
        data_table(summary, page_size=15),
        data_table(replicas, page_size=15),
        data_table(analytical_with_errors, page_size=15),
    )


@app.callback(
    Output("filter-modelo", "value"),
    Output("filter-periodo", "value"),
    Output("filter-lambda", "value"),
    Output("filter-c", "value"),
    Output("filter-status", "value"),
    Output("filter-distribution", "value"),
    Input("clear-filters", "n_clicks"),
    prevent_initial_call=True,
)
def clear_filters(_):
    return None, None, None, None, None, None


def main() -> None:
    app.run(debug=True)


if __name__ == "__main__":
    main()
