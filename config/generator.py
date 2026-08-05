from pathlib import Path
from .default import Config

def generate_config():
    config = Config()

    text = f"""
[database]
# 数据库位置
path = {config.database.path}

[search]
# 搜索结果的相似程度
threshold = {config.search.threshold}

[bangumi]
# 网络请求重试次数
try_times = {config.bangumi.try_times}
# 网络超时设置，单位为秒
timeout = {config.bangumi.timeout}
# 此项用于设置 User-Agent，请不要轻易改动
user_agent = {config.bangumi.user_agent}
"""
    Path('./config.toml').write_text(text.strip(), encoding='utf-8')