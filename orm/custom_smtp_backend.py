import smtplib
from django.core.mail.backends.base import BaseEmailBackend
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import logging

class CustomSMTPBackend(BaseEmailBackend):
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, use_ssl=None, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.host = host or '10.0.1.12'
        self.port = port or 587
        self.username = username or 'riskmanagement@avax.gr'
        self.password = password or 'Fi39#d9%'  # Replace with your actual password
        self.use_tls = use_tls if use_tls is not None else True
        self.use_ssl = use_ssl if use_ssl is not None else False
        self.connection = None

    def open(self):
        try:
            # Step 1: Establish connection
            self.connection = smtplib.SMTP(self.host, self.port)
            self.connection.set_debuglevel(1)  # Enable debug output
            self.connection.ehlo()

            # Step 2: Start TLS if needed
            if self.use_tls:
                self.connection.starttls()
                self.connection.ehlo()

            # Step 3: Manual AUTH LOGIN process
            # Send the encoded username
            encoded_user = base64.b64encode(self.username.encode()).decode()
            self.connection.docmd("AUTH LOGIN", encoded_user)

            # Wait for the server to respond with the password prompt
            encoded_password = base64.b64encode(self.password.encode()).decode()
            self.connection.docmd(encoded_password)

        except smtplib.SMTPException as e:
            if not self.fail_silently:
                raise
            logging.error(f"Failed to open SMTP connection: {e}")
            self.connection = None

    def close(self):
        if self.connection:
            try:
                self.connection.quit()
            except smtplib.SMTPException as e:
                if not self.fail_silently:
                    raise
                logging.error(f"Failed to close SMTP connection: {e}")
            finally:
                self.connection = None

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        self.open()

        if self.connection is None:
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                mime_message = MIMEMultipart()
                mime_message['Subject'] = message.subject
                mime_message['From'] = message.from_email
                mime_message['To'] = ', '.join(message.to)
                mime_message.attach(MIMEText(message.body, 'plain'))

                self.connection.sendmail(mime_message['From'], mime_message['To'], mime_message.as_string())
                num_sent += 1
            except smtplib.SMTPException as e:
                if not self.fail_silently:
                    raise
                logging.error(f"Failed to send email: {e}")

        self.close()

        return num_sent
