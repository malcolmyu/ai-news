# 建造者动态推文卡片 — 实现方案

## 数据源
- 每条推文 URL 格式: `https://x.com/{screen_name}/status/{tweet_id}`
- 数据 API: `https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&token=0`
  返回 JSON: `{text, user: {name, screen_name, profile_image_url_https}, favorite_count, retweet_count, conversation_count, created_at, entities: {media: [{media_url_https, type: "photo"|"video"}]}, photos: [{url}]}`

## 卡片 HTML 模板

每张卡片是一个独立的 `vitem`，内容为自定义推文卡片：

```html
<div class="tweet-card">
  <div class="tweet-header">
    <img class="tweet-avatar" src="{avatar_url}" alt="">
    <div class="tweet-author">
      <span class="tweet-name">{name}</span>
      <span class="tweet-handle">@{screen_name}</span>
    </div>
    <span class="tweet-date">{相对时间}</span>
  </div>
  <div class="tweet-body">{text with t.co links expanded and @mentions styled}</div>
  <!-- 如果有媒体 -->
  <div class="tweet-media">
    <img src="{media_url}" alt="" loading="lazy">
  </div>
  <div class="tweet-metrics">
    <span>♥ {favorite_count}</span>
    <span>↺ {retweet_count}</span>
    <span>💬 {conversation_count}</span>
  </div>
  <a href="{tweet_url}" target="_blank" class="tweet-link">在 X 上查看</a>
</div>
```

## CSS 样式（添加到 styles.css）

```css
.tweet-card {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 16px;
  font-size: 13px;
  line-height: 1.5;
}

.tweet-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.tweet-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tweet-author {
  flex: 1;
  min-width: 0;
}

.tweet-name {
  font-weight: 600;
  font-size: 13px;
  color: var(--text-primary);
  display: block;
  line-height: 1.3;
}

.tweet-handle {
  font-size: 12px;
  color: var(--text-muted);
}

.tweet-date {
  font-size: 12px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.tweet-body {
  margin-bottom: 8px;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.tweet-body a {
  color: var(--accent);
  text-decoration: none;
}

.tweet-media {
  margin-bottom: 8px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border);
}

.tweet-media img {
  width: 100%;
  height: auto;
  display: block;
  max-height: 300px;
  object-fit: cover;
}

.tweet-metrics {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.tweet-link {
  font-size: 12px;
  color: var(--accent);
  text-decoration: none;
}

.tweet-link:hover {
  text-decoration: underline;
}
```

## Codex 任务

1. 写一个 Python 脚本 `fetch_tweet_cards.py`：
   - 接受一个 tweet URL 列表（每行一个）
   - 对每个 URL 提取 tweet_id，调用 `https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&token=0`
   - 解析 JSON，生成上述 HTML 卡片
   - 输出到标准输出，每张卡片一行 HTML

2. 修改 `docs/daily/ai-news-2026-06-04.html`：
   - 建造者动态区当前是纯文本 + 链接的 vitem
   - 替换为 fetch_tweet_cards.py 生成的推文卡片 HTML
   - 保持 vlist-2col 布局
   - 15 条推文的 tweet_id 从 HTML 中的 link href 提取

3. 压缩图片：推文中的媒体图片下载到本地 assets/，压缩到 1200px 宽 / q92 / ≤500KB

## 关键约束
- 所有样式内联或通过 styles.css 全局定义
- 卡片不要破坏现有的 vlist-2col 瀑布流
- 图片必须下载本地压缩，不能用外部 URL
- 推文正文中的 @mention 和 URL 需要转为链接
- 如果没有媒体（纯文本推文），不渲染 tweet-media div
- 如果 API 请求失败（404/超时），回退到当前纯文本 vitem 格式
