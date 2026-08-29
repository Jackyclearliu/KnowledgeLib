# OpenClaw 配置手册

> 基于 OpenClaw 官方文档整理，版本对应 v2026.6.5 及后续版本。  
> 本文档覆盖 `agents` 和 `tools` 两大核心配置域，并对**运行时（runtime）**相关概念进行重点说明。

---

## 目录

1. [配置总览](#一配置总览)
2. [Agent 配置详解](#二agent-配置详解)
   - 2.1 [Agent 默认值](#21-agent-默认值)
   - 2.2 [模型与运行时策略](#22-模型与运行时策略-runtime-重点)
   - 2.3 [启动上下文与提示词预算](#23-启动上下文与提示词预算)
   - 2.4 [心跳机制](#24-心跳机制)
   - 2.5 [上下文压缩](#25-上下文压缩)
   - 2.6 [沙箱与隔离](#26-沙箱与隔离)
   - 2.7 [多 Agent 路由](#27-多-agent-路由)
3. [Tools 配置详解](#三tools-配置详解)
   - 3.1 [工具策略与权限](#31-工具策略与权限)
   - 3.2 [MCP 与插件工具](#32-mcp-与插件工具)
   - 3.3 [代码模式](#33-代码模式)
   - 3.4 [媒体处理](#34-媒体处理)
   - 3.5 [会话工具](#35-会话工具)
   - 3.6 [子 Agent](#36-子-agent)
4. [自定义 Provider 与 Base URL](#四自定义-provider-与-base-url)
5. [Session、Messages 与 Talk](#五sessionmessages-与-talk)
6. [运行时（Runtime）概念详解](#六运行时runtime概念详解)

---

## 一、配置总览

OpenClaw 的配置以 JSON5 格式编写，通常存放在 `~/.openclaw/config.json` 或 `~/.openclaw/config.json5` 中。配置按顶层命名空间划分：

| 命名空间 | 职责 |
|---------|------|
| `agents` | Agent 行为、模型、运行时、沙箱、心跳等 |
| `tools` | 工具白名单/黑名单、工具参数、权限控制 |
| `models` | 自定义 Provider、模型目录、Base URL |
| `session` | 会话生命周期、存储策略、重置规则 |
| `messages` | 消息队列、去抖动、TTS、回复前缀 |
| `talk` | 移动端/桌面端 Talk 模式（语音对话） |
| `channels` | 各频道的接入账号与行为覆盖（见频道文档） |
| `bindings` | 多 Agent 的绑定路由规则 |

> **核心原则**：`agents.defaults` 提供全局默认值，`agents.list[]` 可按 Agent 进行**完全覆盖**，`tools.*` 则是**以安全为导向**的工具权限控制层。

---

## 二、Agent 配置详解

### 2.1 Agent 默认值

#### `agents.defaults.workspace`

```json5
{ agents: { defaults: { workspace: "~/.openclaw/workspace" } } }
```

- Agent 的工作目录。环境变量 `OPENCLAW_WORKSPACE_DIR` 优先级低于显式配置。

#### `agents.defaults.repoRoot`

```json5
{ agents: { defaults: { repoRoot: "~/Projects/openclaw" } } }
```

- 在系统提示词的 Runtime 行中显示的项目根目录。如果不设置，OpenClaw 会从工作目录向上自动探测 `.git` 根目录。

#### `agents.defaults.skills`

```json5
{ agents: { defaults: { skills: ["github", "weather"] } } }
```

- 默认技能白名单。`agents.list[].skills` 为**完全替换**（非合并），`[]` 表示禁用所有技能。

#### `agents.defaults.skipBootstrap` / `skipOptionalBootstrapFiles`

```json5
{ agents: { defaults: { skipBootstrap: true } } }
{ agents: { defaults: { skipOptionalBootstrapFiles: ["SOUL.md", "USER.md"] } } }
```

- 跳过自动创建启动文件（如 `AGENTS.md`、`SOUL.md` 等）。可选文件包括 `SOUL.md`、`USER.md`、`HEARTBEAT.md`、`IDENTITY.md`。

---

### 2.2 模型与运行时策略（Runtime 重点）

这是 OpenClaw 最核心的配置区域，决定了**哪个模型处理请求**，以及**由哪个执行后端运行 Agent 回合**。

#### `agents.defaults.model` — 模型配置

```json5
{ agents: { defaults: { 
    model: { 
      primary: "anthropic/claude-opus-4-6", 
      fallbacks: ["minimax/MiniMax-M2.7"] 
    },
    imageModel: { primary: "openrouter/qwen/qwen-2.5-vl-72b-instruct:free" },
    imageGenerationModel: { primary: "openai/gpt-image-2" },
    videoGenerationModel: { primary: "qwen/wan2.6-t2v" },
    musicGenerationModel: { primary: "google/lyria-3-clip-preview" },
    pdfModel: { primary: "anthropic/claude-opus-4-6" },
    params: { cacheRetention: "long" },
    thinkingDefault: "low",
    reasoningDefault: "off",
    elevatedDefault: "on",
    timeoutSeconds: 600,
    contextTokens: 200000,
    maxConcurrent: 3,
  } } 
}
```

| 字段 | 说明 |
|------|------|
| `model` | 主模型（文本推理），支持 `provider/model` 字符串或 `{ primary, fallbacks }` 对象 |
| `imageModel` | 图像理解模型（视觉模型），当主模型不支持图像时作为降级 |
| `imageGenerationModel` | 图像生成模型（如 `openai/gpt-image-2`） |
| `videoGenerationModel` | 视频生成模型（如 `qwen/wan2.6-t2v`） |
| `musicGenerationModel` | 音乐生成模型 |
| `pdfModel` | PDF 解析模型 |
| `params` | 全局 Provider 参数（如 `cacheRetention`、`temperature`） |
| `thinkingDefault` | 默认思考级别：`off` / `minimal` / `low` / `medium` / `high` / `xhigh` / `adaptive` |
| `reasoningDefault` | 推理可见度：`off` / `on` / `stream` |
| `elevatedDefault` | 提升权限输出级别：`off` / `on` / `ask` / `full` |
| `timeoutSeconds` | 单次 Agent 回合最大超时时间 |
| `contextTokens` | 有效上下文 Token 上限 |
| `maxConcurrent` | 跨会话的最大并行 Agent 运行数（默认 4） |

> **格式说明**：`provider/model` 是标准格式，例如 `anthropic/claude-opus-4-6`。如果省略 Provider，OpenClaw 会尝试别名匹配，然后匹配已配置 Provider，最后降级到默认 Provider。

#### `agents.defaults.models` — 模型目录与别名

```json5
{ agents: { defaults: { 
    models: {
      "anthropic/claude-opus-4-6": { alias: "opus" },
      "minimax/MiniMax-M2.7": { alias: "minimax" },
      "openai/*": {},  // 显示该 Provider 下所有发现的模型
    },
  } } 
}
```

- 每个条目可以设置 `alias`（快捷别名）、`params`（Provider 专属参数）和 `agentRuntime`（运行时策略）。
- 使用 `provider/*` 通配符可以自动列出该 Provider 发现的所有模型，无需手动维护。

**内置别名速查表**：

| 别名 | 对应模型 |
|------|---------|
| `opus` | `anthropic/claude-opus-4-6` |
| `sonnet` | `anthropic/claude-sonnet-4-6` |
| `gpt` | `openai/gpt-5.5` |
| `gpt-mini` | `openai/gpt-5.4-mini` |
| `gpt-nano` | `openai/gpt-5.4-nano` |
| `gemini` | `google/gemini-3.1-pro-preview` |
| `gemini-flash` | `google/gemini-3-flash-preview` |

#### `models.providers.*.agentRuntime` / 模型级 Runtime 策略

```json5
{ models: { providers: { openai: { agentRuntime: { id: "codex" } } } } }
```

```json5
{ agents: { defaults: { 
    models: {
      "anthropic/claude-opus-4-8": { agentRuntime: { id: "claude-cli" } },
      "vllm/*": { agentRuntime: { id: "openclaw" } },
    },
  } } 
}
```

**Runtime 是什么？**  
Runtime 决定了**Agent 的文本回合由哪个执行后端处理**。它只控制**文本 Agent 回合执行**，媒体生成、视觉、PDF、音乐、视频和 TTS 仍然使用各自的 Provider/模型设置。

| `id` 值 | 含义 |
|---------|------|
| `"auto"` | 默认。让已注册的插件 Harness 认领支持的回合，没有匹配时回退到 OpenClaw 内置运行时 |
| `"openclaw"` | 强制使用 OpenClaw 内置运行时 |
| `"codex"` | 使用 Codex CLI 后端（OpenAI 的 Agent 模型默认使用） |
| `"claude-cli"` | 使用 Claude CLI 后端 |
| 插件 Harness ID | 已注册插件的运行时标识 |

**Runtime 选择优先级（从高到低）**：

1. 精确模型策略：`agents.list[].models["provider/model"]`
2. 默认模型策略：`agents.defaults.models["provider/model"]` 或 `models.providers.<provider>.models[]`
3. Agent 级通配符：`agents.list[] / agents.defaults.models["provider/*"]`
4. Provider 级策略：`models.providers.<provider>.agentRuntime`

> ⚠️ **重要**：旧版配置中的 `agents.defaults.agentRuntime`、`agents.list[].agentRuntime`、会话级 Runtime 固定和 `OPENCLAW_AGENT_RUNTIME` 环境变量**已被忽略**。请使用 `models.providers.*.agentRuntime` 或 `agents.defaults.models["provider/model"].agentRuntime` 来配置。运行 `openclaw doctor --fix` 可清理旧配置。

#### `agents.defaults.cliBackends` — CLI 降级后端

```json5
{ agents: { defaults: { 
    cliBackends: {
      "claude-cli": { command: "/opt/homebrew/bin/claude" },
      "my-cli": { 
        command: "my-cli", 
        args: ["--json"], 
        output: "json",
        modelArg: "--model",
        sessionArg: "--session",
        systemPromptArg: "--system",
      },
    },
  } } 
}
```

- 当 API Provider 失败时的纯文本降级方案。CLI 后端**禁用所有工具**，仅用于文本回退。
- 支持会话、图片透传和系统提示词传递。

#### `agents.defaults.localService` — 本地模型服务

```json5
{ models: { providers: { ollama: { 
  localService: {
    healthUrl: "http://localhost:11434",
    command: "/usr/local/bin/ollama",
    args: ["serve"],
    readyTimeoutMs: 30000,
    idleStopMs: 0,  // 0 表示保持运行直到 OpenClaw 退出
  } 
} } } }
```

- 当所选模型属于该 Provider 时，OpenClaw 会先探测 `healthUrl`，如果端点不可用则自动启动 `command`。
- `idleStopMs: 0` 保持进程存活；正值表示空闲多少毫秒后停止进程。

---

### 2.3 启动上下文与提示词预算

OpenClaw 使用**多个独立的提示词预算**来控制不同子系统的上下文注入，而非单一全局限制。

#### `agents.defaults.contextInjection`

```json5
{ agents: { defaults: { contextInjection: "continuation-skip" } } }
```

| 值 | 行为 |
|----|------|
| `"always"`（默认） | 每次回合都注入工作区启动文件 |
| `"continuation-skip"` | 安全续接回合（已完成助手响应后）跳过重新注入，减少提示词大小 |
| `"never"` | 完全禁用工作区启动文件注入 |

#### `agents.defaults.bootstrapMaxChars` / `bootstrapTotalMaxChars`

```json5
{ agents: { defaults: { 
    bootstrapMaxChars: 20000,      // 单个启动文件最大字符数
    bootstrapTotalMaxChars: 60000, // 所有启动文件总字符数上限
  } } 
}
```

#### `agents.defaults.startupContext` — 启动前奏

```json5
{ agents: { defaults: { 
    startupContext: {
      enabled: true,
      applyOn: ["new", "reset"],     // 在 /new 和 /reset 时触发
      dailyMemoryDays: 2,            // 加载最近几天的记忆文件
      maxFileBytes: 16384,
      maxFileChars: 1200,
      maxTotalChars: 2800,
    },
  } } 
}
```

- 在首次重置/启动模型运行时注入的前奏内容。裸 `/new` 和 `/reset` 命令只确认重置，不调用模型。

#### `agents.defaults.contextLimits` — 运行时上下文限制

```json5
{ agents: { defaults: { 
    contextLimits: {
      memoryGetMaxChars: 12000,      // memory_get 摘录上限
      memoryGetDefaultLines: 120,  // memory_get 默认行数
      toolResultMaxChars: 16000,     // 工具结果上限（高级）
      postCompactionMaxChars: 1800,  // 压缩后 AGENTS.md 摘录上限
    },
  } } 
}
```

> `toolResultMaxChars` 的默认值是模型上下文相关的：低于 100K 上下文为 16000，100K+ 为 32000，200K+ 为 64000，且不超过上下文窗口的约 30%。

---

### 2.4 心跳机制

心跳让 Agent 定期自主检查环境、执行预定义任务。

```json5
{ agents: { defaults: { 
    heartbeat: {
      every: "30m",                  // 间隔：0m 禁用
      model: "openai/gpt-5.4-mini", // 心跳专用模型（通常用小模型省成本）
      includeReasoning: false,
      includeSystemPromptSection: true,  // 是否在系统提示词中显示 Heartbeat 段落
      lightContext: false,           // true：仅保留 HEARTBEAT.md
      isolatedSession: false,        // true：每次心跳在新会话中运行（无历史上下文）
      skipWhenBusy: false,           // true：Agent 忙碌时跳过心跳
      session: "main",
      directPolicy: "allow",         // allow | block（直接消息策略）
      target: "none",                // 通知目标：none | last | whatsapp | telegram | ...
      prompt: "Read HEARTBEAT.md if it exists...",
      ackMaxChars: 300,
      suppressToolErrorWarnings: false,
      timeoutSeconds: 45,
    },
  } } 
}
```

**关键说明**：
- `every`: API Key 认证默认 30 分钟，OAuth 认证默认 1 小时。
- `isolatedSession: true` 可将每次心跳的 Token 成本从约 100K 降至 2-5K。
- `lightContext: true` 使用轻量级启动上下文，仅保留 `HEARTBEAT.md`。
- 当**任何 Agent 定义了 heartbeat 时，只有这些 Agent 会运行心跳**。

---

### 2.5 上下文压缩

当会话历史过长时，OpenClaw 会压缩旧上下文以释放 Token 预算。

```json5
{ agents: { defaults: { 
    compaction: {
      mode: "safeguard",             // default | safeguard（分块摘要）
      provider: "my-provider",       // 可选：注册的外部压缩 Provider
      timeoutSeconds: 900,
      reserveTokensFloor: 24000,
      keepRecentTokens: 50000,       // 保留最近多少 Token 的原始记录
      identifierPolicy: "strict",    // strict | off | custom（保留标识符策略）
      qualityGuard: { enabled: true, maxRetries: 1 },
      midTurnPrecheck: { enabled: false },  // 工具循环中检查上下文压力
      postCompactionSections: ["Session Startup", "Red Lines"],  // 压缩后重新注入的 AGENTS.md 段落
      model: "openrouter/anthropic/claude-sonnet-4-6",  // 压缩专用模型
      truncateAfterCompaction: true, // 压缩后旋转到更小的 JSONL
      maxActiveTranscriptBytes: "20mb",  // 主动触发本地压缩的阈值
      notifyUser: true,              // 压缩时通知用户
      memoryFlush: {                 // 压缩前自动存储持久记忆
        enabled: true,
        model: "ollama/qwen3:8b",
        softThresholdTokens: 6000,
        systemPrompt: "Session nearing compaction. Store durable memories now.",
      },
    },
  } } 
}
```

**模式说明**：
- `default`: 标准压缩（完整摘要）
- `safeguard`: 分块摘要，更适合超长的历史记录
- `provider`: 使用外部 Provider 的 `summarize()` 方法替代内置 LLM 摘要，强制使用 `safeguard` 模式

---

### 2.6 沙箱与隔离

沙箱控制 Agent 代码执行的安全边界。

```json5
{ agents: { defaults: { 
    sandbox: {
      mode: "non-main",              // off | non-main | all
      backend: "docker",              // docker | ssh | openshell
      scope: "agent",                 // session | agent | shared
      workspaceAccess: "none",        // none | ro | rw
      workspaceRoot: "~/.openclaw/sandboxes",
      docker: {
        image: "openclaw-sandbox:bookworm-slim",
        containerPrefix: "openclaw-sbx-",
        workdir: "/workspace",
        readOnlyRoot: true,
        network: "none",              // none | bridge（host 被阻止）
        user: "1000:1000",
        capDrop: ["ALL"],
        memory: "1g",
        memorySwap: "2g",
        cpus: 1,
        pidsLimit: 256,
        setupCommand: "apt-get update && apt-get install -y git curl jq",
        binds: ["/home/user/source:/source:rw"],
      },
      browser: {                      // 沙箱内浏览器
        enabled: false,
        image: "openclaw-sandbox-browser:bookworm-slim",
        network: "openclaw-sandbox-browser",
        cdpPort: 9222,
        headless: false,
        enableNoVnc: true,
        allowHostControl: false,     // 阻止沙箱会话控制主机浏览器
      },
      prune: { idleHours: 24, maxAgeDays: 7 },
    },
  } } 
}
```

**模式说明**：
- `mode: "off"`：无沙箱（所有执行在主机上）
- `mode: "non-main"`：仅对非主 Agent 启用沙箱（推荐）
- `mode: "all"`：所有 Agent 都启用沙箱

**后端说明**：
- `docker`（默认）：本地 Docker 运行时
- `ssh`：通过 SSH 连接到远程运行时
- `openshell`：OpenShell 插件管理的运行时

**Scope 说明**：
- `session`：每个会话独立的容器 + 工作区
- `agent`：每个 Agent 一个容器 + 工作区（默认）
- `shared`：共享容器和工作区（无跨会话隔离）

**Workspace 访问**：
- `none`：沙箱工作区在 `~/.openclaw/sandboxes` 下
- `ro`：沙箱工作区在 `/workspace`，Agent 工作区以只读方式挂载到 `/agent`
- `rw`：Agent 工作区以读写方式挂载到 `/workspace`

> 沙箱工具列表在 `tools.sandbox.tools` 中配置，与主工具策略分开管理。详见 [3.1 工具策略](#31-工具策略与权限)。

---

### 2.7 多 Agent 路由

```json5
{ agents: { 
    list: [
      { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
  ],
}
```

**绑定匹配优先级**：
1. `match.peer`（精确匹配发送者）
2. `match.guildId` / `match.teamId`
3. `match.accountId`（精确账号）
4. `match.accountId: "*"`（频道级通配）
5. 默认 Agent

---

## 三、Tools 配置详解

### 3.1 工具策略与权限

#### `tools.profile` — 预设工具集

| Profile | 包含工具 |
|---------|---------|
| `minimal` | 仅 `session_status` |
| `coding` | 文件系统、运行时、Web、会话、记忆、Cron、图像生成、视频生成等 |
| `messaging` | 消息群组、会话工具 |
| `full` | 无限制（等同于未设置） |

#### `tools.allow` / `tools.deny` — 全局白名单/黑名单

```json5
{ tools: { deny: ["browser", "canvas"] } }
```

- 不区分大小写，支持 `*` 通配符。
- `deny` 优先级高于 `allow`。
- `write` 和 `apply_patch` 是**独立的工具 ID**，需要分别控制。

#### 工具群组速查

| 群组 | 包含工具 |
|------|---------|
| `group:runtime` | `exec`, `process`, `code_execution` |
| `group:fs` | `read`, `write`, `edit`, `apply_patch` |
| `group:sessions` | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `session_status` |
| `group:memory` | `memory_search`, `memory_get` |
| `group:web` | `web_search`, `x_search`, `web_fetch` |
| `group:ui` | `browser`, `canvas` |
| `group:automation` | `heartbeat_respond`, `cron`, `gateway` |
| `group:messaging` | `message` |
| `group:media` | `image`, `image_generate`, `music_generate`, `video_generate`, `tts` |
| `group:plugins` | 所有已加载插件拥有的工具 |

#### `tools.byProvider` — 按 Provider 限制工具

```json5
{ tools: { 
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
      "openai/gpt-5.4": { allow: ["group:fs", "sessions_list"] },
    },
  } 
}
```

- 按 Provider 或模型进一步限制工具。优先级：基础 Profile → Provider Profile → allow/deny。

#### `tools.toolsBySender` — 按发送者限制工具

```json5
{ tools: { 
    toolsBySender: {
      "channel:discord:1234567890123": { alsoAllow: ["group:fs"] },
      "id:guest-user-id": { deny: ["group:runtime", "group:fs"] },
      "*": { deny: ["exec", "process", "write", "edit", "apply_patch"] },
    },
  } 
}
```

- 发送者键格式：`channel:<channelId>:<senderId>`、`id:<senderId>`、`e164:<phone>`、`username:<handle>`、`name:<displayName>`、`*`（通配）。

#### `tools.elevated` — 提升权限控制

```json5
{ tools: { 
    elevated: {
      enabled: true,
      allowFrom: {
        whatsapp: ["+15555550123"],
        discord: ["1234567890123"],
      },
    },
  } 
}
```

- 提升权限的 `exec` 绕过沙箱，使用配置的逃逸路径（默认 `gateway`，或 `node` 当执行目标是 `node` 时）。
- Per-agent 的 `agents.list[].tools.elevated` 只能进一步收紧，不能放宽。

---

### 3.2 MCP 与插件工具

MCP（Model Context Protocol）服务器暴露的工具属于插件所有，通常在 `mcp.servers` 中配置。

**沙箱中的 MCP 工具**：

```json5
{ tools: { sandbox: { tools: { alsoAllow: ["bundle-mcp", "group:plugins"] } } } }
```

- `bundle-mcp`：OpenClaw 管理的 MCP 服务器
- `group:plugins`：所有已加载插件拥有的工具
- 也可以指定具体插件 ID 或工具名称（如 `outlook__send_mail` 或 `outlook__*`）

> MCP 工具名称的 glob 匹配使用 Provider 安全前缀（非原始 `mcp.servers` 键）。非 `[A-Za-z0-9_-]` 字符变为 `-`，不以字母开头的名称加 `mcp-` 前缀。例如 `mcp.servers["Outlook Graph"]` 的 glob 为 `outlook-graph__*`。

---

### 3.3 代码模式

```json5
{ tools: { codeMode: { enabled: true } } }
// 或简写
{ tools: { codeMode: true } }
```

- 启用后，模型在代码模式下只看到 `exec` 和 `wait` 工具。
- 正常 OpenClaw 工具移动到沙箱内的 `tools.*` 目录桥后面，MCP 工具通过生成的 `MCP` 命名空间可用。
- 访客代码可以通过 `API.list("mcp")` 和 `API.read("mcp/<server>.d.ts")` 查看 TypeScript 风格的签名。

---

### 3.4 媒体处理

```json5
{ tools: { 
    media: {
      concurrency: 2,
      audio: {
        enabled: true,
        maxBytes: 20971520,
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          { type: "cli", command: "whisper", args: ["--model", "base", "{{MediaPath}}"] },
        ],
      },
      image: {
        enabled: true,
        timeoutSeconds: 180,
        models: [{ provider: "ollama", model: "gemma4:26b" }],
      },
      video: {
        enabled: true,
        maxBytes: 52428800,
        models: [{ provider: "google", model: "gemini-3-flash-preview" }],
      },
    },
  } 
}
```

- 支持 Provider 和 CLI 两种模型入口类型。
- 支持模板变量：`{{MediaPath}}`、`{{Prompt}}`、`{{MaxChars}}` 等。
- 失败时会依次回退到下一个模型条目。

---

### 3.5 会话工具

```json5
{ tools: { sessions: { visibility: "tree" } } }
```

| 值 | 可见范围 |
|----|---------|
| `self` | 仅当前会话 |
| `tree` | 当前会话 + 由它派生的会话（子 Agent） |
| `agent` | 当前 Agent 的所有会话 |
| `all` | 所有会话（跨 Agent 需要 `tools.agentToAgent`） |

**沙箱限制**：当当前会话处于沙箱中且 `agents.defaults.sandbox.sessionToolsVisibility="spawned"` 时，可见性强制为 `tree`。

---

### 3.6 子 Agent

```json5
{ agents: { defaults: { 
    subagents: {
      allowAgents: ["research"],      // 允许派生的目标 Agent ID
      model: "minimax/MiniMax-M2.7",  // 子 Agent 默认模型
      maxConcurrent: 8,               // 最大并行子 Agent
      runTimeoutSeconds: 900,         // 子 Agent 运行超时
      announceTimeoutMs: 120000,      // 通知传递超时
      archiveAfterMinutes: 60,        // 多久后归档
    },
  } } 
}
```

- `allowAgents: ["*"]` 表示允许任何已配置的目标 Agent。
- `subagents.allowAgents` 也可以按 Agent 配置 `agents.list[].subagents.allowAgents`。
- 子 Agent 的工具策略在 `tools.subagents.tools.allow` / `tools.subagents.tools.deny` 中配置。

---

## 四、自定义 Provider 与 Base URL

```json5
{ models: { 
    mode: "merge",  // merge | replace
    providers: {
      "custom-proxy": {
        baseUrl: "http://localhost:4000/v1",
        apiKey: "LITELLM_KEY",
        api: "openai-completions",  // openai-completions | openai-responses | anthropic-messages | google-generative-ai
        models: [
          {
            id: "llama-3.1-8b",
            name: "Llama 3.1 8B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            contextTokens: 96000,
            maxTokens: 32000,
          },
        ],
      },
    },
  } 
}
```

**`api` 适配器说明**：
- `openai-completions`：适用于大多数 OpenAI 兼容的后端（MLX、vLLM、SGLang、本地服务器等）
- `openai-responses`：仅当后端支持 `/v1/responses` 时使用
- `anthropic-messages`：Anthropic 兼容后端（如 MiniMax M3）
- `google-generative-ai`：Google Gemini 风格后端

**安全说明**：`baseUrl` 也是**网络信任决策**——OpenClaw 允许该精确的 `scheme://host:port` 源通过受保护的 Fetch 路径，无需单独配置或信任其他私有源。

**合并优先级**（从高到低）：
1. Agent 的 `models.json` 中的非空 `baseUrl`
2. Agent 的 `models.json` 中的非空 `apiKey`（仅当该 Provider 未被 SecretRef 管理时）
3. 配置中的 `models.providers` 值
4. 插件生成的目录分片

**模型字段说明**：
- `contextWindow`：模型的原生上下文窗口（元数据）
- `contextTokens`：运行时有效上下文上限（可用此限制更小的预算）
- `maxTokens`：最大输出 Token 数
- `input`：输入模态：`["text"]` 或 `["text", "image"]`
- `compat.*`：兼容性提示（如 `thinkingFormat`、`requiresStringContent`、`strictMessageKeys` 等）

---

## 五、Session、Messages 与 Talk

### Session 配置

```json5
{ session: { 
    scope: "per-sender",           // per-sender | global
    dmScope: "main",               // main | per-peer | per-channel-peer | per-account-channel-peer
    identityLinks: {               // 跨频道会话共享
      alice: ["telegram:123456789", "discord:987654321012345678"],
    },
    reset: { mode: "daily", atHour: 4, idleMinutes: 60 },
    resetByType: {                 // 按类型覆盖
      thread: { mode: "daily", atHour: 4 },
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
    },
    maintenance: {                 // 会话维护
      mode: "enforce",
      pruneAfter: "30d",
      maxEntries: 500,
      maxDiskBytes: "500mb",
      highWaterBytes: "400mb",
    },
    threadBindings: {              // 线程绑定会话
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
    agentToAgent: { maxPingPongTurns: 5 },
  } 
}
```

**会话范围说明**：
- `per-sender`（默认）：每个发送者在频道中有独立会话
- `global`：频道内所有参与者共享一个会话（慎用）
- `dmScope` 控制 DM（私聊）的分组方式

### Messages 配置

```json5
{ messages: { 
    responsePrefix: "🦞",         // 或 "auto" 使用 [{identity.name}]
    ackReaction: "👀",
    ackReactionScope: "group-mentions",  // group-mentions | group-all | direct | all
    queue: {                       // 消息队列策略
      mode: "followup",            // steer | followup | collect | interrupt
      debounceMs: 500,
      cap: 20,
      drop: "summarize",           // old | new | summarize
    },
    inbound: { debounceMs: 2000 }, // 入站去抖动（合并同一发送者的快速文本消息）
    tts: { /* 见下文 */ },
  } 
}
```

**响应前缀模板变量**：

| 变量 | 说明 | 示例 |
|------|------|------|
| `{model}` | 短模型名 | `claude-opus-4-6` |
| `{modelFull}` | 完整模型标识 | `anthropic/claude-opus-4-6` |
| `{provider}` | Provider 名 | `anthropic` |
| `{thinkingLevel}` | 当前思考级别 | `high`、`low`、`off` |
| `{identity.name}` | Agent 身份名 | `Samantha` |

### Talk 配置（语音对话）

```json5
{ talk: { 
    provider: "elevenlabs",
    providers: {
      elevenlabs: {
        speakerVoiceId: "elevenlabs_voice_id",
        voiceAliases: { Clawd: "EXAVITQu4vr4xnSDxMaL" },
        modelId: "eleven_v3",
        outputFormat: "mp3_44100_128",
      },
      mlx: { modelId: "mlx-community/Soprano-80M-bf16" },
    },
    consultThinkingLevel: "low",
    consultFastMode: true,
    speechLocale: "ru-RU",
    silenceTimeoutMs: 1500,
    interruptOnSpeech: true,
    realtime: {                    // 实时语音模式
      provider: "openai",
      providers: { openai: { model: "gpt-realtime-2", speakerVoice: "cedar" } },
      instructions: "Speak warmly and keep answers brief.",
      mode: "realtime",
      transport: "webrtc",
      brain: "agent-consult",
    },
  } 
}
```

---

## 六、运行时（Runtime）概念详解

这是 OpenClaw 配置中最容易混淆的部分，本文档单独展开说明。

### 什么是 Runtime？

**Runtime（运行时）**决定了**Agent 的文本回合（text agent turn）由哪个执行后端处理**。它回答的是：**"谁来实际执行这个 Agent 的思考和工具调用？"**

OpenClaw 支持多种运行时后端：

| 运行时 | 描述 | 典型场景 |
|--------|------|---------|
| **OpenClaw 内置** (`openclaw`) | OpenClaw 自己的 Agent 循环，处理工具调用、上下文管理、流式输出 | 默认场景 |
| **Codex** (`codex`) | OpenAI Codex CLI 的 Agent 模式 | 使用 OpenAI GPT-5 系列模型时默认 |
| **Claude CLI** (`claude-cli`) | Anthropic Claude CLI 的 Agent 模式 | 使用 Claude 模型时 |
| **其他插件** | 已注册插件提供的 Harness | 特定生态集成 |

### 运行时与模型的关系

**运行时 ≠ 模型**。这是两个独立的维度：

- **模型**（Model）决定**使用哪个 LLM 进行推理**（如 `anthropic/claude-opus-4-6`）
- **运行时**（Runtime）决定**由哪个执行框架来驱动这个 LLM 的 Agent 循环**

例如，你可以：
- 使用 Claude 模型 + OpenClaw 内置运行时（标准方式）
- 使用 Claude 模型 + Claude CLI 运行时（让 Claude CLI 管理工具调用）
- 使用 GPT-5 模型 + Codex 运行时（OpenAI 官方推荐）

### 运行时配置位置（已更新）

> ⚠️ **重要变化**：旧版配置在 `agents.defaults.agentRuntime` 或 `agents.list[].agentRuntime` 中设置运行时，这在当前版本中**已被忽略**。请按以下方式配置：

```json5
// 方式一：Provider 级运行时（所有该 Provider 的模型使用同一个运行时）
{ models: { providers: { openai: { agentRuntime: { id: "codex" } } } } }

// 方式二：模型级运行时（精确到某个模型）
{ agents: { defaults: { 
    models: {
      "anthropic/claude-opus-4-8": { agentRuntime: { id: "claude-cli" } },
      "vllm/*": { agentRuntime: { id: "openclaw" } },
    },
  } } 
}

// 方式三：Per-Agent 模型级运行时
{ agents: { list: [ { 
    id: "main",
    models: { "openai/gpt-5.5": { agentRuntime: { id: "codex" } } },
  } ] } }
```

### 运行时选择优先级

OpenClaw 按以下顺序确定运行时（从最高到最低优先级）：

1. **Per-Agent 精确模型策略**：`agents.list[].models["provider/model"].agentRuntime`
2. **默认精确模型策略**：`agents.defaults.models["provider/model"].agentRuntime` 或 `models.providers.<provider>.models[].agentRuntime`
3. **Per-Agent 通配符策略**：`agents.list[].models["provider/*"].agentRuntime`
4. **默认通配符策略**：`agents.defaults.models["provider/*"].agentRuntime`
5. **Provider 级策略**：`models.providers.<provider>.agentRuntime`
6. **默认回退**：`auto`（让插件认领，无匹配则用 OpenClaw 内置）

### 运行时选择示例

**场景一：使用 Codex 处理 OpenAI 模型**
```json5
{ models: { providers: { openai: { agentRuntime: { id: "codex" } } } } }
// 效果：所有 openai/* 模型默认使用 Codex CLI 运行时
```

**场景二：使用 Claude CLI 处理特定 Claude 模型**
```json5
{ agents: { defaults: { 
    model: "anthropic/claude-opus-4-8",
    models: { "anthropic/claude-opus-4-8": { agentRuntime: { id: "claude-cli" } } },
  } } 
}
// 效果：opus-4-8 使用 Claude CLI，其他 anthropic 模型使用 OpenClaw 内置
```

**场景三：本地 vLLM 模型使用 OpenClaw 内置**
```json5
{ agents: { defaults: { 
    models: { "vllm/*": { agentRuntime: { id: "openclaw" } } },
  } } 
}
// 效果：所有 vLLM 模型都使用 OpenClaw 内置运行时
```

### 运行时与 CLI 后端的区别

| 维度 | 运行时（Runtime） | CLI 后端（CLI Backends） |
|------|-----------------|------------------------|
| 目的 | 正常 Agent 回合执行 | API 失败时的降级方案 |
| 工具支持 | 支持（取决于运行时） | **不支持工具**（纯文本） |
| 触发方式 | 自动根据模型选择 | 需要手动配置并在 API 失败时触发 |
| 配置位置 | `models.providers.*.agentRuntime` | `agents.defaults.cliBackends` |

### 总结：何时需要关心 Runtime？

| 场景 | 建议 |
|------|------|
| 使用 OpenAI GPT-5 系列 | 默认使用 Codex，通常无需额外配置 |
| 使用 Claude 模型且想尝试 Claude CLI 功能 | 配置 `agentRuntime: { id: "claude-cli" }` |
| 使用本地/自托管模型（vLLM、Ollama 等） | 配置 `agentRuntime: { id: "openclaw" }` 确保使用内置运行时 |
| 使用特殊插件或实验性后端 | 配置插件提供的 Harness ID |
| 遇到 "Runtime 不可用" 错误 | 检查 `openclaw doctor --fix` 清理旧配置，确认 Harness 已注册 |

---

> 📌 **文档维护建议**：本手册基于 OpenClaw 官方文档 `config-agents` 和 `config-tools` 页面整理。当版本升级时，建议重新抓取文档并对比本文档中标记为 **⚠️ 重要** 的部分，因为运行时相关的配置规则可能继续演进。
