class ChatSaltManager:
    def __init__(self, db):
        self.db = db

    def querySalt(self, username, partner):
        query = """SELECT salt FROM chat_salts
        WHERE user_1 = %s AND user_2 = %s"""

        params = (username, partner) if username < partner else (partner, username)
        result = self.db.fetch_one(query, params)

        if result is None:
            return ""
        return result[0].tobytes()

    def registerSalt(self, username, partner, salt):
        query = """INSERT INTO chat_salts (user_1, user_2, salt)
        VALUES (%s, %s, %s)"""

        params = (
            (username, partner, salt)
            if username < partner
            else (partner, username, salt)
        )
        self.db.execute_query(query, params)

    def trySetSalt(self, username, partner, salt):
        old_salt = self.querySalt(username, partner)
        if old_salt == "":
            self.registerSalt(username, partner, salt)
            return salt
        return old_salt
