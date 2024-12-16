from PySide6.QtCore import QObject, Slot, Property, Signal, QTimer
from managers.ChatManager import ChatManager
from managers.SessionManager import SessionManager
from messagist.MessagISTContext import MessagISTContext


# TODO: Forçar logout quando há erros. Arranjar maneira de ligar um signal de
# logout ao qml, que faz voltar ao ecra inicial.
class MessagIST(QObject):
    chatsChanged = Signal()
    loggedOut = Signal()

    def __init__(self, debug, port):
        QObject.__init__(self)
        self.LEASE_TIME = 5000  # 5000ms, 5s
        self.ctx = MessagISTContext(debug, port)
        self.ctx.setChatsChanged(self.chatsChanged)
        self.sessionManager = SessionManager(self.ctx)
        self.chatManager = ChatManager(self.ctx)

    @Slot(str, str, result=bool)
    def signup(self, username, password):
        self.ctx.logger.debug("Signing up")
        return self.sessionManager.signup(username, password)

    @Slot(str, str, result=bool)
    def login(self, username, password):
        self.ctx.logger.debug("Logging in")
        success = self.sessionManager.login(username, password)
        if success:
            self.ctx.logger.debug("Starting session related timers")
            self.logoutTimer = QTimer(parent=self, singleShot=True, timeout=self.logout)
            self.keepAliveTimer = QTimer(parent=self, timeout=self.keepAlive)
            self.logoutTimer.start(self.LEASE_TIME)
            self.keepAliveTimer.start(self.LEASE_TIME / 2)
        return success

    @Slot(result=bool)
    def logout(self):
        self.ctx.logger.debug("Logging out")
        success = self.chatManager.logout() and self.sessionManager.logout()
        self.ctx.logger.debug("Logout " + ("successful" if success else "FAILED"))
        # TODO: Close app if logout not successful?
        self.ctx.logger.debug("Deleting session related timers")
        self.keepAliveTimer.deleteLater()
        self.logoutTimer.deleteLater()
        self.ctx.logger.debug("Emiting loggedOut signal")
        self.loggedOut.emit()
        return success

    @Slot(str, str)
    def sendMessage(self, msg, partner):
        self.ctx.logger.debug("Sending a message to " + partner)
        return self.chatManager.sendMessage(msg, partner)

    @Slot()
    def keepAlive(self):
        self.ctx.logger.debug("Perfoming KeepAlive")
        partners = self.chatManager.chats.keys()
        timestamps = []
        for partner in partners:
            timestamps.append(self.chatManager.chats[partner].timestamp)
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
