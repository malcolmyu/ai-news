任务：改写 ai-news 日报 2026-06-04 的「建造者动态」板块，将纯文本推文摘要改为展现 Twitter 推文卡片。

## 背景
当前 `docs/daily/ai-news-2026-06-04.html` 的建造者动态区用纯文本 vitem 展示 15 条推文，每条只有标题+摘要+链接。用户希望展示更丰富的推文嵌入卡片。

## 数据源
- 推文 URL 格式: `https://x.com/{screen_name}/status/{tweet_id}`
- 数据 API: `https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&token=0`
- API 返回 JSON，包含: text, user.name, user.screen_name, user.profile_image_url_https, favorite_count, retweet_count, conversation_count, created_at, entities.media, photos
- 如果 API 失败（/非 200），回退到当前纯文本格式

## 需要修改的文件

### 1. docs/styles.css — 追加推文卡片样式

在文件末尾追加以下 CSS（不要删除已有内容）：

```css
/* Tweet Card */
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
  width: 36px; height: 36px;
  border-radius: 50%;
  flex-shrink: 0;
}
.tweet-author { flex: 1; min-width: 0; }
.tweet-name { font-weight: 600; font-size: 13px; color: var(--text-primary); display: block; line-height: 1.3; }
.tweet-handle { font-size: 12px; color: var(--text-muted); }
.tweet-date { font-size: 12px; color: var(--text-muted); flex-shrink: 0; }
.tweet-body { margin-bottom: 8px; color: var(--text-primary); white-space: pre-wrap; word-break: break-word; }
.tweet-body a { color: var(--accent); text-decoration: none; }
.tweet-media { margin-bottom: 8px; border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }
.tweet-media img { width: 100%; height: auto; display: block; max-height: 300px; object-fit: cover; }
.tweet-metrics { display: flex; gap: 16px; font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
.tweet-link { font-size: 12px; color: var(--accent); text-decoration: none; }
.tweet-link:hover { text-decoration: underline; }
```

### 2. docs/daily/ai-news-2026-06-04.html — 替换建造者动态区

从 `<div class="label-sm">建造者动态</div>` 到下一个 `</section>` 之前的所有 vitem 内容替换。

当前 HTML 中是 15 个纯文本 vitem，例如：
```html
<div class="vitem">
  <div class="vitem-title">Josh Woodward · OpenAI Codex</div>
  <div class="vitem-desc">分享了 Codex 最新采用数据...</div>
  <div class="vitem-actions"><a href="https://x.com/joshwoodward/status/2061870160315884010" ...>查看原文 →</a></div>
</div>
```

替换为推文卡片格式：
```html
<div class="vitem">
  <div class="tweet-card">
    <div class="tweet-header">
      <img class="tweet-avatar" src="{avatar}" alt="">
      <div class="tweet-author">
        <span class="tweet-name">{name}</span>
        <span class="tweet-handle">@{handle}</span>
      </div>
      <span class="tweet-date">{date}</span>
    </div>
    <div class="tweet-body">{text with links}</div>
    <!-- 如果有媒体图片 -->
    <div class="tweet-media"><img src="{local_media_path}" alt="" loading="lazy"></div>
    <div class="tweet-metrics">
      <span>♥ {favs}</span> <span>↺ {rts}</span> <span>💬 {replies}</span>
    </div>
    <a href="https://x.com/{handle}/status/{id}" target="_blank" class="tweet-link">在 X 上查看</a>
  </div>
</div>
```

### 3. 媒体图片处理

推文中的图片下载到 `docs/daily/assets/tweet_{tweet_id}.jpg`：
- 从 API JSON 的 `photos[0].url` 或 `entities.media[0].media_url_https` 获取
- PIL 压缩：等比缩放到宽度 ≤1200px，quality=92，文件 ≤500KB
- 如果推文无媒体，不渲染 `.tweet-media` div
- 如果没有 photos 但有 `video` 类型 media，用 `media_url_https`（视频缩略图）

### 4. 时间处理

将 `created_at`（如 "Wed Jun 04 18:03:50 +0000 2025"）转为相对时间：
- 同一天 → 显示时间（如 "18:03"）
- 昨天 → "昨天"
- 其他 → "M月D日"

### 5. 文本处理

- 推文正文中的 URL 转为 `<a>` 链接
- @mention 保留纯文本（不必转链接，减少视觉噪点）
- 换行保留（用 white-space: pre-wrap）

## 验证
- 运行 `.github/style-check.sh` 检查
- 浏览器打开 `docs/daily/ai-news-2026-06-04.html` 确认建造者动态显示正常
- 注意：不要修改建造者动态以外的任何内容（标题、深度对话、RSS、GitHub Trending、参考来源等）
