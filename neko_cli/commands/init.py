"""neko init — 初始化项目"""

import os

from neko_cli.config import save, DEFAULT_CONFIG


def run(args) -> None:
    name = args.name or os.path.basename(os.getcwd())
    config = DEFAULT_CONFIG.copy()
    config["name"] = name

    config_path = os.path.join(os.getcwd(), "neko.json")

    if os.path.exists(config_path):
        print(f"当前目录已有 neko.json，跳过初始化。")
        return

    save(config, config_path=config_path)
    print(f"项目 '{name}' 已初始化，配置文件: neko.json")
