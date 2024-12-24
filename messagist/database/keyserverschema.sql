
CREATE TABLE IF NOT EXISTS identity_keys (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    identity_key BYTEA NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_salts (
    id SERIAL PRIMARY KEY,
    user_1 VARCHAR(255) NOT NULL,
    user_2 VARCHAR(255) NOT NULL,
    salt BYTEA NOT NULL,
    CONSTRAINT unique_chat UNIQUE (user_1, user_2), -- Ensure user_1 and user_2 combination is unique
    CONSTRAINT check_user_order CHECK (user_1 < user_2) -- Ensure user_1 is lexicographically less than user_2
);
