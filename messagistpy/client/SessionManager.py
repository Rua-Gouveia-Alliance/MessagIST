import sys

sys.path.insert(1, "../contract/target/")
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2


class SessionManager:
    def __init__(self, ctx):
        self.ctx = ctx

    def login(self, username, password):
        self.ctx.logger.debug("Logging in user " + username)

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
        self.ctx.logger.debug("Signing up user " + username)
        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.SignupRequest(username=username, password=password)
        response = stub.signup(request)
        return response.success
