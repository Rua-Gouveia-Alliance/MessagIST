class UserManager:
    def __init__(self, db):
        self.db = db

    def newUser(self, username, password, salt, key):
        if username == "" or password == "":
            return False

        query = "INSERT INTO users (ist_username, password_hash, salt) VALUES (%s, %s, %s)"
        self.db.query(
            query,
            (
                username,
                password,
                salt,
            ),
        )

        userId = self.getUserId(username)
        query = """INSERT INTO identity_keys (user_id, identity_key)
        VALUES (%s, %s)"""
        self.db.query(query, (userId, key))

        if not self.db.commit():
            self.db.rollback()
            return False

        return True

    def getSalt(self, username):
        query = "SELECT salt FROM users WHERE ist_username = %s"
        result = self.db.fetch_one(query, (username,))
        if result:
            return result[0]
        else:
            return b""

    def validUser(self, username, password):
        query = "SELECT password_hash FROM users WHERE ist_username = %s"
        result = self.db.fetch_one(query, (username,))
        if result:
            return result[0] == password
        return False

    def existingUser(self, username):
        # Check if the user exists in the database
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE ist_username = %s)"
        result = self.db.fetch_one(query, (username,))
        if result:
            return result[0]
        return False

    def getUserKey(self, username):
        userId = self.getUserId(username)
        if userId == -1:
            return ""

        query = """SELECT identity_key FROM identity_keys
        WHERE user_id = %s"""
        result = self.db.fetch_one(query, (userId,))
        if not result:
            return ""
        return result[0]

    def getUserId(self, username):
        # Check if the user exists in the database
        query = "SELECT id FROM users WHERE ist_username = %s"
        result = self.db.fetch_one(query, (username,))
        if result:
            return result[0]
        return -1
