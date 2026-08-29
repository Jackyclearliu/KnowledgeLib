# package.json 配置项完全手册

> 本文档整理了 Node.js 项目 `package.json` 中的所有配置项，包含说明、可选值及使用建议。

---

## 目录

1. [核心配置项](#一核心配置项)
2. [脚本配置](#二脚本配置scripts)
3. [依赖配置](#三依赖配置)
4. [发布与文件配置](#四发布与文件配置)
5. [运行环境配置](#五运行环境配置)
6. [项目信息配置](#六项目信息配置)
7. [包管理器配置](#七包管理器配置)
8. [TypeScript 相关配置](#八typescript-相关配置)
9. [其他常用配置](#九其他常用配置)

---

## 一、核心配置项

### 1. `name`

**说明**：包的名称，是项目在 npm 仓库中的唯一标识。

**规则**：
- 长度 ≤ 214 个字符
- 只能包含小写字母、数字、连字符 `-`、下划线 `_` 和点 `.`
- 不能以点或下划线开头
- 不能包含大写字母
- 不能是 Node.js / npm 保留名（如 `http`、`node_modules` 等）

**作用域包（Scoped Package）**：

```json
{
  "name": "@username/package-name"
}
```

- 作用域以 `@` 开头，`/` 分隔
- 作用域包默认是私有的，发布到 npm 需指定 `--access public`

---

### 2. `version`

**说明**：包的版本号，必须遵循 [SemVer](https://semver.org/)（语义化版本）规范。

**格式**：`主版本号.次版本号.修订号`

```
MAJOR.MINOR.PATCH
1.0.0
```

| 版本位 | 说明 | 示例 |
|--------|------|------|
| MAJOR | 不兼容的 API 修改 | `2.0.0` |
| MINOR | 向下兼容的功能新增 | `1.1.0` |
| PATCH | 向下兼容的问题修复 | `1.0.1` |

**版本前缀**：

| 前缀 | 含义 | 示例 |
|------|------|------|
| `^` | 兼容版本，不改变最左边的非零数字 | `^1.2.3` → `>=1.2.3 <2.0.0` |
| `~` | 近似版本，只改变最后一位 | `~1.2.3` → `>=1.2.3 <1.3.0` |
| `>` / `<` / `>=` / `<=` | 范围比较 | `>1.0.0` |
| `=` | 精确版本 | `=1.0.0` |
| `-` | 范围 | `1.0.0 - 2.0.0` |
| `*` / `x` / `X` | 通配符 | `1.x` 或 `*` |

---

### 3. `description`

**说明**：包的简短描述，显示在 npm 搜索结果中。

```json
{
  "description": "A utility library for string manipulation"
}
```

---

### 4. `main`

**说明**：包的入口文件，当其他项目 `require('your-package')` 时加载的文件。

```json
{
  "main": "dist/index.js"
}
```

**默认值**：`index.js`

---

### 5. `module`

**说明**：ES Module 入口文件，供支持 ESM 的构建工具（如 Rollup、Webpack）使用。

```json
{
  "module": "dist/index.esm.js"
}
```

> ⚠️ 非标准字段，但被广泛支持。

---

### 6. `types` / `typings`

**说明**：TypeScript 类型声明文件入口。

```json
{
  "types": "dist/index.d.ts",
  "typings": "dist/index.d.ts"
}
```

- `types` 和 `typings` 功能相同，推荐用 `types`
- 如果未指定，会自动查找 `index.d.ts`

---

### 7. `exports`

**说明**：定义包的导出映射，是 `main` 的现代替代方案，支持条件导出。

```json
{
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs",
      "types": "./dist/index.d.ts"
    },
    "./package.json": "./package.json",
    "./utils": {
      "import": "./dist/utils.mjs",
      "require": "./dist/utils.cjs"
    }
  }
}
```

**条件关键字**：

| 关键字 | 说明 |
|--------|------|
| `import` | ESM 导入时使用 |
| `require` | CommonJS 导入时使用 |
| `types` | TypeScript 类型解析时使用 |
| `default` | 兜底匹配 |
| `node` | Node.js 环境 |
| `browser` | 浏览器环境 |
| `development` | 开发环境 |
| `production` | 生产环境 |

---

## 二、脚本配置（scripts）

### `scripts`

**说明**：定义可运行的 npm 脚本命令。

```json
{
  "scripts": {
    "start": "node dist/index.js",
    "build": "tsc",
    "test": "jest",
    "test:watch": "jest --watch",
    "lint": "eslint src/**/*.ts",
    "lint:fix": "eslint src/**/*.ts --fix",
    "format": "prettier --write src/**/*.ts",
    "dev": "tsx watch src/index.ts",
    "clean": "rm -rf dist",
    "prebuild": "npm run clean",
    "postbuild": "npm run test"
  }
}
```

**生命周期钩子**：

| 钩子 | 触发时机 |
|------|----------|
| `pre<script>` | 在对应脚本之前自动执行 |
| `post<script>` | 在对应脚本之后自动执行 |
| `prepare` | 在 `npm publish` 和 `npm install` 时运行 |
| `prepublishOnly` | 仅在 `npm publish` 前运行 |
| `preinstall` | 在包安装前运行 |
| `postinstall` | 在包安装后运行 |

**常用内置脚本名**：

| 脚本名 | 说明 |
|--------|------|
| `start` | `npm start` 启动应用 |
| `test` | `npm test` 运行测试 |
| `build` | 构建项目 |
| `dev` | 开发模式运行 |
| `serve` | 启动服务 |

---

## 三、依赖配置

### 1. `dependencies`

**说明**：生产环境依赖，项目运行必需。

```json
{
  "dependencies": {
    "lodash": "^4.17.21",
    "express": "~4.18.0"
  }
}
```

---

### 2. `devDependencies`

**说明**：开发环境依赖，仅在开发、测试、构建时需要，不会安装到生产环境。

```json
{
  "devDependencies": {
    "typescript": "^5.0.0",
    "jest": "^29.0.0",
    "@types/node": "^20.0.0"
  }
}
```

---

### 3. `peerDependencies`

**说明**：对等依赖，指定项目运行需要的宿主依赖版本，但不会自动安装。

```json
{
  "peerDependencies": {
    "react": ">=16.8.0",
    "react-dom": ">=16.8.0"
  }
}
```

**使用场景**：
- 插件/库需要与宿主框架版本匹配（如 React 插件）
- 避免重复安装同一依赖的不同版本

---

### 4. `peerDependenciesMeta`

**说明**：配置 `peerDependencies` 的可选性。

```json
{
  "peerDependencies": {
    "typescript": "^5.0.0"
  },
  "peerDependenciesMeta": {
    "typescript": {
      "optional": true
    }
  }
}
```

---

### 5. `optionalDependencies`

**说明**：可选依赖，安装失败不会导致整体安装失败。

```json
{
  "optionalDependencies": {
    "fsevents": "^2.3.0"
  }
}
```

**使用场景**：平台特定依赖（如 `fsevents` 仅 macOS 需要）

---

### 6. `bundledDependencies` / `bundleDependencies`

**说明**：打包依赖，发布时将这些依赖一同打包，安装时不需要从 registry 下载。

```json
{
  "bundledDependencies": [
    "my-local-package"
  ]
}
```

---

## 四、发布与文件配置

### 1. `files`

**说明**：指定发布到 npm 的文件/目录白名单。

```json
{
  "files": [
    "dist",
    "README.md",
    "LICENSE"
  ]
}
```

**默认包含**：`package.json`、`README`、`LICENSE`、`CHANGELOG`
**默认排除**：`.gitignore`、`.npmignore`、`node_modules`、`test` 等

> ⚠️ 优先级：`.npmignore` > `files` > `.gitignore`

---

### 2. `publishConfig`

**说明**：发布时的配置覆盖。

```json
{
  "publishConfig": {
    "access": "public",
    "registry": "https://registry.npmjs.org",
    "tag": "latest"
  }
}
```

| 字段 | 说明 |
|------|------|
| `access` | `public`（公开）或 `restricted`（私有） |
| `registry` | 指定发布到的 registry |
| `tag` | 发布的标签，默认 `latest` |

---

### 3. `private`

**说明**：设为 `true` 可防止意外发布到 npm。

```json
{
  "private": true
}
```

---

## 五、运行环境配置

### 1. `engines`

**说明**：指定项目运行所需的 Node.js 和 npm 版本。

```json
{
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0",
    "yarn": ">=1.22.0"
  }
}
```

> ⚠️ 默认仅警告，强制执行需配置 `.npmrc`：`engine-strict = true`

---

### 2. `os`

**说明**：指定包支持的操作系统。

```json
{
  "os": [
    "darwin",
    "linux"
  ]
}
```

**可选值**：`darwin`（macOS）、`linux`、`win32`（Windows）、`freebsd`、`openbsd`、`sunos`、`aix`

**排除**：`"!win32`

---

### 3. `cpu`

**说明**：指定包支持的 CPU 架构。

```json
{
  "cpu": [
    "x64",
    "arm64"
  ]
}
```

**可选值**：`x64`、`ia32`、`arm`、`arm64`、`mips`、`mipsel`、`ppc`、`ppc64`、`s390`、`s390x`

---

## 六、项目信息配置

### 1. `author`

**说明**：包的作者信息。

```json
{
  "author": "张三 <zhangsan@example.com> (https://zhangsan.dev)"
}
```

或对象形式：

```json
{
  "author": {
    "name": "张三",
    "email": "zhangsan@example.com",
    "url": "https://zhangsan.dev"
  }
}
```

---

### 2. `contributors`

**说明**：贡献者列表。

```json
{
  "contributors": [
    {
      "name": "李四",
      "email": "lisi@example.com"
    },
    "王五 <wangwu@example.com>"
  ]
}
```

---

### 3. `license`

**说明**：包的许可证。

```json
{
  "license": "MIT"
}
```

**常用许可证**：`MIT`、`Apache-2.0`、`ISC`、`BSD-3-Clause`、`GPL-3.0`、`UNLICENSED`

> ⚠️ `UNLICENSED` 表示不授予任何权利。

---

### 4. `repository`

**说明**：代码仓库地址。

```json
{
  "repository": {
    "type": "git",
    "url": "https://github.com/username/repo.git",
    "directory": "packages/sub-package"
  }
}
```

简写形式：

```json
{
  "repository": "github:username/repo",
  "repository": "gitlab:username/repo",
  "repository": "bitbucket:username/repo"
}
```

---

### 5. `bugs`

**说明**：Bug 反馈地址。

```json
{
  "bugs": {
    "url": "https://github.com/username/repo/issues",
    "email": "bugs@example.com"
  }
}
```

---

### 6. `homepage`

**说明**：项目主页。

```json
{
  "homepage": "https://github.com/username/repo#readme"
}
```

---

### 7. `keywords`

**说明**：关键词标签，用于 npm 搜索。

```json
{
  "keywords": [
    "typescript",
    "utility",
    "string",
    "validation"
  ]
}
```

---

## 七、包管理器配置

### 1. `packageManager`

**说明**：指定项目使用的包管理器及版本（Corepack 使用）。

```json
{
  "packageManager": "pnpm@8.15.0"
}
```

**可选值**：
- `npm@x.x.x`
- `yarn@x.x.x`
- `pnpm@x.x.x`
- `bun@x.x.x`

---

### 2. `workspaces`

**说明**：Monorepo 工作区配置。

```json
{
  "workspaces": [
    "packages/*",
    "apps/*"
  ]
}
```

带排除：

```json
{
  "workspaces": {
    "packages": ["packages/*"],
    "nohoist": ["**/react-native"]
  }
}
```

> ⚠️ Yarn 和 npm 支持此字段，pnpm 使用 `pnpm-workspace.yaml`。

---

## 八、TypeScript 相关配置

### 1. `types` / `typings`

已在前文介绍，这里补充 TypeScript 类型发布最佳实践：

```json
{
  "main": "dist/index.js",
  "module": "dist/index.mjs",
  "types": "dist/index.d.ts",
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.mts",
        "default": "./dist/index.mjs"
      },
      "require": {
        "types": "./dist/index.d.cts",
        "default": "./dist/index.cjs"
      }
    }
  }
}
```

---

### 2. `type`

**说明**：指定模块类型。

```json
{
  "type": "module"
}
```

**可选值**：
- `"commonjs"`（默认）
- `"module"`（ES Module）

> 设置为 `"module"` 后，`.js` 文件被视为 ESM，需要使用 `.cjs` 后缀表示 CommonJS。

---

## 九、其他常用配置

### 1. `sideEffects`

**说明**：标记包是否有副作用，帮助 Tree Shaking。

```json
{
  "sideEffects": false
}
```

指定有副作用的文件：

```json
{
  "sideEffects": [
    "*.css",
    "*.scss",
    "./src/polyfill.ts"
  ]
}
```

---

### 2. `browserslist`

**说明**：指定目标浏览器范围，供 Babel、Autoprefixer 等工具使用。

```json
{
  "browserslist": [
    "> 1%",
    "last 2 versions",
    "not dead",
    "not ie <= 11"
  ]
}
```

**常用查询条件**：

| 条件 | 说明 |
|------|------|
| `> 1%` | 全球使用率 > 1% 的浏览器 |
| `last 2 versions` | 每个浏览器的最新 2 个版本 |
| `not dead` | 排除过去 24 个月无官方支持的浏览器 |
| `defaults` | 默认推荐配置 |
| `supports es6-module` | 支持 ES6 模块的浏览器 |
| `maintained node versions` | 官方维护的 Node.js 版本 |

---

### 3. `man`

**说明**：手册页文件路径。

```json
{
  "man": [
    "./man/doc.1",
    "./man/doc.2"
  ]
}
```

---

### 4. `directories`

**说明**：标注目录结构（仅文档用途）。

```json
{
  "directories": {
    "lib": "./lib",
    "bin": "./bin",
    "man": "./man",
    "doc": "./docs",
    "example": "./examples",
    "test": "./test"
  }
}
```

---

### 5. `config`

**说明**：包特定的配置，可通过 `npm config` 读取。

```json
{
  "config": {
    "port": "8080"
  }
}
```

在脚本中读取：`process.env.npm_package_config_port`

---

## 完整示例

```json
{
  "name": "@my-org/my-package",
  "version": "1.0.0",
  "description": "A TypeScript utility library",
  "type": "module",
  "main": "dist/index.cjs",
  "module": "dist/index.mjs",
  "types": "dist/index.d.ts",
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.mts",
        "default": "./dist/index.mjs"
      },
      "require": {
        "types": "./dist/index.d.cts",
        "default": "./dist/index.cjs"
      }
    }
  },
  "files": [
    "dist",
    "README.md",
    "LICENSE"
  ],
  "scripts": {
    "build": "tsup",
    "dev": "tsx watch src/index.ts",
    "test": "vitest",
    "lint": "eslint src/**/*.ts",
    "format": "prettier --write src/**/*.ts",
    "prepublishOnly": "npm run build && npm run test"
  },
  "dependencies": {
    "lodash-es": "^4.17.21"
  },
  "devDependencies": {
    "typescript": "^5.4.0",
    "tsup": "^8.0.0",
    "vitest": "^1.0.0",
    "@types/node": "^20.0.0"
  },
  "peerDependencies": {
    "typescript": ">=5.0.0"
  },
  "peerDependenciesMeta": {
    "typescript": {
      "optional": true
    }
  },
  "engines": {
    "node": ">=18.0.0"
  },
  "packageManager": "pnpm@8.15.0",
  "sideEffects": false,
  "keywords": [
    "typescript",
    "utility",
    "helpers"
  ],
  "author": "张三 <zhangsan@example.com>",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/my-org/my-package.git"
  },
  "bugs": {
    "url": "https://github.com/my-org/my-package/issues"
  },
  "homepage": "https://github.com/my-org/my-package#readme"
}
```

---

## 参考文档

- [npm package.json 官方文档](https://docs.npmjs.com/cli/v10/configuring-npm/package-json)
- [Node.js modules 文档](https://nodejs.org/api/packages.html)
- [Semantic Versioning](https://semver.org/)
