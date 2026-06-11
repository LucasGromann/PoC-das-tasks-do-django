from django.tasks import task


@task(queue_name="default", priority=0)
def enviar_email_boas_vindas(user_id: int):
    print(f"Enviando e-mail para o usuário {user_id}...")
    return f"E-mail enviado para user_id={user_id}"


@task(queue_name="default")
def gerar_relatorio_mensal(mes: int, ano: int):
    print(f"Gerando relatório {mes}/{ano}...")
    return {"status": "ok", "mes": mes, "ano": ano}