import secrets
import threading


class Session:
    def __init__(self, manager, username):
        self.manager = manager
        self.token = secrets.token_urlsafe(64)
        self.username = username
        self.logoutTimer = threading.Timer(self.manager.LEASE_TIME, self.endSession)
        self.logoutTimer.start()

    def validate(self, token):
        return self.token == token

    def renewLease(self):
        self.logoutTimer.cancel()
        self.logoutTimer.join()
        del self.logoutTimer
        self.logoutTimer = threading.Timer(self.manager.LEASE_TIME, self.endSession)
        self.logoutTimer.start()

    def endSession(self):
        self.manager.endSession(self.username)
