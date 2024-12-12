from managers.Session import Session


class SessionManager:
    def __init__(self):
        self.LEASE_TIME = 5000  # 5000ms, 5s
        self.sessions = {}

    def startSession(self, username):
        if username in self.sessions:
            return ""

        self.sessions[username] = Session(self, username)
        return self.sessions[username].token

    def endSession(self, username):
        if username not in self.sessions:
            return False

        self.sessions[username].timer.deleteLater()
        del self.sessions[username]
        return True

    def validSession(self, username, token):
        return username in self.sessions and self.sessions[username].validate(token)

    def getUser(self, token):
        for username, session in self.sessions.items():
            if session.validate(token):
                return username
        return ""
