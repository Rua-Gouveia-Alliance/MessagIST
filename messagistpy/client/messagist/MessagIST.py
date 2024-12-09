from PySide6.QtCore import QObject, Slot, Property
from managers.ChatManager import ChatManager
from managers.SessionManager import SessionManager
from messagist.MessagISTContext import MessagISTContext


class MessagIST(QObject):
    def __init__(self, debug, port):
        QObject.__init__(self)
        self.ctx = MessagISTContext(debug, port)
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

    @Slot(result=list)
    def showChats(self):
        self.ctx.logger.debug("Listing all chats")
        chats = [partner for partner in self.chatManager.chats]
        return chats

    @Slot(str, result=list)
    def showChatWith(self, partner):
        self.ctx.logger.debug("Showing chat with " + partner)
        if partner not in self.chatManager.chats:
            return []
        return self.chatManager.chats[partner].getMessages()

    @Slot(str, str)
    def sendMessage(self, msg, partner):
        self.ctx.logger.debug("Sending a message to " + partner)
        return self.chatManager.sendMessage(msg, partner)
