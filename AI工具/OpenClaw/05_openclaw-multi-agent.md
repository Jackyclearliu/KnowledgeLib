---
description: OpenClaw Multi-Agent 配置指南，涵盖多代理架构、路由绑定、多账户管理和沙盒隔离
---
# OpenClaw Multi-Agent 用户手册

> 本文档介绍如何在单个 OpenClaw 网关中运行多个隔离的代理，实现不同人格、不同工作空间、不同频道的独立管理。  
> **适用版本**：OpenClaw 2026.4.14+

---

## 目录

- [OpenClaw Multi-Agent 用户手册](#openclaw-multi-agent-用户手册)
  - [术语表](#术语表)
  - [一、Multi-Agent 概述](#一multi-agent-概述)
    - [1.1 什么是 Multi-Agent](#11-什么是-multi-agent)
    - [1.2 单代理 vs 多代理](#12-单代理-vs-多代理)
    - [1.3 适用场景](#13-适用场景)
  - [二、核心概念](#二核心概念)
    - [2.1 Agent（代理）](#21-agent代理)
    - [2.2 Workspace（工作空间）](#22-workspace工作空间)
    - [2.3 AgentDir（代理目录）](#23-agentdir代理目录)
    - [2.4 AccountId（账户 ID）](#24-accountid账户-id)
    - [2.5 Binding（绑定）](#25-binding绑定)
    - [2.6 路由规则](#26-路由规则)
  - [三、路径映射](#三路径映射)
  - [四、快速开始](#四快速开始)
    - [4.1 使用向导创建代理](#41-使用向导创建代理)
    - [4.2 配置多账户](#42-配置多账户)
    - [4.3 创建绑定规则](#43-创建绑定规则)
    - [4.4 验证配置](#44-验证配置)
  - [五、配置详解](#五配置详解)
    - [5.1 agents.list 配置](#51-agentslist-配置)
    - [5.2 bindings 配置](#52-bindings-配置)
    - [5.3 多账户配置](#53-多账户配置)
    - [5.4 沙盒与工具配置](#54-沙盒与工具配置)
  - [六、常见场景](#六常见场景)
    - [场景1：Discord 多机器人](#场景1discord-多机器人)
    - [场景2：Telegram 多机器人](#场景2telegram-多机器人)
    - [场景3：WhatsApp 多号码](#场景3whatsapp-多号码)
    - [场景4：按渠道分配代理](#场景4按渠道分配代理)
    - [场景5：特定对话路由到特定代理](#场景5特定对话路由到特定代理)
    - [场景6：家庭群组专用代理](#场景6家庭群组专用代理)
  - [七、跨代理功能](#七跨代理功能)
    - [7.1 跨代理内存搜索](#71-跨代理内存搜索)
    - [7.2 代理间消息传递](#72-代理间消息传递)
  - [八、CLI 命令速查](#八cli-命令速查)
  - [九、完整配置示例](#九完整配置示例)

---

## 术语表

| 术语 | 英文 | 定义 | 说明 |
|------|------|------|------|
| **代理** | Agent | 具有独立工作空间、配置和会话的 AI 实例 | 每个代理有自己的"大脑"和"人格" |
| **工作空间** | Workspace | 代理的文件存储目录，包含 SOUL.md、AGENTS.md 等 | 代理的"家目录" |
| **代理目录** | AgentDir | 存储代理认证配置和状态的位置 | 通常在工作空间下的 `agent/` 子目录 |
| **绑定** | Binding | 将入站消息路由到特定代理的规则 | 决定哪个代理处理哪条消息 |
| **对等体** | Peer | 消息的发送者或群组 | 可以是个人、群组或频道 |
| **账户 ID** | AccountId | 频道账户的标识符 | 例如不同的 WhatsApp 号码或 Discord Bot |
| **路由** | Routing | 消息从入站到分配给代理的过程 | 基于绑定规则进行 |
| **沙盒** | Sandbox | 隔离的执行环境 | 限制代理的操作权限 |
| **广播组** | Broadcast Group | 将同一消息发送给多个代理的机制 | 用于多代理同时处理 |
| **E.164** | E.164 | 国际电话号码格式 | 如 `+8613800138000` |
| **会话隔离** | Session Isolation | 不同代理的会话相互独立 | 一个代理无法访问另一个代理的会话 |

---

## 一、Multi-Agent 概述

### 1.1 什么是 Multi-Agent

**Multi-Agent** 允许在单个 OpenClaw 网关中运行**多个完全隔离的代理**。每个代理拥有：

- **独立的工作空间**（文件、配置、人格规则）
- **独立的代理目录**（认证配置、模型注册表）
- **独立的会话存储**（聊天记录、路由状态）
- **独立的认证信息**（不同 Bot Token、不同账号）

### 1.2 单代理 vs 多代理

| 特性 | 单代理模式（默认） | 多代理模式 |
|------|------------------|-----------|
| 代理数量 | 1 个（默认 `main`） | 多个 |
| 工作空间 | `~/.openclaw/workspace` | `~/.openclaw/workspace-<agentId>` |
| 会话键 | `agent:main:*` | `agent:<agentId>:*` |
| 适用场景 | 个人使用 | 多人共享、不同场景隔离 |
| 配置复杂度 | 简单 | 较复杂 |

### 1.3 适用场景

1. **多人共享一个网关**：家庭成员各自有独立的 AI 助手
2. **不同场景隔离**：工作代理和私人代理完全分开
3. **不同模型适配**：简单聊天用轻量级模型，复杂任务用强模型
4. **不同人格设定**：客服代理、编程代理、生活助手各有不同角色
5. **安全隔离**：敏感操作代理运行在沙盒中，普通代理不限制

---

## 二、核心概念

### 2.1 Agent（代理）

代理是一个**完全隔离的"大脑"**，包含：

- **Workspace**：文件、AGENTS.md、SOUL.md、USER.md
- **AgentDir**：`~/.openclaw/agents/<agentId>/agent`，存储认证配置
- **Session Store**：`~/.openclaw/agents/<agentId>/sessions`，聊天记录

**重要**：代理之间**不共享认证信息**。如需共享凭证，需手动复制 `auth-profiles.json`。

### 2.2 Workspace（工作空间）

每个代理的默认工作目录：

```
~/.openclaw/workspace-<agentId>/
├── AGENTS.md      # 代理行为规范
├── SOUL.md        # 代理人格设定
├── USER.md        # 用户信息（可选）
├── TOOLS.md       # 工具配置（可选）
└── ...            # 其他文件
```

**注意**：工作空间是**默认 cwd**，不是硬沙盒。相对路径在工作空间内解析，但绝对路径可以访问主机其他位置（除非启用沙盒）。

### 2.3 AgentDir（代理目录）

存储代理特定配置：

```
~/.openclaw/agents/<agentId>/agent/
├── auth-profiles.json    # 认证配置（API Keys、Tokens）
└── ...                   # 其他代理级配置
```

**永远不要**在多个代理间共享 `agentDir`，会导致认证和会话冲突。

### 2.4 AccountId（账户 ID）

用于区分同一频道的多个账户：

- **WhatsApp**：`personal`、`biz` 对应不同手机号
- **Discord**：`default`、`coding` 对应不同 Bot
- **Telegram**：`main`、`alerts` 对应不同 Bot

每个 `accountId` 可以路由到不同的代理。

### 2.5 Binding（绑定）

绑定是**路由规则**，决定入站消息由哪个代理处理：

```json
{
  "agentId": "work",
  "match": {
    "channel": "whatsapp",
    "accountId": "biz"
  }
}
```

### 2.6 路由规则

路由是**确定性的**，采用**最具体匹配优先**策略：

| 优先级 | 匹配类型 | 说明 |
|-------|---------|------|
| 1 | `peer` | 精确匹配 DM/群组/频道 ID |
| 2 | `parentPeer` | 线程继承 |
| 3 | `guildId + roles` | Discord 角色路由 |
| 4 | `guildId` | Discord 服务器 |
| 5 | `teamId` | Slack 工作区 |
| 6 | `accountId` | 频道账户 |
| 7 | `accountId: "*"` | 频道级回退 |
| 8 | 默认代理 | `agents.list[].default` 或 `main` |

**规则**：
- 同优先级下，配置文件中**先出现的绑定优先**
- 绑定可设置多个匹配字段（如 `peer` + `guildId`），**所有字段必须同时匹配**（AND 逻辑）
- 省略 `accountId` 的绑定**仅匹配默认账户**
- 使用 `accountId: "*"` 匹配该频道**所有账户**

---

## 三、路径映射

```
~/.openclaw/                                    # 状态目录（或 OPENCLAW_STATE_DIR）
├── openclaw.json                               # 主配置文件
├── agents/
│   ├── <agentId>/
│   │   ├── agent/                              # 代理目录（agentDir）
│   │   │   └── auth-profiles.json             # 代理级认证配置
│   │   └── sessions/                           # 会话存储
│   │       ├── sessions.json                  # 会话元数据
│   │       └── <sessionId>.jsonl              # 会话转录
│   └── ...
├── workspace/                                  # 默认工作空间（单代理模式）
├── workspace-<agentId>/                        # 多代理工作空间
└── ...
```

---

## 四、快速开始

### 4.1 使用向导创建代理

```bash
# 添加新代理
openclaw agents add work

# 查看所有代理和绑定
openclaw agents list --bindings
```

### 4.2 配置多账户

**Discord**：
1. 为每个代理创建独立的 Discord Bot
2. 在 Discord Developer Portal 启用 Message Content Intent
3. 复制每个 Bot 的 Token

**Telegram**：
1. 通过 BotFather 为每个代理创建 Bot
2. 复制每个 Bot 的 Token

**WhatsApp**：
```bash
# 登录多个 WhatsApp 账号
openclaw channels login --channel whatsapp --account personal
openclaw channels login --channel whatsapp --account biz
```

### 4.3 创建绑定规则

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "agents": {
    "list": [
      { "id": "home", "workspace": "~/.openclaw/workspace-home" },
      { "id": "work", "workspace": "~/.openclaw/workspace-work" }
    ]
  },
  "bindings": [
    { "agentId": "home", "match": { "channel": "whatsapp", "accountId": "personal" } },
    { "agentId": "work", "match": { "channel": "whatsapp", "accountId": "biz" } }
  ]
}
```

### 4.4 验证配置

```bash
# 重启网关
openclaw gateway restart

# 查看代理列表
openclaw agents list --bindings

# 检查频道状态
openclaw channels status --probe
```

---

## 五、配置详解

### 5.1 agents.list 配置

```json
{
  "agents": {
    "list": [
      {
        // REQUIRED: 代理唯一标识符
        // 只能包含字母、数字、连字符
        "id": "work",
        
        // OPTIONAL: 是否为默认代理
        // 当没有绑定匹配时，使用默认代理
        "default": true,
        
        // OPTIONAL: 显示名称
        "name": "Work Assistant",
        
        // OPTIONAL: 工作空间路径
        // 默认：~/.openclaw/workspace-<agentId>
        "workspace": "~/.openclaw/workspace-work",
        
        // OPTIONAL: 代理目录路径
        // 默认：~/.openclaw/agents/<agentId>/agent
        "agentDir": "~/.openclaw/agents/work/agent",
        
        // OPTIONAL: 使用的模型
        "model": "anthropic/claude-sonnet-4-6",
        
        // OPTIONAL: 人格设定
        "identity": {
          "name": "Work Bot",
          "emoji": "💼"
        },
        
        // OPTIONAL: 群组聊天配置
        "groupChat": {
          // 提及模式，用于触发该代理
          "mentionPatterns": ["@work", "@workbot"]
        }
      }
    ]
  }
}
```

### 5.2 bindings 配置

```json
{
  "bindings": [
    {
      // REQUIRED: 目标代理 ID
      "agentId": "work",
      
      // REQUIRED: 匹配条件
      "match": {
        // REQUIRED: 频道类型
        "channel": "whatsapp",
        
        // OPTIONAL: 账户 ID
        // 省略则匹配默认账户
        // "*" 匹配所有账户
        "accountId": "biz",
        
        // OPTIONAL: 对等体匹配（最优先）
        "peer": {
          // "direct" = 私信, "group" = 群组
          "kind": "group",
          // 群组 ID 或用户 ID
          "id": "120363999999999999@g.us"
        },
        
        // OPTIONAL: Discord 服务器 ID
        "guildId": "123456789012345678",
        
        // OPTIONAL: Discord 角色 ID 列表
        "roles": ["111111111111111111"],
        
        // OPTIONAL: Slack Team ID
        "teamId": "T12345678"
      }
    }
  ]
}
```

### 5.3 多账户配置

**Discord 多 Bot**：

```json
{
  "channels": {
    "discord": {
      // 可选：默认账户（当绑定省略 accountId 时使用）
      "defaultAccount": "default",
      
      "accounts": {
        "default": {
          // Bot Token（或使用环境变量 DISCORD_BOT_TOKEN）
          "token": "MTQ3Njg2OTIxNTQ5ODUzOTEyNQ.xxxxxx.xxxxxxxxxxx",
          
          // 服务器配置
          "guilds": {
            "123456789012345678": {
              "channels": {
                "222222222222222222": {
                  "allow": true,
                  "requireMention": false
                }
              }
            }
          }
        },
        "coding": {
          "token": "ANOTHER_BOT_TOKEN_HERE",
          "guilds": {
            "123456789012345678": {
              "channels": {
                "333333333333333333": {
                  "allow": true,
                  "requireMention": false
                }
              }
            }
          }
        }
      }
    }
  }
}
```

**Telegram 多 Bot**：

```json
{
  "channels": {
    "telegram": {
      "accounts": {
        "default": {
          "botToken": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
          "dmPolicy": "pairing"
        },
        "alerts": {
          "botToken": "987654:XYZ-ABC5678defGHI-jkl90M3n2o456pq77",
          "dmPolicy": "allowlist",
          "allowFrom": ["tg:123456789"]
        }
      }
    }
  }
}
```

**WhatsApp 多号码**：

```json
{
  "channels": {
    "whatsapp": {
      "accounts": {
        "personal": {
          // 可选：自定义认证目录
          // 默认：~/.openclaw/credentials/whatsapp/personal
          "authDir": "~/.openclaw/credentials/whatsapp/personal"
        },
        "biz": {
          "authDir": "~/.openclaw/credentials/whatsapp/biz"
        }
      }
    }
  }
}
```

### 5.4 沙盒与工具配置

```json
{
  "agents": {
    "list": [
      {
        "id": "personal",
        "workspace": "~/.openclaw/workspace-personal",
        
        // 沙盒配置
        "sandbox": {
          // 模式："off" | "all" | "write" | "exec"
          // "off": 无沙盒（默认）
          // "all": 所有操作都沙盒化
          // "write": 仅写操作沙盒化
          // "exec": 仅执行操作沙盒化
          "mode": "off"
          // 无沙盒，所有工具可用
        }
      },
      {
        "id": "family",
        "workspace": "~/.openclaw/workspace-family",
        
        "sandbox": {
          "mode": "all",        // 所有操作都沙盒化
          "scope": "agent",     // 每个代理独立容器（"shared" = 共享容器）
          
          // Docker 特定配置（可选）
          "docker": {
            // 容器创建后执行的一次性设置命令
            "setupCommand": "apt-get update && apt-get install -y git curl"
          }
        },
        
        // 工具权限配置
        "tools": {
          // 白名单模式：仅允许列表中的工具
          "allow": [
            "read",           // 读取文件
            "exec",           // 执行命令
            "sessions_list",  // 会话列表
            "sessions_history", // 会话历史
            "sessions_send",  // 发送消息
            "sessions_spawn", // 生成子代理
            "session_status"  // 会话状态
          ],
          
          // 黑名单模式：明确禁止的工具
          "deny": [
            "write",          // 禁止写入文件
            "edit",           // 禁止编辑文件
            "apply_patch",    // 禁止应用补丁
            "browser",        // 禁止浏览器操作
            "canvas",         // 禁止 Canvas 操作
            "nodes",          // 禁止节点操作
            "cron"            // 禁止定时任务
          ]
        }
      }
    ]
  }
}
```

**注意**：
- `tools.allow` 和 `tools.deny` 是**工具级别**的，不是 skill 级别
- 如果 skill 需要执行二进制文件，确保 `exec` 已允许且二进制文件存在于沙盒中
- `setupCommand` 仅在 `sandbox.docker` 下有效，且仅在容器创建时执行一次
- `tools.elevated` 是**全局**的，不能按代理配置

---

## 六、常见场景

### 场景1：Discord 多机器人

```json
{
  "agents": {
    "list": [
      { "id": "main", "workspace": "~/.openclaw/workspace-main" },
      { "id": "coding", "workspace": "~/.openclaw/workspace-coding" }
    ]
  },
  "bindings": [
    { "agentId": "main", "match": { "channel": "discord", "accountId": "default" } },
    { "agentId": "coding", "match": { "channel": "discord", "accountId": "coding" } }
  ],
  "channels": {
    "discord": {
      "groupPolicy": "allowlist",
      "accounts": {
        "default": {
          "token": "DISCORD_BOT_TOKEN_MAIN",
          "guilds": {
            "123456789012345678": {
              "channels": {
                "222222222222222222": { "allow": true }
              }
            }
          }
        },
        "coding": {
          "token": "DISCORD_BOT_TOKEN_CODING",
          "guilds": {
            "123456789012345678": {
              "channels": {
                "333333333333333333": { "allow": true }
              }
            }
          }
        }
      }
    }
  }
}
```

### 场景2：Telegram 多机器人

```json
{
  "agents": {
    "list": [
      { "id": "main", "workspace": "~/.openclaw/workspace-main" },
      { "id": "alerts", "workspace": "~/.openclaw/workspace-alerts" }
    ]
  },
  "bindings": [
    { "agentId": "main", "match": { "channel": "telegram", "accountId": "default" } },
    { "agentId": "alerts", "match": { "channel": "telegram", "accountId": "alerts" } }
  ],
  "channels": {
    "telegram": {
      "accounts": {
        "default": {
          "botToken": "123456:ABC...",
          "dmPolicy": "pairing"
        },
        "alerts": {
          "botToken": "987654:XYZ...",
          "dmPolicy": "allowlist",
          "allowFrom": ["tg:123456789"]
        }
      }
    }
  }
}
```

### 场景3：WhatsApp 多号码

```bash
# 先登录多个账号
openclaw channels login --channel whatsapp --account personal
openclaw channels login --channel whatsapp --account biz
```

```json
{
  "agents": {
    "list": [
      {
        "id": "home",
        "default": true,
        "workspace": "~/.openclaw/workspace-home"
      },
      {
        "id": "work",
        "workspace": "~/.openclaw/workspace-work"
      }
    ]
  },
  "bindings": [
    { "agentId": "home", "match": { "channel": "whatsapp", "accountId": "personal" } },
    { "agentId": "work", "match": { "channel": "whatsapp", "accountId": "biz" } }
  ]
}
```

### 场景4：按渠道分配代理

WhatsApp 用轻量级模型快速回复，Telegram 用强模型深度处理：

```json
{
  "agents": {
    "list": [
      {
        "id": "chat",
        "name": "Everyday",
        "workspace": "~/.openclaw/workspace-chat",
        "model": "anthropic/claude-sonnet-4-6"
      },
      {
        "id": "opus",
        "name": "Deep Work",
        "workspace": "~/.openclaw/workspace-opus",
        "model": "anthropic/claude-opus-4-6"
      }
    ]
  },
  "bindings": [
    { "agentId": "chat", "match": { "channel": "whatsapp" } },
    { "agentId": "opus", "match": { "channel": "telegram" } }
  ]
}
```

### 场景5：特定对话路由到特定代理

WhatsApp 大部分用轻量代理，但某个重要联系人用强代理：

```json
{
  "agents": {
    "list": [
      {
        "id": "chat",
        "model": "anthropic/claude-sonnet-4-6"
      },
      {
        "id": "opus",
        "model": "anthropic/claude-opus-4-6"
      }
    ]
  },
  "bindings": [
    // 特定联系人优先（peer 匹配优先级最高）
    {
      "agentId": "opus",
      "match": {
        "channel": "whatsapp",
        "peer": { "kind": "direct", "id": "+15551234567" }
      }
    },
    // 其他所有 WhatsApp 用轻量代理
    { "agentId": "chat", "match": { "channel": "whatsapp" } }
  ]
}
```

### 场景6：家庭群组专用代理

```json
{
  "agents": {
    "list": [
      {
        "id": "family",
        "name": "Family",
        "workspace": "~/.openclaw/workspace-family",
        "identity": { "name": "Family Bot" },
        "groupChat": {
          "mentionPatterns": ["@family", "@familybot"]
        },
        "sandbox": {
          "mode": "all",
          "scope": "agent"
        },
        "tools": {
          "allow": ["read", "exec", "sessions_list", "sessions_history"],
          "deny": ["write", "edit", "browser", "cron"]
        }
      }
    ]
  },
  "bindings": [
    {
      "agentId": "family",
      "match": {
        "channel": "whatsapp",
        "peer": { "kind": "group", "id": "120363999999999999@g.us" }
      }
    }
  ]
}
```

---

## 七、跨代理功能

### 7.1 跨代理内存搜索

配置一个代理搜索另一个代理的会话转录：

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "qmd": {
          // 额外的搜索集合
          "extraCollections": [
            { "path": "~/agents/family/sessions", "name": "family-sessions" }
          ]
        }
      }
    },
    "list": [
      {
        "id": "main",
        "memorySearch": {
          "qmd": {
            "extraCollections": [
              { "path": "notes" }  // 解析为 "notes-main"
            ]
          }
        }
      },
      { "id": "family" }
    ]
  },
  "memory": {
    "backend": "qmd",
    "qmd": { "includeDefaultMemory": false }
  }
}
```

**说明**：
- 工作空间外的路径需要显式命名集合
- 工作空间内的路径自动命名为 `<path>-<agentId>`
- 代理自己的转录搜索集保持独立

### 7.2 代理间消息传递

默认禁用，需显式启用：

```json
{
  "tools": {
    "agentToAgent": {
      // 启用代理间消息传递
      "enabled": true,
      // 允许通信的代理白名单
      "allow": ["home", "work"]
    }
  }
}
```

---

## 八、CLI 命令速查

| 命令 | 用途 | 示例 |
|------|------|------|
| `openclaw agents add <id>` | 添加新代理 | `openclaw agents add work` |
| `openclaw agents list` | 列出所有代理 | `openclaw agents list --bindings` |
| `openclaw agents remove <id>` | 删除代理 | `openclaw agents remove work` |
| `openclaw channels login` | 登录频道账户 | `openclaw channels login --channel whatsapp --account biz` |
| `openclaw channels logout` | 登出频道账户 | `openclaw channels logout --channel whatsapp --account biz` |
| `openclaw channels status` | 检查频道状态 | `openclaw channels status --probe` |
| `openclaw gateway restart` | 重启网关 | `openclaw gateway restart` |
| `openclaw config list` | 查看配置 | `openclaw config list` |
| `openclaw config get <path>` | 获取配置项 | `openclaw config get agents.list` |
| `openclaw config set <path> <value>` | 设置配置项 | `openclaw config set agents.list.0.model "moonshot/kimi-k2.5"` |

---

## 九、完整配置示例

```json
{
  // ============================================
  // 代理定义
  // ============================================
  "agents": {
    "list": [
      {
        "id": "home",
        "default": true,
        "name": "Home Assistant",
        "workspace": "~/.openclaw/workspace-home",
        "agentDir": "~/.openclaw/agents/home/agent",
        "model": "anthropic/claude-sonnet-4-6",
        "identity": {
          "name": "Home Bot",
          "emoji": "🏠"
        },
        "sandbox": {
          "mode": "off"
        }
      },
      {
        "id": "work",
        "name": "Work Assistant",
        "workspace": "~/.openclaw/workspace-work",
        "agentDir": "~/.openclaw/agents/work/agent",
        "model": "anthropic/claude-opus-4-6",
        "identity": {
          "name": "Work Bot",
          "emoji": "💼"
        },
        "groupChat": {
          "mentionPatterns": ["@work", "@workbot"]
        },
        "sandbox": {
          "mode": "write",
          "scope": "agent"
        },
        "tools": {
          "deny": ["nodes", "cron"]
        }
      },
      {
        "id": "family",
        "name": "Family Bot",
        "workspace": "~/.openclaw/workspace-family",
        "model": "moonshot/kimi-k2.5",
        "identity": {
          "name": "Family",
          "emoji": "👨‍👩‍👧‍👦"
        },
        "sandbox": {
          "mode": "all",
          "scope": "agent",
          "docker": {
            "setupCommand": "apt-get update && apt-get install -y curl"
          }
        },
        "tools": {
          "allow": ["read", "exec", "sessions_list"],
          "deny": ["write", "edit", "browser"]
        }
      }
    ]
  },

  // ============================================
  // 路由绑定
  // ============================================
  "bindings": [
    // WhatsApp 路由
    { "agentId": "home", "match": { "channel": "whatsapp", "accountId": "personal" } },
    { "agentId": "work", "match": { "channel": "whatsapp", "accountId": "biz" } },
    
    // Discord 路由
    { "agentId": "home", "match": { "channel": "discord", "accountId": "default" } },
    { "agentId": "work", "match": { "channel": "discord", "accountId": "work" } },
    
    // Telegram 路由
    { "agentId": "home", "match": { "channel": "telegram", "accountId": "default" } },
    
    // 特定群组路由
    {
      "agentId": "family",
      "match": {
        "channel": "whatsapp",
        "peer": { "kind": "group", "id": "120363999999999999@g.us" }
      }
    },
    
    // 特定联系人路由（高优先级）
    {
      "agentId": "work",
      "match": {
        "channel": "whatsapp",
        "accountId": "personal",
        "peer": { "kind": "direct", "id": "+15551234567" }
      }
    }
  ],

  // ============================================
  // 频道账户配置
  // ============================================
  "channels": {
    "whatsapp": {
      "accounts": {
        "personal": {},
        "biz": {}
      }
    },
    "discord": {
      "defaultAccount": "default",
      "accounts": {
        "default": {
          "token": { "source": "env", "id": "DISCORD_BOT_TOKEN_HOME" },
          "guilds": {
            "123456789012345678": {
              "channels": {
                "111111111111111111": { "allow": true }
              }
            }
          }
        },
        "work": {
          "token": { "source": "env", "id": "DISCORD_BOT_TOKEN_WORK" },
          "guilds": {
            "123456789012345678": {
              "channels": {
                "222222222222222222": { "allow": true }
              }
            }
          }
        }
      }
    },
    "telegram": {
      "accounts": {
        "default": {
          "botToken": { "source": "env", "id": "TELEGRAM_BOT_TOKEN" },
          "dmPolicy": "pairing"
        }
      }
    }
  },

  // ============================================
  // 代理间通信（可选）
  // ============================================
  "tools": {
    "agentToAgent": {
      // 启用代理间消息传递（默认 false）
      "enabled": false,
      // 允许通信的代理列表
      "allow": ["home", "work"]
    }
  },

  // ============================================
  // 内存搜索配置（可选）
  // ============================================
  "memory": {
    "backend": "qmd",
    "qmd": {
      "includeDefaultMemory": false
    }
  }
}
```

---

> **文档版本**: v1.0  
> **最后更新**: 2026-04-16  
> **适用版本**: OpenClaw 2026.4.14+  
>  
> **参考文档**:
> - https://docs.openclaw.ai/concepts/multi-agent
> - https://docs.openclaw.ai/channels/channel-routing
> - https://docs.openclaw.ai/concepts/session
> - https://docs.openclaw.ai/tools/multi-agent-sandbox-tools