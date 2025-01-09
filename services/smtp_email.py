import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders                                  # Импортируем энкодер
from email.mime.base import MIMEBase
import logging


async def send_email(to_email: str, message_email: str, tg_user: int):
    logging.info('send_email()')
    msg = MIMEMultipart()
    from_email = 't338to178@mail.ru'
    password = 'py0UkiRssRXs2a8Wrqnq'
    # to_email = "a.l.ponomarev@mail.ru"
    message = message_email
    msg['Subject'] = 'Avibus_pro'
    msg.attach(MIMEText(message, 'plain'))

    file_path = f"TICKET/{tg_user}.pdf"
    with open(file_path, "rb") as file:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={file_path}")
    msg.attach(part)

    server = smtplib.SMTP_SSL('smtp.mail.ru: 465')
    server.login(from_email, password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

