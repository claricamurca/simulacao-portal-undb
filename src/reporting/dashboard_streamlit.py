from pathlib import Path
import html as html_lib

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


BASE_DIR = Path(__file__).resolve().parents[2]
PAGE_ICON = BASE_DIR / "assets" / "undb_page_icon.png"

FILES = {
    "simulacao_resultados": BASE_DIR / "results" / "simulation" / "simulacao_resultados.csv",
    "resumo_cenarios": BASE_DIR / "results" / "simulation" / "resumo_cenarios.csv",
    "comparacao_analitica": BASE_DIR / "results" / "simulation" / "comparacao_analitica_md1.csv",
    "resumo_tempos": BASE_DIR / "data" / "processed" / "resumo_tempos_observados.csv",
    "modelo_sugerido": BASE_DIR / "data" / "processed" / "modelo_sugerido.csv",
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

COLORS = {
    "bg": "#0B1020",
    "card": "#11182D",
    "border": "#1F2A44",
    "text": "#F4F7FB",
    "muted": "#AAB4D6",
    "pink": "#FF2DAA",
    "cyan": "#22D3EE",
    "purple": "#8B5CF6",
    "blue": "#2563EB",
    "green": "#22C55E",
    "red": "#EF4444",
    "orange": "#F59E0B",
}


st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed",
    page_title="Dashboard de Simulação — Portal UNDB",
    page_icon=str(PAGE_ICON),
)


def apply_css() -> None:
    st.markdown(
        f"""
        <style>
        #MainMenu {{
            visibility: hidden;
        }}

        footer, header {{
            visibility: hidden;
            display: none !important;
        }}

        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="collapsedControl"],
        [data-testid="stSidebar"],
        [data-testid="stSidebarContent"],
        .stDeployButton {{
            display: none !important;
            visibility: hidden !important;
        }}

        :root {{
            --bg: {COLORS["bg"]};
            --card: {COLORS["card"]};
            --border: {COLORS["border"]};
            --text: {COLORS["text"]};
            --muted: {COLORS["muted"]};
            --pink: {COLORS["pink"]};
            --cyan: {COLORS["cyan"]};
            --purple: {COLORS["purple"]};
            --blue: {COLORS["blue"]};
            --green: {COLORS["green"]};
            --red: {COLORS["red"]};
            --orange: {COLORS["orange"]};
        }}

        html, body, [data-testid="stAppViewContainer"] {{
            background:
                radial-gradient(circle at 12% 6%, rgba(34, 211, 238, .15), transparent 26%),
                radial-gradient(circle at 84% 8%, rgba(255, 45, 170, .16), transparent 28%),
                radial-gradient(circle at 50% 96%, rgba(139, 92, 246, .13), transparent 32%),
                var(--bg);
            color: var(--text);
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(17, 24, 45, .98), rgba(11, 16, 32, .98));
            border-right: 1px solid rgba(170, 180, 214, .12);
        }}

        [data-testid="stSidebar"] * {{
            color: var(--text);
        }}

        [data-testid="stSidebar"] label {{
            color: var(--muted) !important;
            font-size: .78rem !important;
            font-weight: 800 !important;
            letter-spacing: .04em;
            text-transform: uppercase;
        }}

        .block-container {{
            padding-top: 1.35rem;
            padding-bottom: 3rem;
            max-width: 1500px;
        }}

        .premium-header {{
            position: relative;
            overflow: hidden;
            padding: 1.45rem 1.7rem;
            margin-bottom: 1.55rem;
            border: 1px solid rgba(170, 180, 214, .14);
            border-radius: 28px;
            background:
                linear-gradient(135deg, rgba(17, 24, 45, .96), rgba(11, 16, 32, .94)),
                radial-gradient(circle at 16% 0%, rgba(34, 211, 238, .24), transparent 30%),
                radial-gradient(circle at 88% 15%, rgba(255, 45, 170, .28), transparent 32%);
            box-shadow: 0 22px 62px rgba(0, 0, 0, .34), 0 0 42px rgba(255, 45, 170, .08);
        }}

        .premium-header::before {{
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(90deg, transparent, rgba(34, 211, 238, .10), transparent),
                repeating-linear-gradient(90deg, rgba(244, 247, 251, .035) 0 1px, transparent 1px 86px);
            pointer-events: none;
        }}

        .premium-title {{
            position: relative;
            z-index: 1;
            margin: 0;
            color: var(--text);
            font-size: 1.75rem;
            line-height: 1.15;
            font-weight: 850;
        }}

        .premium-subtitle {{
            position: relative;
            z-index: 1;
            margin-top: .38rem;
            color: var(--muted);
            font-size: .96rem;
        }}

        .badge-row {{
            position: relative;
            z-index: 1;
            display: flex;
            gap: .55rem;
            flex-wrap: wrap;
            margin-top: .82rem;
        }}

        .neon-badge {{
            display: inline-flex;
            align-items: center;
            padding: .34rem .66rem;
            border-radius: 999px;
            color: #FFEAF7;
            background: rgba(255, 45, 170, .10);
            border: 1px solid rgba(255, 45, 170, .34);
            box-shadow: 0 0 20px rgba(255, 45, 170, .16);
            font-size: .78rem;
            font-weight: 750;
        }}

        .kpi-card, .insight-card, .chart-card, .note-card, .table-card {{
            position: relative;
            overflow: hidden;
            min-height: 100%;
            padding: 1rem;
            border: 1px solid rgba(170, 180, 214, .13);
            border-radius: 22px;
            background: linear-gradient(180deg, rgba(17, 24, 45, .98), rgba(15, 23, 42, .98));
            box-shadow: 0 18px 42px rgba(0, 0, 0, .28), inset 0 1px 0 rgba(244, 247, 251, .04);
        }}

        .kpi-card, .insight-card, .note-card {{
            margin-bottom: 1rem;
        }}

        .chart-card, .table-card {{
            padding: 0;
            margin: .35rem 0 1.35rem;
        }}

        [data-testid="stDecoration"] {{
            display: none !important;
        }}
        .kpi-card::before, .insight-card::before, .chart-card::before, .note-card::before, .table-card::before {{
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(135deg, rgba(255, 45, 170, .13), transparent 30%, rgba(34, 211, 238, .08));
        }}

        .kpi-label {{
            position: relative;
            z-index: 1;
            color: var(--muted);
            font-size: .70rem;
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: .06em;
        }}

        .kpi-value {{
            position: relative;
            z-index: 1;
            margin-top: .38rem;
            color: var(--text);
            font-size: 1.85rem;
            font-weight: 900;
            line-height: 1.05;
            text-shadow: 0 0 20px rgba(255, 45, 170, .24);
        }}

        .kpi-subtitle {{
            position: relative;
            z-index: 1;
            margin-top: .40rem;
            color: var(--muted);
            font-size: .80rem;
            line-height: 1.35;
        }}

        .kpi-accent {{
            position: absolute;
            right: .85rem;
            top: .85rem;
            width: 46px;
            height: 46px;
            border-radius: 50%;
            background:
                radial-gradient(circle, rgba(17, 24, 45, .96) 58%, transparent 61%),
                conic-gradient(var(--accent), rgba(34, 211, 238, .35), rgba(139, 92, 246, .66), var(--accent));
            box-shadow: 0 0 24px color-mix(in srgb, var(--accent) 35%, transparent);
        }}

        .insight-title {{
            position: relative;
            z-index: 1;
            color: var(--text);
            font-weight: 850;
            margin-bottom: .35rem;
        }}

        .insight-body {{
            position: relative;
            z-index: 1;
            color: var(--muted);
            font-size: .88rem;
            line-height: 1.45;
        }}

        .card-header-block {{
            position: relative;
            z-index: 1;
            padding: 1.02rem 1.12rem .82rem;
            border-bottom: 1px solid rgba(170, 180, 214, .10);
            background:
                linear-gradient(135deg, rgba(255, 45, 170, .075), transparent 38%),
                linear-gradient(180deg, rgba(244, 247, 251, .035), transparent);
        }}

        .chart-title, .table-title {{
            position: relative;
            z-index: 1;
            color: var(--text);
            font-weight: 850;
            margin: 0;
            font-size: .98rem;
            letter-spacing: .01em;
        }}

        .chart-subtitle, .table-subtitle {{
            position: relative;
            z-index: 1;
            margin-top: .28rem;
            color: var(--muted);
            font-size: .78rem;
            line-height: 1.35;
        }}

        .table-body {{
            position: relative;
            z-index: 1;
            padding: .85rem 1rem 1rem;
        }}

        .chart-card-header {{
            position: relative;
            z-index: 1;
            overflow: hidden;
            margin: .35rem 0 .18rem;
            padding: 1.02rem 1.12rem .82rem;
            border: 1px solid rgba(170, 180, 214, .13);
            border-radius: 22px 22px 12px 12px;
            background:
                linear-gradient(135deg, rgba(255, 45, 170, .075), transparent 38%),
                linear-gradient(180deg, rgba(17, 24, 45, .98), rgba(15, 23, 42, .98));
            box-shadow: 0 18px 42px rgba(0, 0, 0, .22), inset 0 1px 0 rgba(244, 247, 251, .04);
        }}

        .chart-card-header::before {{
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(135deg, rgba(255, 45, 170, .11), transparent 32%, rgba(34, 211, 238, .07));
        }}

        .table-meta {{
            display: inline-flex;
            align-items: center;
            gap: .45rem;
            margin: .1rem 0 .75rem;
            padding: .34rem .62rem;
            border-radius: 999px;
            color: var(--muted);
            background: rgba(34, 211, 238, .07);
            border: 1px solid rgba(34, 211, 238, .16);
            font-size: .76rem;
            font-weight: 750;
        }}

        .soft-warning {{
            position: relative;
            z-index: 1;
            padding: 1rem;
            border-radius: 18px;
            color: var(--muted);
            background: rgba(17, 24, 45, .82);
            border: 1px solid rgba(245, 158, 11, .28);
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: .35rem;
            padding: .4rem;
            border-radius: 18px;
            background: rgba(17, 24, 45, .48);
            border: 1px solid rgba(170, 180, 214, .10);
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 14px;
            padding: .55rem .95rem;
            color: var(--muted);
            font-weight: 760;
        }}

        .stTabs [aria-selected="true"] {{
            color: var(--text) !important;
            background: linear-gradient(135deg, rgba(255, 45, 170, .28), rgba(34, 211, 238, .16));
            box-shadow: 0 0 20px rgba(255, 45, 170, .14);
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid rgba(170, 180, 214, .14);
            border-radius: 18px;
            overflow: hidden;
            background: rgba(11, 16, 32, .42);
            box-shadow: inset 0 1px 0 rgba(244, 247, 251, .035);
        }}

        div[data-testid="stDataFrame"] div[role="columnheader"] {{
            background: rgba(34, 211, 238, .10) !important;
            color: var(--text) !important;
            font-weight: 800 !important;
        }}

        div[data-testid="stDataFrame"] div[role="gridcell"] {{
            color: var(--muted) !important;
        }}

        div[data-testid="stDataFrame"] div[role="row"]:nth-child(even) div[role="gridcell"] {{
            background: rgba(244, 247, 251, .025) !important;
        }}

        div[data-testid="stDataFrame"] div[role="row"]:hover div[role="gridcell"] {{
            background: rgba(34, 211, 238, .055) !important;
        }}

        div[data-testid="stPlotlyChart"] {{
            position: relative;
            z-index: 1;
        }}

        .table-scroll {{
            width: 100%;
            overflow-x: auto;
            border: 1px solid rgba(31, 42, 68, .95);
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(17, 24, 45, .98), rgba(11, 16, 32, .78));
        }}

        .styled-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            color: var(--muted);
            font-size: .82rem;
            line-height: 1.38;
            min-width: 760px;
        }}

        .styled-table thead th {{
            position: sticky;
            top: 0;
            z-index: 2;
            padding: .78rem .86rem;
            text-align: left;
            color: var(--text);
            background: linear-gradient(180deg, #16213A, rgba(17, 24, 45, .98));
            border-bottom: 1px solid rgba(34, 211, 238, .18);
            font-weight: 820;
            white-space: nowrap;
        }}

        .styled-table tbody td {{
            padding: .68rem .86rem;
            border-bottom: 1px solid rgba(31, 42, 68, .62);
            white-space: nowrap;
        }}

        .styled-table tbody tr:nth-child(odd) td {{
            background: rgba(11, 16, 32, .54);
        }}

        .styled-table tbody tr:nth-child(even) td {{
            background: rgba(17, 24, 45, .74);
        }}

        .styled-table tbody tr:hover td {{
            background: rgba(34, 211, 238, .08);
            color: var(--text);
        }}

        div[data-testid="stExpander"] {{
            border: 1px solid rgba(170, 180, 214, .12);
            border-radius: 18px;
            background: rgba(17, 24, 45, .38);
            margin-bottom: 1rem;
        }}

        div[data-testid="stVerticalBlock"] > div:has(.kpi-card),
        div[data-testid="stVerticalBlock"] > div:has(.insight-card),
        div[data-testid="stVerticalBlock"] > div:has(.chart-card),
        div[data-testid="stVerticalBlock"] > div:has(.chart-card-header),
        div[data-testid="stVerticalBlock"] > div:has(.table-card) {{
            margin-bottom: .55rem;
        }}

        .stButton > button {{
            width: 100%;
            border-radius: 12px;
            border: 1px solid rgba(34, 211, 238, .42);
            background: rgba(34, 211, 238, .07);
            color: var(--cyan);
            font-weight: 800;
        }}

        .stButton > button:hover {{
            border-color: var(--cyan);
            background: rgba(34, 211, 238, .16);
            color: var(--text);
            box-shadow: 0 0 20px rgba(34, 211, 238, .18);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    """Lê CSV de forma robusta, limpa colunas e converte métricas numéricas."""
    csv_path = Path(path)
    if not csv_path.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(csv_path)
    except Exception:
        try:
            df = pd.read_csv(csv_path, engine="python", on_bad_lines="skip")
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


def service_distribution(modelo: str) -> str:
    text = str(modelo).lower()
    if "triangular" in text:
        return "Triangular"
    if "empirical" in text or "empiric" in text:
        return "Empírica"
    if "m/d/c" in text:
        return "Determinística"
    if "m/g/c" in text:
        return "Geral"
    return "Não informado"


def load_all_data() -> dict[str, pd.DataFrame]:
    data = {name: load_csv(str(path)) for name, path in FILES.items()}
    for name in ["simulacao_resultados", "resumo_cenarios"]:
        df = data[name]
        if not df.empty and "modelo" in df.columns:
            df = df.copy()
            df["distribuicao_servico"] = df["modelo"].apply(service_distribution)
            data[name] = df
    return data


def format_number(value, digits: int = 2, suffix: str = "") -> str:
    if value is None or pd.isna(value):
        return "N/D"
    if isinstance(value, str):
        return value
    return f"{float(value):,.{digits}f}{suffix}".replace(",", "X").replace(".", ",").replace("X", ".")


def plotly_theme(fig: go.Figure, height: int = 390) -> go.Figure:
    """Aplica tema Plotly dark neon consistente."""
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font={"family": "Inter, Segoe UI, Arial", "color": COLORS["text"]},
        title_text="",
        margin={"l": 44, "r": 24, "t": 26, "b": 48},
        legend_title_text="",
        hoverlabel={"bgcolor": COLORS["bg"], "bordercolor": COLORS["pink"], "font_size": 12},
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        tickfont={"color": COLORS["muted"]},
        title_font={"color": COLORS["muted"], "size": 12},
        linecolor=COLORS["border"],
    )
    fig.update_yaxes(
        gridcolor="rgba(170, 180, 214, 0.12)",
        zeroline=False,
        tickfont={"color": COLORS["muted"]},
        title_font={"color": COLORS["muted"], "size": 12},
        linecolor=COLORS["border"],
    )
    fig.update_traces(line={"width": 3}, selector={"type": "scatter"})
    fig.update_traces(marker={"size": 8}, selector={"type": "scatter"})
    fig.update_traces(marker_line_width=0, selector={"type": "bar"})
    return fig


def empty_chart(message: str) -> None:
    st.markdown(
        f'<div class="soft-warning">{message}</div>',
        unsafe_allow_html=True,
    )


def render_kpi_card(title: str, value: str, subtitle: str, accent: str = "#FF2DAA") -> None:
    st.markdown(
        f"""
        <div class="kpi-card" style="--accent:{accent};">
            <div class="kpi-accent"></div>
            <div class="kpi-label">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_card(title: str, body: str, accent: str = "#22D3EE") -> None:
    st.markdown(
        f"""
        <div class="insight-card" style="border-left:4px solid {accent};">
            <div class="insight-title">{title}</div>
            <div class="insight-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chart_card(
    title: str,
    fig: go.Figure | None,
    message: str = "Sem dados suficientes.",
    chart_key: str | None = None,
    subtitle: str | None = None,
) -> None:
    subtitle_html = f'<div class="chart-subtitle">{html_lib.escape(subtitle)}</div>' if subtitle else ""
    with st.container():
        header_html = (
            '<div class="chart-card-header">'
            f'<div class="chart-title">{html_lib.escape(title)}</div>'
            f"{subtitle_html}"
            "</div>"
        )
        st.markdown(
            header_html,
            unsafe_allow_html=True,
        )
        if fig is None:
            empty_chart(message)
        else:
            fig.update_layout(title_text="")
            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
                key=chart_key,
            )


def _render_styled_table_legacy(
    title: str,
    df: pd.DataFrame,
    subtitle: str = "",
    columns: list[str] | None = None,
    height: int = 360,
    max_rows: int = 15,
) -> None:
    """Renderiza tabelas em um card visualmente consistente com o dashboard."""
    subtitle_html = f'<div class="table-subtitle">{html_lib.escape(subtitle)}</div>' if subtitle else ""

    if df is None or df.empty:
        empty_chart("Nenhum dado disponível para esta tabela.")
    else:
        table_df = df.copy()
        if columns:
            visible_columns = [col for col in columns if col in table_df.columns]
            if visible_columns:
                table_df = table_df[visible_columns]

        st.markdown(
            f'<div class="table-meta">{len(table_df):,} linhas - {len(table_df.columns)} colunas</div>'.replace(",", "."),
            unsafe_allow_html=True,
        )
        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            height=height,
        )

    return


def render_styled_table(
    title: str,
    df: pd.DataFrame,
    subtitle: str = "",
    columns: list[str] | None = None,
    height: int = 360,
    max_rows: int = 15,
) -> None:
    """Renderiza uma tabela HTML leve, com limite inicial e scroll horizontal."""
    subtitle_html = f'<div class="table-subtitle">{html_lib.escape(subtitle)}</div>' if subtitle else ""

    if df is None or df.empty:
        table_body = '<div class="soft-warning">Nenhum dado disponivel para esta tabela.</div>'
    else:
        table_df = df.copy()
        if columns:
            visible_columns = [col for col in columns if col in table_df.columns]
            if visible_columns:
                table_df = table_df[visible_columns]

        total_rows = len(table_df)
        displayed_df = table_df.head(max_rows).copy()
        for col in displayed_df.select_dtypes(include=["float", "float64", "float32"]).columns:
            digits = 4 if "coeficiente_variacao" in col else 2
            displayed_df[col] = displayed_df[col].round(digits)

        info = (
            f"Exibindo primeiras {min(total_rows, max_rows):,} de {total_rows:,} linhas "
            f"- {len(displayed_df.columns)} colunas"
        ).replace(",", ".")
        table_html = displayed_df.to_html(
            index=False,
            escape=True,
            classes="styled-table",
            border=0,
        )
        table_body = f"""
            <div class="table-meta">{html_lib.escape(info)}</div>
            <div class="table-scroll">{table_html}</div>
        """

    table_component_html = f"""
    <style>
        :root {{
            --bg: #0B1020;
            --card: #11182D;
            --border: #1F2A44;
            --text: #F4F7FB;
            --muted: #AAB4D6;
            --cyan: #22D3EE;
            --pink: #FF2DAA;
        }}
        body {{
            margin: 0;
            background: transparent;
            color: var(--text);
            font-family: Inter, "Segoe UI", Arial, sans-serif;
        }}
        .table-card {{
            overflow: hidden;
            border: 1px solid rgba(31, 42, 68, .95);
            border-radius: 22px;
            background:
                linear-gradient(135deg, rgba(255, 45, 170, .08), transparent 34%),
                linear-gradient(180deg, rgba(17, 24, 45, .98), rgba(11, 16, 32, .84));
            box-shadow: 0 18px 42px rgba(0, 0, 0, .24), inset 0 1px 0 rgba(244, 247, 251, .04);
        }}
        .card-header-block {{
            padding: 1.02rem 1.12rem .82rem;
            border-bottom: 1px solid rgba(170, 180, 214, .10);
            background:
                linear-gradient(135deg, rgba(255, 45, 170, .075), transparent 38%),
                linear-gradient(180deg, rgba(244, 247, 251, .035), transparent);
        }}
        .table-title {{
            color: var(--text);
            font-weight: 850;
            font-size: .98rem;
            letter-spacing: .01em;
        }}
        .table-subtitle {{
            margin-top: .28rem;
            color: var(--muted);
            font-size: .78rem;
            line-height: 1.35;
        }}
        .table-body {{
            padding: .85rem 1rem 1rem;
        }}
        .table-meta {{
            display: inline-flex;
            margin: .1rem 0 .75rem;
            padding: .34rem .62rem;
            border-radius: 999px;
            color: var(--muted);
            background: rgba(34, 211, 238, .07);
            border: 1px solid rgba(34, 211, 238, .16);
            font-size: .76rem;
            font-weight: 750;
        }}
        .table-scroll {{
            width: 100%;
            overflow-x: auto;
            border: 1px solid rgba(31, 42, 68, .95);
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(17, 24, 45, .98), rgba(11, 16, 32, .78));
        }}
        .styled-table {{
            width: 100%;
            min-width: 760px;
            border-collapse: separate;
            border-spacing: 0;
            color: var(--muted);
            font-size: .82rem;
            line-height: 1.38;
        }}
        .styled-table thead th {{
            padding: .78rem .86rem;
            text-align: left;
            color: var(--text);
            background: linear-gradient(180deg, #16213A, rgba(17, 24, 45, .98));
            border-bottom: 1px solid rgba(34, 211, 238, .18);
            font-weight: 820;
            white-space: nowrap;
        }}
        .styled-table tbody td {{
            padding: .68rem .86rem;
            border-bottom: 1px solid rgba(31, 42, 68, .62);
            white-space: nowrap;
        }}
        .styled-table tbody tr:nth-child(odd) td {{
            background: rgba(11, 16, 32, .54);
        }}
        .styled-table tbody tr:nth-child(even) td {{
            background: rgba(17, 24, 45, .74);
        }}
        .styled-table tbody tr:hover td {{
            background: rgba(34, 211, 238, .08);
            color: var(--text);
        }}
        .soft-warning {{
            padding: 1rem;
            border-radius: 18px;
            color: var(--muted);
            background: rgba(17, 24, 45, .82);
            border: 1px solid rgba(245, 158, 11, .28);
        }}
    </style>
    <div class="table-card">
        <div class="card-header-block">
            <div class="table-title">{html_lib.escape(title)}</div>
            {subtitle_html}
        </div>
        <div class="table-body">
            {table_body}
        </div>
    </div>
    """
    components.html(table_component_html, height=height, scrolling=True)
    return


def filtrar_dados(
    df: pd.DataFrame,
    modelos=None,
    periodos=None,
    lambdas=None,
    capacidades=None,
    status=None,
    distribuicoes=None,
    status_col: str = "status_predominante",
) -> pd.DataFrame:
    """Aplica os filtros globais sem quebrar quando algum filtro está vazio."""
    if df.empty:
        return df

    filtered = df.copy()
    filtros = {
        "modelo": modelos or [],
        "periodo": periodos or [],
        "lambda_hora": lambdas or [],
        "c": capacidades or [],
        status_col: status or [],
        "distribuicao_servico": distribuicoes or [],
    }

    for col, values in filtros.items():
        if values and col in filtered.columns:
            filtered = filtered[filtered[col].isin(values)]

    return filtered


def calcular_menor_c_estavel(summary: pd.DataFrame, lambda_hora: float | None = None) -> pd.DataFrame | int | None:
    required = {"lambda_hora", "c", "status_predominante"}
    if summary.empty or not required.issubset(summary.columns):
        return None if lambda_hora is not None else pd.DataFrame(columns=["lambda_hora", "menor_c_estavel"])

    if lambda_hora is not None:
        stable = summary[(summary["lambda_hora"] == lambda_hora) & (summary["status_predominante"] == "ESTAVEL")]
        return int(stable["c"].min()) if not stable.empty else None

    rows = []
    for lam, group in summary.groupby("lambda_hora"):
        stable = group[group["status_predominante"] == "ESTAVEL"]
        rows.append({"lambda_hora": lam, "menor_c_estavel": int(stable["c"].min()) if not stable.empty else np.nan})
    return pd.DataFrame(rows).sort_values("lambda_hora")


def calcular_kpis(summary: pd.DataFrame, empirical: pd.DataFrame, model_selection: pd.DataFrame) -> dict:
    total_cenarios = len(summary)
    total_replicas = int(summary["quantidade_replicas"].sum()) if "quantidade_replicas" in summary.columns else 0
    max_degradacao = summary["fator_degradacao_medio"].max() if "fator_degradacao_medio" in summary.columns else np.nan
    max_p95 = summary["P95_W_medio_seg"].max() if "P95_W_medio_seg" in summary.columns else np.nan
    taxa_estabilidade = (
        summary["status_predominante"].eq("ESTAVEL").mean() * 100
        if "status_predominante" in summary.columns and len(summary) > 0
        else np.nan
    )

    modelo_calibrado = "N/D"
    if not model_selection.empty and {"metrica", "modelo_sugerido"}.issubset(model_selection.columns):
        row = model_selection[model_selection["metrica"] == "tempo_solicitacao"]
        if not row.empty:
            modelo_calibrado = str(row.iloc[0]["modelo_sugerido"])

    servico_calibrado = "N/D"
    cv_servico = "N/D"
    if not empirical.empty and {"metrica", "media"}.issubset(empirical.columns):
        row = empirical[empirical["metrica"] == "tempo_solicitacao"]
        if not row.empty:
            servico_calibrado = f"{format_number(row.iloc[0]['media'], 2)} s"
            if "coeficiente_variacao" in row.columns:
                cv_servico = format_number(row.iloc[0]["coeficiente_variacao"], 4)

    return {
        "total_cenarios": total_cenarios,
        "total_replicas": total_replicas,
        "c_1200": calcular_menor_c_estavel(summary, 1200),
        "max_degradacao": max_degradacao,
        "modelo_calibrado": modelo_calibrado,
        "servico_calibrado": servico_calibrado,
        "cv_servico": cv_servico,
        "max_p95": max_p95,
        "taxa_estabilidade": taxa_estabilidade,
    }


def add_error_percentages(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    if "erro_percentual_Wq" not in df.columns and {"diferenca_Wq_seg", "Wq_analitico_seg"}.issubset(df.columns):
        df["erro_percentual_Wq"] = df["diferenca_Wq_seg"].abs() / df["Wq_analitico_seg"].abs() * 100
    if "erro_percentual_W" not in df.columns and {"diferenca_W_seg", "W_analitico_seg"}.issubset(df.columns):
        df["erro_percentual_W"] = df["diferenca_W_seg"].abs() / df["W_analitico_seg"].abs() * 100
    return df


def plot_period_comparison(summary: pd.DataFrame) -> go.Figure | None:
    required = {"periodo", "W_media_seg", "Wq_media_seg"}
    if summary.empty or not required.issubset(summary.columns):
        return None
    grouped = summary.groupby("periodo", as_index=False).agg(
        W_media_seg=("W_media_seg", "mean"),
        Wq_media_seg=("Wq_media_seg", "mean"),
    )
    fig = px.bar(
        grouped,
        x="periodo",
        y=["W_media_seg", "Wq_media_seg"],
        barmode="group",
        color_discrete_sequence=[COLORS["cyan"], COLORS["pink"]],
        labels={"value": "Tempo (s)", "periodo": "Período", "variable": "Métrica"},
    )
    fig.update_traces(texttemplate="%{y:.1f}", textposition="outside", cliponaxis=False)
    return plotly_theme(fig, 350)


def plot_min_c(summary: pd.DataFrame) -> go.Figure | None:
    table = calcular_menor_c_estavel(summary)
    if table is None or table.empty:
        return None
    fig = px.bar(
        table,
        x="lambda_hora",
        y="menor_c_estavel",
        color="lambda_hora",
        color_continuous_scale=[[0, COLORS["cyan"]], [1, COLORS["orange"]]],
        labels={"lambda_hora": "λ — chegadas/hora", "menor_c_estavel": "Menor c estável"},
    )
    fig.update_traces(texttemplate="%{y:.0f}", textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False)
    return plotly_theme(fig, 350)


def plot_stability_by_model(summary: pd.DataFrame) -> go.Figure | None:
    required = {"modelo", "status_predominante"}
    if summary.empty or not required.issubset(summary.columns):
        return None
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
        color_discrete_sequence=[COLORS["green"], COLORS["pink"], COLORS["cyan"]],
        labels={"modelo": "Modelo", "taxa_estabilidade": "Cenários estáveis (%)"},
    )
    fig.update_yaxes(range=[0, 100])
    fig.update_traces(texttemplate="%{y:.0f}%", textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False)
    return plotly_theme(fig, 350)


def plot_cv(empirical: pd.DataFrame) -> go.Figure | None:
    required = {"metrica", "coeficiente_variacao"}
    if empirical.empty or not required.issubset(empirical.columns):
        return None
    fig = px.bar(
        empirical,
        x="metrica",
        y="coeficiente_variacao",
        color="metrica",
        color_discrete_sequence=[COLORS["purple"], COLORS["pink"], COLORS["cyan"]],
        labels={"metrica": "Métrica", "coeficiente_variacao": "Coeficiente de variação (CV)"},
    )
    fig.add_hline(y=0.10, line_dash="dash", line_color=COLORS["green"], annotation_text="CV = 0,10")
    fig.add_hline(y=0.50, line_dash="dash", line_color=COLORS["red"], annotation_text="CV = 0,50")
    fig.update_layout(showlegend=False)
    return plotly_theme(fig, 380)


def plot_empirical_times(empirical: pd.DataFrame) -> go.Figure | None:
    required = {"metrica", "media", "p90", "p95"}
    if empirical.empty or not required.issubset(empirical.columns):
        return None
    fig = px.bar(
        empirical,
        x="metrica",
        y=["media", "p90", "p95"],
        barmode="group",
        color_discrete_sequence=[COLORS["cyan"], COLORS["pink"], COLORS["purple"]],
        labels={"value": "Tempo (s)", "metrica": "Métrica", "variable": "Estatística"},
    )
    fig.update_traces(texttemplate="%{y:.1f}", textposition="outside", cliponaxis=False)
    return plotly_theme(fig, 380)


def plot_stability_heatmap(summary: pd.DataFrame) -> go.Figure | None:
    required = {"status_predominante", "c", "lambda_hora"}
    if summary.empty or not required.issubset(summary.columns):
        return None
    matrix = summary.assign(
        estabilidade=summary["status_predominante"].eq("ESTAVEL").astype(int)
    ).pivot_table(index="c", columns="lambda_hora", values="estabilidade", aggfunc="mean")
    fig = px.imshow(
        matrix,
        color_continuous_scale=[[0, COLORS["red"]], [1, COLORS["green"]]],
        zmin=0,
        zmax=1,
        aspect="auto",
        labels={"x": "λ — chegadas/hora", "y": "Capacidade paralela (c)", "color": "Estabilidade"},
    )
    fig.update_coloraxes(colorbar_tickvals=[0, 1], colorbar_ticktext=["Instável", "Estável"])
    return plotly_theme(fig, 410)


def plot_rho(summary: pd.DataFrame) -> go.Figure | None:
    required = {"c", "lambda_hora", "rho_medio"}
    if summary.empty or not required.issubset(summary.columns):
        return None
    plot_df = summary.sort_values(["c", "lambda_hora"]).copy()
    plot_df["c_label"] = "c=" + plot_df["c"].astype(str)
    fig = px.line(
        plot_df,
        x="lambda_hora",
        y="rho_medio",
        color="c_label",
        markers=True,
        color_discrete_sequence=[COLORS["cyan"], COLORS["pink"], COLORS["purple"], COLORS["blue"], COLORS["orange"], COLORS["green"]],
        labels={"lambda_hora": "λ — chegadas/hora", "rho_medio": "ρ — utilização", "c_label": "Capacidade"},
    )
    fig.add_hline(y=1, line_dash="dash", line_color=COLORS["red"], annotation_text="ρ = 1")
    return plotly_theme(fig, 410)


def plot_heatmap_metric(summary: pd.DataFrame, metric: str) -> go.Figure | None:
    required = {"c", "lambda_hora", metric}
    if summary.empty or not required.issubset(summary.columns):
        return None
    matrix = summary.pivot_table(index="c", columns="lambda_hora", values=metric, aggfunc="mean")
    fig = px.imshow(
        matrix,
        color_continuous_scale=[[0, "#151B33"], [0.45, COLORS["purple"]], [1, COLORS["pink"]]],
        aspect="auto",
        labels={"x": "λ — chegadas/hora", "y": "Capacidade paralela (c)", "color": metric},
    )
    return plotly_theme(fig, 390)


def plot_line_metric(summary: pd.DataFrame, metric: str, y_label: str, purple: bool = False) -> go.Figure | None:
    required = {"c", "lambda_hora", metric}
    if summary.empty or not required.issubset(summary.columns):
        return None
    plot_df = summary.sort_values(["c", "lambda_hora"]).copy()
    plot_df["c_label"] = "c=" + plot_df["c"].astype(str)
    palette = [COLORS["purple"], COLORS["pink"], COLORS["cyan"], COLORS["blue"], COLORS["orange"], COLORS["green"]] if purple else None
    fig = px.line(
        plot_df,
        x="lambda_hora",
        y=metric,
        color="c_label",
        markers=True,
        color_discrete_sequence=palette,
        labels={"lambda_hora": "λ — chegadas/hora", metric: y_label, "c_label": "Capacidade"},
    )
    return plotly_theme(fig, 390)


def plot_degradation_period(summary: pd.DataFrame) -> go.Figure | None:
    required = {"periodo", "fator_degradacao_medio"}
    if summary.empty or not required.issubset(summary.columns):
        return None
    grouped = summary.groupby("periodo", as_index=False)["fator_degradacao_medio"].mean()
    fig = px.bar(
        grouped,
        x="periodo",
        y="fator_degradacao_medio",
        color="periodo",
        color_discrete_map={"fora_pico": COLORS["cyan"], "pico": COLORS["orange"]},
        labels={"periodo": "Período", "fator_degradacao_medio": "Fator de degradação"},
    )
    fig.update_traces(texttemplate="%{y:.2f}x", textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False)
    return plotly_theme(fig, 390)


def plot_analytical(analytical: pd.DataFrame, sim_col: str, ana_col: str) -> go.Figure | None:
    required = {"lambda_hora", sim_col, ana_col}
    if analytical.empty or not required.issubset(analytical.columns):
        return None
    plot_df = analytical[["lambda_hora", sim_col, ana_col]].melt(
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
        color_discrete_sequence=[COLORS["pink"], COLORS["cyan"]],
        labels={"lambda_hora": "λ — chegadas/hora", "valor": "Tempo (s)", "origem": ""},
    )
    return plotly_theme(fig, 390)


def diagnostic_table(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for name, path in FILES.items():
        df = data.get(name, pd.DataFrame())
        rows.append(
            {
                "arquivo": name,
                "caminho": str(path.relative_to(BASE_DIR)),
                "existe": path.exists(),
                "linhas": len(df),
                "colunas": ", ".join(df.columns.astype(str).tolist()),
            }
        )
    return pd.DataFrame(rows)


def render_header() -> None:
    st.markdown(
        """
        <div class="premium-header">
            <h1 class="premium-title">Dashboard de Simulação — Portal do Aluno UNDB</h1>
            <div class="premium-subtitle">Análise do fluxo de Requerimento de Horas Complementares</div>
            <div class="badge-row">
                <span class="neon-badge">SimPy</span>
                <span class="neon-badge">Notação de Kendall</span>
                <span class="neon-badge">M/D/c</span>
                <span class="neon-badge">M/G/c</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview(summary, empirical, model_selection) -> None:
    kpis = calcular_kpis(summary, empirical, model_selection)
    c1_offpeak = (
        summary[(summary["periodo"] == "fora_pico") & (summary["c"] == 1)]
        if {"periodo", "c"}.issubset(summary.columns)
        else pd.DataFrame()
    )
    c1_ok = not c1_offpeak.empty and "status_predominante" in c1_offpeak.columns and c1_offpeak["status_predominante"].eq("ESTAVEL").all()

    cols = st.columns(4)
    with cols[0]:
        render_kpi_card("Cenários simulados", str(kpis["total_cenarios"]), "combinações de λ, c e modelo", COLORS["cyan"])
    with cols[1]:
        render_kpi_card("Réplicas", str(kpis["total_replicas"]), "execuções independentes", COLORS["blue"])
    with cols[2]:
        render_kpi_card("Menor c estável λ=1200", str(kpis["c_1200"] or "N/D"), "capacidade mínima no pico máximo", COLORS["pink"])
    with cols[3]:
        render_kpi_card("Maior degradação", f"{format_number(kpis['max_degradacao'], 2)}x", "em relação ao baseline", COLORS["purple"])

    cols = st.columns(4)
    with cols[0]:
        render_kpi_card("Modelo calibrado", kpis["modelo_calibrado"], "decisão baseada no CV", COLORS["pink"])
    with cols[1]:
        render_kpi_card("Serviço calibrado", kpis["servico_calibrado"], "média de tempo_solicitacao", COLORS["cyan"])
    with cols[2]:
        render_kpi_card("Maior P95 observado", f"{format_number(kpis['max_p95'], 2)} s", "cauda do tempo no sistema", COLORS["orange"])
    with cols[3]:
        render_kpi_card("Taxa de estabilidade", f"{format_number(kpis['taxa_estabilidade'], 1)}%", "cenários estáveis", COLORS["green"])

    st.write("")
    insight_cols = st.columns(3)
    with insight_cols[0]:
        render_insight_card(
            "Capacidade fora do pico",
            "c=1 foi suficiente fora do pico nos filtros atuais." if c1_ok else "c=1 não cobre todos os cenários fora do pico filtrados ou não há dados suficientes.",
            COLORS["green"] if c1_ok else COLORS["orange"],
        )
    with insight_cols[1]:
        render_insight_card(
            "Pico máximo",
            f"No maior pico λ=1200, o menor c estável foi {kpis['c_1200']}." if kpis["c_1200"] else "Não há c estável visível para λ=1200 com os filtros atuais.",
            COLORS["pink"],
        )
    with insight_cols[2]:
        render_insight_card(
            "Leitura de ρ",
            "ρ ≥ 1 indica saturação: a fila tende a crescer e as métricas deixam de representar regime estacionário.",
            COLORS["red"],
        )

    chart_cols = st.columns(3)
    with chart_cols[0]:
        render_chart_card("W médio fora do pico vs pico", plot_period_comparison(summary), chart_key="overview_w_periodo")
    with chart_cols[1]:
        render_chart_card("Menor c estável por λ", plot_min_c(summary), chart_key="overview_min_c")
    with chart_cols[2]:
        render_chart_card("Taxa de estabilidade por modelo", plot_stability_by_model(summary), chart_key="overview_estabilidade_modelo")


def render_calibration(empirical, model_selection) -> None:
    service_cv = "N/D"
    login_cv = "N/D"
    suggested = "N/D"
    if not empirical.empty and "metrica" in empirical.columns:
        service = empirical[empirical["metrica"] == "tempo_solicitacao"]
        login = empirical[empirical["metrica"] == "tempo_login"]
        if not service.empty and "coeficiente_variacao" in service.columns:
            service_cv = format_number(service.iloc[0]["coeficiente_variacao"], 4)
        if not login.empty and "coeficiente_variacao" in login.columns:
            login_cv = format_number(login.iloc[0]["coeficiente_variacao"], 4)
    if not model_selection.empty and {"metrica", "modelo_sugerido"}.issubset(model_selection.columns):
        row = model_selection[model_selection["metrica"] == "tempo_solicitacao"]
        if not row.empty:
            suggested = str(row.iloc[0]["modelo_sugerido"])

    cols = st.columns(3)
    with cols[0]:
        render_insight_card("Serviço principal", f"tempo_solicitacao foi escolhido porque o CV é {service_cv}, muito baixo.", COLORS["cyan"])
    with cols[1]:
        render_insight_card("Login fora do serviço", f"tempo_login não foi usado como serviço principal porque o CV é {login_cv}.", COLORS["orange"])
    with cols[2]:
        render_insight_card("Modelo sugerido", f"A calibração indica {suggested} para a etapa de solicitação.", COLORS["pink"])

    chart_cols = st.columns(2)
    with chart_cols[0]:
        render_chart_card("Coeficiente de variação por métrica", plot_cv(empirical), chart_key="calibracao_cv")
    with chart_cols[1]:
        render_chart_card("Média, P90 e P95 observados", plot_empirical_times(empirical), chart_key="calibracao_tempos")

    with st.expander("Tabela de calibração empírica", expanded=False):
        render_styled_table(
            "Resumo de tempos observados",
            empirical,
            "Metricas estatisticas usadas para calibrar o servico da simulacao.",
            columns=[
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
        )
    with st.expander("Modelo sugerido pela calibração", expanded=False):
        render_styled_table(
            "Selecao inicial de modelo",
            model_selection,
            "Classificacao baseada no coeficiente de variacao observado.",
        )


def render_stability(summary) -> None:
    cols = st.columns(2)
    with cols[0]:
        render_chart_card("Estabilidade por λ e c", plot_stability_heatmap(summary), chart_key="estabilidade_heatmap")
    with cols[1]:
        render_chart_card("ρ — utilização do sistema", plot_rho(summary), chart_key="estabilidade_rho")
    st.markdown('<div class="note-card">ρ &lt; 1 indica estabilidade; ρ ≥ 1 indica saturação e crescimento da fila.</div>', unsafe_allow_html=True)
    table = calcular_menor_c_estavel(summary)
    cols = st.columns([1, 1.4])
    with cols[0]:
        render_styled_table(
            "Menor c estavel por lambda",
            table,
            "Capacidade minima encontrada para manter rho abaixo de 1.",
            columns=["lambda_hora", "menor_c_estavel"],
            height=300,
        )
    with cols[1]:
        render_chart_card("Capacidade mínima estável", plot_min_c(summary), chart_key="estabilidade_min_c")


def render_queues(summary) -> None:
    cols = st.columns(2)
    with cols[0]:
        render_chart_card("Wq — tempo médio em fila (s)", plot_heatmap_metric(summary, "Wq_media_seg"), chart_key="filas_wq_heatmap")
    with cols[1]:
        render_chart_card("Lq — solicitações médias na fila", plot_heatmap_metric(summary, "Lq_media"), chart_key="filas_lq_heatmap")
    st.markdown('<div class="note-card">Quanto mais intenso o mapa, maior a formação de fila. W, Wq e P95 estão em segundos; L e Lq são quantidades médias.</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    with cols[0]:
        render_chart_card("W — tempo médio no sistema (s)", plot_line_metric(summary, "W_media_seg", "W — tempo médio no sistema (s)"), chart_key="filas_w_linha")
    with cols[1]:
        render_chart_card("P95 de W (s)", plot_line_metric(summary, "P95_W_medio_seg", "P95 de W (s)"), chart_key="filas_p95_linha")


def render_degradation(summary) -> None:
    max_deg = summary["fator_degradacao_medio"].max() if "fator_degradacao_medio" in summary.columns else np.nan
    cols = st.columns([1, 1])
    with cols[0]:
        render_kpi_card("Pior degradação", f"{format_number(max_deg, 2)}x", "em relação ao baseline", COLORS["purple"])
    with cols[1]:
        render_insight_card("Conclusão automática", "O aumento de c reduz a degradação e melhora a estabilidade.", COLORS["purple"])

    cols = st.columns(2)
    with cols[0]:
        render_chart_card("Fator de degradação por λ e c", plot_heatmap_metric(summary, "fator_degradacao_medio"), chart_key="degradacao_heatmap")
    with cols[1]:
        render_chart_card("Pico vs fora do pico", plot_degradation_period(summary), chart_key="degradacao_periodo")
    render_chart_card("Degradação conforme λ", plot_line_metric(summary, "fator_degradacao_medio", "Fator de degradação", purple=True), chart_key="degradacao_lambda")


def render_analytical(analytical) -> None:
    analytical = add_error_percentages(analytical)
    st.markdown('<div class="note-card">Esta comparação valida o comportamento do simulador no caso M/D/1 estável. W e Wq estão em segundos para analítico e simulado.</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    with cols[0]:
        render_chart_card("Wq analítico vs Wq simulado", plot_analytical(analytical, "Wq_simulado_seg", "Wq_analitico_seg"), chart_key="analitica_wq")
    with cols[1]:
        render_chart_card("W analítico vs W simulado", plot_analytical(analytical, "W_simulado_seg", "W_analitico_seg"), chart_key="analitica_w")

    cols = [c for c in ["periodo", "lambda_hora", "c", "status_analitico", "erro_percentual_Wq", "erro_percentual_W"] if c in analytical.columns]
    with st.expander("Tabela de erro percentual", expanded=False):
        render_styled_table(
            "Erro percentual analitico vs simulado",
            analytical[cols] if cols else analytical,
            "Comparacao em segundos para Wq e W no caso M/D/1 estavel.",
        )


def render_data_tables(summary, replicas, analytical) -> None:
    with st.expander("Resumo por cenário", expanded=False):
        render_styled_table(
            "Resumo por cenario",
            summary,
            "Resultados consolidados por combinacao de modelo, periodo, lambda e capacidade c.",
            height=460,
        )
    with st.expander("Resultados por réplica", expanded=False):
        render_styled_table(
            "Resultados por replica",
            replicas,
            "Execucoes independentes da simulacao usadas para estimar as metricas.",
            height=460,
        )
    with st.expander("Comparação analítica", expanded=False):
        render_styled_table(
            "Comparacao analitica M/D/1",
            analytical,
            "Validacao do simulador para cenarios com c=1 e regime estavel.",
            height=420,
        )


def render_diagnostics(data: dict[str, pd.DataFrame]) -> None:
    st.markdown('<div class="note-card">Diagnóstico técnico de carga dos arquivos usados no dashboard.</div>', unsafe_allow_html=True)
    render_styled_table(
        "Arquivos carregados",
        diagnostic_table(data),
        "Caminho, disponibilidade, quantidade de linhas e colunas detectadas.",
        height=360,
    )


def main() -> None:
    apply_css()
    data = load_all_data()

    summary_raw = data["resumo_cenarios"]
    replicas_raw = data["simulacao_resultados"]
    analytical_raw = data["comparacao_analitica"]
    empirical = data["resumo_tempos"]
    model_selection = data["modelo_sugerido"]

    summary = summary_raw.copy()
    replicas = replicas_raw.copy()
    analytical = analytical_raw.copy()

    render_header()

    for name, path in FILES.items():
        if not path.exists():
            st.warning(f"Arquivo não encontrado: {path.relative_to(BASE_DIR)}")

    tabs = st.tabs([
        "Visão Geral",
        "Calibração",
        "Estabilidade",
        "Filas",
        "Degradação",
        "Comparação Analítica",
        "Dados",
        "Diagnóstico",
    ])

    with tabs[0]:
        render_overview(summary, empirical, model_selection)
    with tabs[1]:
        render_calibration(empirical, model_selection)
    with tabs[2]:
        render_stability(summary)
    with tabs[3]:
        render_queues(summary)
    with tabs[4]:
        render_degradation(summary)
    with tabs[5]:
        render_analytical(analytical)
    with tabs[6]:
        render_data_tables(summary, replicas, analytical)
    with tabs[7]:
        render_diagnostics(data)


if __name__ == "__main__":
    main()
