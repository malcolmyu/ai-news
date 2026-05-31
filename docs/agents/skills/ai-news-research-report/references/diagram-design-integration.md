# diagram-design 在 ai-news 报告中的使用模式

## 适用场景

当报告涉及系统架构、数据流、分层设计等需要可视化表达的内容时，用 diagram-design skill 替代纯文字的 grid-2 卡片。

## 已加载的 skill

`diagram-design` skill 位于 `~/.hermes/skills/diagram-design/`，支持 13 种图表类型。

## ai-news 品牌配色覆盖

diagram-design 默认使用 rust orange (`#eb6c36`) 作为 accent。为匹配 ai-news 品牌色，在创建图表时覆盖以下 token：

| Token | ai-news 值 | 说明 |
|-------|-----------|------|
| `paper` | `#f5f5f4` | 与 ai-news 页面背景一致 |
| `ink` | `#1c1c1c` | ai-news 正文色 |
| `accent` | `#2563eb` | ai-news 强调色（替代 rust） |
| `accent-tint` | `rgba(37,99,235,0.08)` | 强调柔底色 |
| `muted` | `#6b6b6b` | 次要文字 |
| `soft` | `#8b8b8b` | 浅灰 |

## 嵌入方式

不使用 inline SVG（字体系统不同，ai-news 报告用 Inter，diagram-design 默认用 Instrument Serif + Geist，两者都不支持中文）。改为：

1. **生成独立 HTML 文件**到 `docs/research/assets/<name>.html`
2. **⛔ 字体必须替换为中文支持字体**：Noto Serif SC（标题） + Noto Sans SC（正文） + Noto Sans Mono SC（标签）
   - Instrument Serif / Geist / Geist Mono 是纯拉丁字体，中文字符会渲染为豆腐块或回退到系统默认字体
   - 字体替换清单：`Instrument Serif` → `Noto Serif SC`、`Geist` → `Noto Sans SC`、`Geist Mono` → `Noto Sans Mono SC`
3. **SVG 内所有标注必须中文**：节点名、层名、端口、图例、箭头标签、卡片标题一律中文。仅技术术语无合适中文时保留英文（如 API、SDK、GPU、ClickHouse）
4. **通过 iframe 嵌入**到报告中：

```html
<div style="background:#f5f5f4;border-radius:8px;overflow:hidden;margin-top:10px;">
  <iframe src="assets/<name>.html" style="width:100%;height:620px;border:none;" loading="lazy"></iframe>
</div>
```

5. **在 iframe 下方添加标签行**展示图中关键组件名。

## 已验证案例

- `docs/research/assets/aios-architecture.html` → 嵌入到 `agent-os-runtime.html`
  - 图表类型：分层架构图（应用层 → 内核 → 硬件层，7 个内核模块）
  - **全中文重绘 + Noto 字体**（2026-05-25 修复：原始 Instrument Serif 字体导致中文不渲染）

- `docs/research/assets/langsmith-architecture.html` → 嵌入到 `langsmith.html`
  - 图表类型：Architecture（控制平面 + 数据平面 + 存储层三层架构）
  - 9 节点，12 箭头，2 个 focal 元素（异步队列 + SmithDB），4 个 summary cards + legend
  - **全中文重绘 + Noto 字体**（2026-05-25 修复：SVG 标签 CONTROL PLANE/STORAGE/PROXY 等全部翻译为中文）

## 注意事项

1. **图表文件需提交到 git**：`docs/research/assets/` 目录下的 .html 文件需随报告一起 push。
2. **搜索索引自动覆盖**：Pagefind 会索引 assets 目录下的 HTML 文件（它们被 lang 检测为 `en`）。
3. **复杂度预算**：diagram-design 限制最多 9 节点、12 箭头、2 个 coral 元素。如果超了，拆成 overview + detail 两张图。
4. **字体独立性**：每个图表 HTML 自带 Google Fonts 引用。**中文报告必须使用 Noto 系列（Noto Serif SC + Noto Sans SC + Noto Sans Mono SC）**，禁止使用 diagram-design 默认的 Instrument Serif + Geist（纯拉丁字体，中文不渲染）。英文报告可保持默认字体。
