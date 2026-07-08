"""包源管理器"""

from neko_cli.sources.base import BaseSource
from neko_cli.sources.pypi_source import PyPISource
from neko_cli.sources.npm_source import NpmSource
from neko_cli.sources.repo_source import RepoSource
from neko_cli.sources.uv_source import UvSource


SOURCES: dict[str, type[BaseSource]] = {
    "pypi": PyPISource,
    "npm": NpmSource,
    "uv": UvSource,
    "repo": RepoSource,
}


def get_source(name: str) -> BaseSource:
    """获取包源实例"""
    if name not in SOURCES:
        raise ValueError(f"未知的包源: {name}，可用源: {', '.join(SOURCES.keys())}")
    return SOURCES[name]()


def detect_source(package: str) -> str:
    """根据包名自动检测包源"""
    import os
    if package.startswith(("./", "../", "/", "~")) or package.endswith((".zip", ".tar.gz", ".tgz", ".whl")):
        return "repo"  # 本地文件也走 repo 源
    # 项目根目录存在 uv.lock 时，优先使用 uv
    if os.path.exists("uv.lock"):
        return "uv"
    # 默认 pypi
    return "pypi"
