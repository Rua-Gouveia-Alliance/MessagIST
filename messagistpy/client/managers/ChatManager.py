import sys

sys.path.insert(1, "../contract/target/")
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2
from managers.Chat import Chat


class ChatManager:
    def __init__(self, ctx):
        self.ctx = ctx
        self.chats = {}

    def startChat(self, partner):
        self.ctx.logger.debug("Starting a new chat with " + partner)

        # TODO: Verificar se este partner efetivamente existe no server (i.e.
        # estamos a tentar contactar uma conta que existe mm)
        if partner in self.chats:
            self.ctx.logger.debug("Failed")
            return False

        self.chats[partner] = Chat()
        self.ctx.chatsChanged.emit()
        self.ctx.logger.debug("Success")
        return True

    def sendMessage(self, msg, partner):
        self.ctx.logger.debug("Sending a message to " + partner)

        if partner not in self.chats:
            self.startChat(partner)

        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.SendRequest(
            token=self.ctx.sessionToken, message=msg, partner=partner
        )
        response = stub.send(request)
        self.chats[partner].append(msg, response.timestamp)
        self.ctx.chatsChanged.emit()

    def logout(self):
        self.ctx.logger.debug("Logging out chat manager")
        if not self.ctx.activeSession:
            self.ctx.logger.debug("Logging out chat manager FAILED")
            return False
        self.chats = {}

    def updateState(self, partners, messages):
        for i, message in enumerate(messages):
            if messages[i] != "":
                self.ctx.logger.debug("New message from: " + partners[i])
                if partners[i] not in self.chats:
                    self.ctx.logger.debug("Discovered new partner: " + partners[i])
                    self.chats[partners[i]] = Chat()
                self.chats[partners[i]].append(
                    message, self.chats[partners[i]].timestamp
                )

        self.ctx.chatsChanged.emit()
