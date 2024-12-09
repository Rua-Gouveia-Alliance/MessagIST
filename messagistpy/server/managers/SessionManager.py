import secrets
from managers.Session import Session


class SessionManager:
    def __init__(self):
        self.sessions = {}

    def startSession(self, username):
        if username in self.sessions:
            return ""

        token = secrets.token_urlsafe(64)
        self.sessions[username] = Session(token)
        return token

    def endSession(self, username):
        if username not in self.sessions:
            return False

        del self.sessions[username]
        return True

    def validSession(self, username, token):
        return self.chat[username] == token
