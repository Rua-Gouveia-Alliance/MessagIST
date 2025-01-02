# A61 MessagIST Project Report

## 1. Introduction

MessagIST is a secure instant messaging service that aims to provide IST
students with a way of securely communicating. Our starting security
requirements were as follows:
1. Only the sender and receiver of a message can read it.
2. The receiver of a message can confirm if whoever claims to be the sender
   actually wrote the message.
3. The conversation participants can detect if messages are out-of-order or
   missing.
4. Messages are only sent to their intended receiver.

In practice, these requirements translate to:
1. Messages must be signed by their sender, each user needs an assymmetric
   key-pair.
2. Messages must be timestamped.
3. Users must authenticate themselves and establish a session with the server in
   order to receive messages.

## 2. Project Development

### 2.1. Secure Document Format

#### 2.1.1. Design

MessagIST messages must be secured before being sent to the server. First, we
append a vector-clock to the message. The message is then signed using Ed25519
[\[4\]](#item4), and encrypted using AES in CBC mode with 256-byte keys.

##### 2.1.1.1. Sign-then-encrypt

It has been argued that encrypt-then-MAC as a few benefits over the
MAC-then-encrypt strategy that we used [\[1\]](#item1). Despite these benefits,
we chose to sign first and encrypt the signature together with the message, to
minimize the information exposed to possible eavesdroppers. If instead we signed
the ciphertext and sent the signature appended to it, our messages would still
be secure, it's still impossible to know *what* we sent, but it would be
possible to confirm that we sent *something*.

##### 2.1.1.2. Ed25519

We chose to use Ed25519 to sign messages because it provides several benefits
over RSA while providing the same security. Compared to RSA, Ed2551 provides
faster signatures and key generation. Besides this, it also provides small
signatures (64 bytes) and keys much smaller than RSA (32 bytes vs. 256 or 512
bytes).

All of these benefits are appealing, but for our use case the most important one
was the key size. While our strategy for recovering assymmetric key-pairs works
for recovering keys of 32 bytes, it would not be fit to recover bigger keys,
like the ones used in RSA.

To allow the recovery of a key, we use a strategy similar to the seed phrases
used to recover cryptocurrency wallets. The private key is transformed in a list
of words that is provided to the user. This list should then be memorized or
stored somewhere safe and can be used to reconstruct the key in case the user
loses it or changes devices. For this purpose, a list of 17 words (the result of
encoding a 32-byte number as words) is not perfect, but is tolerable. A list
with 8 or 16 times this size (the result of encoding a 256 or 512-byte number as
words) is not acceptable.

##### 2.1.1.3. AES CBC

We chose to use AES because it essentially is the "standard". It is one of the
most used encryption algorithms, and, as such, it has been extensively tested.
256-byte keys are used as this is the biggest size supported by AES.

CBC was used because, since a block depends on all blocks before it and we use
a random and unique initializatoin vector, repeated plaintext blocks result in
different ciphered blocks. This is not the case with ECB, where it's possible to
detect patterns.

##### 2.1.1.4. Vector-clocks

The vector-clocks appended to the messages are used to detect potential message
unordering or replay attacks from the server. If there is a missmatch between
the ordering established by the timestamp the server assigns and the vector, the
message is dropped. A client maliciously changing their vector-clock in order to
trick their partners won't go very far, as there will be a missmatch between the
ordering estalished by the server and the vector-clock and the message will just
be dropped.

#### 2.1.2. Implementation

Everything was implemented in Python, using the
[cryptography](https://cryptography.io/en/latest/) library.

We did not face any significant challenges. The library is very well documented
and it supports all the cryptographic primitives we required, so implementing
everything was fairly straightforward.

### 2.2. Infrastructure

#### 2.2.1. Network and Machine Setup
For communications we used gRPC. We decided to use this framework because it
provides efficient object serialization, and every member of the group had used
it before.

The infrastructure for MessagIST consists of several components:
1. Main Server:
   The Main Server is located behind the DMZ in a private network and handles
   the core business logic and operations. It receives and forwards requests
   from the public server (DMZ). It also interacts with the database server for
   data storage and retrieval, providing that relevant data is securely stored
   and managed.
2. Client:
   It's a desktop application that communicates with the server located in the
   Demilitarized Zone (DMZ), the public server. It sends the request to the
   public server and waits for its response.
3. Database Server:
   It's a PostreSQL instance. This server stores user and chat data including
   message history and login information. For this server we decided to use
   PostgreSQL because it is a strong choice for storing this information due to
   its robust security features, such as ACID compliance for data integrity.
   It also offers advanced authentication and authorization, including TLS
   encryption for secure communication, access control through role-based
   permissions, and logging mechanisms for auditing. In addition, this tool had
   been studied previously, therefore every member of the group was confortable
   and had experience using it.
4. Public Server:
   This public server was implemented to act as an intermediary between clients
   and the main server, operating in a Demilitarized Zone (DMZ). It receives
   clients requests and fowards these requests to the main server and relaying
   it's response back to the client.
   The use of a public server in the DMZ reduces the attack surface of the main
   server by isolating it from direct external access.

#### 2.2.2. Server Communication Security

To guarentee communication security we used server-side TLS.
Each server has a certificate (server.crt) and a private key (server.key).
Clients establish secure connections by trusting the server's self-signed
certificate (server.crt), which they use to verify the server's authenticity.
For server-to-server communication (between the public server and the main
server) we use the same TLS setup.
The database server also communicates with the main server over a secure TLS
connection. This is set up by setting `ssl = require` in the PostgresSQL
configuration file. The database server's certificate and server key paths are
specified in the PSQL configuration file

**Key distribution**:
Between the various servers: Manual, the necessary keys were copied to the
machines requiring them.
Between the public server and clients: In practice, the distribution was also
manual. In a real world scenario, the public server's certificate would be
distributed together with the client application.

### 2.3. Security Challenge

#### 2.3.1. Challenge Overview

Since we chose to tackle the first security challenge (Security challenge A),
the security requirements for our messaging service go beyond the basic legal
requirements (GDPR). As such, the security requirements now are as follows:
1. Only the sender and receiver of a message can read it (end-to-end
   encryption).
2. The receiver of a message can confirm if whoever claims to be the sender
   actually wrote the message.
3. The conversation participants can detect if messages are out-of-order or
   missing.
4. Messages are only sent to their intended receiver.
5. If a user switches devices, they can recover their messages.

In practice, these requirements translate to:
1. The sender and receiver need to exchange a session key.
2. Messages must be signed by their sender, each user needs an assymmetric
   key-pair.
3. Messages must be timestamped.
4. Users must authenticate themselves and establish a session with the server in
   order to receive messages.
5. If a user switches devices, they must be able to recover their assymmetric
   key-pair and their session keys.

#### 2.3.2. Attacker Model

We worked under the assumption that the database is fully trusted, it will
always return the correct result of a query. The main server is also fully
trusted. The public server is partially trusted, it might be compromised and
send repeated or out-of-order messages to clients. Clients are not trusted.

#### 2.3.3. Solution Design and Implementation

Our solution was designed from the start with the security challenge in mind, as
we had already selected it at the time we started working on the project.

We now describe the complete protocol and security measures of the application.

##### 2.3.3.1. Signing Up

This is the first step required for a user wanting to use MessagIST. A private
key is generated by the client for this new user. Users are required to sign up
using their IST email, in order to confirm they are members of the IST
community. The client sends to the server a request that includes the user's
public key, their email, and their password (hidden, described below).
Two-factor authentication (described below) is used to confirm the user actually
has access to the provided email.

Upon a successful sign up, the private key is securely stored locally (described
below) and the user is shown a list of words that can be used for private key
recovery (described below).

##### 2.3.3.2. Logging In

Once the user as created an account, they can login into MessagIST. To login,
the client sends a request to the server containing the user's email and
password (hidden, described below). If the email/password pair is successfully
validated by the server, the user is requested to perform two-factor
authentication (described below) in order to complete their login.

If this is successful, the client receives a session token and a session is
established between the client and the MessagIST server (described below).

After this, the client will try to load the user's private key. If this fails,
the user is required to provide their word list in order to recover it
(described below).

##### 2.3.3.3. Sessions

Sessions are automatically established after logging in, and a user is required
to have an active session in order to send and receive messages. Sessions have
an associated *lease*, that expires after a time interval. Once this lease
expires, the session is automatically terminated by the server.

In order to renew their sessions, clients send *keepAlive* requests to the
server. These requests include the session token, so the server can confirm the
client's authenticity, and some information related to the local state of the
client. If the renewal is successful (the token is valid and the session had not
yet expired) the server uses the response to these requests to deliver new
messages to the client.

A lot of the ideas present in these sessions come from how sessions are
implemented by Chubby [\[5\]](#item5).

Session tokens are securely generated by using the python
[secrets](https://docs.python.org/3/library/secrets.html) module.

##### 2.3.3.4. Sending A Message

In order to send a message to a new conversation partner, the user inserts the
partner's username in the appropriate place and creates a new chat.

The first step performed by the client is retrieving the partner's public key
from the server.

If this is successful, the user is prompted to insert the passphrase for that
chat. The passphrase is a secret password shared by the two communicating
parties, and is used by the client to derive the session key used to encrypt the
messages.

After this, messages can be sent. Messages are sent to the server, that assigns
a timestamp to the message. The message is appended to the local chat according
to this timestamp.

The partner's public key and the conversation's session key can be securely
stored locally (described below), if the user wishes to do so when logging out.
This is done merely for convenience. If the session keys are not stored locally,
the user will need to repeat the steps outlined above in order to be able to
receive messages (add a new chat with the desired partner and insert the
passphrase).

We opted to use session keys derived from a passphrase as this is more flexible
for users. It's possible to create strong passphrases that are also memorizable
and can be exchanged verbally, if maximum secrecy is desired. If this is
impractical, it's also possible to use alternative methods to agree on the
shared secret (such as an alternative secure messaging service).

To derive a session key from the passphrase, we used the Scrypt [\[2\]](#item2)
key derivation function. This function has an advantage over other
password-based KDFs, as it is developed to be more resistant to attacks that use
custom-designed parallel circuits to brute-force the password.

##### 2.3.3.5. Receiving A Message

In order to be able to receive messages from someone, the same steps performed
for sending a message need to be executed. After properly setting up the chat
with the appropriate keys, the client receives any messages sent to that chat
automatically.

##### 2.3.3.6. Two-Factor Authentication

Both sign up and login require two-factor authentication. This is an extra
measure for protecting the user's account. Even if a user's account password is
compromised, the attacker won't be able to access the user's MessagIST account
without access to their email.

Two-factor authentication tokens are securely generated by using the python
[secrets](https://docs.python.org/3/library/secrets.html) module.

##### 2.3.3.7. Private Key Recovery

As previously mentioned, to allow the recovery of a key, we use a strategy
similar to the seed phrases used to recover cryptocurrency wallets. The private
key is transformed in a list of 1 number followed by 16 words that is provided
to the user. This list should then be memorized or stored somewhere safe and can
be used to reconstruct the key in case the user loses it or changes devices.

In practice, this is done by splitting the 32-byte number that corresponds to
the private key in numbers of 5 digits. Each 5 digit number is transformed in a
word by using it to index into a list of 99999 words.

##### 2.3.3.8. Hidding Passwords

The original password of a user should never be seen by the server. To achieve
this, we must "hide it" before sending it to the server when signing up and
logging in.

To implement this, we used the Scrypt key derivation function again.

##### 2.3.3.9. Locally Storing Sensitive Data

The user's private key and session keys must be stored in a way that is
inaccessible to others with access to the same computer.

To achieve this, we first derive two keys from the user's password using the
Scrypt key derivation function. The first key is used to cipher the data being
stored, using AES in CBC mode with 256-bit keys, as we also do when protecting
messages. The second key is used to sign the ciphertext with an HMAC, that is
stored together with the ciphered data.

Here, we use an encrypt-then-MAC strategy, as we don't have the same constraints
we have regarding messages. This approach has the benefit of allowing us to
detect if the document has been tampered with before actually decrypting
anything. This saves us time, as we can immediately discard the document instead
of first having to decrypt it, and reduces the attack surface, as tampered data
won't even be decrypted.

## 3. Conclusion

For our group, the main achievements of this work were successfully implementing 
a secure messaging application while using a variety of cryptographic techniques. 
Additionally, we implemented creative solutions that enhanced our work.
We believe that all the security requirements were satisfied.
For the future, the first step would be addressing Security Challenge B, 
which involves implementing group chats. Additionally, our passphrase protocol for 
generating session keys could be changed to something similar to the Signal protocol.
Overall, this project experience provided valuable insights into the implementation 
of cryptographic systems and secure communication protocols.

## 4. Bibliography

<a name="item1">1.</a> [Colin Percival, Encrypt-then-MAC, Daemonic Dispatches Blog, 2009](https://www.daemonology.net/blog/2009-06-24-encrypt-then-mac.html)

<a name="item2">2.</a> [Colin Percival and Simon Josefsson, The scrypt Password-Based Key Derivation Function, IETF RFC 7914, 2016](https://datatracker.ietf.org/doc/html/rfc7914.html)

<a name="item3">3.</a> [Daniel J. Bernstein and Tanja Lange, SafeCurves: choosing safe curves for elliptic-curve cryptography, 2024](https://safecurves.cr.yp.to)

<a name="item4">4.</a> [Daniel J. Bernstein, Niels Duif, Tanja Lange, Peter Schwabe and Bo-Yin Yang, Ed25519: high-speed high-security signatures, 2012](https://ed25519.cr.yp.to/index.html)

<a name="item5">5.</a> [Mike Burrows, The Chubby lock service for loosely-coupled distributed systems, 7th USENI Symposium on Operating Systems Design and Implementation (OSDI), 2012](https://static.googleusercontent.com/media/research.google.com/en//archive/chubby-osdi06.pdf)

----
END OF REPORT
