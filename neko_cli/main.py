"""
Neko CLI 入口
"""

import sys
import argparse

from neko_cli import __version__
from neko_cli.commands import init, install, list_cmd, remove, update, search


def main():
    parser = argparse.ArgumentParser(
        prog="neko",
        description="Neko CLI - 通用包管理命令行工具",
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # neko init
    p_init = subparsers.add_parser("init", help="初始化项目")
    p_init.add_argument("name", nargs="?", default=None, help="项目名称")
    p_init.set_defaults(func=init.run)

    # neko install
    p_install = subparsers.add_parser("install", aliases=["i"], help="安装包")
    p_install.add_argument("package", help="包名或路径")
    p_install.add_argument("--from", dest="source", default=None,
                           choices=["pypi", "npm", "uv", "repo", "local"],
                           help="包源：pypi / npm / uv / repo / local")
    p_install.add_argument("--repo-url", default=None, help="自定义仓库地址（--from repo 时使用）")
    p_install.add_argument("-g", "--global", dest="is_global", action="store_true",
                           help="全局安装")
    p_install.set_defaults(func=install.run)

    # neko list
    p_list = subparsers.add_parser("list", aliases=["ls"], help="列出已安装的包")
    p_list.set_defaults(func=list_cmd.run)

    # neko remove
    p_remove = subparsers.add_parser("remove", aliases=["rm", "uninstall"], help="卸载包")
    p_remove.add_argument("package", help="包名")
    p_remove.set_defaults(func=remove.run)

    # neko update
    p_update = subparsers.add_parser("update", aliases=["up"], help="更新包")
    p_update.add_argument("package", nargs="?", default=None, help="包名（不指定则全部更新）")
    p_update.set_defaults(func=update.run)

    # neko search
    p_search = subparsers.add_parser("search", aliases=["s"], help="搜索包")
    p_search.add_argument("keyword", help="搜索关键词")
    p_search.add_argument("--from", dest="source", default="pypi",
                           choices=["pypi", "npm", "uv"],
                           help="搜索源（默认 pypi）")
    p_search.set_defaults(func=search.run)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n操作已取消。")
        sys.exit(130)
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
