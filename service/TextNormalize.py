import re
import unicodedata

def normalize_title(title: object) -> str:
    if not title:
        return ""

    title = str(title)

    text = unicodedata.normalize('NFKD', title)

    text = re.sub(r"[^\w\u4e00-\u9fff]", "",text)

    return text.lower()