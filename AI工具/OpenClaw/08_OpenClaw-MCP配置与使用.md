---
description: OpenClaw MCP Server 配置、管理与使用全指南，包含三个核心 MCP 服务的安装配置、验证方法、工具使用方式，以及 OpenClaw 自身作为 MCP Server 对外提供的能力
---

# OpenClaw MCP 配置与使用手册

> 本文档基于 OpenClaw 2026.5.20 版本，涵盖 MCP Server 的 CLI 命令、配置项详解、三个核心服务（GitHub / Playwright / Context7）的安装与验证流程、MCP 工具的使用方式，以及 OpenClaw 自身作为 MCP Server 对外暴露的能力。  
> **适用版本**：OpenClaw 2026.5.20+

---

## 目录

- [OpenClaw MCP 配置与使用手册](#openclaw-mcp-配置与使用手册)
  - [目录](#目录)
  - [一、MCP 概述](#一mcp-概述)
    - [1.1 什么是 MCP](#11-什么是-mcp)
    - [1.2 OpenClaw 与 MCP 的双向角色](#12-openclaw-与-mcp-的双向角色)
  - [二、MCP CLI 命令详解](#二mcp-cli-命令详解)
    - [2.1 命令总览](#21-命令总览)
    - [2.2 openclaw mcp list](#22-openclaw-mcp-list)
    - [2.3 openclaw mcp show](#23-openclaw-mcp-show)
    - [2.4 openclaw mcp set](#24-openclaw-mcp-set)
    - [2.5 openclaw mcp unset](#25-openclaw-mcp-unset)
    - [2.6 openclaw mcp serve](#26-openclaw-mcp-serve)
  - [三、MCP 配置项详解](#三mcp-配置项详解)
    - [3.1 配置存储位置](#31-配置存储位置)
    - [3.2 mcp.servers 结构](#32-mcpservers-结构)
    - [3.3 传输方式对比](#33-传输方式对比)
    - [3.4 mcp.sessionIdleTtlMs](#34-mcpsessionidlettlms)
    - [3.5 Codex 投影控制（可选）](#35-codex-投影控制可选)
    - [3.6 环境变量安全过滤](#36-环境变量安全过滤)
  - [四、核心 MCP 服务配置实战](#四核心-mcp-服务配置实战)
    - [4.1 前置条件](#41-前置条件)
    - [4.2 GitHub MCP Server](#42-github-mcp-server)
    - [4.3 Playwright MCP Server](#43-playwright-mcp-server)
    - [4.4 Context7 MCP Server](#44-context7-mcp-server)
    - [4.5 一键安装脚本](#45-一键安装脚本)
    - [4.6 关于 Git MCP 的说明](#46-关于-git-mcp-的说明)
  - [五、验证 MCP 配置](#五验证-mcp-配置)
    - [5.1 查看已配置服务](#51-查看已配置服务)
    - [5.2 查看单个服务详情](#52-查看单个服务详情)
    - [5.3 查看完整配置文件](#53-查看完整配置文件)
    - [5.4 使用 openclaw doctor 诊断](#54-使用-openclaw-doctor-诊断)
    - [5.5 验证工具是否加载](#55-验证工具是否加载)
  - [六、使用已配置的 MCP 服务](#六使用已配置的-mcp-服务)
    - [6.1 工具命名规则](#61-工具命名规则)
    - [6.2 工具可用性控制](#62-工具可用性控制)
    - [6.3 各服务工具示例](#63-各服务工具示例)
    - [6.4 沙箱模式下的 MCP 工具](#64-沙箱模式下的-mcp-工具)
    - [6.5 斜杠命令管理 MCP](#65-斜杠命令管理-mcp)
  - [七、OpenClaw 作为 MCP Server](#七openclaw-作为-mcp-server)
    - [7.1 使用场景](#71-使用场景)
    - [7.2 工作原理](#72-工作原理)
    - [7.3 启动方式](#73-启动方式)
    - [7.4 对外暴露的 MCP 工具](#74-对外暴露的-mcp-工具)
    - [7.5 Event 模型](#75-event-模型)
    - [7.6 Claude Channel 通知模式](#76-claude-channel-通知模式)
    - [7.7 MCP 客户端配置示例](#77-mcp-客户端配置示例)
    - [7.8 安全边界](#78-安全边界)
  - [八、故障排除](#八故障排除)
    - [8.1 MCP 工具未出现](#81-mcp-工具未出现)
    - [8.2 GitHub 操作失败](#82-github-操作失败)
    - [8.3 Playwright 启动失败](#83-playwright-启动失败)
    - [8.4 Context7 连接失败](#84-context7-连接失败)
    - [8.5 serve 模式无对话返回](#85-serve-模式无对话返回)
  - [九、参考链接](#九参考链接)

---

## 一、MCP 概述

### 1.1 什么是 MCP

**MCP（Model Context Protocol）** 是由 Anthropic 推出的开放协议，用于标准化 AI 模型与外部工具、数据源之间的交互。通过 MCP，AI Agent 可以：

- 调用外部 API 和服务
- 操作浏览器进行自动化测试
- 搜索和索引代码库
- 与文件系统、数据库等本地资源交互

MCP 采用客户端-服务器架构：MCP Client（如 Claude Desktop、OpenClaw）连接到 MCP Server（如 GitHub MCP Server），通过标准化的 JSON-RPC 2.0 消息交换来调用工具。

### 1.2 OpenClaw 与 MCP 的双向角色

OpenClaw 在 MCP 生态中扮演**双重角色**：

| 角色 | 说明 | 对应命令 |
|------|------|----------|
| **MCP Client** | OpenClaw 作为客户端，连接并消费外部 MCP Server 提供的工具 | `openclaw mcp list/show/set/unset` |
| **MCP Server** | OpenClaw 作为服务端，将自身的对话通道暴露给其他 MCP Client（如 Claude Code、Codex） | `openclaw mcp serve` |

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw Gateway                         │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │   MCP Client 角色    │    │     MCP Server 角色          │ │
│  │  (消费外部工具)       │    │  (暴露对话通道给外部客户端)    │ │
│  │                     │    │                             │ │
│  │  ← GitHub MCP       │    │  Claude Code →              │ │
│  │  ← Playwright MCP   │    │  Codex →                    │ │
│  │  ← Context7 MCP     │    │  其他 MCP Client →           │ │
│  └─────────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、MCP CLI 命令详解

### 2.1 命令总览

```bash
openclaw mcp [options] [command]

Manage OpenClaw MCP config and channel bridge

Commands:
  list        List configured MCP servers
  serve       Expose OpenClaw channels over MCP stdio
  set         Set one configured MCP server from a JSON object
  show        Show one configured MCP server or the full MCP config
  unset       Remove one configured MCP server
```

### 2.2 openclaw mcp list

列出所有已配置的 MCP Server。

```bash
# 人类可读格式
openclaw mcp list

# JSON 格式输出
openclaw mcp list --json
```

示例输出：
```
github
playwright
context7
```

### 2.3 openclaw mcp show

查看单个或全部 MCP Server 的配置详情。

```bash
# 查看完整 MCP 配置块
openclaw mcp show

# 查看指定服务
openclaw mcp show github

# JSON 格式输出
openclaw mcp show github --json
openclaw mcp show --json          # 输出完整 mcp 配置
```

### 2.4 openclaw mcp set

添加或更新一个 MCP Server 配置。

```bash
openclaw mcp set <name> <value>

# 参数：
#   name   - MCP server 名称（如 github）
#   value  - JSON 对象字符串
```

示例：

```bash
# stdio 传输方式（本地命令）
openclaw mcp set context7 '{"command":"uvx","args":["context7-mcp"]}'

# 带环境变量
openclaw mcp set github '{"command":"npx","args":["-y","@modelcontextprotocol/server-github"],"env":{"GITHUB_PERSONAL_ACCESS_TOKEN":"ghp_xxx"}}'

# HTTP/SSE 传输方式（远程服务）
openclaw mcp set docs '{"url":"https://mcp.example.com","transport":"streamable-http"}'
```

> **注意**：`openclaw mcp set` 只读写配置，**不会**连接到目标服务器验证其是否可达。运行时适配器决定在执行时支持哪些传输形状。

### 2.5 openclaw mcp unset

删除一个已配置的 MCP Server。

```bash
openclaw mcp unset <name>

# 示例
openclaw mcp unset context7
```

> 如果命名的服务器不存在，命令会报错失败。

### 2.6 openclaw mcp serve

将 OpenClaw 自身作为 MCP Server 暴露，使外部 MCP Client（如 Claude Code、Codex）可以通过 stdio 与 OpenClaw 的对话通道交互。

```bash
openclaw mcp serve [options]
```

| 选项 | 说明 |
|------|------|
| `--url <url>` | Gateway WebSocket URL（默认使用 `gateway.remote.url`） |
| `--token <token>` | Gateway 认证 Token |
| `--token-file <path>` | 从文件读取 Token |
| `--password <password>` | Gateway 密码 |
| `--password-file <path>` | 从文件读取密码 |
| `--claude-channel-mode <mode>` | Claude 通道通知模式：`auto`（默认）、`on`、`off` |
| `-v, --verbose` | 详细日志输出到 stderr |

使用示例：

```bash
# 本地 Gateway
openclaw mcp serve

# 远程 Gateway（Token 认证）
openclaw mcp serve --url wss://gateway-host:18789 \
  --token-file ~/.openclaw/gateway.token

# 远程 Gateway（密码认证）
openclaw mcp serve --url wss://gateway-host:18789 \
  --password-file ~/.openclaw/gateway.password

# 关闭 Claude 通知模式，仅使用标准 MCP 工具
openclaw mcp serve --claude-channel-mode off

# 详细日志
openclaw mcp serve --verbose
```

---

## 三、MCP 配置项详解

### 3.1 配置存储位置

MCP 配置存储在 OpenClaw 主配置文件的 `mcp` 键下：

```
~/.openclaw/openclaw.json
```

配置路径：`mcp.servers.<name>`

### 3.2 mcp.servers 结构

```json5
{
  "mcp": {
    "sessionIdleTtlMs": 600000,
    "servers": {
      "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {
          "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx"
        }
      },
      "playwright": {
        "command": "npx",
        "args": ["-y", "@executeautomation/playwright-mcp-server"]
      },
      "context7": {
        "command": "npx",
        "args": ["-y", "@upstash/context7-mcp"],
        "env": {
          "CONTEXT7_API_KEY": "ctx7sk-xxx"
        }
      },
      "remote-docs": {
        "url": "https://mcp.example.com",
        "transport": "streamable-http",
        "headers": {
          "Authorization": "Bearer <token>"
        },
        "connectionTimeoutMs": 10000
      }
    }
  }
}
```

### 3.3 传输方式对比

OpenClaw 支持三种 MCP 传输方式：

| 传输方式 | 配置字段 | 适用场景 | 必需字段 |
|----------|----------|----------|----------|
| **stdio** | 默认（省略 `transport`） | 本地命令/子进程 | `command` |
| **sse** | 省略 `transport` 或显式使用 | 远程 HTTP SSE 服务 | `url` |
| **streamable-http** | `"transport": "streamable-http"` | 远程 HTTP 流式服务 | `url` + `transport` |

**stdio 传输字段：**

| 字段 | 说明 |
|------|------|
| `command` | 要启动的可执行文件（必需） |
| `args` | 命令行参数数组 |
| `env` | 额外的环境变量 |
| `cwd` / `workingDirectory` | 进程工作目录 |

**SSE / HTTP 传输字段：**

| 字段 | 说明 |
|------|------|
| `url` | 远程服务器 HTTP/HTTPS URL（必需） |
| `headers` | HTTP 头键值对（如认证 Token） |
| `connectionTimeoutMs` | 连接超时（毫秒，可选） |

**Streamable HTTP 传输字段：**

| 字段 | 说明 |
|------|------|
| `url` | 远程服务器 URL（必需） |
| `transport` | 必须设为 `"streamable-http"` |
| `headers` | HTTP 头键值对 |
| `connectionTimeoutMs` | 连接超时（毫秒，可选） |

> **兼容性说明**：CLI 原生的 `type: "http"` 值在通过 `openclaw mcp set` 保存时会被自动规范化为 `transport: "streamable-http"`。`openclaw doctor --fix` 也会修复现有配置中的此类别名。

### 3.4 mcp.sessionIdleTtlMs

控制会话作用域内 MCP 运行时的空闲超时：

```json5
{
  "mcp": {
    "sessionIdleTtlMs": 600000  // 默认 10 分钟（600,000 毫秒）
  }
}
```

- **默认值**：`600000`（10 分钟）
- **作用**：MCP 会话空闲超过设定时间后自动关闭，下次调用时重新启动
- **设为 `0`**：禁用超时（不推荐，可能导致进程累积）
- **一次性嵌入运行**（如 `openclaw agent`）在运行结束时自动清理 MCP 运行时

### 3.5 Codex 投影控制（可选）

每个 MCP Server 可附加可选的 `codex` 块，用于控制其在 Codex app-server 线程中的投影行为：

```json5
{
  "mcp": {
    "servers": {
      "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx" },
        "codex": {
          "agents": ["main"],              // 仅限指定的 OpenClaw agent 使用
          "defaultToolsApprovalMode": "approve"  // auto | prompt | approve
        }
      }
    }
  }
}
```

- `codex.agents`：非空数组时，仅向列出的 agent id 投影该服务器；空/无效列表会被拒绝而不是全局生效
- `codex.defaultToolsApprovalMode`：控制 Codex 对该服务器工具的默认审批模式
- OpenClaw 在将配置传递给 Codex 之前会剥离 `codex` 元数据块

### 3.6 环境变量安全过滤

OpenClaw 会拒绝可能改变解释器启动行为的 stdio 环境变量键，即使它们出现在服务器的 `env` 块中。被阻止的键包括：

- `NODE_OPTIONS`
- `PYTHONSTARTUP`
- `PYTHONPATH`
- `PERL5OPT`
- `RUBYOPT`
- `SHELLOPTS`
- `PS4`

> 这些变量如果在 `env` 中配置，启动时会报配置错误。如需使用，应在 Gateway 主机进程层面设置，而非放在 stdio 服务器的 `env` 中。

---

## 四、核心 MCP 服务配置实战

### 4.1 前置条件

- Node.js + npm 已安装（`npx` 可用）
- OpenClaw 已安装并配置
- 以下命令可用：`openclaw`, `npx`

### 4.2 GitHub MCP Server

**功能**：提供 GitHub API 操作能力，包括仓库搜索、Issue/PR 管理、代码读取、提交历史等。

**包名**：`@modelcontextprotocol/server-github`

**传输方式**：stdio

**安装步骤**：

1. 获取 GitHub Personal Access Token：
   - 访问 https://github.com/settings/tokens
   - 点击 **Generate new token (classic)**
   - 勾选权限：`repo`（完整仓库访问）、`read:user`（读取用户信息）、`read:org`（读取组织信息，可选）
   - 复制 Token（`ghp_` 开头）

2. 配置到 OpenClaw：

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_你的Token"

openclaw mcp set github \
  '{"command":"npx","args":["-y","@modelcontextprotocol/server-github"],"env":{"GITHUB_PERSONAL_ACCESS_TOKEN":"'"$GITHUB_PERSONAL_ACCESS_TOKEN"'"}}'
```

**常用工具名示例**：

| 工具名 | 功能 |
|--------|------|
| `github__search_repositories` | 搜索仓库 |
| `github__create_issue` | 创建 Issue |
| `github__get_file_contents` | 读取文件内容 |
| `github__create_pull_request` | 创建 PR |
| `github__search_code` | 搜索代码 |

> **注意**：Token 权限决定了可用操作范围。只读 Token 无法创建 Issue 或 PR。

### 4.3 Playwright MCP Server

**功能**：提供浏览器自动化能力，包括页面导航、截图、PDF 导出、点击元素、填写表单、执行 JavaScript、移动端模拟等。

**包名**：`@executeautomation/playwright-mcp-server`

**传输方式**：stdio

**安装步骤**：

```bash
openclaw mcp set playwright \
  '{"command":"npx","args":["-y","@executeautomation/playwright-mcp-server"]}'
```

**常用工具名示例**：

| 工具名 | 功能 |
|--------|------|
| `playwright__browser_navigate` | 导航到指定 URL |
| `playwright__browser_screenshot` | 页面截图 |
| `playwright__browser_click` | 点击元素 |
| `playwright__browser_fill` | 填写表单 |
| `playwright__browser_pdf` | 导出 PDF |
| `playwright__browser_execute_javascript` | 执行 JavaScript |

> **注意**：首次运行会自动下载浏览器二进制文件（Chromium），需要稳定的网络连接。

### 4.4 Context7 MCP Server

**功能**：提供代码语义搜索、文档索引、知识检索能力。支持索引本地代码库，通过自然语言查询代码，获取函数/类的文档和用法，跨文件引用追踪。

**包名**：`@upstash/context7-mcp`

**传输方式**：stdio

**安装步骤**：

```bash
# 方式一：无需 API Key（本地索引模式）
openclaw mcp set context7 \
  '{"command":"npx","args":["-y","@upstash/context7-mcp"]}'

# 方式二：使用 API Key（云端索引服务）
export CONTEXT7_API_KEY="ctx7sk-你的Key"
openclaw mcp set context7 \
  '{"command":"npx","args":["-y","@upstash/context7-mcp"],"env":{"CONTEXT7_API_KEY":"'"$CONTEXT7_API_KEY"'"}}'
```

**常用工具名示例**：

| 工具名 | 功能 |
|--------|------|
| `context7__search` | 语义搜索代码 |
| `context7__index_repository` | 索引本地代码库 |

### 4.5 一键安装脚本

项目中提供了 `scripts/setup-mcp.sh` 一键安装脚本：

```bash
# 设置环境变量后执行
export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_xxx"
export CONTEXT7_API_KEY="ctx7sk-xxx"  # 可选

./scripts/setup-mcp.sh
```

脚本会依次配置 GitHub、Playwright、Context7 三个服务，并输出配置结果汇总。

### 4.6 关于 Git MCP 的说明

**Anthropic 官方 MCP servers 仓库中不存在 `@modelcontextprotocol/server-git` 包**（npm 返回 404）。

**替代方案**：

| 场景 | 方案 |
|------|------|
| 远程仓库操作 | 使用已配置的 **GitHub MCP Server** |
| 本地 Git 操作 | 使用 OpenClaw 的 `exec` 工具直接执行 `git` 命令 |
| 未来补充 | 如发现可靠的社区 Git MCP 包，可通过 `openclaw mcp set` 添加 |

---

## 五、验证 MCP 配置

### 5.1 查看已配置服务

```bash
openclaw mcp list
```

预期输出：
```
github
playwright
context7
```

### 5.2 查看单个服务详情

```bash
# 查看 GitHub 配置
openclaw mcp show github --json

# 查看 Playwright 配置
openclaw mcp show playwright --json

# 查看 Context7 配置
openclaw mcp show context7 --json
```

### 5.3 查看完整配置文件

```bash
cat ~/.openclaw/openclaw.json | jq '.mcp'
```

预期看到类似结构：
```json
{
  "servers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "env": {
        "CONTEXT7_API_KEY": "ctx7sk-xxx"
      }
    }
  }
}
```

### 5.4 使用 openclaw doctor 诊断

```bash
# 健康检查
openclaw doctor

# 自动修复配置问题
openclaw doctor --fix
```

`openclaw doctor --fix` 可以：
- 将 CLI 原生的 `type: "http"` 规范化为 `transport: "streamable-http"`
- 修复其他 MCP 配置格式问题

### 5.5 验证工具是否加载

MCP 工具在 OpenClaw 的嵌入式 Pi 运行时中自动加载。验证方式：

1. **检查工具配置模式**：确认不是 `minimal` 模式
2. **重启 Gateway**：`openclaw gateway restart`
3. **查看运行时日志**：检查 MCP 连接是否成功
4. **实际调用测试**：在对话中请求使用 MCP 工具（如"帮我搜索 GitHub 上 star 数超过 1000 的 Python MCP 项目"）

---

## 六、使用已配置的 MCP 服务

### 6.1 工具命名规则

OpenClaw 将 MCP 工具注册为以下格式：

```
serverName__toolName
```

示例：
- `github__search_repositories`
- `playwright__browser_navigate`
- `context7__search`

> **前缀安全处理**：非 `[A-Za-z0-9_-]` 字符会变成 `-`；不以字母开头的名称会加 `mcp-` 前缀；过长或重复前缀可能被截断或加后缀。

### 6.2 工具可用性控制

MCP 工具的可见性由以下机制控制：

**1. 工具配置模式（Profile）**

| Profile | 是否包含 MCP 工具 |
|---------|------------------|
| `minimal` | ❌ 不包含（仅 `session_status`） |
| `coding` | ✅ 自动包含所有 MCP 工具 |
| `messaging` | ✅ 自动包含所有 MCP 工具 |
| `full` | ✅ 无限制 |

默认本地配置使用 `coding` 模式，因此 MCP 工具默认可用。

**2. 显式禁用**

在 agent 或 gateway 配置中添加：

```json5
{
  "tools": {
    "deny": ["bundle-mcp"]
  }
}
```

这会完全禁用所有通过 `bundle-mcp` 暴露的 MCP 工具。

**3. 按 Provider 限制**

```json5
{
  "tools": {
    "profile": "coding",
    "byProvider": {
      "google-antigravity": { "profile": "minimal" }
    }
  }
}
```

### 6.3 各服务工具示例

**GitHub 服务示例调用**：

```
用户：搜索 GitHub 上 star 数超过 5000 的 mcp server 项目

→ Agent 调用 github__search_repositories
→ 返回仓库列表
```

**Playwright 服务示例调用**：

```
用户：打开 https://example.com 并截图

→ Agent 调用 playwright__browser_navigate
→ Agent 调用 playwright__browser_screenshot
→ 返回截图
```

**Context7 服务示例调用**：

```
用户：在这个项目里搜索处理用户认证的函数

→ Agent 调用 context7__search
→ 返回相关代码片段和文档
```

### 6.4 沙箱模式下的 MCP 工具

当启用 Docker 沙箱模式（`agents.defaults.sandbox.mode: "all"` 或 `"non-main"`）时，需要在沙箱工具白名单中显式添加 MCP 工具：

```json5
{
  "agents": {
    "defaults": {
      "sandbox": { "mode": "all" }
    }
  },
  "mcp": {
    "servers": {
      "github": { "command": "npx", "args": ["..."] }
    }
  },
  "tools": {
    "sandbox": {
      "tools": {
        "alsoAllow": [
          "web_search",
          "bundle-mcp",           // 允许所有 OpenClaw 管理的 MCP 工具
          // 或精确指定：
          // "github__search_repositories",
          // "github__*"            // 允许 GitHub 服务的所有工具
        ]
      }
    }
  }
}
```

> 如果缺少沙箱层授权，MCP 服务器可以正常加载，但其工具会在发送到 Provider 之前被过滤掉。

### 6.5 斜杠命令管理 MCP

在支持斜杠命令的通道（如 Discord、Telegram）中，如果启用了 `commands.mcp: true`，可以使用 `/mcp` 命令管理 MCP 配置：

```text
/mcp show                    # 查看完整 MCP 配置
/mcp show context7           # 查看指定服务
/mcp set context7={"command":"uvx","args":["context7-mcp"]}
/mcp unset context7          # 删除服务
```

启用方式（gateway 配置）：

```json5
{
  "commands": {
    "mcp": true
  }
}
```

> `/mcp` 命令仅 owner 可用，且数据存储在 OpenClaw 配置中（不是 Pi 项目设置）。

---

## 七、OpenClaw 作为 MCP Server

### 7.1 使用场景

使用 `openclaw mcp serve` 的场景：

- **Codex、Claude Code 或其他 MCP Client** 需要直接与 OpenClaw 的对话通道交互
- 你已有本地或远程 OpenClaw Gateway，且会话路由已配置
- 希望用一个 MCP Server 覆盖 OpenClaw 的所有通道后端（Telegram、Discord、WhatsApp 等），而不是为每个通道单独运行桥接

**与 `openclaw acp` 的区别**：

| 方式 | 用途 |
|------|------|
| `openclaw mcp serve` | 外部 MCP Client 连接 OpenClaw 的对话通道 |
| `openclaw acp` | OpenClaw 自己托管编码运行时，保持 Agent 会话在 OpenClaw 内部 |

### 7.2 工作原理

```
┌─────────────┐    stdio     ┌─────────────┐    WebSocket    ┌─────────────┐
│  MCP Client │  ─────────→  │ openclaw    │  ────────────→  │   Gateway   │
│ (Claude Code│              │ mcp serve   │                 │             │
│  / Codex)   │  ←─────────  │  (桥接进程)  │  ←────────────  │             │
└─────────────┘              └─────────────┘                 └─────────────┘
                                    ↑
                                    │
                              MCP 工具调用
                         (conversations_list,
                          messages_read,
                          messages_send, ...)
```

流程：
1. MCP Client 启动 `openclaw mcp serve` 子进程
2. 桥接进程通过 WebSocket 连接到 OpenClaw Gateway
3. 已路由的会话变成 MCP 对话和聊天记录工具
4. 实时事件在桥接连接期间存入内存队列
5. 可选：Claude 特定推送通知同时生效

**重要行为**：
- 实时队列在桥接连接时启动，断开即消失
- 历史记录通过 `messages_read` 读取
- Claude 推送通知仅在 MCP 会话存活时存在
- 会话重置/删除时，关联的 MCP Client 会被释放
- stdio MCP 子进程在父进程退出时作为进程树被清理

### 7.3 启动方式

```bash
# 本地 Gateway
openclaw mcp serve

# 远程 Gateway（Token）
openclaw mcp serve \
  --url wss://gateway-host:18789 \
  --token-file ~/.openclaw/gateway.token

# 远程 Gateway（密码）
openclaw mcp serve \
  --url wss://gateway-host:18789 \
  --password-file ~/.openclaw/gateway.password

# 详细日志 + 关闭 Claude 模式
openclaw mcp serve --verbose --claude-channel-mode off
```

### 7.4 对外暴露的 MCP 工具

`serve` 模式当前暴露以下标准 MCP 工具：

| 工具名 | 功能 |
|--------|------|
| `conversations_list` | 列出最近有路由元数据的会话对话 |
| `conversation_get` | 通过 `session_key` 获取单个对话 |
| `messages_read` | 读取某个对话的最近聊天记录 |
| `attachments_fetch` | 提取某条消息的非文本内容块（元数据视图） |
| `events_poll` | 从数字游标读取队列中的实时事件 |
| `events_wait` | 长轮询等待下一个匹配事件（通用客户端实时推送替代方案） |
| `messages_send` | 通过会话已有路由发送文本回复 |
| `permissions_list_open` | 列出桥接连接后观察到的待审批请求 |
| `permissions_respond` | 处理单个审批请求：`allow-once`、`allow-always`、`deny` |

**`conversations_list` 过滤参数**：
- `limit` — 返回数量限制
- `search` — 搜索关键词
- `channel` — 按通道过滤
- `includeDerivedTitles` — 包含派生标题
- `includeLastMessage` — 包含最后一条消息

### 7.5 Event 模型

桥接在连接期间维护内存中的事件队列。当前支持的事件类型：

- `message` — 新消息
- `exec_approval_requested` — exec 审批请求
- `exec_approval_resolved` — exec 审批已处理
- `plugin_approval_requested` — 插件审批请求
- `plugin_approval_resolved` — 插件审批已处理
- `claude_permission_request` — Claude 权限请求

> **警告**：队列是实时-only 的，从桥接启动时开始。`events_poll` 和 `events_wait` 不会重放旧的历史记录。持久化历史应通过 `messages_read` 读取。

### 7.6 Claude Channel 通知模式

| 模式 | 说明 |
|------|------|
| `off` | 仅标准 MCP 工具 |
| `on` | 启用 Claude 通道通知 |
| `auto`（默认） | 当前行为与 `on` 相同 |

启用 Claude Channel 模式后，服务器会宣告 Claude 实验性能力，并可以发出：

- `notifications/claude/channel` — 入站用户消息转发
- `notifications/claude/channel/permission` — 权限请求通知

**行为细节**：
- 入站 `user` 转录消息被转发为 `notifications/claude/channel`
- Claude 权限请求在内存中跟踪
- 如果关联对话后续发送 `yes abcde` 或 `no abcde`，桥接会将其转换为 `notifications/claude/channel/permission`
- 这些通知仅存在于当前会话中；MCP Client 断开时无推送目标

> 通用 MCP Client 应依赖标准轮询工具（`events_poll` / `events_wait`），仅在 Client 原生支持 Claude 通知方法时才启用 Claude 模式。

### 7.7 MCP 客户端配置示例

将 OpenClaw 作为 MCP Server 配置到第三方 Client（如 Claude Desktop）的示例：

```json
{
  "mcpServers": {
    "openclaw": {
      "command": "openclaw",
      "args": [
        "mcp",
        "serve",
        "--url",
        "wss://gateway-host:18789",
        "--token-file",
        "/path/to/gateway.token"
      ]
    }
  }
}
```

本地 Gateway 的简化配置：

```json
{
  "mcpServers": {
    "openclaw": {
      "command": "openclaw",
      "args": ["mcp", "serve"]
    }
  }
}
```

### 7.8 安全边界

桥接不会自行发明路由，仅暴露 Gateway 已知道如何路由的对话。这意味着：

- 发送者白名单、配对和通道级信任仍属于底层 OpenClaw 通道配置
- `messages_send` 只能通过已存储的路由回复
- 审批状态仅对当前桥接会话有效（内存中）
- 桥接认证应使用与任何其他远程 Gateway Client 相同的信任级别

如果 `conversations_list` 未返回某个对话，通常原因不是 MCP 配置问题，而是底层 Gateway 会话缺少或缺少完整的路由元数据（channel/provider、recipient、account/thread）。

---

## 八、故障排除

### 8.1 MCP 工具未出现

**排查步骤**：

1. 确认服务已配置：`openclaw mcp list`
2. 重启 Gateway：`openclaw gateway restart`
3. 检查工具配置模式：确认不是 `minimal`（`coding` 或 `messaging` 模式才会暴露 MCP 工具）
4. 检查是否显式禁用了 `bundle-mcp`：`tools.deny` 中不应包含 `"bundle-mcp"`
5. 查看 Gateway 日志是否有 MCP 连接错误
6. 检查沙箱模式：如果启用了沙箱，确认 `tools.sandbox.tools.alsoAllow` 中包含 `bundle-mcp`

### 8.2 GitHub 操作失败

| 现象 | 原因 | 解决 |
|------|------|------|
| API 返回 401/403 | Token 权限不足或过期 | 检查 Token 的 `repo`、`read:user` 权限；重新生成 Token |
| 速率限制 | 触及 GitHub API 限制 | 减少调用频率；考虑使用更高权限的 Token |
| 无法创建 Issue/PR | Token 为只读 | 生成具有 `repo` 完整权限的 Token |

### 8.3 Playwright 启动失败

| 现象 | 原因 | 解决 |
|------|------|------|
| 浏览器下载超时 | 网络不稳定 | 确保网络连接；首次启动需下载 Chromium |
| 命令未找到 | `npx` 或 npm 未安装 | 安装 Node.js 和 npm |
| macOS 权限问题 | 系统安全拦截 | 在 系统设置 → 隐私与安全性 中允许 |

### 8.4 Context7 连接失败

| 现象 | 原因 | 解决 |
|------|------|------|
| API Key 无效 | `CONTEXT7_API_KEY` 错误或过期 | 检查 Key 有效性；或切换为本地模式（无 Key） |
| 包未安装 | npm 包缺失 | 运行 `npm ls -g @upstash/context7-mcp` 确认 |

### 8.5 serve 模式无对话返回

| 现象 | 原因 | 解决 |
|------|------|------|
| `conversations_list` 为空 | Gateway 会话没有路由元数据 | 确认底层会话已存储 channel/provider、recipient、account/thread 信息 |
| `events_poll` 错过旧消息 | 预期行为 | 实时队列从桥接启动时开始；旧历史用 `messages_read` |
| Claude 通知不出现 | Client 不支持或模式关闭 | 检查 `--claude-channel-mode`；确认 Client 理解 Claude 特定通知方法 |
| 审批缺失 | 桥接未连接时发生的审批 | `permissions_list_open` 仅显示桥接连接后观察到的审批 |

---

## 九、参考链接

- [OpenClaw MCP CLI 文档](https://docs.openclaw.ai/cli/mcp)
- [MCP 官方文档](https://modelcontextprotocol.io)
- [MCP 官方 Servers 仓库](https://github.com/modelcontextprotocol/servers)
- [GitHub MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
- [Playwright MCP Server](https://github.com/executeautomation/mcp-playwright)
- [Context7 MCP](https://github.com/upstash/context7)
- [OpenClaw 配置参考 — Tools](/gateway/config-tools)
- [OpenClaw 配置参考 — Gateway](/gateway/configuration-reference)
- [OpenClaw CLI Backends 与 Bundle MCP](/gateway/cli-backends)
