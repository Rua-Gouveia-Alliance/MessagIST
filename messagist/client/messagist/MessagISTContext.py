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

        self.activeSession = False

        server_cert = "../server/keys/server.crt"
        with open(server_cert, "rb") as cert_file:
            trusted_certs = cert_file.read()
        credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
        self.channel = grpc.secure_channel("localhost:" + str(port), credentials)

    def setUsername(self, username):
        self.username = username

    def setSessionToken(self, sessionToken):
        self.sessionToken = sessionToken

    def setActiveSession(self, activeSession):
        self.activeSession = activeSession

    def setIdentityKey(self, identityKey):
        self.identityKey = identityKey

    def setContacts(self, contacts):
        self.contacts = contacts

    def setChatsChanged(self, signal):
        self.chatsChanged = signal
