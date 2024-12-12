import logging


class ChatManager:
    def __init__(self):
        self.chats = {"TESTE1": {}, "TESTE2": {}}

    # TODO: Unnecessary once we have an actual database (i think)
    def initUser(self, username):
        self.chats[username] = {}

    # TODO: Terrible solution to store chats but this will be replaced by a real database
    def startChat(self, user1, user2):
        if user1 in self.chats[user2] or user2 in self.chats[user1]:
            return False

        self.chats[user1][user2] = []
        self.chats[user2][user1] = []
        return True

    def sendMessage(self, user1, user2, msg):
        if user1 not in self.chats[user2] or user2 not in self.chats[user1]:
            return -1

        self.chats[user1][user2].append(msg)
        self.chats[user2][user1].append(msg)
        return len(self.chats[user1][user2]) - 1

    def getMessage(self, user1, user2, index):
        if user1 not in self.chats[user2] or user2 not in self.chats[user1]:
            logging.debug("Chat of " + user1 + " with " + user2 + " not found")
            return ""

        if index > len(self.chats[user1][user2]) - 1 or index < 0:
            logging.debug("Index " + str(index) + " is not a valid index")
            return ""

        return self.chats[user1][user2][index]

    def getPartners(self, username):
        if username not in self.chats:
            return []
        return self.chats[username].keys()
