---
name: Kimi Code CLI 参考手册
description: Kimi Code CLI 命令、工具、斜杠命令和键盘快捷键的完整速查参考
category: 参考
order: 4
---

# Kimi Code CLI 参考手册

> Kimi Code CLI 的所有命令、内置工具、斜杠命令和键盘快捷键速查。适合放在手边随时查阅。

---

## 目录

- [kimi 命令](#kimi-命令)
  - [主命令选项](#主命令选项)
  - [flag 冲突规则](#flag-冲突规则)
  - [典型用法](#典型用法)
  - [子命令](#子命令)
- [内置工具](#内置工具)
  - [文件类](#文件类)
  - [Shell](#shell)
  - [网络类](#网络类)
  - [Plan 模式](#plan-模式)
  - [状态管理](#状态管理)
  - [协作类](#协作类)
  - [后台任务](#后台任务)
  - [定时任务](#定时任务)
- [斜杠命令](#斜杠命令)
  - [账号与配置](#账号与配置)
  - [会话管理](#会话管理)
  - [模式与运行控制](#模式与运行控制)
  - [目标模式](#目标模式)
  - [信息与状态](#信息与状态)
  - [退出](#退出)
  - [内置 Skill 命令](#内置-skill-命令)
  - [Skill 动态命令](#skill-动态命令)
- [键盘快捷键](#键盘快捷键)
- [术语表](#术语表)

---

## kimi 命令

`kimi` 是 Kimi Code CLI 的主命令，用于在终端中启动一次交互式会话。

```bash
kimi [options]
kimi <subcommand> [options]
```

### 主命令选项

| 选项 | 简写 | 说明 |
|------|------|------|
| `--version` | `-V` | 打印版本号并退出 |
| `--help` | `-h` | 显示帮助信息并退出 |
| `--session [id]` | `-S` | 恢复一个会话。带 ID 时直接打开指定会话；不带 ID 时进入交互式选择器 |
| `--continue` | `-C` | 继续当前工作目录下最近一次的会话 |
| `--model <model>` | `-m` | 为本次启动指定模型别名 |
| `--prompt <prompt>` | `-p` | 非交互执行单次 prompt，并把 Assistant 输出流式写到 stdout |
| `--output-format <format>` | — | 设置非交互输出格式，支持 `text` 与 `stream-json`。仅可与 `--prompt` 一起使用 |
| `--yolo` | `-y` | 自动批准普通工具调用，跳过审批请求 |
| `--auto` | — | 以 auto 权限模式启动；工具审批自动处理 |
| `--plan` | — | 以 Plan 模式启动新会话 |
| `--skills-dir <dir>` | — | 从指定目录加载 Skills，替换自动发现的目录。可重复传入 |

> ⚠️ `--yolo` 会跳过普通工具调用的人工确认，包括文件写入和 Shell 命令执行，请只在受信任的工作目录下使用。

### flag 冲突规则

以下组合会在启动时被拒绝：

- `--continue` 与 `--session` 互斥
- `--yolo` 和 `--auto` 互斥
- `--prompt` 不能与 `--yolo`、`--auto` 或 `--plan` 同时使用
- `--output-format` 只能与 `--prompt` 一起使用

恢复会话时，可以通过 `--auto`、`--yolo` 或 `--plan` 覆盖原会话保存的权限或计划模式。

### 典型用法

```bash
# 直接运行开启新会话
kimi

# 从上次中断的地方继续
kimi --continue

# 从历史会话列表中挑选
kimi --session

# 跳过审批确认，适合批处理任务
kimi --yolo

# 让 Agent 自行处理一切，不再向用户提问
kimi --auto

# 先阅读代码、产出实现计划
kimi --plan

# 非交互执行单次 prompt
kimi -p "Summarize the current repository status"

# 临时切换模型
kimi -m kimi-code/kimi-for-coding -p "Explain the latest diff"

# 结构化输出
kimi -p "List changed files" --output-format stream-json
```

### 子命令

#### `kimi login`

通过 RFC 8628 device-code 流程登录 Kimi Code OAuth，无需进入 TUI。

```bash
kimi login
```

- 没有任何 flag
- 轮询期间随时按 `Ctrl-C` 可取消
- 取消或失败时退出码为 `1`，成功为 `0`

#### `kimi acp`

把 Kimi Code CLI 切换到 ACP（Agent Client Protocol）模式：在标准输入/输出上以 JSON-RPC 形式与 ACP 客户端（如 Zed、JetBrains AI Chat 等）对话，让 IDE 直接驱动 kimi 的会话、prompt 与工具调用。

```bash
kimi acp
```

启动后命令不会打印任何 banner，立刻等待 ACP 客户端在 stdin 上发出 `initialize` 请求。日志写到标准错误（以及 `~/.kimi-code/logs/` 下的诊断日志），ACP 通道本身保持干净。

> 通常不需要手动运行——这个命令是给 IDE 的子进程入口准备的。IDE 端配置见「在 IDE 中使用」。

**能力矩阵**

ACP 适配层声明的能力，在 `initialize` 响应的 `agentCapabilities` 字段中返回：

| 能力 | 取值 | 说明 |
|------|------|------|
| `promptCapabilities.image` | `true` | 支持 ACP image 内容块（base64 + mimeType）|
| `promptCapabilities.audio` | `false` | 暂不支持音频 prompt |
| `promptCapabilities.embeddedContext` | `true` | 支持 resource / resource_link 嵌入式资源块 |
| `mcpCapabilities.http` | `true` | 转发 IDE 配置的 HTTP MCP 服务 |
| `mcpCapabilities.sse` | `false` | 不支持 SSE MCP 服务 |
| `loadSession` | `true` | 支持 `session/load` 续接已有会话 |
| `sessionCapabilities.list` | `{}` | 支持 `session/list` 枚举会话 |

**ACP 方法覆盖**

稳定面 agent-side — IDE → agent（10 / 12）：

| 方法 | 状态 | 说明 |
|------|------|------|
| `initialize` | ✅ | 版本协商；返回 agentInfo、能力矩阵、authMethods |
| `authenticate` | ✅ | 校验 `method_id='login'` |
| `session/new` | ✅ | 接受 cwd / mcpServers，返回 configOptions[] |
| `session/load` | ✅ | 恢复磁盘会话并同步回放历史 |
| `session/resume` | ✅ | `session/load` 的轻量版本，跳过历史回放 |
| `session/prompt` | ✅ | 接受 text / image / resource 内容块，流式输出 |
| `session/cancel` | ✅ | 中断当前 turn |
| `session/list` | ✅ | 枚举磁盘会话 |
| `session/set_mode` | ✅ | 兼容路径，同 `set_config_option({configId:'mode'})` |
| `session/set_config_option` | ✅ | 统一的 model / thinking / mode 分发 |
| `session/close` | ❌ | — |
| `logout` | ❌ | — |

稳定面 client-side reverse-RPC — agent → IDE（4 / 9）：

| 方法 | 状态 | 说明 |
|------|------|------|
| `session/update` | ✅ | 流式推送 agent_message_chunk / tool_call / plan 等 |
| `session/request_permission` | ✅ | 工具审批和问题 elicitation 共用通道 |
| `fs/read_text_file` | ✅ | kaos 层文件读取路由到客户端 |
| `fs/write_text_file` | ✅ | kaos 层文件写入路由到客户端 |
| `terminal/*` | ❌ | 终端 reverse-RPC 未接，shell 走本地执行 |

不稳定面（1 / 19）：

| 方法 | 状态 | 说明 |
|------|------|------|
| `session/set_model` | ✅ | 兼容路径，等价于 `set_config_option({configId:'model'})` |
| 其余 18 个方法 | ❌ | 包括 session 生命周期扩展、缓冲区同步、inline-edit 预测等 |

**MCP 转发**

ACP 客户端在 `session/new` 或 `session/load` 中提供 `mcpServers` 时：

- `http` → kimi 的 `transport: 'http'` 配置
- `stdio` → kimi 的 `transport: 'stdio'` 配置
- `sse` / `acp` → 丢弃并写 warn 日志

#### `kimi doctor`

校验 `config.toml` 和 `tui.toml`，不会启动 TUI，也不会修改文件。

```bash
kimi doctor                    # 校验默认配置文件
kimi doctor config [path]      # 只校验 config.toml
kimi doctor tui [path]         # 只校验 tui.toml
```

- 所有被检查的文件都有效或被跳过时，退出码为 `0`
- 任何指定文件缺失或配置无效时，退出码为 `1`

#### `kimi export`

把一个会话打包成 ZIP 文件，便于分享、归档或提交问题反馈。

```bash
kimi export [sessionId] [options]
```

| 参数/选项 | 简写 | 说明 |
|-----------|------|------|
| `sessionId` | — | 要导出的会话 ID。省略时自动选择当前工作目录下最近一次的会话 |
| `--output <path>` | `-o` | 输出 ZIP 文件路径 |
| `--yes` | `-y` | 跳过默认会话的确认提示 |
| `--no-include-global-log` | — | 不打包全局诊断日志 |

#### `kimi migrate`

将旧版 `kimi-cli` 的本地数据迁移到 `kimi-code`，包括历史会话和配置文件。

```bash
kimi migrate
```

#### `kimi upgrade`

立即检查最新版本并展示更新提示。

```bash
kimi upgrade
```

#### `kimi provider`

在 shell 中管理供应商，相当于 TUI 中 `/provider` 的非交互版本。

```bash
kimi provider <action> [options]
```

**`kimi provider add <url>`**：从自定义 registry 批量导入供应商

```bash
kimi provider add https://registry.example.com/v1/models/api.json --api-key YOUR_KEY
```

**`kimi provider remove <providerId>`**：删除指定供应商

```bash
kimi provider remove kohub
```

**`kimi provider list`**：打印每个已配置的供应商

```bash
kimi provider list
kimi provider list --json | jq '.providers | keys'
```

**`kimi provider catalog list [providerId]`**：浏览公开的 models.dev 模型目录

```bash
kimi provider catalog list
kimi provider catalog list --filter anthropic
kimi provider catalog list anthropic
```

**`kimi provider catalog add <providerId>`**：从 catalog 直接导入已知供应商

```bash
kimi provider catalog add anthropic --api-key sk-ant-... --default-model claude-opus-4-7
```

---

## 内置工具

内置工具是 Kimi Code CLI 随核心引擎提供的工具集，无需安装 MCP server 即可使用。

**审批规则**：只读类工具默认自动放行；写入与执行类工具默认需要用户审批。YOLO 模式下普通工具调用的审批会被跳过。

### 文件类

| 工具 | 默认审批 | 说明 |
|------|----------|------|
| `Read` | 自动放行 | 读取文本文件内容 |
| `Write` | 需审批 | 创建或覆盖文件 |
| `Edit` | 需审批 | 精确字符串替换 |
| `Grep` | 自动放行 | 基于 ripgrep 的全文搜索 |
| `Glob` | 自动放行 | 按 glob 模式查找文件 |
| `ReadMediaFile` | 自动放行 | 读取图片或视频文件 |

**Read**：接受 `path`、`line_offset`（起始行号，支持负数）、`n_lines`（读取行数上限）。单次最多返回 1000 行或 100 KB。

**Write**：接受 `path`、`content`、可选 `mode`（`overwrite` 或 `append`，默认覆盖）。父目录必须已存在。

**Edit**：接受 `path`、`old_string`、`new_string`。默认只替换唯一一处匹配；多处相同内容需用 `replace_all: true`。

**Grep**：调用 ripgrep 搜索。支持 `pattern`（正则）、`path`、`type`（文件类型）、`glob`、`output_mode`（`files_with_matches`/`content`/`count_matches`）。`.env`、私钥等敏感文件自动过滤；`include_ignored=true` 可搜索被 `.gitignore` 忽略的文件。

**Glob**：按 `pattern` 在 `path`（默认工作目录）中匹配文件，最多返回 1000 条。纯通配符模式和含花括号扩展的模式会被拒绝。

**ReadMediaFile**：读取图片或视频以多模态内容发送给模型。仅接受 `path`，文件大小上限 100 MB。

### Shell

| 工具 | 默认审批 | 说明 |
|------|----------|------|
| `Bash` | 需审批 | 执行 Shell 命令 |

**Bash** 参数：
- `command`（必填）：要执行的 Shell 命令
- `cwd`：工作目录
- `timeout`：超时时间（毫秒）；前台默认 60 秒、最长 5 分钟
- `run_in_background`：是否以后台任务运行
- `description`：后台任务描述，`run_in_background=true` 时必填
- `disable_timeout`：后台任务是否取消超时限制

前台模式阻塞当前轮次；后台模式立即返回任务 ID。Windows 平台默认使用 Git Bash。

### 网络类

| 工具 | 默认审批 | 说明 |
|------|----------|------|
| `WebSearch` | 自动放行 | 网络搜索 |
| `FetchURL` | 自动放行 | 获取指定 URL 的内容 |

**WebSearch**：接受 `query`、可选 `limit`（1–20，默认 5）及 `include_content`（默认 false）。

**FetchURL**：接受单个 `url`，返回页面正文。

### Plan 模式

| 工具 | 默认审批 | 说明 |
|------|----------|------|
| `EnterPlanMode` | 自动放行 | 进入 Plan 模式 |
| `ExitPlanMode` | 自动放行（需用户确认计划）| 退出 Plan 模式并提交计划 |

**EnterPlanMode**：不接受任何参数，进入成功后返回工作流指引及计划文件路径。

**ExitPlanMode**：读取当前计划文件，呈现给用户审批后退出。可选 `options` 参数允许提供 1–3 个备选方案。

### 状态管理

| 工具 | 默认审批 | 说明 |
|------|----------|------|
| `TodoList` | 自动放行 | 管理任务待办列表 |

**TodoList**：`todos` 参数接受数组，每项含 `title` 和 `status`（`pending`/`in_progress`/`done`）。省略 `todos` 则仅查询；传入空数组则清空。

### 协作类

| 工具 | 默认审批 | 说明 |
|------|----------|------|
| `Agent` | 自动放行 | 派生子 Agent 执行子任务 |
| `AgentSwarm` | swarm mode 自动放行，否则需审批 | 启动基于 item 的子 Agent 群 |
| `AskUserQuestion` | 自动放行 | 向用户提问以获取结构化输入 |
| `Skill` | 自动放行 | 调用已注册的 inline Skill |

**Agent**：必填 `prompt`（任务描述）和 `description`（3–5 词简短说明）。可选 `subagent_type`（默认 `coder`）、`resume`（恢复已有 Agent ID）、`run_in_background`（默认 false）。固定 30 分钟超时。

**AgentSwarm**：从共享的 `prompt_template` 和 `items` 数组启动子 Agent，或通过 `resume_agent_ids` 恢复已有子 Agent。最多支持 128 个子 Agent。若一次模型响应调用 `AgentSwarm`，该调用必须是该响应中的唯一工具调用。

**AskUserQuestion**：`questions` 参数接受 1–4 道题，每道题含 `question`（以 `?` 结尾）、`options`（2–4 个选项）及可选 `header`（最多 12 字符）和 `multi_select`（默认 false）。

**Skill**：接受 `skill`（Skill 名称）和可选 `args`。只有 `type = "inline"` 的 Skill 能被调用；嵌套调用深度上限 3 层。

### 后台任务

| 工具 | 默认审批 | 说明 |
|------|----------|------|
| `TaskList` | 自动放行 | 列出后台任务 |
| `TaskOutput` | 自动放行 | 查看后台任务的输出 |
| `TaskStop` | 需审批 | 停止正在运行的后台任务 |

**TaskList**：可选 `active_only`（默认 true）和 `limit`（默认 20，范围 1–100）。

**TaskOutput**：根据 `task_id` 返回状态与输出。内联预览最多 32 KB；完整日志保存在磁盘上。可选 `block`（默认 false）和 `timeout`（默认 30 秒）。

**TaskStop**：接受 `task_id` 和可选 `reason`（默认 `Stopped by TaskStop`）。

### 定时任务

| 工具 | 默认审批 | 说明 |
|------|----------|------|
| `CronCreate` | 需审批 | 安排一个在未来时刻触发的 prompt |
| `CronList` | 自动放行 | 列出已安排的定时任务 |
| `CronDelete` | 需审批 | 取消已安排的定时任务 |

**CronCreate**：接受 `cron`（5 段 cron 表达式）、`prompt`（触发时注入的文本，上限 8 KB）及可选 `recurring`（默认 true；false 表示一次性提醒）。成功时返回 8 位 16 进制 id。

> 设置 `KIMI_DISABLE_CRON=1` 可整体禁用定时任务。单个会话最多保留 50 个生效中的定时任务。

---

## 斜杠命令

斜杠命令是 Kimi Code CLI 在交互式 TUI 中提供的内置控制命令。在输入框中输入 `/` 即可触发命令补全。

> 部分命令仅在空闲（idle）状态下可用。标注「随时可用」的命令在流式输出期间也可使用。

### 账号与配置

| 命令 | 别名 | 说明 | 随时可用 |
|------|------|------|----------|
| `/login` | — | 选择账号或平台并登录 | 否 |
| `/logout` | — | 清除当前所选账号的凭据 | 否 |
| `/provider` | — | 打开交互式供应商管理器 | 是 |
| `/model` | — | 切换当前会话使用的 LLM 模型 | 是 |
| `/settings` | `/config` | 打开 TUI 内的设置面板 | 是 |
| `/experiments` | `/experimental` | 打开实验功能面板 | 是 |
| `/permission` | — | 选择权限模式 | 是 |
| `/editor` | — | 配置 Ctrl-G 调起的外部编辑器 | 是 |
| `/theme` | — | 切换终端 UI 配色主题 | 是 |

### 会话管理

| 命令 | 别名 | 说明 | 随时可用 |
|------|------|------|----------|
| `/new` | `/clear` | 开启全新会话，丢弃当前上下文 | 否 |
| `/sessions` | `/resume` | 浏览历史会话并切换/恢复 | 否 |
| `/tasks` | `/task` | 浏览后台任务列表 | 是 |
| `/fork` | — | 基于当前会话 fork 一份新会话 | 否 |
| `/title [<text>]` | `/rename` | 显示或设置当前会话标题 | 是 |
| `/compact [<instruction>]` | — | 压缩当前对话上下文 | 否 |
| `/undo [<count>]` | — | 从当前上下文撤销最近的提示词 | 否 |
| `/init` | — | 分析当前代码库并生成 AGENTS.md | 否 |
| `/export-md [<path>]` | `/export` | 将当前会话导出为 Markdown | 否 |
| `/export-debug-zip` | — | 将当前会话导出为调试用 ZIP | 否 |

### 模式与运行控制

| 命令 | 别名 | 说明 | 随时可用 |
|------|------|------|----------|
| `/yolo [on\|off]` | `/yes` | 切换 YOLO 模式 | 是 |
| `/auto [on\|off]` | — | 切换 auto 权限模式 | 是 |
| `/plan [on\|off]` | — | 切换 Plan 模式 | 是 |
| `/plan clear` | — | 清除当前 plan 方案 | 否 |
| `/swarm on\|off` | — | 开启或关闭 swarm mode | 是 |
| `/swarm <task>` | — | 先开启 swarm mode，再发送 task | 否 |

### 目标模式

| 命令 | 作用 | 可用性 |
|------|------|--------|
| `/goal` 或 `/goal status` | 显示当前目标及其状态 | 随时可用 |
| `/goal pause` | 暂停当前目标 | 随时可用 |
| `/goal resume` | 继续被暂停或被阻塞的目标 | 仅空闲时 |
| `/goal cancel` | 移除当前目标 | 随时可用 |
| `/goal replace <objective>` | 用新目标替换已保存的目标 | 仅空闲时 |
| `/goal next <objective>` | 为当前会话安排后续目标 | 随时可用 |
| `/goal next manage` | 打开后续目标管理器 | 随时可用 |

> 如果目标需要以 `status`、`pause`、`resume`、`cancel`、`replace`、`next` 或 `manage` 开头，请在目标前加 `--`。

### 信息与状态

| 命令 | 别名 | 说明 | 随时可用 |
|------|------|------|----------|
| `/help` | `/h`、`/?` | 显示快捷键和所有可用命令 | 是 |
| `/btw [问题]` | — | 在 fork 出的子 Agent 中打开旁路对话 | 是 |
| `/usage` | — | 显示 token 用量、上下文占用及配额信息 | 是 |
| `/status` | — | 显示当前会话运行时状态 | 是 |
| `/mcp` | — | 列出当前会话中的 MCP server 及连接状态 | 是 |
| `/plugins` | — | 打开交互式 plugin 管理器 | 是 |
| `/version` | — | 显示 Kimi Code CLI 版本号 | 是 |
| `/feedback` | — | 提交反馈 | 是 |

### 退出

| 命令 | 别名 | 说明 | 随时可用 |
|------|------|------|----------|
| `/exit` | `/quit`、`/q` | 退出 Kimi Code CLI | 否 |

### 内置 Skill 命令

Kimi Code CLI 随包内置的 Skill 直接以 `/<name>` 形式出现，不需要 `skill:` 前缀：

| 命令 | 说明 |
|------|------|
| `/mcp-config` | 配置 MCP server 并处理 MCP OAuth 登录 |
| `/custom-theme [<text>]` | 创建或编辑自定义 TUI 配色主题 |
| `/update-config` | 查看或编辑 `config.toml` 和 `tui.toml` |
| `/import-from-cc-codex` | 从 Claude Code 和 Codex 导入 instructions、skills 和 MCP 设置 |
| `/sub-skill` | 发现并将本地 skill 库存重组为分层子 skill 包 |

### Skill 动态命令

已激活的外部 Skill 自动注册为斜杠命令：

- 普通外部 Skill：`/skill:<name> [附加文本]`
- 外部子 Skill：`/<parent-skill>.<sub-skill> [附加文本]`
- 简写形式（未被系统命令占用时）：`/<name>` 回退匹配到 `/skill:<name>`

---

## 键盘快捷键

### 通用快捷键

以下键位在输入框中始终可用：

| 快捷键 | 功能 |
|--------|------|
| `Enter` | 提交当前输入 |
| `Shift-Enter` / `Ctrl-J` | 在输入中插入换行 |
| `↑` / `↓` | 浏览输入历史 |
| `Esc` | 关闭弹窗 / 取消补全 / 中断流式输出或上下文压缩 |
| `Ctrl-C` | 中断当前流式输出，或清空输入框 |
| `Ctrl-D` | 在输入框为空时退出 Kimi Code CLI |

> **流式输出期间**按 `Ctrl-C` 会立即取消，无需二次确认。
>
> **退出程序**（输入框为空时按 `Ctrl-C`，或按 `Ctrl-D`）使用「双击确认」机制：第一次按下后状态栏会出现提示，再按一次相同的键才真正退出。中途按其他键会清除确认状态。

### 模式切换

| 快捷键 | 功能 |
|--------|------|
| `Shift-Tab` | 切换 Plan 模式 |

按 `Shift-Tab` 可开启或关闭 Plan 模式。开启后，Agent 会优先使用只读工具进行研究和规划，并可写入当前计划文件；`Bash` 按当前权限模式和普通规则处理。单纯切换模式不会创建空计划文件。再次按 `Shift-Tab` 退出 Plan 模式。

### 输入与编辑

| 快捷键 | 功能 |
|--------|------|
| `Ctrl-G` | 在外部编辑器中编辑当前输入 |
| `Ctrl-V` | 粘贴剪贴板中的图片或视频（Unix / macOS）|
| `Alt-V` | 粘贴剪贴板中的图片或视频（Windows）|
| `Ctrl--` | 撤销（Undo）|

按 `Ctrl-G` 会打开外部编辑器，编辑器按以下优先级选择：`/editor` 命令配置的编辑器 → `$VISUAL` 环境变量 → `$EDITOR` 环境变量。保存并退出后，编辑内容替换输入框；不保存退出则保持原样。

粘贴图片或视频时，输入框中显示占位符，实际媒体数据在提交时一并发送给模型。优先从系统剪贴板读取；Linux 上尝试 Wayland 与 X11，WSL 下通过 PowerShell 兜底读取 Windows 剪贴板。

### 流式输出期间

流式输出期间，输入框依然可以接收输入，并支持以下额外操作：

| 快捷键 | 功能 |
|--------|------|
| `Ctrl-S` | Steer：将当前输入立即注入正在运行的轮次 |
| `Esc` | 中断当前流式输出 |
| `Ctrl-C` | 中断当前流式输出 |

按 `Ctrl-S` 时，模型会在下一个可中断的时机立刻看到你的消息，无需等待当前轮次结束。

### 工具输出

| 快捷键 | 功能 |
|--------|------|
| `Ctrl-O` | 展开或折叠工具输出 |

历史中存在折叠的工具调用结果时，按 `Ctrl-O` 可在折叠和展开之间切换。

### 审批面板

当 Agent 发起需要确认的工具调用时，TUI 会弹出审批面板：

| 快捷键 | 功能 |
|--------|------|
| `↑` / `↓` | 在候选选项之间移动光标 |
| `Enter` | 确认当前选中的选项 |
| `1` ~ `9` | 直接选择对应序号的选项 |
| `Esc` / `Ctrl-C` / `Ctrl-D` | 拒绝当前请求 |
| `Ctrl-E` | 面板包含 diff 或文件内容预览时，展开或折叠完整内容 |
| `Ctrl-O` | 切换其他工具输出的折叠状态 |

需要附带反馈的选项（如「Reject」「Revise」）会在确认后切换到反馈输入态：直接输入反馈文本，按 `Enter` 提交；按 `Esc` 退出反馈输入并回到候选列表。

### 弹窗模式

输入 `/help` 打开帮助面板后，可使用以下键位浏览和关闭面板：

| 快捷键 | 功能 |
|--------|------|
| `↑` / `↓` | 单行滚动 |
| `PageUp` / `PageDown` | 每次滚动 10 行 |
| `Esc` / `Enter` / `q` / `Q` | 关闭面板 |

---

## 术语表

| 术语 | 定义 | 上下文/示例 |
|------|------|------------|
| TUI | Terminal User Interface，终端用户界面 | Kimi Code CLI 的交互式终端界面 |
| YOLO 模式 | 权限模式的一种，自动批准所有工具调用 | `--yolo` 或 `/yolo` |
| Plan 模式 | 先出计划再执行的工作模式 | `--plan` 或 `/plan` |
| ACP | Agent Client Protocol，Agent 客户端协议 | `kimi acp` 子命令 |
| Swarm mode | 多 Agent 并行协作模式 | `/swarm` 命令 |
| MCP | Model Context Protocol，模型上下文协议 | 外部工具接入协议 |
| Skill | Agent 的专业知识或工作流程描述文件 | `SKILL.md` |
| Hook | 生命周期事件触发的本地脚本 | `[[hooks]]` 配置 |
| Token | 模型处理文本时的最小单位 | 上下文长度计量 |
| Cron | 时间表达式，用于定时任务 | `CronCreate` 工具 |
| JSON-RPC | 远程过程调用协议，JSON 格式 | ACP 模式通信协议 |
| Registry | 模型和供应商的注册表 | `kimi provider add` |
| OAuth | 开放授权协议 | `/login` 登录流程 |

---

> 📚 **官方文档**：https://moonshotai.github.io/kimi-code/zh/
