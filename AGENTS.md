# AGENTS.md

这个仓库面向长时运行的 coding agent 工作流。目标不是尽可能快地产出代码，而是让每一轮会话结束后，下一个会话仍然能无猜测地继续工作。

## 开工流程

写代码前先做这些事：

1. 用 `pwd` 确认当前目录。
2. 读取 `.agent/claude-progress.md`，了解最新已验证状态和下一步。
3. 读取 `.agent/feature_list.json`，了解各 pipeline 当前健康状态。
4. 用 `git log --oneline -5` 看最近提交。
5. 运行 `bash .agent/init.sh`（Node 版本 + build + Playwright 健康检查）。
6. 在开始新功能前，先跑必需的 smoke test 或端到端验证。

如果基础验证一开始就失败，先修基础状态，不要在坏的起点上继续叠新功能。

## 工作规则

- 一次只做一个功能。
- 不要因为"代码已经写了"就把功能标记为完成。
- 除非为了消除当前 blocker 的窄范围修复，否则不要扩大到其他功能。
- 实现过程中不要悄悄改弱验证规则。
- 优先依赖仓库里的持久化文件（`.agent/`），而不是聊天记录。

## 必需文件

- `.agent/feature_list.json`：各 pipeline 健康状态的唯一事实来源
- `.agent/claude-progress.md`：会话进度和当前已验证状态
- `.agent/init.sh`：统一的启动与验证入口（`bash .agent/init.sh`）
- `.agent/clean-state-checklist.md`：会话结束前的清理清单
- `.agent/evaluator/`：各模块的质量 harness 文件（按需加载）

## 完成定义

一个功能只有在以下条件都满足时才算完成：

- 目标行为已经实现
- 要求的验证真的跑过（`npm run build` ✅，冒烟测试输出已记录）
- 证据记录在 `.agent/feature_list.json` 或 `.agent/claude-progress.md`
- 仓库仍然能按标准启动路径重新开始工作（`bash .agent/init.sh` ✅）

## 收尾

结束会话前：

1. 更新 `.agent/claude-progress.md`（本次做了什么、验证证据、未完成问题）
2. 更新 `.agent/feature_list.json`（受影响 pipeline 的 `last_success` 和 `status`）
3. 记录仍未解决的风险或 blocker
4. 逐项核对 `.agent/clean-state-checklist.md`
5. 在工作处于安全状态后，用清晰的提交信息提交
6. 保证下一轮会话可以直接运行 `bash .agent/init.sh`

---

## 强制开发工作流（非 trivial 任务必须遵守）

**trivial 豁免**：单文件 bugfix、配置微调、文档编辑等 < 2 步完成的任务可跳过下方四阶段流程。不确定是否 trivial 时，默认按非 trivial 处理，先询问用户。

### Phase 1: Planning

**触发**：任何新功能开发、重构、非 trivial 修复  
**使用技能**：`brainstorming` → `writing-plans`  
**产物路径**：`.agent/plans/active/YYYY-MM-DD-<feature-name>.md`

1. 必须通过 `brainstorming` 澄清需求和设计方案，获得用户批准后方可继续
2. 必须通过 `writing-plans` 产出执行计划（覆盖默认路径，保存到 `.agent/plans/active/`）
3. 计划必须包含：任务列表（按 TDD 粒度拆分）、验收标准、涉及文件路径
4. 计划进入执行阶段时保持在 `active/`；全部任务完成并通过 Phase 3 后，移入 `complete/`

### Phase 2: Execution

**触发**：Phase 1 计划获得用户批准后  
**使用技能**：`executing-plans`

1. 读取 `.agent/plans/active/` 下的计划文件，逐批执行任务
2. 每个任务遵循 TDD 循环（RED → GREEN → REFACTOR），每步写明预期输出
3. 每批（默认 3 个任务）完成后，进入 Phase 3 评估，通过后继续下一批

### Phase 3: Evaluation

**触发**：每批任务完成后  
**使用技能**：`requesting-code-review`（通用代码审查）+ 模块专属 harness

**第一层：通用代码审查**

使用 `requesting-code-review` skill，对照原始计划审查当前 diff：

- **Critical** 问题必须当场修复，不得进入下一批任务
- **Important** 问题必须在本批完成前修复
- **Minor** 问题记录到计划文件末尾，留后处理

**第二层：模块专属 Harness 评估**

| 改动模块 | Harness 文件 |
|---------|-------------|
| `daily-reporter`（日报生成） | `.agent/evaluator/daily-report-harness.md` |
| 其他模块 | *(渐进式补充到 `.agent/evaluator/`)* |

Harness 评估与代码审查并行进行；harness 中任意一项未通过，视同 Critical 问题。

### Phase 4: Completion

**触发**：所有任务完成且全部通过 Phase 3

1. 将计划文件从 `.agent/plans/active/` 移入 `.agent/plans/complete/`
2. 验证 `npm run build` 零错误
3. 更新 `.agent/claude-progress.md` 和 `.agent/feature_list.json`
4. 如涉及结构变更，更新 `ARCHITECTURE.md`

---

## 约束

- 禁止跳过任何阶段
- 禁止在没有 `brainstorming` 确认需求的情况下直接写代码
- 禁止在没有 `writing-plans` 产出计划的情况下直接执行
- 每批任务必须通过 Phase 3 双层评估（代码审查 + harness）才能继续
- 计划文件必须存放在 `.agent/plans/`，禁止使用其他路径
