---
description: 记录 OpenClaw 接入 Discord Bot 的完整流程、配置详解、常见问题及解决方案（基于 2026.4.14 版本）
---

# OpenClaw Discord 接入手册

> 本文档记录 OpenClaw 接入 Discord Bot 的完整流程、配置详解、常见问题及解决方案。  
> **适用版本**：OpenClaw 2026.4.14+

---

## 目录

- [OpenClaw Discord 接入手册](#openclaw-discord-接入手册)
  - [目录](#目录)
  - [一、前置准备](#一前置准备)
  - [二、Discord Bot 创建与配置](#二discord-bot-创建与配置)
    - [2.1 创建 Discord Application](#21-创建-discord-application)
    - [2.2 配置 Bot 权限](#22-配置-bot-权限)
    - [2.3 获取 Bot Token](#23-获取-bot-token)
    - [2.4 邀请 Bot 加入服务器](#24-邀请-bot-加入服务器)
  - [三、OpenClaw 配置](#三openclaw-配置)
    - [3.1 配置 Discord Token](#31-配置-discord-token)
    - [3.2 配置访问控制](#32-配置访问控制)
    - [3.3 完整配置示例](#33-完整配置示例)
    - [3.4 重启 Gateway](#34-重启-gateway)
  - [四、配置项详解](#四配置项详解)
    - [4.1 启动与认证字段](#41-启动与认证字段)
    - [4.2 DM（私聊）策略](#42-dm私聊策略)
    - [4.3 Guild（服务器）策略](#43-guild服务器策略)
    - [4.4 频道级配置（guilds.&lt;id&gt;.channels）](#44-频道级配置guildsidchannels)
    - [4.5 消息与交互字段](#45-消息与交互字段)
    - [4.6 流式传输字段](#46-流式传输字段)
    - [4.7 命令与指令字段](#47-命令与指令字段)
    - [4.8 事件队列与工作者字段](#48-事件队列与工作者字段)
    - [4.9 媒体与重试字段](#49-媒体与重试字段)
    - [4.10 动作权限门（actions）](#410-动作权限门actions)
    - [4.11 在线状态与 UI 字段](#411-在线状态与-ui-字段)
    - [4.12 线程绑定（threadBindings）](#412-线程绑定threadbindings)
    - [4.13 语音频道（voice）](#413-语音频道voice)
    - [4.14 执行审批（execApprovals）](#414-执行审批execapprovals)
    - [4.15 其他功能字段](#415-其他功能字段)
  - [五、Bindings（顶层路由关联）](#五bindings顶层路由关联)
  - [六、常见配置场景](#六常见配置场景)
    - [场景1：仅允许特定用户访问](#场景1仅允许特定用户访问)
    - [场景2：私有服务器自动响应](#场景2私有服务器自动响应)
    - [场景3：多账户配置](#场景3多账户配置)
    - [场景4：语音频道接入](#场景4语音频道接入)
  - [七、常见问题与解决方案](#七常见问题与解决方案)
    - [问题1：Failed to resolve Discord application id](#问题1failed-to-resolve-discord-application-id)
    - [问题2：Connection reset by peer](#问题2connection-reset-by-peer)
    - [问题3：Message Content Intent 未启用](#问题3message-content-intent-未启用)
    - [问题4：配置验证失败 - must NOT have additional properties](#问题4配置验证失败---must-not-have-additional-properties)
  - [八、验证连接](#八验证连接)
  - [九、配对流程](#九配对流程)
  - [十、常用命令速查](#十常用命令速查)
  - [十一、完整配置参考](#十一完整配置参考)
  - [十二、已废弃/不合法的字段（避免踩坑）](#十二已废弃不合法的字段避免踩坑)

---

## 一、前置准备

在开始接入前，请确保以下环境已准备就绪：

| 组件 | 要求 |
|------|------|
| OpenClaw | 已安装并运行 Gateway（2026.4.14+） |
| Discord 账号 | 已注册并验证 |
| 网络环境 | 可访问 Discord（国内需要代理） |
| 代理工具 | Clash / ClashX Pro（推荐） |

---

## 二、Discord Bot 创建与配置

### 2.1 创建 Discord Application

1. 访问 [Discord Developer Portal](https://discord.com/developers/applications)
2. 点击右上角 **"New Application"**
3. 输入应用名称（如：OpenClaw），点击创建

### 2.2 配置 Bot 权限

在左侧菜单选择 **"Bot"**，进行以下配置：

**Privileged Gateway Intents（必须全部启用）：**

| Intent | 说明 | 必需 |
|--------|------|------|
| Message Content Intent | **接收消息内容（关键）** | ✅ 是 |
| Server Members Intent | 接收成员变动事件 | 推荐 |
| Presence Intent | 接收在线状态更新 | 可选 |

> ⚠️ **注意**：Message Content Intent 是 Bot 能读取私信内容的必要权限，必须启用！

**Authorization Flow：**
- ✅ Public Bot：允许其他人添加 Bot
- ⬜ Requires OAuth2 Code Grant：一般不需要

### 2.3 获取 Bot Token

在 Bot 页面点击 **"Reset Token"**，复制生成的新 Token。

> 🔐 **安全提示**：Token 只显示一次，请妥善保存，不要泄露给他人。

### 2.4 邀请 Bot 加入服务器

1. 进入 **OAuth2 > URL Generator**
2. 勾选以下 Scope：
   - `bot`
   - `applications.commands`（用于斜杠命令）
3. 勾选 Bot 权限：
   - View Channels
   - Send Messages
   - Read Message History
   - Embed Links
   - Attach Files
   - Add Reactions（可选）
   - Connect + Speak（如果使用语音）
4. 复制生成的 URL，在浏览器中打开，选择要添加的服务器

---

## 三、OpenClaw 配置

### 3.1 配置 Discord Token

**方式一：使用环境变量（推荐，更安全）**

```bash
# 设置环境变量
export DISCORD_BOT_TOKEN="你的BotToken"

# 配置 OpenClaw 引用环境变量
openclaw config set channels.discord.token \
  --ref-provider default \
  --ref-source env \
  --ref-id DISCORD_BOT_TOKEN

openclaw config set channels.discord.enabled true --strict-json
```

**方式二：直接配置（仅本地测试）**

```bash
openclaw config set channels.discord.token "你的BotToken"
openclaw config set channels.discord.enabled true
```

### 3.2 配置访问控制

**基础访问控制示例：**

```bash
# 设置群组策略为白名单模式
openclaw config set channels.discord.groupPolicy "allowlist"

# 配置允许访问的 Guild（服务器）
openclaw config set channels.discord.guilds."<GUILD_ID>".requireMention false
openclaw config set channels.discord.guilds."<GUILD_ID>".users '["<USER_ID>"]'
```

### 3.3 完整配置示例

**最小可用配置：**

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": {
        "source": "env",
        "provider": "default",
        "id": "DISCORD_BOT_TOKEN"
      },
      "groupPolicy": "allowlist",
      "guilds": {
        "1476767932041138198": {
          "requireMention": false,
          "users": ["1087662067332419655"]
        }
      }
    }
  }
}
```

**生产环境推荐配置：**

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": {
        "source": "env",
        "provider": "default",
        "id": "DISCORD_BOT_TOKEN"
      },
      "groupPolicy": "allowlist",
      "dmPolicy": "pairing",
      "streaming": "off",
      "historyLimit": 20,
      "dmHistoryLimit": 20,
      "maxLinesPerMessage": 17,
      "replyToMode": "off",
      "status": "online",
      "activity": "OpenClaw Ready",
      "activityType": 4,
      "guilds": {
        "1476767932041138198": {
          "requireMention": false,
          "ignoreOtherMentions": true,
          "users": ["1087662067332419655"],
          "channels": {
            "general": { "allow": true },
            "coding": { "allow": true, "requireMention": true }
          }
        }
      }
    }
  }
}
```

### 3.4 重启 Gateway

配置完成后必须重启 Gateway：

```bash
openclaw gateway restart
```

查看日志确认连接状态：

```bash
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep discord
```

成功连接后应看到类似日志：
```
[default] gateway ready
```

---

## 四、配置项详解

### 4.1 启动与认证字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | boolean | `false` | 是否启用 Discord 频道 |
| `token` | string/object | — | Bot Token（优先使用环境变量 `DISCORD_BOT_TOKEN`），支持明文或 SecretRef |
| `accounts` | object | `{}` | 多账户配置，支持 default 账户及命名账户 |
| `accounts.<id>.token` | string | — | 指定账户的 Bot Token |
| `accounts.<id>.name` | string | — | 账户显示名称 |
| `accounts.<id>.allowFrom` | string[] | — | 该账户独立的 DM 白名单 |
| `accounts.<id>.configWrites` | boolean | `true` | 是否允许该账户执行配置写入 |
| `accounts.<id>.ui.components.accentColor` | string | — | 该账户独立的组件主题色 |
| `allowBots` | boolean | `false` | 是否允许处理来自其他 Discord 机器人的消息 |

**Token 配置示例：**

```json
{
  "channels": {
    "discord": {
      "token": {
        "source": "env",
        "provider": "default",
        "id": "DISCORD_BOT_TOKEN"
      }
    }
  }
}
```

**多账户配置示例：**

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "defaultAccount": "personal",
      "accounts": {
        "personal": {
          "token": { "source": "env", "provider": "default", "id": "DISCORD_BOT_TOKEN_PERSONAL" },
          "groupPolicy": "allowlist",
          "guilds": {
            "1476767932041138198": {
              "requireMention": false,
              "users": ["1087662067332419655"]
            }
          }
        },
        "work": {
          "token": { "source": "env", "provider": "default", "id": "DISCORD_BOT_TOKEN_WORK" },
          "groupPolicy": "allowlist",
          "guilds": {
            "987654321098765432": {
              "requireMention": true,
              "roles": ["123456789012345678"]
            }
          }
        }
      }
    }
  }
}
```

### 4.2 DM（私聊）策略

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `dmPolicy` | string | `"pairing"` | DM 访问策略。可选值：`pairing`（配对模式，推荐）、`allowlist`（白名单）、`open`（开放，需配合 `allowFrom: ["*"]`）、`disabled`（禁用） |
| `allowFrom` | string[] | `[]` | DM 允许的用户 ID 列表。`dmPolicy: "open"` 时必须包含 `"*"` |
| `dm.enabled` | boolean | `true` | 是否启用 DM 处理 |
| `dm.groupEnabled` | boolean | `false` | 是否启用群组 DM（Group DM）处理 |
| `dm.groupChannels` | string[] | `[]` | 允许的群组 DM 频道 ID 或别名列表 |

> ⚠️ **注意**：`channels.discord.dm.policy` 是旧写法，新版本中已迁移到 `channels.discord.dmPolicy`。`channels.discord.dm.allowFrom` 也是旧写法，现由顶层 `allowFrom` 控制。

**DM 配置示例：**

```json
{
  "channels": {
    "discord": {
      "dmPolicy": "pairing",
      "allowFrom": ["1087662067332419655"],
      "dmHistoryLimit": 20,
      "dm": {
        "enabled": true,
        "groupEnabled": false,
        "groupChannels": []
      }
    }
  }
}
```

### 4.3 Guild（服务器）策略

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `groupPolicy` | string | `"allowlist"` | 服务器访问策略。可选值：`open`（开放所有服务器）、`allowlist`（白名单，推荐）、`disabled`（禁用） |
| `dangerouslyAllowNameMatching` | boolean | `false` | 是否允许通过用户名/Tag 进行白名单匹配（仅作为应急兼容模式，ID 更安全） |

**服务器详细配置（`guilds`）：**

`guilds` 以 **Guild ID（服务器 ID）** 为键：

```json
"guilds": {
  "1476767932041138198": {
    "slug": "my-server",
    "requireMention": false,
    "ignoreOtherMentions": true,
    "reactionNotifications": "own",
    "users": ["1087662067332419655"],
    "roles": ["123456789012345678"],
    "channels": {}
  }
}
```

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `guilds.<id>.slug` | string | — | 服务器别名（可选，用于可读性） |
| `guilds.<id>.requireMention` | boolean | `false` | 该服务器是否要求 @提及机器人才回复 |
| `guilds.<id>.ignoreOtherMentions` | boolean | `false` | 是否忽略只提及其他用户/角色但未提及机器人的消息（排除 @everyone/@here） |
| `guilds.<id>.reactionNotifications` | string | `"own"` | 反应通知模式 |
| `guilds.<id>.users` | string[] | `[]` | 该服务器允许的用户 ID 白名单（stable ID 推荐） |
| `guilds.<id>.roles` | string[] | `[]` | 该服务器允许的角色 ID 白名单 |
| `guilds.<id>.channels` | object | `{}` | 该服务器下的频道级配置（见 4.4） |

> 白名单行为：当 `groupPolicy` 为 `allowlist` 时，guild 必须匹配 `guilds` 中的键；若配置了 `users` 或 `roles`，发送者需匹配其中之一；若配置了 `channels`，未列出的频道会被拒绝。

**Guild 配置示例：**

```json
{
  "channels": {
    "discord": {
      "groupPolicy": "allowlist",
      "guilds": {
        "1476767932041138198": {
          "slug": "my-server",
          "requireMention": false,
          "ignoreOtherMentions": true,
          "users": ["1087662067332419655"],
          "roles": ["123456789012345678"],
          "reactionNotifications": "own",
          "channels": {
            "general": {
              "allow": true,
              "requireMention": false
            },
            "admin": {
              "allow": true,
              "requireMention": true
            }
          }
        }
      }
    }
  }
}
```

### 4.4 频道级配置（guilds.&lt;id&gt;.channels）

以 **频道 ID** 或 **频道别名** 为键：

```json
"channels": {
  "1359880765724332092": {
    "allow": true,
    "requireMention": true,
    "allowFrom": ["1087662067332419655"],
    "toolPolicy": "open",
    "users": ["1087662067332419655"],
    "roles": [],
    "skills": ["docs"],
    "systemPrompt": "Short answers only."
  }
}
```

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `allow` | boolean | `false` | 是否允许机器人在此频道活动 |
| `requireMention` | boolean | `false` | 该频道是否要求 @提及 |
| `allowFrom` | string[] | `[]` | 该频道允许的用户 ID 列表 |
| `toolPolicy` | string | `"open"` | 工具使用策略：`open`（开放）、`allowlist`（白名单）、`disabled`（禁用） |
| `users` | string[] | `[]` | 频道级用户白名单 |
| `roles` | string[] | `[]` | 频道级角色白名单 |
| `skills` | string[] | `[]` | 该频道限制可用的技能列表 |
| `systemPrompt` | string | — | 该频道专用的系统提示词覆盖 |

### 4.5 消息与交互字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `replyToMode` | string | `"off"` | 回复模式：`off`（不回复）、`first`（回复第一条）、`all`（回复所有）、`batched`（批量回复） |
| `historyLimit` | number | `20` | 群聊上下文历史消息条数上限 |
| `dmHistoryLimit` | number | `20` | DM 上下文历史消息条数上限 |
| `dms.<id>.historyLimit` | number | — | 指定 DM 会话的历史条数覆盖 |
| `textChunkLimit` | number | `2000` | 单条 Discord 消息文本分块长度上限 |
| `chunkMode` | string | `"length"` | 分块模式：`length`（按长度）、`newline`（按换行符） |
| `maxLinesPerMessage` | number | `17` | 单条消息最大行数 |
| `responsePrefix` | string | `""` | 机器人回复前缀字符串 |
| `ackReaction` | string | `👀` | 处理中反应表情 |

### 4.6 流式传输字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `streaming` | string | `"off"` | 流式输出模式：`off`（关闭）、`partial`（部分流式）、`block`（块级流式）、`progress`（进度流式，Discord 上映射为 `partial`） |
| `draftChunk` | boolean/number | `false` | 草稿块大小（启用流式时有效） |
| `blockStreaming` | boolean | `false` | 是否启用块级流式传输 |
| `blockStreamingCoalesce` | boolean | `false` | 是否合并块级流式输出 |

> Legacy：`streamMode` 是 `streaming` 的别名，已弃用。

**流式配置示例：**

```json
{
  "channels": {
    "discord": {
      "streaming": "partial",
      "draftChunk": 800,
      "chunkMode": "length"
    }
  }
}
```

**Block 模式配置：**

```json
{
  "channels": {
    "discord": {
      "streaming": "block",
      "blockStreaming": true,
      "blockStreamingCoalesce": false,
      "draftChunk": 800
    }
  }
}
```

### 4.7 命令与指令字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `commands.native` | boolean\|string | `"auto"` | 原生 Discord Slash Command 开关。`"auto"` 对 Discord/Telegram 开启，Slack 关闭；`false` 会清除已注册的命令 |
| `commands.nativeSkills` | boolean\|string | `"auto"` | 原生技能命令注册开关 |
| `commands.useAccessGroups` | boolean | `true` | 是否使用访问组控制命令权限 |
| `configWrites` | boolean | `true` | 是否允许通过该频道执行配置写入（如 /config 命令） |
| `slashCommand.*` | object | — | Slash Command 详细配置 |

**命令配置示例：**

```json
{
  "channels": {
    "discord": {
      "commands": {
        "native": "auto",
        "nativeSkills": "auto",
        "useAccessGroups": true
      },
      "configWrites": true
    }
  }
}
```

### 4.8 事件队列与工作者字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `eventQueue.listenerTimeout` | number | — | 事件监听超时（监听器预算） |
| `eventQueue.maxQueueSize` | number | — | 事件队列最大长度 |
| `eventQueue.maxConcurrency` | number | — | 事件队列最大并发数 |
| `inboundWorker.runTimeoutMs` | number | — | 入站消息处理 Worker 运行超时（毫秒） |

**事件队列配置示例：**

```json
{
  "channels": {
    "discord": {
      "eventQueue": {
        "listenerTimeout": 120000,
        "maxQueueSize": 1000,
        "maxConcurrency": 10
      },
      "inboundWorker": {
        "runTimeoutMs": 1800000
      }
    }
  }
}
```

### 4.9 媒体与重试字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `mediaMaxMb` | number | `100` | Discord 出站上传文件大小上限（MB） |
| `retry.attempts` | number | `3` | 请求重试次数 |
| `retry.minDelayMs` | number | `500` | 重试最小延迟（毫秒） |
| `retry.maxDelayMs` | number | `30000` | 重试最大延迟（毫秒） |
| `retry.jitter` | number | `0.1` | 重试抖动系数 |

**重试配置示例：**

```json
{
  "channels": {
    "discord": {
      "mediaMaxMb": 100,
      "retry": {
        "attempts": 3,
        "minDelayMs": 500,
        "maxDelayMs": 30000,
        "jitter": 0.1
      }
    }
  }
}
```

### 4.10 动作权限门（actions）

控制 Discord 消息动作（Message Actions）的启用/禁用：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `actions.reactions` | boolean | `true` | 表情反应 |
| `actions.messages` | boolean | `true` | 消息操作（发送/编辑/删除） |
| `actions.threads` | boolean | `true` | 线程操作 |
| `actions.pins` | boolean | `true` | 置顶操作 |
| `actions.polls` | boolean | `true` | 投票操作 |
| `actions.search` | boolean | `true` | 搜索操作 |
| `actions.memberInfo` | boolean | `true` | 成员信息查询 |
| `actions.roleInfo` | boolean | `true` | 角色信息查询 |
| `actions.channelInfo` | boolean | `true` | 频道信息查询 |
| `actions.channels` | boolean | `true` | 频道管理 |
| `actions.voiceStatus` | boolean | `true` | 语音状态 |
| `actions.events` | boolean | `true` | 事件操作（如 event-create，支持 image 参数设置封面） |
| `actions.stickers` | boolean | `true` | 贴纸操作 |
| `actions.emojiUploads` | boolean | `true` | 表情上传 |
| `actions.stickerUploads` | boolean | `true` | 贴纸上传 |
| `actions.permissions` | boolean | `true` | 权限查询 |
| `actions.roles` | boolean | `false` | 角色管理（默认禁用，需显式开启） |
| `actions.moderation` | boolean | `false` | moderation 操作（踢出/封禁/超时，默认禁用） |
| `actions.presence` | boolean | `false` | 在线状态设置（默认禁用） |

**actions 配置示例：**

```json
{
  "channels": {
    "discord": {
      "actions": {
        "reactions": true,
        "messages": true,
        "threads": true,
        "pins": true,
        "polls": true,
        "search": true,
        "memberInfo": true,
        "roleInfo": true,
        "channelInfo": true,
        "channels": true,
        "voiceStatus": true,
        "events": true,
        "stickers": true,
        "emojiUploads": true,
        "stickerUploads": true,
        "permissions": true,
        "roles": false,
        "moderation": false,
        "presence": false
      }
    }
  }
}
```

### 4.11 在线状态与 UI 字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `presence.activity` | string | — | 机器人活动名称（如 "Playing ..."） |
| `presence.status` | string | — | 在线状态：`online`、`idle`、`dnd`、`invisible` |
| `presence.activityType` | string | — | 活动类型 |
| `presence.activityUrl` | string | — | 活动 URL（直播链接等） |
| `ui.components.accentColor` | string | — | Discord Components v2 容器主题色（Hex，如 "#5865F2"） |

> 注意：旧版本中使用顶层字段 `status`、`activity`、`activityType`、`activityUrl`，新版本已统一归入 `presence` 对象下。

**在线状态配置示例：**

```json
{
  "channels": {
    "discord": {
      "presence": {
        "activity": "Helping humans",
        "status": "online",
        "activityType": "PLAYING"
      },
      "ui": {
        "components": {
          "accentColor": "#5865F2"
        }
      }
    }
  }
}
```

### 4.12 线程绑定（threadBindings）

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `threadBindings.enabled` | boolean | `true` | 是否启用线程绑定会话功能 |
| `threadBindings.idleHours` | number | `24` | 线程空闲自动取消关注小时数（`0` 为禁用） |
| `threadBindings.maxAgeHours` | number | `0` | 线程最大存活小时数（`0` 为禁用） |
| `threadBindings.spawnSubagentSessions` | boolean | `false` | 是否在线程中生成子代理会话（需显式开启） |

**线程绑定配置示例：**

```json
{
  "channels": {
    "discord": {
      "threadBindings": {
        "enabled": true,
        "idleHours": 24,
        "maxAgeHours": 0,
        "spawnSubagentSessions": false
      }
    }
  }
}
```

### 4.13 语音频道（voice）

```json
"voice": {
  "enabled": true,
  "autoJoin": [
    {
      "guildId": "123456789012345678",
      "channelId": "234567890123456789"
    }
  ],
  "daveEncryption": true,
  "decryptionFailureTolerance": 24,
  "tts": {
    "provider": "openai",
    "openai": { "voice": "alloy" }
  }
}
```

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `voice.enabled` | boolean | `true` | 是否启用语音功能（默认开启，显式设 `false` 可禁用） |
| `voice.autoJoin` | array | `[]` | 自动加入的语音频道列表，每项包含 `guildId` 和 `channelId` |
| `voice.daveEncryption` | boolean | `true` | 是否启用 DAVE 端到端加密 |
| `voice.decryptionFailureTolerance` | number | `24` | 解密失败容忍次数（传递给 @discordjs/voice） |
| `voice.tts.provider` | string | — | TTS 提供商 |
| `voice.tts.openai.voice` | string | — | OpenAI TTS 语音角色（如 `alloy`） |

> 注意：语音转录回合的发言者身份由 Discord `allowFrom`（或 `dm.allowFrom`）推导；非所有者发言者无法访问所有者专属工具（如 gateway、cron）。

**语音配置示例：**

```json
{
  "channels": {
    "discord": {
      "voice": {
        "enabled": true,
        "autoJoin": [
          {
            "guildId": "1476767932041138198",
            "channelId": "234567890123456789"
          }
        ],
        "daveEncryption": true,
        "decryptionFailureTolerance": 24,
        "tts": {
          "provider": "openai",
          "openai": { "voice": "alloy" }
        }
      }
    }
  }
}
```

### 4.14 执行审批（execApprovals）

```json
"execApprovals": {
  "enabled": "auto",
  "approvers": ["987654321098765432"],
  "agentFilter": ["default"],
  "sessionFilter": ["discord:"],
  "target": "dm",
  "cleanupAfterResolve": false
}
```

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `execApprovals.enabled` | boolean\|string | `"auto"` | 审批开关：`true`（开启）、`false`（关闭）、`"auto"`（自动） |
| `execApprovals.approvers` | string[] | `[]` | 审批者 Discord 用户 ID 列表 |
| `execApprovals.agentFilter` | string[] | `[]` | 仅对指定代理启用审批 |
| `execApprovals.sessionFilter` | string[] | `[]` | 仅对匹配前缀的会话启用审批（如 `["discord:"]`） |
| `execApprovals.target` | string | `"dm"` | 审批消息发送目标：`dm`（私聊）、`channel`（频道）、`both`（两者） |
| `execApprovals.cleanupAfterResolve` | boolean | `false` | 审批解决后是否清理消息 |

**执行审批配置示例：**

```json
{
  "channels": {
    "discord": {
      "execApprovals": {
        "enabled": "auto",
        "approvers": [],
        "agentFilter": [],
        "sessionFilter": ["discord:"],
        "target": "dm",
        "cleanupAfterResolve": false
      }
    }
  }
}
```

### 4.15 其他功能字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `intents` | object | — | Discord Gateway Intents 配置 |
| `agentComponents` | boolean | `false` | 是否启用代理组件 |
| `heartbeat` | object/boolean | — | 心跳配置 |
| `pluralkit` | object | — | PluralKit 集成配置 |

**PluralKit 配置示例：**

```json
{
  "channels": {
    "discord": {
      "pluralkit": {
        "enabled": true,
        "token": "pk_live_..."
      }
    }
  }
}
```

---

## 五、Bindings（顶层路由关联）

`bindings` 位于 `openclaw.json` 顶层（与 `channels` 同级），用于将 Discord 频道/服务器路由到指定代理：

```json
{
  "bindings": [
    {
      "agentId": "lira",
      "match": {
        "channel": "discord",
        "guildId": "1476767932041138198",
        "peer": {
          "kind": "group",
          "id": "1359880765724332092"
        },
        "roles": ["111111111111111111"]
      }
    }
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `bindings[].agentId` | string | 目标代理 ID |
| `bindings[].match.channel` | string | 固定为 `"discord"` |
| `bindings[].match.guildId` | string | Discord 服务器 ID |
| `bindings[].match.peer.kind` | string | `"group"` 或 `"direct"` |
| `bindings[].match.peer.id` | string | 频道 ID 或用户 ID |
| `bindings[].match.roles` | string[] | 角色 ID 列表（仅接受角色 ID），用于角色级代理路由 |

> 路由优先级：`peer` 或 `parent-peer` 绑定 > `roles` 绑定 > `guildId` 绑定。若同时配置多个匹配字段（如 `peer` + `guildId` + `roles`），所有字段必须同时匹配。

---

## 六、常见配置场景

### 场景1：仅允许特定用户访问

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": { "source": "env", "provider": "default", "id": "DISCORD_BOT_TOKEN" },
      "groupPolicy": "allowlist",
      "dmPolicy": "pairing",
      "guilds": {
        "1476767932041138198": {
          "requireMention": false,
          "users": ["1087662067332419655", "987654321098765432"]
        }
      }
    }
  }
}
```

### 场景2：私有服务器自动响应

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": { "source": "env", "provider": "default", "id": "DISCORD_BOT_TOKEN" },
      "groupPolicy": "allowlist",
      "dmPolicy": "pairing",
      "streaming": "off",
      "replyToMode": "off",
      "historyLimit": 20,
      "guilds": {
        "1476767932041138198": {
          "slug": "private-server",
          "requireMention": false,
          "ignoreOtherMentions": true,
          "users": ["1087662067332419655"],
          "channels": {
            "general": { "allow": true },
            "coding": { "allow": true },
            "random": { "allow": true }
          }
        }
      }
    }
  }
}
```

### 场景3：多账户配置

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "defaultAccount": "personal",
      "accounts": {
        "personal": {
          "token": { "source": "env", "provider": "default", "id": "DISCORD_BOT_TOKEN_PERSONAL" },
          "groupPolicy": "allowlist",
          "guilds": {
            "1476767932041138198": {
              "requireMention": false,
              "users": ["1087662067332419655"]
            }
          }
        },
        "work": {
          "token": { "source": "env", "provider": "default", "id": "DISCORD_BOT_TOKEN_WORK" },
          "groupPolicy": "allowlist",
          "guilds": {
            "987654321098765432": {
              "requireMention": true,
              "roles": ["123456789012345678"]
            }
          }
        }
      }
    }
  }
}
```

### 场景4：语音频道接入

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": { "source": "env", "provider": "default", "id": "DISCORD_BOT_TOKEN" },
      "groupPolicy": "allowlist",
      "commands": {
        "native": true
      },
      "voice": {
        "enabled": true,
        "autoJoin": [
          {
            "guildId": "1476767932041138198",
            "channelId": "234567890123456789"
          }
        ],
        "daveEncryption": true,
        "tts": {
          "provider": "openai",
          "openai": { "voice": "alloy" }
        }
      },
      "guilds": {
        "1476767932041138198": {
          "requireMention": false,
          "users": ["1087662067332419655"]
        }
      }
    }
  }
}
```

---

## 七、常见问题与解决方案

### 问题1：Failed to resolve Discord application id

**现象**：
```
[default] channel exited: Failed to resolve Discord application id
```

**原因分析**：
1. Token 无效或过期
2. Bot 已被删除
3. 网络连接问题（最常见）

**排查步骤**：
```bash
# 1. 测试 Discord API 连通性
curl -v https://discord.com/api/v10/gateway

# 2. 检查日志
tail -50 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep discord

# 3. 验证 Token 是否更新
openclaw config list | grep token
```

**解决方案**：
- 在 Discord Developer Portal 重置 Token
- 更新 OpenClaw 配置
- 检查网络/代理配置

---

### 问题2：Connection reset by peer

**现象**：
```bash
curl -v https://discord.com/api/v10/gateway
# 返回：Connection reset by peer
```

**原因**：国内网络环境直连 Discord 会被重置

**解决方案（Clash 配置）**：

编辑 Clash 配置文件，在 `rules:` 部分添加：

```yaml
rules:
  # Discord 相关域名走代理
  - DOMAIN-SUFFIX,discord.com,Ghelper
  - DOMAIN-SUFFIX,discordapp.com,Ghelper
  - DOMAIN-SUFFIX,discord.gg,Ghelper
  - DOMAIN-SUFFIX,discord.media,Ghelper
  - DOMAIN-SUFFIX,discordapp.net,Ghelper
  - DOMAIN-SUFFIX,discordcdn.com,Ghelper
  - DOMAIN-SUFFIX,discord.dev,Ghelper
  - DOMAIN-SUFFIX,discord.new,Ghelper
  - DOMAIN-SUFFIX,discord.gift,Ghelper
  - DOMAIN-SUFFIX,discord.co,Ghelper
  - DOMAIN-SUFFIX,discord-attachments-uploads-prd.storage.googleapis.com,Ghelper
  
  # 原有规则...
  - MATCH,Ghelper
```

---

### 问题3：Message Content Intent 未启用

**现象**：Bot 在线，可以接收消息事件，但无法读取消息内容

**原因**：未启用 Message Content Intent

**解决方案**：
1. 访问 [Discord Developer Portal](https://discord.com/developers/applications)
2. 选择你的 Application → **Bot** 菜单
3. 启用 **Message Content Intent**
4. 保存后等待 1-2 分钟生效
5. 重启 OpenClaw Gateway

---

### 问题4：配置验证失败 - must NOT have additional properties

**现象**：
```
Invalid config at /Users/.../.openclaw/openclaw.json:
- channels.discord: invalid config: must NOT have additional properties
```

**原因**：配置项格式不符合新版本要求，或使用了已废弃/不合法的字段

**常见错误及修复：**

1. **streaming 格式错误**（旧版对象 → 新版字符串）：
```json
// ❌ 错误（旧版对象写法，已过期）
"streaming": {
  "mode": "off"
}

// ✅ 正确
"streaming": "off"
```

2. **presence 位置错误**（旧版顶层 → 新版对象）：
```json
// ❌ 错误（旧版顶层写法，已过期）
{
  "status": "online",
  "activity": "Helping",
  "activityType": 4
}

// ✅ 正确
{
  "presence": {
    "status": "online",
    "activity": "Helping",
    "activityType": "PLAYING"
  }
}
```

3. **使用了非法字段**：
```json
// ❌ 错误（不存在于 Schema 中）
"autoPresence": { ... }
"ackReactionScope": "..."
"threadBindings.spawnAcpSessions": true

// 请对照本文档 4.x 章节，仅使用合法字段
```

4. **缺少必需字段**：
```json
// ✅ 确保 groupPolicy 已设置
{
  "channels": {
    "discord": {
      "enabled": true,
      "groupPolicy": "allowlist",
      "token": "..."
    }
  }
}
```

---

## 八、验证连接

```bash
# 1. 检查 Gateway 状态
openclaw gateway status

# 2. 查看 Discord 连接日志
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep -E "(discord|gateway ready)"

# 3. 检查配置是否有效
openclaw doctor

# 4. 在 Discord 中测试
# - 找到 Bot 用户
# - 发送私信
# - 检查是否收到回复
```

**成功标志**：
- 日志中出现 `[default] gateway ready`
- 私信 Bot 能收到回复
- 配对码生成成功

---

## 九、配对流程

首次连接成功后，需要完成配对：

1. **获取配对码**：DM Bot，它会回复配对码（如：`HTF7KLTT`）

2. **批准配对**（方式一：CLI）：
   ```bash
   openclaw pairing list discord
   openclaw pairing approve discord <CODE>
   ```

3. **批准配对**（方式二：询问 Agent）：
   > "Approve this Discord pairing code: `<CODE>`"

4. **验证配对**：再次发送私信测试是否正常响应

> 配对码有效期为 1 小时。

---

## 十、常用命令速查

| 命令 | 用途 |
|------|------|
| `openclaw gateway status` | 查看 Gateway 状态 |
| `openclaw gateway restart` | 重启 Gateway |
| `openclaw config list` | 列出当前配置 |
| `openclaw config get channels.discord` | 获取 Discord 配置 |
| `openclaw config set channels.discord.enabled true` | 启用 Discord |
| `openclaw doctor` | 诊断检查 |
| `openclaw channels status --probe` | 检查频道状态 |
| `openclaw pairing list discord` | 查看待处理配对 |
| `openclaw pairing approve discord <CODE>` | 批准配对 |
| `tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log` | 查看实时日志 |

---

## 十一、完整配置参考

以下是一个生产环境可用的完整配置示例：

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": {
        "source": "env",
        "provider": "default",
        "id": "DISCORD_BOT_TOKEN"
      },
      "groupPolicy": "allowlist",
      "dmPolicy": "pairing",
      "allowFrom": [],
      "allowBots": false,
      "dm": {
        "enabled": true,
        "groupEnabled": false,
        "groupChannels": []
      },
      "guilds": {
        "1476767932041138198": {
          "slug": "my-private-server",
          "requireMention": false,
          "ignoreOtherMentions": true,
          "reactionNotifications": "own",
          "users": ["1087662067332419655"],
          "roles": [],
          "channels": {
            "1359880765724332092": {
              "allow": true,
              "requireMention": false,
              "allowFrom": ["1087662067332419655"],
              "toolPolicy": "open"
            },
            "1476782105307512977": {
              "allow": true,
              "requireMention": true,
              "users": ["1087662067332419655"],
              "skills": ["image_generate", "read"],
              "systemPrompt": "You are Lira, a creative assistant."
            }
          }
        }
      },
      "commands": {
        "native": "auto",
        "nativeSkills": "auto"
      },
      "configWrites": true,
      "replyToMode": "off",
      "historyLimit": 20,
      "dmHistoryLimit": 20,
      "textChunkLimit": 2000,
      "chunkMode": "length",
      "maxLinesPerMessage": 17,
      "streaming": "off",
      "mediaMaxMb": 100,
      "retry": {
        "attempts": 3,
        "minDelayMs": 500,
        "maxDelayMs": 30000,
        "jitter": 0.1
      },
      "actions": {
        "reactions": true,
        "messages": true,
        "threads": true,
        "pins": true,
        "polls": true,
        "search": true,
        "memberInfo": true,
        "roleInfo": true,
        "channelInfo": true,
        "channels": true,
        "voiceStatus": true,
        "events": true,
        "stickers": true,
        "emojiUploads": true,
        "stickerUploads": true,
        "permissions": true,
        "roles": false,
        "moderation": false,
        "presence": false
      },
      "presence": {
        "activity": "Helping humans",
        "status": "online",
        "activityType": "PLAYING"
      },
      "ui": {
        "components": {
          "accentColor": "#5865F2"
        }
      },
      "threadBindings": {
        "enabled": true,
        "idleHours": 24,
        "maxAgeHours": 0,
        "spawnSubagentSessions": false
      },
      "voice": {
        "enabled": true,
        "autoJoin": [],
        "daveEncryption": true,
        "decryptionFailureTolerance": 24,
        "tts": {
          "provider": "openai",
          "openai": { "voice": "alloy" }
        }
      },
      "execApprovals": {
        "enabled": "auto",
        "approvers": [],
        "agentFilter": [],
        "sessionFilter": ["discord:"],
        "target": "dm",
        "cleanupAfterResolve": false
      }
    }
  },
  "bindings": [
    {
      "agentId": "lira",
      "match": {
        "channel": "discord",
        "guildId": "1476767932041138198",
        "peer": {
          "kind": "group",
          "id": "1359880765724332092"
        }
      }
    }
  ]
}
```

---

## 十二、已废弃/不合法的字段（避免踩坑）

以下字段 **不属于** `channels.discord` 的合法 Schema，配置会导致 `must NOT have additional properties` 错误：

| 非法字段 | 错误写法 | 正确替代 |
|----------|----------|----------|
| `groupAllowFrom` | `"groupAllowFrom": ["..."]` | 使用 `guilds.<id>.users` 或 `guilds.<id>.roles` |
| `dmPolicy` 在 `dm` 对象内 | `"dm": { "policy": "..." }` | 使用顶层 `dmPolicy` |
| `allowFrom` 在 `dm` 对象内 | `"dm": { "allowFrom": ["..."] }` | 使用顶层 `allowFrom` |
| `groupPolicy` 在 `guilds` 内 | `"guilds": { "groupPolicy": "..." }` | `groupPolicy` 只能在 `channels.discord` 顶层 |
| `autoPresence` | `"autoPresence": { ... }` | 已废弃，不再支持 |
| `ackReactionScope` | `"ackReactionScope": "..."` | 已废弃，不再支持 |
| `threadBindings.spawnAcpSessions` | `"spawnAcpSessions": true` | 不存在，仅支持 `spawnSubagentSessions` |
| `streaming` 对象格式 | `"streaming": { "mode": "..." }` | 使用字符串 `"streaming": "off"` |
| `draftChunk` 对象格式 | `"draftChunk": { "minChars": ... }` | 使用布尔/数字 `"draftChunk": false` 或 `"draftChunk": 800` |
| `status`（顶层） | `"status": "online"` | 移入 `presence.status` |
| `activity`（顶层） | `"activity": "..."` | 移入 `presence.activity` |
| `activityType`（顶层） | `"activityType": 4` | 移入 `presence.activityType` |
| `activityUrl`（顶层） | `"activityUrl": "..."` | 移入 `presence.activityUrl` |

---

> **文档版本**：v3.0  
> **最后更新**：2026-05-03  
> **适用版本**：OpenClaw 2026.4.14+  
>  
> **参考文档**：https://docs.openclaw.ai/channels/discord  
> **附录**：[OpenClaw Discord 配置完整参考手册](./OpenClaw排查.docx)
