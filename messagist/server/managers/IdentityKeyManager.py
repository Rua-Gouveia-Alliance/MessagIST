class IdentityKeyManager:
    def __init__(self, db):
        self.db = db

    def registerKey(self, username, key):
        previous_key = self.getKey(username)
        if previous_key == key:
            # same key already registered
            return True
        elif previous_key != "":
            # different key already registered
            return False

        query = """INSERT INTO identity_keys (username, identity_key)
        VALUES (%s, %s)"""
        self.db.execute_query(query, (username, key))
        return True

    def getKey(self, username):
        query = """SELECT identity_key FROM identity_keys
        WHERE username = %s"""

        result = self.db.fetch_one(query, (username,))
        if result is None:
            return ""
        return result[0]
