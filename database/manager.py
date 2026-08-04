import sqlite3
from pathlib import Path

from .schema import CREATE_TABLES

class DatabaseManager:
    DB_VERSION = 1

    def __init__(self, path):
        self.path = Path(path)
        self.conn = None
        self.cursor = None

    def open(self):
        self.connect()
        self.check_database()

    def connect(self):
        self.path.parent.mkdir(parents = True, exist_ok = True)
        self.conn = sqlite3.connect(self.path)
        self.conn.execute("PRAGMA foreign_keys = ON")

        if self.conn is None:
            raise ConnectionError("数据库连接失败")

    def check_database(self):
        version = self.get_version()

        if version == 0:
            print("初始化数据库")

            with self.conn:
                self.create_tables()
                self.set_version(1)

        elif version == 1:
            pass  # 数据库版本匹配，无需操作

        else:
            raise RuntimeError("数据库版本不匹配，当前版本：{}，期望版本：{}".format(version, self.DB_VERSION))

    def get_version(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA user_version")
        return cursor.fetchone()[0]

    def set_version(self, version: int):
        with self.conn:
            self.conn.execute("PRAGMA user_version = {}".format(version))

    def create_tables(self):
        self.conn.executescript(CREATE_TABLES)
        self.commit()

    def execute(self, sql: str, params = ()):
        # 执行单条语句
        cursor = self.conn.execute(sql, params)
        # 只有不返回结果集的语句才立即提交
        if cursor.description is None:
            self.commit()
        return cursor

    def execute_many(self, sql: str, params = ()):
        # 执行多条语句
        cursor = self.conn.executemany(sql, params)
        self.commit()
        return cursor

    def execute_script(self, sql: str, params = ()):
        # 执行脚本
        cursor = self.conn.execute(sql, params)
        self.commit()
        return cursor

    def query_one(self, sql: str, params = ()):
        # 执行查询
        return self.conn.execute(sql, params).fetchone()

    def query_all(self, sql: str, params = ()):
        return self.conn.execute(sql, params).fetchall()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None