#!/usr/bin/env python3
"""Render Daily Digest HTML from JSON source files."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from daily_source import DAILY_DIR, DEFAULT_SECTION_LAYOUT, ROOT, load_digest, section_key


TEMPLATES = Path(__file__).resolve().parent / "templates"

BUILDER_LABELS = ("Builder 动态", "建造者动态")
PODCAST_LABELS = ("深度对话", "深度播客")
CARD_OPEN = re.compile(r'<(?:section|div)\s+class="card span-4"')

MARKER_START = "<!-- DAILY-RENDER:{key}:START -->"
MARKER_END = "<!-- DAILY-RENDER:{key}:END -->"

GITHUB_SECTION_STYLE = 'style="background:rgba(16,185,129,0.02);border-color:rgba(16,185,129,0.12);"'
GITHUB_LABEL_PATTERN = re.compile(r'<div class="label-sm"[^>]*>GitHub Trending')

SECTION_TEMPLATE_MAP = {
    ("github", "simple"): "components/github-section.html",
    ("github", "card"): "components/github-gh-section.html",
    ("builders", "vitem"): "components/builder-section.html",
    ("builders", "tweet"): "components/builder-tweet-section.html",
    ("news", "rss"): "components/news-section.html",
    ("podcasts", "embed"): "components/podcast-section.html",
    ("podcasts", "vitem"): "components/podcast-section.html",
    ("analysis", "highlights"): "components/highlights-section.html",
    ("analysis", "prose"): "components/analysis-section.html",
}


def format_stars(value: int | float | str) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def format_compact_num(value: int | float | str) -> str:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return str(value)
    if number >= 1000:
        text = f"{number / 1000:.1f}k"
        return text.replace(".0k", "k")
    return str(number)


def build_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["format_stars"] = format_stars
    env.filters["format_compact_num"] = format_compact_num
    return env


def render_key_for_section(section: dict) -> str:
    key = section_key(section)
    if len(key) == 3:
        return f"{key[0]}:{key[1]}:{key[2]}"
    return f"{key[0]}:{key[1]}"


def template_for(section: dict) -> str:
    kind = section_key(section)[0]
    layout = section_key(section)[1]
    name = SECTION_TEMPLATE_MAP.get((kind, layout))
    if not name:
        raise ValueError(f"No render template registered for section {kind}/{layout}")
    return name


def render_section(env: Environment, section: dict) -> str:
    template = env.get_template(template_for(section))
    return template.render(block=section).strip()


def render_hero(env: Environment, digest: dict) -> str:
    template = env.get_template("components/hero-section.html")
    return template.render(digest=digest).strip()


def render_sources(env: Environment, digest: dict) -> str:
    if not digest.get("sources"):
        return ""
    template = env.get_template("components/sources-section.html")
    return template.render(digest=digest).strip()


def _card_start_before(content: str, anchor: str) -> int:
    anchor_idx = content.find(anchor)
    if anchor_idx == -1:
        return -1
    section_start = content.rfind('<section class="card span-4"', 0, anchor_idx)
    div_start = content.rfind('<div class="card span-4"', 0, anchor_idx)
    candidates = [pos for pos in (section_start, div_start) if pos != -1]
    return max(candidates) if candidates else -1


def _section_bounds(content: str, label: str) -> tuple[int, int]:
    anchor = f'<div class="label-sm">{label}</div>'
    start = _card_start_before(content, anchor)
    if start == -1:
        raise ValueError(f"Could not locate section label: {label}")
    next_card = CARD_OPEN.search(content, content.find(anchor) + 1)
    if next_card is None:
        raise ValueError(f"Could not locate end of section: {label}")
    return start, next_card.start()


def _find_builder_bounds(content: str) -> tuple[int, int]:
    for label in BUILDER_LABELS:
        pattern = re.compile(rf'<div class="label-sm"[^>]*>{re.escape(label)}</div>')
        match = pattern.search(content)
        if not match:
            continue
        return _section_bounds_by_pattern(content, pattern)
    raise ValueError("Could not locate builders section")


def _find_github_bounds(content: str, layout: str | None) -> tuple[int, int]:
    render_key = f"github:{layout or 'simple'}"
    for key in marker_candidates(render_key):
        start_marker = MARKER_START.format(key=key)
        end_marker = MARKER_END.format(key=key)
        if start_marker in content and end_marker in content:
            return content.find(start_marker), content.find(end_marker) + len(end_marker)

    highlight_start = content.find('<div class="card span-4 card-highlight">')
    label_match = GITHUB_LABEL_PATTERN.search(content)
    if layout == "card" or label_match:
        anchor_idx = label_match.start() if label_match else -1
        if anchor_idx != -1:
            start = _card_start_before(content, label_match.group(0))
            if highlight_start != -1 and highlight_start > start:
                return start, highlight_start
            next_card = CARD_OPEN.search(content, anchor_idx + 1)
            if start != -1 and next_card is not None:
                return start, next_card.start()
    section_start = content.find(GITHUB_SECTION_STYLE)
    if section_start == -1:
        section_start = content.find('style="background:rgba(16,185,129,0.02)')
    if section_start != -1 and highlight_start != -1:
        card_start = content.rfind('<div class="card span-4"', 0, section_start)
        if card_start != -1:
            return card_start, highlight_start
    raise ValueError("Could not locate github section")


def _find_hero_bounds(content: str) -> tuple[int, int]:
    h1 = re.search(r"<h1>", content)
    if not h1:
        raise ValueError("Could not locate hero section")
    start = content.rfind('<div class="card span-4"', 0, h1.start())
    if start == -1:
        start = content.rfind('<section class="card span-4"', 0, h1.start())
    next_card = CARD_OPEN.search(content, h1.start() + 1)
    if start == -1 or next_card is None:
        raise ValueError("Could not locate hero section")
    return start, next_card.start()


def _find_analysis_prose_bounds(content: str) -> tuple[int, int]:
    match = re.search(r'<(?:section|div)\s+class="card span-4 card-highlight"', content)
    if not match:
        raise ValueError("Could not locate analysis prose section")
    start = match.start()
    next_card = CARD_OPEN.search(content, start + len(match.group(0)))
    if next_card is not None:
        return start, next_card.start()
    for marker in ("</main>", "📚 参考来源", '<div class="label-sm">参考来源</div>'):
        idx = content.find(marker, start)
        if idx != -1:
            return start, idx
    raise ValueError("Could not locate end of analysis prose section")


def _find_sources_bounds(content: str) -> tuple[int, int]:
    try:
        return _section_bounds(content, "参考来源")
    except ValueError:
        pass
    marker = content.find("📚 参考来源")
    if marker == -1:
        raise ValueError("Could not locate sources section")
    start = content.rfind('<div class="card span-4"', 0, marker)
    footer = content.find("</main>", marker)
    if footer == -1:
        footer = content.find("</div>", content.rfind("</div>", 0, marker) + 6) + 6
    next_card = CARD_OPEN.search(content, marker + 1)
    end = next_card.start() if next_card and next_card.start() < footer else footer
    if start == -1:
        raise ValueError("Could not locate sources section")
    return start, end


def _find_podcast_bounds(content: str, label: str) -> tuple[int, int]:
    return _section_bounds(content, label)


def marker_candidates(key: str) -> list[str]:
    keys = [key]
    if ":" in key:
        keys.append(key.split(":", 1)[0])
    return keys


def merge_rendered(content: str, key: str, rendered: str, finder) -> str:
    for candidate in marker_candidates(key):
        start_marker = MARKER_START.format(key=candidate)
        end_marker = MARKER_END.format(key=candidate)
        wrapped = f"{start_marker}\n{rendered}\n{end_marker}"
        if start_marker in content and end_marker in content:
            pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)
            return re.sub(pattern, wrapped, content, count=1, flags=re.S)
    start_marker = MARKER_START.format(key=key)
    end_marker = MARKER_END.format(key=key)
    wrapped = f"{start_marker}\n{rendered}\n{end_marker}"
    start, end = finder(content)
    return content[:start] + wrapped + "\n\n" + content[end:]


def merge_section_block(html_path: Path, key: str, rendered: str, finder) -> None:
    content = html_path.read_text(encoding="utf-8")
    updated = merge_rendered(content, key, rendered, finder)
    html_path.write_text(updated, encoding="utf-8")


def merge_sources(html_path: Path, rendered: str) -> None:
    try:
        merge_section_block(html_path, "sources", rendered, _find_sources_bounds)
    except ValueError:
        content = html_path.read_text(encoding="utf-8")
        wrapped = f"{MARKER_START.format(key='sources')}\n{rendered}\n{MARKER_END.format(key='sources')}"
        if MARKER_START.format(key="sources") in content and MARKER_END.format(key="sources") in content:
            pattern = re.escape(MARKER_START.format(key="sources")) + r".*?" + re.escape(MARKER_END.format(key="sources"))
            updated = re.sub(pattern, wrapped, content, count=1, flags=re.S)
        elif "</main>" in content:
            idx = content.rfind("</main>")
            updated = content[:idx] + wrapped + "\n\n" + content[idx:]
        else:
            bento = content.rfind('class="bento"')
            idx = content.rfind("</div>", bento if bento != -1 else 0)
            updated = content[: idx + 6] + "\n\n" + wrapped + content[idx + 6 :]
        html_path.write_text(updated, encoding="utf-8")


def merge_github(html_path: Path, rendered: str, layout: str | None) -> None:
    merge_section_block(html_path, f"github:{layout or 'simple'}", rendered, lambda c: _find_github_bounds(c, layout))


def merge_builders(html_path: Path, rendered: str, layout: str) -> None:
    merge_section_block(html_path, f"builders:{layout}", rendered, _find_builder_bounds)


def merge_labeled_section(html_path: Path, key: str, rendered: str, label: str) -> None:
    pattern = re.compile(rf'<div class="label-sm"[^>]*>{re.escape(label)}</div>')
    merge_section_block(
        html_path,
        key,
        rendered,
        lambda content: _section_bounds_by_pattern(content, pattern),
    )


def _section_bounds_by_pattern(content: str, pattern: re.Pattern[str]) -> tuple[int, int]:
    match = pattern.search(content)
    if not match:
        raise ValueError(f"Could not locate section matching: {pattern.pattern}")
    start = _card_start_before(content, match.group(0))
    next_card = CARD_OPEN.search(content, match.start() + 1)
    if start == -1 or next_card is None:
        raise ValueError(f"Could not locate bounds for section: {pattern.pattern}")
    return start, next_card.start()


def render_daily(date: str, *, merge: bool = True, kinds: list[str] | None = None) -> None:
    digest = load_digest(date)
    env = build_env()
    html_path = DAILY_DIR / f"ai-news-{date}.html"
    if merge and not html_path.exists():
        raise FileNotFoundError(f"Missing daily HTML to merge into: {html_path}")

    rendered_keys: list[str] = []

    if not kinds or "hero" in kinds:
        hero = render_hero(env, digest)
        if merge:
            merge_section_block(html_path, "hero", hero, _find_hero_bounds)
        else:
            print(hero)
        rendered_keys.append("hero")

    for section in digest.get("sections", []):
        kind = section_key(section)[0]
        layout = section_key(section)[1]
        section_render_key = render_key_for_section(section)
        if kinds and kind not in kinds and section_render_key not in kinds:
            continue
        rendered = render_section(env, section)
        key = render_key_for_section(section)
        if merge:
            if kind == "github":
                merge_github(html_path, rendered, layout)
            elif kind == "builders":
                merge_builders(html_path, rendered, layout)
            elif kind == "analysis" and layout == "highlights":
                merge_labeled_section(html_path, key, rendered, "今日要点")
            elif kind == "analysis" and layout == "prose":
                try:
                    merge_section_block(html_path, key, rendered, _find_analysis_prose_bounds)
                except ValueError:
                    content = html_path.read_text(encoding="utf-8")
                    wrapped = f"{MARKER_START.format(key=key)}\n{rendered}\n{MARKER_END.format(key=key)}"
                    anchor = content.rfind("<!-- DAILY-RENDER:github")
                    if anchor == -1:
                        anchor = content.find("📚 参考来源")
                    if anchor == -1:
                        anchor = content.rfind("</main>")
                    if anchor == -1:
                        raise ValueError("Could not locate analysis prose section")
                    updated = content[:anchor] + wrapped + "\n\n" + content[anchor:]
                    html_path.write_text(updated, encoding="utf-8")
            elif kind == "news":
                merge_labeled_section(html_path, key, rendered, "RSS 精选")
            elif kind == "podcasts":
                merge_labeled_section(html_path, key, rendered, section.get("label", "深度播客"))
            else:
                raise ValueError(f"No merge strategy for section {key}")
        else:
            print(rendered)
        rendered_keys.append(key)

    if digest.get("sources") and (not kinds or "sources" in kinds):
        sources = render_sources(env, digest)
        if merge:
            merge_sources(html_path, sources)
        else:
            print(sources)
        rendered_keys.append("sources")

    if merge:
        print(f"Merged {', '.join(rendered_keys)} into {html_path.relative_to(ROOT)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render daily digest sections from JSON source files.")
    parser.add_argument("date", help="Daily date in YYYY-MM-DD format")
    parser.add_argument(
        "--kind",
        action="append",
        dest="kinds",
        help="Only render selected section keys (repeatable), e.g. hero, github, builders",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print rendered HTML to stdout instead of merging into the daily page",
    )
    args = parser.parse_args(argv)

    try:
        render_daily(args.date, merge=not args.stdout, kinds=args.kinds)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
