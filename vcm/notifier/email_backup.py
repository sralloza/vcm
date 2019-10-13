import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from vcm.core.credentials import Credentials

logger = logging.getLogger(__name__)


def send_email(destinations, subject, message, origin="Rpi-VCM", retries=5):
    logger.debug("Sending email")

    username = Credentials.Email.username
    password = Credentials.Email.password

    if isinstance(destinations, str):
        destinations = [destinations]

    msg = MIMEMultipart()
    msg["From"] = f"{origin} <{username}>"
    msg["To"] = ", ".join(destinations)
    msg["Subject"] = subject

    body = message.replace("\n", "<br>")
    msg.attach(MIMEText(body, "html"))

    while retries > 0:
        try:
            server = smtplib.SMTP(Credentials.Email.smtp_server, Credentials.Email.smtp_port)
        except smtplib.SMTPConnectError:
            logger.warning("SMTP Connect Error, retries=%d", retries)
            retries -= 1
            continue

        server.starttls()

        server.login(username, password)

        server.sendmail(username, destinations, msg.as_string())
        server.quit()

        logger.info("Email sent successfully")
        return True

    logger.critical("Critical error sending email, retries=%d", retries)
    return False
