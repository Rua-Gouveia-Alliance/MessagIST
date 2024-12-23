import os
import base64
import argparse
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes, hmac
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def getSalt(username=""):
    salt = os.urandom(16)  # Random bytes
    salt += username.encode("ascii")  # To ensure uniqueness
    return salt


def getIV():
    return os.urandom(16)


def protect(privateIdentityKey, sessionKey, message):
    # Encrypt-then-MAC
    message = message.encode("ascii")

    padder = padding.PKCS7(128).padder()
    message = padder.update(message) + padder.finalize()

    iv = getIV()
    cipher = Cipher(algorithms.AES256(sessionKey), modes.CBC(iv))
    encryptor = cipher.encryptor()
    message = encryptor.update(message) + encryptor.finalize()

    signature = privateIdentityKey.sign(message)

    message = base64.b64encode(message).decode("ascii") + "\n"
    message += base64.b64encode(signature).decode("ascii") + "\n"
    message += base64.b64encode(iv).decode("ascii")

    return message


def unprotect(publicIdentityKey, sessionKey, message):
    message = message.splitlines()
    iv = base64.b64decode(message[2].encode("ascii"))
    signature = base64.b64decode(message[1].encode("ascii"))
    message = base64.b64decode(message[0].encode("ascii"))

    try:
        publicIdentityKey.verify(signature, message)
    except InvalidSignature:
        return None

    try:
        cipher = Cipher(algorithms.AES256(sessionKey), modes.CBC(iv))
        decryptor = cipher.decryptor()
        message = decryptor.update(message) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        message = unpadder.update(message) + unpadder.finalize()
    except ValueError:
        return None

    return message.decode("ascii")


def computeSessionKey(passphrase, salt):
    data = passphrase.encode("ascii")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return kdf.derive(data)


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


def generateIdentityKey():
    ## https://safecurves.cr.yp.to/
    return Ed25519PrivateKey.generate()


def protectKey(key, encryptionKey, hmacKey, username):
    # Encrypt-then-MAC
    serializedKey = key.private_bytes_raw()

    padder = padding.PKCS7(128).padder()
    data = padder.update(serializedKey) + padder.finalize()

    iv = getIV()
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
    path = os.path.abspath(f"./keys/{username}.key")
    if not os.path.exists(path):
        return None

    with open(f"./keys/{username}.key", "r") as f:
        key = f.readlines()
        serializedKey = base64.b64decode(key[0].encode("ascii"))
        signature = base64.b64decode(key[1].encode("ascii"))
        salt = base64.b64decode(key[2].encode("ascii"))
        iv = base64.b64decode(key[3].encode("ascii"))

    encryptionKey, hmacKey = deriveKeysFromPassword(password, salt)
    key = unprotectKey(serializedKey, encryptionKey, hmacKey, iv, signature)
    return key


def storeKey(username, password, key):
    path = os.path.abspath("./keys")
    if not os.path.exists(path):
        os.mkdir(path)

    salt = getSalt(username)
    encryptionKey, hmacKey = deriveKeysFromPassword(password, salt)
    iv, signature, serializedKey = protectKey(key, encryptionKey, hmacKey, username)

    with open(f"./keys/{username}.key", "w") as f:
        serializedKey = base64.b64encode(serializedKey).decode("ascii") + "\n"
        f.write(serializedKey)
        signature = base64.b64encode(signature).decode("ascii") + "\n"
        f.write(signature)
        salt = base64.b64encode(salt).decode("ascii") + "\n"
        f.write(salt)
        iv = base64.b64encode(iv).decode("ascii") + "\n"
        f.write(iv)

    return True


def readFiles(*filepaths):
    contents = []
    for path in filepaths:
        try:
            with open(os.path.abspath(f"{path}"), "r") as f:
                contents.append(f.read())
        except IOError:
            print(f"File not found: {os.path.abspath(f"{path}")}")
            return
    return contents


def protectCLI(args):
    message, identityKey, sessionKey = readFiles(
        args.inputFile, args.identityKey, args.sessionKey
    )

    identityKey = base64.b64decode(identityKey.encode("ascii"))
    identityKey = Ed25519PrivateKey.from_private_bytes(identityKey)

    sessionKey = base64.b64decode(sessionKey.encode("ascii"))

    message = protect(identityKey, sessionKey, message)
    with open(os.path.abspath(f"{args.outputFile}"), "w") as f:
        f.write(message)
    print("Encrypted message written to " + os.path.abspath(f"{args.outputFile}"))


def unprotectCLI(args):
    message, identityKey, sessionKey = readFiles(
        args.inputFile, args.identityKey, args.sessionKey
    )

    identityKey = base64.b64decode(identityKey.encode("ascii"))
    identityKey = Ed25519PublicKey.from_public_bytes(identityKey)

    sessionKey = base64.b64decode(sessionKey.encode("ascii"))

    message = unprotect(identityKey, sessionKey, message)
    with open(os.path.abspath(f"{args.outputFile}"), "w") as f:
        f.write(message)
    print("Decrypted message written to " + os.path.abspath(f"{args.outputFile}"))


def generateIdentityKeyCLI(args):
    key = generateIdentityKey()

    with open(os.path.abspath(os.path.abspath(f"{args.privateOutputFile}")), "w") as f:
        f.write(base64.b64encode(key.private_bytes_raw()).decode("ascii"))
    print("Private key written to " + os.path.abspath(f"{args.privateOutputFile}"))

    with open(os.path.abspath(os.path.abspath(f"{args.publicOutputFile}")), "w") as f:
        f.write(base64.b64encode(key.public_key().public_bytes_raw()).decode("ascii"))
    print("Public key written to " + os.path.abspath(f"{args.publicOutputFile}"))


def generateSessionKeyCLI(args):
    salt = getSalt()
    key = computeSessionKey(args.passphrase, salt)

    with open(os.path.abspath(os.path.abspath(f"{args.outputFile}")), "w") as f:
        f.write(base64.b64encode(key).decode("ascii"))
    print("Session key written to " + os.path.abspath(f"{args.outputFile}"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="MessagISTCrypto", description="MessagIST's cryptography tool."
    )
    subparsers = parser.add_subparsers(
        dest="command", help="Command to run.", required=True
    )

    protectParser = subparsers.add_parser("protect", help="Encrypt and sign a file.")
    protectParser.add_argument("inputFile", help="File to protect.")
    protectParser.add_argument(
        "identityKey",
        help="File containing the private key used to sign the data.",
    )
    protectParser.add_argument(
        "sessionKey",
        help="File containing the key used to encrypt the data.",
    )
    protectParser.add_argument(
        "outputFile",
        help="File to where the protected file is written.",
    )
    protectParser.set_defaults(func=protectCLI)

    unprotectParser = subparsers.add_parser(
        "unprotect", help="Decrypt and verify the integrity of a file."
    )
    unprotectParser.add_argument("inputFile", help="File to unprotect.")
    unprotectParser.add_argument(
        "identityKey",
        help="File containing the public key used to verify the data.",
    )
    unprotectParser.add_argument(
        "sessionKey",
        help="File containing the key used to decrypt the data.",
    )
    unprotectParser.add_argument(
        "outputFile",
        help="File to where the unprotected file is written.",
    )
    unprotectParser.set_defaults(func=unprotectCLI)

    generateIdentityKeyParser = subparsers.add_parser(
        "generate-identity-key",
        help="Generate a key pair that can be used to sign and verify data.",
    )
    generateIdentityKeyParser.add_argument(
        "privateOutputFile",
        help="File to where the private key is written.",
    )
    generateIdentityKeyParser.add_argument(
        "publicOutputFile",
        help="File to where the public key is written.",
    )
    generateIdentityKeyParser.set_defaults(func=generateIdentityKeyCLI)

    generateSessionKeyParser = subparsers.add_parser(
        "generate-session-key",
        help="Generate a symmetric key that can be used to encrypt and decrypt data.",
    )
    generateSessionKeyParser.add_argument(
        "passphrase", help="The passphrase used to generate this key."
    )
    generateSessionKeyParser.add_argument(
        "outputFile",
        help="File to where the key is written.",
    )
    generateSessionKeyParser.set_defaults(func=generateSessionKeyCLI)

    args = parser.parse_args()
    args.func(args)
