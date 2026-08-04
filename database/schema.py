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

ADD_ANIMATION = """
INSERT OR IGNORE INTO animation (bgm_id, name, name_cn, date, summary, score)
VALUES (?, ?, ?, ?, ?, ?)
ON CONFLICT (bgm_id)
DO UPDATE SET
    name = EXCLUDED.name,
    name_cn = EXCLUDED.name_cn,
    date = EXCLUDED.date,
    summary = EXCLUDED.summary,
    score = EXCLUDED.score
"""

SEARCH_ANIMATION = """
SELECT id FROM animation WHERE bgm_id = ?
"""

DELETE_OLD = """
DELETE FROM animation_tag 
WHERE animation_id = ?
"""

ADD_ANIMATION_TAG = """
INSERT OR IGNORE INTO animation_tag (animation_id, tag_id)
VALUES (?, ?)
"""

SEARCH_TAG = """
SELECT id FROM tag WHERE name = ?
"""

ADD_TAG = """
INSERT OR IGNORE INTO tag(name)
VALUES (?)
"""

IF_EXISTS = """
SELECT 1 FROM animation WHERE id = ?
"""

DELETE_BY_ID = """
DELETE FROM animation WHERE id = ?
"""

GET_ID_BY_NAME = """
SELECT id FROM animation WHERE name = ?
"""

DELETE_ANIMATION = """
DELETE FROM animation WHERE id = ?
"""

CLEANUP_UNUSED_TAGS = """
DELETE FROM tag WHERE id NOT IN (SELECT DISTINCT tag_id FROM animation_tag)
"""

SEARCH_ANIMATION_BY_NAME = """
SELECT
animation.id,
animation.bgm_id,
animation.name,
animation.name_cn,
animation.date,
animation.summary,
animation.score,

tag.name

FROM animation

LEFT JOIN animation_tag
ON animation.id = animation_tag.animation_id
LEFT JOIN tag
ON animation_tag.tag_id = tag.id
WHERE animation.name LIKE ? OR animation.name_cn LIKE ?
"""

SEARCH_ALL = """
SELECT name, name_cn FROM animation
"""

SEARCH_ALL_TAG = """
SELECT name FROM tag
"""