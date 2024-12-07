import threading


class Chat:
    def __init__(self, user, partner):
        self.messages = []
        self.bufferedMessages = []
        self.timestamp = 0
        self.user = user
        self.partner = partner
        self.lock = threading.Lock()

    def __str__(self):
        self.lock.acquire()
        string = f"Chat members: {self.user}, {self.partner}"
        for msg in self.messages:
            string += "\n" + msg
        self.lock.release()
        return string

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
