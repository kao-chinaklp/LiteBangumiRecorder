import shutil
import tomllib
from pathlib import Path
from .config import (
    Config,
    AnimeRepoConfig,
    SearchConfig,
    BangumiConfig
)
from .generator import generate_config

CONFIG_PATH = Path('./config.toml')

def load_config() -> Config:
    if not CONFIG_PATH.exists():
        generate_config()
        print("创建默认配置文件：", CONFIG_PATH)

    with open(CONFIG_PATH, 'rb') as f:
        user_data = tomllib.load(f)

    return Config(
        database = AnimeRepoConfig(**user_data["database"]),
        search = SearchConfig(**user_data["search"]),
        bangumi = BangumiConfig(**user_data["bangumi"])
    )