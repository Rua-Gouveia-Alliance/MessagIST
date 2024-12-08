class UserManager:
    def __init__(self):
        self.users = {}

    def newUser(self, username, password):
        if username in self.users:
            return False

        self.users[username] = password
        return True

    def validUser(self, username, password):
        if username not in self.users:
            return False

        return self.users[username] == password
