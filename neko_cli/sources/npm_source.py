"""npm 包源"""

import subprocess
import shutil
import json

from neko_cli.sources.base import BaseSource, PackageInfo


class NpmSource(BaseSource):

    @property
    def name(self) -> str:
        return "npm"

    def install(self, package: str, **kwargs) -> PackageInfo:
        cmd = [self._npm(), "install", package, "--save", "--silent"]
        self._run(cmd)
        version = self._get_installed_version_from_pkg(package)
        return PackageInfo(name=package, version=version or "unknown", source=self.name)

    def uninstall(self, package: str, **kwargs) -> bool:
        cmd = [self._npm(), "uninstall", package, "--silent"]
        self._run(cmd)
        return True

    def update(self, package: str, **kwargs) -> PackageInfo | None:
        cmd = [self._npm(), "update", package, "--silent"]
        self._run(cmd)
        version = self._get_installed_version_from_pkg(package)
        if version:
            return PackageInfo(name=package, version=version, source=self.name)
        return None

    def search(self, keyword: str, **kwargs) -> list[PackageInfo]:
        try:
            result = subprocess.run(
                [self._npm(), "search", keyword, "--json", "--long"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                packages = []
                for item in data[:10]:
                    packages.append(PackageInfo(
                        name=item.get("name", ""),
                        version=item.get("version", ""),
                        source=self.name,
                        description=item.get("description", ""),
                    ))
                return packages
        except Exception:
            pass
        return []

    def get_installed_version(self, package: str, **kwargs) -> str | None:
        return self._get_installed_version_from_pkg(package)

    def _get_installed_version_from_pkg(self, package: str) -> str | None:
        try:
            import os
            pkg_path = os.path.join("node_modules", package, "package.json")
            if os.path.exists(pkg_path):
                with open(pkg_path, "r", encoding="utf-8") as f:
                    return json.load(f).get("version")
        except Exception:
            pass
        return None

    @staticmethod
    def _npm() -> str:
        return shutil.which("npm") or "npm"

    @staticmethod
    def _run(cmd: list[str]) -> None:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or f"命令执行失败: {' '.join(cmd)}")
