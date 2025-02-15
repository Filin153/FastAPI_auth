import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email_validator import validate_email

from .SMTP import SMTP


class Mail(SMTP):
    def __init__(self, smtp_server: str, smtp_port: int,
                 smtp_username: str, smtp_password: str,
                 ssl: bool = False, tls: bool = False):
        super().__init__(smtp_server, smtp_port, smtp_username, smtp_password, ssl, tls)

    async def send(self, to_email: str, title: str, body: str):
        """
        Send msg to email
        :param to_email: email address recipient
        :param title: email title
        :param body: email body, supports HTML
        :return:
        """
        await self.smtp_async.connect()
        to_email = self.__validate_email(to_email)
        msg = MIMEMultipart()
        msg["From"] = self.smtp_username
        msg["To"] = to_email
        msg["Subject"] = title
        msg.attach(MIMEText(body, 'html'))

        self.smtp_async._server.sendmail(self.smtp_username, to_email, msg.as_string())
        logging.info(f"Mail sent successfully to {to_email}")
        await self.smtp_async.disconnect()
        return True

    def send_sync(self, to_email: str, title: str, body: str):
        """
        Send msg to email
        :param to_email: email address recipient
        :param title: email title
        :param body: email body, supports HTML
        :return:
        """
        self.smtp_sync.connect()
        to_email = self.__validate_email(to_email)
        msg = MIMEMultipart()
        msg["From"] = self.smtp_username
        msg["To"] = to_email
        msg["Subject"] = title
        msg.attach(MIMEText(body, 'html'))

        self.smtp_sync._server.sendmail(self.smtp_username, to_email, msg.as_string())
        logging.info(f"Mail sent successfully to {to_email}")
        self.smtp_sync.disconnect()
        return True

    @staticmethod
    def __validate_email(email: str) -> str:
        """
        Validate email string
        :param email:
        :return:
        """
        emailinfo = validate_email(email, check_deliverability=False)
        email = emailinfo.normalized
        return email
