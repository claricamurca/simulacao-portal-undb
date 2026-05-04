import csv
import os
from statistics import mean


def ler_csv(caminho):
    if not os.path.exists(caminho):
        return []

    with open(caminho, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def analisar_fluxo():

    dados = ler_csv("results/metrics_fluxo.csv")

    if not dados:
        print("\nNenhum dado de fluxo encontrado.")
        return

    tempos_login = []
    tempos_solicitacao = []
    tempos_total = []

    sucesso = 0
    erro = 0

    for row in dados:

        try:
            tempos_login.append(float(row["tempo_login"]))
            tempos_solicitacao.append(float(row["tempo_solicitacao"]))
            tempos_total.append(float(row["tempo_total"]))
        except:
            pass

        if row["status"] == "SUCESSO":
            sucesso += 1
        else:
            erro += 1

    print("\n===== TESTE DE FLUXO =====")

    print(f"Execuções: {len(dados)}")

    if tempos_login:
        print(f"Tempo médio login: {round(mean(tempos_login),2)} s")

    if tempos_solicitacao:
        print(f"Tempo médio solicitação: {round(mean(tempos_solicitacao),2)} s")

    if tempos_total:
        print(f"Tempo médio total: {round(mean(tempos_total),2)} s")

    taxa_sucesso = (sucesso / len(dados)) * 100

    print(f"Taxa de sucesso: {round(taxa_sucesso,2)} %")
    print(f"Erros: {erro}")


def analisar_carga():

    dados = ler_csv("results/metrics_carga.csv")

    if not dados:
        print("\nNenhum dado de carga encontrado.")
        return

    tempos_total = []
    simultaneidade = set()

    sucesso = 0
    erro = 0

    for row in dados:

        try:
            tempos_total.append(float(row["tempo_total"]))
        except:
            pass

        if row.get("simultaneidade"):
            simultaneidade.add(row["simultaneidade"])

        if row["status"] == "SUCESSO":
            sucesso += 1
        else:
            erro += 1

    print("\n===== TESTE DE CARGA =====")

    print(f"Execuções: {len(dados)}")

    if tempos_total:
        print(f"Tempo médio total: {round(mean(tempos_total),2)} s")

    if simultaneidade:
        print(f"Simultaneidade usada: {', '.join(simultaneidade)}")

    taxa_sucesso = (sucesso / len(dados)) * 100

    print(f"Taxa de sucesso: {round(taxa_sucesso,2)} %")
    print(f"Erros: {erro}")


def analisar_erros():

    dados = ler_csv("results/metrics_erros.csv")

    if not dados:
        print("\nNenhum dado de teste de erro encontrado.")
        return

    # detectar colunas existentes
    colunas = dados[0].keys()

    if "status" not in colunas:
        print("\nColuna 'status' não encontrada no CSV de erros.")
        print("Colunas disponíveis:", list(colunas))
        return

    if "cenario" not in colunas:
        print("\nColuna 'cenario' não encontrada no CSV de erros.")
        print("Colunas disponíveis:", list(colunas))
        return

    contagem_status = {}
    contagem_cenarios = {}

    for row in dados:

        status = row.get("status", "desconhecido")
        cenario = row.get("cenario", "desconhecido")

        contagem_status[status] = contagem_status.get(status, 0) + 1
        contagem_cenarios[cenario] = contagem_cenarios.get(cenario, 0) + 1

    print("\n===== TESTE DE ERROS =====")

    print("\nStatus:")

    for status, qtd in contagem_status.items():
        print(f"{status}: {qtd}")

    print("\nCenários executados:")

    for cenario, qtd in contagem_cenarios.items():
        print(f"{cenario}: {qtd}")


def main():

    print("\n==============================")
    print("ANÁLISE DOS TESTES AUTOMATIZADOS")
    print("==============================")

    analisar_fluxo()
    analisar_carga()
    analisar_erros()

    print("\nAnálise concluída.\n")


if __name__ == "__main__":
    main()