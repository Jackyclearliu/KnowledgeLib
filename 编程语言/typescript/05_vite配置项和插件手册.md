---
title: Vite 8.0 配置项与插件手册
description: 基于 Vite 8.0.0 官方文档，整理核心配置项、插件 API 及最佳实践
version: 8.0.0
date: 2026-06-23
---

# Vite 8.0 配置项与插件手册

> 基于 Vite 8.0.0 官方文档整理 | 2026-06-23

---

## 一、Vite 8 重大变化速览

Vite 8 于 2026 年 3 月发布，核心变化：

| 特性 | Vite 7 | Vite 8 |
|------|--------|--------|
| 底层打包器 | esbuild + Rollup | **Rolldown**（Rust 统一） |
| JS 转换 | esbuild | **Oxc** |
| JS 压缩 | esbuild | **Oxc Minifier** |
| CSS 压缩 | esbuild | **Lightning CSS**（默认） |
| DevTools | 无 | 内置 `devtools` 选项 |
| tsconfig paths | 需插件 | 原生 `resolve.tsconfigPaths` |
| Node.js 要求 | 18.0+ | **20.19+ / 22.12+** |

> ⚠️ `esbuild` 相关选项已废弃（`optimizeDeps.esbuildOptions` → `rolldownOptions`），但仍保持向后兼容。

---

## 二、配置文件基础

### 2.1 基本结构

```js
import { defineConfig } from 'vite'

export default defineConfig({
  // 配置项...
})
```

`defineConfig` 提供 IDE 类型提示，无需 JSDoc 注释。也支持 TypeScript 配置：

```ts
import type { UserConfig } from 'vite'

export default {
  // ...
} satisfies UserConfig
```

### 2.2 条件配置（函数形式）

```js
export default defineConfig(({ command, mode, isSsrBuild, isPreview }) => {
  if (command === 'serve') {
    return { /* dev 配置 */ }
  }
  return { /* build 配置 */ }
})
```

| 参数 | 说明 |
|------|------|
| `command` | `'serve'`（开发）或 `'build'`（构建） |
| `mode` | `'development'` / `'production'` 或自定义 |
| `isSsrBuild` | 是否为 SSR 构建 |
| `isPreview` | 是否为 preview 模式 |

### 2.3 异步配置

```js
export default defineConfig(async () => {
  const data = await asyncFunction()
  return { /* 使用 data 的配置 */ }
})
```

### 2.4 环境变量

配置文件中**无法直接访问** `.env` 文件变量。需使用 `loadEnv`：

```js
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '') // 第三个参数 '' 表示加载所有变量（不限 VITE_ 前缀）
  return {
    server: { port: Number(env.APP_PORT) || 5173 }
  }
})
```

---

## 三、核心配置项（Shared Options）

### 3.1 基础路径

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `root` | `string` | `process.cwd()` | 项目根目录 |
| `base` | `string` | `/` | 公共基础路径。`'./'` 或 `''` 用于相对路径/嵌入部署 |
| `mode` | `string` | 开发`development`/构建`production` | 覆盖默认模式 |

```js
export default defineConfig({
  base: './',  // 相对路径部署
  mode: 'production' // 强制使用生产模式
})
```

### 3.2 全局替换

```js
export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify('v1.0.0'),
    __DEV__: JSON.stringify(false)
  }
})
```

> 值必须是 JSON 可序列化字符串或单个标识符。TypeScript 用户需在 `vite-env.d.ts` 中声明类型。

### 3.3 路径解析（resolve）

```js
export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '~': path.resolve(__dirname, './src/assets')
    },
    // 或数组形式（支持正则）
    alias: [
      { find: /^@\//, replacement: path.resolve(__dirname, './src/') }
    ],
    dedupe: ['vue'], // 强制使用同一副本（解决 monorepo 重复依赖）
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json'], // 导入时省略的扩展名
    preserveSymlinks: false,
    tsconfigPaths: true, // Vite 8 新增：支持 tsconfig.json 中的 paths 解析
    conditions: ['module', 'browser', 'development|production']
  }
})
```

### 3.4 静态资源

```js
export default defineConfig({
  publicDir: 'public',  // 设为 false 禁用
  cacheDir: 'node_modules/.vite', // 缓存目录
  assetsInclude: ['**/*.gltf'] // 额外静态资源类型
})
```

### 3.5 CSS 配置

```js
export default defineConfig({
  css: {
    // CSS Modules
    modules: {
      scopeBehaviour: 'local',
      generateScopedName: '[name]__[local]___[hash:base64:5]',
      localsConvention: 'camelCaseOnly'
    },
    // PostCSS 配置
    postcss: {
      plugins: [autoprefixer(), pxToViewport()]
    },
    // CSS 预处理器
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler', // 推荐 sass-embedded
        additionalData: `$primary: #1890ff;` // 注入全局变量
      },
      less: { math: 'parens-division' }
    },
    transformer: 'postcss', // 'postcss' | 'lightningcss'（Vite 8）
    lightningcss: { /* Lightning CSS 配置 */ },
    devSourcemap: false // 开发时是否启用 CSS sourcemap
  }
})
```

### 3.6 JSON 处理

```js
export default defineConfig({
  json: {
    namedExports: true,   // 支持命名导入
    stringify: 'auto'     // true / 'auto' / false，大数据量时自动转为 JSON.parse
  }
})
```

### 3.7 Oxc 转换（Vite 8 新默认）

```js
export default defineConfig({
  oxc: {
    jsx: {
      runtime: 'automatic', // 'classic' | 'automatic'
      pragma: 'h',         // classic 模式下使用
      pragmaFrag: 'Fragment'
    },
    jsxInject: `import React from 'react'`, // 自动注入 JSX helper
    include: [/\.[jt]sx$/],  // 自定义转换文件范围
    exclude: [/node_modules/]
  }
})
```

> `esbuild` 选项已废弃，内部自动转换为 `oxc` 选项。

### 3.8 日志与调试

```js
export default defineConfig({
  logLevel: 'info', // 'info' | 'warn' | 'error' | 'silent'
  clearScreen: true, // 是否清屏
  customLogger: createLogger(), // 自定义日志器
  envDir: '.', // .env 文件所在目录
  envPrefix: 'VITE_', // 暴露给客户端的环境变量前缀
  appType: 'spa' // 'spa' | 'mpa' | 'custom'
})
```

---

## 四、开发服务器配置（Server Options）

```js
export default defineConfig({
  server: {
    host: 'localhost',      // '0.0.0.0' 或 true 监听所有地址
    allowedHosts: [],       // 允许的 host（Vite 8 安全增强）
    port: 5173,
    strictPort: false,      // 端口占用时是否退出
    open: true,             // 自动打开浏览器
    https: false,           // 或使用 { key, cert } 对象
    cors: true,             // 或 CorsOptions 对象
    headers: {},            // 响应头
    proxy: {                // 代理配置
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    },
    hmr: {
      overlay: true,      // 显示错误遮罩
      // protocol: 'wss',  // WebSocket 协议
      // clientPort: 3000  // 客户端 WebSocket 端口
    },
    warmup: {             // 预热常用文件（Vite 8）
      clientFiles: ['./src/components/*.vue']
    },
    watch: { usePolling: false }, // 文件监听选项
    middlewareMode: false,  // 中间件模式（配合 Express 等）
    fs: {
      strict: true,         // 限制访问根目录外文件
      allow: ['..'],        // 允许的额外目录
      deny: ['.env']        // 禁止访问的文件
    },
    origin: '',             // 开发时资源 URL 的 origin
    forwardConsole: true    // Vite 8：转发浏览器控制台到终端
  }
})
```

---

## 五、构建配置（Build Options）

```js
export default defineConfig({
  build: {
    target: 'baseline-widely-available', // Vite 8 默认：2025-05-01 Baseline
    // 或 'esnext'、'es2015'、['chrome107', 'firefox104']

    outDir: 'dist',
    assetsDir: 'assets',
    assetsInlineLimit: 4096, // 4KB 以下资源内联为 base64
    
    // Source Map
    sourcemap: false, // true | 'inline' | 'hidden' | false
    
    // CSS
    cssCodeSplit: true,      // CSS 代码分割
    cssTarget: undefined,    // CSS 兼容性目标（默认与 build.target 一致）
    cssMinify: 'lightningcss', // Vite 8 默认 | 'esbuild' | false
    
    // 库模式
    lib: {
      entry: './src/index.ts',
      name: 'MyLib',
      formats: ['es', 'umd'],
      fileName: (format, entryName) => `my-lib.${format}.js`,
      cssFileName: 'my-lib-style'
    },
    
    // Rollup 集成
    rollupOptions: {
      external: ['vue', 'react'],
      output: { globals: { vue: 'Vue' } }
    },
    commonjsOptions: { transformMixedEsModules: true },
    dynamicImportVarsOptions: {},
    
    // 压缩
    minify: 'esbuild', // 'esbuild' | 'terser' | false
    terserOptions: { /* 仅 minify: 'terser' 时生效 */ },
    
    // 其他
    write: true,          // 是否写入磁盘
    emptyOutDir: true,    // 构建前清空输出目录
    copyPublicDir: true,  // 复制 public 目录
    manifest: false,      // 生成 manifest.json
    ssrManifest: false,   // 生成 SSR manifest
    ssr: false,          // SSR 构建
    reportCompressedSize: true, // 报告 gzip 压缩大小
    chunkSizeWarningLimit: 500, // 代码块大小警告阈值（KB）
    watch: null,          // 启用 Rollup 监听模式
    
    // 模块预加载
    modulePreload: { polyfill: true },
    
    // 资产输出（SSR 场景）
    emitAssets: false,
    ssrEmitAssets: false,

    // Rolldown 选项（Vite 8）
    rolldownOptions: {
      output: { minify: true },
      transform: { define: { __DEV__: 'false' } },
      moduleTypes: { '.svg': 'asset' }
    }
  }
})
```

### Vite 8 构建目标特殊值

| 值 | 含义 |
|----|------|
| `baseline-widely-available` | 2025-05-01 Baseline（默认） |
| `esnext` | 最小转译，原生动态导入 |
| `es2015` ~ `es2024` | ECMAScript 版本 |
| `chrome107` | 浏览器 + 版本 |

---

## 六、优化依赖配置（optimizeDeps）

Vite 8 使用 Rolldown 替代 esbuild 进行依赖优化。

```js
export default defineConfig({
  optimizeDeps: {
    entries: ['index.html'],      // 预构建入口
    exclude: ['some-large-lib'],  // 不预构建的依赖
    include: ['dep-to-pre-bundle'], // 强制预构建
    force: false,                 // 强制重新预构建
    holdUntilCrawlEnd: true,      // 等待静态导入爬取完成
    // Vite 8：已废弃 esbuildOptions，使用 rolldownOptions
    rolldownOptions: {
      output: { minify: true },
      transform: { define: {} },
      moduleTypes: {},
      resolve: { extensions: [] }
    }
  }
})
```

> `esbuildOptions` 仍可用但已废弃，内部自动转换为 `rolldownOptions`。

---

## 七、预览配置（Preview Options）

```js
export default defineConfig({
  preview: {
    host: 'localhost',
    allowedHosts: [],
    port: 4173,
    strictPort: false,
    open: false,
    https: false,
    proxy: {},
    cors: true,
    headers: {}
  }
})
```

---

## 八、插件 API

### 8.1 插件基本结构

```js
export default function myPlugin() {
  return {
    name: 'my-plugin', // 必填，用于错误提示
    enforce: 'pre',   // 'pre' | 'post'（可选，控制插件顺序）
    apply: 'build',   // 'serve' | 'build'（可选，控制应用阶段）
    
    // Rollup 通用钩子
    options(options) { /* ... */ },
    buildStart() { /* ... */ },
    resolveId(source, importer) { /* ... */ },
    load(id) { /* ... */ },
    transform(code, id) { /* ... */ },
    buildEnd() { /* ... */ },
    closeBundle() { /* ... */ },
    
    // Vite 专用钩子
    config(config, { mode, command }) { /* ... */ },
    configResolved(resolvedConfig) { /* ... */ },
    configureServer(server) { /* ... */ },
    configurePreviewServer(server) { /* ... */ },
    transformIndexHtml(html, ctx) { /* ... */ },
    handleHotUpdate(ctx) { /* ... */ }
  }
}
```

### 8.2 插件钩子详解

#### config（修改配置）

```js
{
  name: 'config-plugin',
  config(config, { command, mode }) {
    // 返回部分配置（推荐）
    return {
      resolve: { alias: { '@': '/src' } }
    }
  }
}
```

#### configResolved（读取最终配置）

```js
{
  name: 'read-config',
  configResolved(config) {
    // config 为完全解析后的配置
    if (config.command === 'serve') {
      // 开发环境逻辑
    }
  }
}
```

#### configureServer（配置开发服务器）

```js
{
  name: 'server-plugin',
  configureServer(server) {
    // 添加自定义中间件（在 Vite 内部中间件之前）
    server.middlewares.use((req, res, next) => {
      // 自定义处理
      next()
    })
    
    // 返回函数在 Vite 内部中间件之后执行
    return () => {
      server.middlewares.use((req, res, next) => { /* ... */ })
    }
  }
}
```

#### transformIndexHtml（转换 HTML）

```js
{
  name: 'html-transform',
  transformIndexHtml: {
    order: 'pre', // 'pre' | undefined | 'post'
    handler(html, ctx) {
      // 返回字符串、标签描述数组或 { html, tags } 对象
      return html.replace('<title>', '<title>前缀 - ')
    }
  }
}
```

#### handleHotUpdate（自定义 HMR）

```js
{
  name: 'hmr-plugin',
  handleHotUpdate({ file, modules, read, server }) {
    // 过滤或自定义热更新行为
    return modules.filter(m => m.url.includes('should-update'))
  }
}
```

### 8.3 虚拟模块

```js
export default function virtualModulePlugin() {
  const virtualId = 'virtual:my-module'
  const resolvedId = '\0' + virtualId

  return {
    name: 'virtual-module',
    resolveId(id) {
      if (id === virtualId) return resolvedId
    },
    load(id) {
      if (id === resolvedId) {
        return `export const msg = "from virtual module"`
      }
    }
  }
}
```

使用方式：`import { msg } from 'virtual:my-module'`

### 8.4 服务端-客户端通信

```js
// 服务端发送
configureServer(server) {
  server.ws.on('connection', () => {
    server.ws.send('my:event', { msg: 'hello' })
  })
}

// 客户端接收
if (import.meta.hot) {
  import.meta.hot.on('my:event', (data) => console.log(data.msg))
}
```

### 8.5 插件排序

解析后的插件顺序：

1. Alias
2. `enforce: 'pre'` 的用户插件
3. Vite 核心插件
4. 无 `enforce` 的用户插件
5. Vite 构建插件
6. `enforce: 'post'` 的用户插件
7. Vite 后构建插件（压缩、manifest、报告）

---

## 九、常用官方插件清单

| 插件 | 用途 | 安装 |
|------|------|------|
| `@vitejs/plugin-vue` | Vue 3 SFC 支持 | `npm i -D @vitejs/plugin-vue` |
| `@vitejs/plugin-react` | React 支持（Vite 8 使用 Oxc） | `npm i -D @vitejs/plugin-react` |
| `@vitejs/plugin-svelte` | Svelte 支持 | `npm i -D @vitejs/plugin-svelte` |
| `@vitejs/plugin-legacy` | 旧浏览器兼容 | `npm i -D @vitejs/plugin-legacy` |
| `@vitejs/plugin-basic-ssl` | 自签名 HTTPS 证书 | `npm i -D @vitejs/plugin-basic-ssl` |
| `@vitejs/plugin-inspect` | 插件调试检查 | `npm i -D vite-plugin-inspect` |
| `@vitejs/devtools` | Vite 8 开发工具 | `npm i -D @vitejs/devtools` |

### 常用社区插件

| 插件 | 用途 |
|------|------|
| `unplugin-auto-import` | 自动 API 导入 |
| `unplugin-vue-components` | 组件自动导入 |
| `vite-plugin-svg-icons` | SVG 图标管理 |
| `vite-plugin-pwa` | PWA 支持 |
| `vite-plugin-mock` | Mock 数据 |
| `rollup-plugin-visualizer` | 包大小分析 |
| `vite-plugin-compression` | 静态资源压缩 |
| `vite-plugin-dts` | TypeScript 声明文件生成 |

---

## 十、Vite 8 新特性速查

### 10.1 内置 DevTools

```js
export default defineConfig({
  devtools: true // 或 { /* DevToolsConfig */ }
})
```

需要安装 `@vitejs/devtools`。

### 10.2 tsconfig paths 原生支持

```js
export default defineConfig({
  resolve: {
    tsconfigPaths: true // 启用 tsconfig.json 中的 paths 解析
  }
})
```

### 10.3 emitDecoratorMetadata 原生支持

TypeScript 的 `emitDecoratorMetadata` 不再需要外部插件，Vite 8 自动处理。

### 10.4 Wasm SSR 支持

`.wasm?init` 导入在 SSR 环境中正常工作。

### 10.5 浏览器控制台转发

```js
export default defineConfig({
  server: {
    forwardConsole: true // 开发时浏览器控制台输出转发到终端
  }
})
```

编码代理检测到时代码自动激活。

---

## 十一、配置速查表

```js
import { defineConfig } from 'vite'

export default defineConfig({
  // ===== 基础 =====
  root: process.cwd(),
  base: '/',
  mode: undefined, // 自动推断
  define: {},
  plugins: [],
  publicDir: 'public',
  cacheDir: 'node_modules/.vite',
  
  // ===== 解析 =====
  resolve: {
    alias: {},
    dedupe: [],
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json'],
    preserveSymlinks: false,
    tsconfigPaths: false, // Vite 8
    conditions: [],
    mainFields: ['browser', 'module', 'jsnext:main', 'jsnext']
  },
  
  // ===== CSS =====
  css: {
    modules: {},
    postcss: {},
    preprocessorOptions: {},
    preprocessorMaxWorkers: true,
    devSourcemap: false,
    transformer: 'postcss', // 'lightningcss'
    lightningcss: {}
  },
  
  // ===== JSON =====
  json: { namedExports: true, stringify: 'auto' },
  
  // ===== 转换（Vite 8） =====
  oxc: { jsx: {}, jsxInject: '' }, // esbuild 已废弃
  
  // ===== 资产 =====
  assetsInclude: [],
  
  // ===== 日志 =====
  logLevel: 'info',
  customLogger: undefined,
  clearScreen: true,
  
  // ===== 环境 =====
  envDir: '.',
  envPrefix: 'VITE_',
  appType: 'spa', // 'mpa' | 'custom'
  
  // ===== 开发服务器 =====
  server: {
    host: 'localhost',
    allowedHosts: [],
    port: 5173,
    strictPort: false,
    open: false,
    https: false,
    proxy: {},
    cors: { origin: /^https?:\/\/localhost/ },
    headers: {},
    hmr: { overlay: true },
    warmup: {},
    watch: {},
    middlewareMode: false,
    fs: { strict: true, allow: [], deny: ['.env'] },
    origin: undefined,
    forwardConsole: false
  },
  
  // ===== 构建 =====
  build: {
    target: 'baseline-widely-available',
    modulePreload: { polyfill: true },
    outDir: 'dist',
    assetsDir: 'assets',
    assetsInlineLimit: 4096,
    cssCodeSplit: true,
    cssTarget: undefined,
    cssMinify: 'lightningcss',
    sourcemap: false,
    rollupOptions: {},
    commonjsOptions: {},
    dynamicImportVarsOptions: {},
    lib: undefined,
    manifest: false,
    ssrManifest: false,
    ssr: false,
    emitAssets: false,
    ssrEmitAssets: false,
    minify: 'esbuild',
    terserOptions: {},
    write: true,
    emptyOutDir: true,
    copyPublicDir: true,
    reportCompressedSize: true,
    chunkSizeWarningLimit: 500,
    watch: null,
    rolldownOptions: {} // Vite 8
  },
  
  // ===== 依赖优化 =====
  optimizeDeps: {
    entries: [],
    exclude: [],
    include: [],
    force: false,
    holdUntilCrawlEnd: true,
    rolldownOptions: {} // Vite 8，esbuildOptions 已废弃
  },
  
  // ===== 预览 =====
  preview: {
    host: 'localhost',
    allowedHosts: [],
    port: 4173,
    strictPort: false,
    open: false,
    https: false,
    proxy: {},
    cors: true,
    headers: {}
  },
  
  // ===== 实验性（Vite 8） =====
  devtools: false,
  future: {}
})
```

---

> 📖 更多详情参考：[Vite 官方文档](https://vite.dev/config/) | [Vite 8 迁移指南](https://vite.dev/guide/migration)
