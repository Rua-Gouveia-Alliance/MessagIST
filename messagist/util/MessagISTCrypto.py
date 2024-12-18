import os
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import ec


def generateSalt(username):
    salt = os.urandom(16)  # Random bytes
    salt += username.encode("utf-8")  # To ensure uniqueness
    return salt


def prepareServerStorage(password, salt):
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


def prepareLocalStorage(password, salt):
    # Parameter reference: https://datatracker.ietf.org/doc/html/rfc9106#section-4
    # Key derivation for hard-drive encryption
    data = password.encode("utf-8")
    kdf = Argon2id(
        salt=salt,
        length=32,
        iterations=1,
        lanes=4,
        memory_cost=6291456,  # 6GiB
        ad=None,
        secret=None,
    )
    return kdf.derive(data)


def encodeAsWords(key):
    num = str(key.private_numbers().private_value)
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
    return int("".join(number))


def generateKeyPair():
    key = ec.generate_private_key(ec.SECP256R1())
    return key


def protectKey(key, hiddenPassword):
    padder = padding.PKCS7(128).padder()
    data = padder.update(key) + padder.finalize()

    # TODO: ECB is probably okay since we won't have patterns
    cipher = Cipher(algorithms.AES256(hiddenPassword), modes.ECB())
    encryptor = cipher.encryptor()
    data = encryptor.update(data) + encryptor.finalize()
    return data


def unprotectKey(key, hiddenPassword):
    cipher = Cipher(algorithms.AES256(hiddenPassword), modes.ECB())
    decryptor = cipher.decryptor()
    data = decryptor.update(key) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(data) + unpadder.finalize()
    return data


def loadSalt(username):
    path = os.path.abspath(f"./keys/{username}/password.salt")
    if not os.path.exists(path):
        return ""

    with open(f"./keys/{username}/password.salt", "rb") as f:
        salt = f.readline()
        return salt

    # TODO: Is this last return necessary in case the "with" fails?
    return ""


def loadPrivateKey(username, hiddenPassword):
    path = os.path.abspath(f"./keys/{username}/priv.key")
    if not os.path.exists(path):
        return ""

    with open(f"./keys/{username}/priv.key", "rb") as f:
        privKey = f.readline()
        privKey = unprotectKey(privKey, hiddenPassword)
        return privKey

    # TODO: Is this last return necessary in case the "with" fails?
    return ""


def loadPublicKey(username):
    path = os.path.abspath(f"./keys/{username}/pub.key")
    if not os.path.exists(path):
        return ""

    with open(f"./keys/{username}/pub.key", "rb") as f:
        pubKey = f.readline()
        return pubKey

    # TODO: Is this last return necessary in case the "with" fails?
    return ""


def loadKeyPair(username, password):
    salt = loadSalt(username)
    password = prepareLocalStorage(password, salt)
    privKey = loadPrivateKey(username, password)
    pubKey = loadPublicKey(username)
    return privKey, pubKey


def storeSalt(username, salt):
    with open(f"./keys/{username}/password.salt", "wb") as f:
        f.write(salt)
    return True


def storePrivateKey(username, password, key):
    key = protectKey(key, password)
    with open(f"./keys/{username}/priv.key", "wb") as f:
        f.write(key)
    return True


def storePublicKey(username, key):
    with open(f"./keys/{username}/pub.key", "wb") as f:
        f.write(key)
    return True


def storeKeyPair(username, password, pubKey, privKey):
    path = os.path.abspath("./keys")
    if not os.path.exists(path):
        os.mkdir(path)

    path = os.path.abspath(f"./keys/{username}")
    if not os.path.exists(path):
        os.mkdir(path)

    salt = generateSalt(username)
    password = prepareLocalStorage(password, salt)
    storeSalt(username, salt)
    storePrivateKey(username, password, privKey)
    storePublicKey(username, pubKey)
    return True
