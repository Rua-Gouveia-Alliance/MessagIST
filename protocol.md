# Protocol
## Structure
* 4 Vms: 1 Server, 2 Clients, 1 DB.

## Client
### Application Startup
1. Establish TLS (Server Authentication) connection with the server.

### Account creation
1. Create a username and a password.
2. Create a `SIGNUP` request: Username, hash(password).
3. Send the request to the server through the secure TLS connection.
4. Receive the certificate and store it in persistent storage.

### Logging in
1. Provide username and password.
2. Create a `LOGIN` request: Username and hash(password).
3. Send the request to the server through the secure TLS connection.
4. Receive the session token and a list of the client's chat IDs.

### Creating a chat (First Half)
1. Create a `CHAT` request: Recipient username, session token.
2. Send the request to the server through the secure TLS connection.
3. Receive the chat ID.

### Creating a chat (Second Half; Key Exchange)
**TODO**: preciso expandir esta explicacao
1. Compute the chat key by performing a key exchange protocol with the
   desired user.
2. Store the chat key in persistent storage (?).
3. Compute the signing key by performing a key exchange protocol with the
   desired user.
4. Store the signing key in persistent storage (?).

### Sending a message
1. If a chat has not been yet created: create a chat.
2. Create a message to send.
3. Protect the message.
4. Create a `MESSAGE` request: Chat ID, protected message, session token.
7. Send the request to the server through the secure TLS connection.
8. Receive the message global timestamp.
9. Append to the chat accordingly.

**TODO**: 8. e 9. fazem sentido ou ha maneiras melhores?

### Receiving a message
1. Validate message.
2. Compare the timestamp with what we have locally.
3. If less, drop the message (we already received it).
4. If more, buffer it until we eventually receive the missing messages.
5. If it matches, append it to the chat.

### Sessions
* Periodically send `KEEPALIVE` requests to preserve the session.
* All operations besides signing up and logging in require an established
  session.
* Messages are delivered through the responses to the `KEEPALIVE` requests.
  The requests include a list of the client's chat ID's and the amount of
  messages it has received for each chat.
* At application startup, the client will have all chat's empty (messages are
  not stored locally). As such, the answer to the first `KEEPALIVE` will contain
  all old messages.

**TODO**: Nao e mto bom se tiver mtas mensages, talvez seja melhor fazer uma
  especie de cache local onde se vao guardando chats e depois quando a aplicacao
  liga o estado esta mais atualizado (tipo whatsapp no pc).

## Server
### Account creation
1. Receive a `SIGNUP` request: Username, hash(password).
2. Validate the request.
3. Store in the Database the username, hash(password).

### Logging in
1. Receive a `LOGIN` request: Username and hash(password).
2. Validate request.
3. Compute session token.
4. Answer with session token and a list of the client's chat ID's.

### Creating a chat (First Half)
1. Receive a `CHAT` request: Recipient username, session token.
2. Validate the request.
3. Compute the chat ID.
4. Create a new entry in the DB for that chat ID.
5. Answer with chat ID.

### Sending a message
1. Receive a `MESSAGE` request: Chat ID, protected message, session token.
2. Validate request.
3. Append the to the chat in the DB.
4. Calculate the timestamp.
5. Answer the message request with the timestamp.

### Keep Alive
1. Renew session lease.
2. Answer with any pending messages.

## Protecting Messages
1. Sign with HMAC using the signing key:
     - CBC-MAC: Not adequate for messages of variable length.
     - Keyed Hash: Vulnerable to extension attacks.
2. Add nonce (timestamp works as nonce ?).
3. Cipher with AES in CBC using the chat key.
4. Use two different keys because its bad practice reusing keys.

**TODO**: Temos uma diferente para sign e outra para cifrar, mas vamos estar a
reutilizar estas duas ao longo do chat todo. É mau?
