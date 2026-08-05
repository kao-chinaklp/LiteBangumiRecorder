from dataclasses import dataclass, field

@dataclass
class AnimeRepoConfig:
    path: str = "\"anime.db\""

@dataclass
class SearchConfig:
    threshold: int = 75

@dataclass
class BangumiConfig:
    try_times: int = 10
    timeout: int = 10
    user_agent: str = "\"kao-chinaklp/BangumiFatch\""

@dataclass
class Config:
    database: AnimeRepoConfig = field(default_factory=AnimeRepoConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    bangumi: BangumiConfig = field(default_factory=BangumiConfig)