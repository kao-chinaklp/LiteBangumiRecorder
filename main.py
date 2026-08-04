from GetBangumiInfo import get_bangumi_info
from database.AnimeRepo import AnimeRepo
from database.manager import DatabaseManager


def main():
    db = DatabaseManager("anime.db")
    db.open()
    repo = AnimeRepo(db)

    cmd = """
    请输入操作序号：
    1. 添加新动画
    2. 查询所有动画
    3. 查询单个动画
    4. 查询标签
    5. 显示所有标签
    6. 删除动画
    """

    while True:
        op = int(input(cmd))
        if op == 1:
            bgm_name = input("请输入动画名字：")

            info = get_bangumi_info(bgm_name)

            print("搜索结果：")

            for i, item in enumerate(info):
                print(f"{i + 1}. {item['name']} ")

            lst = list(map(int, input("请输入目标动画序号（多个用空格分割，超过范围的值无效）：").split()))

            for idx in lst:
                if idx > len(info) or idx <= 0:
                    continue

                item = info[idx - 1]
                repo.add(
                    bgm_id = item["bgm_id"],
                    name = item["name"],
                    name_cn = item["name_cn"],
                    tags = item["meta_tags"],
                    summary = item["summary"],
                    score = item["score"],
                    date = item["date"]
                )
                print(f"已添加动画：{item['name']}")

        elif op == 2:
            cursor = repo.search_all()
            for row in cursor:
                print(row)

        elif op == 3:
            bgm_name = input("请输入动画名：")
            cursor = repo.search(bgm_name)
            for row in cursor:
                print(row)

        elif op == 4:
            tag_list = input("请输入标签（多个用空格分割)：").split()
            result = repo.get_by_tags(tag_list)
            for row in result:
                print(row)

        elif op == 5:
            tag_list =repo.search_all_tag()
            lst = []
            for row in tag_list:
                lst.append(*row)
            print(",".join(lst))

        elif op == 6:
            anime_name = input("请输入动画名：")
            lst = repo.search(anime_name)
            for i ,item in enumerate(lst):
                print(f"{i + 1}. {item['name']}")

            del_lst = list(map(int, input("相关结果如上，请输入要删除的动画的序号\n（多个用空格分割，超过范围的值无效）：").split()))
            for idx in del_lst:
                if idx < len(lst) or idx <= 0:
                    continue

                item = lst[idx - 1]
                repo.delete(item["id"])
                print(f"已删除动画：{item['name']}")

if __name__ == '__main__':
    main()