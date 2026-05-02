"""neko search — 搜索包"""

from neko_cli.sources import get_source


def run(args) -> None:
    keyword = args.keyword
    source = args.source or "pypi"

    print(f"正在 {source} 搜索 '{keyword}'...\n")

    src = get_source(source)
    results = src.search(keyword)

    if not results:
        print("未找到匹配的包。")
        return

    for i, pkg in enumerate(results, 1):
        print(f"  {i}. {pkg.name}@{pkg.version}")
        if pkg.description:
            print(f"     {pkg.description}")

    print(f"\n共找到 {len(results)} 个结果")
