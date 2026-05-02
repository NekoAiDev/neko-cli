#!/usr/bin/env node
// neko-cli npm wrapper
// 将命令行参数转发给 Python neko_cli 包

const { spawn } = require("child_process");
const { execSync } = require("child_process");

function findPython() {
  const candidates = ["py", "python3", "python"];
  for (const cmd of candidates) {
    try {
      execSync(`${cmd} -c "import neko_cli"`, { stdio: "ignore" });
      return cmd;
    } catch {
      // continue
    }
  }
  return null;
}

function main() {
  const python = findPython();

  if (!python) {
    console.error("错误: 未找到 Python 或 neko-cli 包未安装。");
    console.error("");
    console.error("请先运行以下命令安装 Python 包：");
    console.error("  pip install xiaohondan-nekocli");
    console.error("");
    console.error("Python 下载：https://www.python.org/downloads/");
    process.exit(1);
  }

  const args = process.argv.slice(2);
  const proc = spawn(python, ["-m", "neko_cli.main", ...args], {
    stdio: "inherit",
  });

  proc.on("exit", (code) => process.exit(code || 0));
  proc.on("error", (err) => {
    console.error("无法启动 neko:", err.message);
    process.exit(1);
  });
}

main();
