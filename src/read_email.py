import email
import imaplib
import os
from threading import Thread
from time import perf_counter

from dotenv import load_dotenv

from src.send_email import send_email

load_dotenv()


def convert_bytes(size):
    """Converter bytes para KB, ou MB ou GB"""
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return '%3.1f %s' % (size, x)
        size /= 1024.0


def read_email():
    LIMIT_BYTES = 31457280  # 30 MB
    CONSUMER_BYTES = 0
    #########################################
    # USUARIO E SENHAS
    #########################################
    IMAP_HOST = 'imap.gmail.com'
    USERNAME = os.environ.get('EMAIL')
    PASSWORD = os.environ.get('PASSWORD')
    SEARCH_CRITERIA = os.environ.get('EMAIL_SEARCH')
    # SEARCH_CRITERIA = '(UNSEEN FROM "estudos.invest1@gmail.com")'

    VERBOSE = True

    # Anexos do email
    anexos = {}
    threads = []
    start_time = perf_counter()
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

        #########################################
        # PEGAR ANEXOS
        #########################################
        for msg_id in messages_id_list:
            print('desempacotar', msg_id)
            status, msg_data = imap_client.fetch(msg_id, '(RFC822)')
            if status != 'OK':
                raise Exception(
                    'Não foi possível pegar email com id {}'.format(msg_id)
                )

            anexos = {}

            for response_part in msg_data:
                # print(type(response_part))
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    for part in msg.walk():
                        # if part.get_content_maintype() == 'multipart':
                        if part.is_multipart():
                            continue
                        if part.get('Content-Disposition') is None:
                            continue
                        fileName = part.get_filename()
                        if bool(fileName):
                            file_size = len(str(part))
                            CONSUMER_BYTES += file_size
                            if CONSUMER_BYTES <= LIMIT_BYTES:
                                anexos[fileName] = part.get_payload(
                                    decode=True
                                )
                                #CONSUMER_BYTES += file_size
                            else:
                                print(
                                    'PASSOU 30 MB',
                                    convert_bytes(CONSUMER_BYTES),
                                )
                                task = Thread(
                                    target=send_email, args=(anexos,)
                                )
                                threads.append(task)
                                print(f'criou a Thread {convert_bytes(CONSUMER_BYTES - file_size)}')
                                task.start()
                                print('FIM a Thread')

                                CONSUMER_BYTES = 0
                                anexos = {}

                    print('Enviando Email:.')
                    print(f'Criou a Thread Final {convert_bytes(file_size)}')
                    anexos[fileName] = part.get_payload(
                                    decode=True
                                )
                    task = Thread(target=send_email, args=(anexos,))
                    threads.append(task)
                    task.start()
            # wait for the threads to complete
            for t in threads:
                t.join()
            
    else:
        if VERBOSE:
            print()
            print('Não foram encontrados emails.')

    end_time = perf_counter()        

    if VERBOSE:
        print(
            f'Trabalho finalizado. Aproveite seu dia!/n tempo de execução:{end_time- start_time: 0.2f}'
        )
        print()

    #########################################
    # FECHAR CONEXÃO SERVIDOR
    #########################################
    imap_client.close()
    imap_client.logout()
