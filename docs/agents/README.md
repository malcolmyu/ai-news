# 智能体生产系统

这个目录保存“第二号”内容生产框架的项目内规则。全局 Hermes skill 可以引用这里，但这里才是当前仓库的权威版本。

## 目录入口

- `architecture.md` — Hermes/Codex 分工、生产轨道、执行流程、验证职责。
- `contracts/daily-digest.schema.json` — 日报结构化数据契约。
- `contracts/research-report.schema.json` — 调研报告结构化数据契约。
- `skills/ai-news-research-report/` — 日报和调研报告的项目内生产流程。
- `skills/daily-digest-media-fetch/` — Builder 动态、X/Twitter 图片、YouTube 缩略图和图片尺寸处理流程。

## 分工

Hermes 负责调度。它应该读取本目录中的规则，决定何时生产日报或调研报告，并把任务交给 Codex。

Codex 负责执行。它应该在仓库内完成文件编辑、媒体处理、结构校验、搜索索引重建、浏览器验收和 git 操作。

代码库负责保存契约。任何和这个项目强相关的架构、执行流程、子智能体约定和验证规则，都应该优先写回本目录或 `scripts/`，再考虑同步到全局 skill。

## 更新规则

生产流程发生变化时，先更新项目内文档和脚本，再同步全局 Hermes skill。

页面结构或样式规则发生变化时，同时更新：

- `docs/agents/architecture.md`
- 相关 `docs/agents/skills/*/SKILL.md`
- `scripts/site_harness.py validate`
- `.github/style-check.sh`，如果部署门禁也需要知道这条规则

新增可执行能力时，优先暴露为稳定命令，例如 `npm run site:update`，让 Hermes 和 Codex 都通过同一入口调用。
