# Spine 报告使用的卡片布局模式

> 参考报告：`docs/research/spine-research.html`  
> 使用场景：模式 B — 技术原理 + AI 可行性分析
> 风格基线：`docs/research/managed-agents.html`（100% 正确参考）

## 布局结构概览

```
span-4  Hero（标题+数据+标签）
span-2  关键数据 stats
span-2  什么是 Spine
span-4  架构总览（vlist）
span-2  核心概念 ①（骨骼/插槽/附件 + quote）
span-2  核心概念 ②（皮肤/动画/约束 + vlist）
span-2  渲染管线（vlist + dots-row）
span-2  数据格式（table + quote）
span-2  局限性（vlist）
span-4  【分隔】"Part II · AI Generated Spine"（card-highlight）
span-3  能力矩阵（table + inline-style tags）
span-2  Genielabs（inline-style + vitem + dots-row）
span-2  God Mode AI（inline-style + vitem + dots-row）
span-2  ComfyUI UniRig（inline-style + vitem + dots-row）
span-2  Layer AI & Stretchy（纯 body-text）
span-4  学术界进展（table）
span-4  理想管线设计（vlist 双列并排 + quote）
span-2  Gap 分析（vlist 红 X）
span-2  展望 + quote
span-4  总结（tips-grid + tip-card）
span-4  参考来源
```

## CSS 风格要点

### 全部直写值，无变量

```css
background: #f5f5f4;       /* body */
background: #fff;           /* .card */
border: 1px solid #e8e8e6; /* .card border */
border-radius: 14px;       /* .card 圆角 */
```

### 核心 class 清单（完整 CSS 约 80 行）

| class | 用途 | 关键属性 |
|-------|------|----------|
| `.card` | 所有白卡 | 14px 圆角, 20px padding, 阴影 |
| `.card-highlight` | 分隔强调卡 | rgba(#2563eb, 0.02) 底色 + 12% 边框 |
| `.bento` | 4 列网格 | gap:16px, 桌面 32px/24px/48px padding |
| `.header` + search modal | 统一导航 | bento 外部，由共享页面骨架提供；不要再使用旧 `.nav-back` |
| `.label-sm` | 标签头 | 11px 600 大写, 0.06em 间距 |
| `.vlist / .vitem` | 通用垂直列表 | 10px 圆角, #fafafa 底, gap:10px |
| `.vitem-icon` | 列表图标 | 24×24 灰底圆角方块, 可换色 |
| `.quote` | 引用框 | 左 3px #2563eb 竖线, #fafafa 底 |
| `.tag` | 标签 | 10px 600, 5px 圆角, inline style 换色 |
| `.dots-row` | 标签行 | flex gap:6px wrap |
| `.tips-grid` | 两列网格 | gap:8px |
| `.tip-card` | 网格内项 | 10px 圆角, #fafafa 底 |
| `.text-body` | 正文 | 13px #4a4a4a lh:1.6 |
| `.text-muted` | 辅助文字 | 12px #8b8b8b |
| `.stat-num` | 数据 | 26px 500 **黑色**（非 accent） |
| `.stat-label` | 数据标签 | 11px #8b8b8b |
| `.diagram-wrap` | SVG 容器 | 12px 圆角, #fafafa 底, 16px padding |
| `.code-block` | 代码块 | #1c1c1c 暗底, 12px monospace |

### 排版（与 managed-agents 一致）

```
h1: 32px / 500 / -0.5px / #1c1c1c / mb:4px
h2: 18px / 500 / -0.2px / #1c1c1c / mb:10px
h3: 14px / 600 / #1c1c1c / mb:6px
```

### 标签颜色（inline style）

```html
<span class="tag" style="background:rgba(37,99,235,0.08);color:#2563eb;">强调</span>
<span class="tag" style="background:rgba(16,185,129,0.08);color:#10b981;">可用</span>
<span class="tag" style="background:rgba(245,158,11,0.08);color:#f59e0b;">有限</span>
<span class="tag" style="background:rgba(239,68,68,0.08);color:#ef4444;">不可用</span>
```

### 三栏总结布局

```html
<div style="display:flex;gap:20px;align-items:flex-start;">
  <div style="flex:1;padding-right:20px;border-right:1px solid var(--border-light);">
    ...
  </div>
</div>
```
