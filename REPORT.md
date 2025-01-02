# A51 MessagIST Project Report

## 1. Introduction

(_Provide a brief overview of your project, including the business scenario and the main components: secure documents, infrastructure, and security challenge._)

MessagIST is a secure instant messaging service that aims to provide IST
students with a way of securely communicating. Since we chose to tackle the
first security challenge (Security challenge A), the security requirements for
our messaging service go beyond the basic legal requirements (GDPR). As such,
the security requirements are as follows:
1. Only the sender and receiver of a message can read it (end-to-end
   encryption).
2. The receiver of a message can confirm if whoever claims to be the sender
   actually wrote the message.
3. The conversation participants can detect if messages are out-of-order or
   missing.
4. If a user switches devices, they can recover their messages.

(_Include a structural diagram, in UML or other standard notation._)

## 2. Project Development

### 2.1. Secure Document Format

#### 2.1.1. Design

MessagIST messages must be secured before being sent to the server. Messages are
first signed using Ed25519 [\[4\]](#item4), then encrypted using AES in CBC
mode.

##### 2.1.1.1. Sign-then-encrypt

It has been argued that encrypt-then-MAC as a few benefits over the
MAC-then-encrypt strategy that we used [\[1\]](#item1). Despite these benefits,
we chose to sign first and encrypt the signature together with the message, to
minimize the information exposed to possible eavesdroppers. If instead we signed
the ciphertext and sent the signature appended to it, our messages would still
be secure, it's still impossible to know *what* we sent, but it would be
possible to confirm that we sent *something*.

(_Outline the design of your custom cryptographic library and the rationale behind your design choices, focusing on how it addresses the specific needs of your chosen business scenario._)

(_Include a complete example of your data format, with the designed protections._)

#### 2.1.2. Implementation

(_Detail the implementation process, including the programming language and cryptographic libraries used._)

(_Include challenges faced and how they were overcome._)

### 2.2. Infrastructure

#### 2.2.1. Network and Machine Setup
The infrastructure for MessagIST consists of several components:

1. Main Server

2. Client

3. Database Server: 
   Stores user and chat data (e.g message history, user login information).
   For this server we decided to use PostgreSQL it is a strong choice for
   storing user and chat data due to its robust security features, such as ACID
   compliance for data integrity. It offers advanced authentication and
   authorization, including SSL/TLS encryption for secure communication, access
   control through role-based permissions, and logging mechanisms for auditing.
   Additionally, PostgreSQL ensures reliable, scalable data storage with the
   ability to handle complex queries, making it ideal for applications that need
   to store and manage sensitive information securely.

   ADICIONAR FONTES ???
   https://satoricyber.com/postgres-security/3-pillars-of-postgresql-security/

4. Dmz Server:
   The Dmz server employs gRPC with SSL/TLS between the client and the main
   server. A server certificate is utilized to validate server´s identity and
   ensure that the communication occurs only with a trusted source
(_Provide a brief description of the built infrastructure._)

(_Justify the choice of technologies for each server._)

#### 2.2.2. Server Communication Security

(_Discuss how server communications were secured, including the secure channel solutions implemented and any challenges encountered._)

(_Explain what keys exist at the start and how are they distributed?_)

### 2.3. Security Challenge

#### 2.3.1. Challenge Overview

(_Describe the new requirements introduced in the security challenge and how they impacted your original design._)

#### 2.3.2. Attacker Model

(_Define who is fully trusted, partially trusted, or untrusted._)

(_Define how powerful the attacker is, with capabilities and limitations, i.e., what can he do and what he cannot do_)

#### 2.3.3. Solution Design and Implementation

(_Explain how your team redesigned and extended the solution to meet the security challenge, including key distribution and other security measures._)

(_Identify communication entities and the messages they exchange with a UML sequence or collaboration diagram._)

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

----
END OF REPORT
