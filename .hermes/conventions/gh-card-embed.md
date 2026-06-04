# GitHub 仓库卡片嵌入规范

日报 GitHub Trending 区从普通 vitem 升级为带头像/描述/中文翻译/语言/Topics/Star 数的卡片。

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

脚本调用方式：
```bash
python3 scripts/gen_gh_cards.py docs/daily/ai-news-YYYY-MM-DD.html --translations /tmp/gh-trans-YYYYMMDD.json
```

`--translations` 可选，不传则只显示原文。

## 卡片 HTML

```html
<div class="vitem">
  <div class="gh-card">
    <div class="gh-header">
      <img class="gh-avatar" src="{avatar_url}" alt="" loading="lazy">
      <div class="gh-repo">
        <span class="gh-owner">{owner}</span><span class="gh-sep">/</span><span class="gh-name">{repo}</span>
      </div>
      <span class="gh-stars">⭐ {stars}</span>
    </div>
    <div class="gh-body">{description}</div>
    <!-- 有翻译时渲染 -->
    <div class="gh-translation">{中文描述}</div>
    <div class="gh-meta">
      <span class="gh-lang">● {language}</span>
      <span class="gh-forks">🍴 {forks}</span>
      <span class="gh-topics"><span class="gh-topic">{topic}</span>...</span>
    </div>
    <a href="https://github.com/{owner}/{repo}" target="_blank" class="gh-link">查看仓库 →</a>
  </div>
</div>
```

## CSS（追加到 docs/styles.css）

```css
.gh-card{background:#fff;border:1px solid var(--border);border-radius:12px;padding:14px 16px;font-size:13px;line-height:1.5}
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
.gh-link{font-size:12px;color:var(--accent);text-decoration:none}
.gh-link:hover{text-decoration:underline}
```

## 数字格式化

- star/fork 数 ≥1000 时显示为 `1.2k` / `23.4k`
- Topics 最多显示 4 个

## Codex 工作流

日报生成时，Hermes 主控流程：
1. 生成原始日报 HTML（GitHub Trending 区放占位 vitem 或链接）
2. 翻译所有仓库描述 → 写入 `/tmp/gh-trans-YYYYMMDD.json`
3. 运行 `python3 scripts/gen_gh_cards.py <path> --translations /tmp/gh-trans-YYYYMMDD.json`
4. 运行 `python3 scripts/gen_tweet_cards.py <path> --translations /tmp/tweet-trans-YYYYMMDD.json`
5. 运行 `.github/style-check.sh` 验证
6. 提交推送

## 注意事项

- 不要修改 GitHub Trending 以外的任何内容
- 保持 vlist-2col 瀑布流布局不变
- GitHub API 公开访问 60 req/h，够用
- 提交前运行 `.github/style-check.sh`
- 执行完立即推送
