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

- Accent: `#2563eb` (blue)
- Background: `#f5f5f4` (warm stone)
- Card background: `#ffffff`
- Text primary: `#1c1c1c`, secondary: `#6b6b6b`, muted: `#8b8b8b`
- Border: `#e8e8e6`
- Card border-radius: 14px
- Font: Inter only (weights 300/400/500/600)
- Shared stylesheet: `docs/styles.css`

### Homepage Daily Entries

- Production rule: the homepage Daily section renders exactly the 3 most recent daily entries, followed by the `历史日报` archive row.

### Older Style (thinking/ pages, homepage.html)

- Accent: `#3b82f6` (blue)
- Uses JetBrains Mono alongside Inter
- CSS custom properties with different naming

## Directory Conventions

```
docs/
  styles.css              — shared bento design system
  search.js               — Pagefind search modal and search UI behavior
  site.js                 — shared page interactions: masonry, image lightbox, legacy galleries
  index.html              — homepage
  agents/
    README.md                — project-local production skill ownership notes
    skills/                  — Hermes skills copied into the repo and modernized for this site
  daily/
    ai-news-YYYY-MM-DD.html  — daily reports
    data/YYYY-MM-DD.json     — Daily Source JSON (canonical input for render pipeline)
    assets/YYYY-MM-DD/       — media assets per day
    archive.html             — daily archive index
  research/
    *.html                   — research reports
    screenshots/             — research screenshots
    archive.html             — research archive index
  thinking/
    *.html                   — thinking model pages
scripts/
  python.sh                   — Python runtime resolver for harness scripts
  fetch-daily-media.sh       — download X/Twitter images + YouTube thumbnails
  generate-daily-html.sh     — URL extraction to HTML embed pipeline
  site_harness.py            — content index, homepage/archive generation, structural validation
  update-homepage.py         — compatibility wrapper for homepage generation
.github/
  style-check.sh             — pre-deployment integrity + style check
  workflows/pages.yml        — GitHub Pages deploy on push
```

## Agent Production Skills

Project-local skill source of truth lives in `docs/agents/skills/`.

- `ai-news-research-report` defines the research report and daily page production workflow, updated for shared `docs/styles.css`, `scripts/site_harness.py`, Pagefind, and browser validation.
- `daily-digest-media-fetch` defines X/Twitter + YouTube media fetching, image compression, intrinsic image dimensions, and masonry-friendly Builder card markup.

Global Hermes skills may delegate the work, but Codex should execute repository changes according to these project-local versions.

The harness architecture is documented in `docs/agents/architecture.md`; the architecture decision is captured in `docs/adr/0002-hermes-codex-production-harness.md`.

## Key Terms

- **Builder** — someone building at the frontier of AI (founders, researchers, engineers), tracked in daily digests
- **Bento** — the grid-based card layout used for daily/research content; 4-column grid at desktop, 2 at tablet, 1 at mobile
- **nav-back** — retired "← 返回首页" navigation pattern; current pages should use the shared header/search shell
- **数字分身** — "digital avatar", the framing for the entire site as a persistent AI-powered presence
- **Daily Source** — `docs/daily/data/YYYY-MM-DD.json`; canonical structured input for the Daily Digest render pipeline (hero, sections by `kind`/`layout`, optional `sources`)
