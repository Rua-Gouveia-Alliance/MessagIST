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
        if not username or not password:
            return False

        salt = self.getSalt(username)
        if salt == "":
            return False

        self.ctx.logger.debug("Sending LOGIN request")
        password = MessagISTCrypto.prepareServerStorage(password, salt)
        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.LoginRequest(username=username, password=password)
        response = stub.login(request)
        if response.success:
            self.ctx.logger.debug("Login successful")
            self.ctx.setUsername(username)
            self.ctx.setSessionToken(response.token)
            self.ctx.setActiveSession(True)

        return response.success

    def signup(self, username, password):
        if not username or not password:
            return False

        self.ctx.logger.debug("Sending SIGNUP request")
        salt = MessagISTCrypto.generateSalt(username)
        password = MessagISTCrypto.prepareServerStorage(password, salt)
        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.SignupRequest(username=username, password=password, salt=salt)
        response = stub.signup(request)
        return response.success

    def logout(self):
        self.ctx.logger.debug(
            "Sending LOGOUT request (not really sending anything but will be implemented in the future (???))"
        )
        if not self.ctx.activeSession:
            self.ctx.logger.debug("LOGOUT request FAILED")
            return False

        self.ctx.setUsername("")
        self.ctx.setSessionToken("")
        self.ctx.setActiveSession(False)
        return True
