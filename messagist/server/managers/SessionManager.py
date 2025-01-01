import threading
import logging

from managers.Session import Session


class SessionManager:
    def __init__(self):
        self.LEASE_TIME = 5  # 5s
        self.sessions = {}
        self.lock = threading.Lock()

    def startSession(self, username):
        self.lock.acquire()

        token = ""
        if username not in self.sessions:
            self.sessions[username] = Session(self, username)
            token = self.sessions[username].token

        self.lock.release()
        return token

    def endSession(self, username):
        self.lock.acquire()

        status = False
        if username in self.sessions:
            del self.sessions[username]
            logging.debug(username + "'s session expired")
            status = True

        self.lock.release()
        return status

    def validSession(self, username, token):
        self.lock.acquire()
        status = username in self.sessions and self.sessions[username].validate(token)
        self.lock.release()
        return status

    def getUser(self, token):
        self.lock.acquire()

        result = ""
        for username, session in self.sessions.items():
            if session.validate(token):
                result = username
                break

        self.lock.release()
        return result

    def renewLease(self, username):
        self.lock.acquire()

        status = False
        if username in self.sessions:
            self.sessions[username].renewLease()
            status = True
            logging.debug(username + "'s lease renewed")

        self.lock.release()
        return status
