---
title: Vite 8.0 经典配置案例
description: 三套经典 Vite 配置案例：Vue3 组件库、Vue3 多端适配 Web 应用、TypeScript Node.js SDK
version: 8.0.0
date: 2026-06-23
---

# Vite 8.0 经典配置案例

> 基于 Vite 8.0.0 整理 | 2026-06-23

---

## 案例一：Vue 3 + TypeScript 前端组件库

### 场景

构建一个可发布到 npm 的 Vue 3 组件库，支持 ESM 和 UMD 格式，TypeScript 类型声明，样式隔离，按需加载。

### 技术栈

- Vue 3 + TypeScript
- Vite 8 + `vite-plugin-dts`（类型声明生成）
- SCSS 样式系统
- Element Plus / 自研组件

### 项目结构

```
my-vue-lib/
├── packages/
│   ├── components/          # 组件源码
│   │   ├── Button/
│   │   │   ├── Button.vue
│   │   │   ├── index.ts
│   │   │   └── style.scss
│   │   └── Input/
│   ├── theme-chalk/         # 样式系统
│   │   ├── index.scss
│   │   └── variables.scss
│   └── index.ts            # 库入口
├── src/
│   └── utils/              # 工具函数
├── dist/                   # 构建输出
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### package.json 关键配置

```json
{
  "name": "my-vue-lib",
  "version": "1.0.0",
  "type": "module",
  "main": "./dist/my-vue-lib.umd.js",
  "module": "./dist/my-vue-lib.es.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/my-vue-lib.es.js",
      "require": "./dist/my-vue-lib.umd.js"
    },
    "./dist/style.css": {
      "import": "./dist/style.css",
      "require": "./dist/style.css"
    }
  },
  "files": ["dist"],
  "peerDependencies": {
    "vue": "^3.3.0"
  },
  "devDependencies": {
    "vite": "^8.0.0",
    "@vitejs/plugin-vue": "^5.0.0",
    "vite-plugin-dts": "^4.0.0",
    "typescript": "^5.5.0",
    "vue": "^3.5.0",
    "sass-embedded": "^1.80.0"
  }
}
```

### vite.config.ts

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import dts from 'vite-plugin-dts'
import { resolve } from 'path'

export default defineConfig({
  // 路径别名
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '~': resolve(__dirname, 'packages')
    }
  },

  plugins: [
    // Vue 3 SFC 支持
    vue(),
    
    // 生成 TypeScript 类型声明文件
    dts({
      tsconfigPath: './tsconfig.json',
      include: ['packages/**', 'src/**'],
      exclude: ['**/*.test.ts', '**/*.spec.ts'],
      // 合并到单一声明文件
      rollupTypes: true,
      // 输出目录与 build.outDir 一致
      outDir: 'dist'
    })
  ],

  build: {
    // 输出目录
    outDir: 'dist',
    
    // 组件库不需要 sourcemap（减小体积）
    sourcemap: false,
    
    // CSS 代码分割（异步组件的样式独立）
    cssCodeSplit: true,
    
    // 使用 Lightning CSS 压缩（Vite 8 默认）
    cssMinify: 'lightningcss',
    
    // 库模式配置
    lib: {
      // 入口文件
      entry: resolve(__dirname, 'packages/index.ts'),
      // UMD 格式下的全局变量名
      name: 'MyVueLib',
      // 输出格式：ES Module + UMD
      formats: ['es', 'umd'],
      // 文件名
      fileName: (format) => `my-vue-lib.${format}.js`,
      // CSS 输出文件名
      cssFileName: 'style'
    },
    
    rollupOptions: {
      // 外部依赖：Vue 和 peerDependencies 不打包
      external: ['vue', 'vue-router'],
      
      output: {
        // UMD 格式下全局变量映射
        globals: {
          vue: 'Vue',
          'vue-router': 'VueRouter'
        },
        // 确保导出命名一致
        exports: 'named'
      }
    },
    
    // 压缩选项
    minify: 'esbuild', // Vite 8 默认，更快
    
    // 清空输出目录
    emptyOutDir: true
  },

  // SCSS 配置
  css: {
    preprocessorOptions: {
      scss: {
        // 使用现代编译器 API（推荐 sass-embedded）
        api: 'modern-compiler',
        // 注入全局变量和函数
        additionalData: `
          @use "sass:math";
          @use "~/theme-chalk/variables.scss" as *;
        `
      }
    }
  }
})
```

### 入口文件 packages/index.ts

```typescript
// 组件导出
export { default as MyButton } from './components/Button'
export { default as MyInput } from './components/Input'

// 样式导出（用户可单独导入）
export { default as default } from './components'

// 类型导出
export type { ButtonProps } from './components/Button/types'
export type { InputProps } from './components/Input/types'
```

### 组件导出 packages/components/Button/index.ts

```typescript
import MyButton from './Button.vue'
export type { ButtonProps } from './types'
export default MyButton
```

### 使用方式

```ts
// 全量导入
import MyVueLib from 'my-vue-lib'
import 'my-vue-lib/dist/style.css'
app.use(MyVueLib)

// 按需导入
import { MyButton } from 'my-vue-lib'
import 'my-vue-lib/dist/style.css' // 或单独导入组件样式
```

### 关键设计决策

| 决策 | 说明 |
|------|------|
| `dts` 插件 | 自动生成 `.d.ts` 文件，避免手动维护 |
| `rollupTypes: true` | 合并类型声明到单一文件，简化引用 |
| `cssCodeSplit: true` | 异步组件样式独立，支持按需加载 |
| `sass-embedded` | Vite 8 推荐，编译速度更快 |
| `additionalData` | 自动注入全局 SCSS 变量，组件内直接使用 |

---

## 案例二：Vue 3 + TypeScript 多端适配 Web 应用

### 场景

构建一个适配 PC、平板、手机多端的 Vue 3 应用，使用 viewport 方案（px → vw/vh）实现响应式布局，兼容多种浏览器。

### 技术栈

- Vue 3 + TypeScript + Vue Router + Pinia
- Vite 8 + `@vitejs/plugin-legacy`（旧浏览器兼容）
- PostCSS（px-to-viewport + autoprefixer）
- SCSS 预处理器

### 项目结构

```
my-web-app/
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router/
│   ├── stores/
│   ├── views/
│   ├── components/
│   ├── composables/
│   ├── utils/
│   └── styles/
│       ├── index.scss
│       ├── variables.scss
│       └── mixins.scss
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── postcss.config.js
```

### package.json

```json
{
  "name": "my-web-app",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.4.0",
    "pinia": "^2.2.0",
    "axios": "^1.7.0"
  },
  "devDependencies": {
    "vite": "^8.0.0",
    "@vitejs/plugin-vue": "^5.0.0",
    "@vitejs/plugin-legacy": "^5.4.0",
    "vue-tsc": "^2.1.0",
    "typescript": "^5.5.0",
    "sass-embedded": "^1.80.0",
    "postcss-px-to-viewport": "^1.1.0",
    "autoprefixer": "^10.4.0"
  }
}
```

### vite.config.ts

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import legacy from '@vitejs/plugin-legacy'
import { resolve } from 'path'

export default defineConfig({
  // 基础路径（相对路径，支持部署到任意目录）
  base: './',

  // 路径解析
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@views': resolve(__dirname, 'src/views'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@styles': resolve(__dirname, 'src/styles')
    },
    // 启用 tsconfig paths 支持（Vite 8）
    tsconfigPaths: true
  },

  plugins: [
    // Vue 3 支持
    vue(),
    
    // 旧浏览器兼容（IE11 + 现代浏览器 Polyfill）
    legacy({
      // 生成现代浏览器 chunk（ES Module）
      targets: {
        chrome: '80',
        firefox: '72',
        safari: '13.1',
        edge: '80'
      },
      // 额外的 Polyfill
      modernPolyfills: ['es.promise.finally'],
      // 生成 legacy  chunk（SystemJS + Polyfill）
      renderLegacyChunks: true,
      // 外部 Polyfill CDN
      externalSystemJSPolyfill: true
    })
  ],

  // CSS 配置
  css: {
    postcss: {
      plugins: [
        // px → vw 转换（多端适配核心）
        require('postcss-px-to-viewport')({
          unitToConvert: 'px',          // 要转换的单位
          viewportWidth: 375,           // 设计稿宽度（移动端标准）
          unitPrecision: 5,             // 转换精度
          propList: ['*', '!font-size'], // 转换属性（font-size 通常不转）
          viewportUnit: 'vw',           // 目标单位
          fontViewportUnit: 'vw',         // 字体单位
          selectorBlackList: ['ignore', 'hairline'], // 忽略选择器
          minPixelValue: 1,             // 最小转换值
          mediaQuery: true,              // 支持媒体查询
          replace: true,                 // 替换而非追加
          exclude: [/node_modules/],     // 排除目录
          landscape: false,              // 横屏适配
          landscapeUnit: 'vh',
          landscapeWidth: 667
        }),
        // 自动添加浏览器前缀
        require('autoprefixer')({
          overrideBrowserslist: [
            '> 1%',
            'last 2 versions',
            'not dead',
            'iOS >= 10',
            'Android >= 6'
          ]
        })
      ]
    },
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler',
        // 注入全局变量和 mixins
        additionalData(source: string, filename: string) {
          // 排除 node_modules 和已有导入的文件
          if (filename.includes('node_modules')) return source
          return `
            @use "@styles/variables.scss" as *;
            @use "@styles/mixins.scss" as *;
            ${source}
          `
        }
      }
    }
  },

  build: {
    // 目标浏览器（Vite 8 默认 baseline-widely-available）
    target: 'baseline-widely-available',
    
    // 资源内联阈值（4KB 以下转为 base64）
    assetsInlineLimit: 4096,
    
    // CSS 代码分割（异步 chunk 的 CSS 独立提取）
    cssCodeSplit: true,
    
    // 使用 Lightning CSS 压缩（Vite 8 默认）
    cssMinify: 'lightningcss',
    
    // 代码块大小警告阈值
    chunkSizeWarningLimit: 600,
    
    // Rollup 输出配置
    rollupOptions: {
      output: {
        // 代码分割策略
        manualChunks: {
          // 将 Vue 生态打包到 vendor
          vue: ['vue', 'vue-router', 'pinia'],
          // 工具库单独打包
          utils: ['axios', 'lodash-es']
        },
        // 资源文件命名
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name || ''
          if (/\.(png|jpe?g|gif|svg|webp|ico)$/i.test(info)) {
            return 'assets/images/[name]-[hash][extname]'
          }
          if (/\.(woff2?|eot|ttf|otf)$/i.test(info)) {
            return 'assets/fonts/[name]-[hash][extname]'
          }
          return 'assets/[name]-[hash][extname]'
        },
        // JS chunk 命名
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js'
      }
    },
    
    // SourceMap（生产环境视需求开启）
    sourcemap: false,
    
    // 压缩
    minify: 'esbuild'
  },

  // 开发服务器
  server: {
    host: '0.0.0.0',      // 允许局域网访问（真机调试）
    port: 5173,
    open: true,           // 自动打开浏览器
    cors: true,           // 启用 CORS
    proxy: {              // API 代理
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    },
    hmr: {
      overlay: true       // 显示编译错误遮罩
    }
  },

  // 预览配置
  preview: {
    host: '0.0.0.0',
    port: 4173
  },

  // 依赖优化
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'axios'],
    exclude: []
  }
})
```

### postcss.config.js（备用方案）

```javascript
export default {
  plugins: {
    'postcss-px-to-viewport': {
      viewportWidth: 375,
      unitPrecision: 5,
      propList: ['*', '!font-size'],
      viewportUnit: 'vw',
      selectorBlackList: ['ignore'],
      minPixelValue: 1,
      mediaQuery: true
    },
    autoprefixer: {
      overrideBrowserslist: ['> 1%', 'last 2 versions', 'not dead']
    }
  }
}
```

### 响应式 SCSS 工具（src/styles/mixins.scss）

```scss
// 断点定义
$breakpoints: (
  'sm': 576px,
  'md': 768px,
  'lg': 992px,
  'xl': 1200px,
  'xxl': 1400px
);

// 响应式 Mixin
@mixin respond-to($breakpoint) {
  @if map-has-key($breakpoints, $breakpoint) {
    @media (min-width: map-get($breakpoints, $breakpoint)) {
      @content;
    }
  }
}

// 使用示例
.my-component {
  width: 100vw;
  
  @include respond-to('md') {
    width: 50vw;
  }
  
  @include respond-to('lg') {
    width: 33.33vw;
  }
}
```

### 关键设计决策

| 决策 | 说明 |
|------|------|
| `base: './'` | 相对路径，支持任意部署目录 |
| `postcss-px-to-viewport` | 基于 375px 设计稿，移动端友好 |
| `@vitejs/plugin-legacy` | 支持旧浏览器（IE11 + 现代浏览器） |
| `manualChunks` | 分离 vendor 和工具库，优化缓存 |
| `host: '0.0.0.0'` | 支持局域网访问，方便真机调试 |
| `tsconfigPaths: true` | Vite 8 原生支持，无需额外插件 |
| `sass-embedded` | 编译速度更快，现代 API |

---

## 案例三：TypeScript + Node.js SDK / npm 包

### 场景

构建一个纯 TypeScript 的 SDK 或工具库，用于 Node.js 环境和浏览器环境（可同构）。支持 ESM 和 CJS 双格式输出，Tree-shaking 友好，包含类型声明。

### 技术栈

- TypeScript 5.x
- Vite 8（库模式）
- `vite-plugin-dts`（类型声明）
- Vitest（单元测试）

### 项目结构

```
my-sdk/
├── src/
│   ├── index.ts            # 入口
│   ├── utils/
│   │   ├── format.ts
│   │   └── validate.ts
│   ├── core/
│   │   ├── client.ts
│   │   └── request.ts
│   └── types/
│       └── index.ts
├── tests/
│   └── utils.test.ts
├── dist/                   # 构建输出
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
└── vitest.config.ts
```

### package.json

```json
{
  "name": "my-sdk",
  "version": "1.0.0",
  "description": "A TypeScript SDK for both Node.js and Browser",
  "type": "module",
  "main": "./dist/my-sdk.cjs.js",
  "module": "./dist/my-sdk.es.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/my-sdk.es.js",
      "require": "./dist/my-sdk.cjs.js"
    },
    "./package.json": "./package.json"
  },
  "files": ["dist"],
  "scripts": {
    "build": "vite build",
    "test": "vitest",
    "test:coverage": "vitest --coverage",
    "lint": "eslint src",
    "prepublishOnly": "npm run build"
  },
  "devDependencies": {
    "vite": "^8.0.0",
    "vite-plugin-dts": "^4.0.0",
    "typescript": "^5.5.0",
    "vitest": "^2.0.0",
    "@vitest/coverage-v8": "^2.0.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

### vite.config.ts

```typescript
import { defineConfig } from 'vite'
import dts from 'vite-plugin-dts'
import { resolve } from 'path'

export default defineConfig({
  // 路径别名
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },

  plugins: [
    // 生成类型声明文件
    dts({
      tsconfigPath: './tsconfig.json',
      include: ['src/**/*.ts'],
      exclude: ['src/**/*.test.ts', 'src/**/*.spec.ts'],
      rollupTypes: true,      // 合并类型声明
      outDir: 'dist',         // 输出目录
      // 生成入口声明文件
      insertTypesEntry: true,
      // 入口文件名称
      entryRoot: 'src'
    })
  ],

  build: {
    // 输出目录
    outDir: 'dist',
    
    // 清空输出目录
    emptyOutDir: true,
    
    // 不生成 sourcemap（SDK 场景通常不需要）
    sourcemap: true, // 或 false，视需求
    
    // 库模式
    lib: {
      // 入口文件
      entry: resolve(__dirname, 'src/index.ts'),
      // 输出格式：ES + CommonJS（Node.js SDK 推荐）
      formats: ['es', 'cjs'],
      // 文件名
      fileName: (format) => `my-sdk.${format}.js`
    },
    
    rollupOptions: {
      // 外部依赖：这些不打包进 SDK
      external: [
        // Node.js 内置模块（打包器会自动识别，显式声明更清晰）
        'fs', 'path', 'http', 'https', 'url', 'util', 'stream', 'crypto',
        // 第三方依赖（由用户项目安装）
        // 'axios', 'lodash-es' 等
      ],
      
      output: {
        // 保持文件结构（方便 Tree-shaking）
        preserveModules: false, // 设为 true 可保留目录结构
        
        // 导出模式
        exports: 'named', // 'named' | 'default' | 'auto'
        
        // 确保目录存在
        interop: 'esModule'
      }
    },
    
    // 压缩选项
    minify: 'esbuild', // SDK 用 esbuild 足够，速度快
    
    // 使用 Oxc 转换（Vite 8 默认）
    // 如需特殊处理，可配置 oxc 选项
    // oxc: { ... }
    
    // CommonJS 转换（处理混合模块）
    commonjsOptions: {
      transformMixedEsModules: true
    }
  },

  // 测试配置（Vite 与 Vitest 集成）
  test: {
    globals: true,
    environment: 'node', // 'node' | 'jsdom' | 'happy-dom'
    include: ['tests/**/*.test.ts'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'tests/']
    }
  }
})
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2020", "DOM"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### 入口文件 src/index.ts

```typescript
// 核心导出
export { MyClient } from './core/client'
export { createRequest } from './core/request'

// 工具导出
export { formatDate } from './utils/format'
export { isValidEmail } from './utils/validate'

// 类型导出
export type { ClientConfig, RequestOptions } from './types'
```

### 使用方式

```ts
// ESM 导入（Node.js / 现代浏览器）
import { MyClient, formatDate } from 'my-sdk'

const client = new MyClient({ apiKey: 'xxx' })

// CJS 导入（旧版 Node.js）
const { MyClient } = require('my-sdk')
```

### 关键设计决策

| 决策 | 说明 |
|------|------|
| `formats: ['es', 'cjs']` | Node.js SDK 不需要 UMD，ES + CJS 足够 |
| `rollupTypes: true` | 合并类型声明为单一文件，简化使用 |
| `external: ['fs', 'path', ...]` | 显式声明 Node.js 内置模块为外部依赖 |
| `sourcemap: true` | SDK 建议开启 sourcemap，方便用户调试 |
| `minify: 'esbuild'` | SDK 用 esbuild 压缩足够，不需要 Terser 的额外优化 |
| `preserveModules` | 可选：保留目录结构，更利于 Tree-shaking |

---

## 三案例对比总结

| 维度 | 案例一：Vue 组件库 | 案例二：多端 Web 应用 | 案例三：Node.js SDK |
|------|-------------------|----------------------|-------------------|
| **目标** | 发布到 npm 的组件库 | 部署到服务器的 Web 应用 | 发布到 npm 的工具库 |
| **输出格式** | ES + UMD | 标准应用（HTML + JS + CSS） | ES + CJS |
| **Vite 模式** | `build.lib` | 默认应用模式 | `build.lib` |
| **CSS 处理** | `cssCodeSplit: true` + 主题系统 | `cssCodeSplit: true` + px2vw | 无 CSS |
| **浏览器兼容** | 由宿主项目决定 | `plugin-legacy` + 浏览器列表 | Node.js 18+ / 现代浏览器 |
| **路径策略** | `base: './'` | `base: './'` | 无 |
| **压缩工具** | esbuild | esbuild | esbuild |
| **类型声明** | `vite-plugin-dts` | `vue-tsc` | `vite-plugin-dts` |
| **SourceMap** | `false` | `false` | `true`（推荐） |
| **外部依赖** | `vue` + peerDeps | 无（全量打包） | Node.js 内置模块 |
| **开发服务器** | 无 | 代理 + HMR + 局域网 | 无 |
| **测试** | 可选 | 可选 | Vitest（推荐） |

---

## 通用最佳实践

### 1. 配置文件类型选择

| 项目类型 | 推荐配置格式 | 原因 |
|----------|-------------|------|
| 纯 JS 项目 | `vite.config.js` | 简单直接 |
| TypeScript 项目 | `vite.config.ts` | 类型安全 |
| 需要复杂逻辑 | `vite.config.ts` + 函数形式 | 条件配置、异步加载 |

### 2. 环境变量管理

```typescript
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    define: {
      __API_URL__: JSON.stringify(env.API_URL),
      __VERSION__: JSON.stringify(process.env.npm_package_version)
    }
  }
})
```

### 3. 多环境配置

```typescript
import { defineConfig } from 'vite'

export default defineConfig(({ command, mode }) => {
  const isDev = command === 'serve'
  const isProd = mode === 'production'
  
  return {
    build: {
      minify: isProd ? 'esbuild' : false,
      sourcemap: isDev ? 'inline' : false
    },
    server: {
      hmr: isDev ? { overlay: true } : false
    }
  }
})
```

### 4. Vite 8 迁移检查清单

- [ ] Node.js 版本 ≥ 20.19 或 ≥ 22.12
- [ ] `esbuild` 选项 → 迁移到 `oxc` 选项
- [ ] `optimizeDeps.esbuildOptions` → `optimizeDeps.rolldownOptions`
- [ ] `build.minify: 'terser'` → 确认是否需要（esbuild 默认更快）
- [ ] `sass` → `sass-embedded`（推荐）
- [ ] `resolve.tsconfigPaths: true`（可选，替代插件）
- [ ] 测试 `plugin-legacy` 兼容性（Vite 8 默认目标变化）

---

> 📖 参考文档：[Vite 官方配置](https://vite.dev/config/) | [Vite 8 迁移指南](https://vite.dev/guide/migration) | [Rolldown 文档](https://rolldown.rs/)
