# AGENTS.md

本项目强制使用 Superpowers 技能，按以下四阶段工作流执行所有开发任务。

## 强制工作流

### Phase 1: Planning（Planner）

**触发**：任何新功能开发、重构、非 trivial 修复  
**使用技能**：`brainstorming` → `writing-plans`  
**产物路径**：`.agent/plans/active/YYYY-MM-DD-<feature-name>.md`

1. 必须通过 `brainstorming` 澄清需求和设计方案，获得用户批准后方可继续
2. 必须通过 `writing-plans` 产出执行计划（覆盖默认路径，保存到 `.agent/plans/active/`）
3. 计划必须包含：任务列表（按 TDD 粒度拆分）、验收标准、涉及文件路径
4. 计划进入执行阶段时保持在 `active/`；全部任务完成并通过 Phase 3 后，移入 `complete/`

> 详细计划格式规范见 `writing-plans` skill。

---

### Phase 2: Execution（Generator）

**触发**：Phase 1 计划获得用户批准后  
**使用技能**：`executing-plans`

1. 读取 `.agent/plans/active/` 下的计划文件，逐批执行任务
2. 每个任务遵循 TDD 循环（RED → GREEN → REFACTOR），每步写明预期输出
3. 每批（默认 3 个任务）完成后，进入 Phase 3 评估，通过后继续下一批

---

### Phase 3: Evaluation（Evaluator）

**触发**：每批任务完成后  
**使用技能**：`requesting-code-review`（通用代码审查）+ 模块专属 harness（见下方）

#### 第一层：通用代码审查

使用 `requesting-code-review` skill，对照原始计划审查当前 diff：

- **Critical** 问题必须当场修复，不得进入下一批任务
- **Important** 问题必须在本批完成前修复
- **Minor** 问题记录到计划文件末尾，留后处理

#### 第二层：模块专属 Harness 评估

不同模块有各自的质量门禁，评估时须同时对照对应 harness 文件：

| 改动模块 | Harness 文件 |
|---------|-------------|
| `daily-reporter`（日报生成） | `.agent/evaluator/daily-report-harness.md` |
| 其他模块 | *(待补充，渐进式添加到 `.agent/evaluator/`)* |

Harness 评估与代码审查并行进行：harness 中任意一项未通过，视同 Critical 问题，必须修复。

> 各模块 harness 的完整规则见 `.agent/evaluator/` 目录，渐进式披露，按需加载。

---

### Phase 4: Completion

**触发**：所有任务完成且全部通过 Phase 3  
**使用技能**：`finishing-a-development-branch`（如可用）

1. 将计划文件从 `.agent/plans/active/` 移入 `.agent/plans/complete/`
2. 验证所有测试通过，`npm run build` 零错误
3. 提交最终代码，更新 `ARCHITECTURE.md`（如涉及结构变更）

---

## 约束

- 禁止跳过任何阶段
- 禁止在没有 `brainstorming` 确认需求的情况下直接写代码
- 禁止在没有 `writing-plans` 产出计划的情况下直接执行
- 每批任务必须通过 Phase 3 双层评估（代码审查 + harness）才能继续
- 计划文件必须存放在 `.agent/plans/`，禁止使用 `docs/plans/`
