CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,                 -- Auto-incrementing unique identifier
    ist_id VARCHAR(255) UNIQUE NOT NULL, -- Unique ist_id
    password_hash BYTEA NOT NULL,          -- Field for hashed passwords
    salt BYTEA NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
 -- Automatically set creation time
);

CREATE TABLE IF NOT EXISTS chat (
    chat_id SERIAL PRIMARY KEY,
    user_1 INT NOT NULL,
    user_2 INT NOT NULL,
    FOREIGN KEY (user_1) REFERENCES users(id),
    FOREIGN KEY (user_2) REFERENCES users(id),
    CONSTRAINT unique_chat UNIQUE (user_1, user_2), -- Ensure user_1 and user_2 combination is unique
    CONSTRAINT check_user_order CHECK (user_1 < user_2)
);

CREATE TABLE IF NOT EXISTS messages (
    message_id SERIAL PRIMARY KEY,        -- Unique message identifier
    chat_id INT NOT NULL,                 -- Reference to the chat this message belongs to
    message_text TEXT NOT NULL,           -- The actual message content
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,   -- When the message was sent
    FOREIGN KEY (chat_id) REFERENCES chat(chat_id) ON DELETE CASCADE -- Link to the chat table
);

CREATE TABLE IF NOT EXISTS identity_keys (
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    identity_key BYTEA NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS chat_salts (
    id SERIAL PRIMARY KEY,
    user_1 INT NOT NULL,
    user_2 INT NOT NULL,
    salt BYTEA NOT NULL,
    FOREIGN KEY (user_1) REFERENCES users(id),
    FOREIGN KEY (user_2) REFERENCES users(id),
    CONSTRAINT unique_chat_2 UNIQUE (user_1, user_2),     -- Ensure user_1 and user_2 combination is unique
    CONSTRAINT check_user_order_2 CHECK (user_1 < user_2) -- Ensure user_1 is lexicographically less than user_2
);
