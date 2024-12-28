class ChatSaltManager:
    def __init__(self, db):
        self.db = db

    def querySalt(self, user_id, partner_id):
        query = """SELECT salt FROM chat_salts
        WHERE user_1 = %s AND user_2 = %s"""

        params = (
            (user_id, partner_id) if user_id < partner_id else (partner_id, user_id)
        )
        result = self.db.fetch_one(query, params)

        if result is None:
            return ""
        return result[0].tobytes()

    def registerSalt(self, user_id, partner_id, salt):
        query = """INSERT INTO chat_salts (user_1, user_2, salt)
        VALUES (%s, %s, %s)"""

        params = (
            (user_id, partner_id, salt)
            if user_id < partner_id
            else (partner_id, user_id, salt)
        )
        self.db.execute_query(query, params)

    def trySetSalt(self, user_id, partner_id, salt):
        old_salt = self.querySalt(user_id, partner_id)
        if old_salt == "":
            self.registerSalt(user_id, partner_id, salt)
            return salt
        return old_salt
