class IdentityKeyManager:
    def __init__(self, db):
        self.db = db

    def registerKey(self, user_id, key):
        previous_key = self.getKey(user_id)
        if previous_key == key:
            # same key already registered
            return True
        elif previous_key != "":
            # different key already registered
            return False

        query = """INSERT INTO identity_keys (user_id, identity_key)
        VALUES (%s, %s)"""
        self.db.execute_query(query, (user_id, key))
        return True

    def getKey(self, user_id):
        query = """SELECT identity_key FROM identity_keys
        WHERE user_id = %s"""
        result = self.db.fetch_one(query, (user_id,))
        if result is None:
            return ""
        return result[0].tobytes()
