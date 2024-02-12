# файл email_verif.py

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные окружения из файла .env

def send_verification_email(email, verification_code):
    """
    Sends a verification email to the specified email address with the provided verification code.

    This function constructs an email message with the verification code and sends it
    using the SMTP protocol. The SMTP server details and the credentials are obtained from
    the environment variables.

    Args:
        email (str): The recipient's email address.
        verification_code (str): The verification code to be sent in the email.

    Raises:
        smtplib.SMTPException: An error occurred during the process of sending the email.
    """

    # Настройки SMTP-сервера
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')

    # Формирование сообщения
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = email
    msg['Subject'] = 'Verification Code'

    body = f'Your verification code is: {verification_code}'
    msg.attach(MIMEText(body, 'plain'))

    # Создание объекта SMTP
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Включаем TLS
    server.login(smtp_username, smtp_password)  # Аутентификация на сервере SMTP
    server.sendmail(msg['From'], msg['To'], msg.as_string())  # Отправка письма
    server.quit()
