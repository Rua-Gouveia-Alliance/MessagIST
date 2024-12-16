import os
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id


def generateSalt(username):
    salt = os.urandom(16)  # Random bytes
    salt += username.encode("utf-8")  # To ensure uniqueness
    return salt


def hidePassword(password, salt):
    # Parameter reference: https://datatracker.ietf.org/doc/html/rfc9106#section-4
    # Backend server authentication
    data = password.encode("utf-8")
    kdf = Argon2id(
        salt=salt,
        length=32,
        iterations=1,
        lanes=8,
        memory_cost=4194304,  # 4GiB
        ad=None,
        secret=None,
    )
    return kdf.derive(data)
