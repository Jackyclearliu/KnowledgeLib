# TypeScript 类型系统详解

> 本文档系统整理 TypeScript 的所有类型，包含类型名称、说明、用法示例及注意事项。
> 基于 TypeScript 5.x 版本整理。

---

## 目录

- [基础类型](#基础类型)
- [对象类型](#对象类型)
- [数组与元组](#数组与元组)
- [联合类型与交叉类型](#联合类型与交叉类型)
- [类型别名](#类型别名)
- [接口（Interface）](#接口interface)
- [类型断言](#类型断言)
- [字面量类型](#字面量类型)
- [枚举类型](#枚举类型)
- [泛型](#泛型)
- [条件类型](#条件类型)
- [映射类型](#映射类型)
- [模板字面量类型](#模板字面量类型)
- [内置工具类型](#内置工具类型)
- [类型推断与类型保护](#类型推断与类型保护)
- [其他重要类型](#其他重要类型)

---

## 基础类型

TypeScript 在 JavaScript 原有类型基础上增加了静态类型检查。

| 类型 | 说明 | 示例 |
|------|------|------|
| `boolean` | 布尔值 | `let flag: boolean = true;` |
| `number` | 数字（整数、浮点数、NaN、Infinity） | `let age: number = 25;` |
| `string` | 字符串 | `let name: string = "Alice";` |
| `bigint` | 任意精度的整数（ES2020+） | `let big: bigint = 100n;` |
| `symbol` | 唯一的、不可变的值 | `let sym: symbol = Symbol("key");` |
| `null` | 空值 | `let n: null = null;` |
| `undefined` | 未定义 | `let u: undefined = undefined;` |
| `object` | 非原始类型的值 | `let obj: object = {};` |
| `any` | 任意类型（关闭类型检查） | `let anything: any = 4;` |
| `unknown` | 未知类型（类型安全的 any） | `let notSure: unknown = 4;` |
| `never` | 永不存在的值的类型 | `function error(): never { throw new Error(); }` |
| `void` | 无返回值（通常用于函数） | `function log(): void { console.log("hi"); }` |

### 注意事项

- **`any`**: 尽可能避免使用，会失去类型检查的保护。
- **`unknown`**: 比 `any` 更安全，使用前必须进行类型检查或断言。
- **`never`**: 表示永远不会到达的终点，如抛出异常的函数、无限循环等。
- **`void`**: 与 `undefined` 不同，`void` 表示函数没有返回值（或返回 `undefined`），不能赋值给其他变量。

```typescript
// any vs unknown
let a: any = "hello";
a.toFixed(); // 编译通过，运行时可能报错

let b: unknown = "hello";
// b.toFixed(); // 编译报错！需要类型检查
if (typeof b === "string") {
  b.toUpperCase(); // OK
}
```

---

## 对象类型

### 对象字面量类型

```typescript
let person: { name: string; age: number } = {
  name: "Alice",
  age: 25,
};
```

### 可选属性

```typescript
let user: { name: string; age?: number } = {
  name: "Bob",
  // age 可以省略
};
```

### 只读属性

```typescript
let config: { readonly apiKey: string } = {
  apiKey: "secret-123",
};
// config.apiKey = "new"; // 编译报错！
```

### 索引签名

用于描述具有动态属性的对象：

```typescript
// 字符串索引
let dict: { [key: string]: number } = {
  apple: 1,
  banana: 2,
};

// 数字索引
let arrLike: { [index: number]: string } = ["a", "b", "c"];

// 混合索引签名
interface Mixed {
  [key: string]: string | number;
  name: string; // 必须兼容索引签名类型
  age: number;
}
```

### 方法签名

```typescript
interface Calculator {
  add(a: number, b: number): number;
  subtract: (a: number, b: number) => number; // 两种写法等价
}
```

---

## 数组与元组

### 数组类型

```typescript
// 两种写法等价
let nums: number[] = [1, 2, 3];
let strs: Array<string> = ["a", "b", "c"];

// 多维数组
let matrix: number[][] = [[1, 2], [3, 4]];
```

### 只读数组

```typescript
let readonlyArr: readonly number[] = [1, 2, 3];
// readonlyArr.push(4); // 编译报错！

// 等价写法
let roArray: ReadonlyArray<number> = [1, 2, 3];
```

### 元组（Tuple）

固定长度、固定类型的数组：

```typescript
// 基础元组
let point: [number, number] = [10, 20];

// 可选元素
let person: [string, number?] = ["Alice"];

// 剩余元素
let list: [string, ...number[]] = ["scores", 90, 85, 88];

// 只读元组
let readonlyTuple: readonly [string, number] = ["Alice", 25];
```

### 命名元组（Labeled Tuple Elements）

```typescript
let point: [x: number, y: number] = [10, 20];
// 增强了可读性，但类型检查行为不变
```

---

## 联合类型与交叉类型

### 联合类型（Union Types）

表示值可以是多种类型之一：

```typescript
let value: string | number = "hello";
value = 42; // OK

// 用于函数参数
function padLeft(value: string, padding: string | number) {
  if (typeof padding === "number") {
    return Array(padding + 1).join(" ") + value;
  }
  return padding + value;
}
```

### 交叉类型（Intersection Types）

将多个类型合并为一个：

```typescript
interface Colorful {
  color: string;
}
interface Circle {
  radius: number;
}

type ColorfulCircle = Colorful & Circle;

let cc: ColorfulCircle = {
  color: "red",
  radius: 42,
};
```

---

## 类型别名

使用 `type` 关键字为类型创建新名字：

```typescript
// 基础类型别名
type Point = {
  x: number;
  y: number;
};

// 联合类型别名
type ID = string | number;

// 交叉类型别名
type Employee = Person & { employeeId: number };

// 泛型类型别名
type Container<T> = { value: T };

// 递归类型别名
type TreeNode<T> = {
  value: T;
  children?: TreeNode<T>[];
};
```

### `type` vs `interface`

| 特性 | `type` | `interface` |
|------|--------|-------------|
| 扩展方式 | 使用交叉类型 `&` | 使用 `extends` |
| 同名合并 | ❌ 不可重复定义 | ✅ 自动声明合并 |
| 联合/交叉 | ✅ 可直接定义 | ❌ 不行 |
| 实现类 | ❌ 不能被 `implements` | ✅ 可以 |
| 映射类型 | ✅ 支持 | ❌ 不支持 |

```typescript
// interface 声明合并
interface Animal { name: string; }
interface Animal { age: number; }
// 最终 Animal = { name: string; age: number; }

// type 不行
type Animal2 = { name: string; };
// type Animal2 = { age: number; }; // 编译报错！
```

---

## 接口（Interface）

接口是定义对象结构的另一种方式，支持扩展和实现。

```typescript
interface Person {
  name: string;
  age: number;
  greet(): void;
}

// 可选属性
interface Config {
  host: string;
  port?: number;
}

// 只读属性
interface Point {
  readonly x: number;
  readonly y: number;
}

// 扩展接口
interface Animal {
  name: string;
}
interface Dog extends Animal {
  breed: string;
}

// 类实现接口
class Cat implements Animal {
  name = "Kitty";
}

// 接口继承多个接口
interface Employee extends Person, Identifiable {}
```

---

## 类型断言

告诉编译器"我知道这个值的类型"：

```typescript
let someValue: unknown = "this is a string";

// 尖括号语法（在 JSX 中不可用）
let strLength1: number = (<string>someValue).length;

// as 语法（推荐）
let strLength2: number = (someValue as string).length;

// 双重断言（谨慎使用）
let forced = someValue as unknown as number;

// 非空断言（!）
function getString(maybe: string | null) {
  return maybe!.toUpperCase(); // 告诉编译器这里一定不是 null
}

// const 断言（as const）
let arr = [1, 2, 3] as const; // 类型变为 readonly [1, 2, 3]
let obj = { x: 10, y: 20 } as const; // 所有属性变为 readonly 字面量类型
```

---

## 字面量类型

将值本身作为类型：

```typescript
// 字符串字面量
type EventName = "click" | "dblclick" | "mouseup";
let event: EventName = "click";
// event = "keydown"; // 编译报错！

// 数字字面量
type OneToFive = 1 | 2 | 3 | 4 | 5;

// 布尔字面量
type Bool = true | false; // 等价于 boolean

// 结合使用
interface Options {
  alignment: "left" | "right" | "center";
  padding: 0 | 2 | 4 | 8 | 16;
}

// 对象字面量的 const 断言
let config = {
  host: "localhost",
  port: 3000,
} as const;
// config.host 的类型是字面量 "localhost"，不是 string
```

---

## 枚举类型

### 数字枚举

```typescript
enum Direction {
  Up,      // 0
  Down,    // 1
  Left,    // 2
  Right,   // 3
}

enum Status {
  Pending = 1,
  Approved,  // 2
  Rejected,  // 3
}
```

### 字符串枚举

```typescript
enum Color {
  Red = "RED",
  Green = "GREEN",
  Blue = "BLUE",
}
```

### 异构枚举（不推荐）

```typescript
enum Mixed {
  No = 0,
  Yes = "YES",
}
```

### const 枚举

编译时内联，不生成对象：

```typescript
const enum Direction {
  Up,
  Down,
}
// 编译后直接使用 0 和 1
```

### 环境枚举（declare enum）

```typescript
declare enum ExternalAPI {
  Read,
  Write,
}
// 用于描述已存在的外部枚举，不生成运行时代码
```

### 注意事项

- 枚举会生成运行时对象和反向映射（字符串枚举除外）。
- 现代 TypeScript 项目更推荐使用**联合类型**替代枚举：

```typescript
// 推荐：使用联合类型替代枚举
type Direction = "Up" | "Down" | "Left" | "Right";
```

---

## 泛型

泛型允许定义可重用的组件，支持多种类型。

### 基础泛型

```typescript
function identity<T>(arg: T): T {
  return arg;
}

let output = identity<string>("myString");
let output2 = identity("myString"); // 类型推断
```

### 泛型约束

```typescript
interface HasLength {
  length: number;
}

function logLength<T extends HasLength>(arg: T): T {
  console.log(arg.length);
  return arg;
}

// 约束为特定键
type KeyOf<T, K extends keyof T> = T[K];
```

### 多个泛型参数

```typescript
function pair<T, U>(first: T, second: U): [T, U] {
  return [first, second];
}
```

### 泛型默认值

```typescript
interface Container<T = string> {
  value: T;
}

let c: Container = { value: "hello" }; // T 默认为 string
```

### 泛型接口

```typescript
interface GenericIdentityFn<T> {
  (arg: T): T;
}

let myIdentity: GenericIdentityFn<number> = (x) => x;
```

### 泛型类

```typescript
class GenericNumber<T> {
  zeroValue: T;
  add: (x: T, y: T) => T;
}

let myGenericNumber = new GenericNumber<number>();
myGenericNumber.zeroValue = 0;
myGenericNumber.add = (x, y) => x + y;
```

### 泛型条件约束

```typescript
// 泛型参数必须有特定属性
type WithName<T extends { name: string }> = T;

// 使用
type NamedPerson = WithName<{ name: string; age: number }>; // OK
// type Bad = WithName<{ age: number }>; // 编译报错！
```

### `infer` 关键字

在条件类型中推断类型：

```typescript
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

type Num = ReturnType<() => number>; // number
type Str = ReturnType<(x: string) => string>; // string
```

---

## 条件类型

根据类型关系选择类型：

```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<"hello">; // true
type B = IsString<123>;     // false
```

### 分布式条件类型

当条件类型作用于联合类型时，会**分发**到每个成员：

```typescript
type ToArray<T> = T extends any ? T[] : never;

type StrOrNumArray = ToArray<string | number>;
// 结果是 string[] | number[]，不是 (string | number)[]

// 禁用分布式行为

type ToArrayNonDist<T> = [T] extends [any] ? T[] : never;
type Result = ToArrayNonDist<string | number>; // (string | number)[]
```

### 内置条件类型

| 类型 | 说明 |
|------|------|
| `Exclude<T, U>` | 从 T 中排除可以赋值给 U 的类型 |
| `Extract<T, U>` | 从 T 中提取可以赋值给 U 的类型 |
| `NonNullable<T>` | 从 T 中排除 null 和 undefined |
| `Parameters<T>` | 获取函数参数类型组成的元组 |
| `ReturnType<T>` | 获取函数返回值类型 |
| `InstanceType<T>` | 获取构造函数实例类型 |
| `ThisParameterType<T>` | 获取 this 参数类型 |
| `OmitThisParameter<T>` | 移除 this 参数 |
| `ThisType<T>` | 指定 this 的类型（用于对象字面量） |

---

## 映射类型

基于旧类型创建新类型：

```typescript
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

type Partial<T> = {
  [P in keyof T]?: T[P];
};

type Required<T> = {
  [P in keyof T]-?: T[P]; // -? 移除可选性
};
```

### 键重映射（Key Remapping）

TypeScript 4.1+ 支持：

```typescript
// 使用 as 重映射键
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

interface Person {
  name: string;
  age: number;
}

type PersonGetters = Getters<Person>;
// {
//   getName: () => string;
//   getAge: () => number;
// }
```

### 过滤键

```typescript
type RemoveKindField<T> = {
  [K in keyof T as Exclude<K, "kind">]: T[K];
};

interface Circle {
  kind: "circle";
  radius: number;
}

type KindlessCircle = RemoveKindField<Circle>;
// { radius: number }
```

---

## 模板字面量类型

TypeScript 4.1+ 引入，基于字符串字面量构建类型：

```typescript
type World = "world";
type Greeting = `hello ${World}`; // "hello world"

// 联合类型的组合
type Color = "red" | "blue";
type Size = "small" | "large";
type Style = `${Color}-${Size}`;
// "red-small" | "red-large" | "blue-small" | "blue-large"

// 内置字符串操作类型
type Upper = Uppercase<"hello">;    // "HELLO"
type Lower = Lowercase<"HELLO">;    // "hello"
type Capital = Capitalize<"hello">;  // "Hello"
type Uncapital = Uncapitalize<"Hello">; // "hello"
```

---

## 内置工具类型

### 属性修饰

| 类型 | 说明 | 结果 |
|------|------|------|
| `Partial<T>` | 所有属性变为可选 | `{ a?: string; b?: number; }` |
| `Required<T>` | 所有属性变为必填 | `{ a: string; b: number; }` |
| `Readonly<T>` | 所有属性变为只读 | `{ readonly a: string; }` |
| `Mutable<T>` | 所有属性变为可变（自定义） | `{ a: string; }` |

### 属性选择/排除

| 类型 | 说明 |
|------|------|
| `Pick<T, K>` | 从 T 中选择 K 键 |
| `Omit<T, K>` | 从 T 中排除 K 键 |
| `Record<K, T>` | 创建键为 K、值为 T 的对象类型 |

```typescript
interface User {
  id: number;
  name: string;
  email: string;
}

type UserPreview = Pick<User, "id" | "name">;
// { id: number; name: string; }

type UserWithoutEmail = Omit<User, "email">;
// { id: number; name: string; }

type PageInfo = Record<string, { title: string }>;
// { [key: string]: { title: string; } }
```

### 类型操作

| 类型 | 说明 |
|------|------|
| `Exclude<T, U>` | T 中排除 U |
| `Extract<T, U>` | T 中提取 U |
| `NonNullable<T>` | 排除 null/undefined |
| `Parameters<T>` | 函数参数元组 |
| `ConstructorParameters<T>` | 构造函数参数元组 |
| `ReturnType<T>` | 函数返回类型 |
| `InstanceType<T>` | 类实例类型 |
| `Awaited<T>` | Promise 解析后的类型 |

```typescript
type T0 = Exclude<"a" | "b" | "c", "a">;           // "b" | "c"
type T1 = Extract<"a" | "b" | "c", "a" | "f">;     // "a"
type T2 = NonNullable<string | number | undefined>;  // string | number

type T3 = Parameters<(a: string, b: number) => void>; // [a: string, b: number]
type T4 = ReturnType<() => string>;                   // string

type T5 = Awaited<Promise<Promise<number>>>;          // number
```

### 深度工具类型（自定义）

TypeScript 没有内置深度版本，通常需要自定义：

```typescript
// 深度 Partial
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// 深度 Readonly
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

// 深度 Required
type DeepRequired<T> = {
  [P in keyof T]-?: T[P] extends object ? DeepRequired<T[P]> : T[P];
};
```

---

## 类型推断与类型保护

### 类型推断

TypeScript 自动推断类型：

```typescript
let x = 3;           // 推断为 number
let arr = [1, "a"];  // 推断为 (string | number)[]

// 上下文类型推断
window.onmousedown = (event) => {
  // event 自动推断为 MouseEvent
  console.log(event.button);
};
```

### 类型保护（Type Guards）

```typescript
// typeof 类型保护
function padLeft(value: string, padding: string | number) {
  if (typeof padding === "number") {
    return Array(padding + 1).join(" ") + value;
  }
  // padding 在此处推断为 string
  return padding + value;
}

// instanceof 类型保护
class Bird {
  fly() {}
}
class Fish {
  swim() {}
}

function move(pet: Bird | Fish) {
  if (pet instanceof Bird) {
    pet.fly();
  } else {
    pet.swim();
  }
}

// in 操作符类型保护
interface Admin {
  role: "admin";
  permissions: string[];
}
interface User {
  role: "user";
}

function checkAccess(person: Admin | User) {
  if ("permissions" in person) {
    // person 推断为 Admin
    console.log(person.permissions);
  }
}

// 自定义类型保护函数
function isString(x: unknown): x is string {
  return typeof x === "string";
}

function example(x: unknown) {
  if (isString(x)) {
    x.toUpperCase(); // x 在此处为 string
  }
}

// 判别联合（Discriminated Unions）
interface Circle {
  kind: "circle";
  radius: number;
}
interface Square {
  kind: "square";
  sideLength: number;
}
type Shape = Circle | Square;

function getArea(shape: Shape) {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "square":
      return shape.sideLength ** 2;
  }
}
```

### 断言函数（Assertion Functions）

```typescript
function assertIsString(val: unknown): asserts val is string {
  if (typeof val !== "string") {
    throw new Error("Not a string!");
  }
}

function assertNonNull<T>(val: T): asserts val is NonNullable<T> {
  if (val === null || val === undefined) {
    throw new Error("Value is null or undefined!");
  }
}

function example(x: string | null) {
  assertNonNull(x);
  x.toUpperCase(); // x 在此处为 string
}
```

---

## 其他重要类型

### 类相关类型

```typescript
class Animal {
  name: string = "";
  private age: number = 0;
  protected sound: string = "";
}

// 实例类型
type AnimalInstance = InstanceType<typeof Animal>;

// 类类型（构造函数签名）
type AnimalConstructor = new () => Animal;
```

### `this` 类型

```typescript
class Builder {
  private value: string = "";

  add(str: string): this {
    this.value += str;
    return this;
  }

  build(): string {
    return this.value;
  }
}

class AdvancedBuilder extends Builder {
  exclaim(): this {
    return this.add("!");
  }
}
```

### 索引访问类型

```typescript
interface Person {
  name: string;
  age: number;
}

type NameType = Person["name"]; // string
type PersonKeys = keyof Person;  // "name" | "age"
type PersonValues = Person[keyof Person]; // string | number
```

### 可辨识联合模式

```typescript
interface LoadingState {
  status: "loading";
}
interface SuccessState {
  status: "success";
  data: string;
}
interface ErrorState {
  status: "error";
  error: Error;
}

type State = LoadingState | SuccessState | ErrorState;

function handleState(state: State) {
  switch (state.status) {
    case "loading":
      return "Loading...";
    case "success":
      return state.data;
    case "error":
      return state.error.message;
  }
}
```

### 严格模式相关类型行为

开启 `strictNullChecks` 后：

```typescript
let str: string = "hello";
// str = null; // 编译报错！

let maybeStr: string | null = null; // 必须显式声明 null
```

---

## 类型声明文件（.d.ts）

为没有类型的 JavaScript 库提供类型声明：

```typescript
// my-lib.d.ts
declare module "my-lib" {
  export function doSomething(): void;
  export const version: string;
}

// 全局变量声明
declare const MY_GLOBAL: string;

// 全局函数声明
declare function myGlobalFunction(): void;

// 命名空间声明
declare namespace MyNamespace {
  interface Config {
    timeout: number;
  }
}
```

---

## 类型兼容性

TypeScript 使用**结构化类型**系统（而非名义类型）：

```typescript
interface Point2D {
  x: number;
  y: number;
}

interface Point3D {
  x: number;
  y: number;
  z: number;
}

let p2d: Point2D = { x: 0, y: 0 };
let p3d: Point3D = { x: 0, y: 0, z: 0 };

p2d = p3d; // OK! Point3D 结构兼容 Point2D
// p3d = p2d; // 编译报错！缺少 z 属性
```

### 函数参数的双向协变（Bivariance）

```typescript
enum EventType {
  Mouse,
  Keyboard,
}

interface Event {
  timestamp: number;
}

interface MouseEvent extends Event {
  x: number;
  y: number;
}

function listenEvent(eventType: EventType, handler: (n: Event) => void) {
  /* ... */
}

// 不安全但允许（严格模式下关闭 --strictFunctionTypes 时）
listenEvent(EventType.Mouse, (e: MouseEvent) => console.log(e.x));
```

---

## 参考链接

- [TypeScript 官方文档 - 基础类型](https://www.typescriptlang.org/docs/handbook/basic-types.html)
- [TypeScript 官方文档 - 高级类型](https://www.typescriptlang.org/docs/handbook/advanced-types.html)
- [TypeScript 官方文档 - 泛型](https://www.typescriptlang.org/docs/handbook/generics.html)
- [TypeScript 官方文档 - 工具类型](https://www.typescriptlang.org/docs/handbook/utility-types.html)
- [TypeScript 官方文档 - 模板字面量类型](https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html)

---

> 📅 文档整理日期：2026-05-16
