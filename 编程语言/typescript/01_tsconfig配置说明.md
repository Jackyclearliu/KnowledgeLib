# TypeScript tsconfig.json 配置说明

> 本文档整理了 TypeScript `tsconfig.json` 的所有配置项，包含配置名称、说明、可选值及默认值。
> **基于 TypeScript 6.0 版本整理。**
> 
> ⚠️ TypeScript 6.0 是最后一个基于 JavaScript 的版本，为 TypeScript 7.0（Go 语言重写）铺路。本版本引入了多项默认值变更和弃用项，旨在帮助项目平滑过渡到 v7。

---

## 目录

- [顶层配置（Top-Level）](#顶层配置top-level)
- [编译选项（compilerOptions）](#编译选项compileroptions)
  - [项目选项](#项目选项)
  - [模块解析选项](#模块解析选项)
  - [源映射选项](#源映射选项)
  - [实验性选项](#实验性选项)
  - [高级选项](#高级选项)
  - [JavaScript 支持](#javascript-支持)
  - [编辑器支持](#编辑器支持)
  - [输出选项](#输出选项)
- [迁移指南](#迁移指南)
- [Watch 选项（watchOptions）](#watch-选项watchoptions)
- [类型获取（typeAcquisition）](#类型获取typeacquisition)

---

## 顶层配置（Top-Level）

| 配置名称 | 配置说明 | 类型 | 默认值 |
|---------|---------|------|--------|
| `extends` | 继承另一个 tsconfig.json 的配置 | `string` | — |
| `files` | 明确指定要包含在编译中的文件列表 | `string[]` | — |
| `include` | 指定要包含的文件/目录模式（支持 glob） | `string[]` | — |
| `exclude` | 指定要排除的文件/目录模式 | `string[]` | `["node_modules", "bower_components", "jspm_packages"]` |
| `references` | 项目引用，用于复合项目配置 | `ProjectReference[]` | — |
| `compilerOptions` | 编译器选项 | `object` | — |
| `watchOptions` | 文件监视选项 | `object` | — |
| `typeAcquisition` | 类型自动获取配置 | `object` | — |

> **注意**：`files`、`include`、`exclude` 至少有一个需要配置，否则编译器不知道编译哪些文件。

---

## 编译选项（compilerOptions）

### 项目选项

控制项目的基本行为和目标环境。

| 配置名称 | 配置说明 | 可选值 | 默认值 |
|---------|---------|--------|--------|
| `target` | 指定编译后的 JavaScript 目标版本。TS 5.x 默认值为 `"ES5"`，TS 6.0 默认改为 `"ES2025"`（当前最新 ECMAScript 版本，后续会随规范更新浮动）。这意味着编译器默认不再将代码降级到旧版 ES5。如果你的项目需要兼容旧浏览器或旧版 Node.js，请**显式设置** `"ES5"` 或 `"ES2015"`。新增 `"ES2025"` 选项，支持 `Promise.try()`、新 Set 方法、`RegExp.escape()` 等 API。 | `"ES3"`, `"ES5"`, `"ES6"`/`"ES2015"`, `"ES2016"`, `"ES2017"`, `"ES2018"`, `"ES2019"`, `"ES2020"`, `"ES2021"`, `"ES2022"`, `"ES2023"`, `"ES2025"`, `"ESNext"` | `"ES2025"` |
| `lib` | 指定要包含在编译中的 API 库文件。TS 6.0 新增 `"ES2025"` 选项。另外，`"DOM"` 现已**自动包含** `"DOM.Iterable"` 和 `"DOM.AsyncIterable"`（不再需要单独列出，单独列出也已为空声明）。如需使用 `Temporal` API，需将 `target` 或 `lib` 设置为 `"ESNext"`。 | `"ES5"` ~ `"ES2025"`, `"ESNext"`, `"DOM"`, `"DOM.Iterable"`, `"DOM.AsyncIterable"`, `"WebWorker"`, `"ScriptHost"`, `"FetchAPI"` 等 | 根据 `target` 自动选择 |
| `module` | 指定模块系统。TS 5.x 默认值为 `"CommonJS"`（当 `target < ES6`）或 `"ES6"`，TS 6.0 默认统一改为 `"ESNext"`。ESM 已成为主流模块格式，因此新版本默认输出 ES 模块。如果你的项目仍需要 CommonJS 输出（如旧版 Node.js 或某些测试环境），请**显式设置** `"CommonJS"`。`"AMD"` / `"System"` / `"UMD"` 已被弃用，v7 将移除。 | `"None"`, `"CommonJS"`, `"AMD"`, `"System"`, `"UMD"`, `"ES6"`/`"ES2015"`, `"ES2020"`, `"ES2022"`, `"ESNext"`, `"Node16"`, `"NodeNext"` | `"ESNext"` |
| `moduleResolution` | 指定模块解析策略。`"node"` 即 `"node10"`（传统 Node.js 解析），`"classic"` 为旧版 TypeScript 解析方式。`"node"` 和 `"classic"` 已被弃用，v7 将移除。新项目推荐使用 `"node16"`、`"nodenext"` 或 `"bundler"`。默认逻辑：当 `module` 为 `"AMD"`/`"UMD"`/`"System"` 时为 `"node"`；当 `module` 为 `"Node16"`/`"NodeNext"` 时为 `"node16"`；当 `module` 为 `"ESNext"` 或 `"Preserve"` 时为 `"bundler"`；否则为 `"node"`。 | `"classic"`, `"node"`, `"node16"`, `"nodenext"`, `"bundler"` | 见配置说明 |
| `jsx` | 指定 JSX 代码的生成方式 | `"preserve"`, `"react"`, `"react-native"`, `"react-jsx"`, `"react-jsxdev"` | `"preserve"` |
| `jsxFactory` | 指定 JSX 工厂函数（当 `jsx` 为 `"react"` 时） | `string` | `"React.createElement"` |
| `jsxFragmentFactory` | 指定 JSX Fragment 工厂函数 | `string` | `"React.Fragment"` |
| `jsxImportSource` | 指定 JSX 运行时库的导入源 | `string` | `"react"` |
| `rootDir` | 指定输入文件的根目录。TS 5.x 默认值为所有非声明输入文件的**最长公共路径**（需推断），TS 6.0 默认改为 `"."`（即 tsconfig.json 所在目录）。这减少了编译器的文件结构分析开销，但可能导致输出目录结构变化。如果你的源码在 `src` 目录下，且之前依赖旧默认推断行为，请**显式设置** `"rootDir": "./src"`。 | `string` | `"."` |
| `outDir` | 指定输出目录 | `string` | — |
| `outFile` | **已弃用（v7 将移除）**，将所有输出文件合并为一个文件。在模块化已成为主流的今天，合并输出文件的使用场景极少，因此该选项已被弃用。如需类似功能，请改用打包工具（如 Rollup、Webpack、Vite）处理。 | `string` | — |
| `declaration` | 生成 `.d.ts` 声明文件 | `boolean` | `false` |
| `declarationDir` | 指定声明文件的输出目录 | `string` | — |
| `declarationMap` | 为声明文件生成 sourcemap | `boolean` | `false` |
| `emitDeclarationOnly` | 只输出声明文件，不输出 JS 文件 | `boolean` | `false` |
| `composite` | 启用项目编译（用于项目引用） | `boolean` | `false` |
| `incremental` | 启用增量编译 | `boolean` | `true`（当 `composite` 为 `true` 时） |
| `tsBuildInfoFile` | 指定增量编译信息文件的路径 | `string` | `.tsbuildinfo` |
| `removeComments` | 删除编译后的注释 | `boolean` | `false` |
| `noEmit` | 不输出任何文件（只进行类型检查） | `boolean` | `false` |
| `noEmitOnError` | 有错误时不输出文件 | `boolean` | `true`（当 `composite` 为 `true` 时），否则 `false` |
| `preserveConstEnums` | 保留 `const enum` 声明，不内联 | `boolean` | `false` |
| `isolatedModules` | 确保每个文件可以独立编译（用于 Babel 等工具） | `boolean` | `true`（当 `verbatimModuleSyntax` 为 `true` 时） |
| `verbatimModuleSyntax` | 保留导入/导出的语法（不转换 `import`/`export`） | `boolean` | `false` |
| `allowSyntheticDefaultImports` | 允许从没有默认导出的模块进行默认导入。TS 5.x 默认值为 `false`，TS 6.0 中 `false` 已被**弃用**（v7 将移除）。`true` 是推荐值，且在新项目中默认生效。如需显式关闭，建议先评估是否真的需要，因为禁用后可能导致大量 `has no default export` 报错。 | `boolean` | `true`（当 `module` 为 `"node16"`/`"nodenext"` 时），否则 `true`（`false` 已弃用） |
| `esModuleInterop` | 启用 ES 模块与 CommonJS 模块的互操作性。TS 5.x 中 `false` 是常见设置，但 TS 6.0 中 `false` 已被**弃用**（v7 将移除）。`true` 是推荐值，可让 `import * as fs from 'fs'` 和 `import fs from 'fs'` 都能正常工作。旧项目若之前设置了 `false`，建议迁移为 `true` 或移除该配置（默认即为 `true`）。 | `boolean` | `true`（`false` 已弃用） |
| `forceConsistentCasingInFileNames` | 强制文件名大小写一致 | `boolean` | `true` |
| `skipLibCheck` | 跳过声明文件（`.d.ts`）的类型检查 | `boolean` | `true`（当 `composite` 为 `true` 时） |
| `charset` | **已弃用**，不再生效 | `string` | `"utf8"` |
| `ignoreDeprecations` | **新增选项**，用于过渡期间忽略 TypeScript 6.0 的弃用警告。如果你的项目有大量旧配置（如 `baseUrl`、`target: es5` 等），可暂时设置此选项避免报错，但**必须在迁移到 TS 7.0 之前移除**（v7 将不支持任何弃用选项）。仅接受 `"6.0"` 作为值。 | `"6.0"` | — |
| `noUncheckedSideEffectImports` | 检查副作用导入（如 `import "some-polyfill"`）中的拼写错误。TS 5.x 默认值为 `false`，TS 6.0 默认改为 `true`。开启后，如果拼写错误（如 `import "loding"`），编译器会报错。如果你的项目确实需要动态导入不存在的模块（极少见），可显式设置为 `false`。 | `boolean` | `true` |
| `libReplacement` | 允许通过 npm 包替换内置 lib 文件。TS 5.x 默认值为 `true`，TS 6.0 默认改为 `false`。因为新项目中该功能几乎不会用到，且开启后会导致大量失败的模块解析和额外的文件监视，影响性能。如果你的项目确实使用了自定义 lib 替换包，请显式设置为 `true`。 | `boolean` | `false` |

> **💡 提示**：`lib` 中 `"DOM"` 现已自动包含 `"DOM.Iterable"` 和 `"DOM.AsyncIterable"`，不再需要单独列出。它们仍可写但已为空声明。
>
> **💡 提示**：`target` 和 `lib` 新增 `"ES2025"` 选项，支持 `Promise.try()`、新 Set 方法、`RegExp.escape()` 等最新 API。
>
> **💡 提示**：`Temporal` API 类型现已支持，需将 `target` 或 `lib` 设置为 `"ESNext"`。

---

### 模块解析选项

| 配置名称 | 配置说明 | 可选值 | 默认值 |
|---------|---------|--------|--------|
| `baseUrl` | **已弃用（v7 将移除）**，指定非相对模块解析的基础目录。`baseUrl` 在 `paths` 之外还会作为模块查找根，容易导致意外导入。TS 6.0 建议废除 `baseUrl`，直接在 `paths` 中写**完整路径**（如 `"@mail": ["./src/services/mail/*"]"`）。旧项目可使用实验性工具 `ts5to6` 自动迁移。 | `string` | — |
| `paths` | 指定模块名到路径映射。TS 6.0 建议不再依赖 `baseUrl`，直接在路径中写完整相对路径。例如之前 `"baseUrl": "./src", "paths": { "@mail": ["./services/mail/*"] }"`，现在改为 `"paths": { "@mail": ["./src/services/mail/*"] }"`。 | `object` | — |
| `rootDirs` | 指定虚拟根目录列表（用于合并分散的源代码） | `string[]` | — |
| `typeRoots` | 指定类型声明文件的搜索目录 | `string[]` | `["node_modules/@types"]` |
| `types` | 指定要包含的类型包名称。TS 5.x 默认会**自动枚举** `node_modules/@types` 下所有类型包，这可能导致成百上千个不需要的声明文件被加载，严重影响编译速度。TS 6.0 默认改为 `[]`（空数组），只加载显式声明的类型包。如果你的项目使用了 `process`、`describe` 等全局类型，请**显式添加**到 `types` 中（如 `"types": ["node", "jest"]`）。如需恢复旧行为（不推荐），设置 `"types": ["*"]`。许多项目因此提升了 **20-50%** 的构建速度。 | `string[]` | `[]` |
| `resolveJsonModule` | 允许导入 `.json` 文件 | `boolean` | `false` |
| `traceResolution` | 输出模块解析日志（用于调试） | `boolean` | `false` |
| `allowArbitraryExtensions` | 允许导入任意扩展名的文件（实验性） | `boolean` | `false` |
| `customConditions` | 指定 package.json 中 `exports` 字段的自定义条件 | `string[]` | — |
| `resolvePackageJsonExports` | 在解析 `node_modules` 中的包时使用 `exports` 字段 | `boolean` | `true`（当 `moduleResolution` 为 `"node16"`/`"nodenext"`/`"bundler"` 时） |
| `resolvePackageJsonImports` | 在解析 `#*` 路径时使用 `imports` 字段。TS 6.0 支持 Node.js 24.14+ 的 `#/` 子路径导入（需 `moduleResolution` 为 `"nodenext"` 或 `"bundler"`）。例如 `package.json` 中 `"imports": { "#/data/*": "./src/data/*" }`，然后 `import data from '#/data/index.js'`。 | `boolean` | `true`（当 `moduleResolution` 为 `"node16"`/`"nodenext"`/`"bundler"` 时） |

> **⚠️ 注意**：`types` 默认值改为 `[]` 后，需要显式声明所需的类型包（如 `"node"`、`"jest"`），否则全局类型（如 `process`、`describe`）将不可用。如需恢复旧行为，设置 `"types": ["*"]`。
>
> **⚠️ 注意**：`baseUrl` 已被弃用，建议在 `paths` 中直接写完整路径（如 `"@mail": ["./src/services/mail/*"]"`）。

---

### 源映射选项

| 配置名称 | 配置说明 | 可选值 | 默认值 |
|---------|---------|--------|--------|
| `sourceMap` | 生成对应的 `.js.map` sourcemap 文件 | `boolean` | `false` |
| `inlineSourceMap` | 将 sourcemap 内联到输出文件中 | `boolean` | `false` |
| `inlineSources` | 将源代码内联到 sourcemap 中（需 `inlineSourceMap` 或 `sourceMap`） | `boolean` | `false` |
| `mapRoot` | 指定 sourcemap 文件的根路径 | `string` | — |
| `sourceRoot` | 指定调试时源文件的根路径 | `string` | — |

---

### 实验性选项

| 配置名称 | 配置说明 | 可选值 | 默认值 |
|---------|---------|--------|--------|
| `experimentalDecorators` | 启用实验性的装饰器语法（旧版 TC39 提案） | `boolean` | `false` |
| `emitDecoratorMetadata` | 为装饰器生成类型元数据（需要 `reflect-metadata`） | `boolean` | `false` |

---

### 高级选项

| 配置名称 | 配置说明 | 可选值 | 默认值 |
|---------|---------|--------|--------|
| `strict` | 启用所有严格类型检查选项。TS 5.x 默认值为 `false`，TS 6.0 默认改为 `true`。这是最大的变更之一，意味着新项目会立即启用 `strictNullChecks`、`strictFunctionTypes` 等所有严格选项。如果你的项目之前依赖 `strict: false`（例如有大量隐式 `any`），请**显式设置** `"strict": false`，但建议逐步开启以提高代码质量。 | `boolean` | `true` |
| `alwaysStrict` | 在每个文件开头添加 `"use strict"`。默认值为 `true`（当 `target >= ES2015`）。TS 6.0 中 `false` 已被**弃用**（v7 将移除），因为现代运行时已全面支持严格模式。 | `boolean` | `true`（当 `target` >= `"ES2015"`），`false` 已弃用 |
| `strictNullChecks` | 启用严格的 `null`/`undefined` 检查 | `boolean` | `false` |
| `strictFunctionTypes` | 启用严格的函数类型检查 | `boolean` | `false` |
| `strictBindCallApply` | 对 `bind`、`call`、`apply` 启用严格类型检查 | `boolean` | `false` |
| `strictPropertyInitialization` | 确保类属性在构造函数中初始化 | `boolean` | `false` |
| `noImplicitAny` | 禁止隐式的 `any` 类型 | `boolean` | `true`（当 `strict` 为 `true` 时） |
| `noImplicitThis` | 禁止隐式的 `this` 类型为 `any` | `boolean` | `true`（当 `strict` 为 `true` 时） |
| `useUnknownInCatchVariables` | 将 `catch` 子句中的变量类型设为 `unknown` 而非 `any` | `boolean` | `true`（当 `strict` 为 `true` 且 `target` >= `"ES2022"`） |
| `exactOptionalPropertyTypes` | 区分可选属性与 `undefined` 值 | `boolean` | `false` |
| `noImplicitReturns` | 要求函数的所有分支都有返回值 | `boolean` | `false` |
| `noFallthroughCasesInSwitch` | 禁止 `switch` 语句中的穿透（fallthrough） | `boolean` | `false` |
| `noUncheckedIndexedAccess` | 索引访问结果包含 `undefined` | `boolean` | `false` |
| `noImplicitOverride` | 要求覆盖父类方法时使用 `override` 关键字 | `boolean` | `false` |
| `noPropertyAccessFromIndexSignature` | 禁止对索引签名使用点号访问（强制使用 `[]`） | `boolean` | `false` |
| `noUnusedLocals` | 报告未使用的局部变量 | `boolean` | `false` |
| `noUnusedParameters` | 报告未使用的函数参数 | `boolean` | `false` |
| `allowUnreachableCode` | 是否允许不可达代码 | `boolean` / `undefined` | `undefined` |
| `allowUnusedLabels` | 是否允许未使用的标签 | `boolean` / `undefined` | `undefined` |
| `checkJs` | 对 `.js` 文件进行类型检查 | `boolean` | `false` |
| `maxNodeModuleJsDepth` | 在 `node_modules` 中搜索 `.js` 文件的最大深度 | `number` | `0` |
| `pretty` | 使用彩色和上下文格式化错误信息 | `boolean` | `true`（当 `true` 为 TTY 时） |
| `newLine` | 指定输出文件的换行符 | `"crlf"`, `"lf"` | 平台相关 |
| `noErrorTruncation` | 禁止截断错误信息 | `boolean` | `false` |
| `preserveWatchOutput` | 在 `watch` 模式下不清除控制台输出 | `boolean` | `false` |
| `listEmittedFiles` | 打印所有输出文件的列表 | `boolean` | `false` |
| `listFiles` | 打印所有参与编译的文件列表 | `boolean` | `false` |
| `explainFiles` | 解释为什么每个文件被包含在编译中 | `boolean` | `false` |
| `extendedDiagnostics` | 输出详细的编译性能诊断信息 | `boolean` | `false` |
| `generateCpuProfile` | 生成 CPU 性能分析文件 | `string` | — |
| `generateTrace` | 生成编译跟踪文件 | `string` | — |
| `locale` | 指定错误信息的语言 | `string` | 系统默认 |
| `useDefineForClassFields` | 使用 `Object.defineProperty` 定义类字段（符合 ECMAScript 标准） | `boolean` | `true`（当 `target` >= `"ES2022"`） |
| `emitBOM` | 在输出文件开头添加 UTF-8 BOM | `boolean` | `false` |
| `stripInternal` | 移除标记为 `@internal` 的 JSDoc 注释 | `boolean` | `false` |
| `noResolve` | 不解析 `/// <reference path="..." />` | `boolean` | `false` |
| `noLib` | 不包含默认的 lib 文件 | `boolean` | `false` |
| `disableSizeLimit` | 禁用 JavaScript 项目的大小限制 | `boolean` | `false` |
| `disableSourceOfProjectReferenceRedirect` | 禁用项目引用的 source 重定向 | `boolean` | `false` |
| `disableSolutionSearching` | 禁用解决方案搜索 | `boolean` | `false` |
| `assumeChangesOnlyAffectDirectDependencies` | 假设只有直接依赖会变化（加速 watch） | `boolean` | `false` |
| `declarationOnly` | **拼写错误配置**，请使用 `emitDeclarationOnly` | — | — |

> **⚠️ 注意**：`strict` 默认已改为 `true`。如果你的项目依赖旧默认（`strict: false`），需要显式设置 `"strict": false`。
>
> **⚠️ 注意**：`/// <reference no-default-lib="true"/>` 指令已被弃用，请使用 `--noLib` 或 `--libReplacement` 替代。

---

### JavaScript 支持

| 配置名称 | 配置说明 | 可选值 | 默认值 |
|---------|---------|--------|--------|
| `allowJs` | 允许编译 JavaScript 文件 | `boolean` | `false` |
| `checkJs` | 对 `.js` 文件进行类型检查（需要 `allowJs`） | `boolean` | `false` |
| `maxNodeModuleJsDepth` | 在 `node_modules` 中搜索 `.js` 文件的最大深度 | `number` | `0` |

---

### 编辑器支持

| 配置名称 | 配置说明 | 可选值 | 默认值 |
|---------|---------|--------|--------|
| `plugins` | 指定要加载的语言服务插件列表 | `Plugin[]` | — |

---

### 输出选项

| 配置名称 | 配置说明 | 可选值 | 默认值 |
|---------|---------|--------|--------|
| `downlevelIteration` | **已弃用（v7 将移除）**，为旧环境提供完整的可迭代对象/迭代器支持。在现代浏览器和 Node.js 已全面支持原生迭代器的背景下，该选项的使用场景极少。如果你的代码确实需要在 ES5 环境下使用 `for...of` 循环，请在升级到 TS 7.0 之前改用打包工具（如 Babel）处理降级。 | `boolean` | `false` |
| `importHelpers` | 从 `tslib` 导入辅助函数 | `boolean` | `false` |
| `importsNotUsedAsValues` | **已弃用**，请使用 `verbatimModuleSyntax` 或 `preserveValueImports` | `"remove"`, `"preserve"`, `"error"` | `"remove"` |
| `preserveValueImports` | **已弃用**，保留未被使用的值导入（在 `verbatimModuleSyntax` 后不再使用） | `boolean` | `false` |
| `sourceMap` | 生成 sourcemap 文件 | `boolean` | `false` |
| `inlineSourceMap` | 将 sourcemap 内联到输出文件 | `boolean` | `false` |
| `inlineSources` | 将源代码内联到 sourcemap 中 | `boolean` | `false` |
| `mapRoot` | 指定 sourcemap 文件的根目录 | `string` | — |
| `sourceRoot` | 指定调试器应该查找源文件的根目录 | `string` | — |
| `newLine` | 指定输出文件的换行符 | `"crlf"`, `"lf"` | 平台相关 |
| `emitBOM` | 在输出文件开头添加 UTF-8 BOM | `boolean` | `false` |
| `removeComments` | 删除所有注释（除 `/**/`） | `boolean` | `false` |
| `noEmitHelpers` | 不生成辅助函数（需要外部提供） | `boolean` | `false` |
| `importHelpers` | 从 `tslib` 导入辅助函数 | `boolean` | `false` |

---

## 迁移指南

### 从 TS 5.x 迁移到 TS 6.0

TypeScript 6.0 引入了多项默认值变更和弃用项。以下是迁移要点：

#### 1. 默认值变更（需检查项目是否依赖旧默认值）

| 配置项 | 旧默认值 | 新默认值 | 影响 |
|--------|---------|---------|------|
| `strict` | `false` | `true` | 类型检查更严格，可能暴露新错误 |
| `module` | `CommonJS` | `ESNext` | 输出模块格式变化 |
| `target` | `ES5` | `ES2025` | 不再向下编译到旧版 JS |
| `types` | 枚举所有 `@types` | `[]` | 全局类型可能不可用，需显式配置 |
| `rootDir` | 推断公共路径 | `.` | 输出目录结构可能变化 |
| `noUncheckedSideEffectImports` | `false` | `true` | 副作用导入拼写错误会被检测 |
| `libReplacement` | `true` | `false` | lib 替换默认关闭，提升性能 |

#### 2. 已弃用配置（v7 将彻底移除）

以下配置已被弃用，建议尽快迁移：

- **`baseUrl`** — 路径别名基础目录，建议在 `paths` 中写完整路径
- **`downlevelIteration`** — 旧环境迭代器支持
- **`outFile`** — 合并输出文件
- **`target: es5`** — ES5 目标
- **`module: amd/umd/systemjs`** — 旧模块格式
- **`moduleResolution: node`**（即 `node10`）和 `classic`
- **`esModuleInterop: false`** 和 `allowSyntheticDefaultImports: false`
- **`alwaysStrict: false`**
- 旧版 `module` 关键字声明命名空间（`module X {}`），改用 `namespace X {}`
- `/// <reference no-default-lib="true"/>` 指令，改用 `--noLib`

#### 3. 忽略弃用警告（过渡方案）

在迁移过程中，可在 `tsconfig.json` 中设置：

```json
{
  "compilerOptions": {
    "ignoreDeprecations": "6.0"
  }
}
```

⚠️ **注意**：此选项仅在 TS 6.0 有效，**TS 7.0 将不支持任何弃用选项**。

#### 4. 自动迁移工具

微软提供实验性工具 `ts5to6`，可自动调整 `baseUrl` 和 `rootDir`：

```bash
npx ts5to6
```

---

## CLI 行为变更

在 TS 5.x 中，运行 `tsc foo.ts` 会忽略同一目录下的 `tsconfig.json`。

在 TS 6.0 中，这会产生错误：

```
error TS5112: tsconfig.json is present but will not be loaded if files are specified on commandline. Use '--ignoreConfig' to skip this error.
```

如需忽略 `tsconfig.json` 直接编译文件，使用：

```bash
tsc --ignoreConfig foo.ts
```

---

## Watch 选项（watchOptions）

配置 `--watch` 模式下的文件监视行为。

| 配置名称 | 配置说明 | 可选值 | 默认值 |
|---------|---------|--------|--------|
| `watchFile` | 文件监视策略 | `"fixedPollingInterval"`, `"priorityPollingInterval"`, `"dynamicPriorityPolling"`, `"fixedChunkSizePolling"`, `"useFsEvents"`, `"useFsEventsOnParentDirectory"` | `"useFsEvents"` |
| `watchDirectory` | 目录监视策略 | `"fixedPollingInterval"`, `"dynamicPriorityPolling"`, `"fixedChunkSizePolling"`, `"useFsEvents"` | `"useFsEvents"` |
| `fallbackPolling` | 当系统不支持原生文件监视时的回退策略 | `"fixedPollingInterval"`, `"priorityPollingInterval"`, `"dynamicPriorityPolling"`, `"fixedChunkSizePolling"` | `"priorityPollingInterval"` |
| `synchronousWatchDirectory` | 同步监视目录变化 | `boolean` | `false` |
| `excludeDirectories` | 排除特定目录的监视 | `string[]` | `[]` |
| `excludeFiles` | 排除特定文件的监视 | `string[]` | `[]` |

---

## 类型获取（typeAcquisition）

控制自动类型定义获取行为（用于 JavaScript 项目）。

| 配置名称 | 配置说明 | 可选值 | 默认值 |
|---------|---------|--------|--------|
| `enable` | 启用自动类型获取 | `boolean` | `true`（当 `allowJs` 为 `true` 且没有 `types` 选项时） |
| `include` | 明确包含的类型包 | `string[]` | `[]` |
| `exclude` | 排除的类型包 | `string[]` | `[]` |
| `disableFilenameBasedTypeAcquisition` | 禁用基于文件名的类型获取 | `boolean` | `false` |

---

## 常用配置示例

### 现代 Node.js 项目

```json
{
  "compilerOptions": {
    "target": "ES2025",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2025"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "types": ["node"]
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### 前端 React 项目

```json
{
  "compilerOptions": {
    "target": "ES2025",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2025", "DOM"],
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true
  },
  "include": ["src"]
}
```

### 库项目（发布到 npm）

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2025"],
    "outDir": "./lib",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "composite": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "lib", "**/*.test.ts"]
}
```

---

## 参考链接

- [TypeScript 官方文档 - tsconfig.json](https://www.typescriptlang.org/docs/handbook/tsconfig-json.html)
- [TypeScript 编译选项完整列表](https://www.typescriptlang.org/tsconfig)
- [TypeScript 6.0 发布说明](https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/)
- [TypeScript 6.0 迁移指南](https://blog.logrocket.com/typescript-v6-migration-guide/)
- [ts5to6 自动迁移工具](https://github.com/microsoft/TypeScript/tree/main/ts5to6)

---

> 📅 文档更新日期：2026-06-23
> 📌 基于 TypeScript 6.0 版本