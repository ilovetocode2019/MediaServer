CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    hashed_password TEXT,
    created_at TIMESTAMP DEFAULT (now() at time zone 'utc')
);

CREATE TABLE IF NOT EXISTS files (
    id TEXT PRIMARY KEY,
    user_id INT REFERENCES users (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
    filename TEXT UNIQUE,
    views INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT (now() at time zone 'utc')
);


CREATE TABLE IF NOT EXISTS invites (
    id TEXT PRIMARY KEY,
    user_id INT REFERENCES users (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
    code TEXT,
    uses INT DEFAULT 0,
    max_uses INT DEFAULT 1,
    expires_at TIMESTAMP
);
