import requests

url = "https://api.bgm.tv/v0/search/subjects"

UserAgent = {
    "User-Agent": "kao-chinaklp/BangumiFatch"
}

headers = {
    "Content-Type": "application/json",
    "User-Agent": UserAgent["User-Agent"]
}

def get_bangumi_info(bangumi_name):
    params = {
        "keyword": bangumi_name,
        "filter": {
            "type": [2] # 这里只处理动画所以是 2
        }
    }

    r = requests.post(
        url = url,
        json = params,
        headers = headers
    )

    data = r.json()

    # with open("BangumiTags.json", "w", encoding = "utf-8") as f:
    #     json.dump(data, f, ensure_ascii = False, indent = 4)

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

    # with open("BangumiInfo.json", "w", encoding = "utf-8") as f:
    #     json.dump(result, f, ensure_ascii = False, indent = 4)

    return result