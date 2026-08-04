from database.manager import DatabaseManager
from database.schema import ADD_ANIMATION, SEARCH_ANIMATION, DELETE_OLD, ADD_ANIMATION_TAG, SEARCH_TAG, ADD_TAG, \
    CLEANUP_UNUSED_TAGS, SEARCH_ANIMATION_BY_NAME, SEARCH_ALL, SEARCH_ALL_TAG, IF_EXISTS, DELETE_BY_ID


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

        cursor = self.db.execute(ADD_ANIMATION, (bgm_id, name, name_cn, date, summary, score))

        row = cursor.fetchone()

        if row:
            anime_id = row[0]
        else:
            cursor = self.db.execute(SEARCH_ANIMATION, (bgm_id,))
            res = cursor.fetchone()
            if not res:
                raise RuntimeError(f"Failed to insert or find anime with bgm_id {bgm_id}")
            anime_id = res[0]

        if tags:
            # 删除旧关系
            self.db.execute(DELETE_OLD,  (anime_id,))

            for tag in tags:
                tag_id = self.get_or_create_tag(tag)

                # 建立关系
                self.db.execute(ADD_ANIMATION_TAG, (anime_id, tag_id))

        return anime_id

    def get_or_create_tag(self, tag):
        cursor = self.db.execute(SEARCH_TAG, (tag,))

        result = cursor.fetchone()

        if result:
            return result[0]

        cursor = self.db.execute(ADD_TAG, (tag,))

        return cursor.lastrowid

    def exists(self, anime_id):
        result = self.db.execute(IF_EXISTS, (anime_id,))
        return result.fetchone() is not None

    def delete(self, anime_id):
        if not self.exists(anime_id):
            raise ValueError(f"anime_id {anime_id} does not exist")

        self.db.execute(DELETE_BY_ID, (anime_id,))

    def cleanup_unused_tags(self):
        self.db.execute(CLEANUP_UNUSED_TAGS)

    def search(self, anime_name):
        key = f"%{anime_name}%"
        cursor = self.db.execute(SEARCH_ANIMATION_BY_NAME, (key, key))
        
        rows = cursor.fetchall()
        
        if not rows:
            return ["找不到该动画"]

        return self._format(rows)

    def search_all(self):
        cursor = self.db.execute(SEARCH_ALL)
        return cursor.fetchall()

    def search_all_tag(self):
        self.cleanup_unused_tags()
        cursor = self.db.execute(SEARCH_ALL_TAG)
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