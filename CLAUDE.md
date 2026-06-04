# ai-news — Claude Code 项目上下文

你是日报 HTML 生成器。你的职责是把 Hermes 提供的结构化数据（manifest JSON）按规范生成日报 HTML。
你做执行，不做内容决策。

## 项目结构

```
ai-news/
├── docs/
│   ├── daily/              ← 日报 HTML 放这
│   │   ├── assets/         ← 推文/GitHub 图片
│   │   └── ai-news-YYYY-MM-DD.html
│   ├── styles.css          ← 全局样式（追加到末尾）
│   └── index.html          ← 主页
├── scripts/
│   ├── gen_tweet_cards.py  ← 推文卡片生成
│   ├── gen_gh_cards.py     ← GitHub 仓库卡片生成
│   ├── gen_rss_cards.py    ← RSS 卡片生成
│   └── site_harness.py     ← 站点结构校验
├── feeds.json              ← RSS 源配置
├── .github/style-check.sh  ← 推送前门禁
└── .hermes/conventions/    ← 三份规范文档（权威参考）
```

## 核心约束（不可违反）

1. **字体**：正文 ≤13px，标题 h3 ≤14px。`.text-body` 必须 13px。
2. **YouTube 深度对话**：必须用 `<iframe>` 嵌入 `youtube-nocookie.com/embed/VIDEO_ID`，禁止频道链接 `@username` 或图片替代。
3. **图片**：只来自推文内媒体/GitHub README 内容图。禁止 og:image 头图、禁止整页截图。
4. **布局**：建造者动态和 GitHub Trending 都用 `vlist-2col` 双列瀑布流。
5. **卡片**：推文卡片（`.tweet-card`）、GitHub 卡片（`.gh-card`）、RSS 卡片（`.rss-card`）都是 `<a>` 标签整卡可点击，无底部分离链接。
6. **vitem 透明化**：`.vitem:has(.tweet-card),.vitem:has(.gh-card),.vitem:has(.rss-card)` 自动去掉背景/边框/内边距，无双层边框。
7. **禁止嵌套 `<a>`**：`esc()` 只做 HTML 实体转义，不 linkify URL。
8. **无 ALL-CAPS**：`label-sm`、`section-label` 等不使用全大写。
9. **首页 Featured Card**：`docs/index.html` 的深度报告区第一条必须用 `class="featured-card"`，禁止改成 `daily-entry`。有 `<!-- FEATURED-CARD-START -->` / `<!-- FEATURED-CARD-END -->` 守卫注释，不可删除。

## 日报 HTML 结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>日报标题</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../styles.css">
  <!-- inline styles for header/nav/etc -->
</head>
<body>
  <!-- header nav -->
  <main class="container main-grid">
    <section class="card span-4"><!-- 今日洞察 --></section>
    <section class="card span-4"><!-- 深度对话 --></section>
    <section class="card span-4"><!-- RSS 精选（如有当日更新） --></section>
    <section class="card span-4"><!-- 建造者动态 --></section>
    <section class="card span-4"><!-- GitHub Trending --></section>
    <section class="card span-4"><!-- 今日思考 --></section>
  </main>
  <!-- footer -->
</body>
</html>
```

## 设计系统变量

```css
--accent: #2563eb;           /* Electric Blue */
--bg-primary: #f5f5f4;       /* 页面背景 */
--bg-secondary: #fafaf8;     /* 卡片底色（暖白） */
--text-primary: #1c1c1c;
--text-secondary: #4a4a4a;
--text-muted: #8b8b8b;
--border: #e8e8e6;
--radius-sm: 12px;           /* 实际卡片 border-radius 用 12px */
```

## 卡片 HTML 规范

### 推文卡片（建造者动态）

```html
<div class="vitem">
  <a href="https://x.com/{handle}/status/{tweet_id}" target="_blank" class="tweet-card">
    <div class="tweet-header">
      <img class="tweet-avatar" src="{avatar}" alt="" loading="lazy">
      <div class="tweet-author">
        <span class="tweet-name">{name}</span>
        <span class="tweet-handle">@{handle}</span>
      </div>
      <span class="tweet-date">{相对时间}</span>
    </div>
    <div class="tweet-body">{原文 — URL 纯文本，不加 <a>}</div>
    <div class="tweet-translation">{中文翻译}</div>
    <!-- 仅当有媒体时 -->
    <div class="tweet-media"><img src="assets/tweet_{id}.jpg" alt="" loading="lazy"></div>
    <div class="tweet-metrics">
      <span>♥ {favorites}</span>
      <span>↺ {retweets}</span>
      <span>💬 {replies}</span>
    </div>
  </a>
</div>
```

关键 CSS（已在 styles.css 中）：
- `.tweet-card`: `display:block`, hover 微阴影
- `.tweet-translation`: 灰底 + 蓝色左边线, 12px
- `.tweet-card` 内禁止嵌套 `<a>` — URL 只做纯文本

### GitHub 仓库卡片

```html
<div class="vitem">
  <a href="https://github.com/{owner}/{repo}" target="_blank" class="gh-card">
    <div class="gh-header">
      <img class="gh-avatar" src="{avatar_url}" alt="" loading="lazy">
      <div class="gh-repo">
        <span class="gh-owner">{owner}</span><span class="gh-sep">/</span><span class="gh-name">{repo}</span>
      </div>
      <span class="gh-stars">⭐ {stars}</span>
    </div>
    <div class="gh-body">{description}</div>
    <div class="gh-translation">{中文描述}</div>
    <div class="gh-meta">
      <span class="gh-lang">● {language}</span>
      <span class="gh-forks">🍴 {forks}</span>
      <span class="gh-topics"><span class="gh-topic">{topic}</span></span>
    </div>
  </a>
</div>
```

### RSS 卡片

```html
<div class="vitem">
  <a href="{link}" target="_blank" class="rss-card">
    <div class="rss-header">
      <span class="rss-source">{source}</span>
      <span class="rss-date">{MM-DD HH:MM}</span>
    </div>
    <div class="rss-title">{title}</div>
    <div class="rss-desc">{description}</div>
  </a>
</div>
```

## 卡片生成脚本（执行顺序）

生成 HTML 后，按序运行这些脚本将占位卡片替换为完整卡片：

```bash
# 1. RSS（如有当日更新）
python3 scripts/gen_rss_cards.py docs/daily/ai-news-YYYY-MM-DD.html

# 2. 推文双语卡片
python3 scripts/gen_tweet_cards.py docs/daily/ai-news-YYYY-MM-DD.html \
  --translations /tmp/tweet-trans-YYYYMMDD.json

# 3. GitHub 仓库卡片
python3 scripts/gen_gh_cards.py docs/daily/ai-news-YYYY-MM-DD.html \
  --translations /tmp/gh-trans-YYYYMMDD.json
```

## 推送前检查

```bash
bash .github/style-check.sh .
```

如门禁失败且确认是预存问题（非本次改动引起），用：
```bash
git push --no-verify origin main
```

## 注意事项

- 不修改建造者动态、GitHub Trending、RSS 精选以外的内容
- 保持 vlist-2col 布局不变
- 不要用 ALL-CAPS（text-transform 或全大写文本）
- read_file 输出含行号时，务必 strip 所有 `NN|` 前缀再嵌入 HTML
- 无媒体时不硬塞图 — 建造者动态至少 20% 有图，但无媒体源不强求
- 主页 index.html 的「今日日报」链接同步更新
