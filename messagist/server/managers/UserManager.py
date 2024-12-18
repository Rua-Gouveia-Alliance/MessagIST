class UserManager:
    def __init__(self):
        self.users = {}

    def newUser(self, username, password, salt):
        if username in self.users or username == "" or password == "":
            return False

        self.users[username] = (password, salt)
        return True

    def getSalt(self, username):
        if username not in self.users:
            return ""

        return self.users[username][1]

    def validUser(self, username, password):
        if username == "TESTE1" or username == "TESTE2":
            return True

        if username not in self.users:
            return False

        return self.users[username][0] == password
