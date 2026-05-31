# Cron Prompt Design for Digest → HTML Pipeline

## The Problem

Cron job `88c05cab9efd` (AI Builders Daily Report → ai-news) was producing thin HTML pages that ignored the `context_from` digest, even though the prompt had `⛔ 核心约束` at the top. The agent invented its own content (wrong Hero title, wrong builder list, wrong GitHub rankings).

## Root Cause

Three factors combined:

1. **Digest text is buried** — context_from injects the raw cron output (~900 lines), where the first 750 lines are skill instructions, not digest content. The agent must skip past them.

2. **Sub-steps distract** — When the prompt includes steps like "run fetch-daily-media.sh" or "extract URLs with regex", the agent switches to task-execution mode and loses sight of the content constraint.

3. **Identity drift** — The agent starts as a "content renderer" but slowly shifts to "researcher" mode when asked to process URLs, download media, or validate links.

## The Fix

### Principle: Black-box pre-steps

Any operation that isn't "read digest → write HTML" should be a **black-box sub-step**:

- **Step 0: Media fetch** — Single `bash` command, output to file. Agent reads the file, extracts paths, moves on. No processing, no decision-making.
- **Steps 1-7: Content generation** — Agent stays in "HTML renderer" mode, only using digest text as source.

### Prompt structure

```
## ⛔ 身份定位
你是一个 HTML 渲染器，不是一个研究员。唯一内容源是 context_from。

## 第零步：获取媒体（独立黑盒）
1. 提取 URL → 2. 跑脚本 → 3. 读输出 → 继续

## 第一步：定位 digest 正文
跳过前 ~750 行 skill 指令，从「💡 今日焦点」开始

## 第二-七步：生成 HTML → 更新首页 → 更新归档 → 检查 → 索引 → 推送
```

### Key constraint language

The most effective constraint is an **identity statement** at the top:

> 你是一个 HTML 渲染器，不是一个研究员。

This frames the role so the agent doesn't try to "help" by researching or fetching content.

### Self-check

Add a verification step at the end:

> Hero 标题是否与 digest 主题一致？（不一致→重做第一步）

This catches the most common failure mode: wrong topic entirely.
