# 会话结束清单（Clean State Checklist）

> **Agent 必读**：每次会话结束前，逐项检查以下清单。只有全部通过才算干净结束。

---

## 1. 验证通过

- [ ] `npm run build` 零错误、零警告（`tsc --noEmit` + Babel 编译通过）
- [ ] 如本次修改了 `daily-reporter` 相关代码：跑过 `node dist/main.js daily --no-summarize`，日志中无 `Failed to fetch`
- [ ] 如本次修改了 `homepage-builder` 相关代码：跑过 `node dist/main.js homepage`，`docs/index.html` 有更新

## 2. 代码状态干净

- [ ] 没有未提交的修改（`git status` 干净），或所有改动都有明确理由暂缓提交
- [ ] 没有临时调试代码（`console.log` 临时输出、硬编码的测试 URL、注释掉的旧逻辑等）
- [ ] 没有留在代码里的 `TODO` / `FIXME` 未记录到 `.agent/claude-progress.md`

## 3. 状态文件更新

- [ ] `.agent/claude-progress.md` 已更新本次会话的 "做了什么" 和 "验证证据"
- [ ] `.agent/feature_list.json` 中受影响 pipeline 的 `last_success` 和 `status` 已更新
- [ ] 本次计划（如有）已从 `.agent/plans/active/` 移入 `.agent/plans/complete/`

## 4. 已知问题记录

- [ ] 本次发现但未修复的问题已记录到 `.agent/claude-progress.md` 的 "未完成 / 已知问题" 区块

## 5. Commit 信息规范

- [ ] Commit message 使用 Conventional Commits 格式（`feat:`、`fix:`、`chore:`、`refactor:`、`docs:`）
- [ ] 每个 commit 只包含一个逻辑单元的改动，不要把不相关的文件塞进同一个 commit

---

**清单全部通过 = 干净结束。下次会话可以从确定状态开始。**

**任何一项未通过 → 修复后再结束，不要留烂摊子。**
