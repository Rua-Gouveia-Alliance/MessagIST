import threading
import logging
import ssl
import smtplib
import secrets

from managers.Session import Session
from datetime import datetime
from email.message import EmailMessage


class SessionManager:
    def __init__(self):
        self.LEASE_TIME = 5  # 5s
        self.TWOFACTOR_TIME = 120  # 2min
        self.sessions = {}
        self.lock = threading.Lock()
        self.tokens = {}

    def startSession(self, username):
        self.lock.acquire()

        token = ""
        if username not in self.sessions:
            self.sessions[username] = Session(self, username)
            token = self.sessions[username].token

        self.lock.release()
        return token

    def endSession(self, username):
        self.lock.acquire()

        status = False
        if username in self.sessions:
            del self.sessions[username]
            logging.debug(username + "'s session expired")
            status = True

        self.lock.release()
        return status

    def validSession(self, username, token):
        self.lock.acquire()
        status = username in self.sessions and self.sessions[username].validate(token)
        self.lock.release()
        return status

    def getUser(self, token):
        self.lock.acquire()

        result = ""
        for username, session in self.sessions.items():
            if session.validate(token):
                result = username
                break

        self.lock.release()
        return result

    def renewLease(self, username):
        self.lock.acquire()

        status = False
        if username in self.sessions:
            self.sessions[username].renewLease()
            status = True
            logging.debug(username + "'s lease renewed")

        self.lock.release()
        return status

    def sendTwoFactorToken(self, username):
        logging.debug(f"Token stored for user {username}.")
        self.lock.acquire()
        # TODO: Talvez trocar para pyotp (parece melhor mas pa fazer bem da mais trabalho)
        token = secrets.token_urlsafe(16)
        self.tokens[username] = (token, datetime.now())
        self._sendEmail(username, token)

        self.lock.release()

    def clearTwoFactorToken(self, username):
        """
        Clear the stored token for a user after successful verification or expiration.
        :param username: The username whose token should be cleared
        """
        self.lock.acquire()

        if username in self.tokens:
            del self.tokens[username]
            logging.debug(f"Token cleared for user {username}.")

        self.lock.release()

    def verifyTwoFactorToken(self, username, token):
        self.lock.acquire()

        if username not in self.tokens:
            logging.debug("No token found for user")
            return False

        storedToken, timestamp = self.tokens[username]
        difference = (datetime.now() - timestamp).total_seconds()
        if difference > self.TWOFACTOR_TIME:
            logging.debug("Token expired")
            self.clearToken(username)
            return False

        self.lock.release()
        return token == storedToken

    def _sendEmail(self, username, token):
        emailSender = "messagistauthentication@gmail.com"
        emailPassword = "wlub cnnk xiiw grdz"

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
        em["To"] = username  # TODO
        em["Subject"] = subject
        em.set_content(body)

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(emailSender, emailPassword)
                smtp.sendmail(emailSender, username, em.as_string())
            logging.debug("Token email sent successfully.")
        except Exception as e:
            logging.debug(f"Error sending email: {e}")
