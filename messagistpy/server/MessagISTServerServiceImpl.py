import sys
import logging

sys.path.insert(1, "../contract/target/")
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2
from ChatManager import ChatManager


class MessagISTServerServiceImpl(pb2_grpc.MessagISTServerServicer):
    def __init__(self, *args, **kwargs):
        self.chatManager = ChatManager()

    def send(self, request, context):
        logging.debug("SEND request received.")
        logging.debug("Message: " + request.message)
        user = request.user
        partner = request.partner

        self.chatManager.startChat(user, partner)
        ts = self.chatManager.sendMessage(user, partner, request.message)
        response = pb2.SendResponse()
        response.timestamp = ts
        return response

    def receive(self, request, context):
        logging.debug("RECEIVE request received.")
        logging.debug("Timestamp: " + str(request.timestamp))

        user = request.user
        partner = request.partner

        ts = request.timestamp
        response = pb2.ReceiveResponse()
        response.message = self.chatManager.getMessage(user, partner, ts)
        return response
