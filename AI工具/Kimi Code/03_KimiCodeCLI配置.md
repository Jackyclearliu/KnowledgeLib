---
name: Kimi Code CLI 配置
description: Kimi Code CLI 配置文件、平台模型、配置覆盖、环境变量和数据路径的完整参考
category: 配置
order: 3
---

# Kimi Code CLI 配置

> Kimi Code CLI 将所有长期偏好写进 `~/.kimi-code/` 下的 TOML 文件——模型选择、API 密钥、Agent 循环控制、权限规则等。改一次，每次启动都生效。

---

## 目录

- [配置文件](#配置文件)
  - [config.toml](#configtoml)
  - [tui.toml](#tuitoml)
- [平台与模型](#平台与模型)
  - [支持的供应商类型](#支持的供应商类型)
  - [各供应商接入示例](#各供应商接入示例)
- [配置覆盖](#配置覆盖)
  - [优先级规则](#优先级规则)
  - [命令行选项](#命令行选项)
  - [典型场景](#典型场景)
- [环境变量](#环境变量)
  - [核心路径](#核心路径)
  - [供应商凭证键](#供应商凭证键)
  - [KIMI_MODEL_* 系列](#kimi_model_-系列)
  - [运行时开关](#运行时开关)
  - [HTTP 代理](#http-代理)
- [数据路径](#数据路径)
  - [目录结构](#目录结构)
  - [会话数据](#会话数据)
  - [清理数据](#清理数据)
- [术语表](#术语表)

---

## 配置文件

### config.toml

CLI 从 `~/.kimi-code/config.toml` 读取配置。如需迁移数据目录，用 `KIMI_CODE_HOME` 环境变量覆盖：

```bash
export KIMI_CODE_HOME=/path/to/kimi-home
```

此时配置文件路径变为 `$KIMI_CODE_HOME/config.toml`。文件名固定为 `config.toml`。

> ⚠️ **TOML 注意**：字段名一律用下划线（snake_case），如 `default_model`、`max_context_size`。字段名含 `.` 时需用引号包住，如 `[models."gpt-4.1"]`。

#### 完整示例

```toml
default_model = "kimi-code/kimi-for-coding"
default_thinking = true
default_permission_mode = "manual"
default_plan_mode = false
merge_all_available_skills = true
telemetry = true

[providers."managed:kimi-code"]
type = "kimi"
base_url = "https://api.kimi.com/coding/v1"
api_key = ""

[models."kimi-code/kimi-for-coding"]
provider = "managed:kimi-code"
model = "kimi-for-coding"
max_context_size = 262144

[thinking]
mode = "auto"

[loop_control]
max_retries_per_step = 3
reserved_context_size = 50000

[background]
max_running_tasks = 4
keep_alive_on_exit = false

[experimental]
micro_compaction = true

[[permission.rules]]
decision = "allow"
pattern = "Read"

[[permission.rules]]
decision = "deny"
pattern = "Bash(rm -rf*)"

[[hooks]]
event = "PreToolUse"
matcher = "Bash"
command = "node ~/.kimi-code/hooks/check-bash.mjs"
timeout = 5
```

#### 顶层字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `default_model` | `string` | — | 默认模型别名，必须在 `models` 中定义 |
| `default_thinking` | `boolean` | `false` | 新会话是否默认开启 Thinking 模式；即使 `true`，`[thinking].mode = "off"` 也会强制关闭 |
| `default_permission_mode` | `string` | `manual` | 默认权限模式：`manual`（逐次询问）、`auto`（自动批准读操作）、`yolo`（全部自动批准）|
| `default_plan_mode` | `boolean` | `false` | 新会话是否默认以 Plan 模式启动 |
| `merge_all_available_skills` | `boolean` | `true` | 是否合并所有目录中的 Agent Skills |
| `extra_skill_dirs` | `array<string>` | — | 额外 Skill 搜索目录 |
| `telemetry` | `boolean` | `true` | 是否启用匿名遥测；设为 `false` 关闭 |
| `providers` | `table` | `{}` | API 供应商表 |
| `models` | `table` | — | 模型别名表 |
| `thinking` | `table` | — | Thinking 模式默认参数 |
| `loop_control` | `table` | — | Agent 循环控制参数 |
| `background` | `table` | — | 后台任务运行参数 |
| `experimental` | `table` | — | 实验功能覆盖 |
| `services` | `table` | — | 内置外部服务配置 |
| `permission` | `table` | — | 初始权限规则 |
| `hooks` | `array<table>` | — | 生命周期 hook |

#### providers 表

每项定义一个 API 供应商，以唯一名称为 key。CLI 只从配置文件读取凭证，**不会**从 shell 环境变量自动取后备值。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | `string` | 是 | 供应商类型：`kimi`、`anthropic`、`openai`、`openai_responses`、`google-genai`、`vertexai` |
| `api_key` | `string` | 否 | API 密钥，明文写在配置文件 |
| `base_url` | `string` | 否 | API 基础 URL |
| `oauth` | `table` | 否 | OAuth 凭据引用（由登录流程自动注入）|
| `env` | `table<string, string>` | 否 | 供应商凭证的备用来源，见下文 |
| `custom_headers` | `table<string, string>` | 否 | 每次请求附加的自定义 HTTP 头 |

**env 子表**：可以把供应商惯用的键名（如 `KIMI_API_KEY`）写在 `[providers.<name>.env]` 里，作为 `api_key`/`base_url` 的备用来源。这个子表**只在配置文件里读取**，不会修改 shell 环境。

优先级：`api_key` 字段 > `env` 子表键 > 两者都缺时启动报错。

```toml
[providers.kimi.env]
KIMI_API_KEY = "sk-xxx"
KIMI_BASE_URL = "https://api.moonshot.ai/v1"
```

#### models 表

每项定义一个模型别名（即 `default_model` 或 `-m` 参数使用的名称），以唯一名称为 key。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `provider` | `string` | 是 | 使用的供应商名称，必须在 `providers` 中定义 |
| `model` | `string` | 是 | 调用 API 时实际传给服务端的模型 ID |
| `max_context_size` | `integer` | 是 | 最大上下文长度（token 数），必须 ≥ 1 |
| `max_output_size` | `integer` | 否 | 单次请求的输出 token 上限（仅 `anthropic` 读取）|
| `capabilities` | `array<string>` | 否 | 显式追加能力标签：`thinking`、`image_in`、`video_in`、`audio_in`、`tool_use` |
| `display_name` | `string` | 否 | UI 中显示的名称 |
| `reasoning_key` | `string` | 否 | 仅 `openai` 供应商，非标准推理字段名覆盖 |
| `adaptive_thinking` | `boolean` | 否 | 仅 `anthropic` 供应商，强制开启/关闭 adaptive thinking |

别名中含 `.` 时需加引号：

```toml
[models."gpt-4.1"]
provider = "openai"
model = "gpt-4.1"
max_context_size = 1047576
```

#### thinking 表

控制 Thinking 模式的全局默认行为。`mode = "off"` 会强制关闭 Thinking，即使顶层 `default_thinking = true` 也不例外。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `mode` | `string` | — | 触发策略：`auto`（由模型决定）、`on`（始终开启）、`off`（强制关闭）|
| `effort` | `string` | `high` | Thinking 强度：`low`、`medium`、`high`、`xhigh`、`max` |

#### loop_control 表

控制 Agent 执行循环的步数上限、单步重试次数和上下文压缩阈值。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_steps_per_turn` | `integer` | — | 单轮最大步数；不设或 `0` 则无上限 |
| `max_retries_per_step` | `integer` | `3` | 单步失败后的最大重试次数 |
| `reserved_context_size` | `integer` | — | 预留给模型输出的 token 数；低于此值触发自动压缩 |

#### background 表

控制后台任务的并发数。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_running_tasks` | `integer` | — | 同时运行的最大后台任务数 |
| `keep_alive_on_exit` | `boolean` | `false` | 会话关闭时是否保留后台任务 |

> `keep_alive_on_exit` 可被环境变量 `KIMI_CODE_BACKGROUND_KEEP_ALIVE_ON_EXIT` 覆盖。

#### experimental 表

存放实验功能 flag 的持久化覆盖。目前 `micro_compaction` 是唯一用户可见字段，默认 `true`。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `micro_compaction` | `boolean` | `true` | 清理较旧的大型工具结果内容，保留最近对话 |

#### services 表

配置网页搜索（`moonshot_search`）和网页抓取（`moonshot_fetch`）两项内置服务。只识别这两个固定 key。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `base_url` | `string` | 否 | 服务 API URL |
| `api_key` | `string` | 否 | API 密钥 |
| `oauth` | `table` | 否 | OAuth 凭据引用 |
| `custom_headers` | `table<string, string>` | 否 | 自定义 HTTP 头 |

```toml
[services.moonshot_search]
base_url = "https://api.moonshot.cn/v1/search"
api_key = "sk-xxx"

[services.moonshot_fetch]
base_url = "https://api.moonshot.cn/v1/fetch"
api_key = "sk-xxx"
```

#### permission 表

设置会话启动时自动加载的权限规则，控制 Agent 调用工具时是否需要用户确认。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `decision` | `string` | 是 | `allow`（放行）、`deny`（拒绝）、`ask`（每次询问）|
| `scope` | `string` | 否 | 规则范围：`turn-override`、`session-runtime`、`project`、`user`（默认 `user`）|
| `pattern` | `string` | 是 | 匹配模式，如 `Read`、`Bash(rm -rf*)` |
| `reason` | `string` | 否 | 规则说明，用于调试和审计 |

```toml
[[permission.rules]]
decision = "allow"
pattern = "Read"

[[permission.rules]]
decision = "deny"
pattern = "Bash(rm -rf*)"

[[permission.rules]]
decision = "ask"
pattern = "Bash"
```

> ⚠️ MCP server 的声明配置写在 `~/.kimi-code/mcp.json` 或项目内 `.kimi-code/mcp.json` 中，不在 `config.toml` 里。交互式配置入口是 `/mcp-config`。

### tui.toml

CLI 在同一目录下用 `tui.toml` 保存终端界面与客户端偏好（`~/.kimi-code/tui.toml`，或覆盖后的 `$KIMI_CODE_HOME/tui.toml`）。首次运行时以默认值创建，交互式命令 `/config`、`/theme`、`/editor` 会自动写入。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `theme` | `string` | `auto` | 配色主题：`auto`（跟随终端）、`dark`、`light` 或自定义主题名 |
| `[editor].command` | `string` | `""` | 外部编辑器命令；留空则回退到 `$VISUAL`/`$EDITOR` |
| `[notifications].enabled` | `boolean` | `true` | 是否发送桌面通知 |
| `[notifications].notification_condition` | `string` | `unfocused` | 何时通知：`unfocused`（仅终端失焦时）或 `always` |
| `[upgrade].auto_install` | `boolean` | `true` | 是否自动安装新版本 |

```toml
# ~/.kimi-code/tui.toml
theme = "auto"  # "auto" | "dark" | "light" | 自定义主题名

[editor]
command = ""  # 留空则使用 $VISUAL / $EDITOR

[notifications]
enabled = true
notification_condition = "unfocused"  # "unfocused" | "always"

[upgrade]
auto_install = true
```

修改在下次启动时生效，或用 `/reload-tui` 立即生效；`/reload` 会同时重载 `config.toml` 和 `tui.toml`。

---

## 平台与模型

Kimi Code CLI 支持同时接入多家 LLM 平台——Kimi Code 托管服务、Anthropic Claude、OpenAI 及兼容服务、Google Gemini 等。每个供应商对应一种 API 协议，模型在供应商之上声明自己的名称、上下文长度和能力。

### 支持的供应商类型

| 类型 | 协议 | 典型用途 |
|------|------|----------|
| `kimi` | OpenAI 兼容 | Kimi Code 托管服务、Kimi Platform API 密钥 |
| `anthropic` | Anthropic Messages | Claude 系列模型 |
| `openai` | OpenAI Chat Completions | OpenAI 及兼容服务、DeepSeek、Qwen 等 |
| `openai_responses` | OpenAI Responses API | OpenAI 较新的 Responses 接口 |
| `google-genai` | Google GenAI | Gemini API |
| `vertexai` | Google GenAI on Vertex | Google Cloud Vertex AI |

所有供应商默认以流式方式与模型交互。thinking、视觉、工具调用等能力按模型名前缀自动匹配，通常不需要手动声明。

> 凭证优先级：`api_key` 直接字段 > `[providers.<name>.env]` 子表键 > 两者都缺时启动报错。CLI **不会**从 shell 环境变量自动读取凭证。

### 各供应商接入示例

#### kimi

用于对接 Moonshot AI 的 OpenAI 兼容接口。使用 Kimi Code 托管服务时，`/login` 登录后自动配置，无需手动填写。

- 默认 `base_url`：`https://api.moonshot.ai/v1`
- 凭证键名：`KIMI_API_KEY`、`KIMI_BASE_URL`
- 额外能力：支持视频上传

```toml
[providers.kimi]
type = "kimi"
base_url = "https://api.moonshot.ai/v1"
api_key = "sk-xxxxx"
```

#### anthropic

用于对接 Claude API。标准 Claude 模型自动启用视觉、工具调用及 Thinking。

- 默认 `base_url`：跟随 Anthropic SDK 默认值
- 凭证键名：`ANTHROPIC_API_KEY`、`ANTHROPIC_BASE_URL`
- 默认 `max_tokens`：按模型自动推断；可覆盖 `max_output_size`

```toml
[providers.anthropic]
type = "anthropic"
api_key = "sk-ant-xxxxx"

[models."claude-opus-4-7"]
provider = "anthropic"
model = "claude-opus-4-7"
max_context_size = 200000
# max_output_size = 32000  # 可选，省略时使用模型推断默认值
```

#### openai

用于对接 OpenAI Chat Completions 协议，也可连接任何兼容该协议的第三方服务。第三方推理模型（DeepSeek、Qwen、One API 等）开箱即用：CLI 自动处理 `reasoning_content` 字段和 `reasoning_effort` 注入。

- 默认 `base_url`：`https://api.openai.com/v1`
- 凭证键名：`OPENAI_API_KEY`、`OPENAI_BASE_URL`

```toml
[providers.openai]
type = "openai"
base_url = "https://api.openai.com/v1"
api_key = "sk-xxxxx"
```

#### openai_responses

对应 OpenAI 较新的 Responses API，始终以流式方式工作。配置方式与 `openai` 相同。

- 默认 `base_url`：`https://api.openai.com/v1`
- 凭证键名：`OPENAI_API_KEY`、`OPENAI_BASE_URL`

```toml
[providers.openai-responses]
type = "openai_responses"
base_url = "https://api.openai.com/v1"
api_key = "sk-xxxxx"
```

#### google-genai

用于直连 Google Gemini API。thinking、视觉及多模态能力按模型名自动识别。

- 凭证键名：`GOOGLE_API_KEY`

```toml
[providers.gemini]
type = "google-genai"
api_key = "xxxxx"
```

#### vertexai

与 `google-genai` 共用实现，`type = "vertexai"` 时切换到 Vertex AI 访问路径。认证走 Google Cloud 标准 ADC 流程（`gcloud auth application-default login` 或 `GOOGLE_APPLICATION_CREDENTIALS` 服务账号 JSON）。

项目 ID 和区域必须写在 `[providers.vertexai.env]` 子表里：

```toml
[providers.vertexai]
type = "vertexai"

[providers.vertexai.env]
GOOGLE_CLOUD_PROJECT = "my-gcp-project"
GOOGLE_CLOUD_LOCATION = "us-central1"
```

```bash
gcloud auth application-default login  # 一次性完成认证
kimi
```

### /provider — 交互式供应商管理

在 TUI 中输入 `/provider` 打开供应商管理器，以交互方式添加或删除供应商：

| 按键 | 操作 |
|------|------|
| `↑`/`↓` | 移动光标 |
| `←`/`→` | 翻页 |
| `d` | 删除当前供应商（有 `[y/N]` 确认）|
| `Enter` | 在 `[Add New Platform]` 行添加新供应商 |

添加路径：

- **Known third-party provider**：从 `models.dev` 拉取模型目录，选供应商 → 输入 API 密钥 → 选默认模型
- **Custom registry (api.json)**：粘贴自定义 registry 地址和 Bearer token，CLI 自动创建 `providers`/`models` 条目

> ⚠️ 通过 `/login` 登录的 Kimi Code OAuth 托管账号不会在 `/provider` 里显示，请用 `/login` 和 `/logout` 管理。

非交互环境下：`kimi provider`。

---

## 配置覆盖

Kimi Code CLI 有三个地方可以影响运行参数：**配置文件**、**命令行选项**、**环境变量**。它们不是简单的"谁优先级高谁赢"——三者面向不同场景，作用范围互不相同：

| 配置来源 | 作用范围 | 典型用途 |
|----------|----------|----------|
| **配置文件** | 长期、持久 | 模型选择、密钥、循环控制等 |
| **命令行选项** | 本次启动 | 临时切换模型、进入 Plan 模式等 |
| **环境变量** | 运行时开关 | 数据目录定位、遥测关闭、OAuth 端点切换等 |

### 优先级规则

对普通运行参数（模型别名、Plan 模式、Skills 目录等），优先级从高到低：

1. **命令行选项**（`-m`、`--plan`、`--yolo` 等）：仅对本次启动生效
2. **用户配置文件**（`~/.kimi-code/config.toml`）：保存长期偏好
3. **少数环境变量**：明确覆盖特定配置字段（如 `KIMI_CODE_BACKGROUND_KEEP_ALIVE_ON_EXIT`）

> ⚠️ **重要**：普通运行参数不会从 shell 环境变量取后备值。供应商的 `api_key`/`base_url` 只从 `config.toml`（包括 `[providers.<name>.env]` 子表）读取，不会回退到 shell 里 `export` 的变量。唯一的例外是 `KIMI_MODEL_*` 通道。

### 供应商凭证解析

对单个供应商，凭证按以下顺序解析：

1. `[providers.<name>].api_key` — 配置文件里直接写的密钥，优先级最高
2. `[providers.<name>.env]` 子表里的对应键 — `api_key` 为空时才读这里
3. 两者都缺 → 启动报错

`base_url` 的解析方式相同。

### 命令行选项

| 选项 | 作用 |
|------|------|
| `-S`, `--session [id]` | 恢复指定会话；不带 `id` 时进入交互式选择 |
| `-C`, `--continue` | 续上当前目录的上一次会话 |
| `-y`, `--yolo` | 自动批准所有工具调用 |
| `--plan` | 以 Plan 模式启动 |
| `-m`, `--model <model>` | 指定本次使用的模型别名 |
| `-p`, `--prompt <prompt>` | 非交互模式：执行单条提示词后退出 |
| `--output-format <format>` | `-p` 模式的输出格式：`text` 或 `stream-json` |
| `--skills-dir <dir>` | 替换自动发现的 Skills 目录（可重复，仅本次生效）|

**互斥规则**（违反时启动报错）：

- `--output-format` 只能配合 `-p` 使用
- `--prompt` 不能同时用 `--yolo` 或 `--plan`
- `--continue` 和 `--session` 不能同时用
- 非 prompt 模式下，`--yolo` 和 `--plan` 不能配合 `--continue` 或 `--session`

> `--skills-dir` 是一次性替换，只影响本次启动。如需长期追加搜索目录，在 `config.toml` 里写 `extra_skill_dirs`。

### 典型场景

**隔离测试环境**：

```bash
KIMI_CODE_HOME="$PWD/.kimi-sandbox" kimi
```

**一次性使用测试密钥**：

```toml
[providers.kimi.env]
KIMI_API_KEY = "sk-test"
```

**跳过审批运行批处理任务**：

```bash
kimi --yolo -p "批量重命名以下文件..."
```

**临时进入 Plan 模式**：

```bash
kimi --plan
```

---

## 环境变量

Kimi Code CLI 通过环境变量控制少数运行时行为——迁移数据目录、关闭遥测、不改配置文件临时切换模型。

> ⚠️ **重要**：`KIMI_API_KEY`、`ANTHROPIC_API_KEY`、`OPENAI_API_KEY` 等密钥变量**不会**从 shell 环境变量自动读取。在终端里 `export KIMI_API_KEY=xxx` 不会让任何供应商获得密钥——必须写在 `config.toml` 的 `[providers.<name>]` 段或 `[providers.<name>.env]` 子表里。唯一的例外是 `KIMI_MODEL_*` 系列。

### 核心路径

| 环境变量 | 用途 | 默认值 |
|----------|------|--------|
| `KIMI_CODE_HOME` | 覆盖数据根目录，配置、会话、日志、OAuth 凭据等全部数据落到新路径 | `~/.kimi-code` |
| `KIMI_DISABLE_TELEMETRY` | 设为 `1` 关闭匿名遥测上报（也接受 `true`/`yes`/`y`，不区分大小写）| — |

### 供应商凭证键（写在 config.toml 里）

这些键名不是直接从 shell 读取的——它们是写在 `config.toml` 的 `[providers.<name>.env]` 子表里、作为 `api_key`/`base_url` 备用来源的键名。CLI 只从配置文件读取，不从 `process.env` 读取。

| 键名 | 适用供应商 | 默认值 |
|------|-----------|--------|
| `KIMI_API_KEY` | Kimi / Moonshot | 无 |
| `KIMI_BASE_URL` | Kimi / Moonshot | `https://api.moonshot.ai/v1` |
| `ANTHROPIC_API_KEY` | Anthropic | 无 |
| `ANTHROPIC_BASE_URL` | Anthropic | Anthropic SDK 默认值 |
| `OPENAI_API_KEY` | OpenAI（`openai` 和 `openai_responses`）| 无 |
| `OPENAI_BASE_URL` | OpenAI（`openai` 和 `openai_responses`）| `https://api.openai.com/v1` |
| `GOOGLE_API_KEY` | Google GenAI、Vertex AI | 无 |
| `VERTEXAI_API_KEY` | Vertex AI | 无 |
| `GOOGLE_CLOUD_PROJECT` | Vertex AI | 无 |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI | 无 |

> ⚠️ `GOOGLE_APPLICATION_CREDENTIALS`（服务账号 JSON 路径）是唯一走系统环境变量的例外——它由 Google SDK 自身通过 ADC 流程读取，CLI 不参与。其他所有键名都必须写在 `[providers.<name>.env]` 子表里。

### OAuth 与托管端点

| 环境变量 | 用途 | 默认值 |
|----------|------|--------|
| `KIMI_CODE_OAUTH_HOST` | OAuth 认证 host，优先级最高 | 未设时回退到 `KIMI_OAUTH_HOST` |
| `KIMI_OAUTH_HOST` | OAuth 认证 host，fallback | `https://auth.kimi.com` |
| `KIMI_CODE_BASE_URL` | OAuth 登录后的托管 API base URL | `https://api.kimi.com/coding/v1` |

> ⚠️ `KIMI_CODE_BASE_URL`（OAuth 托管服务，指向 `kimi.com`）和 `KIMI_BASE_URL`（API 密钥直连，指向 `moonshot.ai`）是两个不同的变量，请按场景区分。

### KIMI_MODEL_* 系列

不修改 `config.toml` 临时切换模型——设置 `KIMI_MODEL_NAME` 后，CLI 在内存里合成一个临时供应商，重启后失效。优先级高于 `config.toml` 的 `default_model`，但低于启动时 `-m <alias>` 选项。

```bash
export KIMI_MODEL_NAME="kimi-for-coding"
export KIMI_MODEL_API_KEY="YOUR_API_KEY"
export KIMI_MODEL_BASE_URL="https://api.example.com/v1"
export KIMI_MODEL_MAX_CONTEXT_SIZE="262144"
export KIMI_MODEL_CAPABILITIES="image_in,thinking"
kimi
```

| 环境变量 | 必填 | 用途 | 默认值 |
|----------|------|------|--------|
| `KIMI_MODEL_NAME` | 是 | 发送给 API 的模型 ID | — |
| `KIMI_MODEL_API_KEY` | 是 | API 密钥 | — |
| `KIMI_MODEL_PROVIDER_TYPE` | 否 | 供应商类型：`kimi`、`anthropic`、`openai` | `kimi` |
| `KIMI_MODEL_BASE_URL` | 否 | API 基础 URL | 各类型有各自默认值 |
| `KIMI_MODEL_MAX_CONTEXT_SIZE` | 否 | 最大上下文长度 | `262144`（256K）|
| `KIMI_MODEL_CAPABILITIES` | 否 | 逗号分隔的能力标签 | `image_in,thinking` |
| `KIMI_MODEL_DISPLAY_NAME` | 否 | 在 `/model` 中显示的名称 | 回退到 `KIMI_MODEL_NAME` |
| `KIMI_MODEL_MAX_OUTPUT_SIZE` | 否 | 单次输出上限（仅 anthropic）| 模型默认值 |
| `KIMI_MODEL_REASONING_KEY` | 否 | 推理字段名覆盖（仅 openai）| 自动探测 |
| `KIMI_MODEL_DEFAULT_THINKING` | 否 | 新会话的默认 Thinking 开关 | 跟随全局默认 |
| `KIMI_MODEL_THINKING_MODE` | 否 | Thinking 触发策略：`auto`/`on`/`off` | — |
| `KIMI_MODEL_THINKING_EFFORT` | 否 | Thinking 强度 | — |
| `KIMI_MODEL_ADAPTIVE_THINKING` | 否 | 强制开启/关闭 adaptive thinking（仅 anthropic）| 按模型名推断 |

设置了 `KIMI_MODEL_NAME` 但缺少必填变量时，启动会立即失败并给出明确提示。

### 运行时开关

| 环境变量 | 用途 | 合法值 |
|----------|------|--------|
| `KIMI_DISABLE_TELEMETRY` | 关闭匿名遥测上报 | `1`、`true`、`yes`、`y`（不区分大小写）|
| `KIMI_CODE_BACKGROUND_KEEP_ALIVE_ON_EXIT` | 会话关闭时是否保留后台任务，优先级高于 `config.toml` | `1`/`true`/`yes`/`on`；`0`/`false`/`no`/`off` |
| `KIMI_CODE_PLUGIN_MARKETPLACE_URL` | 替换 `/plugins` 加载的 marketplace JSON | URL 或本地路径 |
| `KIMI_CODE_EXPERIMENTAL_FLAG` | 启用所有已注册的实验功能 | `1`、`true`、`yes`、`on` |
| `KIMI_CODE_EXPERIMENTAL_MICRO_COMPACTION` | 覆盖 `[experimental].micro_compaction` | 真值或假值 |
| `KIMI_SHELL_PATH` | Windows 上覆盖 Git Bash 路径 | 绝对路径 |
| `KIMI_MODEL_MAX_COMPLETION_TOKENS` | 单步 LLM 请求的 max_completion_tokens 硬上限（仅 kimi）| 正整数；`0` 或负数禁用 |
| `KIMI_MODEL_TEMPERATURE` | 每次请求的采样温度（仅 kimi）| 数字，如 `0.3` |
| `KIMI_MODEL_TOP_P` | 每次请求的核采样 top_p（仅 kimi）| 数字，如 `0.95` |
| `KIMI_MODEL_THINKING_KEEP` | Moonshot 保留思考透传（仅 kimi，Thinking 开启时注入）| API 接受的值，如 `all` |
| `KIMI_CODE_NO_AUTO_UPDATE` | 完全禁用更新预检 | `1`/`true`/`yes`/`on` |
| `KIMI_DISABLE_CRON` | 禁用定时任务工具 | `1` 表示禁用 |

### 诊断日志

| 环境变量 | 用途 | 默认值 |
|----------|------|--------|
| `KIMI_LOG_LEVEL` | 日志级别：`off`、`error`、`warn`、`info`、`debug` | `info` |
| `KIMI_LOG_GLOBAL_MAX_BYTES` | 全局日志文件单个最大字节数 | `6291456`（6 MB）|
| `KIMI_LOG_GLOBAL_FILES` | 全局日志文件保留份数 | `5` |
| `KIMI_LOG_SESSION_MAX_BYTES` | 会话级日志文件单个最大字节数 | `5242880`（5 MB）|
| `KIMI_LOG_SESSION_FILES` | 会话级日志文件保留份数 | `3` |

### 系统环境变量

CLI 还会读取一些标准系统变量来检测运行环境，不会修改它们：

| 变量 | 用途 |
|------|------|
| `HOME` | 解析默认数据路径 |
| `VISUAL`、`EDITOR` | 外部编辑器命令（`VISUAL` 优先）|
| `PATH` | 定位 `rg`、`fd`、`fdfind`、`git` 等依赖 |
| `NO_COLOR`、`FORCE_COLOR` | 控制颜色输出（遵循 no-color.org 约定）|
| `CI` | 非空且非 `"0"` 时关闭主题检测，回退深色主题 |
| `TERM_PROGRAM`、`TERM`、`TMUX` | 检测终端特性和通知支持 |
| `DISPLAY`、`WAYLAND_DISPLAY`、`XDG_SESSION_TYPE` | 检测 Linux 图形会话（剪贴板和图片功能）|
| `WSL_DISTRO_NAME`、`WSLENV` | 检测 WSL，剪贴板 PowerShell 桥接 |
| `LOCALAPPDATA` | Windows 上探测 Git Bash 安装路径时的 fallback |

### HTTP 代理

Kimi Code 遵循标准代理环境变量，所有出网流量都走代理：

| 变量 | 用途 |
|------|------|
| `HTTP_PROXY`/`http_proxy` | 用于 `http://` 请求的代理 |
| `HTTPS_PROXY`/`https_proxy` | 用于 `https://` 请求的代理 |
| `ALL_PROXY`/`all_proxy` | 兜底代理；SOCKS 代理通常设在这里 |
| `NO_PROXY`/`no_proxy` | 以逗号分隔的、绕过代理的主机列表 |

同时支持 HTTP(S) 代理和 SOCKS 代理。SOCKS 代理通过 scheme 识别——`socks5://`、`socks5h://`、`socks4://` 或 `socks://`（`socks5://` 的别名）。对 HTTP/HTTPS 流量，HTTP(S) 代理优先于 `ALL_PROXY`。

仅当设置了任一代理变量时才启用代理，否则直连。回环地址（`localhost`、`127.0.0.1`、`::1`）始终绕过代理，因此配置了代理后本地服务（如 localhost 上的 MCP 服务）仍能正常工作。

以 Node 子进程运行的 stdio MCP 服务，在 Node 版本支持 `NODE_USE_ENV_PROXY` 时（Node ≥ 22.21 或 ≥ 24.5）会自动遵循 `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY`；SOCKS 代理仅作用于 Kimi Code 自身的流量。

---

## 数据路径

Kimi Code CLI 把所有运行时数据——配置文件、会话历史、登录凭据、诊断日志——集中存放在 `~/.kimi-code/` 下。

### 数据根目录

默认数据根在不同平台的实际路径：

| 平台 | 路径 |
|------|------|
| macOS | `/Users/<name>/.kimi-code` |
| Linux | `/home/<name>/.kimi-code` |
| Windows | `C:\Users\<name>\.kimi-code` |

如需迁移：`export KIMI_CODE_HOME=/path/to/custom/kimi-code`。设置后，配置、会话、日志、OAuth 凭据、Kimi 专属用户级 Skills、全局 `AGENTS.md` 等 Kimi Code 数据都会落到新路径下。

> 通用 `.agents` 资源仍放在真实 OS home 下，以便跨工具共享。例如，用户级通用 Skills 仍位于 `~/.agents/skills/`，而 Kimi 专属用户级 Skills 会随 `KIMI_CODE_HOME` 移动。

### 目录结构

```
$KIMI_CODE_HOME（默认 ~/.kimi-code）
├── config.toml          # 用户配置
├── tui.toml             # 终端界面偏好（含自动更新开关）
├── AGENTS.md            # 全局 Kimi 专属 Agent 指令（可选）
├── mcp.json             # 用户级 MCP server 声明（可选）
├── skills/              # Kimi 专属用户级 Skills（可选）
├── plugins/
│   ├── installed.json   # 已安装 plugin 记录与启用状态
│   └── managed/         # zip/本地路径安装的 plugin 副本
├── session_index.jsonl  # 会话索引
├── credentials/         # OAuth 凭据（目录 0700，文件 0600）
│   ├── <name>.json
│   └── mcp/
│       └── <key>-<suffix>.json
├── sessions/            # 会话数据
│   └── <workDirKey>/<sessionId>/
├── bin/
│   ├── rg               # Grep 使用的托管 ripgrep 二进制
│   └── fd               # 文件引用使用的托管 fd 二进制
├── logs/
│   └── kimi-code.log    # 全局诊断日志
├── updates/
│   ├── latest.json
│   ├── install.json
│   └── install.lock
└── user-history/
    └── <md5(workDir)>.jsonl
```

**各类文件说明：**

| 文件/目录 | 用途 |
|-----------|------|
| `config.toml` | 主运行时配置，详见[配置文件](#configtoml) |
| `tui.toml` | 终端界面客户端偏好，包括 `[upgrade].auto_install`（自动更新，默认开启）|
| `AGENTS.md` | 全局 Kimi 专属 Agent 指令，会随 `KIMI_CODE_HOME` 移动 |
| `mcp.json` | 用户级 MCP server 声明，启动时与项目内的 `.kimi-code/mcp.json` 合并加载 |
| `skills/` | Kimi 专属用户级 Skills，会随 `KIMI_CODE_HOME` 移动 |
| `plugins/installed.json` | 记录已安装的 plugin、启用状态及 MCP server 能力状态 |
| `plugins/managed/` | 本地路径和 zip URL 安装的文件副本 |
| `credentials/` | OAuth 凭据目录，权限 `0o700`（目录）/`0o600`（文件），仅当前用户可读写 |
| `bin/rg`、`bin/fd` | 托管的 ripgrep 和 fd 二进制；首次使用时自动下载，之后复用 |
| `logs/kimi-code.log` | 全局诊断日志，记录启动、登录、导出等跨会话事件 |
| `updates/` | 自动更新机制维护的状态文件 |
| `user-history/` | 终端输入历史，按工作目录分开保存 |

### 会话数据

每个会话的数据存在 `sessions/<workDirKey>/<sessionId>/` 下，同时在顶层 `session_index.jsonl` 里维护索引。`workDirKey` 是从工作目录路径生成的桶名，格式为 `wd_<slug>_<sha256前12位>`。

会话目录内部包含：

| 文件 | 用途 |
|------|------|
| `state.json` | 会话标题、lastPrompt、创建/更新时间、forkedFrom 等元数据 |
| `upcoming-goals.json` | 由 `/goal next <objective>` 创建的 TUI 专属队列 |
| `agents/main/wire.jsonl` | 主 Agent 的完整通信记录，用于会话恢复和回放 |
| `agents/main/plans/` | Plan 模式下写入的计划文件，按计划 id 命名 |
| `agents/agent-0/` 等 | 子 Agent 实例目录，各自含 `wire.jsonl` |
| `logs/kimi-code.log` | 该会话的诊断日志 |
| `tasks/` | 后台任务持久化：`tasks/<task_id>.json` 保存状态/pid/退出码，`tasks/<task_id>/output.log` 保存输出 |
| `cron/` | 定时任务持久化，`kimi resume` 时重新加载到调度器 |

### 清理数据

| 需求 | 操作 |
|------|------|
| 重置配置 | 删除 `~/.kimi-code/config.toml` |
| 重置终端界面偏好 | 删除 `~/.kimi-code/tui.toml` |
| 清理所有会话 | 删除 `~/.kimi-code/sessions/` 和 `session_index.jsonl` |
| 清理诊断日志 | 删除 `~/.kimi-code/logs/` |
| 清理输入历史 | 删除 `~/.kimi-code/user-history/` |
| 重置更新状态 | 删除 `~/.kimi-code/updates/latest.json` |
| 强制重新下载托管 rg 和 fd | 删除 `~/.kimi-code/bin/` |
| 清除供应商 OAuth 登录态 | 运行 `/logout`，或删除对应的 `credentials/<name>.json` |
| 清除 MCP server OAuth 登录态 | 删除 `credentials/mcp/`（`/logout` 不会清理 MCP 凭据）|
| 移除用户级 MCP 声明 | 删除 `$KIMI_CODE_HOME/mcp.json` |
| 清理全局 Kimi 专属 Agent 指令 | 删除 `$KIMI_CODE_HOME/AGENTS.md` |
| 清理 plugin 安装记录 | 删除 `$KIMI_CODE_HOME/plugins/` |
| 清空 Kimi 专属用户级 Skills | 删除 `$KIMI_CODE_HOME/skills/` |

---

## 术语表

| 术语 | 定义 | 上下文/示例 |
|------|------|------------|
| TOML | 一种结构清晰的纯文本配置格式，支持表、数组表、键值对等 | Kimi Code CLI 使用 TOML 作为配置文件格式 |
| Provider | API 供应商，定义如何连接到某个 AI 平台 | `kimi`、`anthropic`、`openai` 等类型 |
| Model Alias | 模型的短名称，用于 `-m` 参数和 `default_model` | `kimi-code/kimi-for-coding`、`claude-opus-4-7` |
| Thinking 模式 | 模型的深度推理模式，可设置触发策略和强度 | `mode = "auto"`、`effort = "high"` |
| YOLO 模式 | 权限模式的一种，自动批准所有工具调用 | `default_permission_mode = "yolo"` |
| Plan 模式 | 先出计划再执行的工作模式 | `default_plan_mode = true` 或 `--plan` |
| workDirKey | 从工作目录路径生成的桶名，用于会话分组 | 格式：`wd_<slug>_<sha256前12位>` |
| wire.jsonl | Agent 通信记录文件，按时间顺序记录事件 | 用于会话恢复和回放 |
| ADC | Application Default Credentials，Google Cloud 的标准认证流程 | `gcloud auth application-default login` |
| OAuth | 开放授权协议，Kimi Code 托管服务使用 OAuth 而非静态 API 密钥 | 通过 `/login` 完成 |

---

> 📚 **官方文档**：https://moonshotai.github.io/kimi-code/zh/
