class UserManager:
    def __init__(self):
        self.users = {}

    def newUser(self, username, password, salt):
        # is this in database
        # query = "SELECT EXISTS(SELECT 1 FROM users WHERE username = ?)"

        # cur.execute(query, (username,))
        # user_exists = cursor.fetchone()[0]
        if username in self.users or username == "" or password == "":
            return False
        # if user_exists or username == "" or password == "":
        # return False
        # INSERT NA TABELA O NOVO UTILIZADOR
        self.users[username] = (password, salt)

        return True

    def getSalt(self, username):
        if username not in self.users:
            return ""

        return self.users[username][1]

    def validUser(self, username, password):
        # query = "SELECT EXISTS(SELECT 1 FROM users WHERE username = ?)"
        # cur.execute(query, (username,))
        # user_exists = cursor.fetchone()[0]
        # row = cursor.fetchone()
        if username not in self.users:
            return False
        # if row:
        # password_table = row[2]
        # return password_table == password
        # else :
        # return False
        return self.users[username][0] == password
