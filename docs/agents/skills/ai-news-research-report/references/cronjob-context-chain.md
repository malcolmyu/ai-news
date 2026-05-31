# Cronjob 链式调用 — context_from 模式

## 模式说明

Hermes cronjob 支持用 `context_from` 将一个 cronjob 的输出注入到另一个 cronjob 的上下文。适用于「产出 → 消费」管道。

## 配置示例

```javascript
cronjob(
  action="create",
  name="AI Builders Daily Report — ai-news",
  schedule="15 10 * * *",         // 在 digest 之后 15 分钟
  context_from=["1f154869747d"],  // 源 job ID
  workdir="/Users/yuminghao/Work/ai-news",
  enabled_toolsets=["file","terminal","web"],
  deliver="origin",
  prompt="..."
)
```

## 工作流

1. **源 cronjob** 输出完整的 digest 文本（含 skill 元数据 + 实际内容）
2. **目标 cronjob** 运行时，Hermes 自动注入源 cronjob 最近一次完成的输出
3. 目标 cronjob 的 agent 解析上下文中的 digest 内容，然后执行 HTML 生成/文件操作

## 已知陷阱

- **⚠️ context_from 注入但被忽略（2026-05-30 触发）**：即使 `context_from` 正确配置、prompt 写了「用那份文本作为内容源」，agent 仍可能因为 prompt 太长/子步骤太多而被带偏，自己去搜索、抓取完全不同的内容。症状：HTML 页面的 Hero 标题、Builder 动态、GitHub 排名与 digest 完全无关。修复：在 prompt **最顶部**放 `⛔ 核心约束` 块，用直白语言声明「不要搜索、抓取、或生成任何自己的内容」，放在所有子步骤之前。
- **context_from 注入的是完整输出**：包含 SKILL.md 元数据、系统指令等。prompt 必须明确指示 agent 过滤掉这些元数据，只解析实际的 digest 内容。
- **时序依赖**：目标 cronjob 的计划必须在源 cronjob 之后（至少 5-15 分钟间隔），两次运行间隔太短可能导致 context_from 取到上一次而非本次的输出。
- **workdir 的作用**：设定了 `workdir` 后，所有 terminal/git 命令都在该目录下执行。省去了 prompt 中反复写 `cd /path/to/project`。
- **enabled_toolsets 优化**：只开启实际需要的工具集。日报生成只需 `file`（write_file/patch）+ `terminal`（git）+ `web`（浏览器验证），不要开 `mcp`/`computer`/`browser` 等重型工具。
- **deliver="origin" 的副作用**：cronjob 的输出会投递到飞书聊天。日报生成的 cronjob 投递的是「已完成写入」的确认消息（可能包含 HTML 页面路径），用户会看到这条消息。
- **LLM 会编造 URL（致命）**：agent 从 digest 文本生成 HTML 时，经常编造不存在的 X/Twitter URL（推文 ID 是模型猜测的）。prompt 必须包含硬性约束：所有 URL 必须从 digest 原文中精确提取，不得生成或修改。无 URL 的条目直接跳过。
