#!/usr/bin/env node
// postinstall.js - neko-cli npm 包安装后自动配置

const { execSync } = require("child_process");
const { exec } = require("child_process");
const fs = require("fs");
const path = require("path");

console.log("\n=== neko-cli npm 包装器安装完成 ===\n");

// 1. 检测 Python
function findPython() {
  const candidates = ["py", "python3", "python"];
  for (const cmd of candidates) {
    try {
      const out = execSync(`${cmd} --version`, { encoding: "utf8" });
      if (out.includes("Python 3.")) {
        const version = out.trim().split(" ")[1];
        return { cmd, version };
      }
    } catch {
      // ignore
    }
  }
  return null;
}

const py = findPython();
if (!py) {
  console.log("⚠️  未检测到 Python 3.9+");
  console.log("请先安装 Python: https://www.python.org/downloads/");
  console.log("");
  process.exit(0);
}

console.log(`✓ 检测到 Python: ${py.version} (${py.cmd})`);

// 2. 检测 neko-cli Python 包是否已安装
try {
  execSync(`${py.cmd} -m pip show neko-cli`, { stdio: "ignore" });
  console.log("✓ neko-cli Python 包已安装");
  console.log("");
  console.log("使用方式：");
  console.log("  neko --help");
  console.log("  neko init myproject");
  console.log("");
} catch {
  console.log("⚠️  neko-cli Python 包未安装");
  console.log("");
  console.log("请运行以下命令安装 Python 包：");
  console.log(`  ${py.cmd} -m pip install neko-cli`);
  console.log("");
  console.log("安装完成后即可使用：");
  console.log("  neko --help");
  console.log("");
}