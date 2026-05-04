from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import sys
import csv
import os
import time

from test_fluxo_requerimento import (
    criar_driver,
    preparar_fluxo_ate_tela_solicitacao,
    abrir_modal_anexo,
    obter_campos_anexo
)


LOG_DETALHADO = False


def log(usuario, mensagem):
    if LOG_DETALHADO:
        print(f"[{usuario}] {mensagem}")


def log_resumo_erro(usuario, cenario, status, tempo_login, tempo_cenario, tempo_total, erro=""):
    mensagem = (
        f"[{usuario}] RESUMO_ERRO | "
        f"cenario={cenario} | "
        f"status={status} | "
        f"login={tempo_login}s | "
        f"cenario={tempo_cenario}s | "
        f"total={tempo_total}s"
    )

    if erro:
        mensagem += f" | erro={erro}"

    print(mensagem)


def salvar_metricas_erro(
    usuario,
    cenario,
    tempo_login,
    tempo_cenario,
    tempo_total,
    status,
    campo_validado,
    mensagem_validacao,
    erro,
    arquivo_metrics="results/metrics_erros.csv"
):
    arquivo_existe = os.path.isfile(arquivo_metrics)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(arquivo_metrics, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not arquivo_existe or os.path.getsize(arquivo_metrics) == 0:
            writer.writerow([
                "timestamp",
                "usuario",
                "cenario",
                "tempo_login",
                "tempo_cenario",
                "tempo_total",
                "status",
                "campo_validado",
                "mensagem_validacao",
                "erro"
            ])

        writer.writerow([
            timestamp,
            usuario,
            cenario,
            tempo_login,
            tempo_cenario,
            tempo_total,
            status,
            campo_validado,
            mensagem_validacao,
            erro
        ])


def buscar_mensagem_visivel(driver):

    palavras_chave = [
        "arquivo anexado com sucesso",
        "erro",
        "obrigatório",
        "obrigatoria",
        "inválido",
        "invalido",
        "preencha"
    ]

    elementos = driver.find_elements(By.XPATH, "//*[normalize-space(text())!='']")

    for el in elementos:
        texto = el.text.strip()

        if not texto:
            continue

        linhas = [l.strip() for l in texto.splitlines() if l.strip()]

        for linha in linhas:
            for palavra in palavras_chave:
                if palavra in linha.lower():
                    return linha

    return ""


def clicar_botao_adicionar(driver, wait):
    botao = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(.,'Adicionar ao requerimento')]")
        )
    )
    driver.execute_script("arguments[0].click();", botao)


def clicar_botao_solicitar(driver, wait):
    botao = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(.,'Solicitar')]")
        )
    )

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", botao)
    driver.execute_script("arguments[0].click();", botao)


def executar_teste_erro(usuario, senha, cenario, arquivo_metrics="results/metrics_erros.csv"):

    inicio_fluxo = time.time()

    tempo_login = 0
    tempo_cenario = 0
    tempo_total = 0

    status = "ERRO_AUTOMACAO"
    campo_validado = ""
    mensagem_validacao = ""
    erro = ""

    driver = None

    try:

        driver, wait = criar_driver()

        tempo_login, campo_solicitacao = preparar_fluxo_ate_tela_solicitacao(
            driver, wait, usuario, senha
        )

        inicio_cenario = time.time()

        # -------------------------
        # sem descrição principal
        # -------------------------

        if cenario == "sem_descricao_principal":

            campo_validado = "descricao_principal"

            abrir_modal_anexo(driver, wait, usuario)
            descricao_anexo, campo_arquivo = obter_campos_anexo(driver, wait, usuario)

            descricao_anexo.send_keys("Certificado")
            campo_arquivo.send_keys(
                r"C:\Users\clari\testes-portal-undb\data\Certificado_xviec_Participação_10-54-43.pdf"
            )

            clicar_botao_adicionar(driver, wait)
            clicar_botao_solicitar(driver, wait)

            time.sleep(2)

            mensagem = buscar_mensagem_visivel(driver)

            if mensagem:
                status = "ERRO_TRATADO"
                mensagem_validacao = mensagem
            else:
                status = "ACEITO_SEM_VALIDACAO"
                mensagem_validacao = "Descrição principal vazia foi aceita."

        # -------------------------
        # sem descrição anexo
        # -------------------------

        elif cenario == "sem_descricao_anexo":

            campo_validado = "descricao_anexo"

            campo_solicitacao.send_keys("Teste automatizado")

            abrir_modal_anexo(driver, wait, usuario)
            descricao_anexo, campo_arquivo = obter_campos_anexo(driver, wait, usuario)

            campo_arquivo.send_keys(
                r"C:\Users\clari\testes-portal-undb\data\Certificado_xviec_Participação_10-54-43.pdf"
            )

            clicar_botao_adicionar(driver, wait)

            time.sleep(2)

            mensagem = buscar_mensagem_visivel(driver)

            if mensagem:
                status = "ERRO_TRATADO"
                mensagem_validacao = mensagem
            else:
                status = "ACEITO_SEM_VALIDACAO"
                mensagem_validacao = "Descrição do anexo vazia foi aceita."

        # -------------------------
        # sem arquivo
        # -------------------------

        elif cenario == "sem_arquivo":

            campo_validado = "arquivo_anexo"

            campo_solicitacao.send_keys("Teste automatizado")

            abrir_modal_anexo(driver, wait, usuario)
            descricao_anexo, campo_arquivo = obter_campos_anexo(driver, wait, usuario)

            descricao_anexo.send_keys("Certificado")

            clicar_botao_adicionar(driver, wait)

            time.sleep(2)

            mensagem = buscar_mensagem_visivel(driver)

            if mensagem:
                status = "ERRO_TRATADO"
                mensagem_validacao = mensagem
            else:
                status = "ACEITO_SEM_VALIDACAO"
                mensagem_validacao = "Arquivo não anexado foi aceito."

        # -------------------------
        # arquivo inválido
        # -------------------------

        elif cenario == "arquivo_tipo_invalido":

            campo_validado = "tipo_arquivo"

            campo_solicitacao.send_keys("Teste arquivo inválido")

            abrir_modal_anexo(driver, wait, usuario)
            descricao_anexo, campo_arquivo = obter_campos_anexo(driver, wait, usuario)

            descricao_anexo.send_keys("Teste arquivo inválido")

            campo_arquivo.send_keys(
                r"C:\Users\clari\testes-portal-undb\data\Teste de Simulação de Software.txt"
            )

            clicar_botao_adicionar(driver, wait)

            time.sleep(2)

            mensagem = buscar_mensagem_visivel(driver)

            if "arquivo anexado com sucesso" in mensagem.lower():
                status = "ACEITO_SEM_VALIDACAO"
                mensagem_validacao = "Arquivo anexado com sucesso."
            else:
                status = "ERRO_TRATADO"
                mensagem_validacao = mensagem

        # -------------------------
        # concorrência
        # -------------------------

        elif cenario == "solicitacao_concorrente":

            campo_validado = "concorrencia"

            campo_solicitacao.send_keys("Teste concorrência")

            abrir_modal_anexo(driver, wait, usuario)
            descricao_anexo, campo_arquivo = obter_campos_anexo(driver, wait, usuario)

            descricao_anexo.send_keys("Certificado")

            campo_arquivo.send_keys(
                r"C:\Users\clari\testes-portal-undb\data\Certificado_xviec_Participação_10-54-43.pdf"
            )

            clicar_botao_adicionar(driver, wait)

            botao = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(.,'Solicitar')]")
                )
            )

            driver.execute_script("arguments[0].click();", botao)
            driver.execute_script("arguments[0].click();", botao)

            status = "OBSERVAR_COMPORTAMENTO"
            mensagem_validacao = "Dois cliques consecutivos no botão Solicitar."

        # -------------------------
        # descrição curta
        # -------------------------

        elif cenario == "descricao_principal_muito_curta":

            campo_validado = "descricao_principal"

            campo_solicitacao.send_keys("x")

            abrir_modal_anexo(driver, wait, usuario)
            descricao_anexo, campo_arquivo = obter_campos_anexo(driver, wait, usuario)

            descricao_anexo.send_keys("Certificado")

            campo_arquivo.send_keys(
                r"C:\Users\clari\testes-portal-undb\data\Certificado_xviec_Participação_10-54-43.pdf"
            )

            clicar_botao_adicionar(driver, wait)
            clicar_botao_solicitar(driver, wait)

            mensagem = buscar_mensagem_visivel(driver)

            if mensagem:
                status = "ERRO_TRATADO"
                mensagem_validacao = mensagem
            else:
                status = "ACEITO_SEM_VALIDACAO"
                mensagem_validacao = "Descrição principal muito curta aceita."

        # -------------------------
        # descrição longa
        # -------------------------

        elif cenario == "descricao_principal_muito_longa":

            campo_validado = "descricao_principal_tamanho"

            campo_solicitacao.send_keys("A" * 5000)

            abrir_modal_anexo(driver, wait, usuario)
            descricao_anexo, campo_arquivo = obter_campos_anexo(driver, wait, usuario)

            descricao_anexo.send_keys("Certificado")

            campo_arquivo.send_keys(
                r"C:\Users\clari\testes-portal-undb\data\Certificado_xviec_Participação_10-54-43.pdf"
            )

            clicar_botao_adicionar(driver, wait)
            clicar_botao_solicitar(driver, wait)

            mensagem = buscar_mensagem_visivel(driver)

            if mensagem:
                status = "ERRO_TRATADO"
                mensagem_validacao = mensagem
            else:
                status = "ACEITO_SEM_VALIDACAO"
                mensagem_validacao = "Descrição muito longa aceita."

        fim_cenario = time.time()
        tempo_cenario = round(fim_cenario - inicio_cenario, 2)

    except Exception as e:
        erro = f"{type(e).__name__}: {str(e)}"

    finally:

        fim_fluxo = time.time()
        tempo_total = round(fim_fluxo - inicio_fluxo, 2)

        salvar_metricas_erro(
            usuario,
            cenario,
            tempo_login,
            tempo_cenario,
            tempo_total,
            status,
            campo_validado,
            mensagem_validacao,
            erro
        )

        log_resumo_erro(usuario, cenario, status, tempo_login, tempo_cenario, tempo_total, erro)

        if driver:
            driver.quit()


if __name__ == "__main__":

    usuarios = []

    with open("data/usuarios.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            usuarios.append(row)

    cenarios_disponiveis = [
        "sem_descricao_principal",
        "sem_descricao_anexo",
        "sem_arquivo",
        "arquivo_tipo_invalido",
        "solicitacao_concorrente",
        "descricao_principal_muito_curta",
        "descricao_principal_muito_longa"
    ]

    if len(sys.argv) > 1:
        cenario_escolhido = sys.argv[1]

        if cenario_escolhido not in cenarios_disponiveis:
            print("\nCenário inválido.")
            print("Cenários disponíveis:")
            for c in cenarios_disponiveis:
                print("-", c)
            sys.exit()

        cenarios = [cenario_escolhido]
    else:
        cenarios = cenarios_disponiveis

    testar_todos = len(sys.argv) > 2 and sys.argv[2].lower() == "todos"

    if testar_todos:
        for usuario in usuarios:
            for cenario in cenarios:
                executar_teste_erro(usuario["usuario"], usuario["senha"], cenario)
    else:
        usuario = usuarios[0]
        for cenario in cenarios:
            executar_teste_erro(usuario["usuario"], usuario["senha"], cenario)