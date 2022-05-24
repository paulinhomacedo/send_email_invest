import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def send_email(anexos: dict):

    #########################################
    # USUARIO E SENHAS
    #########################################
    endereco_remetente = os.environ.get('EMAIL')
    remetente_senha = os.environ.get('PASSWORD')
    enderecos_destinatarios = os.environ.get('EMAIL_GROUP').split(sep=',')

    #########################################
    # REMETENTE / DESTINATARIO / ASSUNTO
    #########################################
    msg = MIMEMultipart()
    msg['From'] = endereco_remetente
    # msg['To'] = ', '.join(enderecos_destinatarios)
    msg['Cco'] = ', '.join(enderecos_destinatarios)
    msg['Subject'] = '.:Investimentos:.'
    corpo_email = ''

    #########################################
    # ANEXOS E-MAIL
    #########################################    
    for name_arquivo, conteudo in anexos.items():
        suffix = Path(name_arquivo).suffix
        name_file = Path(name_arquivo).name
        corpo_email += f'{name_file}\n'
        attachedfile = MIMEApplication(conteudo, _subtype=suffix)
        attachedfile.add_header(
            'content-disposition', 'attachment', filename=name_arquivo
        )
        msg.attach(attachedfile)
    #########################################
    # CORPO E-MAIL
    #########################################
    # corpo_email = 'Segue anexo '
    msg.attach(MIMEText(corpo_email))

    #########################################
    # ABRIR CONEXÃO / ENVIAR / FECHAR CONEXÃO
    #########################################
    try:
        smtp = smtplib.SMTP(host='smtp.gmail.com', port=587, timeout=240)
    except BaseException as erro:
        v_msg = f'Erro de SMTP > {erro}'        
        raise Exception(v_msg)
    smtp.starttls()
    smtp.login(endereco_remetente, remetente_senha)
    smtp.sendmail(endereco_remetente, enderecos_destinatarios, msg.as_string())
    smtp.close()
