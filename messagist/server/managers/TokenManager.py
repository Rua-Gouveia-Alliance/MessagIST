import threading
import logging
import ssl
import smtplib
import secrets

from datetime import datetime
from email.message import EmailMessage


class TokenManager:
    def __init__(self):
        self.TWOFACTOR_TIME = 180  # 3min
        self.tokens = {}
        self.lock = threading.Lock()

    def sendTwoFactorToken(self, username):
        logging.debug(f"Token stored for user {username}.")
        self.lock.acquire()

        if username in self.tokens:
            storedToken, timestamp = self.tokens[username]
            difference = (datetime.now() - timestamp).total_seconds()
            if difference <= self.TWOFACTOR_TIME:
                logging.debug("Token still valid for user {username}.")
                return False

        token = secrets.token_urlsafe(16)
        self.tokens[username] = (token, datetime.now())

        self._sendEmail(username, token)

        self.lock.release()

        return True

    def clearTwoFactorToken(self, username):
        if username in self.tokens:
            del self.tokens[username]
            logging.debug(f"Token cleared for user {username}.")

    def verifyTwoFactorToken(self, username, token):
        self.lock.acquire()

        if username not in self.tokens:
            logging.debug("No token found for user")
            return False, None

        storedToken, timestamp = self.tokens[username]
        difference = (datetime.now() - timestamp).total_seconds()
        if difference > self.TWOFACTOR_TIME:
            logging.debug("Token expired")
            self.clearTwoFactorToken(username)
            return False, None

        status = token == storedToken
        if status:
            logging.debug("Valid token")
            self.clearTwoFactorToken(username)

        self.lock.release()
        return status

    def _sendEmail(self, username, token):
        # we have created a temporary email address to send 2FA emails
        # this configuration would need to be updated to use a secure and production-ready email system
        emailSender = "messagistauthentication@gmail.com"
        emailPassword = "wlub cnnk xiiw grdz"

        emailReceiver = f"{username}@tecnico.ulisboa.pt"
        subject = "2FA Token"
        body = (
            f"Hello,\n\nYour Two-Factor Authentication (2FA) code is: {token}"
            + f"\n\nThis code is valid for {self.TWOFACTOR_TIME // 60} minutes."
            + " Please enter it in the app to complete your login.\n\nIf you "
            + "did not request this code, please secure your account "
            + "immediately by changing your password or contacting support."
            + "\n\nThank you,\nMessagIST Team"
        )
        em = EmailMessage()
        em["From"] = emailSender
        em["To"] = emailReceiver
        em["Subject"] = subject
        em.set_content(body)

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(emailSender, emailPassword)
                smtp.sendmail(emailSender, emailReceiver, em.as_string())
            logging.debug("Token email sent successfully.")
        except Exception as e:
            logging.debug(f"Error sending email: {e}")
