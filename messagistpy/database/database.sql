
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,                -- Auto-incrementing unique identifier
    username VARCHAR(255) UNIQUE NOT NULL, -- Unique username
    password_hash TEXT NOT NULL,          -- Field for hashed passwords
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
 -- Automatically set creation time
);

