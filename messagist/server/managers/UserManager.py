class UserManager:
    def __init__(self, db):
        self.db = db

    def newUser(self, username, password, salt):
        # is this in database

        query = "SELECT COUNT(1) FROM users WHERE username = %s"

        result = self.db.fetch_one(query, (username,))

        if result[0] > 0 or username == "" or password == "":
            return False

        insert_query = (
            "INSERT INTO users (username, password_hash, salt) VALUES (%s, %s, %s)"
        )
        self.db.execute_query(
            insert_query,
            (
                username,
                password,
                salt,
            ),
        )

        return True

    def getSalt(self, username):
        query = "SELECT salt FROM users WHERE username = %s"
        result = self.db.fetch_one(query, (username,))
        if result:
            return result[0].tobytes()
        else:
            return b""

    def validUser(self, username, password):
        query = "SELECT password_hash FROM users WHERE username = %s"
        result = self.db.fetch_one(query, (username,))
        if result:
            return result[0].tobytes() == password
        return False

    def existingUser(self, username):
        # Check if the user exists in the database
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE username = %s)"
        result = self.db.fetch_one(query, (username,))
        return result[0] if result else False
