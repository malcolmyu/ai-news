# GitHub 仓库卡片嵌入规范

日报 GitHub Trending 区升级为带头像/描述/中文翻译/语言/Topics/Star 数的仓库卡片。整张卡片可点击跳转到仓库。

## 数据源

```
API: https://api.github.com/repos/{owner}/{repo}
Headers: Accept: application/vnd.github+json
返回: {owner: {avatar_url}, description, stargazers_count, forks_count,
       language, topics, homepage}
```

无需认证（公开 API，60 req/h）。API 失败时回退到原始 vitem 格式。

## 双语支持

仓库描述支持原文 + 中文翻译双行显示。翻译通过 `--translations` 参数传入 JSON 文件：

```json
{"owner/repo": "中文描述", ...}
```

脚本调用：
```bash
python3 scripts/gen_gh_cards.py --date YYYY-MM-DD --from-html docs/daily/ai-news-YYYY-MM-DD.html --translations /tmp/gh-trans-YYYYMMDD.json --render
```

Legacy HTML patch 已废弃。脚本现在 upsert `docs/daily/data/YYYY-MM-DD.json` 的 `github` section；加 `--render` 会调用 `render_daily.py` 把模板结果 merge 进日报 HTML。

## 卡片 HTML

整张卡片是 `<a>` 标签，点击跳转到仓库。卡片内不嵌套链接。

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
    <div class="gh-body">{description — URL 纯文本}</div>
    <div class="gh-translation">{中文描述}</div>
    <div class="gh-meta">
      <span class="gh-lang">● {language}</span>
      <span class="gh-forks">🍴 {forks}</span>
      <span class="gh-topics"><span class="gh-topic">{topic}</span>...</span>
    </div>
  </a>
</div>
```

关键点：
- `.gh-card` 是 `<a>` 标签，`display:block` 全卡可点击
- `esc()` 只做 HTML 实体转义，不 linkify URL
- 无底部分离链接

## CSS

```css
.gh-card{display:block;background:#fff;border:1px solid var(--border);border-radius:12px;padding:14px 16px;font-size:13px;line-height:1.5;text-decoration:none;color:inherit;cursor:pointer;transition:border-color .15s,box-shadow .15s}
.gh-card:hover{border-color:#c4c4c0;box-shadow:0 2px 8px rgba(28,28,28,.06)}
.gh-header{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.gh-avatar{width:28px;height:28px;border-radius:6px;flex-shrink:0}
.gh-repo{flex:1;min-width:0;font-size:13px;font-weight:600}
.gh-owner{color:var(--text-muted);font-weight:400}
.gh-sep{color:#c4c4c0;margin:0 1px}
.gh-name{color:var(--text-primary)}
.gh-stars{font-size:12px;font-weight:600;color:#2563eb;flex-shrink:0}
.gh-body{margin-bottom:6px;color:var(--text-primary);font-size:13px;line-height:1.55}
.gh-translation{padding:6px 10px;margin-bottom:6px;background:#f3f4f6;border-radius:8px;color:#4b5563;font-size:12px;line-height:1.65;border-left:3px solid var(--accent)}
.gh-meta{display:flex;align-items:center;gap:10px;flex-wrap:wrap;font-size:11px;color:var(--text-muted);margin-bottom:6px}
.gh-lang{font-weight:500}
.gh-topics{display:flex;gap:4px;flex-wrap:wrap}
.gh-topic{background:#eef2ff;color:#4338ca;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:500}
```

Hover: 边框变深 + 微阴影（与推文卡片一致）。

## 数字格式化

- star/fork 数 ≥1000 → `1.2k` / `23.4k`
- Topics 最多 4 个

## Codex 工作流

1. 生成原始日报 HTML（GitHub Trending 区放占位链接）
2. 翻译所有仓库描述 → `/tmp/gh-trans-YYYYMMDD.json`
3. `python3 scripts/gen_tweet_cards.py <path> --translations /tmp/tweet-trans-YYYYMMDD.json`
4. `python3 scripts/gen_gh_cards.py <path> --translations /tmp/gh-trans-YYYYMMDD.json`
5. `bash .github/style-check.sh .`
6. 提交推送

## 注意事项

- 不修改 GitHub Trending 以外的任何内容
- 保持 vlist-2col 布局
- 卡片内禁止嵌套 `<a>` 标签
- `esc()` 只转义，不 linkify
- GitHub API 公开访问 60 req/h，够用
- style-check.sh 目前用 `vitem-gallery` 检测图片，gh-card 格式不适用 — 后续需更新门禁
