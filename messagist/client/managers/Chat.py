import json
import MessagISTCrypto
import MessagISTServer_pb2_grpc as pb2_grpc
import MessagISTServer_pb2 as pb2
from datetime import datetime, timezone


class Chat:
    def __init__(self, ctx, partner, identityKey):
        self.ctx = ctx
        self.partner = partner
        self.messages = []
        self.bufferedMessages = []
        self.timestamp = 0
        # These clocks also establish a partial order for messages, consider
        # using them to check the server ordering (if the ordering does not
        # match, drop message).
        # With this solution:
        # If a client tries altering the message order by changing the clock,
        # the most it can do is cause the message to be dropped (basically the
        # same as not sending it, achieves nothing).
        # If the server is compromised and tries to altering the message order
        # by changing the timestamp, the most it can do is cause the message to
        # be dropped (basically the same as not sending it, achieves nothing).
        self.index = 0 if self.ctx.username < self.partner else 1
        self.partnerIndex = 1 if self.partner >= self.ctx.username else 0
        self.clock = [0, 0]

        if partner not in self.ctx.contacts:
            self.ctx.contacts[partner] = MessagISTCrypto.createContactsEntry(
                identityKey
            )

        self.pending = False
        self.partnerIdentityKey = self.ctx.contacts[partner]["key"]
        self.sessionKey = self.ctx.contacts[partner]["sessionKey"]
        if self.sessionKey is None:
            self.pending = True

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

        if salt == "":
            return False

        self.sessionKey = MessagISTCrypto.computeSessionKey(passphrase, salt)
        self.ctx.contacts[self.partner]["sessionKey"] = self.sessionKey
        self.pending = False

        return True

    def getMessages(self):
        messages = [self.pending]
        for message in self.messages:
            messages.append(message)
        return messages

    def send(self, message):
        # Sanity check, this should never be called before setting the secret.
        if self.pending:
            return False

        # Calculating message clock
        # TODO: shouldn't we wait the receiving of all messages (len(pedding buffer) == 0), before sending our message?
        #       if we are replaying all the messages in a new instance of the client, and we try to send a message before all
        #       other messages are already local, we could be using a clock in the past (between previously sent messages).
        #       maybe create a chat loading screen where you cannot send messages while you receive messages from the server
        #       (server should send with the last message a flag making you know it's the last one it has from that convo).
        clock = self.clock[:]
        clock[self.index] += 1

        message = self._createMessage(message, clock)
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
            self.ctx.logger.debug("Chat is pending, drop message")
            return

        unprotectedMessage = MessagISTCrypto.unprotect(
            self.partnerIdentityKey, self.sessionKey, message
        )
        sentMessage = False
        if unprotectedMessage is None:  # Unprotect failed with partner's key
            # Check if we sent the message
            unprotectedMessage = MessagISTCrypto.unprotect(
                self.ctx.identityKey.public_key(), self.sessionKey, message
            )
            sentMessage = True

        if unprotectedMessage is None:  # Unprotect also failed with our key
            self.ctx.logger.debug("Decryption failed")
            self.ctx.logger.debug("Dropped message")
            return  # Drop message

        message = json.loads(unprotectedMessage)
        message["sender"] = sentMessage

        self.ctx.logger.debug("Appending to the buffered messages")
        if (ts, message) not in self.bufferedMessages:
            self.bufferedMessages.append((ts, message))
            self.bufferedMessages.sort()

        while (
            len(self.bufferedMessages) != 0
            and self.bufferedMessages[0][0] <= self.timestamp
        ):
            # check for repeated timestamp
            if self.bufferedMessages[0][0] < self.timestamp:
                self.bufferedMessages.pop(0)
                continue

            self.timestamp += 1
            message = self.bufferedMessages.pop(0)[1]
            if self._verifyMessageClock(message):
                self.ctx.logger.debug("Appending to the chat")
                self.messages.append(message)
                self._advanceClock(message["clock"])

    def _advanceClock(self, clock):
        if clock:
            self.clock[self.index] = max(self.clock[self.index], clock[self.index])
            self.clock[self.partnerIndex] = max(
                self.clock[self.partnerIndex], clock[self.partnerIndex]
            )

    def _verifyMessageClock(self, message):
        clock = message["clock"]

        # check for repeated colock
        for msg in self.messages:
            if (
                msg["clock"][0] == clock[0]
                and msg["clock"][1] == clock[1]
                and msg["sender"] == message["sender"]
            ):
                return False

        if len(self.messages) > 0:
            # traditional vector clocks dont make sense for this use case. this condition
            # that they guarantee is already guaranteed by the conditions uncommented below,
            # which are the same thing as having a counter for each client
            # if clock[0] < self.clock[0] and clock[1] < self.clock[1]:
            #    return False

            if message["sender"]:
                if clock[self.index] != self.clock[self.index] + 1:
                    return False
            else:
                if clock[self.partnerIndex] != self.clock[self.partnerIndex] + 1:
                    return False

        return True

    def _createMessage(self, message, clock):
        message = {
            "clock": clock,
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
