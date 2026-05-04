import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# ======================================================
# CONFIG GERAL
# ======================================================

st.set_page_config(
    page_title="Dashboard Analítico de Testes",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = BASE_DIR / "results"

ARQ_FLUXO = RESULTS_DIR / "metrics_fluxo.csv"
ARQ_CARGA = RESULTS_DIR / "metrics_carga.csv"
ARQ_ERROS = RESULTS_DIR / "metrics_erros.csv"

# Paleta visual
COR_FLUXO = "#4DA3FF"
COR_CARGA = "#FF8C42"
COR_SUCESSO = "#2ECC71"
COR_ERRO = "#E74C3C"
COR_ACEITO = "#F1C40F"
COR_OBSERVAR = "#9B59B6"
COR_NEUTRA = "#95A5A6"
FUNDO = "#0E1117"

st.markdown(
    """
    <style>
    .stMetric {
        background-color: #161B22;
        padding: 14px;
        border-radius: 14px;
        border: 1px solid #2A2F3A;
    }
    .bloco-conclusao {
        background-color: #161B22;
        padding: 16px;
        border-radius: 14px;
        border-left: 5px solid #4DA3FF;
        margin-bottom: 10px;
    }
    .bloco-alerta {
        background-color: #161B22;
        padding: 16px;
        border-radius: 14px;
        border-left: 5px solid #FF8C42;
        margin-bottom: 10px;
    }
    .bloco-erro {
        background-color: #161B22;
        padding: 16px;
        border-radius: 14px;
        border-left: 5px solid #E74C3C;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ======================================================
# HELPERS
# ======================================================

def carregar_csv_robusto(caminho):
    if not caminho.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(caminho)
    except Exception:
        try:
            df = pd.read_csv(caminho, engine="python", on_bad_lines="skip")
        except Exception:
            return pd.DataFrame()

    df.columns = [str(c).strip() for c in df.columns]

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()

    return df


def converter_numero(df, colunas):
    for col in colunas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def taxa_sucesso(df):
    if df.empty or "status" not in df.columns:
        return 0
    return round(((df["status"].str.upper() == "SUCESSO").sum() / len(df)) * 100, 2)


def estatistica(serie):
    serie = pd.to_numeric(serie, errors="coerce").dropna()
    if serie.empty:
        return {"media": 0, "mediana": 0, "max": 0, "min": 0, "p95": 0}
    return {
        "media": round(serie.mean(), 2),
        "mediana": round(serie.median(), 2),
        "max": round(serie.max(), 2),
        "min": round(serie.min(), 2),
        "p95": round(serie.quantile(0.95), 2),
    }


def plot_config(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=FUNDO,
        plot_bgcolor=FUNDO,
        font=dict(size=14),
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title_text=""
    )
    return fig


def card_conclusao(texto, tipo="normal"):
    classe = "bloco-conclusao"
    if tipo == "alerta":
        classe = "bloco-alerta"
    elif tipo == "erro":
        classe = "bloco-erro"

    st.markdown(f'<div class="{classe}">{texto}</div>', unsafe_allow_html=True)


# ======================================================
# DASHBOARD DINÂMICO
# ======================================================

st.title("Dashboard Analítico de Testes Automatizados")
st.caption("Atualização automática a cada 5 segundos · Visualização executiva para análise de desempenho, carga e robustez")


@st.fragment(run_every="5s")
def atualizar_dashboard():

    df_fluxo = carregar_csv_robusto(ARQ_FLUXO)
    df_carga = carregar_csv_robusto(ARQ_CARGA)
    df_erros = carregar_csv_robusto(ARQ_ERROS)

    df_fluxo = converter_numero(df_fluxo, ["tempo_login", "tempo_solicitacao", "tempo_total"])
    df_carga = converter_numero(df_carga, ["tempo_login", "tempo_solicitacao", "tempo_total", "simultaneidade"])
    df_erros = converter_numero(df_erros, ["tempo_login", "tempo_cenario", "tempo_total"])

    tab1, tab2, tab3, tab4 = st.tabs(["Visão Geral", "Fluxo", "Carga", "Erros"])

    # ==================================================
    # VISÃO GERAL
    # ==================================================
    with tab1:
        col1, col2, col3, col4 = st.columns(4)

        exec_fluxo = len(df_fluxo)
        exec_carga = len(df_carga)
        exec_erros = len(df_erros)
        sucesso_carga = taxa_sucesso(df_carga)

        col1.metric("Execuções de Fluxo", exec_fluxo)
        col2.metric("Execuções sob Carga", exec_carga)
        col3.metric("Cenários de Erro", exec_erros)
        col4.metric("Taxa de Sucesso em Carga", f"{sucesso_carga}%")

        st.markdown("### Comparação executiva")

        if not df_fluxo.empty and not df_carga.empty:
            media_fluxo = estatistica(df_fluxo["tempo_total"])["media"]
            media_carga = estatistica(df_carga["tempo_total"])["media"]
            sucesso_fluxo = taxa_sucesso(df_fluxo)
            sucesso_carga = taxa_sucesso(df_carga)
            degradacao = round(media_carga / media_fluxo, 2) if media_fluxo > 0 else 0

            comp_df = pd.DataFrame({
                "Tipo de Teste": ["Fluxo", "Carga"],
                "Tempo Médio Total (s)": [media_fluxo, media_carga],
                "Taxa de Sucesso (%)": [sucesso_fluxo, sucesso_carga]
            })

            cA, cB = st.columns(2)

            with cA:
                fig = px.bar(
                    comp_df,
                    x="Tipo de Teste",
                    y="Tempo Médio Total (s)",
                    color="Tipo de Teste",
                    color_discrete_map={"Fluxo": COR_FLUXO, "Carga": COR_CARGA},
                    text="Tempo Médio Total (s)",
                    title="Comparação de Tempo Médio: Fluxo x Carga"
                )
                fig.update_traces(textposition="outside")
                st.plotly_chart(plot_config(fig), use_container_width=True)

            with cB:
                fig2 = px.bar(
                    comp_df,
                    x="Tipo de Teste",
                    y="Taxa de Sucesso (%)",
                    color="Tipo de Teste",
                    color_discrete_map={"Fluxo": COR_FLUXO, "Carga": COR_CARGA},
                    text="Taxa de Sucesso (%)",
                    title="Comparação da Taxa de Sucesso"
                )
                fig2.update_traces(textposition="outside")
                fig2.update_yaxes(range=[0, 100])
                st.plotly_chart(plot_config(fig2), use_container_width=True)

            st.markdown("### Conclusões automáticas")
            card_conclusao(
                f"No fluxo normal, o sistema apresentou tempo médio total de <b>{media_fluxo}s</b>, "
                f"enquanto sob carga esse valor subiu para <b>{media_carga}s</b>.",
                "normal"
            )
            card_conclusao(
                f"A degradação observada foi de aproximadamente <b>{degradacao}x</b> no tempo médio total, "
                f"indicando impacto relevante da concorrência no desempenho.",
                "alerta"
            )

            if not df_erros.empty and "status" in df_erros.columns:
                erros_tratados = (df_erros["status"] == "ERRO_TRATADO").sum()
                erros_aceitos = (df_erros["status"] == "ACEITO_SEM_VALIDACAO").sum()
                observar = (df_erros["status"] == "OBSERVAR_COMPORTAMENTO").sum()

                card_conclusao(
                    f"Foram identificados <b>{erros_tratados}</b> cenários com tratamento explícito, "
                    f"<b>{erros_aceitos}</b> aceitos sem validação visível e "
                    f"<b>{observar}</b> classificados como observação comportamental.",
                    "erro"
                )

    # ==================================================
    # FLUXO
    # ==================================================
    with tab2:
        if df_fluxo.empty:
            st.warning("Sem dados de fluxo.")
        else:
            e_login = estatistica(df_fluxo["tempo_login"])
            e_sol = estatistica(df_fluxo["tempo_solicitacao"])
            e_total = estatistica(df_fluxo["tempo_total"])

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Média Login", f"{e_login['media']} s")
            c2.metric("Média Solicitação", f"{e_sol['media']} s")
            c3.metric("Média Total", f"{e_total['media']} s")
            c4.metric("P95 Total", f"{e_total['p95']} s")
            c5.metric("Taxa de Sucesso", f"{taxa_sucesso(df_fluxo)}%")

            st.markdown("### Distribuição e estabilidade do fluxo")

            cA, cB = st.columns(2)

            with cA:
                fig = px.histogram(
                    df_fluxo,
                    x="tempo_total",
                    nbins=8,
                    title="Distribuição do Tempo Total",
                    color_discrete_sequence=[COR_FLUXO]
                )
                st.plotly_chart(plot_config(fig), use_container_width=True)

            with cB:
                fluxo_exec = df_fluxo.reset_index(drop=True).reset_index(names="execucao")
                fluxo_exec["execucao"] = fluxo_exec["execucao"] + 1

                fig2 = px.line(
                    fluxo_exec,
                    x="execucao",
                    y="tempo_total",
                    markers=True,
                    title="Tempo Total por Execução",
                    color_discrete_sequence=[COR_FLUXO]
                )
                fig2.update_traces(line=dict(width=4))
                st.plotly_chart(plot_config(fig2), use_container_width=True)

            etapas_df = pd.DataFrame({
                "Etapa": ["Login", "Solicitação", "Total"],
                "Tempo Médio (s)": [e_login["media"], e_sol["media"], e_total["media"]]
            })

            fig3 = px.bar(
                etapas_df,
                x="Etapa",
                y="Tempo Médio (s)",
                text="Tempo Médio (s)",
                color="Etapa",
                color_discrete_map={
                    "Login": "#5DADE2",
                    "Solicitação": "#48C9B0",
                    "Total": COR_FLUXO
                },
                title="Tempo Médio por Etapa"
            )
            fig3.update_traces(textposition="outside")
            st.plotly_chart(plot_config(fig3), use_container_width=True)

            if "usuario" in df_fluxo.columns:
                por_usuario = df_fluxo.groupby("usuario", as_index=False)["tempo_total"].mean()
                fig4 = px.bar(
                    por_usuario,
                    x="usuario",
                    y="tempo_total",
                    text="tempo_total",
                    color_discrete_sequence=[COR_FLUXO],
                    title="Tempo Médio Total por Usuário"
                )
                fig4.update_traces(textposition="outside")
                st.plotly_chart(plot_config(fig4), use_container_width=True)

            card_conclusao(
                f"O fluxo individual apresenta média total de <b>{e_total['media']}s</b> e P95 de <b>{e_total['p95']}s</b>, "
                f"o que indica a existência de execuções mais lentas acima do padrão médio."
            )

    # ==================================================
    # CARGA
    # ==================================================
    with tab3:
        if df_carga.empty:
            st.warning("Sem dados de carga.")
        else:
            e_total = estatistica(df_carga["tempo_total"])

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Média Total", f"{e_total['media']} s")
            c2.metric("P95 Total", f"{e_total['p95']} s")
            c3.metric("Máximo", f"{e_total['max']} s")
            c4.metric("Taxa de Sucesso", f"{taxa_sucesso(df_carga)}%")

            st.markdown("### Distribuição e degradação sob concorrência")

            cA, cB = st.columns(2)

            with cA:
                fig = px.box(
                    df_carga,
                    x="tempo_total",
                    points="all",
                    title="Distribuição do Tempo sob Carga",
                    color_discrete_sequence=[COR_CARGA]
                )
                st.plotly_chart(plot_config(fig), use_container_width=True)

            with cB:
                if "simultaneidade" in df_carga.columns:
                    fig2 = px.scatter(
                        df_carga,
                        x="simultaneidade",
                        y="tempo_total",
                        color="status" if "status" in df_carga.columns else None,
                        color_discrete_map={
                            "SUCESSO": COR_SUCESSO,
                            "ERRO": COR_ERRO
                        },
                        size_max=12,
                        title="Relação entre Simultaneidade e Tempo Total"
                    )
                    st.plotly_chart(plot_config(fig2), use_container_width=True)

            if "simultaneidade" in df_carga.columns:
                degradacao = (
                    df_carga.groupby("simultaneidade", as_index=False)["tempo_total"]
                    .mean()
                    .sort_values("simultaneidade")
                )

                fig3 = px.line(
                    degradacao,
                    x="simultaneidade",
                    y="tempo_total",
                    markers=True,
                    title="Degradação do Sistema conforme a Simultaneidade",
                    color_discrete_sequence=[COR_CARGA]
                )
                fig3.update_traces(line=dict(width=5))
                st.plotly_chart(plot_config(fig3), use_container_width=True)

                if not df_fluxo.empty:
                    media_fluxo = df_fluxo["tempo_total"].mean()
                    degradacao["degradacao_x"] = degradacao["tempo_total"] / media_fluxo

                    fig4 = px.bar(
                        degradacao,
                        x="simultaneidade",
                        y="degradacao_x",
                        text="degradacao_x",
                        color_discrete_sequence=["#FF6B6B"],
                        title="Fator de Degradação em Relação ao Fluxo Normal"
                    )
                    fig4.update_traces(texttemplate="%{text:.2f}x", textposition="outside")
                    st.plotly_chart(plot_config(fig4), use_container_width=True)

            card_conclusao(
                "Os gráficos de carga mostram visualmente a elevação do tempo total à medida que a simultaneidade cresce, "
                "evidenciando degradação progressiva do desempenho.",
                "alerta"
            )

    # ==================================================
    # ERROS
    # ==================================================
    with tab4:
        if df_erros.empty:
            st.warning("Sem dados de erros.")
        else:
            status_counts = df_erros["status"].value_counts().reset_index()
            status_counts.columns = ["status", "quantidade"]

            cenario_counts = df_erros["cenario"].value_counts().reset_index()
            cenario_counts.columns = ["cenario", "quantidade"]

            fig1 = px.bar(
                status_counts,
                x="status",
                y="quantidade",
                text="quantidade",
                color="status",
                color_discrete_map={
                    "ERRO_TRATADO": COR_SUCESSO,
                    "ACEITO_SEM_VALIDACAO": COR_ACEITO,
                    "OBSERVAR_COMPORTAMENTO": COR_OBSERVAR,
                    "ERRO_AUTOMACAO": COR_ERRO
                },
                title="Classificação dos Cenários de Erro"
            )
            fig1.update_traces(textposition="outside")
            st.plotly_chart(plot_config(fig1), use_container_width=True)

            fig2 = px.bar(
                cenario_counts,
                x="cenario",
                y="quantidade",
                text="quantidade",
                color_discrete_sequence=[COR_FLUXO],
                title="Execução por Cenário"
            )
            fig2.update_traces(textposition="outside")
            st.plotly_chart(plot_config(fig2), use_container_width=True)

            # Heatmap de falhas
            heatmap_data = (
                df_erros.groupby(["cenario", "status"])
                .size()
                .reset_index(name="quantidade")
            )

            fig3 = px.density_heatmap(
                heatmap_data,
                x="status",
                y="cenario",
                z="quantidade",
                color_continuous_scale="RdYlGn_r",
                title="Heatmap de Falhas por Cenário e Status"
            )
            st.plotly_chart(plot_config(fig3), use_container_width=True)

            if "mensagem_validacao" in df_erros.columns:
                st.markdown("### Mensagens de validação observadas")
                st.dataframe(
                    df_erros[["cenario", "status", "campo_validado", "mensagem_validacao"]],
                    use_container_width=True
                )

            card_conclusao(
                "A classificação dos testes de erro permite identificar quais cenários foram tratados corretamente, "
                "quais foram aceitos sem validação visível e quais exigem observação adicional.",
                "erro"
            )


atualizar_dashboard()