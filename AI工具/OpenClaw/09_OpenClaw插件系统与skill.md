# OpenClaw 插件系统与 Skill 系统手册

> **文档版本**：基于 OpenClaw 2026.5.28 版本文档整理
> **适用对象**：希望扩展本地部署 OpenClaw 能力边界的用户
> **核心目标**：掌握插件（Plugin）和 Skill 的搜索、安装、配置及多 Agent 场景下的精细化管理

---

## 目录

1. [OpenClaw 插件系统详解](#一-openclaw-插件系统详解)
   - 1.1 [什么是插件](#11-什么是插件)
   - 1.2 [插件能提供哪些能力](#12-插件能提供哪些能力)
   - 1.3 [去哪里搜索插件](#13-去哪里搜索插件)
   - 1.4 [如何安装插件](#14-如何安装插件)
   - 1.5 [如何配置插件](#15-如何配置插件)
   - 1.6 [多 Agent 场景下的插件配置](#16-多-agent-场景下的插件配置)
2. [OpenClaw Skill 系统详解](#二-openclaw-skill-系统详解)
   - 2.1 [什么是 Skill](#21-什么是-skill)
   - 2.2 [Skill 能提供哪些能力](#22-skill-能提供哪些能力)
   - 2.3 [去哪里搜索 Skill](#23-去哪里搜索-skill)
   - 2.4 [如何安装 Skill](#24-如何安装-skill)
   - 2.5 [如何配置 Skill](#25-如何配置-skill)
   - 2.6 [多 Agent 场景下的 Skill 配置](#26-多-agent-场景下的-skill-配置)
3. [多 Agent 共享插件与 Skill 配置](#三-多-agent-共享插件与-skill-配置)
4. [CLI 命令完整参考](#四-cli-命令完整参考)
   - 4.1 [插件相关命令](#41-插件相关命令)
   - 4.2 [Skill 相关命令](#42-skill-相关命令)
5. [其他重要内容](#五-其他重要内容)
   - 5.1 [插件 Bundle 与 IDE 兼容](#51-插件-bundle-与-ide-兼容)
   - 5.2 [Skill 创建指南](#52-skill-创建指南)
   - 5.3 [安全注意事项](#53-安全注意事项)
   - 5.4 [常见问题排查](#54-常见问题排查)

---

## 一、OpenClaw 插件系统详解

### 1.1 什么是插件

OpenClaw 的**插件（Plugin）**是扩展系统能力的核心机制。每个插件都是一个独立的 Node.js 包（npm package），通过标准接口向 OpenClaw 注册新的能力。

**插件的关键特征**：

- **独立包形态**：每个插件是一个可发布的 npm 包，带有 `openclaw.plugin.json` 清单文件
- **声明式注册**：通过清单文件声明插件 ID、版本、能力类型、依赖关系
- **动态加载**：OpenClaw 在启动时扫描并加载已安装的插件
- **热更新支持**：可通过 CLI 命令安装、更新、卸载，无需重启整个系统

**插件与 Skill 的核心区别**：

| 维度 | 插件（Plugin） | Skill |
|------|---------------|-------|
| 技术形态 | Node.js npm 包 | Markdown 文件（SKILL.md）+ 可选脚本 |
| 能力范围 | 底层系统扩展（Provider、Channel、CLI 等） | 上层工作流封装（工具调用、任务模板） |
| 安装方式 | `openclaw plugins install` | `openclaw skills install` 或直接放置文件 |
| 配置位置 | `plugins.entries` | `skills.entries` |
| 开发复杂度 | 需要编写 Node.js 代码 | 主要是 Markdown + 可选脚本 |

### 1.2 插件能提供哪些能力

OpenClaw 插件系统采用**能力模型（Capability Model）**，插件可以注册以下类型的能力：

#### 1.2.1 Provider 插件

向 OpenClaw 添加新的 AI 模型提供商：

- **模型推理**：如添加本地 Ollama、Together AI、Fireworks 等后端
- **嵌入模型**：提供文本向量化的模型源
- **图像生成**：如 fal.ai、Replicate 等图像生成服务

**示例**：`@openclaw/anthropic` 插件提供 Claude 系列模型的访问能力。

#### 1.2.2 Channel 插件

扩展 OpenClaw 的消息通道，让 Agent 可以通过更多平台与用户交互：

- **即时通讯**：Discord、Slack、Telegram、WhatsApp
- **邮件**：Email（IMAP/SMTP）
- **Web**：WebSocket、SSE（Server-Sent Events）
- **语音**：WebRTC、电话集成

**示例**：`@openclaw/discord` 插件让 Agent 可以接入 Discord 服务器。

#### 1.2.3 Tool 插件

向 Agent 的工具箱添加新的可调用工具：

- **文件系统操作**：高级文件搜索、批量重命名
- **网络工具**：Web 搜索、API 调用、爬虫
- **开发工具**：Git 操作、代码分析、数据库查询
- **多媒体**：音频转录、图像处理、视频分析

**示例**：`@openclaw/web-search` 插件提供网页搜索工具。

#### 1.2.4 CLI Backend 插件

扩展 `openclaw` CLI 命令本身：

- 添加新的子命令
- 扩展现有命令的选项
- 提供自定义的输出格式化

#### 1.2.5 Bundle 插件

特殊的兼容层插件，用于与第三方 AI IDE 和工具集成（详见 [5.1 节](#51-插件-bundle-与-ide-兼容)）：

- **Codex Bundle**：兼容 OpenAI Codex CLI
- **Claude Bundle**：兼容 Claude Code
- **Cursor Bundle**：兼容 Cursor Agent

### 1.3 去哪里搜索插件

#### 1.3.1 ClawHub（官方插件市场）

OpenClaw 内置了 **ClawHub** 插件市场，这是搜索和安装插件的主要渠道：

```bash
# 列出所有可用插件
openclaw plugins search

# 搜索特定关键词
openclaw plugins search <keyword>

# 查看插件详情
openclaw plugins info <plugin-id>
```

#### 1.3.2 npm 注册表

所有 OpenClaw 插件都是标准的 npm 包，可以在 npm 上搜索：

```bash
# 通过 npm 搜索
npm search openclaw-plugin

# 或者直接安装已知的包名
openclaw plugins install <npm-package-name>
```

#### 1.3.3 GitHub / Git 仓库

可以直接从 Git 仓库安装开发中的插件：

```bash
# 从 GitHub 安装
openclaw plugins install github:<owner>/<repo>

# 从任意 Git 仓库
openclaw plugins install git+<url>
```

#### 1.3.4 本地路径

对于正在开发的插件，可以从本地路径安装：

```bash
# 从本地目录安装（支持符号链接）
openclaw plugins install /path/to/plugin

# 从本地 tarball 安装
openclaw plugins install /path/to/package.tgz
```

#### 1.3.5 内置插件（Bundled Plugins）

OpenClaw 核心安装包含一组内置插件，开箱即用，无需单独安装。

### 1.4 如何安装插件

#### 1.4.1 基本安装命令

```bash
# 从 ClawHub 安装（推荐）
openclaw plugins install <plugin-id>

# 安装特定版本
openclaw plugins install <plugin-id>@<version>

# 从 npm 包安装
openclaw plugins install <npm-package-name>

# 从 GitHub 安装
openclaw plugins install github:<owner>/<repo>

# 从本地路径安装（开发调试）
openclaw plugins install /path/to/plugin
```

#### 1.4.2 安装示例

```bash
# 安装 Discord 通道插件
openclaw plugins install @openclaw/discord

# 安装 Web 搜索工具插件
openclaw plugins install @openclaw/web-search

# 安装特定版本的 Anthropic 提供商
openclaw plugins install @openclaw/anthropic@1.2.0

# 从 GitHub 开发分支安装
openclaw plugins install github:openclaw/web-search#main
```

#### 1.4.3 更新插件

```bash
# 更新所有插件到最新版本
openclaw plugins update

# 更新指定插件
openclaw plugins update <plugin-id>
```

#### 1.4.4 卸载插件

```bash
# 卸载指定插件
openclaw plugins uninstall <plugin-id>

# 强制卸载（忽略依赖检查）
openclaw plugins uninstall <plugin-id> --force
```

#### 1.4.5 查看已安装插件

```bash
# 列出所有已安装插件
openclaw plugins list

# 查看插件详细信息
openclaw plugins info <plugin-id>
```

#### 1.4.6 安装覆盖（测试用途）

对于开发者测试本地打包的插件，可以使用环境变量覆盖安装源：

```bash
export OPENCLAW_ALLOW_PLUGIN_INSTALL_OVERRIDES=1
export OPENCLAW_PLUGIN_INSTALL_OVERRIDES='{
  "codex": "npm-pack:/tmp/openclaw-codex-2026.5.8.tgz",
  "openclaw-web-search": "npm:@openclaw/web-search@2026.5.8"
}'
```

> ⚠️ **安全警告**：覆盖功能仅用于隔离测试环境，切勿在生产环境使用。

### 1.5 如何配置插件

#### 1.5.1 配置文件位置

插件配置位于 OpenClaw 主配置文件中：

```
~/.openclaw/openclaw.json
```

#### 1.5.2 插件配置结构

```json5
{
  plugins: {
    // 已安装插件的实例配置
    entries: {
      "plugin-id-1": {
        enabled: true,
        config: {
          // 插件特定的配置项
          apiKey: "your-api-key",
          endpoint: "https://api.example.com"
        }
      },
      "plugin-id-2": {
        enabled: false,  // 禁用此插件
      }
    }
  }
}
```

#### 1.5.3 插件配置字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `enabled` | boolean | 是否启用该插件 |
| `config` | object | 插件特定的配置参数 |
| `config.apiKey` | string/object | API 密钥（支持明文或 SecretRef） |
| `config.endpoint` | string | 自定义服务端点 URL |

#### 1.5.4 使用 SecretRef 保护敏感信息

对于 API 密钥等敏感配置，建议使用 SecretRef：

```json5
{
  plugins: {
    entries: {
      "@openclaw/anthropic": {
        enabled: true,
        config: {
          apiKey: {
            source: "env",      // 从环境变量获取
            provider: "default",
            id: "ANTHROPIC_API_KEY"
          }
        }
      }
    }
  }
}
```

SecretRef 支持的 `source` 类型：
- `"env"`：从环境变量读取
- `"file"`：从文件读取
- `"keychain"`：从系统密钥链读取（macOS/Linux）

### 1.6 多 Agent 场景下的插件配置

#### 1.6.1 Agent 默认插件配置

在 `agents.defaults` 中设置所有 Agent 的默认插件：

```json5
{
  agents: {
    defaults: {
      // 默认启用的插件列表
      plugins: ["@openclaw/web-search", "@openclaw/github"],
      
      // 默认插件配置
      pluginConfig: {
        "@openclaw/web-search": {
          engine: "duckduckgo"
        }
      }
    }
  }
}
```

#### 1.6.2 特定 Agent 的插件配置

为单个 Agent 覆盖默认插件设置：

```json5
{
  agents: {
    list: [
      {
        id: "coder",
        name: "代码助手",
        // 完全替换默认插件列表
        plugins: ["@openclaw/github", "@openclaw/git"],
        pluginConfig: {
          "@openclaw/github": {
            token: { source: "env", id: "GITHUB_TOKEN_CODER" }
          }
        }
      },
      {
        id: "writer",
        name: "写作助手",
        // 继承默认插件，不覆盖
        // plugins 字段省略时会继承 agents.defaults.plugins
      }
    ]
  }
}
```

#### 1.6.3 插件继承与覆盖规则

| 配置层级 | 作用范围 | 优先级 |
|---------|---------|--------|
| `agents.list[].plugins` | 特定 Agent | 最高（完全替换默认值） |
| `agents.defaults.plugins` | 所有 Agent | 中等（可被列表项覆盖） |
| `plugins.entries` | 全局 | 最低（基础配置） |

**关键规则**：
- `agents.list[].plugins` 是**完整替换**而非合并。如果指定了此字段，默认值将被完全忽略。
- `agents.list[].pluginConfig` 会合并而非替换默认配置。

---

## 二、OpenClaw Skill 系统详解

### 2.1 什么是 Skill

OpenClaw 的 **Skill（技能）** 是一种轻量级的 Agent 能力扩展机制，通过 **SKILL.md** 文件定义工作流和工具调用模板。

**Skill 的核心特征**：

- **Markdown 驱动**：主文件是 `SKILL.md`，人类可读、易于编写
- **工作流封装**：将多步骤任务封装为可复用的模板
- **工具组合**：组合多个工具完成复杂任务
- **即时生效**：修改 SKILL.md 后通常立即生效（无需重启）

**Skill 与插件的对比**：

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 添加新的 AI 模型提供商 | 插件 | 需要 Node.js 运行时集成 |
| 添加新的消息通道 | 插件 | 需要长期运行的服务进程 |
| 封装常见工作流 | Skill | 更轻量、更易维护 |
| 组合现有工具 | Skill | 无需编写代码 |
| 自定义任务模板 | Skill | Markdown 即可描述 |

### 2.2 Skill 能提供哪些能力

#### 2.2.1 工作流模板

将重复性任务封装为标准工作流：

- **代码审查流程**：拉取 PR → 分析 diff → 生成审查意见 → 发布评论
- **文档生成**：读取代码 → 提取注释 → 生成 API 文档 → 保存文件
- **数据分析**：获取数据源 → 清洗处理 → 生成图表 → 导出报告

#### 2.2.2 工具组合

将多个工具组合为单一调用：

- **智能搜索**：网页搜索 → 内容提取 → 摘要生成
- **多媒体处理**：下载图像 → 分析内容 → 生成描述 → 保存元数据
- **自动化部署**：Git 操作 → 构建 → 测试 → 发布

#### 2.2.3 知识库集成

- **文档检索**：连接内部 Wiki、Notion、Confluence
- **代码搜索**：索引代码库，支持语义搜索
- **FAQ 应答**：基于预设知识库回答问题

#### 2.2.4 自定义命令

通过 `SKILL.md` 定义特殊的斜杠命令：

```markdown
---
name: "weather"
description: "获取指定城市的天气信息"
commands:
  - name: "/weather"
    description: "查询天气"
---

当用户请求天气时，使用 `weather` 工具获取数据并以友好格式呈现。
```

### 2.3 去哪里搜索 Skill

#### 2.3.1 ClawHub Skill 市场

```bash
# 搜索可用 Skill
openclaw skills search

# 搜索特定关键词
openclaw skills search <keyword>

# 查看 Skill 详情
openclaw skills info <skill-name>
```

#### 2.3.2 内置 Skill（Bundled Skills）

OpenClaw 核心包含一组内置 Skill，开箱即用：

```bash
# 查看所有内置 Skill
openclaw skills list --bundled
```

常见内置 Skill：
- `github`：GitHub 操作（Issue、PR、代码搜索）
- `weather`：天气查询
- `peekaboo`：系统信息查看
- `image-lab`：图像生成与编辑（需配置 API 密钥）

#### 2.3.3 本地和 Workspace Skill

OpenClaw 会自动扫描以下目录中的 Skill：

| 目录 | 优先级 | 说明 |
|------|--------|------|
| `<workspace>/skills` | 最高 | 当前工作空间的 Skill |
| `<workspace>/.agents/skills` | 高 | 工作空间的 Agent Skill |
| `~/.agents/skills` | 中 | 用户个人 Skill |
| `~/.openclaw/skills` | 中 | OpenClaw 管理的 Skill |
| `bundled skills` | 低 | 内置 Skill |
| `skills.load.extraDirs` | 最低 | 额外配置的目录 |

#### 2.3.4 GitHub / 社区

社区维护的 Skill 仓库：

```bash
# 从 GitHub 安装社区 Skill
openclaw skills install github:<owner>/<repo>
```

### 2.4 如何安装 Skill

#### 2.4.1 从 ClawHub 安装

```bash
# 安装指定 Skill
openclaw skills install <skill-name>

# 安装特定版本
openclaw skills install <skill-name>@<version>
```

#### 2.4.2 从 GitHub 安装

```bash
openclaw skills install github:<owner>/<repo>
```

#### 2.4.3 手动安装（直接放置文件）

对于自定义 Skill，直接将 `SKILL.md` 文件放入扫描目录：

```bash
# 创建个人 Skill 目录
mkdir -p ~/.agents/skills/my-skill

# 编写 SKILL.md
cat > ~/.agents/skills/my-skill/SKILL.md << 'EOF'
---
name: "my-skill"
description: "我的自定义技能"
---

# 使用说明

当用户要求执行 xxx 时，按以下步骤操作：
1. 使用 `tool_a` 获取数据
2. 使用 `tool_b` 处理数据
3. 向用户展示结果
EOF
```

#### 2.4.4 从本地路径安装

```bash
openclaw skills install /path/to/skill-directory
```

#### 2.4.5 查看已安装 Skill

```bash
# 列出所有可用 Skill（包括内置、已安装、本地）
openclaw skills list

# 仅查看已安装的 Skill
openclaw skills list --installed

# 查看特定 Skill 详情
openclaw skills info <skill-name>
```

#### 2.4.6 更新和卸载

```bash
# 更新所有 Skill
openclaw skills update

# 更新指定 Skill
openclaw skills update <skill-name>

# 卸载 Skill
openclaw skills uninstall <skill-name>
```

### 2.5 如何配置 Skill

#### 2.5.1 Skill 配置结构

```json5
{
  skills: {
    // 内置 Skill 白名单（可选，限制可用的内置 Skill）
    allowBundled: ["github", "weather", "peekaboo"],
    
    // Skill 加载配置
    load: {
      // 额外扫描目录
      extraDirs: ["~/Projects/agent-scripts/skills"],
      
      // 允许的符号链接目标（用于跨仓库布局）
      allowSymlinkTargets: ["~/Projects/manager/skills"],
      
      // 是否监听文件变化（默认 true）
      watch: true,
      
      // 监听防抖时间（毫秒）
      watchDebounceMs: 250,
    },
    
    // 安装配置
    install: {
      // 优先使用 Homebrew 安装器
      preferBrew: true,
      
      // Node 包管理器（npm | pnpm | yarn | bun）
      nodeManager: "npm",
      
      // 是否允许上传的归档安装
      allowUploadedArchives: false,
    },
    
    // 各 Skill 的实例配置
    entries: {
      "image-lab": {
        enabled: true,
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" },
        env: {
          GEMINI_API_KEY: "***",
        },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },  // 禁用此 Skill
    },
  },
}
```

#### 2.5.2 关键配置字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `allowBundled` | string[] | 内置 Skill 白名单，仅列出的内置 Skill 可用 |
| `load.extraDirs` | string[] | 额外扫描目录（最低优先级） |
| `load.allowSymlinkTargets` | string[] | 允许的符号链接目标目录 |
| `load.watch` | boolean | 是否监听文件变化并自动刷新 |
| `install.preferBrew` | boolean | 优先使用 Homebrew 安装依赖 |
| `install.nodeManager` | string | Skill 安装使用的 Node 包管理器 |
| `entries.<skill>` | object | 特定 Skill 的配置 |
| `entries.<skill>.enabled` | boolean | 是否启用该 Skill |
| `entries.<skill>.apiKey` | string/object | Skill 的主 API 密钥 |
| `entries.<skill>.env` | object | 注入的环境变量 |

#### 2.5.3 符号链接与跨仓库布局

当 Skill 目录通过符号链接指向外部仓库时，需要显式配置允许的目标：

```json5
{
  skills: {
    load: {
      extraDirs: ["~/Projects/manager/skills"],
      allowSymlinkTargets: ["~/Projects/manager/skills"],
    },
  },
}
```

> 如果不配置 `allowSymlinkTargets`，指向外部目录的符号链接会被跳过，并记录日志：`Skipping escaped skill path outside its configured root`

#### 2.5.4 图像生成 Skill 配置示例

```json5
{
  agents: {
    defaults: {
      // 首选图像生成模型
      imageGenerationModel: {
        primary: "google/gemini-3-pro-image-preview"
        // 或者使用 fal：
        // primary: "fal/fal-ai/flux/dev"
      }
    }
  },
  skills: {
    entries: {
      "image-lab": {
        enabled: true,
        apiKey: { source: "env", id: "GEMINI_API_KEY" }
      }
    }
  }
}
```

### 2.6 多 Agent 场景下的 Skill 配置

#### 2.6.1 Agent 默认 Skill 配置

```json5
{
  agents: {
    defaults: {
      // 所有 Agent 默认可用的 Skill
      skills: ["github", "weather"],
    },
    list: [
      { id: "writer" },  // 继承默认 Skill：github, weather
      { id: "docs", skills: ["docs-search"] },  // 替换默认 Skill
      { id: "locked-down", skills: [] },  // 无 Skill
    ],
  },
}
```

#### 2.6.2 Skill 继承与覆盖规则

| 规则 | 说明 |
|------|------|
| `agents.defaults.skills` | 默认基线白名单，被省略 `skills` 的 Agent 继承 |
| `agents.list[].skills` | 特定 Agent 的最终白名单，**完全替换**默认值 |
| `skills: []` | 显式空列表表示该 Agent 无任何 Skill |
| 省略 `skills` | 继承 `agents.defaults.skills` |

> ⚠️ **重要**：`agents.list[].skills` 是**替换**而非**合并**。如果指定了此字段，默认值将被完全忽略。

#### 2.6.3 完整多 Agent Skill 配置示例

```json5
{
  skills: {
    allowBundled: ["github", "weather", "peekaboo", "image-lab"],
    entries: {
      "image-lab": {
        enabled: true,
        apiKey: { source: "env", id: "GEMINI_API_KEY" }
      }
    }
  },
  agents: {
    defaults: {
      skills: ["github", "weather"],  // 默认所有 Agent 都有 github 和 weather
    },
    list: [
      {
        id: "developer",
        name: "开发助手",
        // 继承默认 Skill
      },
      {
        id: "designer",
        name: "设计助手",
        skills: ["image-lab", "peekaboo"],  // 替换默认
      },
      {
        id: "manager",
        name: "管理助手",
        skills: ["github"],  // 仅保留 github
      }
    ]
  }
}
```

---

## 三、多 Agent 共享插件与 Skill 配置

### 3.1 共享配置策略

在多 Agent 场景中，推荐采用以下配置策略：

#### 策略 1：默认值 + 特定覆盖（推荐）

```json5
{
  // 全局工具和插件配置
  plugins: {
    entries: {
      "@openclaw/web-search": {
        enabled: true,
        config: { engine: "duckduckgo" }
      }
    }
  },
  skills: {
    entries: {
      "weather": { enabled: true }
    }
  },
  
  // Agent 配置
  agents: {
    defaults: {
      // 默认所有 Agent 共享
      plugins: ["@openclaw/web-search"],
      skills: ["weather"],
    },
    list: [
      {
        id: "general",
        // 继承默认值
      },
      {
        id: "coder",
        // 继承默认插件，添加专属插件
        plugins: ["@openclaw/web-search", "@openclaw/github"],
        skills: ["weather", "github"],
      }
    ]
  }
}
```

#### 策略 2：完全隔离

```json5
{
  agents: {
    defaults: {
      plugins: [],  // 默认无插件
      skills: [],   // 默认无 Skill
    },
    list: [
      {
        id: "agent-a",
        plugins: ["@openclaw/web-search"],
        skills: ["weather"],
      },
      {
        id: "agent-b",
        plugins: ["@openclaw/github"],
        skills: ["github"],
      }
    ]
  }
}
```

### 3.2 配置优先级总结

```
优先级从高到低：

1. agents.list[].plugins / agents.list[].skills
   → 特定 Agent 的显式配置（完全替换）
   
2. agents.defaults.plugins / agents.defaults.skills
   → 所有 Agent 的默认配置
   
3. plugins.entries / skills.entries
   → 全局插件/Skill 配置（启用状态、密钥等）
   
4. 内置插件/Skill
   → 核心自带的能力
```

### 3.3 环境变量与密钥隔离

不同 Agent 可以使用不同的 API 密钥：

```json5
{
  agents: {
    list: [
      {
        id: "team-a",
        pluginConfig: {
          "@openclaw/anthropic": {
            apiKey: { source: "env", id: "ANTHROPIC_KEY_TEAM_A" }
          }
        }
      },
      {
        id: "team-b",
        pluginConfig: {
          "@openclaw/anthropic": {
            apiKey: { source: "env", id: "ANTHROPIC_KEY_TEAM_B" }
          }
        }
      }
    ]
  }
}
```

### 3.4 共享工作区 Skill

将工作区级别的 Skill 放在 `<workspace>/skills` 目录，所有在该工作区运行的 Agent 自动可用：

```
my-project/
├── .agents/
│   └── skills/          # 项目 Agent 专属 Skill
├── skills/              # 工作区共享 Skill
│   ├── code-review/
│   │   └── SKILL.md
│   └── deploy/
│       └── SKILL.md
└── ...
```

---

## 四、CLI 命令完整参考

### 4.1 插件相关命令

#### `openclaw plugins install`

安装插件。

```bash
# 从 ClawHub 安装
openclaw plugins install <plugin-id>

# 安装特定版本
openclaw plugins install <plugin-id>@<version>

# 从 npm 包安装
openclaw plugins install <npm-package>

# 从 GitHub 安装
openclaw plugins install github:<owner>/<repo>

# 从本地路径安装
openclaw plugins install /path/to/plugin

# 选项
openclaw plugins install <id> --version <ver>   # 指定版本
openclaw plugins install <id> --force           # 强制重新安装
```

#### `openclaw plugins uninstall`

卸载插件。

```bash
openclaw plugins uninstall <plugin-id>
openclaw plugins uninstall <id> --force  # 强制卸载（忽略依赖）
```

#### `openclaw plugins update`

更新插件。

```bash
openclaw plugins update              # 更新所有插件
openclaw plugins update <plugin-id>  # 更新指定插件
```

#### `openclaw plugins list`

列出已安装插件。

```bash
openclaw plugins list
openclaw plugins list --json       # JSON 格式输出
```

#### `openclaw plugins search`

搜索可用插件。

```bash
openclaw plugins search              # 列出所有
openclaw plugins search <keyword>    # 关键词搜索
```

#### `openclaw plugins info`

查看插件详细信息。

```bash
openclaw plugins info <plugin-id>
```

#### `openclaw plugins enable/disable`

启用/禁用插件。

```bash
openclaw plugins enable <plugin-id>
openclaw plugins disable <plugin-id>
```

### 4.2 Skill 相关命令

#### `openclaw skills install`

安装 Skill。

```bash
# 从 ClawHub 安装
openclaw skills install <skill-name>

# 安装特定版本
openclaw skills install <name>@<version>

# 从 GitHub 安装
openclaw skills install github:<owner>/<repo>

# 从本地路径安装
openclaw skills install /path/to/skill
```

#### `openclaw skills uninstall`

卸载 Skill。

```bash
openclaw skills uninstall <skill-name>
```

#### `openclaw skills update`

更新 Skill。

```bash
openclaw skills update           # 更新所有 Skill
openclaw skills update <name>    # 更新指定 Skill
```

#### `openclaw skills list`

列出 Skill。

```bash
openclaw skills list              # 所有 Skill
openclaw skills list --installed  # 仅已安装
openclaw skills list --bundled    # 仅内置
openclaw skills list --local      # 仅本地
openclaw skills list --json       # JSON 格式
```

#### `openclaw skills search`

搜索 Skill。

```bash
openclaw skills search           # 列出所有
openclaw skills search <keyword> # 关键词搜索
```

#### `openclaw skills info`

查看 Skill 详情。

```bash
openclaw skills info <skill-name>
```

#### `openclaw skills enable/disable`

启用/禁用 Skill。

```bash
openclaw skills enable <skill-name>
openclaw skills disable <skill-name>
```

#### `openclaw skills create`

创建新 Skill（交互式）。

```bash
openclaw skills create <skill-name>
# 按照提示输入名称、描述等信息
```

### 4.3 命令速查表

| 操作 | 插件命令 | Skill 命令 |
|------|---------|-----------|
| 安装 | `openclaw plugins install <id>` | `openclaw skills install <name>` |
| 卸载 | `openclaw plugins uninstall <id>` | `openclaw skills uninstall <name>` |
| 更新 | `openclaw plugins update [id]` | `openclaw skills update [name]` |
| 列出 | `openclaw plugins list` | `openclaw skills list` |
| 搜索 | `openclaw plugins search [keyword]` | `openclaw skills search [keyword]` |
| 详情 | `openclaw plugins info <id>` | `openclaw skills info <name>` |
| 启用 | `openclaw plugins enable <id>` | `openclaw skills enable <name>` |
| 禁用 | `openclaw plugins disable <id>` | `openclaw skills disable <name>` |
| 创建 | - | `openclaw skills create <name>` |

---

## 五、其他重要内容

### 5.1 插件 Bundle 与 IDE 兼容

OpenClaw 提供特殊的 **Bundle 插件**，用于与第三方 AI IDE 和工具保持兼容。

#### 5.1.1 Bundle 类型

| Bundle | 说明 | 安装命令 |
|--------|------|----------|
| **Codex Bundle** | 兼容 OpenAI Codex CLI 的代理协议 | `openclaw plugins install codex` |
| **Claude Bundle** | 兼容 Claude Code 的代理协议 | `openclaw plugins install claude` |
| **Cursor Bundle** | 兼容 Cursor Agent 的代理协议 | `openclaw plugins install cursor` |

#### 5.1.2 Bundle 的作用

Bundle 插件本质上是一个**兼容层**，它将 OpenClaw 的 Agent 运行时适配为第三方工具期望的协议格式：

- 允许 OpenClaw Agent 替代官方工具作为后端
- 复用 OpenClaw 的模型路由、通道、日志等基础设施
- 支持 Multi-Agent 场景下的不同 Bundle 实例

#### 5.1.3 配置示例

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          model: "openai/gpt-4.1",
          // 其他 Codex 特定配置
        }
      }
    }
  }
}
```

### 5.2 Skill 创建指南

#### 5.2.1 SKILL.md 基本结构

```markdown
---
name: "skill-name"
description: "Skill 的简短描述"
author: "Your Name"
version: "1.0.0"
commands:
  - name: "/command-name"
    description: "命令描述"
---

# Skill 名称

## 使用说明

当用户要求...时，按以下步骤操作：

1. 第一步：使用 `tool_name` 执行操作
2. 第二步：处理结果
3. 第三步：向用户反馈

## 注意事项

- 注意点 1
- 注意点 2
```

#### 5.2.2 元数据字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | Skill 的唯一标识符 |
| `description` | 是 | 简短描述 |
| `author` | 否 | 作者信息 |
| `version` | 否 | 版本号 |
| `commands` | 否 | 斜杠命令列表 |
| `metadata.openclaw.skillKey` | 否 | 自定义配置键名 |

#### 5.2.3 Skill 存放位置

根据使用范围选择合适的目录：

| 范围 | 路径 | 优先级 |
|------|------|--------|
| 工作区共享 | `<workspace>/skills/<skill-name>/SKILL.md` | 最高 |
| 工作区 Agent | `<workspace>/.agents/skills/<skill-name>/SKILL.md` | 高 |
| 用户个人 | `~/.agents/skills/<skill-name>/SKILL.md` | 中 |
| OpenClaw 管理 | `~/.openclaw/skills/<skill-name>/SKILL.md` | 中 |

#### 5.2.4 使用 CLI 创建 Skill

```bash
# 交互式创建 Skill
openclaw skills create my-skill

# 按提示输入：
# - Skill 名称
# - 描述
# - 作者
# - 是否添加示例命令
```

### 5.3 安全注意事项

#### 5.3.1 插件安全

- **来源可信**：仅从 ClawHub、官方 npm 组织或可信 Git 仓库安装插件
- **权限审查**：安装前查看插件请求的权限和能力类型
- **隔离测试**：新插件先在隔离环境测试，确认安全后再用于生产
- **及时更新**：关注插件安全更新，及时执行 `openclaw plugins update`

#### 5.3.2 Skill 安全

- **路径安全**：`allowSymlinkTargets` 不要配置过于宽泛的路径（如 `~` 或 `~/Projects`）
- **环境变量**：沙箱环境中的 Skill 不会继承主机的 `process.env`，需要单独配置
- **敏感信息**：使用 SecretRef 而非明文存储 API 密钥

#### 5.3.3 沙箱环境变量

当会话处于**沙箱模式**时，Skill 进程在隔离环境中运行，**不会继承主机的环境变量**：

```json5
// ❌ 错误：沙箱中无效
{
  skills: {
    entries: {
      "image-lab": {
        env: { GEMINI_API_KEY: "***" }  // 沙箱中不生效！
      }
    }
  }
}

// ✅ 正确：通过 Docker 沙箱配置传递
{
  agents: {
    defaults: {
      sandbox: {
        docker: {
          env: { GEMINI_API_KEY: "***" }  // 正确方式
        }
      }
    }
  }
}
```

> ⚠️ **注意**：Docker 沙箱的 `env` 值可以通过 Docker 元数据被具有 Docker 访问权限的用户查看。如需更高安全性，请使用挂载密钥文件或自定义镜像。

### 5.4 常见问题排查

#### 5.4.1 插件安装失败

| 问题 | 可能原因 | 解决方案 |
|------|---------|----------|
| `E404` 包不存在 | 包名错误或 npm 源不同步 | 确认包名，尝试 `npm view <pkg>` 验证 |
| 权限不足 | 全局目录无写入权限 | 检查 npm 全局目录权限，或使用本地安装 |
| 依赖冲突 | 与其他插件版本不兼容 | 使用 `--force` 强制安装，或更新其他插件 |
| 网络超时 | npm 源访问慢 | 切换 npm 镜像源，或重试 |

#### 5.4.2 Skill 未生效

| 问题 | 可能原因 | 解决方案 |
|------|---------|----------|
| Skill 未列出 | 目录不在扫描路径中 | 确认文件放在正确的 skills 目录下 |
| Skill 被跳过 | 符号链接目标未授权 | 配置 `allowSymlinkTargets` |
| 修改后未更新 | 文件监听未触发 | 检查 `skills.load.watch` 是否为 true |
| 配置不生效 | 配置键名不匹配 | 确认使用 `metadata.openclaw.skillKey` 或 Skill 名称 |

#### 5.4.3 多 Agent 配置不生效

| 问题 | 可能原因 | 解决方案 |
|------|---------|----------|
| Agent 未加载插件 | `plugins` 列表为空或错误 | 检查 `agents.list[].plugins` 配置 |
| 继承了不该继承的 | 省略 vs 空列表 | `skills: []` 表示无 Skill，省略表示继承默认 |
| 配置冲突 | 全局与 Agent 级配置冲突 | 检查 `plugins.entries` 中的 `enabled` 状态 |

#### 5.4.4 查看日志诊断

```bash
# 查看 OpenClaw 日志
openclaw logs

# 查看特定插件日志
openclaw logs --plugin <plugin-id>

# 查看 Skill 加载日志
openclaw logs --skill <skill-name>

# 开启调试模式
openclaw --debug
```

### 5.5 进阶主题

#### 5.5.1 插件开发简介

开发自定义插件需要：

1. 创建 Node.js 项目，添加 `openclaw.plugin.json` 清单文件
2. 实现对应的能力接口（Provider、Channel、Tool 等）
3. 发布到 npm 或本地安装测试

**openclaw.plugin.json 示例**：

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "插件描述",
  "main": "dist/index.js",
  "capabilities": ["tool"],
  "dependencies": {}
}
```

#### 5.5.2 Skill Workshop（实验性功能）

OpenClaw 提供实验性的 **Skill Workshop** 功能，可以自动捕获 Agent 的执行过程并生成 SKILL.md：

```bash
# 启动 Workshop 模式
openclaw skills workshop --start

# 执行一系列操作后，生成 Skill 模板
openclaw skills workshop --capture <session-id>

# 保存为新的 Skill
openclaw skills workshop --save <skill-name>
```

#### 5.5.3 推荐配置模板

**开发环境配置**：

```json5
{
  skills: {
    load: {
      watch: true,
      extraDirs: ["~/dev/skills"],
    },
    install: {
      nodeManager: "pnpm",
    }
  },
  plugins: {
    entries: {
      "@openclaw/web-search": { enabled: true }
    }
  }
}
```

**生产环境配置**：

```json5
{
  skills: {
    allowBundled: ["github", "weather"],  // 严格限制内置 Skill
    load: {
      watch: false,  // 禁用文件监听，提高性能
    },
    install: {
      allowUploadedArchives: false,  // 禁止上传安装
    }
  },
  agents: {
    defaults: {
      skills: [],  // 默认无 Skill
      plugins: [], // 默认无插件
    }
  }
}
```

---

## 附录：配置参考速查

### A.1 完整配置结构

```json5
{
  // === 插件配置 ===
  plugins: {
    entries: {
      "plugin-id": {
        enabled: true,
        config: {
          apiKey: { source: "env", id: "KEY" },
          // ...
        }
      }
    }
  },
  
  // === Skill 配置 ===
  skills: {
    allowBundled: ["skill1", "skill2"],
    load: {
      extraDirs: ["~/custom/skills"],
      allowSymlinkTargets: [],
      watch: true,
      watchDebounceMs: 250,
    },
    install: {
      preferBrew: true,
      nodeManager: "npm",
      allowUploadedArchives: false,
    },
    entries: {
      "skill-name": {
        enabled: true,
        apiKey: { source: "env", id: "KEY" },
        env: { VAR: "value" },
      }
    }
  },
  
  // === Agent 配置 ===
  agents: {
    defaults: {
      plugins: ["plugin1"],
      pluginConfig: { /* ... */ },
      skills: ["skill1"],
    },
    list: [
      {
        id: "agent-1",
        name: "Agent 1",
        // 继承 defaults
      },
      {
        id: "agent-2",
        plugins: ["plugin2"],  // 完全替换默认
        skills: ["skill2"],     // 完全替换默认
      }
    ]
  }
}
```

### A.2 环境变量参考

| 变量 | 说明 |
|------|------|
| `OPENCLAW_STATE_DIR` | OpenClaw 状态目录路径 |
| `OPENCLAW_CONFIG_FILE` | 配置文件路径 |
| `OPENCLAW_PLUGINS_DIR` | 插件安装目录 |
| `OPENCLAW_SKILLS_DIR` | Skill 扫描目录 |
| `OPENCLAW_ALLOW_PLUGIN_INSTALL_OVERRIDES` | 允许插件安装覆盖（测试用） |
| `OPENCLAW_PLUGIN_INSTALL_OVERRIDES` | 插件安装覆盖映射（JSON 格式） |

---

> **文档结束**
> 
> 如有疑问，可通过以下方式获取帮助：
> - `openclaw --help`
> - `openclaw plugins --help`
> - `openclaw skills --help`
> - OpenClaw 官方文档：https://docs.openclaw.ai