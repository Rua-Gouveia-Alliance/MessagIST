import os
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes, hmac
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def generateSalt(username):
    salt = os.urandom(16)  # Random bytes
    salt += username.encode("ascii")  # To ensure uniqueness
    return salt


def prepareForStorage(password, salt):
    # https://datatracker.ietf.org/doc/html/rfc7914.html#section-2
    password = password.encode("ascii")
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    return kdf.derive(password)


def deriveKeysFromPassword(password, salt):
    data = password.encode("ascii")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=64,
        salt=salt,
        iterations=480000,
    )
    key = kdf.derive(data)
    hmacKey = key[:32]
    encryptionKey = key[32:]
    return hmacKey, encryptionKey


def encodeAsWords(key):
    num = str(int.from_bytes(key.private_bytes_raw(), "big"))
    numbers = [num[x : min(x + 5, len(num))] for x in range(0, len(num), 5)]
    words = [len(num)]
    with open("words.txt", "r") as f:
        wordList = f.readlines()
        for n in numbers:
            words.append(wordList[int(n)][:-1])
    return words


def decodeFromWords(words):
    number = []
    size = int(words[0])
    with open("words.txt", "r") as f:
        wordList = f.readlines()
        for word in words[1:]:
            index = str(wordList.index(word + "\n"))
            if size >= 5:
                index = "0" * (5 - len(index)) + index
                size -= 5
            else:
                index = "0" * (size - len(index)) + index
            number.append(index)
    privateBytesValue = int("".join(number))
    privateBytes = privateBytesValue.to_bytes(32, "big")
    return Ed25519PrivateKey.from_private_bytes(privateBytes)


def generateKeyPair():
    return Ed25519PrivateKey.generate()


def protectKey(key, encryptionKey, hmacKey):
    # Encrypt-then-MAC
    serializedKey = key.private_bytes_raw()

    padder = padding.PKCS7(128).padder()
    data = padder.update(serializedKey) + padder.finalize()

    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES256(encryptionKey), modes.CBC(iv))
    encryptor = cipher.encryptor()
    data = encryptor.update(data) + encryptor.finalize()

    signer = hmac.HMAC(hmacKey, hashes.SHA256())
    signer.update(data)
    signature = signer.finalize()

    return iv, signature, data


def unprotectKey(serializedKey, encryptionKey, hmacKey, iv, signature):
    signer = hmac.HMAC(hmacKey, hashes.SHA256())
    signer.update(serializedKey)

    try:
        signer.verify(signature)
    except InvalidSignature:
        return None

    cipher = Cipher(algorithms.AES256(encryptionKey), modes.CBC(iv))
    decryptor = cipher.decryptor()
    data = decryptor.update(serializedKey) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(data) + unpadder.finalize()

    return Ed25519PrivateKey.from_private_bytes(data)


def loadKey(username, password):
    path = os.path.abspath(f"./keys/{username}/private.key")
    if not os.path.exists(path):
        return None

    path = os.path.abspath(f"./keys/{username}/private.sig")
    if not os.path.exists(path):
        return None

    path = os.path.abspath(f"./keys/{username}/private.salt")
    if not os.path.exists(path):
        return None

    path = os.path.abspath(f"./keys/{username}/private.iv")
    if not os.path.exists(path):
        return None

    with open(f"./keys/{username}/private.key", "rb") as f:
        serializedKey = f.read()
    with open(f"./keys/{username}/private.sig", "rb") as f:
        signature = f.read()
    with open(f"./keys/{username}/private.salt", "rb") as f:
        salt = f.read()
    with open(f"./keys/{username}/private.iv", "rb") as f:
        iv = f.read()

    encryptionKey, hmacKey = deriveKeysFromPassword(password, salt)
    key = unprotectKey(serializedKey, encryptionKey, hmacKey, iv, signature)
    return key


def storeKey(username, password, key):
    path = os.path.abspath("./keys")
    if not os.path.exists(path):
        os.mkdir(path)

    path = os.path.abspath(f"./keys/{username}")
    if not os.path.exists(path):
        os.mkdir(path)

    salt = generateSalt(username)
    encryptionKey, hmacKey = deriveKeysFromPassword(password, salt)
    iv, signature, serializedKey = protectKey(key, encryptionKey, hmacKey)

    with open(f"./keys/{username}/private.key", "wb") as f:
        f.write(serializedKey)
    with open(f"./keys/{username}/private.sig", "wb") as f:
        f.write(signature)
    with open(f"./keys/{username}/private.salt", "wb") as f:
        f.write(salt)
    with open(f"./keys/{username}/private.iv", "wb") as f:
        f.write(iv)

    return True
