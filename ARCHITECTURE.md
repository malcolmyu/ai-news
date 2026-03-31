# 架构说明

本文档描述本项目的高层架构。如果你想了解这个代码库，从这里开始。

## 全局概览

这是一个 TypeScript CLI 工具，从 RSS 源和网页抓取 AI 新闻，通过 LLM 对文章进行摘要，然后将静态 HTML 页面写入 `docs/`，发布到 GitHub Pages。

整个系统的核心是一条流水线：**抓取 → 摘要 → 渲染 → 发布**。所有状态保存在 `data/` 下的 JSON 文件中。`docs/` 目录是纯粹的构建产物——永远不要手动编辑它。

## 代码地图

### `src/main.ts`

CLI 入口，基于 `commander` 构建。所有子命令（`daily`、`research`、`thinking`、`homepage`、`all` 等）都在这里定义。它本身不做任何事情，把所有工作委托给 `TeamCoordinator`。

### `src/team/coordinator.ts`

`TeamCoordinator` 是编排器。它持有所有 agent 并将它们串联起来。所有 CLI 动作最终都会调用这个类上的某个方法。这里没有任何业务逻辑——它只负责按顺序调用 agent 并返回结果。

`planAndExecute()` 运行完整的三段式工作流，供自动化任务使用。`executeDaily()`、`executeResearch()` 等是大多数交互式命令使用的单 agent 快捷路径。

### `src/agents/`

四个内容生成 agent，每个独立放在自己的目录中：

- **`daily-reporter/`** — 从 RSS 和 HTML 源抓取文章，调用 OpenRouter 进行摘要，生成 `docs/daily/ai-news-YYYY-MM-DD.html`。`fetchers/` 子目录包含两个抓取器实现（`rss-fetcher`、`html-fetcher`）。`summarizer.ts` 负责 OpenRouter 调用。`generator.ts` 负责所有 HTML 渲染。

- **`research-manager/`** — 管理一个手工整理的调研报告库。源 HTML 文件存放在 `data/research/`。该 agent 将文件复制到 `docs/research/`，并维护 `data/research/index.json`。

- **`thinking-system/`** — 管理思维模型页面库（决策框架、方法论等）。源数据存放在 `data/thinking/models.json`。该 agent 按分类生成 HTML 页面到 `docs/thinking/`。

- **`homepage-builder/`** — 汇聚所有其他 agent 的内容（日报归档、调研列表、思维模型分类），渲染 `docs/index.html`。

此外还有两个用于自动化工作流的元 agent：

- **`planner/`** — 接收任务类型，生成 `TaskPlan`（一个按依赖顺序排列的子任务列表及 harness 检查点）。不触碰文件系统。

- **`evaluator/`** — 接收草稿文件路径和 harness 类型，加载对应的 `harness/*/SKILL.md` 规则，返回 `ValidationResult`。草稿通过后，将文件从 `docs/drafts/` 移动到最终的 `docs/` 目标路径。

### `src/types/index.ts`

所有共享的 TypeScript 接口，是数据结构的唯一来源。关键类型：

- `Article`、`SummarizedArticle`、`DailyReport` — 日报流水线
- `ResearchMetadata`、`ThinkingModel` — 内容库
- `TaskPlan`、`SubTask`、`ValidationResult`、`ValidationError` — planner/evaluator 工作流
- `AgentResult` — 每个 agent 方法的统一返回类型

### `src/shared-styles.ts`

所有生成器共用的 HTML 工具函数：`htmlDoc()`、`siteHeader()`、`siteFooter()` 和 `SHARED_CSS`。站点上的每一个页面都由这些原语拼装而成。

### `src/utils/config.ts`

工具模块，提供日志（`Logger`）、配置加载（`loadConfig`）、日期格式化（`formatDate`）以及文件系统帮助函数（`readJSONFile`、`writeJSONFile`）。

### `config/sources.yaml`

声明所有待抓取的 RSS 和 HTML 源。每条记录包含类型、URL、分类，以及 HTML 抓取用的可选 CSS 选择器。添加或删除新闻源时，只需编辑这个文件。

### `data/`

持久化状态。所有 JSON 文件是系统的事实来源，提交到 git。

- `data/daily/archives.json` — 所有已生成日报的索引
- `data/research/index.json` — 所有调研报告的索引
- `data/thinking/models.json` — 所有思维模型的索引
- `data/thinking/relationships/` — 每个模型的关系图
- `data/thinking/versions/` — 每个模型的版本历史
- `data/homepage/feed.json` — 首页渲染用的汇聚数据快照

### `docs/`

GitHub Pages 的输出目录，完全由构建流水线生成。永远不要手动编辑。已提交到 git，这样 Pages 无需 CI 步骤即可直接提供最新构建。

### `harness/content-harness/SKILL.md`

日报输出的质量规则。`EvaluatorAgent` 在运行时读取这个文件，在批准草稿前对每一条规则逐一检查。这是 writer 和 evaluator 之间的契约。

## 数据流

```
config/sources.yaml
       │
       ▼
 daily-reporter  ──→  OpenRouter API
       │
       ▼
 docs/drafts/          （或在快捷路径下直接写入 docs/daily/）
       │
  EvaluatorAgent
  （harness 检查）
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

**`generator.ts` 负责 HTML，`index.ts` 负责逻辑。** 每个生成 HTML 的 agent 都有 `generator.ts`（纯渲染，接受数据，返回 HTML 字符串）和 `index.ts`（抓取、处理、调用生成器、写文件）两个文件。业务逻辑不属于生成器。

**类型层中没有 IO。** `src/types/index.ts` 零 import，不产生任何副作用，它只用来定义数据结构。

**`shared-styles.ts` 是唯一的共享 UI 代码。** agent 不能复制粘贴 HTML 样板代码。如果两个 agent 需要相同的 HTML 结构，它应该放在 `shared-styles.ts` 中。

## 横切关注点

### 外部 API 调用

所有 LLM 调用都通过 `daily-reporter` 中的 `summarizer.ts` 发出。API Key 从 `.env`（`OPENROUTER_API_KEY`）中读取。Key 缺失时，系统跳过摘要步骤继续运行。其他 agent 不发起任何外部 API 调用。

### 文件命名约定

- 日报：`docs/daily/ai-news-YYYY-MM-DD.html`
- 最新日报（软链接目标）：`docs/daily/ai-daily-latest.html`
- 调研报告：`docs/research/<slug>.html`
- 思维模型页面：`docs/thinking/<category-slug>.html`

### 配置加载

`src/utils/config.ts` 中的 `loadConfig()` 读取 `config/sources.yaml` 并与环境变量合并。所有 agent 通过 `TeamCoordinator` 接收配置，而不是自己读取文件。

### Git 发布

`all --push` 命令运行所有 agent，然后执行 `git add . && git commit && git push`。发布模式是：本地运行，提交 `docs/`，推送。GitHub Pages 直接从 `main` 分支的 `docs/` 目录提供服务。
