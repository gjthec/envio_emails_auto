import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from datetime import datetime

# Configurações do e-mail
email_remetente = "contatomaaple@gmail.com"
senha = "fmuw fhov zbjh sgym"  # Senha de app
assunto_email = "Aviso de Cobrança Pendente"

# Configurações da API do Asaas
ASAAS_API = 'https://sandbox.asaas.com/api/v3/payments'
ASAAS_CUSTOMERS_API = 'https://sandbox.asaas.com/api/v3/customers'
ASAAS_TOKEN = '$aact_YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5MzdjNWZmNDQ6OjAwMDAwMDAwMDAwMDAwODgwMzY6OiRhYWNoX2ExMGM1ZjQyLTVmMTctNDNlOS04NzU5LTgxM2Q5YzM5YzIxMg=='  # Substitua pela sua chave
destinatario_teste = "teslaeletronico@gmail.com"

def send_email(destinatario, nome, valor, vencimento, link_pagamento):
    """
    Envia um e-mail para o cliente com os detalhes da cobrança.
    """
    try:
        mensagem_corpo = (
            f"Olá, {nome}!\n\n"
            f"Este é um aviso de cobrança pendente.\n\n"
            f"Valor: R${valor}\n"
            f"Vencimento: {vencimento}\n\n"
            f"Para realizar o pagamento, acesse o link abaixo:\n{link_pagamento}\n\n"
            f"Por favor, regularize o pagamento antes do vencimento. Obrigado! 😊"
        )

        mensagem = MIMEMultipart()
        mensagem["From"] = email_remetente
        mensagem["To"] = destinatario
        mensagem["Subject"] = assunto_email
        mensagem.attach(MIMEText(mensagem_corpo, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login(email_remetente, senha)
            servidor.sendmail(email_remetente, destinatario, mensagem.as_string())

        print(f"[SUCCESS] E-mail enviado para {nome} ({destinatario}).")
    except Exception as e:
        print(f"[ERROR] Erro ao enviar e-mail para {nome} ({destinatario}): {e}")


def fetch_boletos():
    """
    Busca boletos pendentes no Asaas e lista os e-mails dos clientes.
    """
    try:
        print("Buscando boletos...")
        response = requests.get(ASAAS_API, headers={
            'access_token': ASAAS_TOKEN,
            'Content-Type': 'application/json',
            'User-Agent': 'teste_gjtechsolucions'
        })

        response.raise_for_status()
        boletos = response.json().get('data', [])

        if not boletos:
            print("Nenhum boleto pendente encontrado.")
            return []

        print(f"Encontrados {len(boletos)} boletos pendentes.")
        for boleto in boletos:
            customer_id = boleto.get("customer")
            if not customer_id:
                print("[INFO] Cliente não encontrado para este boleto.")
                continue

            # Busca os dados do cliente
            customer_response = requests.get(f"{ASAAS_CUSTOMERS_API}/{customer_id}", headers={
                'access_token': ASAAS_TOKEN,
                'Content-Type': 'application/json',
                'User-Agent': 'teste_gjtechsolucions'
            })
            customer_response.raise_for_status()
            customer = customer_response.json()

            # Dados do cliente e boleto
            nome = customer.get("name", "N/A")
            email = customer.get("email", "N/A")
            valor = boleto.get('value', 0)
            vencimento = boleto.get('dueDate', "N/A")
            link_pagamento = boleto.get('bankSlipUrl', "N/A")

            # Listagem dos dados
            print(f"\n[INFO] Dados do Cliente:")
            print(f"Nome: {nome}")
            print(f"E-mail: {email}")
            print(f"Valor: R${valor}")
            print(f"Vencimento: {vencimento}")
            print(f"Link: {link_pagamento}")

            # Envia o e-mail para o destinatário de teste
            send_email(destinatario_teste, nome, valor, vencimento, link_pagamento)

        return boletos

    except Exception as e:
        print(f"[ERROR] Erro ao buscar boletos: {e}")
        return []


def check_and_notify():
    """
    Função principal que verifica os boletos e envia notificações.
    """
    print(f"\n--- Verificação iniciada em {datetime.now()} ---")
    fetch_boletos()
    print("Processo concluído.\n")


def test_connection():
    """
    Testa a conexão com a API do Asaas.
    """
    try:
        print("Testando conexão com a API do Asaas...")
        response = requests.get(ASAAS_API, headers={
            'access_token': ASAAS_TOKEN,
            'Content-Type': 'application/json',
            'User-Agent': 'teste_gjtechsolucions'
        })

        if response.status_code == 200:
            print("[SUCCESS] Conexão com a API do Asaas bem-sucedida!")
        else:
            print(f"[ERROR] Conexão falhou. Código HTTP: {response.status_code}")
            exit()
    except Exception as e:
        print(f"[ERROR] Erro ao tentar conectar com a API do Asaas: {e}")
        exit()


# Testa a conexão ao iniciar
test_connection()

# Testa a verificação e envio de e-mails
print("Iniciando o processo de verificação e notificação...")
check_and_notify()
