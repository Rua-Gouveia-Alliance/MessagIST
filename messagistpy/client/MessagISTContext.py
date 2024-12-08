import grpc
import logging


class MessagISTContext:
    def __init__(self, debug, port):
        logging.basicConfig(level=(logging.DEBUG if debug else logging.CRITICAL))
        logger_handler = logging.StreamHandler()
        logger_handler.setFormatter(logging.Formatter("[%(levelname)s]: %(message)s"))

        self.logger = logging.getLogger()
        self.logger.handlers = []
        self.logger.addHandler(logger_handler)

        self.channel = grpc.insecure_channel("localhost:" + str(port))

    def setUsername(self, username):
        self.username = username

    def setSessionToken(self, sessionToken):
        self.sessionToken = sessionToken

    def setActiveSession(self, activeSession):
        self.activeSession = activeSession

    def setChannel(self, channel):
        self.channel = channel
