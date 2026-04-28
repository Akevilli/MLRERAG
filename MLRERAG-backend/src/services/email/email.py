from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from src.core import settings, retry_strategy


class EmailService:
    @retry_strategy
    async def sent_welcome_email(self, receiver: str, token: str):
        message = MIMEMultipart()
        message["From"] = settings.SMTP_EMAIL
        message["To"] = receiver
        message["Subject"] = "Account activation"
        message.attach(MIMEText(f"Welcome to MLRERAG! Your activation token: {token}.", "plain"))

        is_ssl_port = settings.SMTP_PORT == 465

        smtp = aiosmtplib.SMTP(
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            use_tls=is_ssl_port,
            timeout=10
        )

        async with smtp:
            await smtp.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
            await smtp.send_message(message)