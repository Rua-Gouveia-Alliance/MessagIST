import logging

class ChatManager:
    def __init__(self):
        self.chats = {}

    def startChat(self, user1, user2):
        chatid = user1 + user2 if user1 > user2 else user2 + user1
        if chatid in self.chats:
            return False

        self.chats[chatid] = []
        return True

    def sendMessage(self, user1, user2, msg):
        chatid = user1 + user2 if user1 > user2 else user2 + user1
        if chatid not in self.chats:
            return -1

        self.chats[chatid].append(msg)
        return len(self.chats[chatid]) - 1

    def getMessage(self, user1, user2, index):
        chatid = user1 + user2 if user1 > user2 else user2 + user1
        if chatid not in self.chats:
            logging.debug("Chat id " + chatid + " not found")
            return ""

        if index > len(self.chats[chatid]) - 1 or index < 0:
            logging.debug("Index " + str(index) + " is not a valid index")
            return ""

        return self.chats[chatid][index]
