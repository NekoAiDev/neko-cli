"""neko list — 列出已安装的包"""

from neko_cli.config import load


def run(args) -> None:
    config = load()
    packages = config.get("packages", {})

    if not packages:
        print("当前没有安装任何包。")
        return

    print(f"{'包名':<30} {'版本':<16} {'来源':<8} {'安装时间'}")
    print("-" * 80)

    for name, info in packages.items():
        version = info.get("version", "-")
        source = info.get("source", "-")
        installed_at = info.get("installed_at", "-")
        if len(installed_at) > 19:
            installed_at = installed_at[:19]
        print(f"{name:<30} {version:<16} {source:<8} {installed_at}")

    print(f"\n共 {len(packages)} 个包")
