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
        self.pendingMessages = []
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
        self.pending = True

        if partner not in self.ctx.contacts:
            stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
            request = pb2.GetIdentityKeyRequest(username=partner)
            response = stub.getIdentityKey(request)

            # TODO: what if identity key doesnt exist (response.identity_key == "")
            if response.identityKey == "":
                print("teste")
            else:
                self.ctx.contacts[partner] = MessagISTCrypto.createContactsEntry(
                    response.identityKey
                )

        self.partnerIdentityKey = self.ctx.contacts[partner]

    def setPassphrase(self, passphrase):
        self.ctx.logger.debug(
            "Setting the passphrase for the chat with " + self.partner
        )
        salt = MessagISTCrypto.getSalt(self.ctx.username + self.partner)

        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.TrySetSaltRequest(
            token=self.ctx.sessionToken, partner=self.partner, salt=salt
        )
        response = stub.trySetSalt(request)
        salt = response.salt

        self.sessionKey = MessagISTCrypto.computeSessionKey(passphrase, salt)
        self.pending = False
        self.pendingMessages.sort(key=lambda x: x[1])
        for message, ts in self.pendingMessages:
            self.append(message, ts)

    def getMessages(self):
        messages = [self.pending]
        for message in self.messages:
            messages.append(message)
        return messages

    def send(self, message):
        # Sanity check, this should never be called before setting the secret.
        if self.pending:
            return False

        message = self._createMessage(message)
        stub = pb2_grpc.MessagISTServerStub(self.ctx.channel)
        request = pb2.SendRequest(
            token=self.ctx.sessionToken, message=message, partner=self.partner
        )
        response = stub.send(request)
        if not response.success:
            return False

        self.append(message, response.timestamp)
        self.ctx.logger.debug("Message: " + str(message))
        return True

    def append(self, message, ts):
        self.ctx.logger.debug("Appeding to the chat with " + self.partner)
        self.ctx.logger.debug("Message: " + str(message))
        self.ctx.logger.debug("Timestamp " + str(ts))
        # Haven't set the passphrase/sessionKey yet
        if self.pending:
            self.pendingMessages.append((message, ts))
            self.ctx.logger.debug("Appending to pending messages")
            return

        message = MessagISTCrypto.unprotect(
            self.partnerIdentityKey, self.sessionKey, message
        )
        sentMessage = False
        if message is None:  # Unprotect failed with partner's key
            # Check if we sent the message
            message = MessagISTCrypto.unprotect(
                self.ctx.identityKey.public_key(), self.sessionKey, message
            )
            sentMessage = True

        if message is None:  # Unprotect also failed with our key
            self.ctx.logger.debug("Decryption failed")
            self.ctx.logger.debug("Dropped message")
            return  # Drop message

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
            self.ctx.logger.debug("Appending to the chat")
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
            self.ctx.logger.debug("Appending to the buffered messages")
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
        message = MessagISTCrypto.protect(
            self.ctx.identityKey, self.sessionKey, message
        )
        return message
