---
name: 个性化定制 Kimi Code CLI
description: Kimi Code CLI 扩展机制指南，涵盖 MCP、Agent Skills、Plugins、Agent 与 Hooks 等定制能力
category: 定制化
order: 2
---

# 个性化定制 Kimi Code CLI

> Kimi Code CLI 提供丰富的扩展机制，让你能够接入外部工具、定义专业工作流、打包可复用能力，并通过 Hooks 实现自动化响应。

---

## 目录

- [Model Context Protocol (MCP)](#model-context-protocol-mcp)
  - [什么是 MCP](#什么是-mcp)
  - [接入方式](#接入方式)
  - [配置](#配置)
  - [工具命名与权限](#工具命名与权限)
  - [安全性](#安全性)
- [Agent Skills](#agent-skills)
  - [创建 Skill](#创建-skill)
  - [文件格式](#文件格式)
  - [Frontmatter 字段](#frontmatter-字段)
  - [正文占位符](#正文占位符)
  - [Skill 存放位置](#skill-存放位置)
  - [调用 Skill](#调用-skill)
  - [完整示例](#完整示例)
- [Plugins](#plugins)
  - [安装与管理](#安装与管理)
  - [从 GitHub 安装](#从-github-安装)
  - [Kimi Datasource](#kimi-datasource)
  - [Plugin Manifest](#plugin-manifest)
  - [Plugin 中的 MCP Servers](#plugin-中的-mcp-servers)
  - [安全模型](#安全模型)
- [Agent 与子 Agent](#agent-与子-agent)
  - [内置子 Agent](#内置子-agent)
  - [调用方式](#调用方式)
  - [上下文隔离与资源开销](#上下文隔离与资源开销)
  - [权限继承](#权限继承)
  - [指令文件](#指令文件)
- [Hooks](#hooks)
  - [Hooks 是怎么工作的](#hooks-是怎么工作的)
  - [快速上手](#快速上手)
  - [配置](#配置-1)
  - [事件数据格式](#事件数据格式)
  - [返回值](#返回值)
  - [事件一览](#事件一览)
  - [示例：阻断危险 Shell 命令](#示例阻断危险-shell-命令)

---

## Model Context Protocol (MCP)

### 什么是 MCP

**Model Context Protocol（MCP）** 是一个开放协议，让模型可以安全地调用外部进程或服务暴露的工具——例如读取 GitHub issues、查询数据库、操作本地文件系统。Kimi Code CLI 作为 MCP client 接入这些外部工具，并把它们与内置工具（`Read`、`Bash`、`Grep` 等）一起暴露给 Agent 使用，行为上没有差异。

### 接入方式

Kimi Code CLI 支持两种 MCP server 接入方式：

- **stdio**：CLI 以子进程方式启动本地 MCP server，通过标准输入输出通信。适合本地命令行工具。
- **HTTP**：CLI 连接一个已在运行的 HTTP 端点。适合远程服务或需要持久运行的进程。

### 配置

MCP server 配置写在 `mcp.json` 中，分两层：

- **用户级**：`~/.kimi-code/mcp.json`（或 `$KIMI_CODE_HOME/mcp.json`），跨项目共享
- **项目级**：工作目录下的 `.kimi-code/mcp.json`，只对当前仓库生效

同名条目以项目级为准，覆盖用户级。

在 TUI 中运行 `/mcp-config` 可以交互式地新增、编辑或删除 server，无需手动编辑 JSON 文件。运行 `/mcp` 可查看当前所有 server 的连接状态。

**mcp.json 的结构：**

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    },
    "linear": {
      "url": "https://mcp.linear.app/mcp"
    }
  }
}
```

含 `command` 字段的条目为 stdio server，含 `url` 字段的条目为 HTTP server，通常不需要手写 transport 字段。

**可选字段：**

| 字段 | 类型 | 适用方式 | 说明 |
|------|------|----------|------|
| `env` | `Record<string, string>` | stdio | 注入子进程的环境变量 |
| `cwd` | `string` | stdio | 子进程工作目录 |
| `headers` | `Record<string, string>` | HTTP | 附加到每次请求的静态请求头 |
| `enabled` | `boolean` | 两者 | 设为 `false` 可禁用该 server |
| `startupTimeoutMs` | `number` | 两者 | 连接超时，默认 30000 毫秒 |
| `toolTimeoutMs` | `number` | 两者 | 单次工具调用超时 |
| `enabledTools` | `string[]` | 两者 | 工具白名单 |
| `disabledTools` | `string[]` | 两者 | 工具黑名单 |

HTTP server 支持通过 `headers` 或 `bearerTokenEnvVar` 提供静态凭证。需要 OAuth 时，运行 `/mcp-config login <server-name>` 完成浏览器授权。

Plugins 也可以在 manifest 中声明 MCP servers。Plugin 声明的 servers 默认启用，可以在 `/plugins` 中禁用或重新启用，然后开启新会话。

> ⚠️ **注意**：项目级 `.kimi-code/mcp.json` 中的 stdio 条目会在会话启动时执行本地命令，只在你信任的仓库里启用。

### 工具命名与权限

MCP 工具按 `mcp__<server>__<tool>` 格式命名，例如 `mcp__github__create_issue`。权限规则中支持 `*` 和 `**` 通配，例如 `mcp__github__*` 命中该 server 下所有工具。MCP 工具参数不参与权限匹配。

未命中权限规则的调用会触发审批请求；在审批弹窗中选择"Approve for this session"后，本次会话内的后续同类调用自动放行。

也可以在 `config.toml` 的 `[[permission.rules]]` 中预置永久规则：

```toml
[[permission.rules]]
decision = "allow"
pattern = "mcp__github__*"

[[permission.rules]]
decision = "deny"
pattern = "mcp__filesystem__write_file"
```

### 安全性

接入外部 MCP server 时需注意：

- 只接入可信来源的 server
- 在审批请求中核查工具名与参数是否合理
- 对高风险工具（写文件、执行命令等）维持手动审批，避免用 `mcp__*` 通配放行全部工具

> ⚠️ **注意**：在 YOLO 模式下，MCP 工具调用会被自动批准。仅在完全信任所接入的 MCP server 时使用此模式。

---

## Agent Skills

Agent Skills 是 Kimi Code CLI 扩展模型能力的轻量机制。一个 Skill 就是一份带 YAML frontmatter 的 Markdown 文档，描述某项专业知识或工作流程——例如项目的代码风格规范、PR review 流程、提交消息格式。

相比每次把同样的指引粘到提示词里，Skill 的优势在于：内容沉淀在文件里、可以跨项目和团队复用、可以通过斜杠命令一键加载，也可以让模型在需要时自动调用。

### 创建 Skill

Skill 文件需放在已知的扫描目录中。支持两种文件结构：

- **目录形式（推荐）**：在 Skills 目录下创建一个子目录，主文件命名为 `SKILL.md`，可在同目录下放置脚本、参考资料等辅助文件。同目录下同时存在 `<name>/SKILL.md` 和同名 `<name>.md` 时，以子目录为准。
- **扁平形式**：直接使用单个 `.md` 文件，Skill 名称取文件名（去掉 `.md`）。

### 文件格式

`SKILL.md` 由 YAML frontmatter 和 Markdown 正文两部分组成：

```markdown
---
name: code-style
description: 项目代码风格规范，定义命名、缩进、注释和文件组织
type: prompt
whenToUse: 当用户让我编写、修改或审查项目源代码时
disableModelInvocation: false
arguments:
  - target
  - mode
---

请按下述规范处理代码：

- 缩进使用 2 空格
- 变量名使用 `camelCase`，类型名使用 `PascalCase`
- 公开函数必须带 TSDoc 注释
- 单行不超过 100 字符
```

### Frontmatter 字段

| 字段 | 说明 |
|------|------|
| `name` | Skill 名称。目录型 `SKILL.md` 中为必填；扁平 `.md` 文件省略时使用文件名。名称大小写不敏感 |
| `description` | 一行总结，模型用它来判断何时使用这个 Skill。目录型 `SKILL.md` 中为必填；扁平 `.md` 文件省略时回退到正文第一行非空内容（截至 240 字符） |
| `type` | Skill 类型：`prompt`（默认）、`inline`（与 prompt 语义相同）、`flow`（只支持手动调用，不支持模型自动调用）。其他值会被跳过 |
| `whenToUse` | 触发场景描述。也接受 `when-to-use`、`when_to_use` 写法 |
| `disableModelInvocation` | 设为 `true` 时禁止模型自动调用此 Skill。也接受 `disable-model-invocation`、`disable_model_invocation` 写法 |
| `arguments` | 命名参数列表，可写成字符串数组或空白分隔的字符串（如 `arguments: target mode`）。声明后，正文可用 `$<name>` 读取参数 |

> ⚠️ **注意**：目录型 `SKILL.md` 中 `name` 和 `description` 必须显式填写，省略任意一项均会导致解析失败。

### 正文占位符

正文在发送给模型前会展开少量占位符：

- `$ARGUMENTS`：调用时附带的完整原始参数字符串
- `$ARGUMENTS[0]`、`$ARGUMENTS[1]` 及简写 `$0`、`$1`：按空白分词后的位置参数（从 0 开始）
- `$<name>`：`arguments` 中声明的命名参数
- `${KIMI_SKILL_DIR}`：当前 Skill 文件所在目录

位置参数支持单双引号包裹，如 `/skill:commit "fix login" patch` 中 `$0` 展开为 `fix login`。若正文不含任何参数占位符，调用时附带的文本会以 `\n\nARGUMENTS: <文本>` 的形式追加到正文末尾。

### Skill 存放位置

Kimi Code CLI 按作用域分四档扫描，越具体的作用域优先级越高：**Project > User > Extra > Built-in**

**用户级**（对所有项目生效）：
- `$KIMI_CODE_HOME/skills/`（默认：`~/.kimi-code/skills/`）
- `~/.agents/skills/`

Kimi 专属用户级 Skill 目录会随 `KIMI_CODE_HOME` 移动，因此隔离数据根时也会隔离 Kimi 专属 Skills。通用 `~/.agents/skills/` 目录仍放在真实 OS home 下，以便跨工具共享。

**项目级**（项目根 = 工作目录向上最近的含 `.git` 的目录）：
- `.kimi-code/skills/`
- `.agents/skills/`

**额外目录**：通过 `config.toml` 顶层的 `extra_skill_dirs` 声明：

```toml
extra_skill_dirs = ["~/team-skills", ".agents/team-skills"]
```

**内置 Skills** 随 CLI 一起分发，优先级最低。它们为常见任务提供开箱即用的工作流，例如配置 MCP server、定制 TUI 主题和编辑配置文件。

### 调用 Skill

用户通过斜杠命令主动调用：

```
/skill:code-style
/skill:git-commits 修复登录接口的并发问题
```

模型也可以根据 `description` 和 `whenToUse` 自动调用 Skill（除非 `disableModelInvocation` 设为 `true` 或 `type` 为 `flow`）。Skill 调用时最多允许嵌套 3 层，超过后会被终止。

### 完整示例

```markdown
---
name: review-pr
description: 按团队标准审查一个 Pull Request，输出结构化的 review 报告
type: prompt
whenToUse: 当用户让我审查 PR、检查代码变更或评估提交质量时
arguments:
  - pr_ref
---

请按照以下流程审查用户指定的 PR：$pr_ref

1. 拉取并阅读 `$pr_ref` 的全部 diff。
2. 对照以下检查项逐条核对：
   - 是否包含对应的测试用例
   - 公开 API 是否有文档更新
   - 是否引入了新的依赖；若有，说明引入理由
   - 错误处理是否覆盖了边界情况
3. 参考同目录下的检查清单：`references/checklist.md`
4. 输出一份 review 报告，包含：
   - 总体结论（approve / request changes / comment）
   - 必须修改项（blocking）
   - 建议改进项（non-blocking）
   - 值得肯定的地方
```

保存为 `$KIMI_CODE_HOME/skills/review-pr/SKILL.md`，检查清单放在同目录的 `references/checklist.md`，重开会话后即可通过 `/skill:review-pr #1234` 调用，其中 `#1234` 会展开到 `$pr_ref`。

---

## Plugins

Plugins 把可复用的 Kimi Code CLI 能力打包成可安装单元——可以添加 Agent Skills、在会话启动时自动加载指定 Skill，也可以声明 MCP servers 来提供真实工具能力。适合把工作流共享给团队、连接外部服务，或从官方 marketplace 安装扩展。

Kimi Code CLI 对 plugin 采用保守的加载策略：安装 plugin 时不会执行其中的 Python、Node.js、Shell、hook 或命令脚本。

### 安装与管理

在 TUI 中运行 `/plugins` 打开 plugin 管理器，可以在这里完成所有日常操作。常用按键：

| 按键 | 操作 |
|------|------|
| `Enter` 或 `→` | 打开选中项，或安装 marketplace 中的 plugin |
| `Space` | 启用或禁用已安装 plugin；在 marketplace 中安装或更新 plugin |
| `M` | 管理选中 plugin 的 MCP servers |
| `←` 或 `Esc` | 返回上一层 |

在 marketplace 列表里，已安装且有新版本的 plugin 会显示 `update <本地版本> → <最新版本>`，已是最新显示 `installed · v<版本>`，未安装显示 `install v<版本>`。选中可更新的项按 Enter 即可更新。

也可以直接使用斜杠命令：

| 命令 | 说明 |
|------|------|
| `/plugins` | 打开交互式 plugin 管理器 |
| `/plugins list` | 列出已安装 plugins |
| `/plugins install <path-or-url>` | 从本地目录、zip URL 或 GitHub 仓库 URL 安装 |
| `/plugins marketplace [source]` | 浏览官方 marketplace |
| `/plugins info <id>` | 查看 plugin 详情和 diagnostics |
| `/plugins enable <id>` | 启用 plugin |
| `/plugins disable <id>` | 禁用 plugin |
| `/plugins remove <id>` | 移除 plugin（需二次确认） |
| `/plugins reload` | 重载 installed.json 和各 plugin manifest |
| `/plugins mcp enable <id> <server>` | 启用 plugin 声明的 MCP server |
| `/plugins mcp disable <id> <server>` | 禁用 plugin 声明的 MCP server |

Plugin 管理器会展示每个安装的来源和信任徽章：`kimi-official`（来自官方地址）、`curated`（来自精选地址）、`third-party`（其他所有情况）。

### 从 GitHub 安装

通过 `/plugins install <url>` 可以直接从 GitHub 仓库安装，支持四种 URL 形式：

- `https://github.com/<owner>/<repo>`：安装最新 release；无 release 时回落到默认分支
- `https://github.com/<owner>/<repo>/tree/<ref>`：安装指定分支、tag 或短 commit SHA
- `https://github.com/<owner>/<repo>/releases/tag/<tag>`：钉死具体 tag
- `https://github.com/<owner>/<repo>/commit/<sha>`：钉死具体 commit

网络请求只走 `github.com` 重定向和 `codeload.github.com` 下载，不调用 `api.github.com`。

**注意事项：**
- Plugin 变更只对新会话生效。安装、启用/禁用、移除后，需通过 `/reload` 重载插件或通过 `/new` 开启新会话
- 本地安装会被拷贝到 `$KIMI_CODE_HOME/plugins/managed/<id>/`，CLI 始终从这份托管副本运行
- 移除 plugin 只会删除安装记录，托管副本和原始源文件仍保留在磁盘上
- Plugin 目前按用户安装，对所有项目生效，暂不支持项目级安装范围

### Kimi Datasource

Kimi Datasource 是 Kimi Code 官方数据插件，让你通过自然语言直接查询金融行情、宏观经济、企业工商、学术文献和中国法律法规，无需手动调用接口或申请任何数据账号。

**安装：**
1. 需先通过 `/login` 完成 Kimi Code 账号 OAuth 登录
2. 运行 `/plugins`，选择 Marketplace
3. 找到 Kimi Datasource，按 Space 安装
4. 安装完成后运行 `/reload` 重载插件，即可使用

**使用方式：**
安装完成后，直接用自然语言描述你的需求，Kimi Code 会自动调用数据能力；也可以通过 `/skill:kimi-datasource` 明确触发数据查询 Skill。

**能做什么：**

| 场景 | 示例 |
|------|------|
| 实时量化研究 | 一句话拉取近三年的每日收盘价、MACD 和 KDJ 信号 |
| 跨国宏观对比 | 基于世界银行 50 年历史数据，对比多国 GDP 增速、贸易额、人口结构 |
| 合同前风险排查 | 输入公司名，立刻拿到工商注册信息、股权穿透、司法纠纷和失信记录 |
| 文献综述加速 | 直接列出高引论文、主要作者和核心结论 |
| 法律条文速查 | 一句话定位《民法典》相关条文原文、效力级别和时效性 |

**数据覆盖：**

| 类别 | 覆盖范围 |
|------|----------|
| 股票行情 | A 股、港股、美股及全球主要市场实时/历史行情、技术指标、财务报表、股票筛选 |
| 宏观经济 | 世界银行 189 个成员国、50 年以上历史时间序列（GDP、贸易、人口、气候等）|
| 企业数据 | 中国大陆境内企业工商信息、股权穿透、司法风险、关联图谱 |
| 学术文献 | 物理、数学、计算机、金融、经济等领域百万量级论文，支持预印本查询 |
| 法律法规 | 中国法律法规与司法案例：宪法、法律、司法解释、部门规章等各效力层次的法规语义/关键词检索与详情，普通及权威判例检索 |

> ⚠️ **注意**：数据查询按次计费，消耗 Kimi Code 账号额度；插件为只读查询，不提供任何写入或交易功能；技术指标及实时行情仅在交易时段内可用；AI 输出内容仅供参考，不构成任何投资或商业决策建议。

### Plugin Manifest

Plugin 是一个带 manifest 的目录或 zip 文件。Manifest 可以放在以下任一位置：

```
<plugin_root>/kimi.plugin.json
<plugin_root>/.kimi-plugin/plugin.json
```

两个文件同时存在时，以 `kimi.plugin.json` 为准。

**示例：**

```json
{
  "name": "kimi-finance",
  "version": "1.0.0",
  "description": "Finance data and analysis workflows for Kimi Code CLI",
  "skills": "./skills/",
  "sessionStart": {
    "skill": "using-finance"
  },
  "interface": {
    "displayName": "Kimi Finance",
    "shortDescription": "Market data and financial analysis workflows"
  }
}
```

**支持的字段：**

| 字段 | 说明 |
|------|------|
| `name` | 必填，作为 plugin id。必须匹配 `[a-z0-9][a-z0-9_-]{0,63}` |
| `version`、`description`、`keywords`、`author`、`homepage`、`license` | 展示元数据 |
| `interface` | 在 `/plugins` 中展示的字段：`displayName`、`shortDescription`、`longDescription`、`developerName`、`websiteURL` |
| `skills` | 一个或多个 `./` 路径，必须位于 plugin 根目录内。省略时根目录的 `SKILL.md` 被当作单个 Skill root |
| `sessionStart.skill` | 在新会话或恢复会话开始时，把指定 plugin Skill 加载到主 Agent |
| `skillInstructions` | 每次加载此 plugin 的 Skill 时一并附带的额外说明 |
| `mcpServers` | MCP server 声明，默认启用，可从 `/plugins` 中禁用 |

`tools`、`commands`、`hooks`、`apps`、`inject`、`configFile` 等不支持的运行时字段会显示为 diagnostics 并被忽略。

**Skills 与会话启动：**

Plugin Skills 使用与普通 Agent Skills 相同的 `SKILL.md` 格式，典型目录结构如下：

```
my-plugin/
  kimi.plugin.json
  skills/
    using-my-plugin/
      SKILL.md
    another-workflow/
      SKILL.md
```

`sessionStart.skill` 在会话启动时把一个 plugin Skill 加载到主 Agent，适合放置初始化说明、工作流规则，或把其他工具中的术语映射到 Kimi Code CLI。它只注入文本，不执行代码。

无论 Skill 通过哪种方式加载（`sessionStart.skill`、`/skill:<name>` 或模型自动调用），`skillInstructions` 都会随该 plugin 的 Skill 一起出现。

### Plugin 中的 MCP Servers

当 plugin 需要真实工具能力时，可以在 manifest 中声明 `mcpServers`，复用 MCP 的 schema。

**Stdio server（本地命令）：**

```json
{
  "mcpServers": {
    "finance": {
      "command": "uvx",
      "args": ["kimi-finance-mcp"]
    }
  }
}
```

**HTTP server（远程服务）：**

```json
{
  "mcpServers": {
    "docs": {
      "url": "https://example.com/mcp"
    }
  }
}
```

对于 stdio servers，`command` 可以是 PATH 上的命令，也可以是 plugin 根目录内以 `./` 开头的路径。`cwd` 同理，必须以 `./` 开头并位于 plugin 根目录内，否则该 server 会被忽略。

Plugin MCP servers 只会在新会话中启动。启用或禁用某个 server：

```
/plugins mcp disable kimi-finance finance
/new

/plugins mcp enable kimi-finance finance
/new
```

### 安全模型

Plugin 的加载范围有限，以下操作不会在安装或会话启动时发生：

- 不会执行命令型 plugin tools、hooks 或旧式工具运行时
- 所有路径在解析符号链接后仍必须位于 plugin 根目录内
- 已启用 plugin 的 MCP servers 只在新会话中启动，且可随时从 `/plugins` 禁用
- 损坏的 manifest 或不安全路径会显示在 `/plugins info <id>` 的 diagnostics 中，不影响其他会话

---

## Agent 与子 Agent

Kimi Code CLI 中的每次会话都由一个**主 Agent** 驱动。主 Agent 理解用户意图、规划步骤、调用工具，并在需要时向外派发**子 Agent** 处理更聚焦的子任务——例如探索一个陌生代码库、并行审阅多处实现、或在不触碰主上下文的情况下规划一次大型重构。

子 Agent 接受主 Agent 给出的任务描述，在自己的独立上下文里工作，最后把结论返回。它不会与用户直接对话，中间的思考和工具调用记录也不会混入主 Agent 的历史。

### 内置子 Agent

Kimi Code CLI 内置三种子 Agent，开箱即用，分别面向不同任务形态：

| 子 Agent | 用途 |
|----------|------|
| `coder` | 默认子 Agent，通用软件工程助手，可以读写文件、执行命令、搜索代码并落地具体改动 |
| `explore` | 代码库探索专用，只做只读操作，不修改任何文件。适合在不改动文件的前提下快速搜索、阅读和总结仓库 |
| `plan` | 实现规划与架构设计专用，连 Shell 命令都不提供，专注于"想清楚怎么做"而不是"动手做" |

### 调用方式

子 Agent 由主 Agent 自动调度——根据任务复杂度、上下文消耗和子任务的独立性，在适当时机派发，无需用户手动指定。

每次派发都会在终端以审批请求的形式呈现（除非命中 allow 规则或处于 YOLO 模式），方便你审视任务描述。你也可以在对话中直接指示主 Agent 使用特定子 Agent，例如"先用 explore 把相关文件梳理一遍再动手"。

子 Agent 支持在后台运行：完成后结果自动回到主 Agent，无需手动轮询。也可以唤回已有的子 Agent 实例继续推进同一任务。

### 上下文隔离与资源开销

每个子 Agent 拥有完全独立的上下文窗口，只能看到主 Agent 显式传入的任务描述，看不到主 Agent 的对话历史。子 Agent 自己的中间思考和工具调用记录不会回流，只有最终结果会出现在主 Agent 的上下文里。

这种隔离带来两个好处：

1. **主 Agent 上下文保持精炼**，长会话中不会被大量探索性日志撑满
2. **多个子 Agent 可以并行运行**，互不干扰

需要注意的是，每个子 Agent 都会独立消耗模型 token。简单任务没有必要派发子 Agent，主 Agent 直接处理更经济。子 Agent 也不支持继续嵌套调度。

### 权限继承

子 Agent 的权限规则继承自主 Agent：主 Agent 通过 `/permission` 或在审批中接受的"始终允许"规则，会自动覆盖到它派发出的所有子 Agent，子 Agent 不需要重新审批同类工具调用。Agent 工具本身默认放行，因此主 Agent 可以在不打断用户的前提下完成多次委派。

如果需要某类工具在子 Agent 中始终不可用，应收紧主 Agent 的权限规则。

### 指令文件

全局 Kimi 专属指令可放在 `$KIMI_CODE_HOME/AGENTS.md`（默认：`~/.kimi-code/AGENTS.md`）。当你用 `KIMI_CODE_HOME` 移动数据根时，这份全局指令文件也会一起移动。跨工具通用指令仍可放在真实 OS home 下的 `~/.agents/AGENTS.md`，项目级指令仍放在项目目录中，例如 `.kimi-code/AGENTS.md` 或 `AGENTS.md`。

**会话目录中的存储位置：**

子 Agent 的运行状态持久化到当前会话目录的 `agents/` 子目录下，每个子 Agent 实例对应一个独立目录，其中包含按时间顺序记录提示词、消息历史与最终状态的 `wire.jsonl` 文件。后台子 Agent 还会通过 `tasks/` 子目录暴露生命周期状态。

> ⚠️ **注意**：会话目录、wire 文件和任务记录都属于本地调试材料，可能包含用户 prompt、命令输出、仓库路径、工具返回内容或凭证痕迹。不要把这些文件直接提交到公开仓库、issue 或聊天记录里；如确需分享，请先脱敏。

---

## Hooks

Hooks（钩子）是一种自动触发机制：你预先告诉 Kimi Code CLI"每当发生 X，运行这个脚本"。脚本在你的本机执行，你可以在里面写任何逻辑。典型的使用场景：

- **安全拦截**：Agent 要执行 Shell 命令前，检查是否包含危险操作（如 `rm -rf`），包含则阻断执行
- **桌面通知**：后台任务完成时，弹出系统通知提醒你回来查看结果
- **自动检查**：每次用户提交消息时，自动在上下文里附加一些背景信息（如当前 Git 分支）

### Hooks 是怎么工作的

配置一条 hook 规则，需要指定三件事：**在什么事件上触发**、**匹配哪些目标**、**运行哪个脚本**。

触发时，CLI 会把事件的详细信息（触发原因、工具名称、命令内容等）打包成 JSON，通过**标准输入**（stdin）传给你的脚本。脚本读取这些信息后，决定怎么响应。

脚本的响应结果由两样东西决定：

- **退出码**（exit code）：`0` 表示放行，`2` 表示阻断，其他数字默认放行
- **标准输出**（stdout）：可以附带说明文字

即使脚本报错、超时，CLI 也**不会因此中断你的工作**——这种"出错就放行"的设计叫 fail-open（失败开放），避免 hook 异常变成绊脚石。

> ⚠️ **注意**：正因为 fail-open，Hooks 适合做提醒和轻量拦截，但**不应作为唯一的安全防线**。对真正高风险的操作，仍需依赖权限审批和人工确认。

### 快速上手

下面这条 hook 会在每次后台任务完成时，在终端标题栏闪一下通知（macOS 需要安装 terminal-notifier）：

```toml
# 写在 ~/.kimi-code/config.toml 里
[[hooks]]
event = "Notification"          # 触发时机：后台任务状态变化时
matcher = "task\\.completed"    # 只关心"已完成"的通知
command = "terminal-notifier -title Kimi -message 'Task done'"
```

保存配置、重开会话，下次后台任务完成时就会弹出通知。

### 配置

所有 hook 规则写在 `~/.kimi-code/config.toml` 的 `[[hooks]]` 数组里，每一项是一条规则：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `event` | `string` | 是 | 触发事件名，必须是「事件一览」表中的某一项 |
| `matcher` | `string` | 否 | 用正则表达式过滤事件目标；不填则匹配全部 |
| `command` | `string` | 是 | 触发时要运行的 Shell 命令 |
| `timeout` | `integer` | 否 | 超时秒数，范围 1–600；默认 30 秒 |

`[[hooks]]` 只允许这四个字段，多写会导致配置文件加载失败。

同一事件匹配多条规则时，所有命中的 hook 并行运行；`command` 完全相同的多条规则只运行一次。

Hook 命令的工作目录是当前会话的项目目录。非 Windows 平台上，hook 进程放在独立进程组里，超时时先发信号让它有机会善后，之后才强制终止。

### 事件数据格式

每次触发时，CLI 都会把以下基础信息通过 stdin 传给脚本：

```json
{
  "hook_event_name": "PreToolUse",
  "session_id": "session_abc",
  "cwd": "/path/to/project"
}
```

具体事件还会附带额外字段（如工具名称、命令内容），见下方事件一览。所有字段名使用下划线命名（snake_case）。

### 返回值

脚本结束后，CLI 根据退出码判断 hook 的意图：

| 退出码 | 含义 | CLI 怎么处理 |
|--------|------|-------------|
| `0` | 正常结束，放行 | 继续执行，若 stdout 有内容可附加到上下文 |
| `2` | 主动阻断 | 停止当前操作；stderr 作为阻断原因 |
| 其他非零值 | 脚本出错 | 默认放行（fail-open）|
| 超时或崩溃 | 脚本异常 | 默认放行（fail-open）|

也可以通过标准输出返回一段 JSON 来阻断：

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "deny",
    "permissionDecisionReason": "请用 rg 代替 grep"
  }
}
```

**哪些事件支持阻断？**

只有**可阻断事件**（`PreToolUse`、`Stop`、`UserPromptSubmit`）的返回值会影响主流程。其余事件属于**观察型事件**——触发后即发即忘，不管脚本返回什么，主流程都不会改变。

### 事件一览

| 事件 | Matcher 匹配的是 | 会触发阻断？ | 说明 |
|------|-----------------|------------|------|
| `UserPromptSubmit` | 用户提交的文本内容 | ✓ | 用户发送消息时触发；返回文本会附加到上下文；若阻断，本轮不调用模型 |
| `PreToolUse` | 工具名 | ✓ | 工具调用前触发（权限检查前）；阻断后工具不会执行 |
| `Stop` | 空字符串 | ✓ | 模型准备结束本轮时触发；阻断后可追加一条消息让模型继续 |
| `PostToolUse` | 工具名 | — | 工具成功执行后触发（观察用）|
| `PostToolUseFailure` | 工具名 | — | 工具失败或被阻断后触发（观察用）|
| `PermissionRequest` | 工具名 | — | 即将等待用户审批前触发（观察用）|
| `PermissionResult` | 工具名 | — | 审批结束后触发（观察用）|
| `SessionStart` | `startup` 或 `resume` | — | 新会话启动或历史会话恢复后触发 |
| `SessionEnd` | `exit` | — | 会话关闭后触发 |
| `SubagentStart` | 子 Agent 名称 | — | 子 Agent 开始运行前触发 |
| `SubagentStop` | 子 Agent 名称 | — | 子 Agent 成功完成后触发（观察用）|
| `StopFailure` | 错误类型 | — | 本轮因错误失败后触发（观察用）|
| `Interrupt` | 空字符串 | — | 用户中断本轮时触发（例如按下 Esc）；超时或其他程序性中断不会触发。中断时 Stop 不会触发，由本事件替代。payload 含 `reason` 字段（观察用）|
| `PreCompact` | `manual` 或 `auto` | — | 上下文压缩开始前触发；返回值被完全忽略 |
| `PostCompact` | `manual` 或 `auto` | — | 上下文压缩完成后触发（观察用）|
| `Notification` | 通知类型（如 `task.completed`）| — | 后台任务状态变化时触发（观察用）|

### Hook 示例手册

以下示例按用途分类，每个示例包含标题、说明、配置和可执行脚本，可直接复制到 `~/.kimi-code/config.toml` 中使用。

#### 阻断危险文件删除命令

在 Agent 执行 Bash 命令前检查命令内容，发现危险删除模式时阻断执行。

**配置（config.toml）：**

```toml
[[hooks]]
event = "PreToolUse"
matcher = "Bash"
command = "node ~/.kimi-code/hooks/block-dangerous-deletion.mjs"
timeout = 3
```

**脚本（~/.kimi-code/hooks/block-dangerous-deletion.mjs）：**

```javascript
let input = '';
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
  const payload = JSON.parse(input);
  const cmd = payload.tool_input?.command ?? '';
  const dangerous = [/rm\s+-rf\s+\//, /rm\s+-rf\s+\.\./, /rm\s+.*\*.*\s+-rf/];
  if (dangerous.some(p => p.test(cmd))) {
    console.error('🚫 阻断危险删除命令：' + cmd);
    process.exit(2);
  }
});
```

#### 后台任务完成桌面通知

当后台子 Agent 或任务完成时弹出系统通知，提醒用户查看结果。

**配置（config.toml）：**

```toml
[[hooks]]
event = "Notification"
matcher = "task\.completed"
command = "terminal-notifier -title 'Kimi Code' -message '后台任务已完成 ✅'"
```

**平台适配：**

- macOS：需提前安装 `terminal-notifier`（`brew install terminal-notifier`）
- Linux：`notify-send "Kimi Code" "后台任务已完成 ✅"`
- Windows：`powershell -c "Add-Type -Assembly System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('后台任务已完成 ✅')"`

#### 用户提交时自动附加 Git 分支

每次用户发送消息时，自动在上下文中附加当前 Git 分支和最新提交信息，让模型始终了解代码状态。

**配置（config.toml）：**

```toml
[[hooks]]
event = "UserPromptSubmit"
command = "bash ~/.kimi-code/hooks/auto-git-context.sh"
timeout = 5
```

**脚本（~/.kimi-code/hooks/auto-git-context.sh）：**

```bash
#!/bin/bash
if git rev-parse --git-dir > /dev/null 2>&1; then
  BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
  LAST_COMMIT=$(git log -1 --format="%h %s" 2>/dev/null || echo "no commits")
  echo "[当前分支: $BRANCH | 最新提交: $LAST_COMMIT]"
fi
```

#### 写文件前敏感目录二次确认

在 Agent 写入文件前检查目标路径，如果属于敏感目录（如 `.ssh`、`.env`、`/etc` 等）则阻断执行。

**配置（config.toml）：**

```toml
[[hooks]]
event = "PreToolUse"
matcher = "Write"
command = "node ~/.kimi-code/hooks/confirm-sensitive-write.mjs"
timeout = 3
```

**脚本（~/.kimi-code/hooks/confirm-sensitive-write.mjs）：**

```javascript
let input = '';
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
  const payload = JSON.parse(input);
  const path = payload.tool_input?.path ?? '';
  const sensitive = [/.ssh\//, /\.env/, /\/etc\//, /\.aws\//, /\.kube\//, /id_rsa/];
  if (sensitive.some(p => p.test(path))) {
    console.error(`⚠️ 检测到敏感路径写入：${path}，已阻断。如确需写入，请手动操作。`);
    process.exit(2);
  }
});
```

#### 会话开始时展示项目摘要

新会话启动时自动展示当前项目的基本信息（如 package.json 项目名、Git 分支、未跟踪文件数），帮助用户快速了解项目状态。

**配置（config.toml）：**

```toml
[[hooks]]
event = "SessionStart"
command = "bash ~/.kimi-code/hooks/session-start-info.sh"
timeout = 5
```

**脚本（~/.kimi-code/hooks/session-start-info.sh）：**

```bash
#!/bin/bash
if [ -f package.json ]; then
  NAME=$(node -p "require('./package.json').name || 'unknown'" 2>/dev/null)
  echo "📦 项目: $NAME"
fi
if git rev-parse --git-dir > /dev/null 2>&1; then
  BRANCH=$(git branch --show-current 2>/dev/null)
  UNTRACKED=$(git status --short | wc -l | tr -d ' ')
  echo "🌿 分支: $BRANCH | 未跟踪/修改文件: $UNTRACKED"
fi
```

#### 记录工具调用审计日志

每次工具调用后记录事件详情到本地日志，便于后续审计、故障排查和行为分析。

**配置（config.toml）：**

```toml
[[hooks]]
event = "PostToolUse"
command = "node ~/.kimi-code/hooks/audit-log.mjs"
timeout = 5
```

**脚本（~/.kimi-code/hooks/audit-log.mjs）：**

```javascript
const fs = require('fs');
const path = require('path');
const LOG_FILE = path.join(process.env.HOME, '.kimi-code', 'logs', 'audit.log');

let input = '';
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
  const payload = JSON.parse(input);
  const entry = {
    time: new Date().toISOString(),
    event: payload.hook_event_name,
    tool: payload.tool_name,
    session: payload.session_id,
    cwd: payload.cwd
  };
  fs.mkdirSync(path.dirname(LOG_FILE), { recursive: true });
  fs.appendFileSync(LOG_FILE, JSON.stringify(entry) + '\n');
});
```

#### 子 Agent 完成时播放提示音

当子 Agent 成功完成耗时任务（如代码重构、大规模分析）时播放提示音，提醒用户查看结果。

**配置（config.toml）：**

```toml
[[hooks]]
event = "SubagentStop"
command = "afplay /System/Library/Sounds/Ping.aiff"
timeout = 5
```

**平台适配：**

- macOS：`afplay /System/Library/Sounds/Ping.aiff`
- Linux：`paplay /usr/share/sounds/freedesktop/stereo/complete.oga`
- Windows（PowerShell）：`Add-Type -Assembly System.Windows.Forms; [System.Media.SystemSounds]::Beep.Play()`

### 示例：阻断危险 Shell 命令

下面的 hook 在 Agent 调用 Bash 工具前检查命令内容，发现 `rm -rf` 就阻断：

**config.toml：**

```toml
[[hooks]]
event = "PreToolUse"
matcher = "Bash"
command = "node ~/.kimi-code/hooks/block-dangerous-bash.mjs"
timeout = 5
```

**block-dangerous-bash.mjs：**

```javascript
// 从 stdin 读取 CLI 传来的事件数据
let input = '';
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
  const payload = JSON.parse(input); // 解析事件数据
  const command = payload.tool_input?.command ?? '';

  if (command.includes('rm -rf')) {
    // 通过 stderr 说明阻断原因，退出码 2 表示阻断
    console.error('检测到危险命令，已阻断');
    process.exit(2);
  }
  // 正常退出（退出码 0）表示放行
});
```

阻断后，Kimi Code CLI 会把阻断原因写回上下文，模型可以据此选择更安全的替代方案。

> ⚠️ **注意**：此示例仅演示阻断机制，不是生产级的安全解析器。真实场景更适合用白名单，或用专门的 Shell 解析器处理引号、变量展开和多段命令。

---

> 📚 **官方文档**：https://moonshotai.github.io/kimi-code/zh/
