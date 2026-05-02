"""neko.json 配置文件读写"""

import json
import os
from datetime import datetime
from pathlib import Path


DEFAULT_CONFIG = {
    "name": "",
    "packages": {},
    "repos": {},
}


def find_config_path() -> Path:
    """从当前目录向上查找 neko.json"""
    current = Path.cwd()
    while current != current.parent:
        config = current / "neko.json"
        if config.exists():
            return config
        current = current.parent
    return Path.cwd() / "neko.json"


def load(config_path: Path | None = None) -> dict:
    """加载配置文件"""
    path = config_path or find_config_path()
    if not path.exists():
        return DEFAULT_CONFIG.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 确保必要字段存在
        for key in DEFAULT_CONFIG:
            if key not in data:
                data[key] = DEFAULT_CONFIG[key].copy() if isinstance(DEFAULT_CONFIG[key], dict) else DEFAULT_CONFIG[key]
        return data
    except (json.JSONDecodeError, IOError):
        return DEFAULT_CONFIG.copy()


def save(data: dict, config_path: Path | None = None) -> None:
    """保存配置文件"""
    path = config_path or find_config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_package(data: dict, name: str) -> dict | None:
    """获取单个包信息"""
    return data.get("packages", {}).get(name)


def add_package(data: dict, name: str, source: str, version: str, **extra) -> None:
    """添加包记录"""
    if "packages" not in data:
        data["packages"] = {}
    data["packages"][name] = {
        "source": source,
        "version": version,
        "installed_at": datetime.now().isoformat(),
        **extra,
    }


def remove_package(data: dict, name: str) -> bool:
    """移除包记录"""
    if name in data.get("packages", {}):
        del data["packages"][name]
        return True
    return False


def update_package(data: dict, name: str, version: str) -> bool:
    """更新包版本"""
    if name in data.get("packages", {}):
        data["packages"][name]["version"] = version
        data["packages"][name]["updated_at"] = datetime.now().isoformat()
        return True
    return False
