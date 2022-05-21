import email
import imaplib
import os
import smtplib

# from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def ler_emails():

    #########################################
    # USUARIO E SENHAS
    #########################################
    IMAP_HOST = 'imap.gmail.com'
    USERNAME = os.environ['email']
    PASSWORD = os.environ['email_senha']
    SEARCH_CRITERIA = '(UNSEEN FROM "estudos.invest1@gmail.com")'
    # SEARCH_CRITERIA = '(FROM "estudos.invest1@gmail.com")'
    # SEARCH_CRITERIA = '(FROM "jorgemnr@gmail.com")'
    VERBOSE = True

    # Anexos do email
    anexos = {}

    #########################################
    # ABRIR CONEXÃO SERVIDOR
    #########################################
    imap_client = imaplib.IMAP4_SSL(IMAP_HOST)
    imap_client.login(USERNAME, PASSWORD)

    #########################################
    # PESQUISAR EMAILS
    #########################################
    status, _ = imap_client.select('INBOX', readonly=True)
    if status != 'OK':
        raise Exception('Não foi possível selecionar INBOX.')

    status, data = imap_client.search(None, SEARCH_CRITERIA)
    if status != 'OK':
        raise Exception('Não foi possível procurar emails.')

    #########################################
    # LOOP EMAILS
    #########################################
    messages_id_list = data[0].decode('utf-8').split(' ')
    # Fetch each message data
    if messages_id_list[0] != '':
        if VERBOSE:
            print()
            print(
                '{} emails foram encontrados. Encaminhamento irá começar imediatamente.'.format(
                    len(messages_id_list)
                )
            )
            print('Emails ids: {}'.format(messages_id_list))
        messages_sent = []

        #########################################
        # PEGAR ANEXOS
        #########################################
        while len(messages_sent) < len(messages_id_list):
            msg_id = messages_id_list[len(messages_sent)]

            status, msg_data = imap_client.fetch(msg_id, '(RFC822)')
            if status != 'OK':
                raise Exception(
                    'Não foi possível pegar email com id {}'.format(msg_id)
                )

            anexos = {}
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    for part in msg.walk():
                        if part.get_content_maintype() == 'multipart':
                            continue
                        if part.get('Content-Disposition') is None:
                            continue
                        fileName = part.get_filename()
                        if bool(fileName):
                            # Email menor igual a 25 Megabytes
                            if (
                                len(str(anexos.values())) / 1024**2
                                + len(part.get_payload(decode=True))
                                / 1024**2
                                <= 25
                            ):
                                anexos[fileName] = part.get_payload(
                                    decode=True
                                )
                            else:
                                #########################################
                                # ENVIAR E-MAIL
                                #########################################
                                enviarEmails(anexos=anexos)
                                anexos = {}
                                anexos[fileName] = part.get_payload(
                                    decode=True
                                )
            messages_sent.append(msg_id)

            #########################################
            # ENVIAR E-MAIL
            #########################################
            enviarEmails(anexos=anexos)
            # break
    else:
        if VERBOSE:
            print()
            print('Não foram encontrados emails.')

    if VERBOSE:
        print('Trabalho finalizado. Aproveite seu dia!')
        print()

    #########################################
    # FECHAR CONEXÃO SERVIDOR
    #########################################
    imap_client.close()
    imap_client.logout()
    return 'Trabalho finalizado. Aproveite seu dia!'


#################################################################################################


def enviarEmails(anexos: dict):

    #########################################
    # USUARIO E SENHAS
    #########################################
    endereco_remetente = os.environ['email']
    remetente_senha = os.environ['email_senha']
    enderecos_destinatarios = [
        'paulo.macedo@seara.com.br',
        'jorge.manuel@seara.com.br',
        'cristiano.born@seara.com.br',
    ]

    #########################################
    # REMETENTE / DESTINATARIO / ASSUNTO
    #########################################
    msg = MIMEMultipart()
    msg['From'] = endereco_remetente
    msg['To'] = ', '.join(enderecos_destinatarios)
    msg['Subject'] = 'Investimentos'

    #########################################
    # CORPO E-MAIL
    #########################################
    corpo_email = 'Investimentos'
    msg.attach(MIMEText(corpo_email))

    #########################################
    # ANEXOS E-MAIL
    #########################################
    for f in anexos or {}:
        # with open(f, "rb") as fil:
        # ext = f.split('.')[-1:]
        ext = f[f.find('.') + 1 :]
        attachedfile = MIMEApplication(anexos[f], _subtype=ext)
        attachedfile.add_header(
            'content-disposition', 'attachment', filename=f
        )
        msg.attach(attachedfile)

    #########################################
    # ABRIR CONEXÃO / ENVIAR / FECHAR CONEXÃO
    #########################################
    try:
        smtp = smtplib.SMTP(host='smtp.gmail.com', port=587, timeout=240)
    except BaseException as erro:
        v_msg = f'Erro de SMTP > {erro}'
        print(v_msg)
        raise Exception(v_msg)

    smtp.starttls()
    smtp.login(endereco_remetente, remetente_senha)
    smtp.sendmail(endereco_remetente, enderecos_destinatarios, msg.as_string())
    smtp.close()


ler_emails()
