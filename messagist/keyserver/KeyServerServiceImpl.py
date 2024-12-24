import sys
import logging
from managers.IdentityKeyManager import IdentityKeyManager
from managers.ChatSaltManager import ChatSaltManager

sys.path.insert(1, "../contract/target/")
import KeyServer_pb2_grpc as pb2_grpc
import KeyServer_pb2 as pb2


class KeyServerServiceImpl(pb2_grpc.KeyServerServicer):
    def __init__(self, db, *args, **kwargs):
        self.identityKeyManager = IdentityKeyManager(db)
        self.chatSaltManager = ChatSaltManager(db)

    def registerIdentityKey(self, request, context):
        logging.debug("REGISTERIDENTITYKEY request received")
        logging.debug("Message: " + request.message)

        # TODO: this is vulnerable
        username = request.username
        identity_key = request.identity_key
        if not self.identityKeyManager.registerKey(username, identity_key):
            logging.debug("GETCLIENTKU FAILED")
            return pb2.ResgiterIdentityKeyResponse(success=False)

        logging.debug("GETCLIENTKU success")
        return pb2.ResgiterIdentityKeyResponse(success=True)

    def getIdentityKey(self, request, context):
        logging.debug("GETIDENTITYKEY request received")
        logging.debug("Message: " + request.message)

        username = request.username
        identity_key = self.identityKeyManager.getKey(username)
        if identity_key == "":
            logging.debug("GETIDENTITYKEY FAILED")

        logging.debug("GETIDENTITYKEY success")
        return pb2.GetIdentityKeyResponse(identity_key=identity_key)

    def trySetSalt(self, request, context):
        logging.debug("TRYSETSALT request received")
        logging.debug("Username: " + request.username)

        username = request.username
        partner = request.partner
        received_salt = request.salt
        salt = self.chatSaltManager.trySetSalt(username, partner, received_salt)

        if salt == received_salt:
            logging.debug("New salt")
        else:
            logging.debug("Salt already existed for this chat")

        return pb2.TrySetSaltResponse(salt=salt)
