import MessagISTCrypto
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2
import re


# TODO catch grpc.RpcError e emitir logout signal
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
        
        username = username.split("@")[0]
        
        salt = self.getSalt(username)
        
        if salt == "":
            return {"success": False, "error": "User does not exist"}

        self.ctx.logger.debug("Sending LOGIN request")
        hiddenPassword = MessagISTCrypto.prepareForStorage(password, salt)
        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.LoginRequest(username=username, password=hiddenPassword)
        response = stub.login(request)
        if response.success:
            return {"success": True}
        return {"success": False, "error": "Invalid username or password"}

    def submitTwoFactorTokenLogin(self, username, password, token):
        self.ctx.logger.debug("Sending SUBMITTWOFACTORTOKEN request")
        
        username = username.split("@")[0]

        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.SubmitTwoFactorTokenLoginRequest(username=username, token=token)
        response = stub.submitTwoFactorTokenLogin(request)
        if response.success:
            self.ctx.setUsername(username)
            self.ctx.setSessionToken(response.token)
            self.ctx.setIdentityKey(MessagISTCrypto.loadKey(username, password))
            self.ctx.setContacts(MessagISTCrypto.loadContacts(username, password))
            self.ctx.setActiveSession(True)
            return {"success": True}
        return {"success": False, "error": "Invalid token"}

    def signup(self, username, password):
        if not username or username == "":
            return {"success": False, "error": "Username cannot be empty"}
        if not password or password == "":
            return {"success": False, "error": "Password cannot be empty"}

        pattern = r"^[a-zA-Z0-9._%+-]+@tecnico\.ulisboa\.pt$"
        ist_type = bool(re.match(pattern, username))
        if not ist_type:
            return {"success": False, "error": "Username should be your ist email"}
        #TODO descomentar
        """verify_password_mistakes =  self.verify_password(password,username)
        if verify_password_mistakes != []:
            return {"success": False, "error": "Password verification failed:\n" + "\n".join(verify_password_mistakes)}"""
        self.ctx.logger.debug("Sending SIGNUP request")

        username = username.split("@")[0]
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
            return {"success": True}

        return {"success": False, "error": "Invalid username or password"}

    def submitTwoFactorTokenSignUp(self, username, password, token):
        self.ctx.logger.debug("Sending SUBMITTWOFACTORTOKEN request")
        username = username.split("@")[0]

        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.SubmitTwoFactorTokenSignUpRequest(username=username, token=token)
        response = stub.submitTwoFactorTokenSignUp(request)
        if response.success:
            identityKey = MessagISTCrypto.loadKey(username, password)
            wordList = MessagISTCrypto.encodeAsWords(identityKey)
            return {"success": True, "words": "\n".join(wordList)}

        return {"success": False, "error": "Invalid token"}

    def logout(self, password=""):
        # TODO: Send logout request?
        self.ctx.logger.debug("Sending LOGOUT request (not really sending)")
        if not self.ctx.activeSession:
            self.ctx.logger.debug("LOGOUT request FAILED")
            return False

        if password != "":
            MessagISTCrypto.storeContacts(
                self.ctx.username, password, self.ctx.contacts
            )

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
    
    def verify_password(self,password,username):
        errors = []
        if len(password) < 8 :
            errors.append("Password must be at least 8 characters long.")

        if not any(char.isupper() for char in password):
            errors.append("Password must contain at least one uppercase letter.")  
        if not any(char.islower() for char in password):
            errors.append("Password must contain at least one lowercase letter.")      
        if not any(char.isdigit() for char in password):
            errors.append("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Password must contain at least one special character (e.g., !, @, #).")
        common_patterns = ["123", "abc", "password", "qwerty"]
        if any(pattern in password.lower() for pattern in common_patterns):
            errors.append("Password must not contain common patterns like '123', 'abc', or 'password'.")
        if password == username : 
            errors.append("Password must not be the same as the name of the user.")
        return errors

