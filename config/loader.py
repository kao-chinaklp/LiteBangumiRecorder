import shutil
import tomllib
from pathlib import Path
from .config import (
    Config,
    AnimeRepoConfig,
    SearchConfig,
    BangumiConfig
)

CONFIG_DIR = Path(".")

DEFAULT_CONFIG = CONFIG_DIR / "default.toml"
USER_CONFIG = CONFIG_DIR / "config.toml"

def init_config():
    CONFIG_DIR.mkdir(exist_ok=True)

    if not USER_CONFIG.exists():
        shutil.copy(DEFAULT_CONFIG, USER_CONFIG)
        print("创建默认配置文件：", USER_CONFIG)

def load_config() -> Config:
    init_config()

    with USER_CONFIG.open("rb") as f:
        user_data = tomllib.load(f)

    return Config(
        database = AnimeRepoConfig(**user_data["database"]),
        search = SearchConfig(**user_data["search"]),
        bangumi = BangumiConfig(**user_data["bangumi"])
    )