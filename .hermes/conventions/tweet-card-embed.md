# 推文卡片嵌入规范

日报建造者动态区的推文展示从纯文本升级为带头像/正文/中文翻译/媒体/互动数据的双语卡片。

## 数据源

```
API: https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&token=***
返回: {text, user: {name, screen_name, profile_image_url_https}, 
       favorite_count, retweet_count, conversation_count, created_at,
       photos: [{url}], entities: {media: [{type, media_url_https}]}}
```

API 失败时回退到纯文本 vitem 格式（保持 vitem-title + vitem-desc + vitem-actions）。

## 双语支持

推文卡片支持原文 + 中文翻译双行显示。翻译通过 `--translations` 参数传入 JSON 文件：

```json
{"tweet_id": "中文翻译文本", ...}
```

脚本调用方式：
```bash
python3 scripts/gen_tweet_cards.py docs/daily/ai-news-YYYY-MM-DD.html --translations /tmp/trans.json
```

`--translations` 可选，不传则只显示原文（向后兼容）。

## 卡片 HTML

```html
<div class="vitem">
  <div class="tweet-card">
    <div class="tweet-header">
      <img class="tweet-avatar" src="{avatar}" alt="" loading="lazy">
      <div class="tweet-author">
        <span class="tweet-name">{name}</span>
        <span class="tweet-handle">@{handle}</span>
      </div>
      <span class="tweet-date">{相对时间}</span>
    </div>
    <div class="tweet-body">{原文}</div>
    <!-- 有翻译时渲染 -->
    <div class="tweet-translation">{中文翻译}</div>
    <!-- 仅当推文有媒体时 -->
    <div class="tweet-media"><img src="assets/tweet_{tweet_id}.jpg" alt="" loading="lazy"></div>
    <div class="tweet-metrics">
      <span>♥ {favorite_count}</span>
      <span>↺ {retweet_count}</span>
      <span>💬 {conversation_count}</span>
    </div>
    <a href="https://x.com/{handle}/status/{tweet_id}" target="_blank" class="tweet-link">在 X 上查看</a>
  </div>
</div>
```

## CSS（追加到 docs/styles.css 末尾）

```css
.tweet-card{background:#fff;border:1px solid var(--border);border-radius:12px;padding:14px 16px;font-size:13px;line-height:1.5}
.tweet-header{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.tweet-avatar{width:36px;height:36px;border-radius:50%;flex-shrink:0}
.tweet-author{flex:1;min-width:0}
.tweet-name{font-weight:600;font-size:13px;color:var(--text-primary);display:block;line-height:1.3}
.tweet-handle{font-size:12px;color:var(--text-muted)}
.tweet-date{font-size:12px;color:var(--text-muted);flex-shrink:0}
.tweet-body{margin-bottom:8px;color:var(--text-primary);white-space:pre-wrap;word-break:break-word}
.tweet-body a{color:var(--accent);text-decoration:none}
.tweet-translation{padding:8px 10px;margin-bottom:8px;background:#f3f4f6;border-radius:8px;color:#4b5563;font-size:12px;line-height:1.65;white-space:pre-wrap;word-break:break-word;border-left:3px solid var(--accent)}
.tweet-media{margin-bottom:8px;border-radius:12px;overflow:hidden;border:1px solid var(--border)}
.tweet-media img{width:100%;height:auto;display:block;max-height:300px;object-fit:cover}
.tweet-metrics{display:flex;gap:16px;font-size:12px;color:var(--text-muted);margin-bottom:6px}
.tweet-link{font-size:12px;color:var(--accent);text-decoration:none}
.tweet-link:hover{text-decoration:underline}
```

`.tweet-translation` 样式要点：
- 浅灰背景 `#f3f4f6`，左侧蓝色 accent 竖线区分原文
- 字号 12px，比原文（13px）小一号
- 保留换行和 URL 链接（与原文一致，通过 esc() 处理）

## 图片处理

- 路径：`docs/daily/assets/tweet_{tweet_id}.jpg`
- 从 API JSON 的 `photos[0].url` 或 `entities.media[0].media_url_https` 获取
- PIL 压缩：等比缩放宽度 ≤1200px，JPEG quality=92，目标 ≤500KB
- 无媒体时不渲染 `.tweet-media` div
- 已存在本地文件时跳过下载（幂等）

## 时间格式

created_at 如 "Wed Jun 04 18:03:50 +0000 2025" 转为：
- 同一天 → HH:MM
- 昨天 → "昨天"
- 其他 → "M月D日"

## 文本处理

- 推文正文中的 URL 转为 `<a>` 链接
- HTML 实体转义（& < >）
- 保留换行（white-space: pre-wrap）
- 中文翻译同样经过 esc() 转义和 URL 链接化

## Codex 工作流

日报生成时，Hermes 主控流程：
1. 生成原始日报 HTML（建造者动态区放占位链接）
2. 翻译所有推文 → 写入 `/tmp/tweet-trans-YYYYMMDD.json`
3. 运行 `python3 scripts/gen_tweet_cards.py <path> --translations /tmp/tweet-trans-YYYYMMDD.json`
4. 运行 `.github/style-check.sh` 验证
5. 提交推送

## 注意事项

- 不要修改建造者动态以外的任何内容
- 保持 vlist-2col 瀑布流布局不变
- 提交前运行 `.github/style-check.sh`
- 执行完立即推送
