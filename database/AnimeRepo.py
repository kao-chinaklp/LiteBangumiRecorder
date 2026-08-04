from database.manager import DatabaseManager


class AnimeRepo:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def add(self,
            bgm_id,
            name,
            name_cn,
            tags = None,
            summary = None,
            score = None,
            date = None):
        cursor = self.db.execute(
            """
            INSERT OR IGNORE INTO animation (bgm_id, name, name_cn, date, summary, score)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (bgm_id)
            DO UPDATE SET
                name = EXCLUDED.name,
                name_cn = EXCLUDED.name_cn,
                date = EXCLUDED.date,
                summary = EXCLUDED.summary,
                score = EXCLUDED.score
            """,
            (bgm_id, name, name_cn, date, summary, score),
        )

        anime_id = cursor.lastrowid

        if not anime_id:
            # 如果插入失败，说明记录已存在，获取现有记录的ID
            cursor = self.db.execute(
                """
                SELECT id FROM animation WHERE bgm_id = ?
                """,
                (bgm_id,)
            )
            anime_id = cursor.fetchone()[0]

        if tags:
            # 删除旧关系
            self.db.execute(
                """
                DELETE FROM animation_tag 
                WHERE animation_id = ?
                """, (anime_id,))

            for tag in tags:
                tag_id = self.get_or_create_tag(tag)

                # 建立关系
                self.db.execute(
                    """
                    INSERT OR IGNORE INTO animation_tag (animation_id, tag_id)
                    VALUES (?, ?)
                    """,
                    (anime_id, tag_id)
                )

        return anime_id

    def get_or_create_tag(self, tag):
        cursor = self.db.execute(
            """
            SELECT id FROM tag WHERE name = ?
            """,
            (tag,)
        )

        result = cursor.fetchone()

        if result:
            return result[0]

        cursor = self.db.execute(
            """
            INSERT OR IGNORE INTO tag(name)
            VALUES (?)
            """,
            (tag,)
        )

        return cursor.lastrowid

    def exists(self, anime_id):
        result = self.db.execute(
            """
            SELECT 1 FROM animation WHERE id = ?
            """,
            (anime_id,)
        )
        return result.fetchone() is not None

    def delete(self, anime_id):
        if not self.exists(anime_id):
            raise ValueError(f"anime_id {anime_id} does not exist")

        self.db.execute(
            """
            DELETE FROM animation WHERE id = ?
            """,
            (anime_id,)
        )

    def cleanup_unused_tags(self):
        cursor = self.db.execute(
            """
            DELETE FROM tag WHERE id NOT IN (SELECT DISTINCT tag_id FROM animation_tag)
            """
        )
        self.db.commit()

    def search(self, anime_name):
        sql = """
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
        key = f"%{anime_name}%"
        rows = self.db.execute(sql, (key, key))

        return self._format(rows)

    def search_all(self):
        cursor = self.db.execute("SELECT name, name_cn FROM animation")
        return cursor.fetchall()

    def search_all_tag(self):
        self.cleanup_unused_tags()
        cursor = self.db.execute("SELECT name FROM tag")
        return cursor.fetchall()

    def get_by_tags(self, tags, mode = "AND"):
        if not tags:
            return []

        if mode == "AND":
            return self._get_by_tags_and(tags)
        elif mode == "OR":
            return self._get_by_tags_or(tags)
        else:
            raise ValueError("mode must be 'AND' or 'OR'")

    def _get_by_tags_and(self, tags):
        placeholders = ",".join("?" * len(tags))

        sql = f"""
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
            
        JOIN animation_tag
        ON animation.id = animation_tag.animation_id
        
        JOIN tag
        ON animation_tag.tag_id = tag.id
        
        WHERE tag.name IN ({placeholders})
        
        GROUP BY animation.id
        HAVING COUNT(DISTINCT tag.id) = ?
        """

        params = tags + [len(tags)]

        rows = self.db.execute(sql, params).fetchall()

        return self._format(rows)

    def _get_by_tags_or(self, tags):
        placeholders = ",".join("?" * len(tags))

        sql = f"""
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
            
        JOIN animation_tag 
        ON animation.id = animation_tag.animation_id
            
        JOIN tag
        ON animation_tag.tag_id = tag.id
        WHERE tag.name IN ({placeholders})
        """

        rows = self.db.execute(sql, tags).fetchall()

        return self._format(rows)

    def _format(self, rows):
        result = {}

        for row in rows:
            (id_, bgm_id, name, name_cn, date, summary, score, tag) = row
            if id_ not in result:
                result[id_] = {
                    "id": id_,
                    "bgm_id": bgm_id,
                    "name": name,
                    "name_cn": name_cn,
                    "date": date,
                    "summary": summary,
                    "score": score,
                    "tags": []
                }

            if tag:
                result[id_]["tags"].append(tag)

        return list(result.values())