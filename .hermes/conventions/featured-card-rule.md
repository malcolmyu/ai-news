# 首页深度报告区 Featured Card 规范

## 规则

首页 `#research` 区域的**第一条报告**必须使用 `featured-card` 样式，**禁止**改用 `daily-entry`。

## HTML 结构

```html
<a href="research/xxx.html" class="featured-card">
  <div class="featured-content">
    <div class="featured-meta">
      <span class="featured-badge">最新</span>
      <span>YYYY/M/D</span>
    </div>
    <h3 class="featured-title">报告标题</h3>
    <p class="featured-desc">报告描述，1-2 句话，约 50 字。</p>
  </div>
  <div class="featured-arrow">→</div>
</a>
```

## featured-card vs daily-entry 对比

| | featured-card | daily-entry |
|---|---|---|
| 布局 | grid 两列（内容+箭头） | flex 单行 |
| 内边距 | 24px | 14px 20px |
| 标题字号 | 18px h3 | 14px div |
| 有描述？ | ✅ `<p class="featured-desc">` | ❌ |
| 有徽章？ | ✅ `最新` 蓝色徽章 | ❌ |
| 图标 | 无 | 📊 emoji |

## 保护机制

1. **HTML 守卫注释**：featured-card 前后有 `<!-- FEATURED-CARD-START -->` / `<!-- FEATURED-CARD-END -->` 标记，任何代码生成工具应识别并保留。
2. **style-check.sh 硬门禁**：检测 `#research` 区域第一条是否为 `class="featured-card"`，否则阻止推送。
3. **CLAUDE.md 声明**：项目规范文件中明确写死此规则。

## 更新流程

当首页深度报告列表需要更新（新增报告、调整顺序）时：
- 最新的报告放在第一位，使用 `featured-card`
- 其余报告使用 `daily-entry`
- 更新 featured-card 的标题、描述、日期、链接
- **不要删除 `featured-card` 结构**
