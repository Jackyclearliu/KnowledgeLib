# 目录

- [前置条件](#前置条件)
- [基本使用](#基本使用)
  - [1、基于工作流为chat添加定制化要求](#1基于工作流为chat添加定制化要求)
    - [概述](#概述)
    - [自定义说明（.instructions.md）](#自定义说明instructionsmd)
      - [一、创建copilot-instructions.md](#一创建copilot-instructionsmd)
      - [二、创建自定义.instructions.md](#二创建自定义instructionsmd)
      - [三、.instructions.md格式](#三instructionsmd格式)
      - [四、关联设置和命令](#四关联设置和命令)
    - [通用提示词文件（.prompt.md）](#通用提示词文件promptmd)
      - [一、创建.prompt.md](#一创建promptmd)
      - [二、.prompt.md格式](#二promptmd格式)
      - [三、变量详解](#三变量详解)
      - [四、使用指南（超详细版）](#四使用指南超详细版)
      - [五、关键设置和命令](#五关键设置和命令)
  - [2、引入并使用MCP](#2引入并使用mcp)
    - [概述](#概述)
    - [如何查看已安装的MCP](#如何查看已安装的mcp)
    - [如何安装MCP](#如何安装mcp)
      - [一、自动安装](#一自动安装)
      - [二、手动安装](#二手动安装)
      - [三、查看MCP Server配置](#三查看mcp-server配置)
    - [如何配置MCP Server](#如何配置mcp-server)
      - [一、区分服务器类型](#一区分服务器类型)
      - [二、配置结构](#二配置结构)
      - [三、开始使用](#三开始使用)
        - [1、查看已经配置的MCP服务](#1查看已经配置的mcp服务)
        - [2、如何管理并启动MCP服务](#2如何管理并启动mcp服务)
        - [3、如何在与Copilot的对话中使用已经成功配置并启用的MCP Server](#3如何在与copilot的对话中使用已经成功配置并启用的mcp-server)
        - [4、如何修改MCP Server配置](#4如何修改mcp-server配置)
    - [关键设置与命令](#关键设置与命令)

---

## 前置条件
1. 安装新版VS Code，建议版本最早不要低于1.104.0，实测使用较旧版本的VS Code，Copilot功能受限严重，基本无法正常使用
2. 注册github账号并开通copilot pro订阅计划，10$ per month，大概70块人民币左右，可以使用claude sonnect4模型，新注册的用户可以免费体验一个月
3. 打开VS Code并使用github账号登录，扩展商店搜索并安装**GitHub Copilot**、**GitHub Copilot Chat**扩展
4. 完成以上步骤就可以在VS Code中使用Copilot了

## 基本使用
### 1、基于工作流为chat添加定制化要求
#### 概述
VS Copilot支持设置持久化配置，使其能自动将你偏好的上下文、工具和指南应用到每一次对话中，从而使AI生成的结果更加匹配用户自己的代码实践和项目需要。

#### 自定义说明（.instructions.md）
自定义指令允许你在 Markdown 文件中为生成代码、执行代码审查或生成提交消息等任务定义通用指南或规则，VS Copilot会在每一次对话时，自动应用这些说明文件中的内容。

使用自定义指令的部分场景：

+ 明确编码规范、首选技术或项目要求，以便生成的代码符合你的标准
+ 提供关于提交信息或拉取请求标题及描述应如何构建的指导原则
+ 制定代码审查规则，例如检查安全漏洞、性能问题或对编码标准的遵守情况

VS Copilot支持多种基于 Markdown 的指令文件

+ 一个单独的.github/copilot-instructions.md，该文件自动适用于工作区中的所有聊天请求，并保存在当前工作空间也就是项目根目录的.vscode文件下
+ 可以多个存在的.instructions.md文件
    - 用于特定任务
    - 支持使用 **applyTo** 前置元数据来定义指令应用于哪些文件
    - 可以存储在工作空间或用户配置文件中

##### 一、创建copilot-instructions.md
1、打开VS Code的设置面板（按Ctrl+，组合键），搜索github.copilot.chat.codeGeneration.useInstructionFiles并设置为true

2、直接在根目录下创建.github/copilot-instructions.md即可

##### 二、创建自定义.instructions.md
有两种方式

1、点击聊天窗口右上角的设置按钮，并在弹出的菜单中选择Instructions，然后在接下来的弹窗中点击创建即可

![](https://cdn.nlark.com/yuque/0/2025/png/52580108/1762742999648-3f643194-b488-4052-8d48-7dcf6f969c2b.png)

![](https://cdn.nlark.com/yuque/0/2025/png/52580108/1762743023042-29480c7b-1eff-41af-9392-31d157a3ae0c.png)

2、打开VS Code命令面板（按Ctrl+Shift+P 组合键），输入**Chat: New Instructions File**命令即可

注意以上两种方式最后一步的选择文件保存位置，推荐保存到.github文件下

![](https://cdn.nlark.com/yuque/0/2025/png/52580108/1762743970311-579972ca-c767-476a-9714-0febcb125bb5.png)

##### 三、.instructions.md格式
+ 头部：指定 YAML 前置元数据，包含两个可选项
    - **description**自定义说明的简要描述
    - **applyTo**配置指令应何时自动应用的通配符（使用 **表示应用在全部文件）举例说明：applyTo: "**/*.ts,**/*.tsx"代表仅将该自定义说明应用在typescript文件中
+ 正文：Markdown 格式的说明作为

**自定义说明示例（python编码规范）**

```markdown
---
applyTo: "**/*.py"
---
# Project coding standards for Python
- Follow the PEP 8 style guide for Python.
- Always prioritize readability and clarity.
- Write clear and concise comments for each function.
- Ensure functions have descriptive names and include type hints.
- Maintain proper indentation (use 4 spaces for each level of indentation).
```

##### 四、关联设置和命令
+ github.copilot.chat.codeGeneration.useInstructionFiles 配置是否允许在每一次的copilot对话中添加.github/copilot-instructions.md中的说明
+ chat.instructionsFilesLocations 指定自定义说明可以在对话中生效的位置，默认为.github/instructions
+ **Chat: New Instructions File**创建自定义说明
+ **Chat: Configure Instructions**修改自定义说明

#### 通用提示词文件（.prompt.md）
提示文件允许你在 Markdown 文件中为常见且可重复的开发任务定义可复用的提示。提示文件是独立的提示，可以直接在聊天中运行它们（**比如一个名为fix-bug.prompt.md的提示词文件，可以直接在聊天框通过斜杠命令/fix-bug使用它**）。你可以包含特定任务的上下文以及关于该任务应如何执行的指导方针。将提示文件与自定义说明相结合，以确保复杂任务的一致执行。

使用提示词文件的部分场景

+ 为常见的编码任务创建可重用的提示词，例如搭建新组件、API 路由或生成测试
+ 定义用于执行代码审查的提示词，比如检查代码质量、安全漏洞或性能问题
+ 为复杂流程或项目特定模式创建分步指南
+ 定义用于生成实施计划、架构设计或迁移策略的提示词

##### 一、创建.prompt.md
1、勾选chat.promptFiles设置

2、打开VS Code命令面板，输入**Chat: New Prompt File**命令，或者点击聊天窗口右上角的设置按钮，并在弹出的菜单中选择Prompt Files

3、选择文件添加的位置，建议添加到.github\prompts目录下

![](https://cdn.nlark.com/yuque/0/2025/png/52580108/1762757869039-4b9e77e3-f2db-4686-b39a-93c3352a119c.png)

##### 二、.prompt.md格式
+ 头部：指定 YAML 前置元数据，包含4个可选项
    - description 对于prompt的简短描述
    - name 提示的名称，在聊天中键入 / 后使用。如果未指定，则使用文件名。
    - agent 运行该prompt将使用的聊天模式：ask、edit、agent（默认）
    - model 运行提示词时使用的语言模型。如果未指定，则使用模型选择器中当前选中的模型
    - tools 可使用的工具（集）名称数组。点击“Configure Tools”可以从工作区的可用工具列表中选择工具。如果在运行提示时某个特定工具（集）不可用，则会忽略该工具（集）

![](https://cdn.nlark.com/yuque/0/2025/png/52580108/1762764552356-107a64eb-b4ce-4c8e-b607-633cac1980cf.png)

工具调用优先级：

1、tools数组中指定的工具列表

2、所选聊天模式的默认工具

+ 正文：Markdown 格式的prompt说明

支持在正文中通过使用 Markdown 链接来引用其他工作区文件、prompt文件或instruction文件。引用这些文件时使用相对路径，并确保路径根据提示文件的位置是正确的。

在提示文件中，可以使用 ${variableName} 语法来引用变量。支持引用以下变量  
1、**工作区变量：**`${workspaceFolder}`, `${workspaceFolderBasename}`

2、**选择变量：**`${selection}`, `${selectedText}`

3、**文件上下文变量：**`${file}`, `${fileBasename}`, `${fileDirname}`, `${fileBasenameNoExtension}`

4、**输入变量：**`${input:variableName}`, `${input:variableName:placeholder}`**通用提示词文件示例**

```markdown
---
agent: agent
description: "Based on the code and error description provided by the user, fix the bug in the code."
model: GPT-5
tools: ['search', 'edit', 'fetch', 'todos', 'fetch', 'upstash/context7/get-library-docs', 'upstash/context7/resolve-library-id']
---

# Fix Bug

## Role

You are a professional software developer. Your task is to based on the code and error description provided by the user, carefully analyze the code, list possible causes of errors, and provide detailed repair suggestions and code modification plans. Finally, output the repaired complete code and verify its correctness, Ensure that the code is well-structured, efficient, and follows best practices. Provide a brief explanation of the changes made to fix the bug.

- Understand the files where the user encountered bugs and the functions that the code is intended to implement.
- Locate the position of the bug
- Analyze the causes of the bug and the consequences it will bring.
- Provide solutions to the bug. If third-party SDKs, plugins, component libraries, etc., are used, use context7 to obtain their complete and latest documents and sample codes to ensure accurate understanding and application of relevant APIs.
- Output the repaired complete code and verify its correctness, Ensure that the code is well-structured, efficient, and follows best practices
- Provide a brief explanation of the changes made to fix the bug.
```

##### 三、变量详解
**工作区变量 (Workspace Variables)**
|**变量名**|**含义**|**示例值** |
| :--- | :--- | :--- |
| `${workspaceFolder}` | 当前工作区根目录的**完整绝对路径** | `/home/user/projects/my-app` |
| `${workspaceFolderBasename}` | 工作区根目录的**文件夹名称** | `my-app` |


```markdown
# 示例：创建README的Prompt File
Based on the project structure in ${workspaceFolder}, generate a README.md file 
that explains the purpose of the ${workspaceFolderBasename} project.
```

**选择变量 (Selection Variables)**
|**变量名**|**含义**|**示例值** |
| :--- | :--- | :--- |
| `${selection}` | **文件路径+代码范围** | `src/main.js:10-25` |
| `${selectedText}` | 选中的**纯文本内容** | `function add(a, b) { return a + b; }` |


```markdown
# 示例：重构代码的Prompt File
Please refactor the selected function: ${selectedText}

Focus on improving readability and adding type safety.
```

**文件上下文变量 (File Context Variables)**
|**变量名**|**含义**|**示例：**`**/home/user/projects/my-app/src/utils/helper.js**` |
| :--- | :--- | :--- |
| `${file}` | 当前文件的**完整路径** | `/home/user/projects/my-app/src/utils/helper.js` |
| `${fileBasename}` | 文件名（**含扩展名**） | `helper.js` |
| `${fileDirname}` | 文件所在**目录路径** | `/home/user/projects/my-app/src/utils` |
| `${fileBasenameNoExtension}` | 文件名（**不含扩展名**） | `helper` |


```markdown
# 示例：生成测试文件的Prompt File
Create a Jest test file for ${fileBasename} located at ${fileDirname}/__tests__/
Test the main exported function from ${fileBasenameNoExtension}.
```

**输入变量 (Input Variables)**
|**变量名**|**含义**|**用法** |
| :--- | :--- | :--- |
| `${input:variableName}` | 从聊天框接收输入值，**必填** | `${input:componentName}` |
| `${input:variableName:placeholder}` | 带占位符的**可选输入**| `${input:framework:React}` |**交互流程**：当Prompt被执行时，VS Code会弹出输入框要求用户填写值。

```markdown
# 示例：生成React组件的Prompt File
Create a ${input:componentType} component named ${input:componentName} 
using ${input:framework:React} framework.

Requirements:
- Place in ${fileDirname}/components/
- Use TypeScript
- Include basic styling
```

**copilot执行时**：会依次弹窗询问：

1. `componentType` (无默认值，必须输入)
2. `componentName` (无默认值，必须输入)
3. `framework` (输入框预填`React`，可修改)

##### 四、使用指南（超详细版）
1、创建.vscode/prompts/refactor.md（仅举例说明，具体创建过程前面已给出）

2、在聊天框中使用（核心步骤）

**使用**`**/**`**命令**：

    1. 打开目标文件
    2. 选中要处理的代码片段
    3. 在 Copilot Chat 输入框中输入 `/`
    4. 选择 `/refactor`（会自动列出所有prompt文件，这里使用refactor仅举例用）
    5. 按回车执行

**手动指定上下文**：

如果未选中代码，可以这样操作：（**这会将**`**helper.js**`**作为**`**${file}**`**注入，即使它不是当前打开的文件。**）

:::info
/refactor #file:src/utils/helper.js

:::

3、针对特定文件进行精确控制(以下场景仅举例用)

**场景：为指定文件生成单元测试创建**`**test-generator.prompt.md**`

```markdown
为 ${fileBasename} 生成 Jest 测试文件

测试要求：
- 覆盖所有导出函数
- 使用 @testing-library/react
- 模拟外部依赖
- 输出路径：${fileDirname}/__tests__/${fileBasenameNoExtension}.test.js
```

**使用方式（3种）：**1.**当前文件**（最简单）：`/test-generator`_当前编辑器中的文件自动成为 _`_${file}_`
    2. **引用特定文件**（推荐）：`/test-generator #file:src/components/Button.jsx`_使用 _`_#file:_`_ 语法显式指定_
    3. **拖动文件到聊天框**：
        * 从资源管理器拖动文件到聊天输入框
        * 输入 `/test-generator`
        * 文件自动关联为上下文

4、高级技巧：多文件引用

Prompt File 支持引用多个文件：

```markdown
分析 ${file:1} 和 ${file:2} 中的重复代码
提取公共函数到 ${fileDirname:1}/shared/utils.js

文件1: ${fileBasename:1}
文件2: ${fileBasename:2}
```

使用方式：

/duplication-check #file:src/featureA.js #file:src/featureB.js

5、交互式输入示例

```markdown
生成一个 ${input:componentType} 组件：${input:name}
技术栈：${input:tech:React}
文件位置：${fileDirname}/components/${input:name}.jsx
要求：
- TypeScript
- 包含样式
- 添加 PropTypes
```

**copilot执行过程：**

1. 输入 `/create-component`
2. 弹出输入框： _"componentType"_ （必填）
3. 弹出输入框： _"name"_ （必填）
4. 弹出输入框： _"tech"_ （预填 React，可修改）
5. 生成代码

:::info
总结一下写好prompt的关键：

1. 清晰描述提示词应实现的目标以及预期的输出格式。
2. 提供预期输入和输出的示例，
3. 使用 Markdown 链接引用自定义指令，而非在每个提示词中重复准则。
4. 利用像 ${selection} 这样的内置变量和输入变量，使提示词更具灵活性。
5. 使用编辑器的播放按钮测试你的提示词，并根据结果进行优化

:::

##### 五、关键设置和命令
+ chat.promptFiles 配置是否在聊天中启用prompt文件
+ chat.promptFilesLocations 设置prompt.md文件保存的位置
+ chat.promptFilesRecommendations 在开始新的聊天会话时，将prompt显示为推荐操作
+ **Chat: New Prompt File**创建一个新的prompt文件
+ **Chat: Configure Prompt Files**编辑已有的prompt文件

### 2、引入并使用MCP
#### 概述
MCP（模型上下文协议）是一种用于将人工智能应用程序连接到外部系统的开源标准。借助 MCP，像 Claude 或 ChatGPT 这样的人工智能应用程序能够连接到数据源（例如本地文件、数据库）、工具（例如搜索引擎、计算器）以及工作流程（例如特定的提示词），从而使它们能够获取关键信息并执行任务。可以把 MCP 想象成人工智能应用程序的 USB-C 接口。就像 USB-C 为连接电子设备提供了一种标准化方式一样，MCP 为连接人工智能应用程序与外部系统提供了一种标准化方式。

![](https://cdn.nlark.com/yuque/0/2025/png/52580108/1760076485381-0f28351e-a70e-4464-a600-d88f5c04f45b.png)

#### 如何查看已安装的MCP
1. 打开VS Code的设置面板（按Ctrl+，组合键），搜索chat.mcp.gallery.enabled，设置为true
2. 打开扩展视图（按 Ctrl+Shift+X 组合键），并在搜索框中输入 @mcp，以显示 MCP 服务器列表。或者打开VS Code命令面板（按Ctrl+Shift+P 组合键），输入**MCP: Browse Servers**命令

#### 如何安装MCP
有两种方式，用户可以自行选择是自动安装还是手动安装

##### 一、自动安装
通过在扩展视图中搜索框输入@mcp命令，获取VS Code官方推荐的MCP Server列表，从中选择自己所需要的MCP Server，点击右下角的install按钮进行安装。

优点：安装非常方便，VS Code会自动生成user profile的MCP Server配置文件（保存在C:\Users\Administrator\AppData\Roaming\Code\User，仅对当前用户生效，多项目共享，对于项目的合作者无法生效），基本不需要用户自行配置

缺点：不够灵活，缺乏对于用户本地部署或者小众第三方MCP Server的支持，只能安装官方推荐列表中的MCP Server

##### 二、手动安装
1. 打开VS Code命令面板输入**MCP: Add Server**，执行该命令后会出现选择要添加的MCP Server类型的弹窗

![](https://cdn.nlark.com/yuque/0/2025/png/52580108/1760079234885-7586bb08-3084-42ef-8494-de766c67c165.png)

2. 根据你要添加的MCP Server选择相应的类型，然后点击进行下一步
3. 按照弹窗中的提示填写好相应的内容后一直执行到最后一步，选择你所要添加的MCP Server配置文件的位置，这里可以看到有两个可选，一个是全局（选择该项会将mcp.json放到C:\Users\Administrator\AppData\Roaming\Code\User路径下，**该配置仅对你自己生效**），另一个是工作空间（选择该项会在你当前项目的根目录下创建.vscode/mcp.json文件，配置就写到这里），放到工作空间有个好处就是你可以提交到git仓库将配置**共享给项目的协作者**

![](https://cdn.nlark.com/yuque/0/2025/png/52580108/1760079439884-e39c3f00-0321-4745-a7b2-887a162e4d5a.png)

##### 三、查看MCP Server配置
经过上面的步骤安装好MCP Server后，我们可以通过**MCP: Open User Configuration**命令和**MCP: Open Workspace Folder MCP Configuration**命令分别查看和编辑保存到C:\Users\Administrator\AppData\Roaming\Code\User路径的mcp.json或者保存到当前项目根目录下的.vscode/mcp.json文件中的配置

#### 如何配置MCP Server
大家在上面的手动安装MCP时应该会产生很多困惑，比如选择不同类型的MCP Server后进行下一步时VS Code提示要求输入的东西是什么

##### 一、区分服务器类型
MCP Server可以使用不同的传输方法进行连接。请根据服务器的通信方式选择合适的配置。

1. 标准输入 / 输出（stdio）服务器

这是用户在本地部署运行的服务器最常见的类型，对应用户执行**MCP: Add Server**命令后可选的第一个类型

2. HTTP 和服务器发送事件（SSE）服务器

通过 HTTP 进行通信的服务器，一般为远程http服务器，对应用户执行**MCP: Add Server**命令后可选的第二个类型

##### 二、配置结构
MCP 服务器通过一个 JSON 文件（mcp.json）进行配置，该文件定义了两个主要部分：服务器定义以及用于敏感数据的可选输入变量。

配置文件有两个主要部分：

+ **servers: {}** - 在该字段下配置MCP Server列表以及他们对应的配置
+ **inputs: []**- 可选的敏感信息相关配置**对于标准输入 / 输出（stdio）服务器，有以下配置可用**
|**字段名**|**是否必填**|**描述**|**可选参数**（**部分字段并不仅限于下面内容，具体参考你所要使用的MCP Server**） |
| --- | --- | --- | --- |
| `type` | 是 | 服务器链接类型 | `"stdio"` |
| `command` | 是 | 启动服务器可执行文件的命令。该命令必须在您的系统路径中可用，或者包含其完整路径。 | `"npx"`<br/>, `"node"`<br/>, `"python"`<br/>, `"docker"` |
| `args` | 否 | 传递给命令的参数数组，数组中的位置对应参数的拼接顺序 | `["server.py", "--port", "3000"]` |
| `env` | 否 | 服务器环境变量 | `{"API_KEY": "${input:api-key}"}` |
| `envFile` | 否 | 加载更多变量的环境文件的路径 | "${workspaceFolder}/.env" |


以下是一个标准输入 / 输出（stdio）MCP服务器配置示例，该示例采用github上一个用于Swagger文档生成和ApiFox平台集成的MCP服务（链接地址[code-to-apifox-mcp](https://github.com/xzg0919/code-to-apifox-mcp)）

![](https://cdn.nlark.com/yuque/0/2025/png/52580108/1763457325661-b8a2c982-b1fa-44a8-acc8-d3f755714506.png)

**标准输入 / 输出（stdio）MCP服务器配置示例**

```json
{
  "servers": {
    "doc-mcp-server": {
      "type": "stdio",
      "command": "code-to-apifox-mcp",
      "args": ["--stdio"]
    }
  }
}
```

**对于HTTP 和服务器发送事件（SSE）服务器，有以下配置可用**
|**字段名**|**是否必填**|**描述**|**可选参数** |
| --- | --- | --- | --- |
| `type` | 是 | 服务器连接类型 | `"http"`<br/>, `"sse"` |
| `url` | 是 | 服务器URL | `"http://localhost:3000"`<br/>, `"https://api.example.com/mcp"` |
| `headers` | 否 | 服务器用于身份验证或配置的 HTTP 头，该字段需要参考引入的MCP Server提供的文档 | `{"Authorization": "Bearer ${input:api-token}"}` |


**HTTP 和服务器发送事件（SSE）服务器示例**

```json
{
	"servers": {
		"upstash/context7": {
			"type": "http",
			"url": "https://mcp.context7.com/mcp",
			"headers": {
				"CONTEXT7_API_KEY": "${input:context7_api_key}"
			},
			"gallery": "https://api.mcp.github.com",
			"version": "1.0.0"
		}
	},
	"inputs": [
		{
			"id": "context7_api_key",
			"type": "promptString",
			"description": "Context7 API key (optional; increases rate limits). Get one at https://context7.com/dashboard",
			"password": true
		}
	]
}
```

**对于敏感数据使用输入变量**

输入变量可以定义配置值的占位符，从而无需直接在服务器配置中对 API 密钥或密码等敏感信息进行硬编码。当在mcp.json中使用了${input:variable-id} 引用输入变量时，VS Code 会在服务器首次启动时提示用户输入该值。

| **字段名**|**是否必填**|**描述**|**可选参数** |
| --- | --- | --- | --- |
| `type` | 是 | 输入提示类型 | `"promptString"` |
| `id` | 是 | 独一无二的变量id | `"api-key"`<br/>, `"database-url"` |
| `description` | 是 | 该输入变量的简要描述，方便用户知道该变量是用来配置什么的 | `"GitHub Personal Access Token"` |
| `password` | 否 | 是否对外隐藏输入值，默认关闭（一般用来对API Key和密码等敏感数据进行加密） | `true | false`<br/> |


##### 三、开始使用
###### 1、查看已经配置的MCP服务
方法一： 通过左侧扩展列表查看

![](https://cdn.nlark.com/yuque/0/2025/png/52580108/1763517246626-6d79dd63-25ba-4e7a-8234-72cd0155cf90.png)

方法二：使用**MCP: List Servers**命令

###### 2、如何管理并启动MCP服务
方法一：鼠标移动到扩展列表中对应的MCP Server上右击

![](https://cdn.nlark.com/yuque/0/2025/png/52580108/1763517429784-7ac03569-eb5e-42bf-a78f-b908564a9d13.png)

方法二：使用**MCP: List Servers**命令后，在弹出的服务列表中点击对应MCP Server

![](https://cdn.nlark.com/yuque/0/2025/png/52580108/1763517513427-716cd70f-82fa-4bbe-ad46-a7fd526d3fe0.png)

方法三：在mcp.json中使用对应的MCP Server的控制按钮进行管理

![](https://cdn.nlark.com/yuque/0/2025/png/52580108/1763517607863-2a4d59a8-2bf6-4139-9432-9da6ab0e1e82.png)

###### 3、如何在与Copilot的对话中使用已经成功配置并启用的MCP Server
成功添加 MCP 服务器后，copilot会自动将MCP提供的方法添加到工具集。MCP 工具的工作方式与 VS Code 中的其他工具类似：在使用代理时，它们可以被自动调用，也可以在用户的提示词中被明确引用。

这里使用我之前安装的upstash/context7进行举例

1、启动MCP Server

![](https://cdn.nlark.com/yuque/0/2025/png/52580108/1763519525403-10920eb7-2185-47da-8177-08d98e9de031.png)

2、打开一个新的聊天窗口并点击左下角的工具按钮，在弹出的工具菜单中可以看到该MCP Server提供的两个工具已经被添加到工具集，**勾选对应的工具**

![](https://cdn.nlark.com/yuque/0/2025/png/52580108/1763519634112-24c61883-dc78-4993-a411-d961ea9d39ec.png)

然后在聊天的提示词中，可以使用语义化描述让模型自动调用工具：“帮我完成XX任务，基于XXsdk，使用context7”。也可以直接在提示词中使用#工具名的方式手动告诉模型使用工具

至于每个MCP Server有哪些功能，提供了哪些工具以及对应的工具有什么作用，使用时参考相关文档即可

###### 4、如何修改MCP Server配置
VS Code提供了两个命令

+ **MCP: Open User Configuration**开启并修改当前用户保存的MCP Server配置
+ **MCP: Open Workspace Folder Configuration**开启并修改当前工作区保存的MCP Server配置

#### 关键设置与命令
+ chat.mcp.discovery.enabled 配置是否允许VS Code 能够自动检测并复用来自其他应用程序（如 Claude Desktop）的 MCP 服务器配置。
+ chat.mcp.gallery.enabled 配置是否启动扩展菜单中MCP服务器列表
+ chat.mcp.autostart 设置当MCP Server配置更新后是否自动重启服务
+ github.copilot.chat.virtualTools.threshold 同时启用过多的工具会造成聊天上下文过长并导致代码生成时间延长，因此对于不需要的工具应当及时的取消勾选，copilot默认支持最多同时勾选128个工具，可以通过该设置修改所支持的最大工具数量
+ **MCP: Reset Cached Tools**VS Code会缓存MCP 服务器的工具列表。使用该命令可以清除缓存的工具
+ **MCP: Open User Configuration**开启并修改当前用户保存的MCP Server配置
+ **MCP: Open Workspace Folder Configuration**开启并修改当前工作区保存的MCP Server配置
+ **MCP: List Servers**列出所有已配置的MCP Server列表

:::info
结语：

本文档仅总结了部分Copilot的进阶用法，如果想要更全面和深入的掌握Copilot的基础用法和其他进阶用法，请自行参考[VS Code copilot官方文档](https://code.visualstudio.com/docs/copilot/overview)

:::

