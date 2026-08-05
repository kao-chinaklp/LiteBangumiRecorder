from dataclasses import dataclass

@dataclass(slots = True)
class AnimeRepoConfig:
    path: str

@dataclass(slots = True)
class SearchConfig:
    threshold: int

@dataclass(slots = True)
class BangumiConfig:
    try_times: int
    timeout: int
    user_agent: str

@dataclass(slots = True)
class Config:
    database: AnimeRepoConfig
    search: SearchConfig
    bangumi: BangumiConfig