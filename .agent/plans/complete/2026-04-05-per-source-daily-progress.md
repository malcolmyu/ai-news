# 计划：按信息源维护 progress 日志（替代按日全量快照）

**状态：** 已完成（2026-04-05）  
**创建日期：** 2026-04-05  
**修订：** 进度文件直接放在 `.agent/progress/daily/`，不建 `sources/` 子目录；删除全部旧 `daily-checker-*.json`。

---
**涉及 pipeline：** `daily-reporter`（`.agent/progress/daily/` 写入策略）

---

## 1. 需求澄清（brainstorming）

### 1.1 当前问题

- 每次 `daily` 运行会生成 **`daily-checker-YYYY-MM-DD.json`**，内含**当日所有源**及每源下**全部文章元数据**。
- 多天时，同一 RSS/HTML 源在相邻日期的条目高度重叠；按日存储导致：
  - 文件内容重复、体积膨胀；
  - 跨会话排查「某一源是否长期异常」需要打开多个按日文件对比。

### 1.2 目标（用户意图）

- **按信息源**持久化进度/健康日志，而不是按「自然日一份大 JSON」。
- 每个源可保留 **20 条以上** 的历史记录（建议上限可配置，例如 **25～30**），形成**时间序列**，便于观察单源稳定性。
- 「每天拉取内容基本一样」→ 不必在磁盘上为每一天重复存全量快照；**以源为维度的滚动历史**更符合运维与 agent 续跑需求。

### 1.3 非目标（本阶段明确不做或后置）

- **不**改变 `data/daily/archives.json` 与 `docs/daily/*.html` 的生成语义（日报产物仍以「报告日期」为准）。
- **不**要求与旧 `daily-checker-*.json` 二进制兼容；可做**迁移说明**与**过渡期并存**策略。
- **不**将摘要全文写入 progress（保持与现有一致：元数据 + 可选摘要长度）。

### 1.4 约束与原则

- 路径仍落在 **`.agent/progress/`** 下，符合仓库对 agent 持久化的约定。
- 文件名需**稳定、可预测**（与 `config/sources.yaml` 中源名或 URL 派生 id 绑定），避免中文路径问题（建议 **ASCII slug**）。
- 单文件大小有界：通过 **条数上限 + 每条字段精简** 控制。

---

## 2. 设计方案

### 2.1 目录与文件命名

建议结构：

```text
.agent/progress/daily/sources/
  <source-slug>.json    # 每个启用源一个文件（或仅记录曾抓取过的源）
```

- **`source-slug`**：由 `name` + `url` 稳定哈希或规范化 slug（例如 `sha1` 前 8 位 + 短名），避免同名不同 URL 冲突。
- 可选：在 JSON 内保存 `sourceName`、`sourceUrl` 供人类阅读。

### 2.2 单文件 JSON schema（草案）

```json
{
  "_schema": "ai-news-source-progress/v1",
  "sourceName": "宝玉",
  "sourceUrl": "https://s.baoyu.io/feed.xml",
  "sourceType": "rss",
  "updatedAt": "2026-04-05T01:28:27.861Z",
  "runs": [
    {
      "reportDate": "2026-04-05",
      "generatedAt": "2026-04-05T01:28:27.861Z",
      "fetchSuccess": true,
      "errorMessage": null,
      "fetchDurationMs": 1114,
      "fetchedArticles": 3,
      "articles": [ { "title", "link", "publishedDate", "hasSummary", "summaryLength" } ]
    }
  ]
}
```

- **`runs`**：**新记录 prepend 或 append**（实现选一种；建议 **unshift 最新在前**，便于阅读）。
- **保留策略**：超过 `MAX_RUNS`（默认 **25**，可配置常量或环境变量）时丢弃最旧记录。
- **失败运行**也写入一条 `fetchSuccess: false`，便于统计连续失败天数。

### 2.3 与现有 `DailyCheckReport` 的关系

| 能力 | 现状 | 变更后 |
|------|------|--------|
| 单次运行控制台摘要 | `generateSummary(report)` | **保留**：仍基于**内存中**当次 `DailyCheckReport` 生成，行为不变。 |
| 落盘 | 单日 `daily-checker-YYYY-MM-DD.json` | **改为**每源 `sources/<slug>.json` 追加/更新；**可选**是否保留一份「仅元数据的当日索引」见下。 |
| 跨日对比 | 打开多个按日文件 | **打开单源文件**即见多期历史 |

**可选（Minor，可放 Phase 2）：** 仍写一份轻量 `daily-checker-YYYY-MM-DD.meta.json`（只含日期、各源 slug 列表、成功/失败计数），用于快速按日索引；**非验收必须**。

### 2.4 迁移与兼容

- **旧文件** `.agent/progress/daily/daily-checker-*.json`：**保留不删**（历史归档），新逻辑不再写入。
- 在 `ARCHITECTURE.md` 或 `.agent/claude-progress.md` 中**一行说明**新旧路径，避免 agent 误读旧文件为「当前事实」。

---

## 3. 任务拆分（TDD 粒度，执行阶段用）

> 以下在 **Phase 2** 经用户批准后再实现；顺序建议自上而下。

1. **类型与工具函数**  
   - 定义 `SourceProgressFile`、`SourceRunEntry`（与现有 `SourceCheckResult` 字段对齐并精简）。  
   - 实现 `makeSourceSlug(source: SourceConfig): string`（单元测试：同名不同 URL、特殊字符）。

2. **`DailyChecker` 重构**  
   - 新增 `appendSourceRun(source, runPayload)` 或等价 API；读-改-写单文件，带 `MAX_RUNS`。  
   - 保留 `createEmptyReport` / `addSourceCheck` / `generateSummary` 供单次运行与日志输出。  
   - **移除或替换** `saveReport` 的「按日全文件」行为 → 改为在 `fetchArticlesWithCheck` 循环内每源写完 **或** 循环结束后批量写（推荐 **每源立即写**，避免中途崩溃丢失全部）。

3. **`DailyReporter` 集成**  
   - `fetchArticlesWithCheck` 末尾：不再调用 `saveReport(checkReport)` 写单日大文件；改为对每个 `checkReport.sources` 对应的源调用新 API。  
   - 确认 `DailyCheckReport` 仍用于 `generateSummary` 与 logger。

4. **测试**  
   - `src/test/` 增加 `daily-checker` 或 `source-progress` 测试：slug、截断、JSON 读写、失败路径。  
   - `npm run build` + `npm run test` 全绿。

5. **文档**  
   - `ARCHITECTURE.md` Harness/数据流小节更新 progress 路径；`src/agents/daily-reporter/AGENTS.md` 若有 progress 描述则同步。  
   - `.agent/evaluator/daily-report-harness.md` 若提及 progress，检查是否需改路径（只读）。

6. **Phase 4 收尾**  
   - `bash .agent/init.sh`、更新 `.agent/claude-progress.md` / `feature_list.json`（若本变更影响 `daily-reporter` 验证命令）。

---

## 4. 验收标准（Phase 3 对照）

- [ ] 运行 `daily` 后，**`.agent/progress/daily/sources/`** 下出现**每源一个** JSON，且每个文件内 `runs` 条数 **≤ MAX_RUNS**（默认 25），且包含**最近一次**运行记录。
- [ ] 控制台 **Daily Check Summary** 与现网行为一致（仍可读）。
- [ ] **不再生成**新的 `daily-checker-YYYY-MM-DD.json`（旧文件可保留）。
- [ ] `npm run build` 零错误；`npm run test` 通过；新增测试覆盖 slug + 滚动保留逻辑。
- [ ] 文档已说明新路径与旧文件仅为历史归档。

---

## 5. 涉及文件路径（预期）

| 文件 | 变更 |
|------|------|
| `src/agents/daily-reporter/daily-checker.ts` | 核心：按源落盘、滚动历史 |
| `src/agents/daily-reporter/index.ts` | 调用新保存逻辑 |
| `src/test/...`（新建或扩展） | slug + 滚动 + 集成 |
| `ARCHITECTURE.md` | progress 说明 |
| `src/agents/daily-reporter/AGENTS.md` | 如有 progress 描述则更新 |

---

## 6. 风险与待决问题

1. **Slug 碰撞**：极小概率；可通过哈希后缀解决（测试中强制覆盖策略）。  
2. **并发**：若未来并行抓取多源，需文件锁或顺序写；**当前串行循环**无此问题。  
3. **Git 噪音**：每源文件每次运行会变；与现状按日大文件类似，可接受；若需可 `.gitignore` `sources/`（**需用户显式决定**，默认仍提交以便 agent 续跑）。

---

## 7. 批准后再执行

本计划经 **用户确认** 后，进入 **Phase 2（Execution）**：按上表任务顺序实现，每批完成后 **Phase 3（Evaluation）**：`requesting-code-review` 对照本计划 + `.agent/evaluator/daily-report-harness.md`。

**请确认：**  
- `MAX_RUNS` 默认 **25** 是否可接受？  
- 新日志目录 **`.agent/progress/daily/sources/`** 是否 OK？  
- 旧 `daily-checker-*.json` **仅保留、不再写入** 是否可接受？
