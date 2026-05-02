"""包源管理器基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PackageInfo:
    """包信息"""
    name: str
    version: str
    source: str
    description: str = ""
    latest_version: str = ""


class BaseSource(ABC):
    """包源基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """源名称"""
        ...

    @abstractmethod
    def install(self, package: str, **kwargs) -> PackageInfo:
        """安装包"""
        ...

    @abstractmethod
    def uninstall(self, package: str, **kwargs) -> bool:
        """卸载包"""
        ...

    @abstractmethod
    def update(self, package: str, **kwargs) -> PackageInfo | None:
        """更新包，返回新版本信息"""
        ...

    @abstractmethod
    def search(self, keyword: str, **kwargs) -> list[PackageInfo]:
        """搜索包"""
        ...

    @abstractmethod
    def get_installed_version(self, package: str, **kwargs) -> str | None:
        """获取已安装版本"""
        ...
