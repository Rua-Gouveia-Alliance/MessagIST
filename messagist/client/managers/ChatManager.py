from managers.Chat import Chat
import MessagISTCrypto
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2


class ChatManager:
    def __init__(self, ctx):
        self.ctx = ctx
        self.chats = {}

    def startChat(self, partner):
        self.ctx.logger.debug("Starting a new chat with " + partner)

        if partner in self.chats:
            self.ctx.logger.debug("Failed")
            return False

        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.GetIdentityKeyRequest(username=partner)
        response = stub.getIdentityKey(request)

        if response.identityKey == "":
            self.ctx.logger.debug("Failed to get partner identityKey (doesnt exist)")
            return False

        self.chats[partner] = Chat(self.ctx, partner, response.identityKey)
        self.ctx.chatsChanged.emit()
        self.ctx.logger.debug("Success")
        return True

    def sendMessage(self, message, partner):
        if partner not in self.chats:
            return False

        self.chats[partner].send(message)
        self.ctx.chatsChanged.emit()

        return True

    def setChatPassphrase(self, partner, passphrase):
        if partner not in self.chats:
            return False

        if not self.chats[partner].setPassphrase(passphrase):
            del self.chats[partner]
            return False

        self.ctx.chatsChanged.emit()
        return True

    def logout(self):
        self.ctx.logger.debug("Logging out chat manager")
        if not self.ctx.activeSession:
            self.ctx.logger.debug("Logging out chat manager FAILED")
            return False
        self.chats = {}
        self.ctx.chatsChanged.emit()
        return True

    def updateState(self, partners, messages):
        for i, message in enumerate(messages):
            if messages[i] != "":
                self.ctx.logger.debug("New message from: " + partners[i])
                if partners[i] not in self.chats:
                    self.ctx.logger.debug("Discovered new partner: " + partners[i])
                    self.chats[partners[i]] = Chat(self.ctx, partners[i])
                self.chats[partners[i]].append(
                    message, self.chats[partners[i]].timestamp
                )

        self.ctx.chatsChanged.emit()
