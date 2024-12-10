from PySide6.QtCore import QObject, Slot, Property, Signal
from managers.ChatManager import ChatManager
from managers.SessionManager import SessionManager
from messagist.MessagISTContext import MessagISTContext


class MessagIST(QObject):
    chatsChanged = Signal()

    def __init__(self, debug, port):
        QObject.__init__(self)
        self.ctx = MessagISTContext(debug, port)
        self.ctx.setChatsChanged(self.chatsChanged)
        self.sessionManager = SessionManager(self.ctx)
        self.chatManager = ChatManager(self.ctx)

    @Slot(str, str, result=bool)
    def signup(self, username, password):
        return self.sessionManager.signup(username, password)

    @Slot(str, str, result=bool)
    def login(self, username, password):
        return self.sessionManager.login(username, password)

    @Slot(result=bool)
    def logout(self):
        self.ctx.logger.debug("Logging out")
        return self.chatManager.logout() and self.sessionManager.logout()

    @Slot(str, str)
    def sendMessage(self, msg, partner):
        self.ctx.logger.debug("Sending a message to " + partner)
        return self.chatManager.sendMessage(msg, partner)

    def getChats(self):
        chats = {}
        for partner in self.chatManager.chats:
            chats[partner] = self.chatManager.chats[partner].getMessages()
        return chats

    chats = Property(type="QVariant", fget=getChats, notify=chatsChanged)
