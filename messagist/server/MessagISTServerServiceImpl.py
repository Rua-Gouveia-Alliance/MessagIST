import sys
import logging

sys.path.insert(1, "../contract/target/")
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2
from managers.ChatManager import ChatManager
from managers.SessionManager import SessionManager
from managers.UserManager import UserManager
from managers.IdentityKeyManager import IdentityKeyManager
from managers.ChatSaltManager import ChatSaltManager


# TODO: Configurar logger em condicoes
class MessagISTServerServiceImpl(pb2_grpc.MessagISTServerServicer):
    def __init__(self, db, *args, **kwargs):
        self.userManager = UserManager(db)
        self.chatManager = ChatManager(db)
        self.sessionManager = SessionManager()
        self.identityKeyManager = IdentityKeyManager(db)
        self.chatSaltManager = ChatSaltManager(db)

    def signup(self, request, context):
        logging.debug("SIGNUP request received.")
        logging.debug("Username: " + request.username)

        username = request.username
        password = request.password
        salt = request.salt
        success = self.userManager.newUser(username, password, salt)  # basede dados
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
            token = self.sessionManager.startSession(username)
            logging.debug("LOGIN " + ("success" if token != "" else "FAILED"))
            return pb2.LoginResponse(success=(token != ""), token=token)
        logging.debug("LOGIN FAILED")
        return pb2.LoginResponse(success=False, token="")

    def send(self, request, context):
        logging.debug("SEND request received")
        logging.debug("Message: " + request.message)

        username = self.sessionManager.getUser(request.token)
        partner = request.partner
        if username == "" or not self.userManager.existingUser(partner):
            logging.debug("SEND FAILED")
            return pb2.SendResponse(success=False, timestamp=-1)
        if username == partner:
            # cant chat with yourself
            logging.debug("SEND FAILED")
            return pb2.SendResponse(success=False, timestamp=-1)

        user_id = self.userManager.getUserId(username)
        partner_id = self.userManager.getUserId(partner)
        self.chatManager.startChat(user_id, partner_id)
        ts = self.chatManager.sendMessage(user_id, partner_id, request.message)
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

    def registerIdentityKey(self, request, context):
        logging.debug("REGISTERIDENTITYKEY request received")
        logging.debug("Username: " + request.username)

        username = self.sessionManager.getUser(request.token)
        if username == "":
            logging.debug("GETCLIENTKU FAILED")
            return pb2.RegisterIdentityKeyResponse(success=False)

        identity_key = request.identity_key
        user_id = self.userManager.getUserId(username)
        if not self.identityKeyManager.registerKey(user_id, identity_key):
            logging.debug("GETCLIENTKU FAILED")
            return pb2.RegisterIdentityKeyResponse(success=False)

        logging.debug("GETCLIENTKU success")
        return pb2.RegisterIdentityKeyResponse(success=True)

    def getIdentityKey(self, request, context):
        logging.debug("GETIDENTITYKEY request received")
        logging.debug("Username: " + request.username)

        username = request.username
        user_id = self.userManager.getUserId(username)
        if user_id == -1:
            logging.debug("GETIDENTITYKEY FAILED")
            return pb2.GetIdentityKeyResponse(identity_key=b"")

        identity_key = self.identityKeyManager.getKey(user_id)
        if identity_key == "":
            logging.debug("GETIDENTITYKEY FAILED")
            return pb2.GetIdentityKeyResponse(identity_key=b"")

        logging.debug("GETIDENTITYKEY success")
        return pb2.GetIdentityKeyResponse(identity_key=identity_key)

    def trySetSalt(self, request, context):
        logging.debug("TRYSETSALT request received")
        logging.debug("Username: " + request.username)

        username = self.sessionManager.getUser(request.token)
        partner = request.partner
        received_salt = request.salt
        if username == "" or not self.userManager.existingUser(partner):
            logging.debug("TRYSETSALT FAILED")
            return pb2.TrySetSaltResponse(salt=received_salt)
        if username == partner:
            # cant chat with yourself
            logging.debug("TRYSETSALT FAILED")
            return pb2.SendResponse(success=False, timestamp=-1)

        user_id = self.userManager.getUserId(username)
        partner_id = self.userManager.getUserId(partner)
        salt = self.chatSaltManager.trySetSalt(user_id, partner_id, received_salt)

        if salt == received_salt:
            logging.debug("New salt")
        else:
            logging.debug("Salt already existed for this chat")

        return pb2.TrySetSaltResponse(salt=salt)
