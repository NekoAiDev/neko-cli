"""neko remove — 卸载包"""

from neko_cli.config import load, save, remove_package
from neko_cli.sources import get_source


def run(args) -> None:
    package = args.package

    config = load()
    pkg_info = config.get("packages", {}).get(package)

    if not pkg_info:
        print(f"未找到包: {package}")
        return

    source = pkg_info.get("source", "pypi")
    print(f"正在卸载 {package} (来源: {source})...")

    src = get_source(source)
    src.uninstall(package)

    remove_package(config, package)
    save(config)

    print(f"  {package} 已卸载")
