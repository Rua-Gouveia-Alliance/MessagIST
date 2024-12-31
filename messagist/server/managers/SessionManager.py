import threading
import logging
from managers.Session import Session
import time
import pyotp


class SessionManager:
    def __init__(self):
        self.LEASE_TIME = 5  # 5s
        self.sessions = {}
        self.lock = threading.Lock()
        self.tokens= {}

    def startSession(self, username):
        self.lock.acquire()

        token = ""
        if username not in self.sessions:
            self.sessions[username] = Session(self, username)
            token = self.sessions[username].token

        self.lock.release()
        return token

    def endSession(self, username):
        self.lock.acquire()

        status = False
        if username in self.sessions:
            del self.sessions[username]
            logging.debug(username + "'s session expired")
            status = True

        self.lock.release()
        return status

    def validSession(self, username, token):
        self.lock.acquire()
        status = username in self.sessions and self.sessions[username].validate(token)
        self.lock.release()
        return status

    def getUser(self, token):
        self.lock.acquire()

        result = ""
        for username, session in self.sessions.items():
            if session.validate(token):
                result = username
                break

        self.lock.release()
        return result

    def renewLease(self, username):
        self.lock.acquire()

        status = False
        if username in self.sessions:
            self.sessions[username].renewLease()
            status = True
            logging.debug(username + "'s lease renewed")

        self.lock.release()
        return status
    def storeToken(self, username,token, timestamp):

        self.tokens[username] = (token, timestamp)
        logging.debug(f"Token stored for user {username}.")
    def retrieveToken(self, username):
        """
        Retrieve the token and timestamp for a specific user.
        :param username: The username whose token is being retrieved
        :return: A tuple (token, timestamp) or None if the user has no token
        """
        return self.tokens.get(username)
    def clearToken(self, username):
        """
        Clear the stored token for a user after successful verification or expiration.
        :param username: The username whose token should be cleared
        """
        if username in self.tokens:
            del self.tokens[username]
            logging.debug(f"Token cleared for user {username}.")    

    def verifyToken(self, username, token):
        # Retrieve stored token and timestamp
        stored_token_data = self.retrieveToken(username)
        if not stored_token_data:
            logging.warning("No token found for user.")
            return False

        stored_token, timestamp = stored_token_data
        if time.time() - timestamp > 300:  # Token expired
            logging.warning("Token expired.")
            self.clearToken(username)
            return False
        

        # Verify the token
        key = "NeuralNineMySuperSecretKey"
        totp = pyotp.TOTP(key)

        return totp.verify(token)