from rapidfuzz import fuzz

from config.config import Config
from database.manager import DatabaseManager
from database.schema import ADD_ANIMATION, DELETE_OLD, ADD_ANIMATION_TAG, SEARCH_TAG, ADD_TAG, \
    CLEANUP_UNUSED_TAGS, SEARCH_ALL, SEARCH_ALL_TAG, DELETE_BY_ID, SEARCH_ALL_ANIMATION, \
    SEARCH_ANIMATION_BY_ID, SEARCH_ANIMATION_BY_NAME
from service.TextNormalize import normalize_title


class AnimeRepo:
    def __init__(self, db: DatabaseManager, config: Config):
        self.db = db
        self._choices: list[tuple[int, str]] = []
        self._normalized_choices: list[str] = []
        self._animes = {}
        self._load_cache()
        self.config = config

    def _load_cache(self):
        rows = self.db.execute(SEARCH_ALL_ANIMATION).fetchall()
        for row in rows:
            anime_id = row[0]
            name = row[2]
            name_cn = row[3]

            self._animes[anime_id] = row[1]

            if name:
                self._choices.append((anime_id, name))
                self._normalized_choices.append(normalize_title(name))
            if name_cn:
                self._choices.append((anime_id, name_cn))
                self._normalized_choices.append(normalize_title(name_cn))

    def _remove_cached_anime(self, anime_id):
        filtered = [
            (choice, normalized)
            for choice, normalized in zip(self._choices, self._normalized_choices)
            if choice[0] != anime_id
        ]

        self._choices = [choice for choice, _ in filtered]
        self._normalized_choices = [normalized for _, normalized in filtered]

    def add(self,
            bgm_id,
            name,
            name_cn,
            tags = None,
            summary = None,
            score = None,
            date = None):

        summary = (summary or "").replace("\r", "").replace("\n", "")

        cursor = self.db.execute(ADD_ANIMATION, (bgm_id, name, name_cn, date, summary, score))

        row = cursor.fetchone()

        if row:
            anime_id = row[0]
        else:
            cursor = self.db.execute(SEARCH_ANIMATION_BY_ID, (bgm_id,))
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

        self._animes[anime_id] = bgm_id
        self._remove_cached_anime(anime_id)

        if name:
            self._choices.append((anime_id, name))
            self._normalized_choices.append(normalize_title(name))
        if name_cn:
            self._choices.append((anime_id, name_cn))
            self._normalized_choices.append(normalize_title(name_cn))

        return anime_id

    def get_or_create_tag(self, tag):
        cursor = self.db.execute(SEARCH_TAG, (tag,))

        result = cursor.fetchone()

        if result:
            return result[0]

        cursor = self.db.execute(ADD_TAG, (tag,))

        return cursor.lastrowid

    def delete(self, anime_name):
        res = self.db.execute(SEARCH_ANIMATION_BY_NAME, (anime_name,)).fetchone()

        if len(res) == 0:
            return

        anime_id = res[0]

        self._remove_cached_anime(anime_id)
        self._animes.pop(anime_id, None)

        self.db.execute(DELETE_BY_ID, (anime_id,))

    def cleanup_unused_tags(self):
        self.db.execute(CLEANUP_UNUSED_TAGS)

    def search(self, anime_name):
        anime_name = normalize_title(anime_name)

        if not anime_name or not self._choices:
            return []

        ranked = sorted(
            enumerate(self._normalized_choices),
            key = lambda item: fuzz.ratio(anime_name, item[1]),
            reverse = True,
        )

        results = []
        visited = set()

        for index, normalized_title in ranked:
            if anime_name in normalized_title:
                results.append(self._choices[index][1])
                visited.add(self._choices[index][0])
                continue

            score = fuzz.ratio(anime_name, normalized_title)
            if score <= self.config.search.threshold:
                continue

            anime_id, title = self._choices[index]

            if anime_id in visited:
                continue

            visited.add(anime_id)

            results.append(title)
        
        return results

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