CREATE_TABLES = """

CREATE TABLE IF NOT EXISTS animation
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bgm_id INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_cn TEXT NOT NULL,
    date TEXT,
    summary TEXT,
    score REAL
);
CREATE TABLE IF NOT EXISTS tag
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS animation_tag
(
    animation_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    
    PRIMARY KEY(animation_id, tag_id),
    
    FOREIGN KEY(animation_id) REFERENCES animation(id)
    ON DELETE CASCADE,
    FOREIGN KEY(tag_id) REFERENCES tag(id)
    ON DELETE CASCADE
);
"""