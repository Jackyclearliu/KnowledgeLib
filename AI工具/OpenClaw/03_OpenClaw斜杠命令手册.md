# OpenClaw 斜杠命令手册

> 本文档整理自 OpenClaw 官方文档，汇总所有可用的斜杠命令及其子命令。

---

## 目录

- [概述](#概述)
- [指令（Directives）](#指令directives)
- [核心内置命令](#核心内置命令)
- [Dock 命令](#dock-命令)
- [插件命令](#插件命令)
- [动态技能命令](#动态技能命令)
- [配置说明](#配置说明)
- [使用注意事项](#使用注意事项)

---

## 概述

OpenClaw 的斜杠命令由 Gateway 处理。大多数命令必须以 **独立消息** 形式发送，且以 `/` 开头。

**命令分类：**

| 类别 | 说明 |
|------|------|
| **指令 (Directives)** | 如 `/think`、`/model` 等，可从消息中剥离，不进入模型上下文 |
| **核心内置命令** | OpenClaw 内置的基础命令 |
| **Dock 命令** | 由各频道插件生成的命令 |
| **插件命令** | 由已安装插件提供的命令 |
| **动态技能命令** | 用户可调用的技能命令 |
| **快捷命令** | 内联快捷方式，如 `/help`、`/status` |

---

## 指令（Directives）

指令在消息进入模型前被剥离，用于控制会话设置。

| 指令 | 别名 | 说明 | 典型用法 | 权限要求 |
|------|------|------|----------|----------|
| `/think` | `/thinking`, `/t` | 设置思考级别 | `/think high` | 需 `commands.allowFrom` 或频道白名单 |
| `/verbose` | `/v` | 切换详细输出模式 | `/verbose on` | 同上 |
| `/fast` | - | 显示或设置快速模式 | `/fast on` | 同上 |
| `/reasoning` | `/reason` | 切换推理可见性 | `/reasoning on` | 同上 |
| `/elevated` | `/elev` | 切换提权模式 | `/elevated on` | 需 `tools.elevated` 白名单 |
| `/exec` | - | 设置执行默认值 | `/exec host=sandbox` | 同上 |
| `/model` | - | 显示或设置模型 | `/model gpt-4` | 同上 |
| `/queue` | - | 管理队列行为 | `/queue steer` | 同上 |

**说明字段详解：**
- `off|minimal|low|medium|high|xhigh` - 思考级别选项
- `on|off|full` - 详细输出选项
- `status|on|off` - 快速模式选项
- `on|off|stream` - 推理可见性选项
- `on|off|ask|full` - 提权模式选项

---

## 核心内置命令

### 会话管理

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/new` | `[model]` | 新建会话 | 启动新会话，`/reset` 为别名 | `/new gpt-4` | 无特殊要求 |
| `/reset` | - | 重置会话 | `/new` 的别名 | `/reset` | 同上 |
| `/compact` | `[instructions]` | 压缩会话 | 压缩会话上下文 | `/compact` | 同上 |
| `/stop` | - | 停止运行 | 中止当前运行 | `/stop` | 同上 |
| `/session` | `idle <duration\|off>` | 空闲超时 | 管理线程绑定过期时间 | `/session idle 30m` | 需线程绑定功能启用 |
| `/session` | `max-age <duration\|off>` | 最大年龄 | 管理会话最大存活时间 | `/session max-age 24h` | 同上 |

### 模型与工具

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/models` | `[provider] [page] [limit=<n>\|size=<n>\|all]` | 模型列表 | 列出提供商或模型 | `/models openai` | 无特殊要求 |
| `/tools` | `[compact\|verbose]` | 工具列表 | 显示当前代理可用工具 | `/tools verbose` | 同上 |
| `/context` | `[list\|detail\|json]` | 上下文解释 | 解释上下文如何组装 | `/context detail` | 同上 |

### 状态与信息

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/help` | - | 帮助 | 显示简短帮助摘要 | `/help` | 无特殊要求 |
| `/commands` | - | 命令目录 | 显示生成的命令目录 | `/commands` | 同上 |
| `/status` | - | 状态 | 显示运行时状态 | `/status` | 同上 |
| `/tasks` | - | 任务列表 | 列出后台任务 | `/tasks` | 同上 |
| `/whoami` | - | 身份识别 | 显示发送者 ID，`/id` 为别名 | `/whoami` | 同上 |
| `/usage` | `off\|tokens\|full\|cost` | 用量控制 | 控制响应页脚用量显示 | `/usage tokens` | 同上 |

### 导出与技能

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/export-session` | `[path]` | 导出会话 | 导出会话为 HTML，`/export` 为别名 | `/export-session` | 无特殊要求 |
| `/skill` | `<name> [input]` | 运行技能 | 按名称运行技能 | `/skill weather 北京` | 同上 |
| `/btw` | `<question>` | 附带问题 | 进行不改变上下文的快速提问 | `/btw 当前任务是什么？` | 同上 |

### 子代理管理

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/subagents` | `list` | 子代理列表 | 列出子代理 | `/subagents list` | 无特殊要求 |
| `/subagents` | `kill` | 终止子代理 | 终止子代理运行 | `/subagents kill` | 同上 |
| `/subagents` | `log` | 查看日志 | 查看子代理日志 | `/subagents log` | 同上 |
| `/subagents` | `info` | 子代理信息 | 显示子代理信息 | `/subagents info` | 同上 |
| `/subagents` | `send` | 发送消息 | 向子代理发送消息 | `/subagents send` | 同上 |
| `/subagents` | `steer` | 引导子代理 | 引导子代理行为 | `/subagents steer` | 同上 |
| `/subagents` | `spawn` | 创建子代理 | 创建新的子代理 | `/subagents spawn` | 同上 |
| `/kill` | `<id\|#\|all>` | 终止代理 | 终止一个或所有子代理 | `/kill all` | 同上 |
| `/steer` | `<id\|#> <message>` | 引导代理 | 向运行中的子代理发送引导，`/tell` 为别名 | `/steer 1 继续处理` | 同上 |

### ACP 会话管理

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/acp` | `spawn` | 创建会话 | 创建 ACP 会话 | `/acp spawn` | 无特殊要求 |
| `/acp` | `cancel` | 取消会话 | 取消 ACP 会话 | `/acp cancel` | 同上 |
| `/acp` | `steer` | 引导会话 | 引导 ACP 会话 | `/acp steer` | 同上 |
| `/acp` | `close` | 关闭会话 | 关闭 ACP 会话 | `/acp close` | 同上 |
| `/acp` | `sessions` | 会话列表 | 列出 ACP 会话 | `/acp sessions` | 同上 |
| `/acp` | `status` | 状态 | 显示 ACP 状态 | `/acp status` | 同上 |
| `/acp` | `set-mode` | 设置模式 | 设置 ACP 模式 | `/acp set-mode` | 同上 |
| `/acp` | `set` | 设置选项 | 设置 ACP 选项 | `/acp set` | 同上 |
| `/acp` | `cwd` | 工作目录 | 设置工作目录 | `/acp cwd` | 同上 |
| `/acp` | `permissions` | 权限 | 管理 ACP 权限 | `/acp permissions` | 同上 |
| `/acp` | `timeout` | 超时 | 设置超时 | `/acp timeout` | 同上 |
| `/acp` | `model` | 模型 | 设置 ACP 模型 | `/acp model` | 同上 |
| `/acp` | `reset-options` | 重置选项 | 重置 ACP 选项 | `/acp reset-options` | 同上 |
| `/acp` | `doctor` | 诊断 | ACP 诊断 | `/acp doctor` | 同上 |
| `/acp` | `install` | 安装 | 安装 ACP | `/acp install` | 同上 |
| `/acp` | `help` | 帮助 | ACP 帮助 | `/acp help` | 同上 |

### Discord 线程绑定

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/focus` | `<target>` | 绑定目标 | 绑定当前 Discord 线程到会话目标 | `/focus main` | 需线程绑定功能启用 |
| `/unfocus` | - | 解除绑定 | 移除当前绑定 | `/unfocus` | 同上 |
| `/agents` | - | 代理列表 | 列出线程绑定代理 | `/agents` | 同上 |

### 白名单与审批

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/allowlist` | `list` | 白名单列表 | 列出白名单条目 | `/allowlist list` | `commands.config=true` |
| `/allowlist` | `add` | 添加白名单 | 添加白名单条目 | `/allowlist add user1` | 同上 |
| `/allowlist` | `remove` | 移除白名单 | 移除白名单条目 | `/allowlist remove user1` | 同上 |
| `/approve` | `<id> <decision>` | 审批 | 解决执行审批提示 | `/approve 12345 allow` | 需审批权限 |

### 所有者命令（Owner-only）

以下命令需要所有者权限，且需要在配置中启用相应功能：

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/config` | `show` | 显示配置 | 读取 `openclaw.json` | `/config show` | Owner-only, `commands.config: true` |
| `/config` | `get` | 获取配置项 | 获取特定配置项 | `/config get messages.responsePrefix` | 同上 |
| `/config` | `set` | 设置配置项 | 写入配置 | `/config set messages.responsePrefix="[openclaw]"` | 同上 |
| `/config` | `unset` | 移除配置项 | 移除配置项 | `/config unset messages.responsePrefix` | 同上 |
| `/mcp` | `show` | 显示 MCP | 读取 MCP 配置 | `/mcp show` | Owner-only, `commands.mcp: true` |
| `/mcp` | `get` | 获取 MCP | 获取 MCP 配置项 | `/mcp show context7` | 同上 |
| `/mcp` | `set` | 设置 MCP | 写入 MCP 配置 | `/mcp set context7={...}` | 同上 |
| `/mcp` | `unset` | 移除 MCP | 移除 MCP 配置项 | `/mcp unset context7` | 同上 |
| `/plugins` | `list` | 插件列表 | 列出插件 | `/plugins list` | Owner-only 写入, `commands.plugins: true` |
| `/plugins` | `inspect/show/get` | 查看插件 | 查看插件详情 | `/plugins show context7` | 同上 |
| `/plugins` | `install` | 安装插件 | 安装插件 | `/plugins install <spec>` | Owner-only |
| `/plugins` | `enable` | 启用插件 | 启用插件 | `/plugins enable context7` | Owner-only |
| `/plugins` | `disable` | 禁用插件 | 禁用插件 | `/plugins disable context7` | 同上 |
| `/plugin` | - | 插件别名 | `/plugins` 的别名 | `/plugin list` | 同上 |
| `/debug` | `show` | 显示调试 | 显示运行时覆盖 | `/debug show` | Owner-only, `commands.debug: true` |
| `/debug` | `set` | 设置调试 | 设置运行时覆盖 | `/debug set messages.responsePrefix="[test]"` | 同上 |
| `/debug` | `unset` | 移除调试 | 移除运行时覆盖 | `/debug unset messages.responsePrefix` | 同上 |
| `/debug` | `reset` | 重置调试 | 重置所有覆盖 | `/debug reset` | 同上 |
| `/send` | `on\|off\|inherit` | 发送策略 | 设置发送策略 | `/send on` | Owner-only |

### TTS 控制

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/tts` | `on\|off\|status` | TTS 开关 | 控制文本转语音 | `/tts on` | 无特殊要求 |
| `/tts` | `provider` | TTS 提供商 | 设置 TTS 提供商 | `/tts provider` | 同上 |
| `/tts` | `limit` | TTS 限制 | 设置 TTS 限制 | `/tts limit` | 同上 |
| `/tts` | `summary` | TTS 摘要 | TTS 摘要控制 | `/tts summary` | 同上 |
| `/tts` | `audio` | TTS 音频 | TTS 音频控制 | `/tts audio` | 同上 |
| `/tts` | `help` | TTS 帮助 | 显示 TTS 帮助 | `/tts help` | 同上 |

### 激活与系统

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/activation` | `mention\|always` | 激活模式 | 设置群组激活模式 | `/activation mention` | 无特殊要求 |
| `/restart` | - | 重启 | 重启 OpenClaw | `/restart` | `commands.restart: true`（默认启用） |

### Bash 命令（文本命令）

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/bash` | `<command>` | Bash 执行 | 运行主机 shell 命令，`! <cmd>` 为别名 | `/bash ls -la` | `commands.bash: true` + `tools.elevated` 白名单 |
| `!` | `<command>` | Bash 快捷 | `/bash` 的快捷方式 | `! ls -la` | 同上 |
| `!poll` | `[sessionId]` | 轮询后台任务 | 检查后台 bash 任务 | `!poll` | 同上 |
| `!stop` | `[sessionId]` | 停止后台任务 | 停止后台 bash 任务 | `!stop` | 同上 |

---

## Dock 命令

由频道插件生成的命令，用于管理 Dock 连接。

| 命令 | 别名 | 说明 | 典型用法 | 权限要求 |
|------|------|------|----------|----------|
| `/dock-discord` | `/dock_discord` | Discord Dock 管理 | `/dock-discord` | 无特殊要求 |
| `/dock-mattermost` | `/dock_mattermost` | Mattermost Dock 管理 | `/dock-mattermost` | 同上 |
| `/dock-slack` | `/dock_slack` | Slack Dock 管理 | `/dock-slack` | 同上 |
| `/dock-telegram` | `/dock_telegram` | Telegram Dock 管理 | `/dock-telegram` | 同上 |

---

## 插件命令

由已安装插件提供的命令。

### Dreaming（记忆梦境）

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/dreaming` | `on\|off\|status\|help` | 梦境模式 | 切换记忆梦境 | `/dreaming on` | 无特殊要求 |

### Pairing（设备配对）

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/pair` | `qr` | 配对二维码 | 显示配对二维码 | `/pair qr` | 无特殊要求 |
| `/pair` | `status` | 配对状态 | 显示配对状态 | `/pair status` | 同上 |
| `/pair` | `pending` | 待处理配对 | 显示待处理请求 | `/pair pending` | 同上 |
| `/pair` | `approve` | 批准配对 | 批准配对请求 | `/pair approve` | 同上 |
| `/pair` | `cleanup` | 清理配对 | 清理配对状态 | `/pair cleanup` | 同上 |
| `/pair` | `notify` | 配对通知 | 发送配对通知 | `/pair notify` | 同上 |

### Phone（手机节点控制）

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/phone` | `status` | 手机状态 | 显示手机节点状态 | `/phone status` | 无特殊要求 |
| `/phone` | `arm <camera\|screen\|writes\|all> [duration]` | 激活高风险命令 | 临时激活高风险手机命令 | `/phone arm camera 5m` | 同上 |
| `/phone` | `disarm` | 解除激活 | 解除高风险命令激活 | `/phone disarm` | 同上 |

### Voice（语音配置）

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/voice` | `status` | 语音状态 | 显示语音配置状态 | `/voice status` | 无特殊要求 |
| `/voice` | `list [limit]` | 语音列表 | 列出可用语音 | `/voice list` | 同上 |
| `/voice` | `set <voiceId\|name>` | 设置语音 | 设置默认语音 | `/voice set Nova` | 同上 |

**注意：** 在 Discord 上，原生命令名称为 `/talkvoice`。

### LINE 卡片

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/card` | `...` | 发送卡片 | 发送 LINE 富卡片预设 | `/card ...` | 无特殊要求 |

### QQBot 专用命令

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/bot-ping` | - | Ping | 测试连接 | `/bot-ping` | 无特殊要求 |
| `/bot-version` | - | 版本 | 显示版本 | `/bot-version` | 同上 |
| `/bot-help` | - | 帮助 | 显示帮助 | `/bot-help` | 同上 |
| `/bot-upgrade` | - | 升级 | 升级 QQBot | `/bot-upgrade` | 同上 |
| `/bot-logs` | - | 日志 | 查看日志 | `/bot-logs` | 同上 |

---

## 动态技能命令

用户可调用的技能也作为斜杠命令暴露。

| 命令 | 子命令/参数 | 官方名称 | 说明 | 典型用法 | 权限要求 |
|------|-------------|----------|------|----------|----------|
| `/skill` | `<name> [input]` | 运行技能 | 通用技能入口 | `/skill weather 北京` | 无特殊要求 |
| `/<skill-name>` | `[input]` | 特定技能 | 技能特定命令（如 `/prose`） | `/prose 写一篇故事` | 同上 |

**说明：**
- 技能名称会被清理为 `a-z0-9_` 格式（最多 32 字符）
- 冲突名称会添加数字后缀（如 `_2`）
- 技能可通过声明 `command-dispatch: tool` 直接路由到工具（确定性执行，不经过模型）

---

## 配置说明

### 命令配置选项

在 `openclaw.json` 中的 `commands` 部分：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `commands.text` | boolean | `true` | 启用文本命令解析 |
| `commands.native` | string | `"auto"` | 注册原生命令（Discord/Telegram 自动启用） |
| `commands.nativeSkills` | string | `"auto"` | 注册技能原生命令 |
| `commands.bash` | boolean | `false` | 启用 `! <cmd>` bash 命令 |
| `commands.bashForegroundMs` | number | `2000` | Bash 前台等待时间（0 立即后台） |
| `commands.config` | boolean | `false` | 启用 `/config` 命令 |
| `commands.mcp` | boolean | `false` | 启用 `/mcp` 命令 |
| `commands.plugins` | boolean | `false` | 启用 `/plugins` 命令 |
| `commands.debug` | boolean | `false` | 启用 `/debug` 命令 |
| `commands.restart` | boolean | `true` | 启用 `/restart` 命令 |
| `commands.useAccessGroups` | boolean | `true` | 使用访问组进行权限控制 |

### 权限配置示例

```json5
{
  commands: {
    // 全局白名单
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    // 所有者白名单（独立于 allowFrom）
    ownerAllowFrom: ["discord:123456789012345678"],
    ownerDisplay: "raw",  // 或 "hash"
    ownerDisplaySecret: "${OWNER_ID_HASH_SECRET}",
  }
}
```

---

## 使用注意事项

### 命令格式

- 命令和参数之间可使用可选的 `:`（如 `/think: high`、`/send: on`）
- `/new <model>` 接受模型别名、`provider/model` 或提供商名称（模糊匹配）

### 权限与安全

- **所有者命令**（`/config`、`/mcp`、`/debug` 等）仅对所有者可用
- **授权发送者**：命令和指令仅对授权发送者生效
- **未授权发送者**：命令被静默忽略，内联 `/...` 标记视为纯文本

### 快捷方式

以下命令可作为内联快捷方式（在普通消息中使用，会被剥离）：

| 快捷命令 | 说明 |
|----------|------|
| `/help` | 显示帮助 |
| `/commands` | 显示命令目录 |
| `/status` | 显示状态 |
| `/whoami` 或 `/id` | 显示身份信息 |

### 群组使用建议

- **`/reasoning` 和 `/verbose`**：在群组中使用时可能暴露内部推理或工具输出，建议保持关闭
- **`/activation`**：可设置群组激活模式为 `mention`（仅提及响应）或 `always`（始终响应）

### 模型切换

- `/model` 立即持久化新模型设置
- 如果代理空闲，下次运行立即使用新模型
- 如果运行中，会标记待切换，在干净的重试点重启到新模型

### 快速路径

- **仅命令消息**：来自白名单发送者的命令立即处理（绕过队列和模型）
- **群组提及门控**：白名单发送者的仅命令消息绕过提及要求

### 特定平台说明

| 平台 | 特殊说明 |
|------|----------|
| **Discord** | 使用自动完成和下拉菜单；`/vc join\|leave\|status` 控制语音频道；`/status` 保留为 `/agentstatus` |
| **Telegram** | 命令支持选择时显示按钮菜单 |
| **Slack** | 需要为每个内置命令创建斜杠命令；参数菜单以 Block Kit 按钮形式发送；`/status` 改为 `/agentstatus` |
| **WhatsApp/WebChat/Signal/iMessage/Google Chat/Teams** | 无原生命令支持，但文本命令仍可用 |

---

*文档整理时间：2026年4月8日*  
*来源：OpenClaw 官方文档 <https://docs.openclaw.ai/tools/slash-commands>*
