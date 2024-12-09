import sys
import logging

sys.path.insert(1, "../contract/target/")
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2
from managers.ChatManager import ChatManager
from managers.SessionManager import SessionManager
from managers.UserManager import UserManager


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

        response = pb2.SignupResponse()
        response.success = self.userManager.newUser(username, password)
        return response

    def login(self, request, context):
        logging.debug("LOGIN request received.")
        logging.debug("Username: " + request.username)

        username = request.username
        password = request.password

        response = pb2.LoginResponse()
        if self.userManager.validUser(username, password):
            response.token = self.sessionManager.startSession(username)
            response.success = response.token != ""
        else:
            response.token = ""
            response.success = False
        return response

    def send(self, request, context):
        logging.debug("SEND request received.")
        logging.debug("Message: " + request.message)

        username = request.username
        partner = request.partner

        self.chatManager.startChat(username, partner)
        ts = self.chatManager.sendMessage(username, partner, request.message)
        response = pb2.SendResponse()
        response.timestamp = ts
        return response

    def receive(self, request, context):
        logging.debug("RECEIVE request received.")
        logging.debug("Timestamp: " + str(request.timestamp))

        username = request.username
        partner = request.partner
        ts = request.timestamp

        response = pb2.ReceiveResponse()
        response.message = self.chatManager.getMessage(username, partner, ts)
        return response
