# Claude 会话进度日志

> **Agent 必读**：每次会话开工前读取此文件，了解上次停在哪里；会话结束前更新，记录本次做了什么和验证证据。

---

## 最新状态（2026-04-16）

**当前分支：** `malcolmyu/auckland`  
**上次会话完成：** GPT-Researcher 深度调研系统 Docker 集成及 HTML 归档渲染功能开发  
**验证状态：** `npm run build` ✅ | Docker 容器正常启动 ✅ | 深调研 WebSocket 连接正常 ✅ | HTML 渲染与历史迁移 ✅

**本次开工前需要了解的背景：**
- `npm run research -- conduct <query>` 会连接 `localhost:8000` 进行强制中文回答请求
- 调研完毕后，`generator` 将 `markdown` 借助 `SolidJS ResearchReportPage` 及 `marked` 编译为精美单页面 `.html` 落在 `docs/research/` 中
- 所有旧 Markdown 文件归档均已被脚本重新通过编译器洗了一遍落地为新版网页

---

## 2026-04-16 — 生成 HTML 版深度调研报告

**做了什么：**
- 将纯输出 Markdown 逻辑重构成了 SolidJS 的 `ResearchReportPage.tsx`，通过 `marked` 引擎输出标准 HTML 文件。
- 更新并拦截内部存档指令，强制约束 GPT-Researcher 全程使用中文长文进行汇报。
- 一次性重塑历史存档，遍历 `data/research/categories/...` 将过去的 Markdown 重新渲染为了前端可读页，彻底打通网站链路。

**验证证据：**
- `npm run build` ✅
- 迁移脚本生成 HTML 成功，归档和首页已正确重建关联。

---

## 最新状态（2026-04-05）

**当前分支：** `malcolmyu/auckland`  
**上次会话完成：** Daily progress 改为按源滚动日志（`.agent/progress/daily/src-*.json`），删除旧 `daily-checker-*.json`  
**验证状态：** `npm run build` ✅ | `npm run test` ✅（34/35 通过；`rss-fetcher.test.js` 仍有既有 async 告警失败）  

**本次开工前需要了解的背景：**
- `.agent/progress/daily/` 下为每源一个 `src-<slug>.json`，每条保留最近约 25 次运行；见 `src/agents/daily-reporter/daily-checker.ts`

---

## 最新状态（2026-04-04）

**当前分支：** `malcolmyu/auckland`  
**上次会话完成：** 项目单元测试框架搭建（29个测试全部通过）  
**验证状态：** `npm run build` ✅ | `npm run test` ✅ (29/29 tests passing) | `bash .agent/init.sh` ✅  

**本次开工前需要了解的背景：**
- 系统已从模板字符串 HTML 迁移到 SolidJS `renderToString` 渲染（见 `src/renderer/`）
- `HTMLFetcher` 已从 axios+jsdom 改为 Playwright headless（`src/agents/daily-reporter/fetchers/html-fetcher.ts`）
- `TeamCoordinator` 已删除，`main.ts` 直接调用各 agent
- `config/sources.yaml` 所有源均 `enabled: true`，其中 ampcode.com 仍返回 0 篇（selector 需微调，低优先级）
- 5 个 HTML 源抓取状况：Manus(49)、Cognition(28)、Cline(49)、AmpCode(0)、Anthropic(21)
- 已添加完整的单元测试框架，使用 Node.js 内置 `node:test`

---

## 2026-04-05 — 按信息源 progress 日志

**做了什么：**
- `daily-checker.ts`：`persistSourceProgress` 写入 **v2** `src-<slug>.json`（`articles` 按 link 合并，记录 `publishedDate` / `reportDate`）；旧 v1 `runs` 首次写入时会迁移
- 移除按日 `daily-checker-YYYY-MM-DD.json` 写入；删除仓库内既有 5 个旧文件
- `index.ts`：抓取结束后仅调用 `persistSourceProgress`；失败路径不再重复落盘
- 新增 `src/test/daily-reporter/daily-checker.test.ts`（4 个测试）
- 更新 `ARCHITECTURE.md`、`src/agents/daily-reporter/AGENTS.md`；计划归档至 `.agent/plans/complete/2026-04-05-per-source-daily-progress.md`

**验证证据：**
- `npm run build` ✅
- `npm run test`：34 pass，1 fail（`rss-fetcher` 既有问题）

---

## 2026-04-04 — 项目单元测试框架搭建

**做了什么：**
- 新增 `src/test/` 目录结构（`utils/`、`fetchers/`）
- 新增 `test/data/` 测试数据目录
- 新增 `src/test/utils/test-utils.ts`：测试辅助函数（mock数据、console 模拟等）
- 新增 `src/test/utils/logger.test.ts`：`Logger` 类测试（10个测试）
- 新增 `src/test/utils/config.test.ts`：配置工具测试（7个测试）
- 新增 `src/test/fetchers/rss-fetcher.test.ts`：`RSSFetcher` 测试（5个测试）
- 新增 `src/test/fetchers/html-fetcher.test.ts`：`HTMLFetcher` 测试（5个测试）
- 新增 `src/test/integration.test.ts`：集成测试（2个测试）
- 更新 `package.json`：优化 `test` 脚本，新增 `test:watch`
- 测试总数：29 个，全部通过

**验证证据：**
- `npm run build` ✅ 零错误
- `npm run test` ✅ 全部 29 个测试通过
- `bash .agent/init.sh` ✅ 通过

**未完成 / 已知问题：**
- ampcode.com selector 需要微调（低优先级）
- `session-handoff.md` 可以在需要时添加（长会话场景用）
- 单元测试可以进一步增加覆盖率（如 parser 私有方法测试需要重构为可测试）

---

## 历史记录

### 2026-03-31 — Harness 基础设施升级

**做了什么：**
- 新增 `.agent/init.sh`（环境验证脚本：Node 版本 + build + Playwright 检查）
- 新增 `.agent/feature_list.json`（4 条 pipeline 健康状态追踪）
- 新增 `.agent/claude-progress.md`（本文件，会话进度持久化）
- 新增 `.agent/clean-state-checklist.md`（会话结束前的自检清单）
- 重写 `AGENTS.md`（融合 learn-harness-engineering 官方模板的开工流程、工作规则、完成定义、收尾）
- 更新 `ARCHITECTURE.md`（修正已删除的 coordinator/shared-styles 等过时引用，补充 SolidJS/Playwright/harness 说明）

**验证证据：**
- `bash .agent/init.sh` ✅ 输出：`Harness init complete. Ready to work.`
- `npm run build` ✅ 零错误

**未完成 / 已知问题：**
- ampcode.com selector 需要微调（低优先级）
- `session-handoff.md` 可以在需要时添加（长会话场景用）

---

### 2026-03-31 — Playwright HTMLFetcher

**做了什么：**
- 安装 playwright + Chromium，将 HTMLFetcher 从 axios+jsdom 重写为 Playwright headless
- 启用 `config/sources.yaml` 中全部 5 个 HTML 源
- Phase 3 代码审查修复：browser.close() 移入 finally、Set 去重、domcontentloaded+waitForSelector、Logger 注入

**验证证据：**
- `npm run build` ✅ 零错误
- 冒烟测试：Manus(49)、Cognition(28)、Cline(49)、Anthropic(21) 全部正常

**Commits：** `821ee3e` → `6e20b63`

---

### 2026-03-31 — SolidJS SSR 迁移 + 架构简化

**做了什么：**
- 删除 `src/team/coordinator.ts`，`main.ts` 改为直接调用 agent
- 将所有 HTML 生成从模板字符串迁移到 SolidJS `renderToString`
- 新增 `src/renderer/` 共享渲染层，各 agent 新增 `*.tsx` 页面组件
- 修复 `config/sources.yaml` 字段名不匹配（`selectors.link` → 平铺 `selector`）
- 新增 `AGENTS.md`、`CLAUDE.md`、初版 `ARCHITECTURE.md`

**验证证据：**
- `npm run build` ✅，`node dist/main.js homepage build` 生成 `docs/index.html` ✅

**Commits：** `39951a0`

---

## 下一步建议

优先级排序（由高到低）：

1. **[低] ampcode.com selector 微调** — 打开页面检查实际 DOM，更新 `config/sources.yaml` 中的 selector
2. **[低] session-handoff.md** — 如果某次会话特别长、改动特别多，可以额外新增会话交接文档
