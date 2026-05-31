# 002 — Hermes/Codex 生产框架归属代码库

## 背景

AI 日报和深度调研报告最初主要依赖全局 Hermes skill 和 Codex 的临场执行。这个模式可以产出内容，但生产契约有一部分在仓库外部：样式要求、媒体规则、搜索索引、验证命令和交接方式容易随着不同 agent 或不同 skill 版本发生漂移。

用户的目标不是只维护一批 HTML 文件，而是在项目里构建一套生产框架：Hermes 调度，Codex 执行，仓库保存架构、执行方式、子智能体协议和验证规则。

## 决策

把本仓库视为生产框架的权威来源。

Hermes 负责定时、调度和选择项目内 skill。Codex 负责执行仓库改动、运行验证和做浏览器验收。所有项目特定的生产说明、结构契约和架构文档都放进 `docs/agents/`。可执行的站点维护和结构校验放在 `scripts/` 与 `.github/`。

稳定命令入口是：

```bash
npm run site:update
npm run site:validate
npm run build:search
bash .github/style-check.sh .
```

## 理由

这个项目的复杂度不在静态托管，而在稳定生产。日报和调研报告需要同时满足内容质量、媒体完整性、视觉一致性、搜索索引、归档同步和移动端展示。把这些约束放回仓库，智能体才能检查、修改、验证和继承。

项目内 contract 也能减少全局 skill 版本差异带来的隐性风险。全局 Hermes skill 可以作为入口，但它应该引用仓库内的规则，而不是自己成为规则来源。

## 影响

- `docs/agents/skills/` 是项目本地 skill 的来源。
- `docs/agents/contracts/` 描述未来结构化渲染器应产出的数据形状。
- `docs/agents/architecture.md` 描述 Hermes/Codex 的分工和执行流程。
- `scripts/site_harness.py` 是首页、归档和结构校验的核心脚本。
- 全局 Hermes skill 可以同步这些规则，但不能覆盖本仓库里的项目契约。
- Codex 在引入新的生产行为前，应优先更新仓库内生产框架和文档。
