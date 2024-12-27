import MessagISTCrypto
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2

import re


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
            return {"success": False, "error": "Username or password cannot be empty"}
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

        # return response.success

    def signup(self, username, password):
        if not username:
            return {"success": False, "error": "Username cannot be empty"}
        if not self.checkPassword(password):
            # TODO: Avisar utilizador
            return {
                "success": False,
                "error": "Password needs to have at least 1 digit, 1 symbol and more than 11 letters",
            }

        self.ctx.logger.debug("Sending SIGNUP request")

        salt = MessagISTCrypto.getSalt(username)
        hiddenPassword = MessagISTCrypto.prepareForStorage(password, salt)

        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.SignupRequest(
            username=username, password=hiddenPassword, salt=salt
        )
        response = stub.signup(request)

        if response.success:
            identityKey = MessagISTCrypto.generateIdentityKey()
            publicKeyBytes = identityKey.public_key().public_bytes_raw()

            stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
            request = pb2.RegisterIdentityKeyRequest(
                username=username, identity_key=publicKeyBytes
            )
            response = stub.registerIdentityKey(request)

            if not response.success:
                return {"success": False, "error": "Error registing identity key"}

            MessagISTCrypto.storeKey(username, password, identityKey)
            return {"success": True}

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

    def checkPassword(self, password):
        return True
        # has_uppercase = bool(re.search(r"[A-Z]", password))
        # has_symbol = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        # if len(password) > 11 and has_symbol and has_uppercase:
        #     return True
        # return False
