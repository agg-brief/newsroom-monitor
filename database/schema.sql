CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    category TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    text TEXT NOT NULL,
    url TEXT NOT NULL DEFAULT '',
    language TEXT NOT NULL DEFAULT 'und',
    platform TEXT NOT NULL,
    content_hash TEXT NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_posts_timestamp ON posts(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_posts_category_timestamp ON posts(category, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_posts_source_timestamp ON posts(source, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_posts_content_hash ON posts(content_hash);
