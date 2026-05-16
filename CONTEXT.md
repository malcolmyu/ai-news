# CONTEXT

## Project Identity

**第二号** (Number Two) is a personal digital avatar — a hand-crafted static HTML site that publishes Chinese-language AI industry news and research. Deployed via GitHub Pages from `docs/`.

## Content Tracks

- **日报** (Daily Digest) — `docs/daily/ai-news-YYYY-MM-DD.html`. Daily AI news summaries tracking builders, podcasts, and GitHub trending repos. Uses bento grid layout.
- **深度调研** (Deep Research) — `docs/research/*.html`. Long-form architecture and trend analysis reports. Uses bento grid layout.
- **思维模型** (Thinking Models) — `docs/thinking/*.html`. Conceptual framework pages (cognition, communication, decision, product). Uses older visual style.
- **首页** (Homepage) — `docs/index.html`. Aggregates latest daily and research content.

## Design Conventions

### Bento Style (current standard)

- Accent: `#5e6ad2` (indigo)
- Background: `#f5f5f4` (warm stone)
- Card background: `#ffffff`
- Text primary: `#1c1c1c`, secondary: `#6b6b6b`, muted: `#8b8b8b`
- Border: `#e8e8e6`
- Card border-radius: 14px
- Font: Inter only (weights 300/400/500/600)
- Shared stylesheet: `docs/styles.css`

### Older Style (thinking/ pages, homepage.html)

- Accent: `#3b82f6` (blue)
- Uses JetBrains Mono alongside Inter
- CSS custom properties with different naming

## Directory Conventions

```
docs/
  styles.css              — shared bento design system
  index.html              — homepage
  daily/
    ai-news-YYYY-MM-DD.html  — daily reports
    assets/YYYY-MM-DD/       — media assets per day
    archive.html             — daily archive index
  research/
    *.html                   — research reports
    screenshots/             — research screenshots
    archive.html             — research archive index
  thinking/
    *.html                   — thinking model pages
scripts/
  fetch-daily-media.sh       — download X/Twitter images + YouTube thumbnails
  generate-daily-html.sh     — URL extraction to HTML embed pipeline
  update-homepage.py         — inject research section into homepage via markers
.github/
  style-check.sh             — pre-deployment integrity + style check
  workflows/pages.yml        — GitHub Pages deploy on push
```

## Key Terms

- **Builder** — someone building at the frontier of AI (founders, researchers, engineers), tracked in daily digests
- **Bento** — the grid-based card layout used for daily/research content; 4-column grid at desktop, 2 at tablet, 1 at mobile
- **nav-back** — the "← 返回首页" navigation pattern used on content pages
- **数字分身** — "digital avatar", the framing for the entire site as a persistent AI-powered presence
