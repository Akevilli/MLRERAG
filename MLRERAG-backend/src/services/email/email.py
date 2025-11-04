import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.core import settings


class EmailService:
    def sent_welcome_email(self, receiver: str, token: str):
        message = MIMEMultipart()

        message["From"] = settings.SMTP_EMAIL
        message["To"] = receiver
        message["Subject"] = "Account activation"
        message.attach(MIMEText(f"Welcome to MLRERAG! Your activation token: {token}.", "plain"))

        context = ssl.create_default_context()

        smtp = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        
        smtp.starttls(context=context)
        smtp.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)

        smtp.send_message(message)