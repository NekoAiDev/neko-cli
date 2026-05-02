"""自定义仓库包源（支持 GitHub 仓库 / 本地文件 / URL）"""

import os
import subprocess
import shutil
import tempfile
import urllib.request
import zipfile

from neko_cli.sources.base import BaseSource, PackageInfo


class RepoSource(BaseSource):

    @property
    def name(self) -> str:
        return "repo"

    def install(self, package: str, **kwargs) -> PackageInfo:
        repo_url = kwargs.get("repo_url", "")
        is_local = os.path.exists(package)

        if is_local:
            return self._install_local(package)
        elif repo_url:
            return self._install_repo(package, repo_url)
        elif package.startswith("http://") or package.startswith("https://"):
            return self._install_url(package)
        else:
            raise ValueError(f"无法识别的包来源: {package}。请使用 --repo-url 指定仓库地址。")

    def uninstall(self, package: str, **kwargs) -> bool:
        target = os.path.join(".neko_packages", package)
        if os.path.isdir(target):
            shutil.rmtree(target)
            return True
        return False

    def update(self, package: str, **kwargs) -> PackageInfo | None:
        repo_url = kwargs.get("repo_url", "")
        if not repo_url:
            raise ValueError("更新仓库包需要指定 --repo-url")
        # 先卸载再重新安装
        self.uninstall(package)
        return self.install(package, **kwargs)

    def search(self, keyword: str, **kwargs) -> list[PackageInfo]:
        # 自定义仓库暂不支持搜索
        print(f"提示: 自定义仓库暂不支持搜索功能。")
        return []

    def get_installed_version(self, package: str, **kwargs) -> str | None:
        meta = os.path.join(".neko_packages", package, ".neko_meta.json")
        if os.path.exists(meta):
            import json
            with open(meta, "r", encoding="utf-8") as f:
                return json.load(f).get("version")
        return None

    def _install_local(self, path: str) -> PackageInfo:
        """从本地路径安装"""
        target = os.path.join(".neko_packages", os.path.basename(path).replace(".zip", "").replace(".tar.gz", ""))
        os.makedirs(".neko_packages", exist_ok=True)

        if os.path.isfile(path) and (path.endswith(".zip") or path.endswith(".tar.gz")):
            if path.endswith(".zip"):
                with zipfile.ZipFile(path, "r") as z:
                    z.extractall(target)
            else:
                subprocess.run(["tar", "xzf", path, "-C", target], check=True)
        elif os.path.isdir(path):
            if os.path.exists(target):
                shutil.rmtree(target)
            shutil.copytree(path, target)
        else:
            raise ValueError(f"不支持的文件格式: {path}")

        # 写入 meta
        self._write_meta(target)
        return PackageInfo(name=os.path.basename(target), version="local", source=self.name)

    def _install_repo(self, package: str, repo_url: str) -> PackageInfo:
        """从 GitHub 仓库安装"""
        target = os.path.join(".neko_packages", package)
        os.makedirs(".neko_packages", exist_ok=True)

        if os.path.exists(target):
            shutil.rmtree(target)

        # 优先用 git clone，失败则用 zip 下载
        if shutil.which("git"):
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", repo_url, target],
                    capture_output=True, text=True, check=True, timeout=60
                )
            except subprocess.CalledProcessError:
                # git clone 失败，尝试 zip
                self._download_zip(repo_url, target)
        else:
            self._download_zip(repo_url, target)

        self._write_meta(target)
        return PackageInfo(name=package, version="latest", source=self.name, description=f"来自 {repo_url}")

    def _install_url(self, url: str) -> PackageInfo:
        """从 URL 下载安装"""
        filename = url.split("/")[-1]
        tmp = os.path.join(tempfile.gettempdir(), filename)

        print(f"正在下载: {url}")
        urllib.request.urlretrieve(url, tmp)
        result = self._install_local(tmp)
        os.unlink(tmp)
        return result

    @staticmethod
    def _download_zip(repo_url: str, target: str) -> None:
        """通过 GitHub archive URL 下载"""
        download_url = repo_url.rstrip("/").replace("github.com", "codeload.github.com") + "/zip/refs/heads/main"
        tmp = os.path.join(tempfile.gettempdir(), "neko_repo.zip")
        urllib.request.urlretrieve(download_url, tmp)
        with zipfile.ZipFile(tmp, "r") as z:
            z.extractall(target)
        os.unlink(tmp)

    @staticmethod
    def _write_meta(target: str) -> None:
        import json
        from datetime import datetime
        meta = {
            "installed_at": datetime.now().isoformat(),
            "source": "repo",
        }
        with open(os.path.join(target, ".neko_meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
