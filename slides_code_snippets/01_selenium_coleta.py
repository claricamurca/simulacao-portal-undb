def executar_fluxo(identificador, credenciais, arquivo_metrics):
    inicio_fluxo = time.time()
    tempo_login = tempo_solicitacao = tempo_total = 0.0
    status, erro = "ERRO", ""
    try:
        driver, wait = criar_driver()
        tempo_login, campo_solicitacao = preparar_fluxo_ate_tela_solicitacao(
            driver, wait, credenciais
        )
        inicio_solicitacao = time.time()
        preencher_solicitacao(campo_solicitacao)
        anexar_documento(driver, wait)
        enviar_solicitacao(driver, wait)
        tempo_solicitacao = round(time.time() - inicio_solicitacao, 2)
        status = "SUCESSO"
    except Exception as e:
        erro = formatar_erro_curto(e)
    finally:
        tempo_total = round(time.time() - inicio_fluxo, 2)
        salvar_metricas_fluxo(
            identificador, tempo_login, tempo_solicitacao,
            tempo_total, status, erro
        )
