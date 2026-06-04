# 推文卡片嵌入规范

日报建造者动态区的推文展示为带头像/正文/中文翻译/媒体/互动数据的双语卡片。整张卡片可点击跳转到推文原文。

## 数据源

```
API: https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&token=***
返回: {text, user: {name, screen_name, profile_image_url_https}, 
       favorite_count, retweet_count, conversation_count, created_at,
       photos: [{url}], entities: {media: [{type, media_url_https}]}}
```

API 失败时回退到纯文本 vitem 格式。

## 双语支持

推文卡片支持原文 + 中文翻译双行显示。翻译通过 `--translations` 参数传入 JSON 文件：

```json
{"tweet_id": "中文翻译文本", ...}
```

脚本调用：
```bash
python3 scripts/gen_tweet_cards.py docs/daily/ai-news-YYYY-MM-DD.html --translations /tmp/tweet-trans-YYYYMMDD.json
```

## 卡片 HTML

整张卡片是 `<a>` 标签，点击跳转到推文原文。卡片内不嵌套链接，URL 显示为纯文本。

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
    <div class="tweet-body">{原文 — URL 纯文本，不加链接}</div>
    <div class="tweet-translation">{中文翻译}</div>
    <div class="tweet-media"><img src="assets/tweet_{id}.jpg" alt="" loading="lazy"></div>
    <div class="tweet-metrics">
      <span>♥ {favorite_count}</span>
      <span>↺ {retweet_count}</span>
      <span>💬 {conversation_count}</span>
    </div>
  </a>
</div>
```

关键点：
- `.tweet-card` 是 `<a>` 标签，`display:block` 全卡可点击
- `esc()` 只做 HTML 实体转义，不 linkify URL — 避免嵌套 `<a>`
- 无底部分离链接 — 整卡即链接

## CSS

```css
.tweet-card{display:block;background:#fff;border:1px solid var(--border);border-radius:12px;padding:14px 16px;font-size:13px;line-height:1.5;text-decoration:none;color:inherit;cursor:pointer;transition:border-color .15s,box-shadow .15s}
.tweet-card:hover{border-color:#c4c4c0;box-shadow:0 2px 8px rgba(28,28,28,.06)}
.tweet-header{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.tweet-avatar{width:36px;height:36px;border-radius:50%;flex-shrink:0}
.tweet-author{flex:1;min-width:0}
.tweet-name{font-weight:600;font-size:13px;color:var(--text-primary);display:block;line-height:1.3}
.tweet-handle{font-size:12px;color:var(--text-muted)}
.tweet-date{font-size:12px;color:var(--text-muted);flex-shrink:0}
.tweet-body{margin-bottom:8px;color:var(--text-primary);white-space:pre-wrap;word-break:break-word}
.tweet-translation{padding:8px 10px;margin-bottom:8px;background:#f3f4f6;border-radius:8px;color:#4b5563;font-size:12px;line-height:1.65;white-space:pre-wrap;word-break:break-word;border-left:3px solid var(--accent)}
.tweet-media{margin-bottom:8px;border-radius:12px;overflow:hidden;border:1px solid var(--border)}
.tweet-media img{width:100%;height:auto;display:block;max-height:300px;object-fit:cover}
.tweet-metrics{display:flex;gap:16px;font-size:12px;color:var(--text-muted);margin-bottom:6px}
```

Hover: 边框变深 + 微阴影。

## 图片处理

- 路径：`docs/daily/assets/tweet_{tweet_id}.jpg`
- 从 API JSON 的 `photos[0].url` 或 `entities.media[0].media_url_https` 获取
- PIL 压缩：等比缩放宽度 ≤1200px，JPEG quality=92，目标 ≤500KB
- 无媒体时不渲染 `.tweet-media` div
- 已存在本地文件时跳过下载（幂等）

## 时间格式

created_at → 同一天 HH:MM / 昨天 / M月D日

## 文本处理

- HTML 实体转义（& < >）
- **不 linkify URL** — 整卡可点击，内嵌 `<a>` 是非法 HTML
- 保留换行（white-space: pre-wrap）

## Codex 工作流

1. 生成原始日报 HTML（建造者动态区放占位链接）
2. 翻译所有推文 → `/tmp/tweet-trans-YYYYMMDD.json`
3. `python3 scripts/gen_tweet_cards.py <path> --translations /tmp/tweet-trans-YYYYMMDD.json`
4. `python3 scripts/gen_gh_cards.py <path> --translations /tmp/gh-trans-YYYYMMDD.json`
5. `bash .github/style-check.sh .`
6. 提交推送

## 注意事项

- 不修改建造者动态以外的任何内容
- 保持 vlist-2col 布局
- 卡片内禁止嵌套 `<a>` 标签
- `esc()` 只转义，不 linkify
