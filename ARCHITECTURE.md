# 架构说明

本文档描述本项目的高层架构。如果你想了解这个代码库，从这里开始。

## 全局概览

这是一个 TypeScript CLI 工具，从 RSS 源和网页抓取 AI 新闻，通过 LLM 对文章进行摘要，然后将静态 HTML 页面写入 `docs/`，发布到 GitHub Pages。

整个系统的核心是一条流水线：**抓取 → 摘要 → 渲染 → 发布**。所有状态保存在 `data/` 下的 JSON 文件中。`docs/` 目录是纯粹的构建产物——永远不要手动编辑它。

## 代码地图

### `src/main.ts`

CLI 入口，基于 `commander` 构建。所有子命令（`daily`、`research`、`thinking`、`homepage`、`all` 等）都在这里定义，直接实例化对应 agent 并调用——没有额外的协调层。

### `src/agents/`

四个内容生成 agent，每个独立放在自己的目录中：

- **`daily-reporter/`** — 从 RSS 和 HTML 源抓取文章，调用 OpenRouter 进行摘要，生成 `docs/daily/ai-news-YYYY-MM-DD.html`。
  - `fetchers/rss-fetcher.ts` — RSS/Atom feed 抓取器
  - `fetchers/html-fetcher.ts` — Playwright headless 浏览器抓取器（用于 SPA 页面）
  - `summarizer.ts` — OpenRouter LLM 摘要调用
  - `generator.ts` — 调用 `src/renderer/` 渲染 HTML
  - `DailyReportPage.tsx` — SolidJS 日报页面组件
  - `DailyArchivePage.tsx` — SolidJS 日报归档页面组件

- **`research-manager/`** — 管理手工整理的调研报告库。源 HTML 文件存放在 `data/research/`，该 agent 将文件复制到 `docs/research/` 并维护归档索引。

- **`thinking-system/`** — 管理思维模型页面库。源数据存放在 `data/thinking/models.json`，该 agent 按分类生成 HTML 页面到 `docs/thinking/`。

- **`homepage-builder/`** — 汇聚所有其他 agent 的内容（日报归档、调研列表、思维模型分类），渲染 `docs/index.html`。

### `src/renderer/`

共享渲染层，提供统一的 SolidJS `renderToString` 输出。所有 HTML 生成都通过这里，而非各自维护模板字符串。

- `index.ts` — 导出 `renderPage(component, title, extraHead?)` 函数，封装 `renderToString` 调用
- `components/Layout.tsx` — 页面骨架（`<html>`、`<head>`、`<body>`、CSS 变量）
- `components/SiteHeader.tsx` — 全局顶部导航
- `components/SiteFooter.tsx` — 全局底部
- `styles/shared.css.ts` — 共享 CSS 变量、组件样式（以 TS 字符串导出，注入 `<style>` 标签）

### `src/types/index.ts`

所有共享的 TypeScript 接口，是数据结构的唯一来源。关键类型：

- `Article`、`SummarizedArticle`、`DailyReport` — 日报流水线
- `ResearchMetadata`、`ThinkingModel` — 内容库
- `AgentResult` — 每个 agent 方法的统一返回类型

### `src/utils/config.ts`

工具模块，提供日志（`Logger`）、配置加载（`loadConfig`）、日期格式化（`formatDate`）以及文件系统帮助函数（`readJSONFile`、`writeJSONFile`）。

### `config/sources.yaml`

声明所有待抓取的 RSS 和 HTML 源。每条记录包含类型、URL、分类，以及 HTML 抓取用的可选 CSS 选择器（`selector`、`title_selector`、`link_selector`）。添加或删除新闻源时，只需编辑这个文件。

### `data/`

持久化状态。所有 JSON 文件是系统的事实来源，提交到 git。

- `data/daily/archives.json` — 所有已生成日报的索引
- `data/research/index.json` — 所有调研报告的索引
- `data/thinking/models.json` — 所有思维模型的索引

### `docs/`

GitHub Pages 的输出目录，完全由构建流水线生成。永远不要手动编辑。已提交到 git，这样 Pages 无需 CI 步骤即可直接提供最新构建。

## Harness 基础设施

位于 `.agent/` 目录，是 agent 会话的控制层：

| 文件 | 用途 |
|------|------|
| `.agent/init.sh` | 环境验证入口：Node 版本 + build + Playwright 健康检查 |
| `.agent/feature_list.json` | 各 pipeline 的健康状态（唯一事实来源） |
| `.agent/claude-progress.md` | 跨会话进度日志 |
| `.agent/clean-state-checklist.md` | 会话结束前的自检清单 |
| `.agent/evaluator/daily-report-harness.md` | 日报生成的质量门禁（来源配额、摘要规范、HTML 结构等） |
| `.agent/plans/active/` | 当前进行中的计划文件 |
| `.agent/plans/complete/` | 已完成的计划归档 |

## 数据流

```
config/sources.yaml
       │
       ▼
 rss-fetcher + html-fetcher (Playwright headless)
       │
       ▼
 daily-reporter/index.ts  ──→  OpenRouter API (LLM 摘要)
       │
       ▼
 src/renderer/renderPage()
 (SolidJS renderToString)
       │
       ▼
 docs/daily/ai-news-YYYY-MM-DD.html
       │
 homepage-builder
       │
       ▼
 docs/index.html
```

## 架构不变式

**`docs/` 是构建产物。** 流水线中没有任何环节从 `docs/` 读取数据，它只被写入。读取自己的输出是一个 bug。

**每个 agent 只拥有自己的数据目录。** `daily-reporter` 拥有 `data/daily/`，`research-manager` 拥有 `data/research/`，agent 之间不互相读取数据目录。`HomepageBuilder` 是唯一例外——它读取所有数据文件来构建汇聚视图，但不写入它们。

**`src/types/index.ts` 是定义共享类型的唯一地方。** agent 文件内不允许内联定义接口，不允许重复定义类型。

**`generator.ts` 负责 HTML，`index.ts` 负责逻辑。** 每个生成 HTML 的 agent 都有 `generator.ts`（纯渲染，调用 `renderPage()`，返回文件路径）和 `index.ts`（抓取、处理、调用生成器、写文件）两个文件。业务逻辑不属于生成器。

**`src/renderer/` 是唯一的共享 UI 代码。** agent 不能复制粘贴 HTML 样板代码。共享 CSS、布局、页头页脚全部在 `src/renderer/` 中。

**类型层中没有 IO。** `src/types/index.ts` 零 import，不产生任何副作用，它只用来定义数据结构。

## 横切关注点

### 外部 API 调用

所有 LLM 调用都通过 `daily-reporter` 中的 `summarizer.ts` 发出。API Key 从 `.env`（`OPENROUTER_API_KEY`）中读取。Key 缺失时，系统跳过摘要步骤继续运行。其他 agent 不发起任何外部 API 调用。

### HTML 渲染方式

所有 HTML 输出通过 SolidJS `renderToString` 渲染，不使用模板字符串。每个 agent 有对应的 `*.tsx` 页面组件（如 `DailyReportPage.tsx`），通过 `src/renderer/renderPage()` 注入到完整页面骨架中。

### Playwright HTML 抓取

`html-fetcher.ts` 使用 Playwright headless Chromium 抓取 SPA 页面。共享一个 `Browser` 实例（`getBrowser()`），每次 `fetchFromSource()` 新建 `Page`，用完即关（`page.close()` 在 `finally` 中）。`DailyReporter` 在所有 HTML 源抓取完毕后调用 `htmlFetcher.close()` 关闭浏览器（同样在 `finally` 中）。

### 配置加载

`src/utils/config.ts` 中的 `loadConfig()` 读取 `config/sources.yaml` 并与环境变量合并。各 agent 在构造函数中直接调用 `loadConfig()`，无需协调层传入。

### 文件命名约定

- 日报：`docs/daily/ai-news-YYYY-MM-DD.html`
- 最新日报：`docs/daily/ai-daily-latest.html`
- 调研报告：`docs/research/<slug>.html`
- 思维模型页面：`docs/thinking/<category-slug>.html`

### Git 发布

`all --push` 命令运行所有 agent，然后执行 `git add . && git commit && git push`。发布模式是：本地运行，提交 `docs/`，推送。GitHub Pages 直接从 `main` 分支的 `docs/` 目录提供服务。
