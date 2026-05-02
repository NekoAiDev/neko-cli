"""neko install — 安装包"""

from neko_cli.config import load, save, add_package
from neko_cli.sources import get_source, detect_source


def run(args) -> None:
    package = args.package
    source = args.source or detect_source(package)

    # 自动检测本地文件
    import os
    if os.path.exists(package) and source == "pypi":
        source = "repo"

    print(f"正在安装 {package} (来源: {source})...")

    src = get_source(source)
    kwargs = {
        "is_global": getattr(args, "is_global", False),
        "repo_url": getattr(args, "repo_url", None),
    }

    info = src.install(package, **kwargs)
    print(f"  {info.name}@{info.version} 安装成功")

    # 更新 neko.json
    config = load()
    add_package(config, info.name, source, info.version)
    save(config)

    print(f"  已记录到 neko.json")
