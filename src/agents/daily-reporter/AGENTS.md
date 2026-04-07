# AGENTS.md — Daily Reporter

在对本目录下任何文件做修改，或者生成 `docs/daily/` 下的任何产物之前，**必须先完整阅读**：

```
harness/content-harness/SKILL.md
```

该文件包含以下强制约束，违反任意一条须原地重写：

- 单个来源 ≤ 3 条文章（按 summaryQuality 裁剪）
- 日报总条数 5 — 20 条
- 摘要字符 50 — 400，禁用推测词，须覆盖核心事件 / 关键洞察 / 实际影响三个维度
- 分类名称必须在白名单内，单报分类数 ≤ 6
- HTML 产物使用规定 class 结构，含响应式和暗色模式，禁止硬编码颜色
- 文件输出路径：`docs/daily/ai-news-YYYY-MM-DD.html`

## 本模块职责

| 文件 | 职责 |
|------|------|
| `index.ts` | `DailyReporter` agent 类：抓取、摘要、归档、触发主页重建 |
| `generator.ts` | `DailyReportGenerator`：将 `DailyReport` 数据渲染为 HTML |
| `summarizer.ts` | 调用 OpenAI 兼容 API 批量摘要（`ANTHROPIC_*` 火山方舟优先） |
| `check-sources.ts` | 验证配置中各 RSS/HTML 来源的可用性 |
| `fetchers/rss-fetcher.ts` | 抓取 RSS 源 |
| `fetchers/html-fetcher.ts` | 抓取 HTML 页面并解析文章列表；支持 `date_selector` / `resolve_missing_article_date` |
| `daily-checker.ts` | 单次运行汇总 + 按源写入 `src-<slug>.json`（**v2** `articles` 聚合去重，含 `reportDate`） |

## 关键常量

- `MAX_ARTICLES_PER_SOURCE = 2`（代码层硬限制，harness 层限制为 3，取严格值）
- 日报输出目录：`docs/daily/`
- 归档数据文件：`data/daily/archives.json`
- 源进度日志：`.agent/progress/daily/src-*.json`（每源一个文件，文章全集 + `reportDate`）
