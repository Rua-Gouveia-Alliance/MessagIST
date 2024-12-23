import logging


class ChatManager:
    def __init__(self, db):
        self.chats = {"TESTE1": {}, "TESTE2": {}}
        self.db = db

    # TODO: Terrible solution to store chats but this will be replaced by a real database
    def startChat(self, user1, user2):
        query = """
        SELECT COUNT(*) FROM chat 
        WHERE user_1 = LEAST(%s, %s) AND user_2 = GREATEST(%s, %s)
        """


        user_1, user_2 = min(user_1, user_2), max(user_1, user_2)

        result = self.db.fetch_one(query, (user1,user2,))

        if result and result[0][0] > 0:
            return False
        insert_query = (
            "INSERT INTO users (user_1, user_2) VALUES (%s, %s)"
        )
        self.db.execute_query(insert_query,(user1,user2,))
        #self.chats[user1][user2] = []
        #self.chats[user2][user1] = []
        return True

    def sendMessage(self, user1, user2, msg):
        
        query = "SELECT chat_id FROM chat WHERE user_1 = LEAST(%s, %s) AND user_2 = GREATEST(%s, %s)"


        result = self.db.fetch_one(query, (user1,user2,))

        if result:
            return -1
        
        chat_id = result[0]

        insert_query = "INSERT INTO messages (chat_id, message_text) VALUES (%s)"

        self.db.execute_query(insert_query, (chat_id, msg))
        #self.chats[user1][user2].append(msg)
        #self.chats[user2][user1].append(msg)

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
