# 首页日历组件

首页 Daily 区域包含一个右侧日历组件，展示当月所有日报日期。

## 实现位置

- **HTML**: `docs/index.html` 的 `<script>` 块内含有 `REPORTS` 数组和日历渲染逻辑
- **CSS**: `docs/styles.css` 的 「Daily Section Two-Column Layout」和「Calendar Card」节

## 日历数据

日历通过硬编码的 `REPORTS` 数组知道哪些日期有日报文件：

```js
const REPORTS = [
  '2026-03-26','2026-03-27','2026-03-28','2026-03-29','2026-03-30','2026-03-31',
  '2026-04-01','2026-04-02','2026-04-03','2026-04-04','2026-04-05','2026-04-06',
  '2026-04-09','2026-04-15',
  '2026-05-11','2026-05-13','2026-05-14','2026-05-15','2026-05-16','2026-05-17',
  '2026-05-18','2026-05-19','2026-05-20','2026-05-21','2026-05-22','2026-05-23'
];
```

## ⛔ 新增日报时必须同步更新 REPORTS 数组

每次创建新的 `docs/daily/ai-news-YYYY-MM-DD.html` 后，**必须在 `docs/index.html` 的 REPORTS 数组中添加该日期**，否则日历不会标记该天有日报。

同时更新「历史日报」卡片的归档总数（`共 N 期归档`）。

## 每日 AI 日报卡片布局（⛔ 硬性约束）

首页 Daily 区域左侧为日报列表，右侧为日历。左侧固定 **4 行**，通过 flex + `align-items: stretch` 与右侧日历高度对齐。

**⛔ 条目数硬性上限：3 条日报 + 1 条归档 = 4 行。** 违背此约束会导致左右列高度不对齐。

### 四行结构

| 行 | 内容 | CSS class | 特征 |
|----|------|-----------|------|
| 1 | 今日日报 | `daily-entry daily-entry-today` | 无图标，badge 左置，摘要+数据行 |
| 2 | 昨日日报 | `daily-entry` | 标准：图标+标题+日期 |
| 3 | 前日日报 | `daily-entry` | 标准：图标+标题+日期 |
| 4 | 历史日报 | `daily-entry daily-entry-archive` | 无图标，灰底虚线，极矮 |

**⛔ 严禁出现第 5 行。** 昨前日之后的旧日报（如大前日）不得出现在首页列表中——读者应通过「历史日报」入口访问归档页。

### 今日日报卡片（第 1 行）

```html
<a href="daily/ai-news-YYYY-MM-DD.html" class="daily-entry daily-entry-today" style="padding:18px 20px;">
  <div style="flex:1;min-width:0;">
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
      <span class="featured-badge">最新</span>
      <span style="font-size:12px;color:var(--text-muted);">5月23日</span>
    </div>
    <div style="font-weight:500;font-size:15px;margin-bottom:6px;">标题</div>
    <div style="font-size:12px;color:var(--text-secondary);line-height:1.55;margin-bottom:10px;">2 句摘要段落</div>
    <div style="display:flex;gap:18px;">
      <div><span style="font-size:18px;font-weight:500;color:#1c1c1c;">N</span><span style="font-size:10px;color:var(--text-muted);margin-left:3px;">标签</span></div>
      <!-- 共 4 项数据 -->
    </div>
  </div>
  <div style="flex-shrink:0;font-size:18px;color:var(--text-muted);">→</div>
</a>
```

关键约束：
- **无 `.entry-icon`** — 对齐 Research featured-card 风格
- **`featured-badge` 在标题左侧**，非右侧的 `badge-latest`
- 摘要从日报 digest 的 Hero 副标题中提取，2 句即可
- 数据行从日报 Hero 的 `.stat-row` 提取 4 项（如焦点事件/深度播客/Builder/项目）

### 历史日报卡片（第 4 行）

```html
<a href="daily/archive.html" class="daily-entry daily-entry-archive" style="justify-content:space-between;">
  <span style="font-size:12px;font-weight:500;color:var(--text-secondary);">历史日报</span>
  <span style="font-size:11px;color:var(--text-muted);">共 N 期归档 →</span>
</a>
```

关键约束：
- **无图标、纯文字**
- `background: #fafafa`，`border: 1px dashed var(--border)`（在 styles.css 的 `.daily-entry-archive` 中定义）
- `padding: 6px 16px`，极小高度
- 两端分散布局（`justify-content: space-between`）
- 每次新增日报后同步更新 `N` 计数

### CSS 依赖（styles.css）

```css
.daily-layout {
  align-items: stretch;  /* ⛔ 必须是 stretch，非 start */
}
.daily-entry-today {
  flex: 2.6;
  padding: 16px 20px;
}
.daily-entry-archive {
  flex: 0.45;
  padding: 6px 16px;
  background: #fafafa !important;
  border: 1px dashed var(--border) !important;
}
```

### 新增日报时的首页更新清单

1. 更新第 1 行 href + 标题 + 摘要 + 数据行
2. 下移旧日日报到第 2、3 行
3. 在 REPORTS 数组中追加新日期
4. 更新第 4 行「共 N 期归档」计数
5. 浏览器验证 4 行高度与右侧日历对齐

## 日历交互

- 月份切换：左右箭头按钮（`calPrev()` / `calNext()`）
- 有日报的日期：淡紫底色 + 紫色圆点标记，clickable → 跳转到 `daily/ai-news-YYYY-MM-DD.html`
- 今天：深紫底色高亮
- 底部图例：有日报 / 今天 / 本月 N 篇日报
