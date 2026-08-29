---
description: OpenClaw 会话管理全面指南,涵盖会话路由、生命周期、压缩、修剪、后台任务和跨会话工具
---
# OpenClaw 会话管理手册

> 本文档全面介绍 OpenClaw 的会话管理机制,包括会话路由、生命周期管理、上下文压缩、工具修剪、后台任务追踪和跨会话操作工具。
> **适用版本**:OpenClaw 2026.4.14+

---

## 目录

- [OpenClaw 会话管理手册](#openclaw-会话管理手册)
  - [术语表](#术语表)
  - [一、会话基础概念](#一会话基础概念)
    - [1.1 什么是会话](#11-什么是会话)
    - [1.2 会话路由规则](#12-会话路由规则)
    - [1.3 会话键(Session Key)格式](#13-会话键session-key格式)
  - [二、会话生命周期](#二会话生命周期)
    - [2.1 会话创建](#21-会话创建)
    - [2.2 会话重置](#22-会话重置)
    - [2.3 会话过期](#23-会话过期)
    - [2.4 会话存储位置](#24-会话存储位置)
  - [三、DM 隔离配置](#三dm-隔离配置)
    - [3.1 DM 作用域(dmScope)](#31-dm作用域dmscope)
    - [3.2 身份链接(identityLinks)](#32-身份链接identitylinks)
  - [四、上下文压缩(Compaction)](#四上下文压缩compaction)
    - [4.1 什么是压缩](#41-什么是压缩)
    - [4.2 自动压缩](#42-自动压缩)
    - [4.3 手动压缩](#43-手动压缩)
    - [4.4 压缩配置](#44-压缩配置)
    - [4.5 压缩 vs 修剪](#45-压缩-vs-修剪)
  - [五、会话修剪(Session Pruning)](#五会话修剪session-pruning)
    - [5.1 什么是修剪](#51-什么是修剪)
    - [5.2 修剪工作原理](#52-修剪工作原理)
    - [5.3 修剪配置](#53-修剪配置)
    - [5.4 默认配置](#54-默认配置)
  - [六、会话工具](#六会话工具)
    - [6.1 工具列表](#61-工具列表)
    - [6.2 工具如何工作](#62-工具如何工作)
    - [6.3 工具使用场景示例](#63-工具使用场景示例)
    - [6.4 工具参数详解](#64-工具参数详解)
    - [6.5 工具调用流程](#65-工具调用流程)
    - [6.6 工具可见性范围](#66-工具可见性范围)
  - [七、后台任务(Background Tasks)](#七后台任务background-tasks)
    - [7.1 什么是后台任务](#71-什么是后台任务)
    - [7.2 任务创建场景](#72-任务创建场景)
    - [7.3 任务生命周期](#73-任务生命周期)
    - [7.4 任务 CLI 命令](#74-任务-cli-命令)
    - [7.5 通知策略](#75-通知策略)
    - [7.6 任务与相关系统的关系](#76-任务与相关系统的关系)
  - [八、频道路由](#八频道路由)
    - [8.1 路由规则](#81-路由规则)
    - [8.2 代理选择流程](#82-代理选择流程)
    - [8.3 广播组](#83-广播组)
  - [九、会话维护](#九会话维护)
    - [9.1 维护模式](#91-维护模式)
    - [9.2 清理命令](#92-清理命令)
    - [9.3 存储控制](#93-存储控制)
  - [十、常用命令速查](#十常用命令速查)
  - [十一、完整配置示例](#十一完整配置示例)

- [OpenClaw 会话管理手册](#openclaw-会话管理手册)
  - [目录](#目录)
  - [一、会话基础概念](#一会话基础概念)
    - [1.1 什么是会话](#11-什么是会话)
    - [1.2 会话路由规则](#12-会话路由规则)
    - [1.3 会话键(Session Key)格式](#13-会话键session-key格式)
  - [二、会话生命周期](#二会话生命周期)
    - [2.1 会话创建](#21-会话创建)
    - [2.2 会话重置](#22-会话重置)
    - [2.3 会话过期](#23-会话过期)
    - [2.4 会话存储位置](#24-会话存储位置)
  - [三、DM 隔离配置](#三dm-隔离配置)
    - [3.1 DM 作用域(dmScope)](#31-dm作用域dmscope)
    - [3.2 身份链接(identityLinks)](#32-身份链接identitylinks)
  - [四、上下文压缩(Compaction)](#四上下文压缩compaction)
    - [4.1 什么是压缩](#41-什么是压缩)
    - [4.2 自动压缩](#42-自动压缩)
    - [4.3 手动压缩](#43-手动压缩)
    - [4.4 压缩配置](#44-压缩配置)
    - [4.5 压缩 vs 修剪](#45-压缩-vs-修剪)
  - [五、会话修剪(Session Pruning)](#五会话修剪session-pruning)
    - [5.1 什么是修剪](#51-什么是修剪)
    - [5.2 修剪工作原理](#52-修剪工作原理)
    - [5.3 修剪配置](#53-修剪配置)
    - [5.4 默认配置](#54-默认配置)
  - [六、会话工具](#六会话工具)
    - [6.1 工具列表](#61-工具列表)
    - [6.2 工具如何工作](#62-工具如何工作)
    - [6.3 工具使用场景示例](#63-工具使用场景示例)
    - [6.4 工具参数详解](#64-工具参数详解)
    - [6.5 工具调用流程](#65-工具调用流程)
    - [6.6 工具可见性范围](#66-工具可见性范围)
  - [七、后台任务(Background Tasks)](#七后台任务background-tasks)
    - [7.1 什么是后台任务](#71-什么是后台任务)
    - [7.2 任务创建场景](#72-任务创建场景)
    - [7.3 任务生命周期](#73-任务生命周期)
    - [7.4 任务 CLI 命令](#74-任务-cli-命令)
    - [7.5 通知策略](#75-通知策略)
    - [7.6 任务与相关系统的关系](#76-任务与相关系统的关系)
  - [八、频道路由](#八频道路由)
    - [8.1 路由规则](#81-路由规则)
    - [8.2 代理选择流程](#82-代理选择流程)
    - [8.3 广播组](#83-广播组)
  - [九、会话维护](#九会话维护)
    - [9.1 维护模式](#91-维护模式)
    - [9.2 清理命令](#92-清理命令)
    - [9.3 存储控制](#93-存储控制)
  - [十、常用命令速查](#十常用命令速查)
  - [十一、完整配置示例](#十一完整配置示例)

---

## 术语表

本文档中使用的专业术语和缩略语:

### OpenClaw 核心概念

| 术语 | 英文全称 | 定义 | 示例/说明 |
|------|----------|------|-----------|
| **会话** | Session | 用户与 Agent 之间的一段连续对话上下文 | 每个聊天窗口对应一个会话 |
| **Agent** | Agent | OpenClaw 中的智能代理,负责处理用户请求 | 可以理解为"AI 助手实例" |
| **网关** | Gateway | OpenClaw 的核心服务进程,管理所有会话和路由 | 运行 `openclaw gateway` 启动 |
| **频道** | Channel | 消息来源渠道,如 Telegram、Discord、Slack 等 | `telegram`、`discord` 等 |
| **会话键** | Session Key | 唯一标识一个会话的字符串,用于路由和隔离 | `agent:main:telegram:group:xxx` |
| **DM** | Direct Message | 私信/直接消息,一对一的私人对话 | 区别于群组消息 |
| **Guild** | Guild | Discord 中的服务器/社群 | 相当于 Telegram 的群组 |

### 技术术语

| 术语 | 英文全称 | 定义 | 说明 |
|------|----------|------|------|
| **Cron** | Cron | 类 Unix 系统中的定时任务调度器 | 用于设置周期性执行的任务 |
| **ACP** | Agent Calling Protocol | Agent 调用协议,用于连接外部代码编辑器 | 支持 Codex、Claude Code 等 |
| **TTL** | Time To Live | 生存时间,数据有效的持续时间 | 如缓存 TTL 表示缓存过期时间 |
| **Webhook** | Webhook | HTTP 回调机制,用于接收外部事件通知 | 当事件发生时发送 HTTP 请求 |
| **JSONL** | JSON Lines | 每行一个 JSON 对象的文本格式 | 便于流式处理和追加写入 |
| **JSON** | JavaScript Object Notation | 轻量级数据交换格式 | OpenClaw 配置文件使用 JSON |
| **OAuth** | Open Authorization | 开放授权协议,用于第三方应用授权 | 如 Discord Bot 授权 |
| **Token** | Token | 令牌,用于身份验证的字符串 | 如 Discord Bot Token |
| **CLI** | Command Line Interface | 命令行界面 | `openclaw` 命令行工具 |
| **API** | Application Programming Interface | 应用程序编程接口 | 如 Discord API |

### 会话管理特定术语

| 术语 | 定义 | 相关概念 |
|------|------|----------|
| **上下文压缩** (Compaction) | 将旧对话总结为摘要,减少 Token 使用 | Context Window、Token |
| **会话修剪** (Pruning) | 临时移除旧工具结果,减少上下文大小 | Cache、Tool Results |
| **后台任务** (Background Task) | 在主会话外运行的异步任务 | ACP、Subagent、Cron |
| **子代理** (Subagent) | 由主 Agent 生成的独立工作进程 | sessions_spawn |
| **转录** (Transcript) | 会话的完整对话记录 | Session History |
| **沙盒** (Sandbox) | 隔离的执行环境 | 安全限制、权限控制 |
| **空闲超时** (Idle Timeout) | 会话无活动后的过期时间 | Session Reset |
| **上下文窗口** (Context Window) | 模型能处理的最大 Token 数量 | Model Limit |

### 数据单位

| 单位 | 含义 | 换算关系 |
|------|------|----------|
| **Token** | 语言模型处理文本的最小单位 | 英文约 0.75 词,中文约 0.5 字 |
| **d** | 天 (day) | 1d = 24 小时 |
| **h** | 小时 (hour) | 1h = 60 分钟 |
| **m** | 分钟 (minute) | 1m = 60 秒 |
| **s** | 秒 (second) | 基本时间单位 |
| **ms** | 毫秒 (millisecond) | 1ms = 0.001 秒 |
| **MB** | 兆字节 (Megabyte) | 1MB = 1024 KB |

---

## 一、会话基础概念

### 1.1 什么是会话

OpenClaw 将对话组织到**会话(Session)**中。每个消息根据来源被路由到相应的会话:

| 来源 | 行为 |
|------|------|
| 私信(DM) | 默认共享一个主会话 |
| 群组聊天 | 每个群组隔离 |
| 房间/频道 | 每个房间隔离 |
| 定时任务 | 每次运行创建新会话 |
| Webhooks | 每个钩子隔离 |

### 1.2 会话路由规则

OpenClaw 将回复**路由回消息来源的频道**。路由是确定性的,由主机配置控制,而不是由模型选择。

### 1.3 会话键(Session Key)格式

会话键标识对话桶(路由 + 隔离)。常见格式:

| 类型 | Session Key 格式 | 示例 |
|------|------------------|------|
| 主/直接聊天 | `agent:<agentId>:<mainKey>` | `agent:main:main` |
| 群组 | `agent:<agentId>:<channel>:group:<id>` | `agent:main:telegram:group:-1001234567890` |
| 频道/房间 | `agent:<agentId>:<channel>:channel:<id>` | `agent:main:discord:channel:123456` |
| 线程(Slack/Discord) | `...:thread:<threadId>` | `agent:main:discord:channel:123:thread:987654` |
| 话题(Telegram) | `...:topic:<topicId>` | `agent:main:telegram:group:-100123:topic:42` |
| 定时任务 | `cron:<job.id>` | `cron:backup-job` |
| Webhook | `hook:<uuid>` | `hook:a1b2c3d4` |

---

## 二、会话生命周期

### 2.1 会话创建

会话在以下情况下创建:
- 首次向特定会话键发送消息
- 会话被手动重置(`/new` 或 `/reset`)
- 每日重置时间到达(默认凌晨 4:00)
- 空闲超时后收到新消息

### 2.2 会话重置

| 方式 | 说明 |
|------|------|
| **每日重置**(默认) | 在网关主机的本地时间凌晨 4:00 创建新会话 |
| **空闲重置** | 空闲一段时间后创建新会话,设置 `session.reset.idleMinutes` |
| **手动重置** | 聊天中输入 `/new` 或 `/reset`,`/new <model>` 还可切换模型 |

当同时配置每日和空闲重置时,**哪个先到期就执行哪个**。

### 2.3 会话过期

会话状态由**网关**拥有。存储位置:
- **存储**:`~/.openclaw/agents/<agentId>/sessions/sessions.json`
- **转录**:`~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`

### 2.4 会话存储位置

每个代理在网关主机上的存储位置:

| 文件 | 路径 |
|------|------|
| Session Store | `~/.openclaw/agents/<agentId>/sessions/sessions.json` |
| 转录文件 | `~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl` |
| Telegram 话题转录 | `.../<sessionId>-topic-<threadId>.jsonl` |

可通过 `session.store` 和 `{agentId}` 模板覆盖存储路径。

---

## 三、DM 隔离配置

### 3.1 DM 作用域(dmScope)

默认情况下,所有私信共享一个会话以保持连续性。这在单用户设置中没问题,但**多用户访问时需要启用 DM 隔离**。

⚠️ **警告**:如果不启用 DM 隔离,所有用户将共享相同的对话上下文--Alice 的私信对 Bob 可见。

**解决方案**:

```json
{
  "session": {
    // REQUIRED: DM 隔离作用域(默认 "main")
    // "main": 所有 DM 共享一个会话(单用户场景)
    // "per-peer": 按发送者隔离(跨所有频道)
    // "per-channel-peer": 按频道+发送者隔离(推荐,多用户场景)
    // "per-account-channel-peer": 按账户+频道+发送者隔离(最严格)
    "dmScope": "per-channel-peer"
  }
}
```

**dmScope 选项**:

| 选项 | 说明 |
|------|------|
| `main`(默认) | 所有 DM 共享一个会话 |
| `per-peer` | 按发送者隔离(跨频道) |
| `per-channel-peer` | 按频道 + 发送者隔离(推荐) |
| `per-account-channel-peer` | 按账户 + 频道 + 发送者隔离 |

### 3.2 身份链接(identityLinks)

如果同一个人从多个频道联系你,使用 `session.identityLinks` 链接他们的身份,使他们共享一个会话。

```json
{
  "session": {
    // OPTIONAL: 身份链接列表
    // 用于将同一用户的不同渠道身份关联起来
    // 这样用户无论从哪个渠道联系,都使用同一个会话
    "identityLinks": [
      {
        // 该用户的所有标识符列表
        // 格式:user:<channel>:<userId>
        "identifiers": [
          "user:telegram:123456",   // Telegram 用户 ID
          "user:discord:789012",    // Discord 用户 ID
          "user:signal:555666"      // Signal 用户 ID
        ]
      },
      {
        // 可以配置多个用户的身份链接
        "identifiers": [
          "user:telegram:999888",
          "user:discord:777666"
        ]
      }
    ]
  }
}
```

**使用场景**:
- 你在 Telegram 和 Discord 都有 Bot
- 用户张三在 Telegram 的 ID 是 123456,在 Discord 的 ID 是 789012
- 配置 identityLinks 后,张三从任意平台发送消息,都使用同一个会话上下文

使用 `openclaw security audit` 验证你的设置。

---

## 四、上下文压缩(Compaction)

### 4.1 什么是压缩

当对话接近模型的上下文窗口限制时,OpenClaw 将旧消息**压缩**成摘要,以便聊天可以继续。

**工作原理**:
1. 将旧对话轮次总结为紧凑条目
2. 摘要保持保存在会话转录中
3. 保留近期消息不变

### 4.2 自动压缩

自动压缩默认开启。当会话接近上下文限制时触发,或当模型返回上下文溢出错误时(此时 OpenClaw 压缩后重试)。

**溢出错误签名**:
- `request_too_large`
- `context length exceeded`
- `input exceeds the maximum number of tokens`
- `input token count exceeds the maximum number of input tokens`
- `input is too long for the model`
- `ollama error: context length exceeded`

> 💡 **提示**:压缩前,OpenClaw 会自动提醒代理将重要笔记保存到内存文件,防止上下文丢失。

### 4.3 手动压缩

在聊天中输入 `/compact` 强制压缩。可添加指令引导摘要:

```
/compact 重点关注 API 设计决策
```

### 4.4 压缩配置

**基础配置**:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        // REQUIRED: 启用上下文压缩功能
        // 当设为 false 时,不会自动压缩,可能导致上下文溢出错误
        "enabled": true,

        // OPTIONAL: 保留 Token 数量(默认根据模型自动计算)
        // 为提示词和模型输出预留的 Token 空间
        // 值越大,越早触发压缩;值越小,可用上下文越多
        // 建议:对于 128k 上下文模型,设为 16384-32768
        "reserveTokens": 16384,

        // OPTIONAL: 保留的近期消息 Token 数量(默认自动计算)
        // 这部分消息不会被压缩,保持完整上下文
        // 值越大,保留的近期对话越多
        "keepRecentTokens": 20000,

        // OPTIONAL: 是否通知用户压缩发生(默认 false)
        // 设为 true 时,压缩开始会显示提示消息
        "notifyUser": false
      }
    }
  }
}
```

**使用不同模型进行压缩**:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        // OPTIONAL: 专门用于压缩摘要的模型
        // 主模型是本地小模型时,可用更强的模型做摘要
        // 格式:provider/model-id
        "model": "openrouter/anthropic/claude-sonnet-4-6"
      }
    }
  }
}
```

**标识符保留策略**:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        // OPTIONAL: 标识符保留策略(默认 "strict")
        // "strict": 严格保留文件路径、URL、ID 等标识符
        // "off": 不特殊保留,摘要可能省略具体标识符
        // "custom": 自定义保留规则,配合 identifierInstructions 使用
        "identifierPolicy": "strict"
      }
    }
  }
}
```

**完整高级配置示例**:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        // 基础配置
        "enabled": true,
        "reserveTokens": 16384,
        "keepRecentTokens": 20000,
        "notifyUser": false,

        // 模型选择(可选)
        "model": "moonshot/kimi-k2.5",

        // 标识符策略(可选)
        "identifierPolicy": "custom",
        "identifierInstructions": "保留所有 API 端点、数据库表名和错误代码",

        // 内存刷新配置(可选)
        // 压缩前自动保存重要信息到内存文件
        "memoryFlush": {
          "enabled": true,                    // 启用自动内存刷新
          "softThresholdTokens": 4000,        // 软阈值:达到此 Token 数时触发
          "prompt": "请将当前任务的重要上下文和决策保存到内存",  // 刷新提示词
          "systemPrompt": "使用 NO_REPLY 标记静默执行"             // 系统提示词
        }
      }
    }
  }
}
```

### 4.5 压缩 vs 修剪

| 特性 | 压缩(Compaction) | 修剪(Pruning) |
|------|-------------------|----------------|
| **作用** | 总结旧对话 | 修剪旧工具结果 |
| **是否保存** | 是(保存在转录中) | 否(仅内存,每次请求) |
| **范围** | 整个对话 | 仅工具结果 |

它们互补--修剪在压缩周期之间保持工具输出精简。

---

## 五、会话修剪(Session Pruning)

### 5.1 什么是修剪

会话修剪在每次 LLM 调用前**修剪旧工具结果**,减少累积工具输出(执行结果、文件读取、搜索结果)造成的上下文膨胀,而不重写正常对话文本。

> 修剪仅在内存中进行--不会修改磁盘上的会话转录。完整历史始终保留。

### 5.2 修剪工作原理

1. 等待缓存 TTL 过期(默认 5 分钟)
2. 查找要修剪的旧工具结果(对话文本不受影响)
3. **软修剪**超大结果--保留头部和尾部,插入 `...`
4. **硬清除**其余部分--替换为占位符
5. 重置 TTL,后续请求复用新鲜缓存

### 5.3 修剪配置

**启用修剪**:

```json
{
  "agents": {
    "defaults": {
      "contextPruning": {
        // REQUIRED: 修剪模式
        // "cache-ttl": 基于缓存 TTL 修剪(推荐)
        // "off": 禁用修剪
        "mode": "cache-ttl",

        // OPTIONAL: 缓存生存时间(默认 "5m")
        // 格式:数字 + 单位(s=秒, m=分钟, h=小时, d=天)
        // 缓存过期后才触发修剪,减少重复缓存写入
        "ttl": "5m"
      }
    }
  }
}
```

**禁用修剪**:

```json
{
  "agents": {
    "defaults": {
      "contextPruning": {
        "mode": "off"  // 完全禁用修剪功能
      }
    }
  }
}
```

### 5.4 默认配置

OpenClaw 为 Anthropic 配置文件自动启用修剪:

| 配置文件类型 | 修剪启用 | 心跳 |
|-------------|---------|------|
| Anthropic OAuth/Token 认证(包括 Claude CLI 复用) | 是 | 1 小时 |
| API Key | 是 | 30 分钟 |

如果设置了显式值,OpenClaw 不会覆盖它们。

---

## 六、会话工具

### 6.1 工具列表

OpenClaw 为代理提供跨会话工作的工具:

| 工具 | 功能 |
|------|------|
| `sessions_list` | 列出会话(可选按类型、最近活动过滤) |
| `sessions_history` | 读取特定会话的转录 |
| `sessions_send` | 向另一个会话发送消息并可选择等待响应 |
| `sessions_spawn` | 生成隔离的子代理会话用于后台工作 |
| `sessions_yield` | 结束当前轮次并等待后续子代理结果 |
| `subagents` | 列出、引导或终止此会话生成的子代理 |
| `session_status` | 显示 `/status` 样式的状态卡并可选择设置每会话模型覆盖 |

### 6.2 工具如何工作

**重要说明**:

会话工具**不是**在配置文件中配置的,而是 **OpenClaw 自动暴露给 Agent 的工具函数**。Agent 在运行时会根据需要自行决定是否调用这些工具。

**使用方式**:

1. **Agent 自动调用** - 当你在对话中提出需要跨会话操作的需求时,Agent 会自动调用相应工具
2. **用户明确要求** - 你可以在聊天中直接要求 Agent 使用特定工具
3. **通过 CLI** - 部分功能也可以通过 `openclaw` CLI 命令直接使用

**配置可见性范围**(可选):

虽然工具本身不需要配置,但你可以在配置中限制 Agent 能看到哪些会话:

```json
{
  "agents": {
    "defaults": {
      "sessionToolVisibility": "tree"
    }
  }
}
```

选项:`"self"`、`"tree"`(默认)、`"agent"`、`"all"`

### 6.3 工具使用场景示例

**场景 1:查看其他会话状态**

你可以在对话中说:
> "请列出我最近活跃的会话"

Agent 会自动调用 `sessions_list` 工具,然后告诉你结果。

**场景 2:向其他会话发送消息**

> "帮我在 Discord 的 general 频道发送一条消息,说'我会晚点到'"

Agent 会调用 `sessions_send` 工具完成这个操作。

**场景 3:生成子代理处理后台任务**

> "请生成一个子代理来分析这个日志文件,分析完成后告诉我结果"

Agent 会调用 `sessions_spawn` 生成子代理,然后使用 `sessions_yield` 等待结果。

### 6.4 工具参数详解

**列出会话**:

```json
{
  "tool": "sessions_list",
  "params": {
    "kinds": ["main", "group"],
    "activeMinutes": 60
  }
}
```

**读取会话历史**:

```json
{
  "tool": "sessions_history",
  "params": {
    "sessionKey": "agent:main:main",
    "includeTools": true,
    "limit": 50
  }
}
```

**发送跨会话消息**:

```json
{
  "tool": "sessions_send",
  "params": {
    "sessionKey": "agent:main:telegram:group:-1001234567890",
    "message": "请帮我检查这个代码",
    "timeoutSeconds": 30
  }
}
```

**生成子代理**:

```json
{
  "tool": "sessions_spawn",
  "params": {
    "task": "分析这个日志文件并总结错误",
    "runtime": "subagent",
    "model": "moonshot/kimi-k2.5",
    "timeoutSeconds": 300
  }
}
```

**检查子代理状态**:

```json
{
  "tool": "subagents",
  "params": {
    "action": "list"
  }
}
```

### 6.5 工具调用流程

当 Agent 调用会话工具时,流程如下:

```
用户请求 → Agent 分析需求 → 决定调用工具 → OpenClaw 执行工具 → 返回结果 → Agent 处理结果 → 回复用户
```

**实际对话示例**:

**用户**:请帮我查看一下 Telegram 群组里的最新消息

**Agent 思考**:用户想查看 Telegram 群组的消息。我需要:
1. 先列出会话找到 Telegram 群组会话
2. 然后读取该会话的历史

**Agent 调用工具 1**:
```json
{
  "tool": "sessions_list",
  "params": {
    "kinds": ["group"],
    "activeMinutes": 60
  }
}
```

**工具返回**:
```json
{
  "sessions": [
    {
      "sessionKey": "agent:main:telegram:group:-1001234567890",
      "channel": "telegram",
      "lastActivity": "2026-04-16T14:30:00Z"
    }
  ]
}
```

**Agent 调用工具 2**:
```json
{
  "tool": "sessions_history",
  "params": {
    "sessionKey": "agent:main:telegram:group:-1001234567890",
    "limit": 10
  }
}
```

**Agent 回复用户**:
> 我在你的 Telegram 群组中找到了以下最新消息:
> 1. [张三]: 有人能帮我看看这个 bug 吗?
> 2. [李四]: 我来处理,已经修复了
> ...

### 6.6 工具可见性范围

你可以配置 Agent 能看到哪些会话:

| 级别 | 范围 | 说明 |
|------|------|------|
| `self` | 仅当前会话 | Agent 只能操作当前对话 |
| `tree` | 当前会话 + 子代理 | 可以管理当前会话派生的子代理(默认) |
| `agent` | 此代理的所有会话 | 可以操作该代理的所有会话 |
| `all` | 所有会话 | 跨代理访问(需特别配置) |

**配置示例**:

```json
{
  "agents": {
    "defaults": {
      "sessionToolVisibility": "tree"
    }
  }
}
```

默认是 `tree`。沙盒会话无论配置如何都被限制为 `tree`。

**注意事项**:
- 可见性只限制 Agent 能"看到"哪些会话,不影响工具本身的可用性
- 如果你尝试访问超出可见范围的会话,工具会返回权限错误
- 建议保持默认的 `tree` 设置,既安全又足以满足大多数需求

---

## 七、后台任务(Background Tasks)

### 7.1 什么是后台任务

后台任务追踪**在主对话会话外运行**的工作:ACP 运行、子代理生成、隔离定时任务执行和 CLI 启动的操作。

任务**不**替代会话、定时任务或心跳--它们是记录分离工作何时发生、是否成功的**活动账本**。

### 7.2 任务创建场景

| 来源 | 运行时类型 | 何时创建任务记录 | 默认通知策略 |
|------|-----------|-----------------|-------------|
| ACP 后台运行 | `acp` | 生成子 ACP 会话时 | `done_only` |
| 子代理编排 | `subagent` | 通过 `sessions_spawn` 生成子代理时 | `done_only` |
| 定时任务(所有类型) | `cron` | 每次 cron 执行(主会话和隔离) | `silent` |
| CLI 操作 | `cli` | 通过网关运行的 `openclaw agent` 命令 | `silent` |
| 代理媒体作业 | `cli` | 会话支持的 `video_generate` 运行 | `silent` |

**不创建任务的情况**:
- 心跳轮次(主会话)
- 正常交互式聊天轮次
- 直接 `/command` 响应

### 7.3 任务生命周期

```
[*] → queued → running → succeeded
              ↓          → failed
              ↓          → timed_out
              ↓          → cancelled
queued → lost (会话消失 > 5 分钟)
running → lost (会话消失 > 5 分钟)
```

| 状态 | 说明 |
|------|------|
| `queued` | 已创建,等待代理启动 |
| `running` | 代理轮次正在执行 |
| `succeeded` | 成功完成 |
| `failed` | 错误完成 |
| `timed_out` | 超过配置的超时时间 |
| `cancelled` | 操作员通过 `openclaw tasks cancel` 停止 |
| `lost` | 运行时在 5 分钟宽限期后失去权威支持状态 |

### 7.4 任务 CLI 命令

```bash
# 列出所有任务(最新的在前)
openclaw tasks list

# 按运行时或状态过滤
openclaw tasks list --runtime acp
openclaw tasks list --status running

# 显示特定任务的详情(通过 ID、运行 ID 或会话键)
openclaw tasks show <lookup>

# 取消正在运行的任务(终止子会话)
openclaw tasks cancel <lookup>

# 更改任务的通知策略
openclaw tasks notify <lookup> state_changes

# 运行健康审计
openclaw tasks audit

# 预览或应用维护
openclaw tasks maintenance
openclaw tasks maintenance --apply

# 检查 TaskFlow 状态
openclaw tasks flow list
openclaw tasks flow show <lookup>
openclaw tasks flow cancel <lookup>
```

### 7.5 通知策略

| 策略 | 说明 |
|------|------|
| `done_only`(默认) | 仅终端状态(成功、失败等) |
| `state_changes` | 每个状态转换和进度更新 |
| `silent` | 完全不通知 |

更改策略:
```bash
openclaw tasks notify <lookup> state_changes
```

### 7.6 任务与相关系统的关系

| 系统 | 关系 |
|------|------|
| **Task Flow** | Task Flow 是后台任务之上的流程编排层。单个流程可能在其生命周期内协调多个任务 |
| **Cron** | 定时任务定义在 `~/.openclaw/cron/jobs.json` 中。每次 cron 执行都创建任务记录 |
| **Heartbeat** | 心跳运行是主会话轮次--不创建任务记录。任务完成时可以触发心跳唤醒 |
| **Sessions** | 任务可能引用 `childSessionKey`(工作运行处)和 `requesterSessionKey`(启动者) |
| **Agent Runs** | 任务的 `runId` 链接到执行工作的代理运行 |

**存储和保留**:
- 位置:`$OPENCLAW_STATE_DIR/tasks/runs.sqlite`
- 终端记录保留 **7 天**,然后自动修剪
- 清扫器每 60 秒运行一次

**Cron 任务相关配置**:

```json
{
  "cron": {
    // 定时任务会话保留时间(默认 "24h")
    // 超过此时间的隔离 cron 会话会被清理
    // 设为 false 可禁用自动清理
    "sessionRetention": "24h",

    // 运行日志配置
    "runLog": {
      // 单个运行日志文件最大字节数(默认 2_000_000 = 2MB)
      "maxBytes": 2000000,

      // 每个运行日志保留的最大行数(默认 2000)
      "keepLines": 2000
    }
  }
}
```

---

## 八、频道路由

### 8.1 路由规则

OpenClaw 将回复**路由回消息来源的频道**。关键术语:

| 术语 | 说明 |
|------|------|
| **Channel** | `telegram`、`whatsapp`、`discord`、`slack`、`signal` 等 |
| **AccountId** | 每个频道的账户实例(支持时) |
| **AgentId** | 隔离的工作空间 + 会话存储("大脑") |
| **SessionKey** | 用于存储上下文和控制并发的桶键 |

**主 DM 路由固定**:

当 `session.dmScope` 为 `main` 时,为防止会话的 `lastRoute` 被非所有者 DM 覆盖:
- 如果 `allowFrom` 只有一个非通配符条目
- 且该条目可归一化为该频道的具体发送者 ID
- 且入站 DM 发送者与该固定所有者不匹配

OpenClaw 仍记录入站会话元数据,但跳过更新主会话 `lastRoute`。

### 8.2 代理选择流程

路由为每个入站消息选择**一个代理**:

1. **精确对等匹配**(`bindings` 带 `peer.kind` + `peer.id`)
2. **父对等匹配**(线程继承)
3. **Guild + 角色匹配**(Discord)通过 `guildId` + `roles`
4. **Guild 匹配**(Discord)通过 `guildId`
5. **Team 匹配**(Slack)通过 `teamId`
6. **账户匹配**(频道上的 `accountId`)
7. **频道匹配**(该频道的任何账户,`accountId: "*"`)
8. **默认代理**(`agents.list[].default`,否则列表第一项,回退到 `main`)

当绑定包含多个匹配字段(`peer`、`guildId`、`teamId`、`roles`)时,**所有提供的字段必须匹配**该绑定才适用。

### 8.3 广播组

广播组允许你**为同一对等体运行多个代理**:

```json
{
  "broadcast": {
    // REQUIRED: 广播策略
    // "parallel": 并行执行所有代理(默认)
    "strategy": "parallel",

    // 对等体 ID(如 WhatsApp 群组 JID 或手机号)
    // 对应的代理列表,这些代理会同时处理该群组的消息
    "120363403215116621@g.us": ["alfred", "baerbel"],  // WhatsApp 群组
    "+15555550123": ["support", "logger"]              // 特定手机号
  }
}
```

**使用场景**:
- 在一个群组中同时运行 "support" 和 "logger" 两个代理
- 一个负责回复用户,一个负责记录所有对话
- 注意:需要确保代理间不会冲突,或接受多个回复

## 九、会话维护

### 9.1 维护模式

OpenClaw 自动限制会话存储随时间的增长。默认在 `warn` 模式下运行(报告会清理什么)。设置 `session.maintenance.mode` 为 `"enforce"` 以启用自动清理:

```json
{
  "session": {
    "maintenance": {
      // REQUIRED: 维护模式
      // "warn": 仅报告哪些会被清理,不实际删除(默认)
      // "enforce": 实际执行清理操作
      "mode": "enforce",

      // OPTIONAL: 陈旧条目截止时间(默认 "30d")
      // 超过此时间的会话数据会被清理
      // 格式:数字 + 单位(d=天, h=小时, m=分钟, s=秒)
      "pruneAfter": "30d",

      // OPTIONAL: sessions.json 最大条目数(默认 500)
      // 超过后自动清理最旧的条目
      "maxEntries": 500,

      // OPTIONAL: 文件大小阈值(默认 "10mb")
      // sessions.json 超过此大小时自动轮换
      "rotateBytes": "10mb",

      // OPTIONAL: 重置存档保留时间
      // /new 或 /reset 时创建的存档文件保留时间
      // 默认与 pruneAfter 相同,设为 false 可永久保留
      "resetArchiveRetention": "30d",

      // OPTIONAL: 磁盘预算控制(高级)
      "maxDiskBytes": 1073741824,    // 会话目录最大 1GB
      "highWaterBytes": 858993459    // 清理后目标 800MB(默认 maxDiskBytes 的 80%)
    }
  }
}
```

### 9.2 清理命令

```bash
# 预览清理
openclaw sessions cleanup --dry-run

# 执行清理
openclaw sessions cleanup --enforce
```

### 9.3 存储控制

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `mode` | `warn` 或 `enforce` | `warn` |
| `pruneAfter` | 陈旧条目截止时间 | `30d` |
| `maxEntries` | `sessions.json` 条目上限 | `500` |
| `rotateBytes` | 超大时轮换 `sessions.json` | `10mb` |
| `resetArchiveRetention` | 重置存档保留时间 | 同 `pruneAfter` |
| `maxDiskBytes` | 会话目录预算(可选) | - |
| `highWaterBytes` | 清理后目标(默认 `maxDiskBytes` 的 80%) | - |

**Cron 会话和运行日志**:

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `cron.sessionRetention` | 清理旧的隔离 cron 运行会话 | `24h` |
| `cron.runLog.maxBytes` | 运行日志文件大小限制 | `2_000_000` |
| `cron.runLog.keepLines` | 运行日志保留行数 | `2000` |

---

## 十、常用命令速查

| 命令 | 用途 |
|------|------|
| `openclaw status` | 会话存储路径和近期活动 |
| `openclaw sessions --json` | 所有会话(用 `--active <minutes>` 过滤) |
| `/status` | 上下文使用、模型和开关 |
| `/context list` | 系统提示中的内容 |
| `/new` | 开始新会话 |
| `/reset` | 重置当前会话 |
| `/compact` | 手动压缩上下文 |
| `/compact <指令>` | 带指令的手动压缩 |
| `/tasks` | 聊天任务板 |
| `openclaw sessions cleanup --dry-run` | 预览清理 |
| `openclaw sessions cleanup --enforce` | 执行清理 |
| `openclaw security audit` | 验证 DM 隔离设置 |
| `openclaw tasks list` | 列出所有后台任务 |
| `openclaw tasks show <id>` | 显示任务详情 |
| `openclaw tasks cancel <id>` | 取消任务 |
| `openclaw tasks audit` | 运行任务健康审计 |

---

## 十一、完整配置示例

以下是一个生产环境可用的完整配置示例,包含详细的配置说明:

```json
{
  // ============================================
  // 会话级别配置
  // ============================================
  "session": {
    // DM 隔离作用域(默认 "main")
    // "main": 所有私信共享一个会话(适合单用户)
    // "per-peer": 按发送者隔离(跨频道)
    // "per-channel-peer": 按频道+发送者隔离(推荐,适合多用户)
    // "per-account-channel-peer": 按账户+频道+发送者隔离(最严格)
    "dmScope": "per-channel-peer",

    // 会话重置配置
    "reset": {
      // 空闲超时重置(可选)
      // 会话空闲 60 分钟后,下次消息来时创建新会话
      // 设为 0 或删除此项可禁用空闲重置
      "idleMinutes": 60,

      // 每日定时重置(可选)
      // 在网关主机本地时间的凌晨 4:00 重置所有会话
      // 格式:"HH:MM" 24小时制
      "dailyAt": "04:00"
    },

    // 会话存储维护配置
    "maintenance": {
      // 维护模式:"warn" 仅报告,"enforce" 自动清理
      "mode": "enforce",

      // 陈旧条目清理:30 天前的会话数据会被清理
      // 格式:数字 + 单位(d=天, h=小时, m=分钟)
      "pruneAfter": "30d",

      // sessions.json 最大条目数,超过后会清理最旧的
      "maxEntries": 500,

      // 文件大小超过 10MB 时自动轮换 sessions.json
      "rotateBytes": "10mb"
    },

    // 身份链接配置(可选)
    // 将同一用户在不同平台的身份关联起来
    "identityLinks": [
      {
        // 同一用户的所有平台标识符
        // 格式:user:<channel>:<userId>
        "identifiers": [
          "user:telegram:123456789",    // Telegram 用户 ID
          "user:discord:987654321"      // Discord 用户 ID
        ]
      }
    ]
  },

  // ============================================
  // 代理默认配置
  // ============================================
  "agents": {
    "defaults": {
      // 上下文压缩配置
      "compaction": {
        // 启用自动上下文压缩(默认 true)
        "enabled": true,

        // 为提示词和输出预留的 Token 数量
        // 值越大越早触发压缩,建议:128k 模型设为 16384-32768
        "reserveTokens": 16384,

        // 保留的近期消息 Token 数(不被压缩)
        "keepRecentTokens": 20000,

        // 压缩时是否显示通知给用户
        "notifyUser": false,

        // 专门用于压缩摘要的模型(可选)
        // 默认使用主模型,可指定更强的模型做摘要
        "model": "moonshot/kimi-k2.5",

        // 标识符保留策略:"strict" | "off" | "custom"
        // strict: 保留路径、URL、ID 等标识符
        "identifierPolicy": "strict",

        // 压缩前自动内存刷新配置(可选)
        "memoryFlush": {
          // 启用自动保存重要上下文到内存文件
          "enabled": true,
          // 当剩余 Token 数低于此值时触发刷新
          "softThresholdTokens": 4000,
          // 刷新提示词(可选,使用默认即可)
          "prompt": "请将当前任务的重要上下文保存到内存",
          // 刷新时的系统提示词(可选)
          "systemPrompt": "使用 NO_REPLY 标记静默执行"
        }
      },

      // 会话修剪配置
      "contextPruning": {
        // 修剪模式:"cache-ttl" | "off"
        "mode": "cache-ttl",
        // 缓存生存时间,过期后才修剪
        "ttl": "5m"
      }
    }
  },

  // ============================================
  // 代理绑定配置(路由规则)
  // ============================================
  "bindings": [
    {
      // 示例:Telegram 群组绑定到 main 代理
      "match": {
        "channel": "telegram",                    // 频道类型
        "peer": {
          "kind": "group",                        // 对等体类型:group | user
          "id": "-1001234567890"                  // 群组 ID(Telegram 群组通常以 -100 开头)
        }
      },
      "agentId": "main"                           // 使用的代理 ID
    },
    {
      // 示例:Discord 服务器绑定到 main 代理
      "match": {
        "channel": "discord",
        "guildId": "1476767932041138198"         // Discord 服务器(Guild)ID
      },
      "agentId": "main"
    },
    {
      // 示例:Slack 工作区绑定
      "match": {
        "channel": "slack",
        "teamId": "T12345678"                    // Slack Team ID
      },
      "agentId": "main"
    }
  ],

  // ============================================
  // 后台任务配置(可选)
  // ============================================
  "cron": {
    // 定时任务会话保留时间
    "sessionRetention": "24h",
    // 运行日志配置
    "runLog": {
      "maxBytes": 2000000,    // 单个运行日志文件最大 2MB
      "keepLines": 2000       // 保留最近 2000 行日志
    }
  }
}
```

### 配置使用建议

1. **单用户场景**:设置 `"dmScope": "main"`,所有对话共享一个会话
2. **多用户场景**:设置 `"dmScope": "per-channel-peer"`,确保用户间隔离
3. **上下文频繁溢出**:增大 `reserveTokens` 或减小 `keepRecentTokens`
4. **磁盘空间有限**:启用 `maintenance.mode: "enforce"` 并减小 `pruneAfter`
5. **重要对话需要长期保留**:增大 `sessionRetention` 或使用自定义存储路径

---

> **文档版本**：v2.0  
> **最后更新**：2026-04-16  
> **适用版本**：OpenClaw 2026.4.14+
>
> **参考文档**:
> - https://docs.openclaw.ai/concepts/session
> - https://docs.openclaw.ai/concepts/session-pruning
> - https://docs.openclaw.ai/concepts/compaction
> - https://docs.openclaw.ai/concepts/session-tool
> - https://docs.openclaw.ai/reference/session-management-compaction
> - https://docs.openclaw.ai/automation/tasks
> - https://docs.openclaw.ai/channels/channel-routing
