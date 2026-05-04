import csv
import os

arquivo = "results/metrics.csv"

def salvar_metricas(usuario, tempo_login, tempo_req, tempo_total, status):

    arquivo_existe = os.path.isfile(arquivo)

    with open(arquivo, "a", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        if not arquivo_existe:
            writer.writerow(["usuario","tempo_login","tempo_requerimento","tempo_total","status"])

        writer.writerow([usuario, tempo_login, tempo_req, tempo_total, status])