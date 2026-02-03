-- schema.sql
-- SQLite schema for faculty semantic search system

CREATE TABLE IF NOT EXISTS Faculty (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    profile_url TEXT,
    image_url TEXT,
    qualification TEXT,
    semantic_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Research_Tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    faculty_id INTEGER,
    tag TEXT,
    FOREIGN KEY (faculty_id) REFERENCES Faculty(id)
);
