from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os
import sys
from datetime import datetime

def formatar_erro_curto(e):
    mensagem = str(e).split("Stacktrace:")[0].replace("Message:", "").strip()
    mensagem = " ".join(mensagem.split())

    if mensagem:
        return f"{type(e).__name__}: {mensagem}"
    return type(e).__name__

LOG_DETALHADO = False


def log(usuario, mensagem):
    if LOG_DETALHADO:
        print(f"[{usuario}] {mensagem}")


def log_resumo(usuario, status, tempo_login, tempo_solicitacao, tempo_total, erro=""):
    mensagem = (
        f"[{usuario}] RESUMO | "
        f"status={status} | "
        f"login={tempo_login}s | "
        f"solicitacao={tempo_solicitacao}s | "
        f"total={tempo_total}s"
    )

    if erro:
        mensagem += f" | erro={erro}"

    print(mensagem)


def criar_driver():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 20)
    return driver, wait


def abrir_portal(driver):
    driver.get("https://portal.undb.edu.br/FrameHTML/web/app/edu/PortalEducacional/login/")


def fazer_login(driver, wait, usuario, senha):
    inicio_login = time.time()

    campo_usuario = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//*[@id='User']"))
    )
    campo_usuario.clear()
    campo_usuario.send_keys(usuario)

    campo_senha = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//*[@id='Pass']"))
    )
    campo_senha.clear()
    campo_senha.send_keys(senha)

    botao_acessar = wait.until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[2]/form/div[4]/input"))
    )
    botao_acessar.click()

    time.sleep(9)

    fim_login = time.time()
    tempo_login = round(fim_login - inicio_login, 2)
    log(usuario, f"Tempo login: {tempo_login} s")
    return tempo_login


def acessar_requerimentos(driver, wait, usuario):
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='show-menu']"))
    ).click()

    time.sleep(8)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='EDU_PORTAL_ACADEMICO_SECRETARIA_REQUERIMENTOS']"))
    ).click()

    log(usuario, "Aba Requerimentos acessada")
    time.sleep(9)


def abrir_atividades_complementares(driver, wait, usuario):
    link = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[contains(., 'ATIVIDADES COMPLEMENTARES (GERAL)')]")
        )
    )

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(., 'ATIVIDADES COMPLEMENTARES (GERAL)')]")
        )
    )

    driver.execute_script("arguments[0].click();", link)
    log(usuario, "Atividades Complementares encontrada")
    time.sleep(4)


def obter_campo_solicitacao(wait):
    campo_solicitacao = wait.until(
        EC.presence_of_element_located((By.XPATH, "//textarea"))
    )
    return campo_solicitacao


def preencher_solicitacao(campo_solicitacao):
    campo_solicitacao.send_keys(
        "Olá, por favor desconsiderar esses envios, estou fazendo testes automatizados para a disciplina de Simulação de Softwares. Obrigado!"
    )
    time.sleep(8)


def abrir_modal_anexo(driver, wait, usuario):
    botao_anexo = wait.until(
        EC.presence_of_element_located((By.ID, "buttonAnexo"))
    )

    driver.execute_script("window.scrollBy(0, 250);")
    time.sleep(1)
    driver.execute_script("arguments[0].click();", botao_anexo)
    log(usuario, "Modal de anexo aberto")


def obter_campos_anexo(driver, wait, usuario):
    descricao_anexo = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//div[contains(@class,'modal')]//input[@type='text']")
        )
    )

    campo_arquivo = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'modal')]//input[@type='file']")
        )
    )

    log(usuario, "Campo de arquivo encontrado")

    campos_arquivo = driver.find_elements(By.XPATH, "//input[@type='file']")
    log(usuario, f"Quantidade de inputs file: {len(campos_arquivo)}")

    return descricao_anexo, campo_arquivo


def preencher_anexo(descricao_anexo, campo_arquivo, usuario):
    descricao_anexo.send_keys("Certificado de participação em atividade complementar")
    log(usuario, "Descrição do anexo preenchida")

    campo_arquivo.send_keys(
        r"C:\Users\clari\testes-portal-undb\data\Certificado_xviec_Participação_10-54-43.pdf"
    )
    log(usuario, "Arquivo enviado para o input")

    time.sleep(2)


def adicionar_anexo(driver, wait, usuario):
    botao_adicionar = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(.,'Adicionar ao requerimento')]")
        )
    )

    driver.execute_script("arguments[0].click();", botao_adicionar)
    log(usuario, "Arquivo adicionado ao requerimento")


def enviar_solicitacao(driver, wait, usuario):
    botao_enviar = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(.,'Solicitar')]")
        )
    )

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", botao_enviar)
    driver.execute_script("arguments[0].click();", botao_enviar)

    log(usuario, "Solicitação enviada")


def salvar_metricas_fluxo(
    usuario,
    tempo_login,
    tempo_solicitacao,
    tempo_total,
    status,
    erro,
    arquivo_metrics="results/metrics_fluxo.csv",
    simultaneidade=""
):
    arquivo_existe = os.path.isfile(arquivo_metrics)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(arquivo_metrics, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not arquivo_existe or os.path.getsize(arquivo_metrics) == 0:
            writer.writerow([
                "timestamp",
                "usuario",
                "simultaneidade",
                "tempo_login",
                "tempo_solicitacao",
                "tempo_total",
                "status",
                "erro"
            ])

        writer.writerow([
            timestamp,
            usuario,
            simultaneidade,
            tempo_login,
            tempo_solicitacao,
            tempo_total,
            status,
            erro
        ])


def preparar_fluxo_ate_tela_solicitacao(driver, wait, usuario, senha):
    abrir_portal(driver)
    tempo_login = fazer_login(driver, wait, usuario, senha)
    acessar_requerimentos(driver, wait, usuario)
    abrir_atividades_complementares(driver, wait, usuario)
    campo_solicitacao = obter_campo_solicitacao(wait)
    return tempo_login, campo_solicitacao


def executar_fluxo(usuario, senha, arquivo_metrics="results/metrics_fluxo.csv", simultaneidade=""):
    inicio_fluxo = time.time()

    tempo_login = 0.0
    tempo_solicitacao = 0.0
    tempo_total = 0.0
    status = "ERRO"
    erro = ""

    driver = None

    try:
        driver, wait = criar_driver()

        tempo_login, campo_solicitacao = preparar_fluxo_ate_tela_solicitacao(
            driver, wait, usuario, senha
        )

        inicio_solicitacao = time.time()

        preencher_solicitacao(campo_solicitacao)
        abrir_modal_anexo(driver, wait, usuario)

        descricao_anexo, campo_arquivo = obter_campos_anexo(driver, wait, usuario)
        preencher_anexo(descricao_anexo, campo_arquivo, usuario)
        adicionar_anexo(driver, wait, usuario)
        enviar_solicitacao(driver, wait, usuario)

        fim_solicitacao = time.time()
        tempo_solicitacao = round(fim_solicitacao - inicio_solicitacao, 2)
        log(usuario, f"Tempo solicitação: {tempo_solicitacao} s")

        status = "SUCESSO"

    except Exception as e:
        erro = formatar_erro_curto(e)
        log(usuario, "Erro durante a execução do fluxo")
        log(usuario, erro)

    finally:
        fim_fluxo = time.time()
        tempo_total = round(fim_fluxo - inicio_fluxo, 2)

        log_resumo(usuario, status, tempo_login, tempo_solicitacao, tempo_total, erro)

        salvar_metricas_fluxo(
            usuario=usuario,
            tempo_login=tempo_login,
            tempo_solicitacao=tempo_solicitacao,
            tempo_total=tempo_total,
            status=status,
            erro=erro,
            arquivo_metrics=arquivo_metrics,
            simultaneidade=simultaneidade
        )

        if driver is not None:
            driver.quit()

if __name__ == "__main__":
    import sys
    import csv

    if len(sys.argv) > 1 and sys.argv[1] == "todos":

        with open("data/usuarios.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                executar_fluxo(row["usuario"], row["senha"])

    else:
        executar_fluxo("002-024820", "camurca1532")