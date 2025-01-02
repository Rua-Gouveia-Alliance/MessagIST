# A51 MessagIST Project Report

## 1. Introduction

(_Provide a brief overview of your project, including the business scenario and the main components: secure documents, infrastructure, and security challenge._)

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

(_Include a structural diagram, in UML or other standard notation._)

TODO

## 2. Project Development

### 2.1. Secure Document Format

#### 2.1.1. Design

(_Outline the design of your custom cryptographic library and the rationale behind your design choices, focusing on how it addresses the specific needs of your chosen business scenario._)

MessagIST messages must be secured before being sent to the server. Messages are
first signed using Ed25519 [\[4\]](#item4), then encrypted using AES in CBC
mode with 256-byte keys.

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

##### 2.1.1.2. AES CBC

We chose to use AES because it essentially is the "standard". It is one of the
most used encryption algorithms, and, as such, it has been extensively tested.
256-byte keys are used as this is the biggest size supported by AES.

CBC was used because, since a block depends on all blocks before it and we use
a random and unique initializatoin vector, repeated plaintext blocks result in
different ciphered blocks. This is not the case with ECB, where it's possible to
detect patterns.

(_Include a complete example of your data format, with the designed protections._)

TODO

#### 2.1.2. Implementation

(_Detail the implementation process, including the programming language and cryptographic libraries used._)

Everything was implemented in Python, using the
[cryptography](https://cryptography.io/en/latest/) library.

(_Include challenges faced and how they were overcome._)

We did not face any significant challenges. The library is very well documented
and it supports all the cryptographic primitives we required, so implementing
everything was fairly straightforward.

### 2.2. Infrastructure

#### 2.2.1. Network and Machine Setup
The infrastructure for MessagIST consists of several components:

1. Main Server:
   The Main Server is located behind the DMZ in a private network and handles the core business logic and operations. 
   The Main Server receives and forwards requests from the Public Server (DMZ), with the communication between these 
   servers being secured using TLS encryption. This ensures that all data transmitted between the servers is protected 
   from potential interception or tampering.
   Once the Main Server receives requests from the Public Server, it processes them based on the business logic.
   It then interacts with the Database Server for data storage and retrieval, providing that relevant data is securely 
   stored and managed. The interaction with the Database Server is done using secure database connections.
   The server uses gRPC for communication. 
   Additionally, the Main Server interacts with the Public Server, receiving its requests and processing them . 
   Once the Main Server has completed its tasks, it sends the responses back to the Public Server. T
   he communication between the Public Server and the Main Server is fully secured with TLS, 
   ensuring that the integrity and confidentiality of the data are maintained at all times.
   A self-signed certificate (server.crt) is used for server authentication, safeguarding trust between entities.

2. Client:
   It's a desktop application that communicates with the server located in the Demilitarized Zone (DMZ), the public server.
   It sends the request to the public server and waits for its response. 
   All the communications are secured using TLS, which guarantees that all communication between the server and the client 
   are encryted.
   The server's certificate is used to ensure that the client is connected to the correct server, minimizing the risks of
   man-in-the-middle attacks.

3. Database Server:
   It's a PostreSQL instance hosted in a secure server.
   It includes TLS Encryption: The server certificate in /keys folder 
   guarantee that the communications between the client and the server is encrypted 
   and secure. The SSL Mode is require in the code. 
   This server stores user and chat data including message history and login information.
   For this server we decided to use PostgreSQL because it is a strong choice for
   storing this information due to its robust security features, such as ACID
   compliance for data integrity. 
   It also offers advanced authentication and authorization, including TLS 
   encryption for secure communication, access control through role-based permissions, 
   and logging mechanisms for auditing. Also, PostgreSQL ensures reliable, 
   scalable data storage with the
   ability to handle complex queries. 
   In addition, this tool had been studied previously, therefore every member
   of the group was confortable and had experience using it.
   We choose the psycopg library, that is a PostgreSQL adapter for Python, 
   that allows Python applications to interact with PostgreSLQ. The reason why
   we choose this library it is because of its performance, security: Supports parameterized queries, 
   protecting against SQL injection attacks and flexibility.
   ADICIONAR FONTES ???
   https://satoricyber.com/postgres-security/3-pillars-of-postgresql-security/

4. Public Server:
   This public server was implemented to act as an intermediary between clients and the main server, operating in a Demilitarized Zone (DMZ).
   It helps to isolate the main server to direct exposere TODO , providing an extra layer of security.
   It is a gRPC-based secure messaging design to facilitate the communciation between clients and a 
   main server. It garantees secure data transfer using SSL  for both client-server and server-server communication.
   It receives clients requests and fowards this request to the main server waiting for the main server´s response. 
   When it receives this response from the main server it relays this response back to the client.
   A self-signed certificate (server.crt) is used for server authentication, safeguarding trust between entities.
   We decided to implement this because the setup reduces the attack surface, as the main server is shielded behind the public Server.
   It also enables scability 
(_Provide a brief description of the built infrastructure._)

(_Justify the choice of technologies for each server._)

#### 2.2.2. Server Communication Security

(_Discuss how server communications were secured, including the secure channel solutions implemented and any challenges encountered._)

(_Explain what keys exist at the start and how are they distributed?_)

### 2.3. Security Challenge

#### 2.3.1. Challenge Overview

(_Describe the new requirements introduced in the security challenge and how they impacted your original design._)

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

(_Define who is fully trusted, partially trusted, or untrusted._)

(_Define how powerful the attacker is, with capabilities and limitations, i.e., what can he do and what he cannot do_)

#### 2.3.3. Solution Design and Implementation

(_Explain how your team redesigned and extended the solution to meet the security challenge, including key distribution and other security measures._)

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
password (hidden). If the email/password pair is successfully validated by the
server, the user is requested to perform two-factor authentication (described
below) in order to complete their login.

If this is successful, the client receives a session token and a session is
established between the client and the MessagIST server (described below).

After this, the client will try to load the users private key. If this fails,
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

The first step for sending a message to a new conversation partner, is
retrieving the partner's public key from the server.

If this is successful, the user is prompted to insert the passphrase for that
chat. The passphrase is a secret password shared by the two communicating
parties, and is used to derive the session key used to encrypt the messages.

We opted to use session keys derived from a passphrase as this is more flexible
for users. It's possible to create strong passphrases that are also memorizable
and can be exchanged verbally, if maximum secrecy is desired. If this is
impractical, it's also possible to use alternative methods to agree on the
shared secret (such as an alternative secure messaging service).

To derive a session key from the passphrase, the PBKDF2 algorithm with HMAC and
SHA-256 is used.

(_Identify communication entities and the messages they exchange with a UML sequence or collaboration diagram._)

TODO

## 3. Conclusion

(_State the main achievements of your work._)

(_Describe which requirements were satisfied, partially satisfied, or not satisfied; with a brief justification for each one._)

(_Identify possible enhancements in the future._)

(_Offer a concluding statement, emphasizing the value of the project experience._)

## 4. Bibliography

(_Present bibliographic references, with clickable links. Always include at least the authors, title, "where published", and year._)

<a name="item1">1.</a> [Colin Percival, Encrypt-then-MAC, Daemonic Dispatches Blog, 2009](https://www.daemonology.net/blog/2009-06-24-encrypt-then-mac.html)

<a name="item2">2.</a> [Colin Percival and Simon Josefsson, The scrypt Password-Based Key Derivation Function, IETF RFC 7914, 2016](https://datatracker.ietf.org/doc/html/rfc7914.html)

<a name="item3">3.</a> [Daniel J. Bernstein and Tanja Lange, SafeCurves: choosing safe curves for elliptic-curve cryptography, 2024](https://safecurves.cr.yp.to)

<a name="item4">4.</a> [Daniel J. Bernstein, Niels Duif, Tanja Lange, Peter Schwabe and Bo-Yin Yang, Ed25519: high-speed high-security signatures, 2012](https://ed25519.cr.yp.to/index.html)

<a name="item5">5.</a> [Mike Burrows, The Chubby lock service for loosely-coupled distributed systems, 7th USENI Symposium on Operating Systems Design and Implementation (OSDI), 2012](https://static.googleusercontent.com/media/research.google.com/en//archive/chubby-osdi06.pdf)

----
END OF REPORT
