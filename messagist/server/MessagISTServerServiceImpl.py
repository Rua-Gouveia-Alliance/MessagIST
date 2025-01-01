import sys
import logging

sys.path.insert(1, "../contract/target/")
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2
from managers.ChatManager import ChatManager
from managers.SessionManager import SessionManager
from managers.UserManager import UserManager


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
            self.sessionManager.sendToken(username)
            return pb2.LoginResponse(success=True)

        logging.debug("LOGIN FAILED")
        return pb2.LoginResponse(success=False)

    def submitTwoFactorToken(self, request, context):
        logging.debug("SUBMITTWOFACTORTOKEN received")
        logging.debug("Username: " + request.username)

        username = request.username
        token = request.token
        if self.sessionManager.verifyToken(username, token):
            logging.debug("Valid token")
            self.sessionManager.clearToken(username)
            token = self.sessionManager.startSession(username)
            return pb2.SubmitTwoFactorTokenRequest(success=(token != ""), token=token)

        logging.debug("SUBMITTWOFACTORTOKEN FAILED")
        return pb2.SubmitTwoFactorTokenRequest(success=False, token="")

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
