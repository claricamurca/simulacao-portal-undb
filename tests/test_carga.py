import csv
import threading
import time
from test_fluxo_requerimento import executar_fluxo

# número máximo de navegadores rodando ao mesmo tempo
MAX_SESSOES_SIMULTANEAS = 30

# número de execuções por usuário
SESSOES_POR_USUARIO = 7

semaforo = threading.Semaphore(MAX_SESSOES_SIMULTANEAS)

usuarios = []

with open("data/usuarios.csv", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        usuarios.append(row)

def executar_com_controle(usuario, senha):
     
     with semaforo:
        print(f"[{usuario}] Sessão iniciada")
        executar_fluxo(
            usuario,
            senha,
            "results/metrics_carga.csv",
            MAX_SESSOES_SIMULTANEAS
        )
        print(f"[{usuario}] Sessão finalizada")

threads = []

inicio_carga = time.time()

for usuario in usuarios:

    for i in range(SESSOES_POR_USUARIO):

        t = threading.Thread(
            target=executar_com_controle,
            args=(usuario["usuario"], usuario["senha"])
        )

        threads.append(t)
        t.start()

        time.sleep(1)  # evita abrir todos os navegadores exatamente ao mesmo tempo

for t in threads:
    t.join()

fim_carga = time.time()

tempo_total = round(fim_carga - inicio_carga, 2)

print("\n=== RESUMO DO TESTE DE CARGA ===")
print(f"Usuários no CSV: {len(usuarios)}")
print(f"Sessões por usuário: {SESSOES_POR_USUARIO}")
print(f"Total de execuções: {len(threads)}")
print(f"Máximo simultâneo: {MAX_SESSOES_SIMULTANEAS}")
print(f"Tempo total da carga: {tempo_total} s")