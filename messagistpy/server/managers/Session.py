import secrets


class Session:
    def __init__(self, manager, username):
        self.manager = manager
        self.token = secrets.token_urlsafe(64)
        self.username = secrets.token_urlsafe(64)
        # self.timer = QTimer(parent=self, singleShot=True, timeout=self.logout)
        # self.logoutTimer.start(self.LEASE_TIME)

    def validate(self, token):
        return self.token == token

    def renewLease(self):
        # self.logoutTimer.start(self.LEASE_TIME)
        return

    def endSession(self):
        self.manager.endSession(self.username)
