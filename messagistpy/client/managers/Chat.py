import threading


class Chat:
    def __init__(self):
        self.messages = []
        self.bufferedMessages = []
        self.timestamp = 0
        self.lock = threading.Lock()

    def getMessages(self):
        self.lock.acquire()
        messages = []
        for message in self.messages:
            messages.append(message)
        self.lock.release()
        return messages

    def append(self, msg, ts):
        self.lock.acquire()
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
        self.lock.release()
