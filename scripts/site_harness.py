#!/usr/bin/env python3
"""Content index, render, and validation harness for the static site."""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
AGENTS_DIR = DOCS / "agents"
DAILY_DIR = DOCS / "daily"
RESEARCH_DIR = DOCS / "research"
INDEX = DOCS / "index.html"
ASSET_VERSION = "20260531d"

HOMEPAGE_DAILY_START = "<!-- HOMEPAGE-DAILY-START -->"
HOMEPAGE_DAILY_END = "<!-- HOMEPAGE-DAILY-END -->"
HOMEPAGE_RESEARCH_START = "<!-- HOMEPAGE-RESEARCH-START -->"
HOMEPAGE_RESEARCH_END = "<!-- HOMEPAGE-RESEARCH-END -->"


@dataclass(frozen=True)
class ContentItem:
    track: str
    path: Path
    href: str
    title: str
    display_title: str
    date: datetime
    summary: str
    category: str = ""

    @property
    def iso_date(self) -> str:
        return self.date.strftime("%Y-%m-%d")

    @property
    def short_date(self) -> str:
        return f"{self.date.month}月{self.date.day}日"

    @property
    def slash_date(self) -> str:
        return f"{self.date.year}/{self.date.month}/{self.date.day}"

    @property
    def chinese_date(self) -> str:
        return f"{self.date.year}年{self.date.month}月{self.date.day}日"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def strip_tags(value: str) -> str:
    value = re.sub(r"<script\b.*?</script>", "", value, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", "", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", "", value)
    return html.unescape(re.sub(r"\s+", " ", value)).strip()


def match_text(pattern: str, content: str) -> str:
    m = re.search(pattern, content, flags=re.I | re.S)
    return strip_tags(m.group(1)) if m else ""


def match_attr(pattern: str, content: str) -> str:
    m = re.search(pattern, content, flags=re.I | re.S)
    return html.unescape(m.group(1)).strip() if m else ""


def clean_title(value: str) -> str:
    value = value.replace(" - 第二号", "").replace(" — 第二号", "")
    value = value.replace("AI 日报", "").strip(" -—·")
    return value.strip()


def is_useful_summary(value: str) -> bool:
    value = value.strip()
    if len(value) < 6:
        return False
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    if re.fullmatch(r"\d+\s*篇文章\s*·\s*AI 日报", value):
        return False
    return True


def extract_news_summary(content: str) -> str:
    titles = [
        strip_tags(title)
        for title in re.findall(r'<h3[^>]*class=["\'][^"\']*news-title[^"\']*["\'][^>]*>(.*?)</h3>', content, flags=re.I | re.S)
    ]
    titles = [title for title in titles if title]
    if titles:
        return " + ".join(titles[:3])
    return ""


def git_first_commit_ts(path: Path) -> int:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(ROOT), "log", "--diff-filter=A", "--format=%ct", "--", str(path)],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return int(out.strip().split("\n")[-1])
    except (subprocess.CalledProcessError, ValueError, IndexError):
        return 0


def parse_meta_date(content: str, path: Path) -> datetime:
    raw = match_attr(r'<meta[^>]*name=["\']date["\'][^>]*content=["\']([^"\']+)["\']', content)
    if raw:
        return datetime.strptime(raw, "%Y-%m-%d")

    filename_date = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
    if filename_date:
        return datetime.strptime(filename_date.group(1), "%Y-%m-%d")

    ts = git_first_commit_ts(path) or path.stat().st_mtime
    return datetime.fromtimestamp(ts)


def first_summary(content: str, fallback: str) -> str:
    selectors = [
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
        r'<div[^>]*class=["\'][^"\']*subtitle[^"\']*["\'][^>]*>(.*?)</div>',
        r'<p[^>]*class=["\'][^"\']*featured-desc[^"\']*["\'][^>]*>(.*?)</p>',
        r'<div[^>]*class=["\'][^"\']*archive-meta[^"\']*["\'][^>]*>(.*?)</div>',
        r'<div[^>]*class=["\'][^"\']*text-body[^"\']*["\'][^>]*>(.*?)</div>',
    ]
    for pattern in selectors:
        value = match_attr(pattern, content) if "content=" in pattern else match_text(pattern, content)
        if value and is_useful_summary(value):
            return value[:180]
    news_summary = extract_news_summary(content)
    if news_summary:
        return news_summary[:180]
    return fallback


def extract_item(track: str, path: Path) -> ContentItem:
    content = read_text(path)
    title = match_text(r"<title>(.*?)</title>", content)
    h1 = match_text(r"<h1[^>]*>(.*?)</h1>", content)
    display_title = clean_title(h1 or title or path.stem)
    page_title = clean_title(title or display_title)
    date = parse_meta_date(content, path)
    summary = first_summary(content, display_title)
    category = match_attr(r'<meta[^>]*(?:name|property)=["\']category["\'][^>]*content=["\']([^"\']+)["\']', content)
    if not category and track == "research":
        category = "深度调研"
    href = f"{track}/{path.name}" if track == "daily" else f"research/{path.name}"
    return ContentItem(track, path, href, page_title, display_title, date, summary, category)


def load_daily_items() -> list[ContentItem]:
    items = [extract_item("daily", path) for path in DAILY_DIR.glob("ai-news-*.html")]
    return sorted(items, key=lambda item: item.date, reverse=True)


def load_research_items() -> list[ContentItem]:
    items = [
        extract_item("research", path)
        for path in RESEARCH_DIR.glob("*.html")
        if path.name != "archive.html"
    ]
    return sorted(items, key=lambda item: item.date, reverse=True)


def archive_overrides(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    content = read_text(path)
    overrides: dict[str, dict[str, str]] = {}
    for block in re.findall(r'<a\s+href=["\']([^"\']+\.html)["\'][^>]*class=["\'][^"\']*archive-item[^"\']*["\'][^>]*>(.*?)</a>', content, flags=re.I | re.S):
        href, body = block
        values: dict[str, str] = {}
        summary = match_text(r'<div[^>]*class=["\'][^"\']*archive-meta[^"\']*["\'][^>]*>(.*?)</div>', body)
        if summary and is_useful_summary(summary):
            values["summary"] = summary
        category_matches = re.findall(r'<div[^>]*color:var\(--text-secondary\)[^>]*>(.*?)</div>', body, flags=re.I | re.S)
        if category_matches:
            category = strip_tags(category_matches[-1])
            if category:
                values["category"] = category
        if values:
            overrides[href] = values
    return overrides


def e(value: str) -> str:
    return html.escape(value, quote=True)


def search_assets(prefix: str) -> str:
    return f"""<link rel="stylesheet" href="{prefix}pagefind/pagefind-ui.css">
<script src="{prefix}pagefind/pagefind-ui.js" defer></script>
<script src="{prefix}search.js?v={ASSET_VERSION}" defer></script>"""


def header(prefix: str, daily_href: str, research_href: str) -> str:
    return f"""<header class="header" data-pagefind-ignore>
<div class="container">
<div class="header-inner">
<a href="{prefix}index.html" class="logo">
<div class="logo-icon">🤖</div>
<span class="logo-text">第二号</span>
</a>
<nav class="nav">
<a href="{prefix}index.html" class="nav-link">首页</a>
<a href="{daily_href}" class="nav-link">AI 日报</a>
<a href="{research_href}" class="nav-link">深度调研</a>
</nav>
<button class="search-trigger" type="button" data-search-open aria-haspopup="dialog" aria-controls="search-modal">
<span class="search-trigger-icon">⌕</span>
<span class="search-trigger-label">Search</span>
<kbd>⌘K</kbd>
</button>
</div>
</div>
</header>"""


def search_modal() -> str:
    return """<div class="search-modal" id="search-modal" aria-hidden="true" data-pagefind-ignore>
<div class="search-modal-backdrop" data-search-close></div>
<div class="search-dialog" role="dialog" aria-modal="true" aria-labelledby="search-dialog-title">
<div class="search-dialog-head">
<div>
<div class="search-dialog-label">Search</div>
<h2 id="search-dialog-title">搜索第二号知识库</h2>
</div>
<button class="search-close" type="button" data-search-close aria-label="关闭搜索">×</button>
</div>
<div class="search-dialog-meta">
<span>AI 日报</span>
<span>深度调研</span>
<span>思维模型</span>
<span class="search-shortcut">Esc 关闭</span>
</div>
<div id="site-search" class="site-search"></div>
</div>
</div>"""


def footer() -> str:
    return """<footer style="padding:32px 0;border-top:1px solid var(--border);text-align:center;margin-top:48px;" data-pagefind-ignore>
<div class="container">
<p style="font-size:13px;color:var(--text-muted);">🤖 <strong>第二号</strong> — 把自己产品化 — 持续进化中</p>
</div>
</footer>"""


def page_shell(title: str, prefix: str, body: str, daily_href: str, research_href: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}styles.css?v={ASSET_VERSION}">
{search_assets(prefix)}
</head>
<body style="background:var(--bg-primary);">
{header(prefix, daily_href, research_href)}
{body}
{footer()}
{search_modal()}
</body>
</html>
"""


def render_reports_script(daily_items: list[ContentItem]) -> str:
    dates = [f"'{item.iso_date}'" for item in sorted(daily_items, key=lambda item: item.date)]
    lines = []
    for i in range(0, len(dates), 6):
        lines.append("  " + ",".join(dates[i : i + 6]))
    reports_literal = ",\n".join(lines)
    return f"""<script>
// Calendar — report dates from daily/ file listing
const REPORTS = [
{reports_literal}
];
const REPORT_SET = new Set(REPORTS);
const DAY_NAMES = ['一','二','三','四','五','六','日'];

function fmtDate(y,m,d){{return y+'-'+String(m+1).padStart(2,'0')+'-'+String(d).padStart(2,'0');}}
const MONTH_LABELS = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];

(function(){{
  let curYear, curMonth;
  const today = new Date();

  function renderCal() {{
    const grid = document.getElementById('cal-grid');
    const label = document.getElementById('cal-month-label');
    const count = document.getElementById('cal-count');
    if (!grid) return;

    label.textContent = curYear + '年 ' + MONTH_LABELS[curMonth];

    let monthCount = 0;
    for (const d of REPORTS) {{
      const p = d.split('-');
      if (+p[0] === curYear && +p[1] === curMonth+1) monthCount++;
    }}
    count.textContent = monthCount + ' 篇日报';

    const firstDay = new Date(curYear, curMonth, 1).getDay();
    const daysInMonth = new Date(curYear, curMonth+1, 0).getDate();
    const startOffset = firstDay === 0 ? 6 : firstDay - 1;

    let html = '';
    for (let i = 0; i < startOffset; i++) html += '<span class="cal-day empty"></span>';
    for (let d = 1; d <= daysInMonth; d++) {{
      const ds = fmtDate(curYear, curMonth, d);
      const has = REPORT_SET.has(ds);
      const isToday = ds === fmtDate(today.getFullYear(), today.getMonth(), today.getDate());
      let cls = 'cal-day';
      if (has) cls += ' has-report';
      if (isToday) cls += ' today';
      html += has
        ? '<a class="'+cls+'" href="daily/ai-news-'+ds+'.html" title="'+ds+'">'+d+'</a>'
        : '<span class="'+cls+'">'+d+'</span>';
    }}
    grid.innerHTML = html;
  }}

  window.calPrev = function() {{
    curMonth--;
    if (curMonth < 0) {{ curMonth = 11; curYear--; }}
    renderCal();
  }};
  window.calNext = function() {{
    curMonth++;
    if (curMonth > 11) {{ curMonth = 0; curYear++; }}
    renderCal();
  }};

  function init() {{
    curYear = today.getFullYear();
    curMonth = today.getMonth();
    renderCal();
  }}
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
}})();
</script>"""


def render_daily_homepage(daily_items: list[ContentItem]) -> str:
    latest = daily_items[0]
    entries = []
    entries.append(f"""<a href="{e(latest.href)}" class="daily-entry daily-entry-today" style="padding:18px 20px;">
<div style="flex:1;min-width:0;">
<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
<span class="featured-badge">最新</span>
<span style="font-size:12px;color:var(--text-muted);">{e(latest.short_date)}</span>
</div>
<div style="font-weight:500;font-size:15px;margin-bottom:6px;">{e(latest.display_title)}</div>
<div style="font-size:12px;color:var(--text-secondary);line-height:1.55;margin-bottom:10px;">{e(latest.summary)}</div>
</div>
<div style="flex-shrink:0;font-size:18px;color:var(--text-muted);">→</div>
</a>""")
    for item in daily_items[1:3]:
        entries.append(f"""<a href="{e(item.href)}" class="daily-entry">
<div class="entry-icon">📰</div>
<div style="flex:1;">
<div style="font-weight:500;font-size:14px;margin-bottom:3px;">{e(item.display_title)}</div>
<div style="font-size:12px;color:var(--text-muted);">{e(item.short_date)} · {e(item.summary)}</div>
</div>
<div style="font-size:16px;color:var(--accent);">→</div>
</a>""")
    entries.append(f"""<a href="daily/archive.html" class="daily-entry daily-entry-archive" style="justify-content:space-between;">
<span style="font-size:12px;font-weight:500;color:var(--text-secondary);">历史日报</span>
<span style="font-size:11px;color:var(--text-muted);">共 {len(daily_items)} 期归档 →</span>
</a>""")
    return f"""{HOMEPAGE_DAILY_START}
<div class="container">
<div class="section-header-hp">
<div>
<div class="section-label">AI Insight</div>
<h2 class="section-title-hp">每日 AI 日报</h2>
</div>
<a href="daily/archive.html" class="section-link">查看全部 →</a>
</div>
<div class="daily-layout">
<div class="daily-left">
{"".join(entries)}
</div>
<div class="daily-right">
<div class="calendar-card">
<div class="cal-header">
<button class="cal-nav-btn" onclick="calPrev()" title="上个月">◀</button>
<span class="cal-month-label" id="cal-month-label">{latest.date.year}年 {latest.date.month}月</span>
<button class="cal-nav-btn" onclick="calNext()" title="下个月">▶</button>
</div>
<div class="cal-day-names">
<span class="cal-day-name" title="周一">一</span>
<span class="cal-day-name" title="周二">二</span>
<span class="cal-day-name" title="周三">三</span>
<span class="cal-day-name" title="周四">四</span>
<span class="cal-day-name" title="周五">五</span>
<span class="cal-day-name" title="周六">六</span>
<span class="cal-day-name" title="周日">日</span>
</div>
<div class="cal-grid" id="cal-grid"></div>
<div class="cal-legend">
<span class="cal-legend-dot has"></span>有日报
<span class="cal-legend-dot today"></span>今天
<span class="cal-count" id="cal-count">0 篇日报</span>
</div>
</div>
</div>
</div>
</div>
{HOMEPAGE_DAILY_END}"""


def render_research_homepage(research_items: list[ContentItem]) -> str:
    entries = []
    for i, item in enumerate(research_items[:3]):
        if i == 0:
            entries.append(f"""<a href="{e(item.href)}" class="featured-card">
<div class="featured-content">
<div class="featured-meta"><span class="featured-badge">最新</span><span>{e(item.slash_date)}</span></div>
<h3 class="featured-title">{e(item.display_title)}</h3>
<p class="featured-desc">{e(item.summary)}</p>
</div>
<div class="featured-arrow">→</div>
</a>""")
        else:
            entries.append(f"""<a href="{e(item.href)}" class="daily-entry">
<div class="entry-icon">📊</div>
<div style="flex:1;">
<div style="font-weight:500;font-size:14px;margin-bottom:2px;">{e(item.display_title)}</div>
<div style="font-size:12px;color:var(--text-muted);">{e(item.slash_date)} · {e(item.category)}</div>
</div>
<div style="font-size:16px;color:var(--text-muted);">→</div>
</a>""")
    return f"""{HOMEPAGE_RESEARCH_START}
<div class="container">
<div class="section-header-hp">
<div>
<div class="section-label">Research</div>
<h2 class="section-title-hp">深度调研报告</h2>
</div>
<a href="research/archive.html" class="section-link">查看全部 →</a>
</div>
<div style="display:flex;flex-direction:column;gap:10px;">
{"".join(entries)}
</div>
</div>
{HOMEPAGE_RESEARCH_END}"""


def replace_between(content: str, start: str, end: str, replacement: str) -> str:
    if start in content and end in content:
        return re.sub(re.escape(start) + r".*?" + re.escape(end), replacement, content, flags=re.S)
    raise ValueError(f"missing markers: {start} / {end}")


def replace_section(content: str, section_id: str, replacement: str) -> str:
    pattern = rf'(<section class="hp-section" id="{section_id}">).*?(</section>)'
    return re.sub(pattern, rf"\1\n{replacement}\n\2", content, count=1, flags=re.S)


def update_homepage() -> None:
    daily_items = load_daily_items()
    research_items = load_research_items()
    content = read_text(INDEX)

    content = re.sub(r"<script>\s*// Calendar.*?</script>", render_reports_script(daily_items), content, count=1, flags=re.S)
    daily_fragment = render_daily_homepage(daily_items)
    if HOMEPAGE_DAILY_START in content:
        content = replace_between(content, HOMEPAGE_DAILY_START, HOMEPAGE_DAILY_END, daily_fragment)
    else:
        content = replace_section(content, "daily", daily_fragment)

    research_fragment = render_research_homepage(research_items)
    content = replace_between(content, HOMEPAGE_RESEARCH_START, HOMEPAGE_RESEARCH_END, research_fragment)
    write_text(INDEX, content)
    print(f"Updated homepage: {len(daily_items)} daily items, {len(research_items)} research reports")


def render_daily_archive(items: list[ContentItem], overrides: dict[str, dict[str, str]]) -> str:
    links = []
    for i, item in enumerate(items):
        summary = overrides.get(item.path.name, {}).get("summary", item.summary)
        latest = " latest" if i == 0 else ""
        badge = '<span class="badge-latest">最新</span>' if i == 0 else ""
        links.append(f"""<a href="{e(item.path.name)}" class="archive-item{latest}">
<div class="archive-icon">📰</div>
<div class="archive-content">
<div class="archive-date">{e(item.chinese_date)}{badge}</div>
<div class="archive-meta">{e(summary)}</div>
</div>
<div class="archive-arrow">→</div>
</a>""")
    body = f"""<div class="archive-header">
<div class="container-sm">
<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;">
<div><h1>📚 历史日报归档</h1><div class="subtitle">AI Daily News Archive</div></div>
<div style="text-align:right;"><div class="stats-value">{len(items)}</div><div class="stats-label">历史日报</div></div>
</div>
</div>
</div>
<main class="container-sm">
<div class="archive-list">
{"".join(links)}
</div>
</main>"""
    return page_shell("历史日报归档 - 第二号", "../", body, "archive.html", "../research/archive.html")


def render_research_archive(items: list[ContentItem], overrides: dict[str, dict[str, str]]) -> str:
    latest = items[0]
    latest_summary = overrides.get(latest.path.name, {}).get("summary", latest.summary)
    links = []
    for item in items:
        category = overrides.get(item.path.name, {}).get("category", item.category)
        links.append(f"""<a href="{e(item.path.name)}" class="archive-item">
<div class="archive-icon">📊</div>
<div class="archive-content">
<div style="font-size:12px;color:var(--text-muted);margin-bottom:3px;">{e(item.slash_date)}</div>
<div style="font-size:15px;font-weight:500;margin-bottom:3px;">{e(item.display_title)}</div>
<div style="font-size:12px;color:var(--text-secondary);">{e(category)}</div>
</div>
<div class="archive-arrow">→</div>
</a>""")
    body = f"""<div class="archive-header">
<div class="container-sm">
<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;">
<div><h1>📊 调研报告归档</h1><div class="subtitle">Research Reports Archive</div></div>
<div style="text-align:right;"><div class="stats-value">{len(items)}</div><div class="stats-label">调研报告</div></div>
</div>
</div>
</div>
<main class="container-sm">
<div class="section-label">Featured</div>
<a href="{e(latest.path.name)}" class="featured-card">
<div class="featured-content">
<div class="featured-meta"><span>{e(latest.slash_date)} · 最新</span></div>
<h3 class="featured-title">{e(latest.display_title)}</h3>
<p class="featured-desc">{e(latest_summary)}</p>
</div>
<div class="featured-arrow">→</div>
</a>
<div class="section-label">History</div>
<div class="archive-list">
{"".join(links)}
</div>
</main>"""
    return page_shell("调研报告归档 - 第二号", "../", body, "../daily/archive.html", "archive.html")


def update_archives() -> None:
    daily_items = load_daily_items()
    research_items = load_research_items()
    daily_overrides = archive_overrides(DAILY_DIR / "archive.html")
    research_overrides = archive_overrides(RESEARCH_DIR / "archive.html")
    write_text(DAILY_DIR / "archive.html", render_daily_archive(daily_items, daily_overrides))
    write_text(RESEARCH_DIR / "archive.html", render_research_archive(research_items, research_overrides))
    print(f"Updated archives: {len(daily_items)} daily items, {len(research_items)} research reports")


def validate() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    html_files = sorted(DOCS.rglob("*.html"))

    for path in html_files:
        content = read_text(path)
        rel = path.relative_to(ROOT)
        if "[truncated]" in content:
            errors.append(f"{rel}: contains literal [truncated]")
        if not content.rstrip().endswith("</html>"):
            errors.append(f"{rel}: does not end with </html>")
        if re.search(r"<style\b.*?\d+\|\.", content, flags=re.S):
            errors.append(f"{rel}: style block contains read_file line prefixes")
        if path.parent in {DAILY_DIR, RESEARCH_DIR} and path.name != "archive.html":
            if "styles.css" not in content:
                errors.append(f"{rel}: missing shared styles.css")
            if "data-pagefind-ignore" not in content:
                warnings.append(f"{rel}: missing unified header/search ignore marker")
            if path.parent == RESEARCH_DIR and not match_attr(r'<meta[^>]*name=["\']date["\'][^>]*content=["\']([^"\']+)["\']', content):
                errors.append(f"{rel}: research report missing meta date")
            if path.parent == DAILY_DIR:
                for gallery in re.findall(r'<div[^>]*class=["\'][^"\']*vitem-gallery[^"\']*["\'][^>]*>(.*?)</div>', content, flags=re.I | re.S):
                    for img in re.findall(r"<img\b[^>]*>", gallery, flags=re.I):
                        if 'src="assets/' in img or "src='assets/" in img:
                            if not re.search(r'\bwidth=["\']\d+["\']', img) or not re.search(r'\bheight=["\']\d+["\']', img):
                                errors.append(f"{rel}: vitem-gallery local image missing width/height")
        if path.name == "index.html" and path.parent == DOCS:
            for marker in (HOMEPAGE_DAILY_START, HOMEPAGE_DAILY_END, HOMEPAGE_RESEARCH_START, HOMEPAGE_RESEARCH_END):
                if marker not in content:
                    errors.append(f"{rel}: missing {marker}")

    styles = read_text(DOCS / "styles.css") if (DOCS / "styles.css").exists() else ""
    for token in ("--accent: #2563eb", "--bg-primary: #f5f5f4", "--text-primary: #1c1c1c", "--border: #e8e8e6", "--radius-lg: 14px"):
        if token not in styles:
            errors.append(f"docs/styles.css: missing token {token}")

    for required in (
        AGENTS_DIR / "architecture.md",
        AGENTS_DIR / "contracts" / "daily-digest.schema.json",
        AGENTS_DIR / "contracts" / "research-report.schema.json",
    ):
        if not required.exists():
            errors.append(f"{required.relative_to(ROOT)}: missing production harness contract")
        elif required.suffix == ".json":
            try:
                json.loads(read_text(required))
            except json.JSONDecodeError as exc:
                errors.append(f"{required.relative_to(ROOT)}: invalid JSON schema ({exc})")

    daily_items = load_daily_items()
    research_items = load_research_items()
    index = read_text(INDEX)
    for item in daily_items[:3]:
        if item.href not in index:
            errors.append(f"docs/index.html: missing homepage daily link {item.href}")
    for item in research_items[:3]:
        if item.href not in index:
            errors.append(f"docs/index.html: missing homepage research link {item.href}")

    daily_archive = read_text(DAILY_DIR / "archive.html")
    for item in daily_items:
        if item.path.name not in daily_archive:
            errors.append(f"docs/daily/archive.html: missing {item.path.name}")
    research_archive = read_text(RESEARCH_DIR / "archive.html")
    for item in research_items:
        if item.path.name not in research_archive:
            errors.append(f"docs/research/archive.html: missing {item.path.name}")

    for path in html_files:
        content = read_text(path)
        for href in re.findall(r'href=["\']([^"\']+\.html)["\']', content):
            if href.startswith(("http://", "https://", "#")):
                continue
            target = (path.parent / href).resolve()
            try:
                target.relative_to(ROOT)
            except ValueError:
                continue
            if not target.exists():
                errors.append(f"{path.relative_to(ROOT)}: broken link {href}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        print(f"Site harness validation failed: {len(errors)} error(s), {len(warnings)} warning(s)", file=sys.stderr)
        return 1
    print(f"Site harness validation passed: {len(html_files)} HTML files, {len(warnings)} warning(s)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Maintain and validate ai-news static site content.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("update-homepage")
    sub.add_parser("update-archives")
    sub.add_parser("update-all")
    sub.add_parser("validate")
    args = parser.parse_args()

    if args.command == "update-homepage":
        update_homepage()
        return 0
    if args.command == "update-archives":
        update_archives()
        return 0
    if args.command == "update-all":
        update_homepage()
        update_archives()
        return 0
    if args.command == "validate":
        return validate()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
