import os
import base64
import argparse
import pickle
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
    """
    Generate a salt value.

    Parameters:
    username(str): Optional username that ensures uniqueness of the salt. Default is empty string.

    Returns:
    bytes: Random salt.
    """
    salt = os.urandom(16)  # Random bytes
    salt += username.encode("ascii")  # To ensure uniqueness
    return salt


def getIV():
    """
    Generate a random Initialization Vector (IV).

    Returns:
    bytes: 16-byte random IV.
    """
    return os.urandom(16)


def protect(privateIdentityKey, sessionKey, message):
    """
    Encrypt message and genrate a digital signature (Encrypt-then-MAC).

    This function protects a plaintext message by first encrypting it with AES in CBC mode
    using a randomly generated Initialization Vector (IV) and a provided session key.
    Then, the resulting ciphertext is signed using the sender's private identity key to
    produce a digital signature. This ensures both confidentiality, integrity, and authenticity.

    Parameters:
    privateIdentityKey (Ed25519PrivateKey): Private key used to sign the message.
    sessionKey (bytes): Symmetric key used for encryption.
    message (str): Plaintext message to protect.

    Returns:
    str: Base64-encoded encrypted message, signature, and IV, separated by newlines.
    """
    message = message.encode("ascii")

    # Apply padding to ensure message size is multiple of the AES block size
    padder = padding.PKCS7(128).padder()
    message = padder.update(message) + padder.finalize()

    # Encrypt the message
    iv = getIV()  # Ensures uniqueness even if messages are the same
    cipher = Cipher(algorithms.AES256(sessionKey), modes.CBC(iv))
    encryptor = cipher.encryptor()
    message = encryptor.update(message) + encryptor.finalize()

    # Generate signature
    signature = privateIdentityKey.sign(message)

    # Concatenate all
    message = base64.b64encode(message).decode("ascii") + "\n"
    message += base64.b64encode(signature).decode("ascii") + "\n"
    message += base64.b64encode(iv).decode("ascii")

    return message


def unprotect(publicIdentityKey, sessionKey, message):
    """
    Decrypt protected message and verify its integrity (Encrypt-then-MAC).

    Parameters:
    publicIdentityKey (Ed25519PublicKey): Public key used to verify the message.
    sessionKey (bytes): Symmetric key used for decryption.
    message (str): Base64-encoded encrypted message, signature, and IV, separated by newlines.

    Returns:
    str or None: Decrypted plaintext message, or None if verification fails.
    """
    message = message.splitlines()
    iv = base64.b64decode(message[2].encode("ascii"))
    signature = base64.b64decode(message[1].encode("ascii"))
    message = base64.b64decode(message[0].encode("ascii"))

    # Verify the digital signature using the public key
    try:
        publicIdentityKey.verify(signature, message)
    except InvalidSignature:
        # If signature not valid, return None (verification failed)
        return None

    # Decrypt the message
    try:
        cipher = Cipher(algorithms.AES256(sessionKey), modes.CBC(iv))
        decryptor = cipher.decryptor()
        message = decryptor.update(message) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        message = unpadder.update(message) + unpadder.finalize()
    except ValueError:
        # If decryption or unpadding fails, return None
        return None

    return message.decode("ascii")


def computeSessionKey(passphrase, salt):
    """
    Derive cryptographic session key from a passphrase and salt.

    This function uses PBKDF2 (Password-Based Key Derivation Function 2) algorithm
    with HMAC (Hash-based Message Authentication Code) and SHA-256 to derive a secure
    cryptographic session key from a user-povided passphrase and a salt.

    Parameters:
    passphrase (str): Passphrase used for key derivation.
    salt (bytes): Unique salt to ensure secure and unique key derivation.

    Returns:
    bytes: 32-byte derived session key.
    """
    data = passphrase.encode("ascii")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,  # Ensures uniqueness even if same passphrase is chosen
        iterations=480000,
    )
    return kdf.derive(data)


def prepareForStorage(password, salt):
    """
    Derive a cryptographic key from the password and salt as it is stored in the server's database.

    Parameters:
    password (str): Password used for key derivation.
    salt (bytes): Unique salt for key derivation.

    Returns:
    bytes: 32-byte derived key.
    """

    # https://datatracker.ietf.org/doc/html/rfc7914.html#section-2
    password = password.encode("ascii")
    kdf = Scrypt(
        salt=salt,  # Ensures uniqueness even if same password is chosen
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    return kdf.derive(password)


def deriveKeysFromPassword(password, salt):
    """
    Derive HMAC and encryption keys from a password.

    Parameters:
    password (str): Password used for key derivation.
    salt (bytes): Unique salt for key derivation.

    Returns:
    tuple: A tuple that contains:
        - hmacKey (bytes): 32 bytes for HMAC operations.
        - encryptionKey (bytes): 32 bytes for encryption operations.
    """
    data = password.encode("ascii")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=64,
        salt=salt,  # Ensures uniqueness even if same password is chosen
        iterations=480000,
    )
    key = kdf.derive(data)
    hmacKey = key[:32]
    encryptionKey = key[32:]
    return hmacKey, encryptionKey


def encodeAsWords(key):
    """
    Encode a private key as a sequence of words for human-friendly storage.

    This function involves converting the key into a large integer, dividing the
    number into smaller chunks, and mapping each chunk to a corresponding word
    from a predefined word list.

    The word list (`words.txt`) is expected to be a file where each line corresponds
    to a unique word.

    Parameters:
    key (Ed25519PrivateKey): Private key to encode.

    Returns:
    list: A list where:
        - The first element is the total length of the numeric representation of the key.
        - The subsequent elements are words mapped from chunks of the numeric key.
    """
    num = str(int.from_bytes(key.private_bytes_raw(), "big"))
    numbers = [num[x : min(x + 5, len(num))] for x in range(0, len(num), 5)]
    words = [str(len(num))]
    with open("words.txt", "r") as f:
        wordList = f.readlines()
        for n in numbers:
            words.append(wordList[int(n)][:-1])
    return words


def decodeFromWords(words):
    """
    Decode a sequence of words back into a private key.

    This function does the inverse of the function `encodeAsWords`. It maps each word
    back into its corresponding numeric value, based on the same `words.txt` word list.
    This numeric values are concatenated to reconstruct the original large integer, which
    is converted back into the private key.

    Parameters:
    words (list): A list where:
        - The first element is an integer that corresponds to the total length of the numeric
          representation of the key.
        - The subsequent elements are the words encoding the key.

    Returns:
    Ed25519PrivateKey: The reconstructed private key.
    """
    try:
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
        identityKey = Ed25519PrivateKey.from_private_bytes(privateBytes)
    except Exception:
        return None
    return identityKey


def generateIdentityKey():
    """
    Generate new Ed25519 private identity key.

    Returns:
    Ed25519PrivateKey: Newly generated private identity key.
    """

    ## https://safecurves.cr.yp.to/
    return Ed25519PrivateKey.generate()


def protectLocalData(data, encryptionKey, hmacKey):
    """
    Encrypt data and generate a MAC signature (Encrypt-then-MAC).

    This function protects sensitive binary data by first encrypting it with AES-256
    in CBC mode using a randomly generated Initialization Vector (IV) and a provided
    encryption key. After encryption, the resulting ciphertext is signed with HMAC-SHA256
    and a provided HMAC key to generate a message authentication code (MAC). This ensures
    confidentiality, integrity, and authenticity.

    Parameters:
    data (bytes): Plaintext data to encrypt.
    encryptionKey (bytes): Key used for AES encryption.
    hmacKey (bytes): Key used for HMAC signature generation.

    Returns:
    tuple: A tuple containing:
        - iv (bytes): Initialization Vector used for encryption.
        - signature (bytes): HMAC signature of the encrypted data.
        - encryptedData (bytes): Encrypted data.
    """

    # Apply padding to ensure message size is multiple of the AES block size
    padder = padding.PKCS7(128).padder()
    data = padder.update(data) + padder.finalize()

    # Encrypt the data
    iv = getIV()  # Ensures uniqueness even if messages are the same
    cipher = Cipher(algorithms.AES256(encryptionKey), modes.CBC(iv))
    encryptor = cipher.encryptor()
    data = encryptor.update(data) + encryptor.finalize()

    # Generate signature
    signer = hmac.HMAC(hmacKey, hashes.SHA256())
    signer.update(data)
    signature = signer.finalize()

    return iv, signature, data


def unprotectLocalData(data, encryptionKey, hmacKey, iv, signature):
    """
    Decrypt data and verify its integrity (Encrypt-then-MAC).

    Parameters:
    data (bytes): Encrypted data to decrypt.
    encryptionKey (bytes): Key used for AES decryption.
    hmacKey (bytes): Key used for HMAC signature verification.
    iv (bytes): Initialization Vector used for encryption.
    signature (bytes): HMAC signature to veirfy.

    Returns:
    bytes or None: Decrypted plaintext data, or None if verification fails.
    """
    signer = hmac.HMAC(hmacKey, hashes.SHA256())
    signer.update(data)

    # Verify the digital signature
    try:
        signer.verify(signature)
    except InvalidSignature:
        # If signature not valid, return None (verification failed)
        return None

    # Decrypt the data
    try:
        cipher = Cipher(algorithms.AES256(encryptionKey), modes.CBC(iv))
        decryptor = cipher.decryptor()
        data = decryptor.update(data) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(data) + unpadder.finalize()
    except ValueError:
        # If decryption or unpadding fails, return None
        return None

    return data


def loadKey(username, password):
    """
    Load and decrypt a stored identity key.

    Parameters:
    username (str): Username associated with the stored key.
    password (str): Password to decrypt the key.

    Returns:
    Ed25519PrivateKey or None: The private key if decryption succeeds, or None if it fails.
    """
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
    key = unprotectLocalData(serializedKey, encryptionKey, hmacKey, iv, signature)

    # Unprotect failed
    if key is None:
        return None
    return Ed25519PrivateKey.from_private_bytes(key)


def storeKey(username, password, key):
    """
    Encrypt and store a private identity key.

    Parameters:
    username (str): Username associated with the key.
    password (str): Password used to encrypt the key.
    key (Ed25519PrivateKey): The private key to store.
    """
    path = os.path.abspath("./keys")
    if not os.path.exists(path):
        os.mkdir(path)

    salt = getSalt(username)
    encryptionKey, hmacKey = deriveKeysFromPassword(password, salt)
    iv, signature, serializedKey = protectLocalData(
        key.private_bytes_raw(), encryptionKey, hmacKey
    )

    with open(f"./keys/{username}.key", "w") as f:
        serializedKey = base64.b64encode(serializedKey).decode("ascii") + "\n"
        f.write(serializedKey)
        signature = base64.b64encode(signature).decode("ascii") + "\n"
        f.write(signature)
        salt = base64.b64encode(salt).decode("ascii") + "\n"
        f.write(salt)
        iv = base64.b64encode(iv).decode("ascii") + "\n"
        f.write(iv)


def encodeContacts(contacts):
    """
    Serialize and encode contacts for storage.

    Parameters:
    contacts (dict): A dictionary mapping partner usernames to their public keys.

    Returns:
    bytes: Serialized and pickled contacts.
    """
    serializedContacts = {}
    for partner, identityKey in contacts.items():
        serializedContacts[partner] = identityKey.public_bytes_raw()
    return pickle.dumps(serializedContacts)


def decodeContacts(serializedContacts):
    """
    Deserialize and decode contacts from storage.

    Parameters:
    serializedContacts (bytes): Serialized and pickled contacts.

    Returns:
    dict: Dictionary mapping partner usernames to their public keys.
    """
    contacts = pickle.loads(serializedContacts)
    for partner, identityKey in contacts.items():
        contacts[partner] = Ed25519PublicKey.from_public_bytes(identityKey)
    return contacts


def loadContacts(username, password):
    """
    Load and decrypt contacts from storage.

    Parameters:
    username (str): Username associated with the contacts file.
    password (str): Password used to decrypt the contacts.

    Returns:
    dict: Dictionary of contacts, or an empty dictionary if decryption fails.
    """
    path = os.path.abspath(f"./contacts/{username}.contacts")
    if not os.path.exists(path):
        return {}

    with open(f"./contacts/{username}.contacts", "r") as f:
        contacts = f.readlines()
        serializedContacts = base64.b64decode(contacts[0].encode("ascii"))
        signature = base64.b64decode(contacts[1].encode("ascii"))
        salt = base64.b64decode(contacts[2].encode("ascii"))
        iv = base64.b64decode(contacts[3].encode("ascii"))

    encryptionKey, hmacKey = deriveKeysFromPassword(password, salt)
    serializedContacts = unprotectLocalData(
        serializedContacts, encryptionKey, hmacKey, iv, signature
    )

    # Unprotect failed
    if serializedContacts is None:
        return {}
    return decodeContacts(serializedContacts)


def storeContacts(username, password, contacts):
    """
    Encrypt and store contacts.

    Parameters:
    username (str): Username associated with the contacts file.
    password (str): Password used to encrypt the contacts.
    contacts (dict): Dictionary of contacts to store.
    """
    path = os.path.abspath("./contacts")
    if not os.path.exists(path):
        os.mkdir(path)

    salt = getSalt(username)
    encryptionKey, hmacKey = deriveKeysFromPassword(password, salt)
    contacts = encodeContacts(contacts)
    iv, signature, contacts = protectLocalData(contacts, encryptionKey, hmacKey)

    with open(f"./contacts/{username}.contacts", "w") as f:
        contacts = base64.b64encode(contacts).decode("ascii") + "\n"
        f.write(contacts)
        signature = base64.b64encode(signature).decode("ascii") + "\n"
        f.write(signature)
        salt = base64.b64encode(salt).decode("ascii") + "\n"
        f.write(salt)
        iv = base64.b64encode(iv).decode("ascii") + "\n"
        f.write(iv)


def createContactsEntry(data):
    return Ed25519PublicKey.from_public_bytes(data)


def readFiles(*filepaths):
    contents = []
    for path in filepaths:
        try:
            with open(os.path.abspath(f"{path}"), "r") as f:
                contents.append(f.read())
        except IOError:
            print(f"File not found: {os.path.abspath(f"{path}")}")
            return None
    return contents


def protectCLI(args):
    contents = readFiles(args.inputFile, args.identityKey, args.sessionKey)
    if contents is None:
        return
    message, identityKey, sessionKey = contents

    identityKey = base64.b64decode(identityKey.encode("ascii"))
    identityKey = Ed25519PrivateKey.from_private_bytes(identityKey)

    sessionKey = base64.b64decode(sessionKey.encode("ascii"))

    message = protect(identityKey, sessionKey, message)
    with open(os.path.abspath(f"{args.outputFile}"), "w") as f:
        f.write(message)
    print("Encrypted message written to " + os.path.abspath(f"{args.outputFile}"))


def unprotectCLI(args):
    contents = readFiles(args.inputFile, args.identityKey, args.sessionKey)
    if contents is None:
        return
    message, identityKey, sessionKey = contents

    identityKey = base64.b64decode(identityKey.encode("ascii"))
    identityKey = Ed25519PublicKey.from_public_bytes(identityKey)

    sessionKey = base64.b64decode(sessionKey.encode("ascii"))

    message = unprotect(identityKey, sessionKey, message)
    if message is None:
        print("Verification/Decryption failed")
        return

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
