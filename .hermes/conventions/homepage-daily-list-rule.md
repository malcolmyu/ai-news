---
name: homepage-daily-list-rule
description: 首页日报列表最多保留 3 天，与右侧日历高度对齐。
---

# 首页日报列表规范

## 规则

首页 `#daily` 区域的日报条目**严格限制 3 条**（今日 + 昨日 + 前日），外加 1 条「历史日报」归档链接。**禁止出现第 4 条日报条目。**

## 原因

右侧日历的高度大约对齐 3 条日报 + 归档链接。出现第 4 条日报会导致左侧超出日历高度，视觉不对齐。

## 正确结构（共 4 行）

```html
<div class="daily-left">
  <!-- 行 1：今日日报 — daily-entry daily-entry-today，无图标，有「最新」badge -->
  <a href="daily/ai-news-YYYY-MM-DD.html" class="daily-entry daily-entry-today">
    <span class="featured-badge">最新</span> 日期 → 标题 → 摘要 → 箭头
  </a>

  <!-- 行 2：昨日日报 — daily-entry，有 📰 图标 -->
  <a href="daily/ai-news-YYYY-MM-DD.html" class="daily-entry">
    <div class="entry-icon">📰</div> 日期 → 标题 → 箭头
  </a>

  <!-- 行 3：前日日报 — daily-entry，有 📰 图标 -->
  <a href="daily/ai-news-YYYY-MM-DD.html" class="daily-entry">
    <div class="entry-icon">📰</div> 日期 → 标题 → 箭头
  </a>

  <!-- 行 4：历史日报 — daily-entry daily-entry-archive -->
  <a href="daily/archive.html" class="daily-entry daily-entry-archive">
    历史日报 · 共 N 期归档 →
  </a>
</div>
```

## 错误结构（禁止）

第 4 条日报（如下面的 6/3）会破坏对齐：

```html
<!-- ❌ 禁止：多了一条 6/3，共 5 行 -->
<a href="daily/ai-news-2026-06-03.html" class="daily-entry">...</a>
```

## 更新日报时的步骤

1. 新增 `daily-entry-today`（最新日报）
2. 把旧的 today 降级为普通 `daily-entry`（去掉 `daily-entry-today` 和 `featured-badge`）
3. 把原第 2 条降为第 3 条
4. **删除原来的第 3 条**（它变成第 4 条了，不符合 3 天限制）
5. 更新「共 N 期归档」计数

## 保护机制

- CLAUDE.md 核心约束 #10
- style-check.sh 检测超过 3 条日报
