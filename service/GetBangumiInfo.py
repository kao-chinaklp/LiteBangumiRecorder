import requests
from config.config import Config

url = "https://api.bgm.tv/v0/search/subjects"

UserAgent = {
    "User-Agent": ""
}

headers = {
    "Content-Type": "application/json",
    "User-Agent": UserAgent["User-Agent"]
}

def set_user_agent(user_agent):
    headers["User-Agent"] = user_agent

def get_bangumi_info(bangumi_name, config: Config):
    params = {
        "keyword": bangumi_name,
        "filter": {
            "type": [2] # 这里只处理动画所以是 2
        }
    }

    last_exc = None
    r = None

    for attempt in range(config.bangumi.try_times):
        try:
            r = requests.post(
                url = url,
                json = params,
                headers = headers,
                timeout = config.bangumi.timeout
            )
            r.raise_for_status()
            break
        except requests.Timeout as exc:
            last_exc = exc
            if attempt < config.bangumi.try_times - 1:
                continue
            raise TimeoutError(f"请求 Bangumi 接口超时（{config.bangumi.timeout} 秒），已重试 {config.bangumi.try_times} 次，请稍后重试") from exc
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < config.bangumi.try_times - 1:
                continue
            raise RuntimeError(f"请求 Bangumi 接口失败：{exc}") from exc

    if last_exc is not None and 'r' not in locals():
        raise RuntimeError(f"请求 Bangumi 接口失败：{last_exc}") from last_exc

    data = r.json()

    result = []

    for item in data["data"]:
        result.append({
            "name": item["name"],
            "name_cn": item["name_cn"],
            "summary": item["summary"],
            "meta_tags": item["meta_tags"],
            "date": item["date"],
            "bgm_id": item["id"],
            "score": item["rating"]["score"]
        })

    return result