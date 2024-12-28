import logging


class ChatManager:
    def __init__(self, db):
        self.chats = {"TESTE1": {}, "TESTE2": {}}
        self.db = db

    # TODO: Arede tira os comentarios que nao sao precisos
    def startChat(self, user1, user2):
        query = """
        SELECT COUNT(*) FROM chat
        WHERE user_1 = %s AND user_2 = %s
        """
        user1 = user1.strip()
        user2 = user2.strip()

        user_1_query = "SELECT id FROM users WHERE username = %s"
        user_2_query = "SELECT id FROM users WHERE username = %s"

        user_id_1 = self.db.fetch_one(user_1_query, (user1,))
        user_id_2 = self.db.fetch_one(user_2_query, (user2,))

        user_id_1 = user_id_1[0]
        user_id_2 = user_id_2[0]
        if not (user_id_1 > 0 and user_id_2 > 0):
            return False

        user_id_1, user_id_2 = min(user_id_1, user_id_2), max(user_id_1, user_id_2)

        result = self.db.fetch_one(
            query,
            (
                user_id_1,
                user_id_2,
            ),
        )

        if result and result[0] > 0:
            return False

        insert_query = """
        INSERT INTO chat (user_1, user_2)
        VALUES (%s, %s)
        """

        self.db.execute_query(
            insert_query,
            (
                user_id_1,
                user_id_2,
            ),
        )
        self.chats[user1][user2] = []
        self.chats[user2][user1] = []
        return True

    def sendMessage(self, user1, user2, msg):
        user1 = user1.strip()
        user2 = user2.strip()
        user_1_query = "SELECT id FROM users WHERE username = %s"
        user_2_query = "SELECT id FROM users WHERE username = %s"

        user_id_1 = self.db.fetch_one(user_1_query, (user1,))
        user_id_2 = self.db.fetch_one(user_2_query, (user2,))

        user_id_1 = user_id_1[0]
        user_id_2 = user_id_2[0]

        print(user_id_1)

        query = """SELECT *
        FROM chat
        WHERE (user_1 = %s AND user_2 = %s)
        OR (user_1 = %s AND user_2 = %s)"""

        chat_id = self.db.fetch_one(
            query,
            (
                user_id_1,
                user_id_2,
                user_id_2,
                user_id_1,
            ),
        )

        if chat_id:
            return -1

        insert_query = "INSERT INTO messages (chat_id, message_text) VALUES (%s)"

        self.db.execute_query(insert_query, (chat_id, msg))
        # self.chats[user1][user2].append(msg)
        # self.chats[user2][user1].append(msg)

        # TODO: Calcular o numero de mensagens enviadas no chat em questao e retornar esse numero menos 1.
        return len(self.chats[user1][user2]) - 1

    def getMessage(self, user1, user2, index):
        query = """
        SELECT m.message_text
        FROM messages m
        JOIN chat c ON m.chat_id = c.chat_id
        JOIN users u1 ON c.user_1 = u1.id
        JOIN users u2 ON c.user_2 = u2.id
        WHERE (u1.username = %s AND u2.username = %s) OR (u1.username = %s AND u2.username = %s)
        ORDER BY m.created_at
        LIMIT 1 OFFSET %s;
        """

        result = self.db.fetch_one(
            query,
            (
                user1,
                user2,
                user2,
                user1,
                index,
            ),
        )

        if result:
            return result[0]
        else:
            logging.debug(
                f"Message at index {index} not found for chat between {user1} and {user2}"
            )
            return ""
        """if user1 not in self.chats[user2] or user2 not in self.chats[user1]:
            logging.debug("Chat of " + user1 + " with " + user2 + " not found")
            return ""

        if index > len(self.chats[user1][user2]) - 1 or index < 0:
            logging.debug("Index " + str(index) + " is not a valid index")
            return ""

        return self.chats[user1][user2][index]"""

    def getPartners(self, username):
        query = """
        SELECT DISTINCT
            CASE
                WHEN c.user_1 = u1.id THEN u2.username
                ELSE u1.username
            END AS chat_partner
        FROM chat c
        JOIN users u1 ON c.user_1 = u1.id
        JOIN users u2 ON c.user_2 = u2.id
        WHERE u1.username = %s OR u2.username = %s;
        """

        result = self.db.fetch_one(query, (username))

        chat_partners = [row[0] for row in result]

        return chat_partners
        # if username not in self.chats:
        # return []
        # return self.chats[username].keys()
