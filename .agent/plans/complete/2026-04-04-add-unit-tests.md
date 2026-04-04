---
name: 添加单元测试
description: 为项目核心模块添加单元测试，提高代码质量和可维护性
type: feature
---

## 概述

为项目的核心功能模块添加单元测试，包括：
- `RSSFetcher` - RSS 源文章获取器
- `HTMLFetcher` - HTML 源文章获取器  
- `Config` - 配置加载工具
- `Logger` - 日志工具
- 其他核心工具函数

使用 Node.js 内置的 `node:test` 测试框架，无需额外依赖。

## 任务列表

### 1. 项目配置准备
- [ ] 更新 `package.json`，添加 `test` 脚本和必要的类型定义
- [ ] 创建 `src/test` 目录结构
- [ ] 创建测试数据目录 `test/data/`

### 2. 核心工具测试
- [ ] 编写 `Logger` 类的测试 (`src/test/utils/logger.test.ts`)
- [ ] 编写配置工具的测试 (`src/test/utils/config.test.ts`)
- [ ] 编写日期格式化等工具函数的测试 (`src/test/utils/date.test.ts`)

### 3. 数据类型验证
- [ ] 创建测试辅助函数 (`src/test/utils/test-utils.ts`)
- [ ] 编写类型验证和转换的测试

### 4. RSS Fetcher 测试
- [ ] 编写 `RSSFetcher` 类的测试 (`src/test/fetchers/rss-fetcher.test.ts`)
- [ ] 测试 RSS 解析逻辑（`parseRSSItem`）
- [ ] 测试 Atom 解析逻辑（`parseAtomEntry`）
- [ ] 测试分类过滤功能
- [ ] 测试最大文章数限制功能

### 5. HTML Fetcher 测试
- [ ] 编写 `HTMLFetcher` 类的测试 (`src/test/fetchers/html-fetcher.test.ts`)
- [ ] 测试浏览器实例管理
- [ ] 测试 URL 规范化逻辑
- [ ] 测试元素解析逻辑

### 6. 集成测试
- [ ] 创建简单的集成测试 (`src/test/integration.test.ts`)
- [ ] 测试模块间的协作

## 验收标准

1. 所有测试通过
2. `npm run test` 命令正常工作
3. 测试覆盖率覆盖核心功能
4. 测试代码符合项目风格
5. 不影响现有功能的正常运行

## 涉及文件路径

- `package.json` - 更新测试脚本
- `src/test/` - 新增测试文件目录
- `src/test/utils/logger.test.ts`
- `src/test/utils/config.test.ts`
- `src/test/utils/date.test.ts`
- `src/test/utils/test-utils.ts`
- `src/test/fetchers/rss-fetcher.test.ts`
- `src/test/fetchers/html-fetcher.test.ts`
- `src/test/integration.test.ts`
- `test/data/` - 测试数据目录（模拟 RSS 响应、HTML 内容等）

## 测试策略

- 使用 `node:test` 作为测试框架，无需额外安装依赖
- 使用 `sinon` 或内置的 `jest` 风格模拟功能
- 对外部 API 调用进行模拟，避免网络依赖
- 测试边界条件和错误处理
- 测试数据使用 JSON 或 YAML 格式存储在 `test/data/` 目录中
