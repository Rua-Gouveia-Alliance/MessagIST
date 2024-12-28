import logging


class ChatManager:
    def __init__(self, db):
        self.db = db

    # TODO: Arede tira os comentarios que nao sao precisos
    def startChat(self, user_id_1, user_id_2):
        user_id_1, user_id_2 = min(user_id_1, user_id_2), max(user_id_1, user_id_2)

        query = """
        SELECT COUNT(*) FROM chat
        WHERE user_1 = %s AND user_2 = %s
        """
        result = self.db.fetch_one(
            query,
            (
                user_id_1,
                user_id_2,
            ),
        )

        if result and result[0] > 0:
            return False  # chat already exists

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
        return True

    def sendMessage(self, user_id_1, user_id_2, msg):
        user_id_1, user_id_2 = min(user_id_1, user_id_2), max(user_id_1, user_id_2)

        query = """
        SELECT chat_id FROM chat
        WHERE user_1 = %s AND user_2 = %s
        """
        result = self.db.fetch_one(
            query,
            (
                user_id_1,
                user_id_2,
            ),
        )
        chat_id = result[0]
        if chat_id:
            return -1

        insert_query = "INSERT INTO messages (chat_id, message_text) VALUES (%s)"
        self.db.execute_query(insert_query, (chat_id, msg))

        return self.getChatLen(chat_id) - 1

    def getChatLen(self, chat_id):
        query = """
        SELECT COUNT(*)
        FROM messages
        WHERE chat_id = %s"""
        result = self.db.fetch_one(query, (chat_id,))
        if result:
            return result[0]
        return 0

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
