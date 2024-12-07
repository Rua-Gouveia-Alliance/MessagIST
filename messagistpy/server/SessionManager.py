import secrets

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def startSession(self, username):
        if self.sessions[username] is not None:
            return ""

        token = secrets.token_urlsafe(64)
        self.sessions[username] = token
        return token

    def endSession(self, username):
        if self.sessions[username] is None:
            return False

        del self.sessions[username]
        return True

    def validSession(self, username, token):
        return self.chat[username] == token
