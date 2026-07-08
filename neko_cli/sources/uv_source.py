"""uv 包源

uv 是 Astral 出品的极速 Python 包管理器（Rust 编写），兼容 pip 接口。
本源底层调用 `uv pip install/uninstall` 系列命令，默认将包安装到本地
隔离目录 `.neko_packages`（与 PyPISource 行为一致），全局模式使用 `--system`。
"""

import os
import re
import json
import shutil
import subprocess
import urllib.request

from neko_cli.sources.base import BaseSource, PackageInfo


def _normalize(name: str) -> str:
    """按 PEP 503 规范化包名：小写，[-_.]+ 归一为单个 -"""
    return re.sub(r"[-_.]+", "-", name).lower()


class UvSource(BaseSource):

    @property
    def name(self) -> str:
        return "uv"

    def install(self, package: str, **kwargs) -> PackageInfo:
        is_global = kwargs.get("is_global", False)
        cmd = [self._uv(), "pip", "install", package, "--quiet"]
        if not is_global:
            cmd += ["--target", ".neko_packages"]
        else:
            cmd += ["--system"]
        self._run(cmd)
        version = self._get_installed_version(package) or self._get_latest_version(package)
        return PackageInfo(name=package, version=version or "unknown", source=self.name)

    def uninstall(self, package: str, **kwargs) -> bool:
        is_global = kwargs.get("is_global", False)
        if not is_global:
            # 本地安装：直接删除目录与 dist-info
            norm = _normalize(package)
            candidates = [
                os.path.join(".neko_packages", package),
                os.path.join(".neko_packages", package.replace("-", "_")),
                os.path.join(".neko_packages", norm),
            ]
            removed = False
            for path in candidates:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    removed = True
            # 清理残留的 .dist-info
            base = ".neko_packages"
            if os.path.isdir(base):
                name_pat = norm.replace("-", "[-_]")
                for entry in os.listdir(base):
                    if re.match(rf"^{name_pat}-[^-]+\.dist-info$", entry, re.IGNORECASE):
                        shutil.rmtree(os.path.join(base, entry))
                        removed = True
            return removed
        cmd = [self._uv(), "pip", "uninstall", package, "-y", "--quiet", "--system"]
        self._run(cmd)
        return True

    def update(self, package: str, **kwargs) -> PackageInfo | None:
        is_global = kwargs.get("is_global", False)
        cmd = [self._uv(), "pip", "install", "--upgrade", package, "--quiet"]
        if not is_global:
            cmd += ["--target", ".neko_packages"]
        else:
            cmd += ["--system"]
        self._run(cmd)
        version = self._get_installed_version(package) or self._get_latest_version(package)
        if version:
            return PackageInfo(name=package, version=version, source=self.name)
        return None

    def search(self, keyword: str, **kwargs) -> list[PackageInfo]:
        # uv 没有 search 子命令，复用 PyPI JSON API（与 PyPISource 一致）
        try:
            url = f"https://pypi.org/pypi/{keyword}/json"
            req = urllib.request.Request(url, headers={"User-Agent": "neko-cli/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                info = data.get("info", {})
                return [PackageInfo(
                    name=info.get("name", keyword),
                    version=info.get("version", ""),
                    source=self.name,
                    description=info.get("summary", ""),
                )]
        except Exception:
            return []

    def get_installed_version(self, package: str, **kwargs) -> str | None:
        return self._get_installed_version(package)

    def _get_installed_version(self, package: str) -> str | None:
        base = ".neko_packages"
        if not os.path.isdir(base):
            return None
        norm = _normalize(package)
        name_pat = norm.replace("-", "[-_]")
        try:
            for entry in os.listdir(base):
                m = re.match(rf"^{name_pat}-([^-]+)\.dist-info$", entry, re.IGNORECASE)
                if m:
                    return m.group(1)
        except Exception:
            pass
        return None

    def _get_latest_version(self, package: str) -> str | None:
        try:
            url = f"https://pypi.org/pypi/{package}/json"
            req = urllib.request.Request(url, headers={"User-Agent": "neko-cli/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                return data.get("info", {}).get("version")
        except Exception:
            return None

    @staticmethod
    def _uv() -> str:
        uv = shutil.which("uv")
        if not uv:
            raise RuntimeError(
                "未检测到 uv，请先安装：https://github.com/astral-sh/uv "
                "（或使用 pip 源：neko install xxx --from pypi）"
            )
        return uv

    @staticmethod
    def _run(cmd: list[str]) -> None:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or f"命令执行失败: {' '.join(cmd)}")
