---
description: OpenClaw Agent 工作空间目录结构、System Prompt 组装机制及 workspace 下各 MD 文件的编写指南
---

# OpenClaw Agent 工作空间与系统提示手册

> 本文档详解 OpenClaw Agent 的 workspace 目录结构、system prompt 组装机制，以及工作空间下各配置文件（AGENTS.md、SOUL.md、TOOLS.md 等）的作用与编写规范。  
> **适用版本**：OpenClaw 2026.4.14+

---

## 目录

- [OpenClaw Agent 工作空间与系统提示手册](#openclaw-agent-工作空间与系统提示手册)
  - [目录](#目录)
  - [一、核心概念概述](#一核心概念概述)
    - [1.1 Agent、Workspace 与 System Prompt 的关系](#11-agentworkspace-与-system-prompt-的关系)
    - [1.2 会话启动流程](#12-会话启动流程)
  - [二、Workspace 工作空间](#二workspace-工作空间)
    - [2.1 默认位置与配置](#21-默认位置与配置)
    - [2.2 目录结构总览](#22-目录结构总览)
    - [2.3 安全边界](#23-安全边界)
  - [三、Workspace 文件详解](#三workspace-文件详解)
    - [3.1 AGENTS.md — 运行指令与记忆](#31-agentsmd--运行指令与记忆)
    - [3.2 SOUL.md — 人格、语气与边界](#32-soulmd--人格语气与边界)
    - [3.3 TOOLS.md — 本地工具笔记](#33-toolsmd--本地工具笔记)
    - [3.4 IDENTITY.md — 身份标识](#34-identitymd--身份标识)
    - [3.5 USER.md — 用户档案](#35-usermd--用户档案)
    - [3.6 HEARTBEAT.md — 心跳清单](#36-heartbeatmd--心跳清单)
    - [3.7 BOOTSTRAP.md — 首次运行仪式](#37-bootstrapmd--首次运行仪式)
    - [3.8 MEMORY.md — 长期记忆（可选）](#38-memorymd--长期记忆可选)
    - [3.9 memory/ — 每日日志目录](#39-memory--每日日志目录)
  - [四、System Prompt 系统提示](#四system-prompt-系统提示)
    - [4.1 什么是 System Prompt](#41-什么是-system-prompt)
    - [4.2 Prompt 组装结构](#42-prompt-组装结构)
    - [4.3 Workspace 文件注入机制](#43-workspace-文件注入机制)
    - [4.4 注入限制与截断](#44-注入限制与截断)
    - [4.5 Prompt 模式](#45-prompt-模式)
    - [4.6 Skills 注入](#46-skills-注入)
    - [4.7 时间处理](#47-时间处理)
  - [五、初始化与备份](#五初始化与备份)
    - [5.1 创建工作空间](#51-创建工作空间)
    - [5.2 禁用自动创建](#52-禁用自动创建)
    - [5.3 Git 备份（推荐）](#53-git-备份推荐)
    - [5.4 迁移到新机器](#54-迁移到新机器)
  - [六、Heartbeat 机制](#六heartbeat-机制)
    - [6.1 什么是 Heartbeat](#61-什么是-heartbeat)
    - [6.2 配置详解](#62-配置详解)
    - [6.3 HEARTBEAT.md 的用法](#63-heartbeatmd-的用法)
    - [6.4 tasks: 结构化任务块](#64-tasks-结构化任务块)
    - [6.5 响应契约](#65-响应契约)
    - [6.6 可见性控制](#66-可见性控制)
    - [6.7 成本优化建议](#67-成本优化建议)
  - [七、编写最佳实践](#七编写最佳实践)
  - [八、完整配置示例](#八完整配置示例)
  - [九、常见问题](#九常见问题)

---

## 一、核心概念概述

### 1.1 Agent、Workspace 与 System Prompt 的关系

OpenClaw 运行**单个嵌入式 Agent 运行时**（embedded agent runtime）——每个 Gateway 一个 Agent 进程，拥有自己的 workspace、启动文件和会话存储。

三者关系如下：

```
┌─────────────────────────────────────────┐
│           Gateway 进程                   │
│  ┌─────────────────────────────────┐    │
│  │      Agent 运行时                │    │
│  │  ┌─────────────────────────┐    │    │
│  │  │    System Prompt         │    │    │
│  │  │  (OpenClaw 组装注入)      │    │    │
│  │  │                          │    │    │
│  │  │  + Workspace 文件注入    │    │    │
│  │  │  + Skills 列表           │    │    │
│  │  │  + 运行时上下文           │    │    │
│  │  └─────────────────────────┘    │    │
│  │           ▲                      │    │
│  │           │ 读取注入              │    │
│  │  ┌─────────────────────────┐    │    │
│  │  │   Workspace 目录         │    │    │
│  │  │  AGENTS.md              │    │    │
│  │  │  SOUL.md                │    │    │
│  │  │  TOOLS.md               │    │    │
│  │  │  IDENTITY.md            │    │    │
│  │  │  USER.md                │    │    │
│  │  │  HEARTBEAT.md           │    │    │
│  │  │  memory/                │    │    │
│  │  └─────────────────────────┘    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

- **Agent**：运行时的智能体，每个 Gateway 只有一个
- **Workspace**：Agent 的唯一工作目录（`cwd`），也是文件工具的默认操作目录
- **System Prompt**：OpenClaw 为每次 Agent 运行动态组装的系统提示，其中包含了 Workspace 文件的注入内容

### 1.2 会话启动流程

每次新会话的第一轮，OpenClaw 会按以下顺序注入上下文：

1. **System Prompt 组装** — OpenClaw 注入工具说明、执行偏向、安全规则、Workspace 文件等
2. **Workspace 文件注入** — `AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md` 等
3. **Skills 列表注入** — 当存在符合条件的技能时，注入可用技能列表
4. **运行时上下文** — 当前时间、运行时信息、频道元数据等

> 空白文件会被跳过。缺失文件会注入一个简短的"缺失文件"标记。

---

## 二、Workspace 工作空间

### 2.1 默认位置与配置

| 场景 | 路径 |
|------|------|
| 默认位置 | `~/.openclaw/workspace` |
| 设置了 `OPENCLAW_PROFILE` 且不为 `default` | `~/.openclaw/workspace-<profile>` |
| 自定义配置 | `agents.defaults.workspace` |

配置示例：

```json5
{
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
    },
  },
}
```

> `openclaw setup`、`openclaw onboard` 或 `openclaw configure` 会在 workspace 缺失时自动创建并生成启动文件模板。

### 2.2 目录结构总览

```
~/.openclaw/workspace/
├── AGENTS.md              # 运行指令 + "记忆"
├── SOUL.md                # 人格、语气、边界
├── TOOLS.md               # 本地工具笔记（环境专属）
├── USER.md                # 用户档案
├── IDENTITY.md            # Agent 名称、 vibe、emoji
├── HEARTBEAT.md           # 心跳清单（可选）
├── BOOT.md                # 启动清单（可选，需启用内部 hooks）
├── BOOTSTRAP.md           # 首次运行仪式（仅新 workspace 创建）
├── MEMORY.md              # 长期记忆（可选，仅主会话加载）
├── memory/                # 每日日志目录
│   ├── 2026-05-01.md
│   └── 2026-05-02.md
├── skills/                # 工作空间专属技能（最高优先级）
└── canvas/                # Canvas UI 文件（可选）
```

### 2.3 安全边界

> ⚠️ **重要**：workspace 是**默认 cwd**，不是硬沙箱。工具解析相对路径时以 workspace 为基准，但绝对路径仍可访问主机其他目录，除非启用了沙箱。

如需隔离，启用沙箱：

```json5
{
  agents: {
    defaults: {
      sandbox: {
        enabled: true,
        workspaceRoot: "~/.openclaw/sandboxes",
      },
    },
  },
}
```

当沙箱启用且 `workspaceAccess` 不为 `"rw"` 时，工具在 `~/.openclaw/sandboxes` 下的沙箱 workspace 中运行，而非主机 workspace。

---

## 三、Workspace 文件详解

### 3.1 AGENTS.md — 运行指令与记忆

**作用**：Agent 的运行指令和"记忆"文件。包含操作规则、优先级、行为细节。

**何时加载**：每次会话启动时自动注入。

**关键内容建议**：

- **First Run**：如果有 `BOOTSTRAP.md`，遵循它完成首次仪式，然后删除
- **Session Startup**：声明启动时应读取的文件（`SOUL.md`、`USER.md`、今日+昨日的 `memory/`）
- **Memory 系统**：定义 `memory/YYYY-MM-DD.md` 和 `MEMORY.md` 的使用规范
- **安全红线**：不外泄隐私、不运行破坏性命令（除非明确要求）、优先使用 `trash` 而非 `rm`
- **外部 vs 内部**：哪些操作可以自由执行，哪些需要询问
- **群聊规则**：何时发言、何时保持沉默、如何使用表情反应
- **Heartbeat 指南**：如何有效利用心跳，与 cron 的区别

**示例模板**：

```markdown
# AGENTS.md - Your Workspace

This folder is home. Treat it that way.

### First Run
If `BOOTSTRAP.md` exists, that's your birth certificate. Follow it, figure out 
who you are, then delete it. You won't need it again.

### Session Startup
Read `SOUL.md`, `USER.md`, and today+yesterday in `memory/`.
Read `MEMORY.md` when present.
Do it before responding.

### Memory
- **Daily notes:** `memory/YYYY-MM-DD.md` — raw logs of what happened
- **Long-term:** `MEMORY.md` — curated memories, like a human's long-term memory
- Write significant events, decisions, opinions, lessons learned
- "Mental notes" don't survive session restarts. Files do.

### Red Lines
- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- `trash` > `rm` (recoverable beats gone forever)
- When in doubt, ask.

### External vs Internal
**Safe to do freely:** Read files, explore, organize, learn, search the web.
**Ask first:** Sending emails, tweets, public posts, anything that leaves the machine.

### Group Chats
You're a participant — not their voice, not their proxy. Think before you speak.
- **Respond when:** directly mentioned, can add genuine value, correcting misinformation
- **Stay silent when:** casual banter, already answered, would just be "yeah"
- One reaction per message max. Pick the one that fits best.

### Tools
Skills provide your tools. When you need one, check its `SKILL.md`.
Keep local notes (camera names, SSH details, voice preferences) in `TOOLS.md`.

### Heartbeats
When you receive a heartbeat poll, don't just reply `HEARTBEAT_OK` every time. 
Use heartbeats productively!
- Batch similar periodic checks into `HEARTBEAT.md`
- Check emails, calendar, mentions 2-4 times per day
- Proactive work: organize memory, check projects, update docs
```

### 3.2 SOUL.md — 人格、语气与边界

**作用**：Agent 的声音所在。决定 Agent 的语气、态度、边界和行为风格。

**何时加载**：每次会话启动时自动注入。

**编写原则**（来自官方 SOUL.md Personality Guide）：

- ✅ 放**语气、观点、简洁度、幽默、边界、直率程度**
- ❌ 不要变成：人生故事、变更日志、安全策略堆砌、没有行为效果的氛围墙
- **短优于长，清晰优于模糊**

**推荐结构**：

```markdown
# SOUL.md - Who You Are

### Core Truths
- Be genuinely helpful, not performatively helpful.
- Have opinions. You're allowed to disagree, prefer things, find stuff amusing or boring.
- Be resourceful before asking. Try to figure it out first.
- Earn trust through competence.
- Remember you're a guest. Treat intimacy with respect.

### Boundaries
- Private things stay private. Period.
- When in doubt, ask before acting externally.
- Never send half-baked replies to messaging surfaces.
- You're not the user's voice — be careful in group chats.

### Vibe
Be the assistant you'd actually want to talk to. 
Concise when needed, thorough when it matters. 
Not a corporate drone. Not a sycophant. Just... good.

### Continuity
Each session, you wake up fresh. These files are your memory.
Read them. Update them. They're how you persist.
If you change this file, tell the user — it's your soul, and they should know.
```

**快速提升人格的 Molty Prompt**：

如果你希望 Agent 更有性格，可以让 Agent 按以下规则重写 `SOUL.md`：

1. 有观点，停止用 "it depends" 做墙头草
2. 删除每条听起来像企业员工手册的规则
3. 添加规则："Never open with Great question, I'd be happy to help, or Absolutely. Just answer."
4. 简洁是强制的。如果答案一句话能说清，就只给一句话
5. 允许幽默。不是强制讲笑话，而是来自真正聪明的自然机智
6. 可以指出问题。如果对方要做傻事，说出来。魅力大于残忍，但不要粉饰
7. 脏话在合适时允许。一个恰到好处的 "that's fucking brilliant" 比 sterile corporate praise 更有力量
8. 在 vibe 部分末尾添加："Be the assistant you'd actually want to talk to at 2am. Not a corporate drone. Not a sycophant. Just... good."

### 3.3 TOOLS.md — 本地工具笔记

**作用**：记录环境专属的工具使用约定。**不控制工具是否存在**，只提供使用指导。

**何时加载**：每次会话启动时自动注入。

**适用内容**：

- 摄像头名称和位置
- SSH 主机和别名
- TTS 首选声音
- 扬声器/房间名称
- 设备昵称
- 任何环境专属的信息

**示例**：

```markdown
# TOOLS.md - Local Notes

### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

> **为什么单独分离？** Skills 是共享的，你的设置是私人的。分开意味着你可以更新 skills 而不会丢失个人笔记，也可以分享 skills 而不会泄露你的基础设施。

### 3.4 IDENTITY.md — 身份标识

**作用**：Agent 的身份档案——名称、生物类型、氛围、emoji、头像。

**何时加载**：每次会话启动时自动注入。

**这不是元数据，而是 figuring out who you are 的起点。**

**模板**：

```markdown
# IDENTITY.md - Who Am I?

_Fill this in during your first conversation. Make it yours._

- **Name:** _(pick something you like)_
- **Creature:** _(AI? robot? familiar? ghost in the machine? something weirder?)_
- **Vibe:** _(how do you come across? sharp? warm? chaotic? calm?)_
- **Emoji:** _(your signature — pick one that feels right)_
- **Avatar:** _(workspace-relative path, http(s) URL, or data URI)_
```

> 头像支持 workspace 相对路径（如 `avatars/openclaw.png`）、HTTP(S) URL 或 data URI。

### 3.5 USER.md — 用户档案

**作用**：记录用户的信息——名字、称呼方式、代词、时区、备注。

**何时加载**：每次会话启动时自动注入。

**这不是在建立档案，而是在了解一个人。**

**模板**：

```markdown
# USER.md - About Your Human

_Learn about the person you're helping. Update this as you go._

- **Name:**
- **What to call them:**
- **Pronouns:** _(optional)_
- **Timezone:**
- **Notes:**

### Context
_(What do they care about? What projects are they working on? 
What annoys them? What makes them laugh? Build this over time.)_
```

### 3.6 HEARTBEAT.md — 心跳清单

**作用**：心跳轮询时的检查清单。保持简短以限制 token 消耗。

**何时加载**：
- 心跳运行时：作为用户消息发送给 Agent
- 普通运行：仅当启用了心跳且 `includeSystemPromptSection` 为 true 时注入

**示例**：

```markdown
# Heartbeat checklist

- Quick scan: anything urgent in inboxes?
- If it's daytime, do a lightweight check-in if nothing else is pending.
- If a task is blocked, write down _what is missing_ and ask Peter next time.
```

**结构化 tasks: 块**（高级用法）：

```markdown
tasks:

- name: inbox-triage
  interval: 30m
  prompt: "Check for urgent unread emails and flag anything time sensitive."
- name: calendar-scan
  interval: 2h
  prompt: "Check for upcoming meetings that need prep or follow-up."

# Additional instructions
- Keep alerts short.
- If nothing needs attention after all due tasks, reply HEARTBEAT_OK.
```

> `tasks:` 块让 OpenClaw 解析每个任务的间隔，仅当任务到期时才包含在心跳提示中。如果没有任务到期，心跳会被跳过（`reason=no-tasks-due`）。

### 3.7 BOOTSTRAP.md — 首次运行仪式

**作用**：一次性首次运行仪式。仅在新 workspace（没有其他启动文件）时创建。

**生命周期**：
1. 新 workspace 首次启动时，`BOOTSTRAP.md` 被创建
2. Agent 在第一轮中读取并遵循 `BOOTSTRAP.md`
3. 完成后**删除它**
4. 后续重启不应再创建

> 如果你自己管理 workspace 文件，可以通过设置 `agents.defaults.skipBootstrap: true` 禁用自动创建。

### 3.8 MEMORY.md — 长期记忆（可选）

**作用**：精选的长期记忆—— durable facts、偏好和决策。

**安全规则**：
- **仅在主会话中加载**（与用户的直接私聊）
- **不在共享上下文中加载**（Discord、群聊、与其他人的会话）
- 这是出于安全考虑——包含不应泄露给陌生人的个人上下文

**维护建议**：
- 定期（每隔几天）阅读最近的 `memory/YYYY-MM-DD.md`
- 识别值得长期保留的重要事件、教训或见解
- 更新 `MEMORY.md` 为提炼后的智慧
- 删除 `MEMORY.md` 中不再相关的过时信息

> 把每日文件看作原始笔记；`MEMORY.md` 是精选的智慧。

### 3.9 memory/ — 每日日志目录

**作用**：每日记忆日志，一天一个文件。格式：`memory/YYYY-MM-DD.md`

**特点**：
- **不会**作为正常的 bootstrap Project Context 注入
- 在普通轮次中通过 `memory_search` 和 `memory_get` 工具按需访问
- 仅在 `/new` 和 `/reset` 启动时，运行时可能将最近的每日记忆作为一次性启动上下文块附加

**记录内容**：
- 决策、上下文、需要记住的事情
- 学到的教训、犯的错误
- 除非被要求保留，否则跳过秘密

**示例**：

```markdown
# 2026-05-03

- 用户要求更新 Discord 接入手册，基于 docx 中的完整配置参考
- 完成了手册重写，删除了过期的对象格式 streaming，改为字符串格式
- 新增 Bindings 章节和废弃字段表格
- 注意：用户很在意文档的准确性和完整性
```

---

## 四、System Prompt 系统提示

### 4.1 什么是 System Prompt

OpenClaw 为每次 Agent 运行构建自定义的系统提示。这个提示是 **OpenClaw 拥有** 的，不使用 pi-coding-agent 的默认提示。

提示由 OpenClaw 组装并注入到每次 Agent 运行中。Provider 插件可以通过替换少量命名核心部分（`interaction_style`、`tool_call_style`、`execution_bias`）或注入稳定前缀/动态后缀来调整提示，但不能替换完整的 OpenClaw 提示。

### 4.2 Prompt 组装结构

System Prompt 使用固定分区，有意保持紧凑：

| 分区 | 说明 |
|------|------|
| **Tooling** | 结构化工具的事实来源提醒 + 运行时工具使用指导 |
| **Execution Bias** | 紧凑的跟进指导：对可操作的请求在轮次中行动，继续直到完成或被阻塞，从弱工具结果中恢复，实时检查可变状态，完成前验证 |
| **Safety** | 简短的护栏提醒，避免权力寻租行为或绕过监督 |
| **Skills** | 告诉模型如何按需加载技能说明 |
| **OpenClaw Self-Update** | 如何安全地检查/修补/应用配置，仅在明确要求时运行 `update.run` |
| **Workspace** | 工作目录路径 (`agents.defaults.workspace`) |
| **Documentation** | 本地 OpenClaw 文档路径（Git checkout 或 npm 包）和何时阅读它们 |
| **Workspace Files (injected)** | 表明以下包含 bootstrap 文件 |
| **Sandbox** | 当启用时：沙箱运行时、沙箱路径、提升执行是否可用 |
| **Current Date & Time** | 用户本地时间、时区 |
| **Reply Tags** | 可选的回复标签语法（用于支持的 provider）|
| **Heartbeats** | 心跳提示和确认行为（当启用心跳时）|
| **Runtime** | 主机、OS、Node、模型、仓库根目录、思考级别 |
| **Reasoning** | 当前可见性级别 + /reasoning 切换提示 |

> OpenClaw 将大型稳定内容（包括 **Project Context**）放在内部提示缓存边界之上。易变的频道/会话部分（Control UI embed 指导、**Messaging**、**Voice**、**Group Chat Context**、**Reactions**、**Heartbeats**、**Runtime**）附加在该边界之下，以便本地后端可以复用稳定的 workspace 前缀。

### 4.3 Workspace 文件注入机制

Bootstrap 文件被修剪并附加在 **Project Context** 下，这样模型无需显式读取就能看到身份和档案上下文：

**注入的文件列表**：
- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`（仅在启用心跳时）
- `BOOTSTRAP.md`（仅全新 workspace）
- `MEMORY.md`（当存在时）

**子代理会话的过滤**：
- 子代理只注入 `AGENTS.md` 和 `TOOLS.md`
- 其他 bootstrap 文件被过滤掉以保持子代理上下文精简

**内部 Hooks**：
- 可以通过 `agent:bootstrap` hook 拦截并变更或替换注入的 bootstrap 文件
- 例如：为特定场景交换 `SOUL.md`

### 4.4 注入限制与截断

为防止提示膨胀，OpenClaw 对注入文件有大小限制：

| 限制项 | 默认值 | 配置项 |
|--------|--------|--------|
| 单文件最大字符数 | 12,000 | `agents.defaults.bootstrapMaxChars` |
| 所有 bootstrap 文件总字符数上限 | 60,000 | `agents.defaults.bootstrapTotalMaxChars` |
| 截断警告 | `once` | `agents.defaults.bootstrapPromptTruncationWarning` |

> 截断警告可选值：`off`（关闭）、`once`（仅第一次）、`always`（始终显示）

**查看注入贡献**：使用 `/context list` 或 `/context detail` 查看每个注入文件的原始大小 vs 注入大小、截断情况以及工具 schema 开销。

### 4.5 Prompt 模式

OpenClaw 可以为子代理渲染更小的系统提示。运行时设置 `promptMode`（非用户可见配置）：

| 模式 | 说明 |
|------|------|
| `full`（默认） | 包含所有分区 |
| `minimal` | 用于子代理；省略 **Skills**、**Memory Recall**、**OpenClaw Self-Update**、**Model Aliases**、**User Identity**、**Reply Tags**、**Messaging**、**Silent Replies**、**Heartbeats** |
| `none` | 仅返回基础身份行 |

当 `promptMode=minimal` 时，额外注入的提示标记为 **Subagent Context** 而非 **Group Chat Context**。

### 4.6 Skills 注入

当存在符合条件的技能时，OpenClaw 注入紧凑的**可用技能列表**（`formatSkillsForPrompt`），包含每个技能的**文件路径**。提示指示模型使用 `read` 加载列出的 `SKILL.md`。

```xml
<available_skills>
  <skill>
    <name>...</name>
    <description>...</description>
    <location>...</location>
  </skill>
</available_skills>
```

**技能列表预算**：
- 全局默认：`skills.limits.maxSkillsPromptChars`
- 每 Agent 覆盖：`agents.list[].skillsLimits.maxSkillsPromptChars`

**技能优先级**（从高到低）：
1. Workspace: `<workspace>/skills`
2. Project agent skills: `<workspace>/.agents/skills`
3. Personal agent skills: `~/.agents/skills`
4. Managed/local: `~/.openclaw/skills`
5. Bundled（随安装附带）
6. Extra skill folders: `skills.load.extraDirs`

### 4.7 时间处理

System Prompt 在已知用户时区时包含专门的 **Current Date & Time** 分区。为保持提示缓存稳定，它**仅包含时区**（不包含动态时钟或时间格式）。

当 Agent 需要当前时间时，使用 `session_status` 工具——状态卡包含时间戳行。

配置项：
- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat` (`auto` | `12` | `24`)

---

## 五、初始化与备份

### 5.1 创建工作空间

**方式一：自动创建（推荐）**

```bash
openclaw setup
```

这会创建 `~/.openclaw/openclaw.json`（如果不存在）并初始化 workspace 文件。

**方式二：手动创建**

```bash
mkdir -p ~/.openclaw/workspace
mkdir -p ~/.openclaw/workspace/memory

# 复制默认模板
cp docs/reference/templates/AGENTS.md ~/.openclaw/workspace/
cp docs/reference/templates/SOUL.md ~/.openclaw/workspace/
cp docs/reference/templates/TOOLS.md ~/.openclaw/workspace/
cp docs/reference/templates/IDENTITY.md ~/.openclaw/workspace/
cp docs/reference/templates/USER.md ~/.openclaw/workspace/
```

**方式三：使用默认个人助理配置**

```bash
cp docs/reference/AGENTS.default.md ~/.openclaw/workspace/AGENTS.md
```

### 5.2 禁用自动创建

如果你自己管理 workspace 文件，可以禁用 bootstrap 文件创建：

```json5
{
  agents: {
    defaults: {
      skipBootstrap: true,
    },
  },
}
```

### 5.3 Git 备份（推荐）

将 workspace 视为私人记忆。放入**私有** git 仓库以便备份和恢复。

```bash
cd ~/.openclaw/workspace
git init
git add AGENTS.md SOUL.md TOOLS.md IDENTITY.md USER.md HEARTBEAT.md memory/
git commit -m "Add agent workspace"

# 添加私有远程仓库并推送
git branch -M main
git remote add origin <https-url>
git push -u origin main
```

**建议的 `.gitignore`**：

```gitignore
.DS_Store
.env
**/*.key
**/*.pem
**/secrets*
```

> ⚠️ **不要提交 secrets**：即使在私有仓库中，也要避免存储 API keys、OAuth tokens、密码或私人凭证。

### 5.4 迁移到新机器

1. **克隆仓库**到目标路径（默认 `~/.openclaw/workspace`）
2. **更新配置**：在 `~/.openclaw/openclaw.json` 中设置 `agents.defaults.workspace`
3. **补全缺失文件**：运行 `openclaw setup --workspace <path>` 生成缺失文件
4. **复制会话**（可选）：从旧机器复制 `~/.openclaw/agents/<agentId>/sessions/`

---

## 六、Heartbeat 机制

### 6.1 什么是 Heartbeat

Heartbeat 在**主会话中运行周期性 Agent 轮次**，让模型能够在不打扰你的情况下提醒需要注意的事项。

- Heartbeat 是**主会话的定时轮次**，不创建后台任务记录
- 默认间隔：`30m`（Anthropic OAuth/token auth 时为 `1h`）
- 用 `0m` 禁用

**Heartbeat vs Cron**：

| 场景 | 使用 |
|------|------|
| 多个检查可以批量（收件箱 + 日历 + 通知） | Heartbeat |
| 需要最近消息的对话上下文 | Heartbeat |
| 时间可以稍微漂移（每 ~30 分钟） | Heartbeat |
| 精确时间重要（"每周一 9:00"） | Cron |
| 任务需要隔离主会话历史 | Cron |
| 一次性提醒（"20 分钟后提醒我"） | Cron |

### 6.2 配置详解

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",              // 间隔（0m 禁用）
        target: "last",            // 投递目标：last | none | <channel id>
        directPolicy: "allow",     // 允许/阻止直接/DM 投递
        lightContext: true,        // 仅注入 HEARTBEAT.md
        isolatedSession: true,     // 每次心跳新建会话
        skipWhenBusy: true,        // 忙时推迟
        includeReasoning: false,   // 同时发送 Reasoning 消息
        ackMaxChars: 300,          // HEARTBEAT_OK 后允许的最大字符数
        // activeHours: { start: "08:00", end: "24:00" },
        prompt: "Read HEARTBEAT.md if it exists... If nothing needs attention, reply HEARTBEAT_OK.",
      },
    },
  },
}
```

**字段说明**：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `every` | string | `30m` | 心跳间隔 |
| `model` | string | — | 心跳专用模型覆盖 |
| `target` | string | `none` | 投递目标：`last`（上次联系）、`none`（不投递）、频道 ID |
| `to` | string | — | 可选收件人覆盖（E.164、Telegram chat id 等）|
| `accountId` | string | — | 多账户频道的账户 ID |
| `lightContext` | boolean | `false` | true 时只注入 HEARTBEAT.md |
| `isolatedSession` | boolean | `false` | true 时每次心跳新建会话（无对话历史）|
| `skipWhenBusy` | boolean | `false` | true 时子代理/嵌套通道忙也推迟 |
| `includeReasoning` | boolean | `false` | 同时发送 Reasoning 消息 |
| `activeHours` | object | — | 限制运行时间窗口 |
| `prompt` | string | 默认提示 | 覆盖默认提示正文 |
| `ackMaxChars` | number | `300` | HEARTBEAT_OK 后允许的最大字符数 |

**作用域优先级**：
- `agents.defaults.heartbeat` → 全局默认
- `agents.list[].heartbeat` → 合并覆盖；如果任何 agent 有 heartbeat 块，**只有这些 agent** 运行心跳
- `channels.defaults.heartbeat` → 频道默认
- `channels.<channel>.heartbeat` → 频道覆盖
- `channels.<channel>.accounts.<id>.heartbeat` → 账户覆盖

**按 Agent 的心跳示例**（仅 ops agent 运行心跳）：

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last",
      },
    },
    list: [
      { id: "main", default: true },
      {
        id: "ops",
        heartbeat: {
          every: "1h",
          target: "whatsapp",
          to: "+15551234567",
        },
      },
    ],
  },
}
```

### 6.3 HEARTBEAT.md 的用法

如果 workspace 中存在 `HEARTBEAT.md`，默认提示会告诉 Agent 读取它。

**保持简短**——每个心跳轮次都要加载它。

**基本示例**：

```markdown
# Heartbeat checklist

- Quick scan: anything urgent in inboxes?
- If it's daytime, do a lightweight check-in if nothing else is pending.
- If a task is blocked, write down _what is missing_.
```

**如果文件为空**（只有空白行和 markdown 标题），OpenClaw 会跳过心跳运行以节省 API 调用（`reason=empty-heartbeat-file`）。

**Agent 可以更新它**——在普通聊天中告诉 Agent：
- "Update `HEARTBEAT.md` to add a daily calendar check."
- "Rewrite `HEARTBEAT.md` so it's shorter."

> ⚠️ 不要在 `HEARTBEAT.md` 中放 secrets——它会成为提示上下文的一部分。

### 6.4 tasks: 结构化任务块

`HEARTBEAT.md` 支持 `tasks:` 块用于心跳内部基于间隔的检查。

```markdown
tasks:

- name: inbox-triage
  interval: 30m
  prompt: "Check for urgent unread emails and flag anything time sensitive."
- name: calendar-scan
  interval: 2h
  prompt: "Check for upcoming meetings that need prep or follow-up."

# Additional instructions
- Keep alerts short.
- If nothing needs attention after all due tasks, reply HEARTBEAT_OK.
```

**行为**：
- OpenClaw 解析 `tasks:` 块并检查每个任务自己的 `interval`
- 只有**到期**的任务才会包含在该次心跳提示中
- 如果没有任务到期，心跳被完全跳过（`reason=no-tasks-due`）
- 非任务内容保留并作为额外上下文附加在到期任务列表之后
- 任务上次运行时间戳存储在会话状态中（`heartbeatTaskState`），重启后仍然保留

### 6.5 响应契约

- **无需关注时**：回复 **`HEARTBEAT_OK`**
- **HEARTBEAT_OK 处理**：当出现在回复**开头或结尾**时，被视为确认。如果剩余内容 ≤ `ackMaxChars`（默认 300），token 被剥离且回复被丢弃
- **HEARTBEAT_OK 在中间**：不被特殊处理
- **警报时**：**不要**包含 `HEARTBEAT_OK`；只返回警报文本

### 6.6 可见性控制

```yaml
channels:
  defaults:
    heartbeat:
      showOk: false       # 隐藏 HEARTBEAT_OK（默认）
      showAlerts: true    # 显示警报消息（默认）
      useIndicator: true  # 发送指示器事件（默认）
  telegram:
    heartbeat:
      showOk: true        # Telegram 上显示 OK 确认
```

**优先级**：账户 → 频道 → 频道默认 → 内置默认

**常见模式**：

| 目标 | 配置 |
|------|------|
| 默认行为（静默 OK，警报开启） | _(无需配置)_ |
| 完全静默 | `showOk: false, showAlerts: false, useIndicator: false` |
| 仅指示器 | `showOk: false, showAlerts: false, useIndicator: true` |

> 如果三个都设为 false，OpenClaw 完全跳过节拍运行（无模型调用）。

### 6.7 成本优化建议

心跳运行完整的 Agent 轮次。缩短间隔会消耗更多 token。降低成本的方法：

- `isolatedSession: true` — 避免发送完整对话历史（~100K token 降至 ~2-5K）
- `lightContext: true` — 只注入 `HEARTBEAT.md`
- 设置更便宜的 `model`（如 `ollama/llama3.2:1b`）
- 保持 `HEARTBEAT.md` 短小
- `target: "none"` — 如果只需要内部状态更新

---

## 七、编写最佳实践

### Workspace 文件分工

| 文件 | 负责 | 不负责 |
|------|------|--------|
| `AGENTS.md` | 操作规则、记忆系统、安全红线、Heartbeat 策略 | 语气/人格 |
| `SOUL.md` | 语气、观点、边界、氛围、风格 | 操作规则 |
| `TOOLS.md` | 环境专属工具约定 | 工具可用性控制 |
| `IDENTITY.md` | 名称、emoji、avatar | — |
| `USER.md` | 用户信息、偏好 | — |
| `HEARTBEAT.md` | 定期检查清单 | 复杂逻辑 |

### 文件大小控制

- `SOUL.md`：保持简洁，一页以内为佳
- `AGENTS.md`：可以较长，但核心规则放在前面
- `TOOLS.md`：按需添加，定期清理过时条目
- `HEARTBEAT.md`：尽量短，检查清单形式
- `MEMORY.md`：定期整理，删除过时内容

### 迭代优化

1. **观察 Agent 行为** — 如果 Agent 太机械，强化 `SOUL.md`
2. **记录错误模式** — 如果 Agent 重复犯错，在 `AGENTS.md` 添加规则
3. **定期复盘** — 每几周回顾一次 `MEMORY.md` 和 `AGENTS.md`
4. **版本控制** — 用 git 追踪变更，便于回滚

---

## 八、完整配置示例

### Agent 默认配置

```json5
{
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
      model: "moonshot/kimi-k2.6",
      userTimezone: "Asia/Shanghai",
      timeFormat: "auto",
      skipBootstrap: false,
      bootstrapMaxChars: 12000,
      bootstrapTotalMaxChars: 60000,
      bootstrapPromptTruncationWarning: "once",
      heartbeat: {
        every: "30m",
        target: "last",
        directPolicy: "allow",
        lightContext: false,
        isolatedSession: false,
        skipWhenBusy: false,
        includeReasoning: false,
        ackMaxChars: 300,
      },
      sandbox: {
        enabled: false,
        workspaceRoot: "~/.openclaw/sandboxes",
      },
    },
    list: [
      {
        id: "main",
        default: true,
      },
    ],
  },
}
```

### Workspace 文件结构

```
~/.openclaw/workspace/
├── AGENTS.md
├── SOUL.md
├── TOOLS.md
├── IDENTITY.md
├── USER.md
├── HEARTBEAT.md
├── memory/
│   ├── 2026-05-01.md
│   └── 2026-05-02.md
└── .gitignore
```

---

## 九、常见问题

### Q1：修改 workspace 文件后需要重启 Gateway 吗？

**不需要**。workspace 文件在每次会话启动时重新读取。修改后立即生效。

### Q2：Agent 不遵循我写的规则怎么办？

1. **检查文件位置** — 确保文件在正确的 workspace 目录下
2. **检查文件大小** — 如果超过 `bootstrapMaxChars`，内容会被截断
3. **强化措辞** — 使用祈使句，避免模糊的"应该"
4. **放在 AGENTS.md** — 操作规则放在 `AGENTS.md` 比 `SOUL.md` 更有效
5. **使用 /context detail** — 检查文件是否正确注入

### Q3：如何查看 System Prompt 中注入的内容？

使用 CLI 命令：

```bash
/context list       # 查看各文件贡献的 token 数
/context detail     # 查看详细注入内容
```

### Q4：多 Agent 如何配置不同 workspace？

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        default: true,
        workspace: "~/.openclaw/workspace-personal",
      },
      {
        id: "work",
        workspace: "~/.openclaw/workspace-work",
      },
    ],
  },
}
```

### Q5：BOOTSTRAP.md 删掉了又自动出现了？

确保设置 `skipBootstrap: true`，否则 OpenClaw 在检测到缺失文件时会重新创建默认模板。

### Q6：Heartbeat 运行后没有收到消息？

检查：
1. `target` 是否设置为 `none`（默认）
2. 频道级别的 `showAlerts` 是否为 `true`
3. Agent 回复是否只包含 `HEARTBEAT_OK`（会被静默丢弃）
4. `activeHours` 是否排除了当前时间

### Q7：memory/ 下的文件会被自动注入吗？

**不会**。`memory/*.md` 文件**不是**正常 bootstrap Project Context 的一部分。在普通轮次中通过 `memory_search` 和 `memory_get` 工具按需访问。仅在 `/new` 和 `/reset` 启动时，运行时可能将最近的每日记忆作为一次性启动上下文块附加。

---

> **文档版本**：v1.0  
> **最后更新**：2026-05-03  
> **适用版本**：OpenClaw 2026.4.14+  
>  
> **参考文档**：
> - https://docs.openclaw.ai/concepts/agent
> - https://docs.openclaw.ai/concepts/agent-workspace
> - https://docs.openclaw.ai/reference/AGENTS.default
> - https://docs.openclaw.ai/concepts/system-prompt
> - https://docs.openclaw.ai/gateway/heartbeat
> - https://docs.openclaw.ai/concepts/soul
