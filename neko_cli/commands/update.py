"""neko update — 更新包"""

from neko_cli.config import load, save, update_package
from neko_cli.sources import get_source


def run(args) -> None:
    package = args.package

    config = load()
    packages = config.get("packages", {})

    if not packages:
        print("当前没有安装任何包。")
        return

    if package:
        # 更新单个包
        pkg_info = packages.get(package)
        if not pkg_info:
            print(f"未找到包: {package}")
            return
        _update_one(config, package, pkg_info)
    else:
        # 全部更新
        for name, info in list(packages.items()):
            _update_one(config, name, info)
        print(f"\n全部更新完成，共 {len(packages)} 个包。")


def _update_one(config: dict, name: str, info: dict) -> None:
    source = info.get("source", "pypi")
    print(f"正在更新 {name} (来源: {source})...")

    try:
        src = get_source(source)
        new_info = src.update(name)
        if new_info:
            update_package(config, name, new_info.version)
            save(config)
            print(f"  {name} -> {new_info.version}")
        else:
            print(f"  {name} 已是最新版本")
    except Exception as e:
        print(f"  {name} 更新失败: {e}")
