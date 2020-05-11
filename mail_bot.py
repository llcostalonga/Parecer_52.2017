import imaplib, email, getpass, time
import os, shutil, sys
import yagmail
from email import policy
from datetime import datetime

from parecer52_2017.config import settings
from parecer52_2017.parecer import Parecer

import logging

RECONNECTION_TIME = 300 # 3600 #segundos


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('service_status.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def run_bot():

    imap_host = 'imap.gmail.com'
    imap_user = 'resolucao52.2017@gmail.com'

    running_time = 0
    # init imap connection
    mail = imaplib.IMAP4_SSL(imap_host, 993)
    # rc, resp = mail.login(imap_user, getpass.getpass())
    rc, resp = mail.login(imap_user, "cpad2020")
    logger.info(str(datetime.now()) + " login sucessfull ")
    print(str(datetime.now()) + " login sucessfull ")

    print(str(datetime.now()) + " Service started...")
    logger.info("Service started...")
    while 1:
        try:
            # if running_time==0:
            #     # rc, resp = mail.login(imap_user, getpass.getpass())
            #     rc, resp = mail.login(imap_user, "cpad2020")
            #     logger.info(str(datetime.now()) + " login sucessfull ")
            #     print(str(datetime.now()) + " login sucessfull ")

            if running_time % 300 == 0:
                print(str(datetime.now()) + " ...still running")

            mailbox = 'Inbox'
            try:
                mail.select(mailbox)
            except Exception as e:
                print(e)
                mail = login(mailbox)

            status, data = mail.search(None, '(UNSEEN)')

            # for each e-mail messages, print text content
            for num in data[0].split():

                try:
                    # get a single message and parse it by policy.SMTP (RFC compliant)
                    status, data = mail.fetch(num, '(RFC822)')
                except Exception as e:
                    print(e)
                    mail = login(mailbox)
                    status, data = mail.fetch(num, '(RFC822)')


                email_msg = data[0][1]
                email_msg = email.message_from_bytes(email_msg, policy=policy.SMTP)
                return_email = str(email_msg['Return-Path'])[1:-1]

                print("Processando email de  " + return_email)

                attachments = get_attachments(email_msg)

                if (len(attachments) > 0 and check_attachments(attachments)):
                    parecer = Parecer.run()
                    try:
                        print("    anexos de acordo com o esperado")
                        reply_email(return_email,email_msg, parecer)
                        logger.info( "Respondido: " + str(email_msg['From']) + " anexos: " + str(attachments))
                        delete_files()
                        print("    e-mail respondido com o parecer")
                    except:
                        print("    falha ao tentar responder o e-mail ")
                        logger.info( "Falha da resposta: " + str(email_msg['From']) + " anexos: " + str(attachments))
                else:
                    send_instruction_email(return_email)
                    print("    respondido com o email de instrução")

              #Remove e-mail da Inbox
                mail.store(num, '+FLAGS', r'(\Deleted)')

            time.sleep(60)
            running_time+=60
        except:
            print("Unexpected error:", sys.exc_info()[0])


def login(mailbox):
    mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    mail.login('resolucao52.2017@gmail.com','cpad2020')
    logger.info(" logging in again.. sucessfull ")
    print(str(datetime.now()) + " logging in again.. sucessfull ")
    mail.select(mailbox)
    return mail

def get_attachments(email_msg):
    attachments_names = []
    for part in email_msg.walk():
        # this part comes from the snipped I don't understand yet...
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = part.get_filename()
        if bool(fileName):
            attachments_names.append(fileName)
            #log_entry += " " + fileName + ","
            filePath = os.path.join(settings.data_folder, fileName)
            if not os.path.isfile(filePath):
                fp = open(filePath, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
    return attachments_names

def reply_email(return_email, email_msg, parecer:Parecer):

    # initializing the server connection
    yag = yagmail.SMTP(user='resolucao52.2017@gmail.com', password='cpad2020')
    # sending the email
    yag.send(to=return_email, subject="Reply:" + email_msg['Subject'], contents=str(parecer),
             attachments=parecer.lista_aquivos)
    # yag.send(to=return_email, subject="Reply:" + email_msg['Subject'], contents= str(parecer),
    #          attachments='anexo.docx')


def send_instruction_email(email_address):
    try:
        # initializing the server connection
        yag = yagmail.SMTP(user='resolucao52.2017@gmail.com', password='cpad2020')

        conteudo_email = "Olá, \n  Seu e-mail foi recebido mas ele não está instruído com os arquivos que " \
                        "é preciso para realizar a análise automatizada. São necessários: \n" \
                        "   a) Relatório de Progressão obtido no portal do docente ('ProgressaoDocente.pdf')\n" \
                        "   b) Ficha de qualificação funcional para progressão obtida no portal do servidor " \
                        "( 'ficha_qualificacao_progressao.pdf') \n" \
                        "   c)Arquivo XML do Currículo Lattes obtido na própria platafoma ('curriculo.xml') \n" \
                        "\n Atenção: os nomes dos arquivos precisam ser exatamente como descritos acima.  Mais informações" \
                        " em http://http://tiny.cc/nd4voz  " \
                         "\n Prof. Leandro Costalonga (CPAD/CEUNES/UFES)"

        # sending the email
        yag.send(to=email_address, subject="Ops..os anexos não foram reconhecidos", contents=conteudo_email)
        # yag.send(to=return_email, subject="Reply:" + email_msg['Subject'], contents= str(parecer),
        #          attachments='anexo.docx')
        logger.info("Email de instrução enviado para " + email_address)
    except:
        logger.exception("Falha ao enviar e-mail de instrução para" + email_address)

def check_attachments ( list_filenames):
    expected_files = [settings.filename_ficha_funcional,
                      settings.filename_portal_docente,
                      settings.filename_xml_lattes]

    for file in list_filenames:
        if not(file in expected_files):
            return False
    return True

def delete_files():
    folder = settings.data_folder
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


if __name__ == "__main__":
    run_bot()

