import sys
import threading
import time

sys.path.insert(1, "../contract/target/")
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2
from managers.Chat import Chat


class ChatManager:
    def __init__(self, ctx):
        self.ctx = ctx
        self.chats = {}
        self.update_interval = 2
        self.stopped = True
        self.chat_update_thread = threading.Thread(
            group=None, target=self.updateLoop, args=(lambda x: self.stopped,)
        )

    def startChat(self, partner):
        self.ctx.logger.debug("Starting a new chat with " + partner)

        if partner in self.chats:
            self.ctx.logger.debug("Failed")
            return False

        self.chats[partner] = Chat()
        self.ctx.logger.debug("Success")
        return True

    def sendMessage(self, msg, partner):
        self.ctx.logger.debug("Sending a message to " + partner)

        if partner not in self.chats:
            self.startChat(partner)

        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.SendRequest(
            message=msg, username=self.ctx.username, partner=partner
        )
        response = stub.send(request)
        self.chats[partner].append(msg, response.timestamp)

    def getMessage(self, partner, timestamp):
        self.ctx.logger.debug(
            "Checking if there is a message from "
            + partner
            + " at timestamp "
            + str(timestamp)
        )

        if partner not in self.chats:
            return ""

        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.ReceiveRequest(
            timestamp=timestamp, username=self.ctx.username, partner=partner
        )
        response = stub.receive(request)
        return response.message

    def updateState(self):
        self.ctx.logger.debug("Checking chats for updates")

        for partner, chat in self.chats.items():
            self.ctx.logger.debug("Trying to update chat with " + partner)
            timestamp = chat.timestamp
            message = self.getMessage(partner, timestamp)
            if message != "":
                self.ctx.logger.debug("Update succeded")
                chat.append(message, timestamp)

    def updateLoop(self, stop):
        while not stop():
            self.updateState()
            time.sleep(self.update_interval)

    def start(self):
        self.stopped = False
        if not self.chat_update_thread.is_alive():
            self.chat_update_thread.start()

    def logout(self):
        if not self.ctx.activeSession:
            return False

        self.chats = {}
        self.stopped = True
        self.chat_update_thread.join()
        self.chat_update_thread = threading.Thread(
            group=None, target=self.updateLoop, args=(lambda x: self.stopped,)
        )
