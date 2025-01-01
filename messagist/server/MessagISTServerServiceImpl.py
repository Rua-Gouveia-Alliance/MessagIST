import sys
import logging

import time
import pyotp
import os

sys.path.insert(1, "../contract/target/")
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2
from managers.ChatManager import ChatManager
from managers.SessionManager import SessionManager
from managers.UserManager import UserManager

from email.message import EmailMessage
import ssl
import smtplib


# TODO: Configurar logger em condicoes
class MessagISTServerServiceImpl(pb2_grpc.MessagISTServerServicer):
    def __init__(self, db, *args, **kwargs):
        self.db = db
        self.userManager = UserManager(db)
        self.chatManager = ChatManager(db)
        self.sessionManager = SessionManager()

    def signup(self, request, context):
        logging.debug("SIGNUP request received.")
        logging.debug("Username: " + request.username)

        username = request.username
        password = request.password
        salt = request.salt
        identityKey = request.identityKey
        success = self.userManager.newUser(username, password, salt, identityKey)
        if not success:
            logging.debug("SIGNUP FAILED")
        return pb2.SignupResponse(success=success)

    def getSalt(self, request, context):
        logging.debug("GETSALT request received")
        logging.debug("Username: " + request.username)

        username = request.username
        salt = self.userManager.getSalt(username)

        if salt != b"":
            logging.debug("Found salt")

        return pb2.GetSaltResponse(success=(salt != b""), salt=salt)

    def login(self, request, context):
        logging.debug("LOGIN request received")
        logging.debug("Username: " + request.username)

        username = request.username
        password = request.password

        if self.userManager.validUser(username, password):

            logging.debug("Valid user")
            # Generate 2FA Token
            key = "NeuralNineMySuperSecretKey"
            totp = pyotp.TOTP(key)
            token = totp.now()
            self.sendMailToken(username, token)
            self.sessionManager.storeToken(username, token, time.time())
            return pb2.LoginResponse(success=True, token="")

        logging.debug("LOGIN FAILED")
        return pb2.LoginResponse(success=False, token="")

    def submit_2fa_code(self, request, context):
        logging.debug("2FA code submission received")
        username = request.username
        token = request.code
        if self.sessionManager.verifyToken(username, token):
            session_token = self.sessionManager.startSession(username)
            logging.debug("2FA success, session started.")
            self.sessionManager.clearToken(username)
            return pb2.LoginResponse(success=True, token=session_token)

        logging.debug("2FA failed")
        return pb2.LoginResponse(success=False)

    def sendMailToken(self, username, token):
        email_sender = "messagistauthentication@gmail.com"
        # email_password = os.environ.get("EMAIL_PASSWORD")
        email_password = "wlub cnnk xiiw grdz"
        ist_id = username
        email_receiver =  f"{ist_id}@tecnico.ulisboa.pt"

        subject = "2FA Token"

        body = f"""
        Hello,

        Your Two-Factor Authentication (2FA) code is: {token}

        This code is valid for 5 minutes. Please enter it in the app to complete your login.

        If you did not request this code, please secure your account immediately by changing your password or contacting support.

        Thank you,
        MessagIST Team
        """
        em = EmailMessage()
        em["From"] = email_sender
        em["To"] = email_receiver
        em["subject"] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())
            logging.info("Token email sent successfully.")
        except Exception as e:
            logging.error(f"Error sending email: {e}")

    def send(self, request, context):
        logging.debug("SEND request received")
        logging.debug("Message: " + request.message)

        username = self.sessionManager.getUser(request.token)
        partner = request.partner

        logging.debug("Username: " + username)
        logging.debug("Partner: " + partner)

        if username == "" or not self.userManager.existingUser(partner):
            logging.debug("Invalid username")
            logging.debug("SEND FAILED")
            return pb2.SendResponse(success=False, timestamp=-1)
        if username == partner:
            logging.debug("Cannot send message tou yourself")
            logging.debug("SEND FAILED")
            return pb2.SendResponse(success=False, timestamp=-1)

        user_id = self.userManager.getUserId(username)
        partner_id = self.userManager.getUserId(partner)
        self.chatManager.startChat(user_id, partner_id)
        ts = self.chatManager.sendMessage(user_id, partner_id, request.message)
        logging.debug("Timestamp: " + str(ts))
        logging.debug("SEND " + ("success" if ts != -1 else "FAILED"))
        return pb2.SendResponse(success=(ts != -1), timestamp=ts)

    def keepAlive(self, request, context):
        logging.debug("KEEPALIVE request received")

        username = self.sessionManager.getUser(request.token)
        if not self.sessionManager.renewLease(username):
            logging.debug("KEEPALIVE FAILED")
            return pb2.KeepAliveResponse(success=False, messages=[], partners=[])

        partners = request.partners
        timestamps = request.timestamps
        allPartners = self.chatManager.getPartners(username)
        for partner in allPartners:
            if partner not in partners:
                partners.append(partner)
                timestamps.append(0)

        messages = []
        for i, partner in enumerate(partners):
            if self.userManager.existingUser(partner):
                messages.append(
                    self.chatManager.getMessage(username, partner, timestamps[i])
                )
            else:
                messages.append("")
        logging.debug("KEEPALIVE success")
        return pb2.KeepAliveResponse(success=True, messages=messages, partners=partners)

    def getIdentityKey(self, request, context):
        logging.debug("GETIDENTITYKEY request received")
        logging.debug("Username: " + request.username)

        username = request.username
        identityKey = self.userManager.getUserKey(username)
        if identityKey == "":
            logging.debug("GETIDENTITYKEY FAILED")
            return pb2.GetIdentityKeyResponse(identityKey=b"")

        logging.debug("GETIDENTITYKEY success")
        return pb2.GetIdentityKeyResponse(identityKey=identityKey)

    def trySetSalt(self, request, context):
        logging.debug("TRYSETSALT request received")
        logging.debug("Partner: " + request.partner)

        username = self.sessionManager.getUser(request.token)
        partner = request.partner
        received_salt = request.salt
        if username == "" or not self.userManager.existingUser(partner):
            logging.debug("TRYSETSALT FAILED")
            return pb2.TrySetSaltResponse(salt=received_salt)
        if username == partner:
            # cant chat with yourself
            logging.debug("TRYSETSALT FAILED")
            return pb2.TrySetSaltResponse(slat="")

        user_id = self.userManager.getUserId(username)
        partner_id = self.userManager.getUserId(partner)
        salt = self.chatManager.trySetSalt(user_id, partner_id, received_salt)

        if salt == received_salt:
            logging.debug("New salt")
        elif salt == "":
            logging.error("Error setting/getting salt")
        else:
            logging.debug("Salt already existed for this chat")

        return pb2.TrySetSaltResponse(salt=salt)
