import json
from datetime import datetime, timezone


class Chat:
    def __init__(self, username, partner):
        self.username = username
        self.partner = partner
        self.messages = []
        self.bufferedMessages = []
        self.timestamp = 0

    def createMessage(self, message):
        message = {
            "sender_istid": self.username,
            "receiver_istid": self.partner,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "content": message,
        }
        message = json.dumps(message, indent=4)
        # message = MessagISTCrypto.protect(message)
        return message

    def getMessages(self):
        messages = []
        for message in self.messages:
            messages.append(json.loads(message))
        return messages

    def append(self, msg, ts):
        if ts == self.timestamp:
            self.messages.append(msg)
            self.timestamp += 1
            while (
                len(self.bufferedMessages) != 0
                and self.bufferedMessages[0][0] == self.timestamp
            ):
                msg = self.bufferedMessages.pop(0)[1]
                self.messages.append(msg)
                self.timestamp += 1
        elif ts > self.timestamp:
            if (ts, msg) not in self.bufferedMessages:
                self.bufferedMessages.append((ts, msg))
                self.bufferedMessages.sort()
