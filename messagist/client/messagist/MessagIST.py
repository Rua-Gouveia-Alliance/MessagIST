from PySide6.QtCore import QObject, Slot, Property, Signal, QTimer
from managers.ChatManager import ChatManager
from managers.SessionManager import SessionManager
from messagist.MessagISTContext import MessagISTContext


# TODO: Forçar logout quando há erros.
class MessagIST(QObject):
    chatsChanged = Signal()
    loggedOut = Signal()

    def __init__(self, debug, host, port):
        QObject.__init__(self)
        self.LEASE_TIME = 5000  # 5000ms, 5s
        self.ctx = MessagISTContext(debug, host, port)
        self.ctx.setChatsChanged(self.chatsChanged)
        self.sessionManager = SessionManager(self.ctx)
        self.chatManager = ChatManager(self.ctx)

    @Slot(str, str, result="QVariant")
    def signup(self, username, password):
        self.ctx.logger.debug("Signing up")
        result = self.sessionManager.signup(username, password)
        return result

    @Slot(str, str, result="QVariant")
    def login(self, username, password):
        self.ctx.logger.debug("Logging in")
        if self.ctx.activeSession:
            return {"success": False, "error": "Session already active"}

        result = self.sessionManager.login(username, password)
        if result["success"]:
            self.ctx.logger.debug("Starting session related timers")
            self.logoutTimer = QTimer(parent=self, singleShot=True, timeout=self.logout)
            self.keepAliveTimer = QTimer(parent=self, timeout=self.keepAlive)
            self.logoutTimer.start(self.LEASE_TIME)
            self.keepAliveTimer.start(self.LEASE_TIME / 2)
            if self.ctx.identityKey is None:
                self.ctx.logger.debug("Identity key needs to be recovered")
                result["recovery"] = True
        return result

    @Slot(str, result=bool)
    def logout(self, password):
        self.ctx.logger.debug("Logging out")
        if not self.ctx.activeSession:
            return False

        success = self.chatManager.logout() and self.sessionManager.logout(password)
        self.ctx.logger.debug("Logout " + ("successful" if success else "FAILED"))
        # TODO: Close app if logout not successful?
        self.ctx.logger.debug("Deleting session related timers")
        self.keepAliveTimer.deleteLater()
        self.logoutTimer.deleteLater()
        self.ctx.logger.debug("Emiting loggedOut signal")
        self.loggedOut.emit()
        return success

    @Slot(str, str, result=bool)
    def sendMessage(self, msg, partner):
        self.ctx.logger.debug("Sending a message to " + partner)
        return self.chatManager.sendMessage(msg, partner)

    @Slot(str, result=bool)
    def startChat(self, partner):
        self.ctx.logger.debug("Starting a new chat with " + partner)
        return self.chatManager.startChat(partner)

    @Slot(str, str, result=bool)
    def setChatPassphrase(self, partner, passphrase):
        self.ctx.logger.debug("Setting the passphrase to the chat with " + partner)
        return self.chatManager.setChatPassphrase(partner, passphrase)

    @Slot(str, str, result=bool)
    def recoverIdentityKey(self, wordList, password):
        self.ctx.logger.debug("Recovering the key for user " + self.ctx.username)
        return self.sessionManager.recoverIdentityKey(wordList, password)

    @Slot()
    def keepAlive(self):
        self.ctx.logger.debug("Perfoming KeepAlive")
        partners = []
        timestamps = []
        for partner, chat in self.chatManager.chats.items():
            if not chat.pending:
                partners.append(partner)
                timestamps.append(chat.timestamp)

        success, partners, messages = self.sessionManager.keepAlive(
            partners, timestamps
        )
        if not success:
            self.ctx.logger.debug("KeepAlive not successful")
            self.logout()
            return
        self.ctx.logger.debug("KeepAlive successful")
        self.chatManager.updateState(partners, messages)
        self.logoutTimer.start(self.LEASE_TIME)  # Reseting the timer

    def getChats(self):
        chats = {}
        for partner in self.chatManager.chats:
            chats[partner] = self.chatManager.chats[partner].getMessages()
        return chats

    chats = Property(type="QVariant", fget=getChats, notify=chatsChanged)
