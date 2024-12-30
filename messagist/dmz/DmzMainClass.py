import sys
import logging
import os

sys.path.insert(1, "../contract/target/")

import grpc
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# TODO: Configurar logger em condicoes
class DmzMainClass(pb2_grpc.MessagISTServerServicer):
    def __init__(self, main_server_address):
        server_cert = "../server/keys/server.crt"
        with open(server_cert, "rb") as cert_file:
            trusted_certs = cert_file.read()
        credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
        self.ms_channel = grpc.secure_channel(main_server_address, credentials)
        # self.stub = pb2_grpc.MessagISTServerStub(self.channel)

    def login(self, request, context):
        try:
            # Forward the request to the main server and return the response
            stub = pb2_grpc.MessagISTServerStub(self.ms_channel)
            response = stub.login(request)
            return response
        except grpc.RpcError as e:
            # Handle errors from the main server
            context.set_code(e.code())
            context.set_details(e.details())
            return pb2.LoginResponse(success=False, token="", error="Main server error")

    def signup(self, request, context):
        try:
            # Forward the request to the main server and return the response
            stub = pb2_grpc.MessagISTServerStub(self.ms_channel)
            response = stub.signup(request)
            return response
        except grpc.RpcError as e:
            # Handle errors from the main server
            context.set_code(e.code())
            context.set_details(e.details())
            return pb2.SignupResponse(success=False, error="Main server error")

    def getSalt(self, request, context):
        try:
            # Forward the request to the main server and return the response
            stub = pb2_grpc.MessagISTServerStub(self.ms_channel)
            response = stub.getSalt(request)
            return response
        except grpc.RpcError as e:
            # Handle errors from the main server
            context.set_code(e.code())
            context.set_details(e.details())
            return pb2.GetSaltResponse(
                success=False, salt="", error="Main server error"
            )

    def send(self, request, context):
        try:
            # Forward the request to the main server and return the response
            stub = pb2_grpc.MessagISTServerStub(self.ms_channel)
            response = stub.send(request)
            return response
        except grpc.RpcError as e:

            # Handle errors from the main server
            context.set_code(e.code())
            context.set_details(e.details())
            return pb2.SendResponse(
                success=False, timestamp=0, error="Main server error"
            )

    def keepAlive(self, request, context):
        try:
            # Forward the request to the main server and return the response
            stub = pb2_grpc.MessagISTServerStub(self.ms_channel)
            response = stub.keepAlive(request)
            return response
        except grpc.RpcError as e:
            # Handle errors from the main server
            context.set_code(e.code())
            context.set_details(e.details())
            return pb2.KeepAliveResponse(
                success=False, partners="", messages="", error="Main server error"
            )

    def getIdentityKey(self, request, context):
        try:
            # Forward the request to the main server and return the response
            stub = pb2_grpc.MessagISTServerStub(self.ms_channel)
            response = stub.getIdentityKey(request)
            return response
        except grpc.RpcError as e:
            # Handle errors from the main server
            context.set_code(e.code())
            context.set_details(e.details())
            return pb2.GetIdentityKeyResponse(identityKey="")

    def trySetSalt(self, request, context):
        try:
            # Forward the request to the main server and return the response
            stub = pb2_grpc.MessagISTServerStub(self.ms_channel)
            response = stub.trySetSalt(request)
            return response
        except grpc.RpcError as e:
            # Handle errors from the main server
            context.set_code(e.code())
            context.set_details(e.details())
            return pb2.TrySetSaltResponse(salt="")
