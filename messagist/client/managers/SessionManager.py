import MessagISTCrypto
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2


# TODO catch _InactiveRpcError(state) e emitir logout signal
class SessionManager:
    def __init__(self, ctx):
        self.ctx = ctx

    def keepAlive(self, partners, timestamps):
        self.ctx.logger.debug("Sending KEEPALIVE request")
        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.KeepAliveRequest(
            token=self.ctx.sessionToken, partners=partners, timestamps=timestamps
        )
        response = stub.keepAlive(request)
        self.ctx.logger.debug(
            "KEEPALIVE " + ("sucess" if response.success else "FAILED")
        )
        return response.success, response.partners, response.messages

    def getSalt(self, username):
        if not username:
            return ""

        self.ctx.logger.debug("Sending GETSALT request")
        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.GetSaltRequest(username=username)
        response = stub.getSalt(request)
        if response.success:
            self.ctx.logger.debug("Salt retrieved successfully")

        return response.salt

    def login(self, username, password):
        if not username or username == "":
            return {"success": False, "error": "Username cannot be empty"}
        if not password or password == "":
            return {"success": False, "error": "Password cannot be empty"}

        salt = self.getSalt(username)
        if salt == "":
            return {"success": False, "error": "User does not exist"}

        self.ctx.logger.debug("Sending LOGIN request")
        hiddenPassword = MessagISTCrypto.prepareForStorage(password, salt)
        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.LoginRequest(username=username, password=hiddenPassword)
        response = stub.login(request)
        if response.success:
            self.ctx.logger.debug("Login successful")
            self.ctx.setUsername(username)
            self.ctx.setSessionToken(response.token)
            self.ctx.setIdentityKey(MessagISTCrypto.loadKey(username, password))
            self.ctx.setContacts(MessagISTCrypto.loadContacts(username, password))
            self.ctx.setActiveSession(True)
            return {"success": True}
        return {"success": False, "error": "Invalid username or password"}

    def signup(self, username, password):
        if not username or username == "":
            return {"success": False, "error": "Username cannot be empty"}
        if not password or password == "":
            return {"success": False, "error": "Password cannot be empty"}

        self.ctx.logger.debug("Sending SIGNUP request")

        salt = MessagISTCrypto.getSalt(username)
        hiddenPassword = MessagISTCrypto.prepareForStorage(password, salt)

        identityKey = MessagISTCrypto.generateIdentityKey()
        publicKeyBytes = identityKey.public_key().public_bytes_raw()

        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.SignupRequest(
            username=username,
            password=hiddenPassword,
            identityKey=publicKeyBytes,
            salt=salt,
        )
        response = stub.signup(request)

        if response.success:
            MessagISTCrypto.storeKey(username, password, identityKey)
            wordList = MessagISTCrypto.encodeAsWords(identityKey)
            return {"success": True, "words": "\n".join(wordList)}

        return {"success": False, "error": "Invalid username or password"}

    def logout(self):
        # TODO: Send logout request?
        self.ctx.logger.debug("Sending LOGOUT request (not really sending)")
        if not self.ctx.activeSession:
            self.ctx.logger.debug("LOGOUT request FAILED")
            return False

        self.ctx.setUsername("")
        self.ctx.setSessionToken("")
        self.ctx.setIdentityKey(None)
        self.ctx.setContacts(None)
        self.ctx.setActiveSession(False)
        return True

    def recoverIdentityKey(self, wordList, password):
        wordList = wordList.splitlines()
        identityKey = MessagISTCrypto.decodeFromWords(wordList)
        if identityKey is None:
            return False
        MessagISTCrypto.storeKey(self.ctx.username, password, identityKey)
        self.ctx.setIdentityKey(identityKey)
        return True
