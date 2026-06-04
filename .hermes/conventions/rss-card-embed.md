# RSS 精选规范

日报 RSS 精选板块从 feeds.json 配置的 RSS 源拉取最新文章，生成整卡可点击的 vitem 卡片。

## 数据源

`feeds.json` 配置 RSS 源：

```json
{
  "feeds": [
    {"name": "宝玉的博客", "url": "https://baoyu.io/feed.xml", "lang": "zh"},
    {"name": "Tw93", "url": "https://tw93.fun/feed.xml", "lang": "zh"},
    {"name": "AIGC Weekly", "url": "https://aigc-weekly.agi.li/rss.xml", "lang": "zh"}
  ]
}
```

## 脚本调用

```bash
python3 scripts/gen_rss_cards.py docs/daily/ai-news-YYYY-MM-DD.html
```

自动：
1. 读取 feeds.json
2. 拉取所有 RSS 源
3. 每源取最新 2 篇文章
4. 去重已存在的 RSS 区块
5. 插入到"建造者动态"之前

## 卡片 HTML

整卡可点击，无底部分离链接。

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

## CSS

```css
.rss-card{display:block;background:#fff;border:1px solid var(--border);border-radius:12px;padding:14px 16px;font-size:13px;line-height:1.5;text-decoration:none;color:inherit;cursor:pointer;transition:border-color .15s,box-shadow .15s}
.rss-card:hover{border-color:#c4c4c0;box-shadow:0 2px 8px rgba(28,28,28,.06)}
.rss-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:6px}
.rss-source{font-size:11px;font-weight:500;color:var(--accent);background:#eef2ff;padding:2px 8px;border-radius:20px}
.rss-date{font-size:11px;color:var(--text-muted)}
.rss-title{font-size:13px;font-weight:600;color:var(--text-primary);line-height:1.5;margin-bottom:4px}
.rss-desc{font-size:12px;color:#4a4a4a;line-height:1.55}
```

## 日期解析

支持三种格式：
1. RFC 2822：`Sat, 23 May 2026 00:00:00 GMT`
2. ISO 8601：`2026-05-23T00:00:00Z`
3. ISO date only：`2026-05-01`

## 注意事项

- **ElementTree 的 `Element` 是 falsy 的**！不要用 `element or fallback`，必须用 `if element is None`
- 每源限制 2 篇，全源按日期倒序排列
- `vitem:has(.rss-card)` 自动透明化，无双层边框
- 如无 RSS 更新，不插入区块
- WeChat 公众号无原生 RSS，需通过 RSSHub 或手动补充

## Codex 工作流

日报生成时按序执行：
1. `python3 scripts/gen_rss_cards.py <path>`
2. `python3 scripts/gen_tweet_cards.py <path> --translations /tmp/tweet-trans-YYYYMMDD.json`
3. `python3 scripts/gen_gh_cards.py <path> --translations /tmp/gh-trans-YYYYMMDD.json`
4. `bash .github/style-check.sh .`
5. 提交推送
