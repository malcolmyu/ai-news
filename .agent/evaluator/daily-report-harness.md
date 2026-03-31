---
name: content-harness
description: AI 日报完整质量门禁（Harness）。涵盖摘要内容、来源配额、HTML 产物结构、分类规范和文件命名。生成或修改日报相关任何内容前必须遵守。
---

# AI 日报生成规范（Daily Report Harness）

作为本系统的 AI 记者，你的输出是用户每天了解行业动态的核心入口。以下规范分为五个层次，全部为强制约束，违反任意一条须原地重写，不得强行写入。

---

## 1. 来源配额约束（Source Quota）

**单个来源（source）在同一篇日报中最多出现 3 条文章。**

- 超出 3 条时，保留 `summaryQuality` 分值最高的 3 条，其余丢弃。
- 如果多条文章来自同一来源且质量分相同，保留 `published` 时间最晚的 3 条。
- 每日日报总条数建议区间：**5 — 20 条**。低于 5 条时须在日报顶部注明"今日内容较少"，超过 20 条须先按质量分截断再生成。

自检问题：当前日报里，有没有某个 source 名称出现超过 3 次？如有，立刻裁剪。

---

## 2. 摘要内容质量（Summary Quality）

### 2.1 长度与饱满度
- 单条摘要字符数：**50 — 400 字**（中文字符计 1，英文单词计 5）。
- 必须由多个完整句子组成，禁止用孤立的单句或标题党式短语敷衍。

### 2.2 防幻觉约束
- **禁用推测词**：或许、大概、可能、也许、似乎、好像、据说（对应英文：maybe, perhaps, possibly, apparently, seemingly）。
- 输出必须基于原文可核实的事实，不得凭空补充细节或数据。
- 遇到原文信息不足时，直接缩短摘要，不要捏造。

### 2.3 必须涵盖的三个维度
每条摘要在逻辑上须包含（无需显式标题）：
1. **核心事件**：这条新闻在说什么，涉及哪家公司或技术。
2. **关键洞察**：有什么突破点、开源特性或反常规之处。
3. **实际影响**：对开发者、产品或行业带来了什么可操作的启示。

---

## 3. 分类规范（Category Rules）

文章按 `article.category` 字段分组渲染为独立 `<section>`。

### 3.1 有效分类白名单
只允许以下分类名称，不得自造新词：

| 分类名称 | 适用场景 |
|----------|----------|
| 大模型动态 | LLM 新版本、评测、能力更新 |
| 开源社区 | GitHub 项目、开源框架发布 |
| 产品与工具 | 新产品发布、工具更新、API 变更 |
| AI 安全与伦理 | 对齐研究、监管政策、安全漏洞 |
| 行业与商业 | 融资、并购、市场动态 |
| 研究与论文 | 学术论文、技术报告 |
| 综合资讯 | 不属于以上任何分类时的兜底项 |

若原文分类超出白名单，一律归入**综合资讯**。

### 3.2 分类数量限制
- 单篇日报中，出现的分类数量不得超过 **6 个**。
- 超出时，将条数最少的分类合并至**综合资讯**，直到满足限制。

---

## 4. HTML 产物结构规范（Output HTML Structure）

生成的 HTML 文件须严格使用以下 CSS 类名和结构，不得自行发明新 class 或内联覆盖已有样式。

### 4.1 文章卡片（必须结构）
```html
<article class="news-card">
  <div class="news-meta">
    <span class="news-source">{来源名称}</span>
    <span>·</span>
    <span>{发布日期}</span>
  </div>
  <h3 class="news-title">{文章标题}</h3>
  <p class="news-summary">{摘要正文}</p>
  <a href="{原文链接}" class="news-link" target="_blank" rel="noopener noreferrer">阅读原文 →</a>
</article>
```

禁止省略 `rel="noopener noreferrer"`，禁止将 `<article>` 替换为 `<div>`。

### 4.2 分类区块（必须结构）
```html
<section class="section">
  <div class="section-header">
    <h2 class="section-title">{分类名称}</h2>
    <span class="section-count">{N} 条</span>
  </div>
  <div class="news-list">
    <!-- 文章卡片列表 -->
  </div>
</section>
```

### 4.3 页头（必须结构）
```html
<div class="daily-header">
  <div class="container-sm">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div>
        <h1>🤖 AI 日报</h1>
        <p class="subtitle">{YYYY-MM-DD}</p>
      </div>
      <div style="text-align:right;">
        <div class="stats-value">{总条数}</div>
        <div class="stats-label">条资讯</div>
      </div>
    </div>
  </div>
</div>
```

### 4.4 响应式与暗色模式
- 所有产物 HTML 必须包含 `@media (max-width: 640px)` 断点规则。
- 必须包含 `@media (prefers-color-scheme: dark)` 暗色变量覆盖。
- 不得在 HTML 标签上硬编码颜色值（如 `color: #333`），必须使用 CSS 变量（`var(--text-primary)` 等）。

---

## 5. 文件命名与路径规范（File Naming）

| 产物 | 路径规范 | 示例 |
|------|----------|------|
| 日报 HTML | `docs/daily/ai-news-YYYY-MM-DD.html` | `docs/daily/ai-news-2026-03-31.html` |
| 最新日报副本 | `docs/daily/ai-daily-latest.html` | 每次生成后自动覆盖 |
| 归档索引页 | `docs/daily/archive.html` | 每次生成日报后重建 |

- 日期格式严格为 `YYYY-MM-DD`，月份和日期补零（03 而非 3）。
- 不得在 `docs/` 以外的路径写入 HTML 产物。

---

## 自检清单（保存前逐项核对）

在将任何日报内容写入文件之前，过一遍以下清单：

- [ ] 无单个来源超过 3 条文章
- [ ] 总条数在 5 — 20 条区间内
- [ ] 每条摘要字符数 50 — 400，无推测词
- [ ] 每条摘要覆盖核心事件、关键洞察、实际影响三个维度
- [ ] 所有分类名称在白名单内，且分类数 ≤ 6
- [ ] HTML 使用规定 class 名，无硬编码颜色，含响应式和暗色模式
- [ ] 文件路径和命名符合 `docs/daily/ai-news-YYYY-MM-DD.html` 格式

**任意一项未通过 → 原地重写，不得强行写入。**
