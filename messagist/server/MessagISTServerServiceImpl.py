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
    def __init__(self, *args, **kwargs):
        self.userManager = UserManager()
        self.chatManager = ChatManager()
        self.sessionManager = SessionManager()

    def signup(self, request, context):
        logging.debug("SIGNUP request received.")
        logging.debug("Username: " + request.username)

        username = request.username
        password = request.password
        salt = request.salt
        success = self.userManager.newUser(username, password, salt)
        if success:
            # TODO: Unnecessary once we have an actual database (i think)
            self.chatManager.initUser(username)
        return pb2.SignupResponse(success=success)

    def getSalt(self, request, context):
        logging.debug("GETSALT request received")
        logging.debug("Username: " + request.username)

        username = request.username
        salt = self.userManager.getSalt(username)

        if salt != "":
            logging.debug("Found salt")

        return pb2.GetSaltResponse(success=(salt != ""), salt=salt)

    def login(self, request, context):
        logging.debug("LOGIN request received")
        logging.debug("Username: " + request.username)

        username = request.username
        password = request.password

        if self.userManager.validUser(username, password):
            logging.debug("Valid user")
            token = self.sessionManager.startSession(username)
            logging.debug("LOGIN " + ("success" if token != "" else "FAILED"))
            return pb2.LoginResponse(success=(token != ""), token=token)
        logging.debug("LOGIN FAILED")
        return pb2.LoginResponse(success=False, token="")

    def send(self, request, context):
        logging.debug("SEND request received")
        logging.debug("Message: " + request.message)

        username = self.sessionManager.getUser(request.token)
        if username == "":
            logging.debug("SEND FAILED")
            return pb2.SendResponse(success=False, timestamp=-1)

        partner = request.partner
        self.chatManager.startChat(username, partner)
        ts = self.chatManager.sendMessage(username, partner, request.message)
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
            messages.append(
                self.chatManager.getMessage(username, partner, timestamps[i])
            )
        logging.debug("KEEPALIVE success")
        return pb2.KeepAliveResponse(success=True, messages=messages, partners=partners)
