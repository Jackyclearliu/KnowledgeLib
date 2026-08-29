---
name: 开始使用 Kimi Code CLI
description: Kimi Code CLI 入门指南，涵盖安装、启动、常用命令、会话管理等内容
category: 指南
order: 1
---

# 开始使用 Kimi Code CLI

> Kimi Code CLI 是一个运行在终端中的 AI Agent，帮助你完成软件开发任务和日常的终端操作。

---

## 目录

- [Kimi Code CLI 是什么](#kimi-code-cli-是什么)
- [安装](#安装)
  - [脚本安装（推荐）](#脚本安装推荐)
  - [npm 安装](#npm-安装)
- [升级与卸载](#升级与卸载)
- [第一次启动](#第一次启动)
  - [配置 API 来源](#配置-api-来源)
  - [第一个对话](#第一个对话)
- [常用命令与快捷键速查](#常用命令与快捷键速查)
- [会话与上下文](#会话与上下文)
  - [会话存储](#会话存储)
  - [启动与恢复会话](#启动与恢复会话)
  - [上下文压缩](#上下文压缩)
  - [派生会话](#派生会话)
  - [导出会话](#导出会话)
- [数据存放在哪里](#数据存放在哪里)
- [下一步](#下一步)

---

## Kimi Code CLI 是什么

Kimi Code CLI 是一个运行在终端中的 AI Agent，帮助你完成软件开发任务和日常的终端操作——阅读和修改代码、执行 Shell 命令、搜索文件、抓取网页，并在执行过程中根据反馈自主规划和调整下一步行动。

它适用于以下场景：

- **编写和修改代码**：实现新功能、修复 bug、完成重构
- **理解项目**：探索陌生的代码库，解答架构和实现层面的问题
- **自动化任务**：批量处理文件、运行构建与测试、串联多个脚本

整套 CLI 以 TypeScript 编写，通过 npm 分发，运行在 Node.js 之上。

---

## 安装

> **注意**：Kimi Code CLI 为全交互式 TUI 应用，推荐在支持真彩色与连字的现代终端中运行以获得最佳体验，例如 [Kitty](https://sw.kovidgoyal.net/kitty/) 或 [Ghostty](https://ghostty.org/) 。

提供两种安装方式：官方安装脚本（推荐，无需预装 Node.js）和 npm 全局安装。

### 脚本安装（推荐）

**macOS / Linux：**

```bash
curl -fsSL https://code.kimi.com/kimi-code/install.sh | bash
```

**Windows（PowerShell）：**

```powershell
irm https://code.kimi.com/kimi-code/install.ps1 | iex
```

> **Windows 用户注意**：首次启动前还需要安装 [Git for Windows](https://git-scm.com/download/win)，Kimi Code CLI 会使用其中的 Git Bash 作为 Shell 环境。如果 Git Bash 安装在非标准路径，请把 `KIMI_SHELL_PATH` 设为 `bash.exe` 的绝对路径。

脚本会自动下载最新版本、校验 checksum，并把 `kimi` 可执行文件放到你的 PATH 中。

### npm 安装

需要 Node.js **22.19.0 或更高版本**：

```bash
node --version
npm install -g @moonshot-ai/kimi-code
```

或用 pnpm：

```bash
pnpm add -g @moonshot-ai/kimi-code
```

---

## 升级与卸载

安装完成后，验证可执行文件是否就绪：

```bash
kimi --version
```

### 升级

运行 `kimi upgrade`，CLI 会检查最新版本并展示更新选项。选择 `Install update now` 后根据当前安装来源执行升级；也可以直接用包管理器：

```bash
npm install -g @moonshot-ai/kimi-code@latest
```

### 卸载

- 脚本安装的用户：删除 `kimi` 可执行文件即可
- npm 安装的用户：

```bash
npm uninstall -g @moonshot-ai/kimi-code
```

---

## 第一次启动

进入项目目录后直接运行 `kimi` 启动交互界面：

```bash
cd your-project
kimi
```

只想执行一条指令而不进入交互界面时，使用 `-p`：

```bash
kimi -p "帮我看一下这个项目的目录结构"
```

继续上一次会话加 `-C`：

```bash
kimi -C
```

### 配置 API 来源

首次启动时需要配置 API 来源。在交互界面中输入 `/login` 进入登录流程：

```
/login
```

`/login` 会弹出平台选择器，支持两种方式：

1. **Kimi Code（OAuth）** — 验证码流程，在任意设备打开链接、登录并输入验证码即可授权
2. **Kimi Platform API 密钥** — 输入来自 [platform.kimi.com](https://platform.kimi.com) 或 [platform.kimi.ai](https://platform.kimi.ai) 的 API 密钥

需要退出登录时，输入 `/logout` 清除当前凭证。

> **使用其他 AI 供应商**：如果你想接入 Anthropic、OpenAI、Google 等其他供应商，需要直接编辑 `~/.kimi-code/config.toml` 配置 API 密钥。

### 第一个对话

登录完成后，用自然语言描述任务即可。先让它熟悉当前项目：

```
帮我看一下这个项目的目录结构，简单介绍一下每个目录是做什么的
```

Kimi Code CLI 会自动调用文件读取、搜索等工具浏览相关内容后给出回答。只读操作默认自动执行无需确认；对于会修改文件或执行 Shell 命令的操作，默认会在执行前征求确认。

也可以直接描述更具体的任务：

```
在 src/utils 里新增一个函数，用来把任意字符串转成 kebab-case，并补一个单元测试
```

Kimi Code CLI 会规划步骤、修改代码、运行测试，并在每一步告诉你它做了什么。

> **不知道能做什么？** 输入 `/help`，可以打开内置的命令和快捷键面板，按 `↑` / `↓` 翻看，`Esc` 关闭。退出时输入 `/exit`，或按 `Ctrl-C` 两次，或在输入框为空时按 `Ctrl-D`。

---

## 常用命令与快捷键速查

### 会话相关命令

| 命令 | 说明 |
|------|------|
| `/new` | 开启新会话，清空当前上下文 |
| `/sessions` | 浏览历史会话，选择恢复 |
| `/model` | 切换当前使用的模型 |
| `/compact` | 手动压缩上下文，释放 token |
| `/fork` | 派生当前会话，保留历史独立继续 |

### 最常用快捷键

| 快捷键 | 说明 |
|--------|------|
| `Esc` | 中断流式输出 / 关闭弹窗 |
| `Ctrl-C` | 中断输出；空闲时连按两次退出 |
| `Shift-Tab` | 切换 Plan 模式 |
| `Ctrl-S` | 输出中途插入消息，无需等待结束 |
| `Ctrl-O` | 折叠 / 展开工具输出 |

> 想看完整列表，输入 `/help` 或访问官方文档的斜杠命令参考和键盘快捷键页面。

---

## 会话与上下文

Kimi Code CLI 把每次对话持久化为一个「会话」，保留消息历史和元数据，可以随时关闭终端后再回来继续。

### 会话存储

所有会话保存在 `$KIMI_CODE_HOME/sessions/` 下（默认 `~/.kimi-code/sessions/`），按工作目录分组存放：

```
~/.kimi-code/
├── config.toml
├── session_index.jsonl
└── sessions/
    └── <workDirKey>/
        └── <sessionId>/
            ├── state.json
            └── agents/
                ├── main/
                │   └── wire.jsonl
                └── <subagentId>/
                    └── wire.jsonl
```

- `state.json`：会话标题、创建时间等元数据
- `agents/*/wire.jsonl`：Agent 事件流，用于会话恢复和回放

> ⚠️ **注意**：`sessions/` 目录下的文件请勿手动编辑，否则可能导致会话无法正常恢复。

### 启动与恢复会话

每次直接运行 `kimi` 都会创建新会话。以下方式可以恢复历史会话：

**继续当前目录最近的会话：**

```bash
kimi --continue
```

**恢复指定会话（通过 ID）：**

```bash
kimi --session abc123
```

**交互式浏览历史会话并选择：**

```bash
kimi --session
```

> ⚠️ `--continue` 与 `--session` 互斥。

### 在 TUI 中切换会话

不离开当前终端也可以管理会话，以下斜杠命令仅在 Agent 空闲时可用：

- `/new`（别名 `/clear`）：切换到新会话，丢弃当前上下文
- `/sessions`（别名 `/resume`）：浏览并恢复历史会话
- `/fork`：派生当前会话
- `/title <text>`（别名 `/rename`）：设置会话标题方便识别；不带参数时显示当前标题

### 上下文压缩

对话变长时，Kimi Code CLI 会在上下文接近窗口上限时自动压缩历史消息，释放 token 空间。也可以随时手动触发：

```
/compact
```

压缩时可以附带指引，告诉模型优先保留哪些信息：

```
/compact 保留与数据库迁移相关的讨论
```

### 派生会话

想在不破坏当前对话的前提下尝试新思路，使用 `/fork`：

```
/fork
```

派生后的两个会话彼此独立，互不影响，可以随时通过 `/sessions` 切回原来的会话。

> 已保存的 `/goal` 不会复制到派生会话。如果你想在派生会话中进行自主 goal 工作，需要在那里开始一个新 goal。

### 导出会话

用 `kimi export` 把会话打包为 ZIP，适合分享、归档或提交问题反馈：

```bash
kimi export <sessionId>
```

不传 `sessionId` 时导出当前目录最近的会话（有交互式确认，加 `-y` 跳过）。用 `-o` 指定输出路径：

```bash
kimi export <sessionId> -o ~/Desktop/my-session.zip
```

导出包含会话目录下的所有文件，包括诊断日志。全局诊断日志（`~/.kimi-code/logs/kimi-code.log`）默认也会打包；如不需要，加 `--no-include-global-log` 排除。

也可以在 TUI 内导出，无需离开交互界面：

- `/export-debug-zip`：产生与 `kimi export` 相同的调试 ZIP
- `/export-md`（别名 `/export`）：导出为人类可读的 Markdown 对话记录，适合分享或存档。可选接收路径参数；不带参数时写入工作目录下的 `kimi-export-<short-id>-<timestamp>.md`

> ⚠️ **注意**：导出文件可能包含代码、命令输出和路径等敏感信息，分享前请先确认内容。

---

## 数据存放在哪里

Kimi Code CLI 的本地数据默认保存在 `~/.kimi-code/` 下，包含配置文件、会话记录、日志和更新缓存。如需迁移到别处，通过 `KIMI_CODE_HOME` 环境变量指定新路径。

---

## 下一步

- **交互与输入** — 输入框操作、审批流程、Plan 模式和 YOLO 模式详解
- **常见使用案例** — 典型任务的 prompt 示例
- **在 IDE 中使用** — 与 VS Code 等编辑器集成

---

> 📚 **官方文档**：https://moonshotai.github.io/kimi-code/zh/
