# Neko CLI

> 通用包管理命令行工具，支持 PyPI、npm、自定义仓库三种包源。

## 安装

```bash
pip install xiaohondan-nekocli
```

## 使用

```bash
# 初始化项目
neko init

# 安装包
neko install requests                    # 默认从 PyPI
neko install lodash --from npm           # 从 npm
neko install my-plugin --from repo https://github.com/NekoDev/repo  # 自定义仓库
neko install ./local-package.zip         # 本地安装

# 查看已安装
neko list

# 卸载
neko remove requests

# 更新
neko update requests
neko update                              # 全部更新

# 搜索
neko search requests
```

## 命令

| 命令 | 说明 |
|------|------|
| `neko init [name]` | 初始化项目，生成 `neko.json` |
| `neko install <pkg>` | 安装包 |
| `neko list` | 列出已安装的包 |
| `neko remove <pkg>` | 卸载包 |
| `neko update [pkg]` | 更新包 |
| `neko search <keyword>` | 搜索包 |
| `neko --version` | 查看版本 |
| `neko --help` | 查看帮助 |

## 配置文件 `neko.json`

```json
{
  "name": "my-project",
  "packages": {
    "requests": {
      "source": "pypi",
      "version": "2.31.0",
      "installed_at": "2026-05-02T12:00:00"
    }
  },
  "repos": {
    "nekocraft": "https://github.com/NekoDev/nekocraft-repo"
  }
}
```
