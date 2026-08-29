# 02｜Copilot 自定义能力：Custom Agents、Agent Skills 与 Hooks（精简版）

- [前置条件](#前置条件)
- [基本使用](#基本使用)
  - [1、自定义 Agent（Custom Agents）](#1自定义-agentcustom-agents)
    - [概述：它解决什么问题](#概述它解决什么问题)
    - [创建与存放位置](#创建与存放位置)
    - [文件格式（.agent.md）](#文件格式agentmd)
    - [Handoffs：把多步工作流串起来](#handoffs把多步工作流串起来)
    - [管理与排错](#管理与排错)
    - [完整示例（.agent.md，覆盖主要配置项）](#agent-example)
  - [2、Agent Skills（技能库）](#2agent-skills技能库)
    - [概述：Skills vs 自定义说明](#概述skills-vs-自定义说明)
    - [创建与存放位置](#创建与存放位置-1)
    - [SKILL.md 格式](#skillmd-格式)
    - [如何加载：渐进式加载（省上下文）](#如何加载渐进式加载省上下文)
    - [共享技能与安全建议](#共享技能与安全建议)
    - [完整示例（Skill 目录 + SKILL.md，覆盖主要配置项）](#skill-example)
  - [3、Agent Hooks（钩子，Preview）](#3agent-hooks钩子preview)
    - [概述：为什么需要 Hooks](#概述为什么需要-hooks)
    - [生命周期事件（8 个）](#生命周期事件8-个)
    - [配置文件位置与优先级](#配置文件位置与优先级)
    - [配置格式（JSON）](#配置格式json)
    - [输入 / 输出与退出码](#输入--输出与退出码)
    - [常见用法：拦截、自动化、注入上下文](#常见用法拦截自动化注入上下文)
    - [排错与注意事项](#排错与注意事项)
    - [完整示例（.github/hooks/*.json，覆盖主要配置项）](#hooks-example)
- [关键设置与命令速查](#关键设置与命令速查)

---

## 前置条件
1. 已安装并启用 **GitHub Copilot** 与 **GitHub Copilot Chat**。
2. VS Code 版本建议：
   - **Custom Agents**：文档标注从 **1.106** 起可用。
   - **Hooks**：文档标注为 **Preview**（示例版本 **1.109.3**），后续可能变更。
3. 团队/企业环境可能会通过策略禁用 Hooks 等能力；若发现相关菜单/命令不可用，优先检查企业策略。

## 基本使用

### 1、自定义 Agent（Custom Agents）

#### 概述：它解决什么问题
Custom Agents 的核心价值是：**把“指令 + 工具选择 + 模型偏好”打包成一个可切换的工作角色**。

你可以把它理解为：给 Copilot Chat 配置多套“工作模式”，例如：
- 规划（只读工具 + 输出计划）
- 实施（允许编辑/终端）
- 代码审查（偏安全/质量检查）

这样做的好处：
- **减少手动切换**：不用每次都重新勾选工具、重复贴规则。
- **更可控**：不同任务只暴露必要工具，降低误操作。
- **可复用**：同一套 agent 可用于本地 agent / 后台 agent / 云端 agent（取决于你启用的形态）。

#### 创建与存放位置
Custom Agent 本质是一个 Markdown 定义文件：

- 工作区共享（推荐团队用）：`.github/agents/*.agent.md`
- 用户级复用（跨项目）：放到 **VS Code 当前 Profile** 的自定义 agents 目录
- 兼容格式：`.claude/agents/*.md`（Claude sub-agents 格式；VS Code 会做映射）

常用入口：
- Chat 输入框：`/agents` 打开配置界面
- 命令面板：`Chat: New Custom Agent`

补充：可以用 `chat.agentFilesLocations` 配置额外扫描目录（用于把 agents 集中放到某个共享路径）。

#### 文件格式（.agent.md）
`.agent.md` 由两部分组成：

1）**YAML Frontmatter（可选）**：描述 agent 的元信息与运行约束。常用字段：
- `name`：agent 名称（不写则用文件名）
- `description`：Chat 输入框占位描述
- `argument-hint`：提示用户需要补充什么参数
- `tools`：允许使用的工具/工具集（可包含 MCP 工具；要包含某个 MCP server 的全部工具可用 `<server>/*`）
- `agents`：允许作为 subagent 调用的 agent 名单（如果你使用 subagent，别忘了把 agent 工具也放进 `tools`）
- `model`：指定单个模型或一个优先级列表
- `user-invokable`：是否显示在 agents 下拉列表（默认 true）
- `disable-model-invocation`：禁止被其他 agent 作为 subagent 调用

2）**正文（Markdown）**：真正的“行为定义”。当切换到该 agent 时，这段内容会被自动前置到你的对话请求中。

可复用写法：在正文用 Markdown 链接引用其他说明文件（例如 instructions/prompt 文件），避免重复维护。

#### Handoffs：把多步工作流串起来
Handoffs 用来把一个复杂任务拆成多个可控步骤，并在回答结束后提供“下一步按钮”跳转到另一个 agent。

典型用法：
- Planning → Implementation（先出计划，再开始动代码）
- Implementation → Review（做完后交给审查 agent）

示例（简化版）：
```md
---
description: 生成实施计划
tools: ['search', 'fetch']
handoffs:
  - label: 开始实现
    agent: implementation
    prompt: 基于上面的计划开始实现。
    send: false
    model: GPT-5.2 (copilot)
---

# 规划规则
- 输出可执行的分步计划
- 标注风险与验证方式
```

说明：`send: true` 会在切换后自动发送预填 prompt；默认 `false` 更适合“先让人看一眼再执行”。

#### 管理与排错
- 显示/隐藏：在 Configure Custom Agents 列表里用“眼睛”图标控制。
- 移除：删除对应 `.agent.md` 文件，或在列表里使用删除。
- 兼容迁移：旧的 `.chatmode.md` 需要改名为 `.agent.md`。
- 工具优先级（决定最终可用工具集合）：
  1. prompt file 里声明的 tools
  2. prompt file 引用的 custom agent 的 tools
  3. 当前选中 agent 的默认 tools
- 诊断：Chat 视图右键 → `Diagnostics` 可查看加载到的 agents/prompt/instructions/skills 以及错误信息。

<a id="agent-example"></a>
#### 完整示例（.agent.md，覆盖主要配置项）
下面示例尽量覆盖 Custom Agent frontmatter 的主要配置项（含 handoffs / tools / subagents / model 等）。你可以把它保存为：`.github/agents/planner.agent.md`。

```md
---
# 展示在 Chat 输入框里的占位提示
description: 生成可执行的实施计划（含风险与验证）

# Agent 显示名；不填会用文件名
name: Planner

# 可选：提示用户该怎么提问
argument-hint: "[目标] [约束] [验收标准]"

# 可用工具（可填工具名或工具集名；工具不可用时会被忽略）
# 可包含 MCP 工具；要包含某个 MCP server 的全部工具可用 <server-name>/*
tools:
  - search
  - fetch
  - todos
  # - upstash/context7/*

# 允许作为 subagent 调用的 agent 列表：'*' 允许所有；[] 禁用 subagent
# 注意：若你要启用 subagent，需确保 agent 工具也在 tools 列表中（由 VS Code 工具系统提供）
agents:
  - "*"

# 指定模型：可以是字符串，也可以是按优先级排列的数组
model:
  - GPT-5.2 (copilot)
  - GPT-5 (copilot)

# 是否出现在 Agents 下拉列表中（默认 true）
user-invokable: true

# 是否禁止被其他 agent 作为 subagent 调用（默认 false）
disable-model-invocation: false

# 目标环境：文档给出的可选值包含 vscode / github-copilot
target: vscode

# 仅在 target: github-copilot 场景下使用：声明要加载的 MCP server 配置
# mcp-servers:
#   - "${workspaceFolder}/.vscode/mcp.json"

# Handoffs：回答完成后提供“下一步按钮”跳转到另一个 agent
handoffs:
  - label: 开始实现
    agent: implementation
    prompt: "基于上面的计划开始实现，并按验收标准自测。"
    send: false
    model: GPT-5.2 (copilot)
  - label: 安全审查
    agent: security-review
    prompt: "请对刚完成的变更进行安全与质量审查，并给出修改建议。"
    send: false

# 旧字段 infer 已在文档中标注为 Deprecated：建议不要再使用
# infer: true
---

# Planner Agent 规则

## 输出格式
- 先给结论（可做/不可做 + 关键假设）
- 再给分步计划（每步含：产物、命令/文件、验证方式）
- 最后列风险与回滚点

## 约束
- 默认只做只读分析；如果需要改代码，先说明会改哪些文件
```

---

### 2、Agent Skills（技能库）

#### 概述：Skills vs 自定义说明
Skills 的定位是：**把“可复用能力/工作流”做成一个文件夹（指令 + 脚本 + 示例 + 资源）**，并遵循开放标准（agentskills.io），强调跨工具可移植。

对比自定义说明（instructions）：
- instructions 更像“项目规范/编码准则”，内容通常只有规则文本；可按 glob 常驻生效。
- skills 更像“可被按需加载的能力模块”，可以携带脚本和样例，且采用“渐进式加载”节省上下文。

适合用 Skills 的场景：测试、排障、部署、项目特定的操作流程模板等。

#### 创建与存放位置
Skill 是一个目录，目录内必须包含 `SKILL.md`：

- 项目级（推荐团队共享）：`.github/skills/<skill-name>/SKILL.md`
- 个人级（跨项目）：用户目录下的 skills 路径（VS Code 支持多种约定位置）

可通过 `chat.agentSkillsLocations` 增加扫描目录。

入口：
- Chat 输入框：`/skills` 打开技能管理
- Chat 输入框：输入 `/`，在列表里看到 skill（和 prompt files 并列）

#### SKILL.md 格式
`SKILL.md` 是 Markdown + YAML Frontmatter（头部必填）：

```md
---
name: webapp-testing
description: 说明这个 skill 做什么、何时用
argument-hint: (可选) 提示需要的参数
user-invokable: true|false
disable-model-invocation: true|false
---

# Skill Instructions
- 什么时候用
- 分步怎么做
- 输入输出示例
- 引用目录里的脚本/示例
```

关键约束：
- `name` 必须是小写 + 连字符，且 **必须与目录名一致**（否则不会被加载）。

#### 如何加载：渐进式加载（省上下文）
Skills 的加载是分层的（progressive disclosure）：
1. **发现层**：Copilot 只读取每个 skill 的 `name/description`（很轻量）
2. **指令层**：当请求与 skill 匹配时，加载 `SKILL.md` 正文
3. **资源层**：只有在需要时才访问 skill 目录里的脚本/示例文件

这意味着你可以安装很多 skills，但真正占用上下文的只有当前任务相关部分。

#### 共享技能与安全建议
- 共享：把 skill 目录复制到 `.github/skills/` 并提交即可团队共享。
- 引用第三方 skills：建议“先审计再使用”，尤其是包含脚本的技能。
- 终端/脚本执行：建议结合 VS Code 的工具审批与自动审批白名单机制，避免不受控执行。
- 扩展贡献 skills：扩展可以通过 `package.json` 的 `chatSkills` contribution point 注册 skill（指向 `SKILL.md`）。

<a id="skill-example"></a>
#### 完整示例（Skill 目录 + SKILL.md，覆盖主要配置项）
Skill 是“一个目录 + 一个 SKILL.md”。下面示例基本覆盖 `SKILL.md` 的主要 frontmatter 配置项，并展示如何引用同目录下的脚本/示例文件。

目录结构示例：
```text
.github/
  skills/
    webapp-testing/
      SKILL.md
      scripts/
        run-tests.ps1
      examples/
        login.spec.md
```

`SKILL.md` 示例：
```md
---
# 必填：必须与父目录名一致（这里的目录名是 webapp-testing）
name: webapp-testing

# 必填：要写清“做什么 + 什么时候用”，帮助 Copilot 决定是否自动加载
description: |
  用于 Web 应用测试：给出测试策略、运行命令、最小可复现实例与常见失败排查。
  适用于：新增/修改页面功能后需要回归；或 CI 测试失败需要定位。

# 可选：作为 /webapp-testing slash command 时的参数提示
argument-hint: "[页面/模块] [期望行为] [已有测试框架]"

# 可选：是否显示在 / 菜单里（默认 true）
user-invokable: true

# 可选：是否禁止模型自动加载该 skill（默认 false）
# 设为 true 后只能手动用 /webapp-testing 调用
disable-model-invocation: false
---

# Webapp Testing Skill

## 什么时候用
- 改动 UI/交互/接口后需要回归测试
- PR/CI 测试失败，需要快速定位失败面与复现路径

## 标准流程
1. 明确范围：受影响页面、关键路径、边界条件
2. 优先跑最小测试集：相关 spec / 相关目录
3. 若失败：先本地复现，再收敛到最小复现用例

## 运行命令（示例）
- Windows PowerShell：参考 [scripts/run-tests.ps1](./scripts/run-tests.ps1)

## 最小复现实例
- 参考示例用例：[examples/login.spec.md](./examples/login.spec.md)
```

---

### 3、Agent Hooks（钩子，Preview）

#### 概述：为什么需要 Hooks
Hooks 是一种 **确定性、代码驱动的自动化机制**：在 agent 会话的关键生命周期点执行你指定的命令。

它和 instructions/prompt 的区别在于：
- instructions/prompt 只是“引导模型怎么做”，并不保证结果。
- hooks 是“执行你写的命令”，可以 **强制阻止**、**自动修复**、**写审计日志**、**注入上下文**，结果更可控。

典型用途：
- 安全：拦截危险操作（例如破坏性命令）
- 质量：编辑后自动 format/lint/test
- 合规：记录工具调用、命令执行、文件变更
- 审批：对敏感工具强制 `ask` 或 `deny`

#### 生命周期事件（8 个）
VS Code 支持 8 个 hook 事件（在一次 agent 会话中按时机触发）：
- `SessionStart`：会话开始
- `UserPromptSubmit`：用户提交 prompt
- `PreToolUse`：调用任意工具前
- `PostToolUse`：工具成功执行后
- `PreCompact`：上下文将被压缩前
- `SubagentStart`：启动 subagent
- `SubagentStop`：subagent 结束
- `Stop`：会话结束

#### 配置文件位置与优先级
VS Code 会在以下位置查找 hook 配置（workspace 优先于 user）：
- Workspace：`.github/hooks/*.json`（推荐：可提交共享）
- Workspace：`.claude/settings.local.json`（本地，不提交）
- Workspace：`.claude/settings.json`
- User：`~/.claude/settings.json`

同一事件类型若 workspace 与 user 都有配置，workspace 生效优先。

#### 配置格式（JSON）
hook 配置文件是 JSON，包含 `hooks` 对象，每个事件对应一个数组：

```json
{
  "hooks": {
    "PreToolUse": [
      { "type": "command", "command": "./scripts/validate-tool.sh", "timeout": 15 }
    ],
    "PostToolUse": [
      { "type": "command", "command": "npx prettier --write \"$TOOL_INPUT_FILE_PATH\"" }
    ]
  }
}
```

命令字段要点：
- 必填：`type: "command"`、`command`
- 可选：`windows`/`linux`/`osx`（按 OS 覆盖命令）、`cwd`、`env`、`timeout`（秒，默认 30）

注意：远程开发（SSH/容器/WSL）时，“OS 选择”以扩展宿主（extension host）平台为准，可能与你本机不同。

#### 输入 / 输出与退出码
Hooks 与 VS Code 的通信方式：
- stdin：输入 JSON（包含时间、cwd、sessionId、事件名、transcript 路径等）
- stdout：可输出 JSON 影响后续行为（例如继续/阻止、提示信息）

通用输出字段示例：
```json
{ "continue": true, "stopReason": "...", "systemMessage": "..." }
```

退出码语义：
- `0`：成功，stdout 会被解析为 JSON
- `2`：阻断错误，停止处理并把错误展示给模型
- 其他：警告，继续处理

#### 常见用法：拦截、自动化、注入上下文
1）`PreToolUse`：工具调用前拦截/审批/改参数
- 可设置 `permissionDecision: allow | ask | deny`
- 可用 `updatedInput` 修改工具输入（必须符合工具 schema；不符合会被忽略）
- 多个 hook 同时生效时：**最严格**（deny > ask > allow）优先

2）`PostToolUse`：工具完成后的自动化
- 常见：格式化、跑 lint/test、记录结果
- 可注入 `additionalContext` 让后续对话“带着执行结果继续”

3）`SessionStart`：开局注入工程上下文
- 常见：项目名/版本/分支/运行时版本等，让 agent 更快进入状态

4）`Stop`：阻止会话结束（例如强制跑测试）
- 注意：阻止 stop 会让 agent 继续运行并消耗额外请求；要检查 `stop_hook_active`，避免无限循环。

#### 排错与注意事项
- 快速配置：`/hooks` 会打开交互式 UI，选事件→选/新建配置文件→定位到 command 字段。
- 诊断：Chat 视图右键 → `Diagnostics` 查看 hooks 是否被加载、是否校验失败。
- 输出日志：Output 面板选择 `GitHub Copilot Chat Hooks` 查看 hook 的 stdout/stderr。
- 安全建议：Hooks 会用 VS Code 同等权限执行命令；不要启用来源不明的 hook。
- 防自修改风险：如果 agent 能编辑 hook 脚本，就可能“边改脚本边执行”。可用 `chat.tools.edits.autoApprove` 等审批设置，限制对 hook 脚本的自动编辑/执行。

<a id="hooks-example"></a>
#### 完整示例（.github/hooks/*.json，覆盖主要配置项）
下面示例展示一个工作区 hooks 配置文件，基本覆盖 hook command 的主要配置项：`type`、`command`、`windows/linux/osx`、`cwd`、`env`、`timeout`，并把 8 个生命周期事件都写全。

保存路径示例：`.github/hooks/agent-guardrails.json`

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "./scripts/hooks/session-start.sh",
        "windows": "powershell -File scripts\\hooks\\session-start.ps1",
        "linux": "./scripts/hooks/session-start.sh",
        "osx": "./scripts/hooks/session-start.sh",
        "cwd": ".",
        "env": {"HOOK_LEVEL": "info"},
        "timeout": 10
      }
    ],
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "./scripts/hooks/audit-prompt.sh",
        "windows": "powershell -File scripts\\hooks\\audit-prompt.ps1",
        "linux": "./scripts/hooks/audit-prompt.sh",
        "osx": "./scripts/hooks/audit-prompt.sh",
        "cwd": ".",
        "env": {"AUDIT": "true"},
        "timeout": 10
      }
    ],
    "PreToolUse": [
      {
        "type": "command",
        "command": "./scripts/hooks/pre-tool-use.sh",
        "windows": "powershell -File scripts\\hooks\\pre-tool-use.ps1",
        "linux": "./scripts/hooks/pre-tool-use.sh",
        "osx": "./scripts/hooks/pre-tool-use.sh",
        "cwd": ".",
        "env": {"POLICY_MODE": "strict"},
        "timeout": 15
      }
    ],
    "PostToolUse": [
      {
        "type": "command",
        "command": "./scripts/hooks/post-tool-use.sh",
        "windows": "powershell -File scripts\\hooks\\post-tool-use.ps1",
        "linux": "./scripts/hooks/post-tool-use.sh",
        "osx": "./scripts/hooks/post-tool-use.sh",
        "cwd": ".",
        "env": {"AUTO_FORMAT": "true"},
        "timeout": 30
      }
    ],
    "PreCompact": [
      {
        "type": "command",
        "command": "./scripts/hooks/pre-compact.sh",
        "windows": "powershell -File scripts\\hooks\\pre-compact.ps1",
        "linux": "./scripts/hooks/pre-compact.sh",
        "osx": "./scripts/hooks/pre-compact.sh",
        "cwd": ".",
        "env": {"EXPORT_CONTEXT": "true"},
        "timeout": 10
      }
    ],
    "SubagentStart": [
      {
        "type": "command",
        "command": "./scripts/hooks/subagent-start.sh",
        "windows": "powershell -File scripts\\hooks\\subagent-start.ps1",
        "linux": "./scripts/hooks/subagent-start.sh",
        "osx": "./scripts/hooks/subagent-start.sh",
        "cwd": ".",
        "env": {"TRACE_SUBAGENTS": "true"},
        "timeout": 10
      }
    ],
    "SubagentStop": [
      {
        "type": "command",
        "command": "./scripts/hooks/subagent-stop.sh",
        "windows": "powershell -File scripts\\hooks\\subagent-stop.ps1",
        "linux": "./scripts/hooks/subagent-stop.sh",
        "osx": "./scripts/hooks/subagent-stop.sh",
        "cwd": ".",
        "env": {"TRACE_SUBAGENTS": "true"},
        "timeout": 10
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "./scripts/hooks/stop.sh",
        "windows": "powershell -File scripts\\hooks\\stop.ps1",
        "linux": "./scripts/hooks/stop.sh",
        "osx": "./scripts/hooks/stop.sh",
        "cwd": ".",
        "env": {"REQUIRE_TESTS": "false"},
        "timeout": 10
      }
    ]
  }
}
```

---

## 关键设置与命令速查
- Agents
  - 斜杠命令：`/agents`
  - 命令面板：`Chat: New Custom Agent`
  - 设置：`chat.agentFilesLocations`
  - 团队共享：提交 `.github/agents/*.agent.md`
  - 组织级发现：`github.copilot.chat.organizationCustomAgents.enabled`
- Skills
  - 斜杠命令：`/skills`（管理）与 `/`（调用）
  - 设置：`chat.agentSkillsLocations`
  - 团队共享：提交 `.github/skills/<name>/SKILL.md`
- Hooks
  - 斜杠命令：`/hooks`
  - 工作区目录：`.github/hooks/*.json`
  - 排错：Chat 右键 `Diagnostics`；Output 面板 `GitHub Copilot Chat Hooks`
