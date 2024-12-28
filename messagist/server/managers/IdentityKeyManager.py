class IdentityKeyManager:
    def __init__(self, db):
        self.db = db

    def registerKey(self, username, key, usermgr):
        previous_key = self.getKey(username, usermgr)
        if previous_key == key:
            # same key already registered
            return True
        elif previous_key != "":
            # different key already registered
            return False

        user_id = usermgr.getUserId(username)

        query = """INSERT INTO identity_keys (user_id, identity_key)
        VALUES (%s, %s)"""
        self.db.execute_query(query, (user_id, key))
        return True

    def getKey(self, username, usermgr):
        user_id = usermgr.getUserId(username)

        query = """SELECT identity_key FROM identity_keys
        WHERE user_id = %s"""
        result = self.db.fetch_one(query, (user_id,))
        if result is None:
            return ""
        return result[0].tobytes()
