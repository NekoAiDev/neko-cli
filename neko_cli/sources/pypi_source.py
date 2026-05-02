"""PyPI 包源"""

import subprocess
import json
import re

from neko_cli.sources.base import BaseSource, PackageInfo


class PyPISource(BaseSource):

    @property
    def name(self) -> str:
        return "pypi"

    def install(self, package: str, **kwargs) -> PackageInfo:
        is_global = kwargs.get("is_global", False)
        cmd = [self._pip(), "install", package, "--quiet", "--disable-pip-version-check"]
        if not is_global:
            cmd.append("--target")
            cmd.append(".neko_packages")
        self._run(cmd)
        version = self._get_latest_version(package)
        return PackageInfo(name=package, version=version or "unknown", source=self.name)

    def uninstall(self, package: str, **kwargs) -> bool:
        is_global = kwargs.get("is_global", False)
        if not is_global:
            # 本地安装：直接删除目录
            import shutil
            target = f".neko_packages/{package}"
            normalized = f".neko_packages/{package.replace('-', '_')}"
            if os.path.isdir(normalized):
                shutil.rmtree(normalized)
                return True
            if os.path.isdir(target):
                shutil.rmtree(target)
                return True
            return False
        cmd = [self._pip(), "uninstall", package, "-y", "--quiet"]
        self._run(cmd)
        return True

    def update(self, package: str, **kwargs) -> PackageInfo | None:
        is_global = kwargs.get("is_global", False)
        cmd = [self._pip(), "install", "--upgrade", package, "--quiet", "--disable-pip-version-check"]
        if not is_global:
            cmd.append("--target")
            cmd.append(".neko_packages")
        self._run(cmd)
        version = self._get_latest_version(package)
        if version:
            return PackageInfo(name=package, version=version, source=self.name)
        return None

    def search(self, keyword: str, **kwargs) -> list[PackageInfo]:
        try:
            result = subprocess.run(
                [self._pip(), "search", keyword, "--disable-pip-version-check"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                packages = []
                for line in result.stdout.strip().split("\n"):
                    match = re.match(r"^(\S+)\s+\((.+?)\)", line)
                    if match:
                        packages.append(PackageInfo(
                            name=match.group(1),
                            version=match.group(2),
                            source=self.name,
                        ))
                return packages
        except Exception:
            pass
        # pip search 不可用时，用 PyPI JSON API
        try:
            import urllib.request
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
        is_global = kwargs.get("is_global", False)
        if not is_global:
            try:
                result = subprocess.run(
                    [self._pip(), "show", package, "--target", ".neko_packages"],
                    capture_output=True, text=True
                )
            except Exception:
                return None
        else:
            result = subprocess.run(
                [self._pip(), "show", package], capture_output=True, text=True
            )
        for line in result.stdout.splitlines():
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()
        return None

    def _get_latest_version(self, package: str) -> str | None:
        try:
            import urllib.request
            url = f"https://pypi.org/pypi/{package}/json"
            req = urllib.request.Request(url, headers={"User-Agent": "neko-cli/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                return data.get("info", {}).get("version")
        except Exception:
            return None

    @staticmethod
    def _pip() -> str:
        import shutil
        return shutil.which("pip") or shutil.which("pip3") or "pip"

    @staticmethod
    def _run(cmd: list[str]) -> None:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or f"命令执行失败: {' '.join(cmd)}")


import os
