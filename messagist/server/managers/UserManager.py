class UserManager:
    def __init__(self, db):
        self.users = {}
        self.db = db

    def newUser(self, username, password, salt):
        # is this in database

        query = "SELECT COUNT(1) FROM users WHERE username = %s"

        result = self.db.fetch_one(query, (username,))
        print(result)
        print(result[0][0])

        # cur.execute(query, (username,))
        # user_exists = cursor.fetchone()[0]
        # if username in self.users or username == "" or password == "":
        # return False

        if result[0][0] > 0 or username == "" or password == "":
            return False
        # self.users[username] = (password, salt)

        insert_query = (
            "INSERT INTO users (username, password_hash, salt) VALUES (%s, %s, %s)"
        )
        self.db.execute_query(insert_query, (username, password, salt))
        print("TESTE")

        return True

    def getSalt(self, username):
        query = "SELECT salt FROM users WHERE username = %s"
        result = self.db.fetch_one(query, (username,))
        if result:
            return result[0][0].tobytes()
        else:
            return b""
        # if username not in self.users:
        # return ""

        # return self.users[username][1]

    def validUser(self, username, password):
        query = "SELECT password_hash FROM users WHERE username = %s"
        result = self.db.fetch_one(query, (username,))
        print(result)
        if result:
            print(result[0][0].tobytes())
            print(password)
            return result[0][0].tobytes() == password
        return False
        # if username not in self.users:
        # return False

        # return self.users[username][0] == password

    def existingUser(self, username):
        # Check if the user exists in the database
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE username = %s)"
        result = self.db.fetch_one(query, (username,))
        return result[0] if result else False
