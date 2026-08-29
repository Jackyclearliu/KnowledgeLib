# OpenClaw Models CLI 手册

> **文档版本**: 2025-04-21  
> **适用 OpenClaw 版本**: 2026.4.x  
> **官方文档**: https://docs.openclaw.ai/concepts/models

---

## 目录

1. [概述](#1-概述)
2. [模型选择机制](#2-模型选择机制)
3. [官方支持的 Providers](#3-官方支持的-providers)
4. [模型配置详解](#4-模型配置详解)
5. [CLI 命令参考](#5-cli-命令参考)
6. [模型故障转移 (Failover)](#6-模型故障转移-failover)
7. [媒体生成模型配置](#7-媒体生成模型配置)
8. [配置示例](#8-配置示例)
9. [故障排除](#9-故障排除)

---

## 1. 概述

OpenClaw 的 Models CLI 提供了完整的模型管理能力，包括：

- **模型选择**: 支持多层级模型选择和自动故障转移
- **Provider 管理**: 内置 20+ 个 AI Provider，支持自定义 Provider
- **认证管理**: API Key、OAuth、多密钥轮换等多种认证方式
- **媒体生成**: 图像、音乐、视频生成模型的统一配置
- **实时监控**: 模型状态检查和故障诊断

### 快速上手

如果你不想手动编辑配置，推荐使用 onboarding 向导：

```bash
# 交互式配置向导
openclaw onboard

# 指定认证方式
openclaw onboard --auth-choice openai-api-key
openclaw onboard --auth-choice anthropic
```

---

## 2. 模型选择机制

### 2.1 模型选择优先级

OpenClaw 按以下顺序选择模型：

```
1. 主模型 (primary) → agents.defaults.model.primary
2. 备用模型 (fallbacks) → agents.defaults.model.fallbacks (按顺序尝试)
3. Provider 认证故障转移 → 在切换到下一个模型前，先尝试同一 Provider 的其他认证
```

### 2.2 模型引用格式

模型引用使用 `provider/model` 格式：

```
anthropic/claude-opus-4-6
openai/gpt-5.4
google/gemini-3.1-pro-preview
moonshot/kimi-k2.5
```

**注意**: 模型 ID 会被规范化为小写。Provider 别名如 `z.ai/*` 会被规范化为 `zai/*`。

### 2.3 特殊模型配置

| 配置项 | 用途 |  fallback 链 |
|--------|------|-------------|
| `agents.defaults.model` | 文本对话主模型 | primary → fallbacks |
| `agents.defaults.imageModel` | 图像理解模型 | 主模型不支持图像时使用 |
| `agents.defaults.pdfModel` | PDF 处理模型 | 优先 imageModel，其次主模型 |
| `agents.defaults.imageGenerationModel` | 图像生成模型 | primary → fallbacks → 自动检测 |
| `agents.defaults.musicGenerationModel` | 音乐生成模型 | primary → fallbacks → 自动检测 |
| `agents.defaults.videoGenerationModel` | 视频生成模型 | primary → fallbacks → 自动检测 |

---

## 3. 官方支持的 Providers

### 3.1 内置 Providers (pi-ai catalog)

OpenClaw 内置以下 Provider，无需额外配置 `models.providers`，只需设置认证即可使用：

#### OpenAI

| 项目 | 详情 |
|------|------|
| **Provider ID** | `openai` |
| **认证方式** | API Key (`OPENAI_API_KEY`) |
| **密钥轮换** | `OPENAI_API_KEYS`, `OPENAI_API_KEY_1`, `OPENAI_API_KEY_2`, `OPENCLAW_LIVE_OPENAI_KEY` |
| **示例模型** | `openai/gpt-5.4`, `openai/gpt-5.4-pro` |
| **CLI 配置** | `openclaw onboard --auth-choice openai-api-key` |
| **传输方式** | `auto` (WebSocket 优先，SSE 回退) |

**配置示例**:
```json5
{
  env: { OPENAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

**高级参数**:
- `transport`: `"auto"`, `"sse"`, `"websocket"`
- `openaiWsWarmup`: WebSocket 预热 (默认 true)
- `serviceTier`: 优先级处理 (`"auto"`, `"default"`, `"flex"`, `"priority"`)
- `fastMode`: 快速模式 (映射到 `service_tier=priority`)

---

#### Anthropic (Claude)

| 项目 | 详情 |
|------|------|
| **Provider ID** | `anthropic` |
| **认证方式** | API Key (`ANTHROPIC_API_KEY`) 或 Claude CLI 复用 |
| **密钥轮换** | `ANTHROPIC_API_KEYS`, `ANTHROPIC_API_KEY_1`, `ANTHROPIC_API_KEY_2`, `OPENCLAW_LIVE_ANTHROPIC_KEY` |
| **示例模型** | `anthropic/claude-opus-4-6`, `anthropic/claude-sonnet-4-6` |
| **CLI 配置** | `openclaw onboard --auth-choice apiKey` |

**配置示例**:
```json5
{
  env: { ANTHROPIC_API_KEY: "sk-ant-..." },
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

**Claude 4.6 思考模式**:
- 默认 `adaptive` 思考模式
- 可覆盖: `agents.defaults.models["anthropic/<model>"].params.thinking`

**Prompt Caching**:
```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" }, // "none" | "short" (5min) | "long" (1h)
        },
      },
    },
  },
}
```

**Fast Mode**:
- `/fast on` → `service_tier: "auto"`
- `/fast off` → `service_tier: "standard_only"`

---

#### OpenAI Code (Codex)

| 项目 | 详情 |
|------|------|
| **Provider ID** | `openai-codex` |
| **认证方式** | OAuth (ChatGPT 登录) |
| **示例模型** | `openai-codex/gpt-5.4`, `openai-codex/gpt-5.3-codex-spark` |
| **CLI 配置** | `openclaw onboard --auth-choice openai-codex` |
| **传输方式** | `auto` (WebSocket 优先) |

**配置示例**:
```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

**上下文窗口限制**:
- 原生 `contextWindow`: 1,050,000
- 默认运行时 `contextTokens`: 272,000
- 可自定义覆盖:
```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [{ id: "gpt-5.4", contextTokens: 160000 }],
      },
    },
  },
}
```

---

#### Google (Gemini)

| 项目 | 详情 |
|------|------|
| **Provider ID** | `google` |
| **认证方式** | API Key (`GEMINI_API_KEY` 或 `GOOGLE_API_KEY`) |
| **OAuth 方式** | `google-gemini-cli` (Gemini CLI PKCE OAuth) |
| **示例模型** | `google/gemini-3.1-pro-preview`, `google/gemini-3.1-flash-preview` |
| **CLI 配置** | `openclaw onboard --auth-choice gemini-api-key` |

**配置示例**:
```json5
{
  agents: { defaults: { model: { primary: "google/gemini-3.1-pro-preview" } } },
}
```

**Gemini 特性**:
- 图像生成: `google/gemini-3.1-flash-image-preview`
- 视频生成: `google/veo-3.1-fast-generate-preview`
- 音乐生成: `google/lyria-3-clip-preview`
- 文本转语音: `gemini-3.1-flash-tts-preview`
- Web 搜索: Gemini Grounding

**思考模式**:
- Gemini 3.x 使用 `thinkingLevel` (而非 `thinkingBudget`)
- Gemma 4 模型支持思考模式

---

### 3.2 其他订阅制 Provider

| Provider | Provider ID | 认证方式 | 特性 |
|----------|-------------|----------|------|
| **Qwen** | `qwen` | API Key / Coding Plan | 文本模型、媒体理解、视频生成 |
| **MiniMax** | `minimax` | API Key / OAuth | 文本、图像、音乐、视频生成 |
| **Z.AI (GLM)** | `zai` | API Key / Coding Plan | GLM-5 系列、工具流支持 |

### 3.3 代理/聚合 Providers

| Provider | Provider ID | 认证方式 | 说明 |
|----------|-------------|----------|------|
| **OpenCode** | `opencode`, `opencode-go` | `OPENCODE_API_KEY` | Zen/Go 运行时 |
| **OpenRouter** | `openrouter` | `OPENROUTER_API_KEY` | 多提供商聚合 |
| **GitHub Copilot** | `github-copilot` | OAuth | Copilot 订阅复用 |

### 3.4 其他支持的 Providers

| Provider ID | 类型 | 说明 |
|-------------|------|------|
| `moonshot` | 中国 | Kimi 系列模型 |
| `xai` | 美国 | Grok 系列模型 |
| `mistral` | 欧洲 | Mistral 系列模型 |
| `alibaba` | 中国 | 通义千问 |
| `byteplus` | 中国 | Seedance 视频生成 |
| `fal` | 托管 | FLUX 图像、第三方视频 |
| `runway` | 美国 | Gen-4 视频生成 |
| `together` | 托管 | 开源模型聚合 |
| `nvidia` | 美国 | NIM 推理服务 |
| `cloudflare-ai-gateway` | 网关 | Cloudflare AI Gateway |
| `huggingface` | 托管 | Hugging Face 推理 |

---

## 4. 模型配置详解

### 4.1 核心配置键

```json5
{
  agents: {
    defaults: {
      // 主模型配置
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: [
          "anthropic/claude-sonnet-4-6",
          "openai/gpt-5.4"
        ]
      },
      
      // 图像理解模型 (当主模型不支持图像时使用)
      imageModel: {
        primary: "google/gemini-3.1-flash-preview",
        fallbacks: ["openai/gpt-5.4"]
      },
      
      // PDF 处理模型
      pdfModel: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["openai/gpt-5.4"]
      },
      
      // 图像生成模型
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
        fallbacks: ["google/gemini-3.1-flash-image-preview"]
      },
      
      // 音乐生成模型
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
        fallbacks: ["minimax/music-2.5+"]
      },
      
      // 视频生成模型
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
        fallbacks: ["openai/sora-2"]
      },
      
      // 模型白名单 + 别名定义
      models: {
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "openai/gpt-5.4": { alias: "GPT-5.4" },
      },
    },
  },
  
  // 自定义 Provider 配置
  models: {
    providers: {
      "custom-provider": {
        baseUrl: "https://api.custom.com/v1",
        apiKey: "${CUSTOM_API_KEY}",
        models: [
          { id: "model-1", contextWindow: 128000 },
          { id: "model-2", contextWindow: 32000 }
        ]
      }
    }
  }
}
```

### 4.2 模型白名单 (Allowlist)

当设置 `agents.defaults.models` 时，它会成为可用模型的白名单。如果用户选择的模型不在白名单中，OpenClaw 会返回：

```
Model "provider/model" is not allowed. Use /model to list available models.
```

**示例白名单配置**:
```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-sonnet-4-6" },
      models: {
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "openai/gpt-5.4": { alias: "GPT-5.4" },
      },
    },
  },
}
```

### 4.3 单模型参数配置

可以为每个模型设置特定参数：

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            transport: "auto",           // 传输方式
            fastMode: true,              // 快速模式
            serviceTier: "priority",     // 服务层级
            openaiWsWarmup: true,        // WebSocket 预热
            thinking: "medium",          // 思考级别
            cacheRetention: "long",      // 缓存保留 (Anthropic)
            context1m: true,             // 1M 上下文 (Anthropic beta)
            responsesServerCompaction: true,  // 服务器端压缩
          },
        },
        "anthropic/claude-opus-4-6": {
          params: {
            thinking: "adaptive",
            cacheRetention: "short",
            fastMode: true,
          },
        },
      },
    },
  },
}
```

### 4.4 模型注册表 (models.json)

自定义 Provider 配置会被写入 `~/.openclaw/agents/<agentId>/agent/models.json`，合并规则如下：

1. Agent `models.json` 中已存在的非空 `baseUrl` 优先
2. 非 SecretRef 管理的非空 `apiKey` 优先
3. SecretRef 管理的密钥会从源标记刷新
4. 其他字段从配置和目录数据刷新

---

## 5. CLI 命令参考

### 5.1 模型管理命令

```bash
# 显示模型状态 (默认命令)
openclaw models
openclaw models status

# 列出可用模型
openclaw models list                    # 显示已配置模型
openclaw models list --all             # 显示完整目录
openclaw models list --local           # 仅本地 Provider
openclaw models list --provider <name> # 按 Provider 筛选
openclaw models list --plain           # 每行一个模型
openclaw models list --json            # 机器可读输出

# 设置默认模型
openclaw models set <provider/model>
openclaw models set-image <provider/model>

# 认证管理
openclaw models auth login --provider <provider>
openclaw models auth logout --provider <provider>

# 扫描 OpenRouter 免费模型
openclaw models scan
openclaw models scan --no-probe                    # 跳过实时探测
openclaw models scan --min-params 70               # 最小参数量 (B)
openclaw models scan --max-age-days 30             # 最大模型年龄
openclaw models scan --set-default                 # 设置第一个为默认
openclaw models scan --set-image                   # 设置图像模型
```

### 5.2 别名管理

```bash
# 列出别名
openclaw models aliases list

# 添加别名
openclaw models aliases add <alias> <provider/model>
# 示例: openclaw models aliases add gpt4 openai/gpt-5.4

# 移除别名
openclaw models aliases remove <alias>
```

### 5.3 备用模型管理

```bash
# 列出备用模型
openclaw models fallbacks list
openclaw models image-fallbacks list

# 添加备用模型
openclaw models fallbacks add <provider/model>
openclaw models image-fallbacks add <provider/model>

# 移除备用模型
openclaw models fallbacks remove <provider/model>
openclaw models image-fallbacks remove <provider/model>

# 清除所有备用
openclaw models fallbacks clear
openclaw models image-fallbacks clear
```

### 5.4 状态检查选项

```bash
# 基础状态
openclaw models status

# 纯文本输出 (仅主模型)
openclaw models status --plain

# JSON 输出
openclaw models status --json

# 自动化检查 (退出码: 1=缺失/过期, 2=即将过期)
openclaw models status --check

# 实时认证探测
openclaw models status --probe
```

---

## 6. 模型故障转移 (Failover)

### 6.1 故障转移流程

OpenClaw 分两个阶段处理故障：

1. **认证配置轮换** - 在当前 Provider 内尝试其他认证配置
2. **模型备用切换** - 切换到 `agents.defaults.model.fallbacks` 中的下一个模型

**运行时流程**:
```
1. 解析当前会话模型和认证配置偏好
2. 构建模型候选链
3. 使用认证轮换/冷却规则尝试当前 Provider
4. 如果 Provider 耗尽且错误值得故障转移，切换到下一个模型候选
5. 在重试前持久化选定的备用覆盖
6. 如果备用候选失败，回滚备用拥有的会话覆盖字段
7. 如果所有候选都失败，抛出 FallbackSummaryError
```

### 6.2 认证存储

- **存储位置**: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- **运行时状态**: `~/.openclaw/agents/<agentId>/agent/auth-state.json`
- **凭证类型**:
  - `type: "api_key"` → `{ provider, key }`
  - `type: "oauth"` → `{ provider, access, refresh, expires, email? }`

### 6.3 冷却机制

当认证配置因认证/速率限制错误失败时，OpenClaw 会将其标记为冷却状态。

**冷却时间** (指数退避):
- 第 1 次: 1 分钟
- 第 2 次: 5 分钟
- 第 3 次: 25 分钟
- 上限: 1 小时

**状态存储**:
```json
{
  "usageStats": {
    "provider:profile": {
      "lastUsed": 1736160000000,
      "cooldownUntil": 1736160600000,
      "errorCount": 2
    }
  }
}
```

**账单禁用**:
- 账单/信用失败 (如"余额不足") 会标记为禁用而非冷却
- 默认禁用退避: 5 小时起，每次失败翻倍，上限 24 小时

### 6.4 轮换顺序

1. **显式配置**: `auth.order[provider]` (如果设置)
2. **已配置配置**: `auth.profiles` 按 Provider 筛选
3. **存储的配置**: `auth-profiles.json` 中的条目

**默认轮询顺序**:
- 主键: 配置类型 (**OAuth 先于 API Key**)
- 次键: `usageStats.lastUsed` (同一类型内最旧优先)
- 冷却/禁用的配置移到末尾，按最早过期时间排序

### 6.5 会话粘性

OpenClaw **每个会话固定选定的认证配置** 以保持 Provider 缓存热。固定配置会重复使用直到：
- 会话重置 (`/new` / `/reset`)
- 压缩完成 (压缩计数增加)
- 配置进入冷却/禁用状态

**手动选择**: `/model ...@<profileId>` 设置用户覆盖，自动轮换直到新会话开始。

---

## 7. 媒体生成模型配置

### 7.1 图像生成

**支持的 Providers**:

| Provider | 默认模型 | 编辑支持 | API Key |
|----------|----------|----------|---------|
| OpenAI | `gpt-image-1` | 是 (最多5张图) | `OPENAI_API_KEY` |
| Google | `gemini-3.1-flash-image-preview` | 是 | `GEMINI_API_KEY` |
| fal | `fal-ai/flux/dev` | 是 | `FAL_KEY` |
| MiniMax | `image-01` | 是 | `MINIMAX_API_KEY` |
| ComfyUI | `workflow` | 是 | `COMFY_API_KEY` |
| Vydra | `grok-imagine` | 否 | `VYDRA_API_KEY` |

**配置示例**:
```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
        fallbacks: [
          "google/gemini-3.1-flash-image-preview",
          "fal/fal-ai/flux/dev"
        ],
      },
    },
  },
}
```

**工具参数**:
- `prompt`: 图像生成提示词
- `action`: `"generate"` (默认) 或 `"list"`
- `model`: Provider/model 覆盖
- `image`/`images`: 参考图像 (编辑模式)
- `size`: 尺寸提示 (`1024x1024`, `1536x1024`, 等)
- `aspectRatio`: 宽高比 (`1:1`, `16:9`, 等)
- `resolution`: 分辨率 (`1K`, `2K`, `4K`)
- `count`: 生成数量 (1-4)

### 7.2 音乐生成

**支持的 Providers**:

| Provider | 默认模型 | 参考输入 | 支持控制 |
|----------|----------|----------|----------|
| Google | `lyria-3-clip-preview` | 最多10张图 | `lyrics`, `instrumental`, `format` |
| MiniMax | `music-2.5+` | 无 | `lyrics`, `instrumental`, `durationSeconds`, `format=mp3` |
| ComfyUI | `workflow` | 最多1张图 | 工作流定义 |

**配置示例**:
```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
        fallbacks: ["minimax/music-2.5+"],
      },
    },
  },
}
```

**异步行为**:
- 会话支持的 Agent 运行: 创建后台任务，完成后唤醒 Agent 发布结果
- 重复预防: 任务 `queued` 或 `running` 时，后续调用返回任务状态
- 状态检查: `action: "status"`

### 7.3 视频生成

**支持的 Providers**:

| Provider | 默认模型 | 文本 | 图像参考 | 视频参考 | API Key |
|----------|----------|------|----------|----------|---------|
| Google | `veo-3.1-fast-generate-preview` | 是 | 是 | 是 | `GEMINI_API_KEY` |
| OpenAI | `sora-2` | 是 | 是 | 是 | `OPENAI_API_KEY` |
| MiniMax | `MiniMax-Hailuo-2.3` | 是 | 是 | 否 | `MINIMAX_API_KEY` |
| BytePlus | `seedance-1-5-pro-251215` | 是 | 是 | 否 | `BYTEPLUS_API_KEY` |
| Runway | `gen4.5` | 是 | 是 | 是 | `RUNWAYML_API_SECRET` |
| Qwen | `wan2.6-t2v` | 是 | 是 | 是 | `QWEN_API_KEY` |
| xAI | `grok-imagine-video` | 是 | 是 | 是 | `XAI_API_KEY` |

**配置示例**:
```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
        fallbacks: [
          "openai/sora-2",
          "minimax/MiniMax-Hailuo-2.3"
        ],
      },
    },
  },
}
```

**工具参数**:
- `prompt`: 视频描述
- `action`: `"generate"`, `"status"`, `"list"`
- `image`/`images`: 参考图像 (最多9张)
- `video`/`videos`: 参考视频 (最多4个)
- `aspectRatio`: 宽高比
- `resolution`: 分辨率 (`480P`, `720P`, `1080P`)
- `durationSeconds`: 目标时长 (秒)
- `audio`: 启用生成音频
- `watermark`: 水印开关

---

## 8. 配置示例

### 8.1 基础配置

```json5
{
  env: {
    ANTHROPIC_API_KEY: "sk-ant-...",
    OPENAI_API_KEY: "sk-...",
  },
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["openai/gpt-5.4"],
      },
    },
  },
}
```

### 8.2 多 Provider 完整配置

```json5
{
  env: {
    ANTHROPIC_API_KEY: "sk-ant-...",
    OPENAI_API_KEY: "sk-...",
    GEMINI_API_KEY: "...",
    MINIMAX_API_KEY: "...",
  },
  agents: {
    defaults: {
      // 主模型配置
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: [
          "anthropic/claude-sonnet-4-6",
          "openai/gpt-5.4",
          "google/gemini-3.1-pro-preview",
        ],
      },
      
      // 模型白名单和别名
      models: {
        "anthropic/claude-opus-4-6": {
          alias: "Opus",
          params: {
            thinking: "adaptive",
            cacheRetention: "long",
          },
        },
        "anthropic/claude-sonnet-4-6": {
          alias: "Sonnet",
          params: { fastMode: true },
        },
        "openai/gpt-5.4": { alias: "GPT-5" },
        "google/gemini-3.1-pro-preview": { alias: "Gemini-Pro" },
      },
      
      // 媒体生成模型
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
        fallbacks: ["google/gemini-3.1-flash-image-preview"],
      },
      
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
        fallbacks: ["minimax/music-2.5+"],
      },
      
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
        fallbacks: ["openai/sora-2"],
      },
    },
  },
  
  // 认证配置顺序 (可选)
  auth: {
    order: {
      anthropic: ["anthropic:default"],
      openai: ["openai:default"],
    },
  },
}
```

### 8.3 自定义 Provider 配置

```json5
{
  models: {
    providers: {
      "my-openai-compatible": {
        baseUrl: "https://api.example.com/v1",
        apiKey: "${MY_API_KEY}",
        models: [
          {
            id: "llama-3-70b",
            contextWindow: 128000,
            contextTokens: 32000,
          },
        ],
      },
    },
  },
  agents: {
    defaults: {
      model: {
        primary: "my-openai-compatible/llama-3-70b",
      },
    },
  },
}
```

### 8.4 每 Agent 模型覆盖

```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-sonnet-4-6" },
    },
    list: [
      {
        id: "research",
        default: true,
        model: "anthropic/claude-opus-4-6",
      },
      {
        id: "alerts",
        model: "openai/gpt-5.4-mini",
        params: {
          cacheRetention: "none",
        },
      },
    ],
  },
}
```

---

## 9. 故障排除

### 9.1 常见错误

**"Model is not allowed"**
- 原因: 选择的模型不在 `agents.defaults.models` 白名单中
- 解决: 添加模型到白名单，或清除白名单配置

**"No API key found for provider"**
- 原因: 认证是按 Agent 隔离的，新 Agent 不继承主 Agent 的密钥
- 解决: 重新运行 onboarding，或在网关主机配置 API Key

**"No credentials found for profile"**
- 原因: 认证配置不存在或已过期
- 解决: 运行 `openclaw models status` 查看活跃配置，重新运行 onboarding

**"All models are temporarily rate-limited"**
- 原因: 所有候选模型都处于速率限制冷却期
- 解决: 检查 `openclaw models status --json` 查看 `auth.unusableProfiles`，等待冷却结束或添加其他认证配置

### 9.2 诊断命令

```bash
# 检查模型状态
openclaw models status

# 详细 JSON 输出
openclaw models status --json

# 检查认证问题
openclaw models status --check

# 实时探测
openclaw models status --probe

# 列出所有可用模型
openclaw models list --all

# 查看特定 Provider
openclaw models list --provider anthropic

# 检查网关状态
openclaw status

# 运行诊断
openclaw doctor
```

### 9.3 环境变量参考

| 变量 | 用途 |
|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 |
| `OPENAI_API_KEYS` | OpenAI 多密钥轮换 |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 |
| `GEMINI_API_KEY` | Google Gemini API 密钥 |
| `GOOGLE_API_KEY` | Google API 密钥 (备选) |
| `MOONSHOT_API_KEY` | Moonshot API 密钥 |
| `XAI_API_KEY` | xAI API 密钥 |
| `OPENROUTER_API_KEY` | OpenRouter API 密钥 |
| `FAL_KEY` | fal API 密钥 |
| `MINIMAX_API_KEY` | MiniMax API 密钥 |
| `RUNWAYML_API_SECRET` | Runway API 密钥 |
| `BYTEPLUS_API_KEY` | BytePlus API 密钥 |

---

## 附录 A: 术语表

| 术语 | 说明 |
|------|------|
| **Provider** | AI 模型提供商 (如 OpenAI, Anthropic) |
| **Model Ref** | 模型引用格式 `provider/model` |
| **Primary** | 主模型，优先使用 |
| **Fallback** | 备用模型，主模型失败时使用 |
| **Auth Profile** | 认证配置，包含 API Key 或 OAuth 令牌 |
| **Cooldown** | 认证配置的冷却期，失败后暂时禁用 |
| **Allowlist** | 允许使用的模型列表 |
| **Alias** | 模型别名，简化引用 |
| **Context Window** | 模型原生上下文窗口大小 |
| **Context Tokens** | 运行时有效的上下文令牌上限 |
| **OAuth** | 开放授权，用于订阅制认证 |
| **API Key** | API 密钥认证 |

---

## 附录 B: 相关链接

- **官方文档**: https://docs.openclaw.ai/concepts/models
- **Model Providers**: https://docs.openclaw.ai/concepts/model-providers
- **Model Failover**: https://docs.openclaw.ai/concepts/model-failover
- **Image Generation**: https://docs.openclaw.ai/tools/image-generation
- **Music Generation**: https://docs.openclaw.ai/tools/music-generation
- **Video Generation**: https://docs.openclaw.ai/tools/video-generation
- **Configuration Reference**: https://docs.openclaw.ai/gateway/configuration-reference
- **OpenClaw 官网**: https://openclaw.ai
- **GitHub**: https://github.com/openclaw/openclaw
- **Discord 社区**: https://discord.com/invite/clawd

---

_本文档基于 OpenClaw 官方文档整理，最后更新: 2025-04-21_