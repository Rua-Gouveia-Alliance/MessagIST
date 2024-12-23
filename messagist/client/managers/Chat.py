import json
import MessagISTCrypto
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2
from datetime import datetime, timezone


class Chat:
    def __init__(self, ctx, partner):
        self.ctx = ctx
        self.partner = partner
        self.messages = []
        self.bufferedMessages = []
        self.timestamp = 0
        # These nonces also establish a partial order for messages, consider
        # using them to check the server ordering (if the ordering does not
        # match, drop message).
        # With this solution:
        # If a client tries altering the message order by changing the nonce,
        # the most it can do is cause the message to be dropped (basically the
        # same as not sending it, achieves nothing).
        # If the server is compromised and tries to altering the message order
        # by changing the timestamp, the most it can do is cause the message to
        # be dropped (basically the same as not sending it, achieves nothing).
        self.nonce = [0, 0]

        # partnerIdentityKey = Request partner's identityKey from the keyServer
        # self.partnerIdentityKey = partnerIdentityKey

    def setSecret(self, secret):
        self.secret = secret
        # self.DHValue = Calculate DH value
        # send DHValue to keyServer

    def getMessages(self):
        messages = []
        for message in self.messages:
            messages.append(message)
        return messages

    def send(self, message, partner):
        # Sanity check, this should never be called before setting the secret.
        # if self.secret is None:
        #    return False
        #
        # if self.pending and not self._tryGetPartnerDHValue():
        #     return False

        message = self._createMessage(message)
        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.SendRequest(
            token=self.ctx.sessionToken, message=message, partner=partner
        )
        response = stub.send(request)
        self.append(message, response.timestamp)
        return True

    def append(self, message, ts):
        # Sanity check, can't receive messages if we haven't set the secret and
        # uploaded our dh value to the server.
        # if self.secret is None:
        #    return
        #
        # if self.pending and not self._tryGetPartnerDHValue():
        #     return

        # message = MessagISTCrypto.unprotect(self.partnerIdentityKey, self.sessionKey, message)
        # sentMessage = False
        # if message is None:  # Unprotect failed with partner's key
        # # Check if we sent the message
        #     message = MessagISTCrypto.unprotect(self.ctx.identityKey.public_key(), self.sessionKey, message)
        #     sentMessage = True
        #
        # if message is None:  # Unprotect also failed with our key
        #     self.ctx.logger.debug("Decryption failed")
        #     self.ctx.logger.debug("Dropped message")
        #     return # Drop message

        message = json.loads(message)
        if not sentMessage:
            aux = message["nonce"][0]
            message["nonce"][0] = message["nonce"][1]
            message["nonce"][1] = aux

        # Checking if we already received this nonce
        for msg in self.messages:
            if (
                msg["nonce"][0] == message["nonce"][0]
                and msg["nonce"][1] == message["nonce"][1]
            ):
                self.ctx.logger.debug("Duplicate nonce")
                self.ctx.logger.debug("Dropped message")
                return  # Drop message

        if ts == self.timestamp:
            self.messages.append(message)
            self.timestamp += 1
            while (
                len(self.bufferedMessages) != 0
                and self.bufferedMessages[0][0] == self.timestamp
            ):
                message = self.bufferedMessages.pop(0)[1]
                self.messages.append(message)
                self.timestamp += 1
        elif ts > self.timestamp:
            if (ts, message) not in self.bufferedMessages:
                self.bufferedMessages.append((ts, message))
                self.bufferedMessages.sort()

        # Updating the next nonce to be used
        self.nextNonce(sentMessage)

    def nextNonce(self, sentMessage):
        self.nonce[0 if sentMessage else 1] += 1

    def _createMessage(self, message):
        message = {
            "nonce": self.nonce,
            "sender_istid": self.ctx.username,
            "receiver_istid": self.partner,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "content": message,
        }
        message = json.dumps(message, indent=4)
        # message = MessagISTCrypto.protect(self.ctx.identityKey, self.sessionKey, message)
        return message

    # def _tryGetPartnerDHValue():
    #     partnerDHValue = Request partner's DHValue for this conversation from the keyServer
    #     if partnerDHValue.success:
    #         self.sessionKey = self._computeSessionKey(partnerDHValue)
    #         self.pending = False
    #         return True
    #     return False
