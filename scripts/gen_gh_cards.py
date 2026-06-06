#!/usr/bin/env python3
"""Fetch GitHub repo data and upsert the github section in Daily Source JSON."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import requests

from daily_source import (
    DATA_DIR,
    ROOT,
    date_from_html_path,
    get_section,
    load_digest,
    save_digest,
    upsert_section,
)


GITHUB_MARKER_START = "<!-- DAILY-RENDER:github:START -->"
GITHUB_MARKER_END = "<!-- DAILY-RENDER:github:END -->"
GITHUB_SECTION_STYLE = 'style="background:rgba(16,185,129,0.02);border-color:rgba(16,185,129,0.12);"'
GITHUB_LABEL_PATTERN = re.compile(r'<div class="label-sm"[^>]*>GitHub Trending')
REPO_IN_URL = re.compile(r"github\.com/([^/]+)/([^/\"'?#]+)")
CARD_OPEN = re.compile(r'<(?:section|div)\s+class="card span-4"')


def fetch_repo(owner: str, repo: str) -> dict | None:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        response = requests.get(url, headers={"Accept": "application/vnd.github+json"}, timeout=10)
        return response.json() if response.status_code == 200 else None
    except requests.RequestException:
        return None


def strip_tag_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_compact_num(raw: str) -> int:
    value = raw.strip().replace(",", "")
    if value.endswith("k"):
        return int(float(value[:-1]) * 1000)
    return int(float(value))


def github_chunk(html: str) -> tuple[str, str]:
    start = html.find(GITHUB_MARKER_START)
    end = html.find(GITHUB_MARKER_END)
    if start != -1 and end != -1:
        chunk = html[start:end]
        layout = "card" if "gh-card" in chunk else "simple"
        return chunk, layout

    label_match = GITHUB_LABEL_PATTERN.search(html)
    if label_match:
        label_idx = label_match.start()
        card_starts = [match.start() for match in CARD_OPEN.finditer(html, 0, label_idx)]
        start_pos = card_starts[-1] if card_starts else label_idx
        next_card = CARD_OPEN.search(html, label_idx + 1)
        end_pos = next_card.start() if next_card else len(html)
        chunk = html[start_pos:end_pos]
        return chunk, "card" if "gh-card" in chunk else "simple"

    style_idx = html.find(GITHUB_SECTION_STYLE)
    if style_idx != -1:
        card_start = html.rfind('<div class="card span-4"', 0, style_idx)
        highlight_idx = html.find('<div class="card span-4 card-highlight">', style_idx)
        chunk = html[card_start:highlight_idx] if card_start != -1 and highlight_idx != -1 else html[style_idx : style_idx + 12000]
        return chunk, "simple"

    raise ValueError("Could not locate GitHub section in HTML")


def extract_repos_from_html(html_path: Path) -> tuple[list[tuple[str, str, str]], str]:
    chunk, layout = github_chunk(html_path.read_text(encoding="utf-8"))
    seen: set[str] = set()
    repos: list[tuple[str, str, str]] = []
    for url in re.findall(r'href="(https://github\.com/[^"]+)"', chunk):
        match = REPO_IN_URL.search(url)
        if not match:
            continue
        owner = match.group(1)
        repo = match.group(2).rstrip("/")
        key = f"{owner}/{repo}"
        if key not in seen:
            seen.add(key)
            repos.append((owner, repo, key))
    return repos, layout


def parse_gh_card_item(block: str, key: str) -> dict | None:
    owner_match = re.search(r'gh-owner">([^<]+)<', block)
    name_match = re.search(r'gh-name">([^<]+)<', block)
    body = re.search(r'gh-body">(.*?)</div>', block, re.S)
    translation = re.search(r'gh-translation">(.*?)</div>', block, re.S)
    stars = re.search(r'gh-stars">⭐\s*([^<]+)<', block)
    forks = re.search(r'gh-forks">🍴\s*([^<]+)<', block)
    language = re.search(r'gh-lang">●\s*([^<]+)<', block)
    avatar = re.search(r'gh-avatar" src="([^"]+)"', block)
    url = re.search(r'href="(https://github\.com/[^"]+)"', block)
    topics = [strip_tag_text(topic) for topic in re.findall(r'gh-topic">([^<]+)<', block)]
    owner = owner_match.group(1) if owner_match else key.split("/")[0]
    repo_name = name_match.group(1) if name_match else key.split("/", 1)[1]
    item = {
        "title": key,
        "owner": owner,
        "repoName": repo_name,
        "summary": strip_tag_text(body.group(1)) if body else "",
        "url": url.group(1) if url else f"https://github.com/{owner}/{repo_name}",
    }
    if translation:
        item["translation"] = strip_tag_text(translation.group(1))
    if stars:
        item["stars"] = parse_compact_num(stars.group(1))
    if forks:
        item["forks"] = parse_compact_num(forks.group(1))
    if language:
        item["language"] = strip_tag_text(language.group(1))
    if avatar:
        item["avatar"] = avatar.group(1)
    if topics:
        item["topics"] = topics[:4]
    return item


def parse_simple_github_item(block: str, key: str) -> dict | None:
    title_line = re.search(r'vitem-title">([^<]+)<', block)
    desc = re.search(r'vitem-desc">([^<]+)<', block)
    url = re.search(r'href="(https://github\.com/[^"]+)"', block)
    item: dict = {
        "title": key,
        "url": url.group(1) if url else f"https://github.com/{key}",
    }
    if desc:
        item["summary"] = strip_tag_text(desc.group(1))
    if title_line:
        stars_match = re.search(r"⭐\s*([\d,]+)", title_line.group(1))
        lang_match = re.search(r"·\s*(.+)$", title_line.group(1).strip())
        if stars_match:
            item["stars"] = int(stars_match.group(1).replace(",", ""))
        if lang_match:
            item["language"] = strip_tag_text(lang_match.group(1))
    return item


def existing_items_from_html(html_path: Path) -> dict[str, dict]:
    chunk, layout = github_chunk(html_path.read_text(encoding="utf-8"))
    items: dict[str, dict] = {}
    if layout == "card":
        for block in re.findall(r'(<div class="vitem">\s*<a[^>]+class="gh-card".*?</a>\s*</div>)', chunk, re.S):
            url = REPO_IN_URL.search(block)
            if not url:
                continue
            key = f"{url.group(1)}/{url.group(2)}"
            parsed = parse_gh_card_item(block, key)
            if parsed:
                items[key] = parsed
        return items

    for block in re.split(r'(?=<div class="vitem">)', chunk):
        if "github.com" not in block:
            continue
        url = REPO_IN_URL.search(block)
        if not url:
            continue
        key = f"{url.group(1)}/{url.group(2)}"
        if key in items:
            continue
        parsed = parse_simple_github_item(block, key)
        if parsed:
            items[key] = parsed
    return items


def build_github_items(
    repos: list[tuple[str, str, str]],
    translations: dict[str, str],
    existing_items: list[dict] | None,
    layout: str,
    *,
    use_api: bool,
) -> list[dict]:
    existing_by_key = {item.get("title"): item for item in (existing_items or []) if item.get("title")}
    items: list[dict] = []
    for owner, repo, key in repos:
        fallback = existing_by_key.get(key, {})
        data = fetch_repo(owner, repo) if use_api else None
        if data and "owner" in data:
            if layout == "card":
                item = {
                    "title": key,
                    "owner": owner,
                    "repoName": repo,
                    "summary": data.get("description") or fallback.get("summary", ""),
                    "translation": translations.get(key) or fallback.get("translation", ""),
                    "url": f"https://github.com/{owner}/{repo}",
                    "stars": data.get("stargazers_count", 0),
                    "forks": data.get("forks_count", 0),
                    "language": data.get("language") or fallback.get("language", ""),
                    "avatar": data.get("owner", {}).get("avatar_url", fallback.get("avatar", "")),
                    "topics": (data.get("topics") or fallback.get("topics") or [])[:4],
                }
            else:
                item = {
                    "title": key,
                    "summary": translations.get(key) or fallback.get("summary") or data.get("description") or "",
                    "url": f"https://github.com/{owner}/{repo}",
                    "stars": data.get("stargazers_count", 0),
                    "language": data.get("language") or fallback.get("language", ""),
                }
            items.append(item)
            continue
        if key in existing_by_key:
            items.append(existing_by_key[key])
            print(f"  KEEP: {key} — preserved existing", file=sys.stderr)
            continue
        print(f"  FAIL: {key} — skipped", file=sys.stderr)
    return items


def detect_section_title(html_path: Path) -> str:
    chunk, _ = github_chunk(html_path.read_text(encoding="utf-8"))
    match = re.search(r"<h2>(.*?)</h2>", chunk, re.S)
    if match:
        return strip_tag_text(match.group(1))
    return "GitHub Trending"


def ensure_digest(date: str, html_path: Path | None) -> dict:
    json_path = DATA_DIR / f"{date}.json"
    if json_path.exists():
        return load_digest(date)
    title = f"{date} AI 日报"
    summary = ""
    if html_path and html_path.exists():
        content = html_path.read_text(encoding="utf-8")
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.S)
        subtitle = re.search(r'class="subtitle"[^>]*>(.*?)</div>', content, re.S)
        if h1:
            title = strip_tag_text(re.sub(r"<[^>]+>", "", h1.group(1)))
        if subtitle:
            summary = strip_tag_text(re.sub(r"<[^>]+>", "", subtitle.group(1)))[:180]
    return {
        "schemaVersion": 1,
        "date": date,
        "title": title,
        "summary": summary,
        "sections": [],
    }


def upsert_github_section(
    date: str,
    items: list[dict],
    digest: dict,
    html_path: Path,
    layout: str,
) -> None:
    existing = get_section(digest, "github")
    month_day = f"{int(date[5:7])}月{int(date[8:10])}日"
    label = existing.get("label") if existing else None
    if not label:
        label = "GitHub Trending"
        if layout == "simple":
            label = f"GitHub Trending · {month_day}"
    section = {
        "kind": "github",
        "layout": layout,
        "label": label if layout == "simple" else "GitHub Trending",
        "title": existing.get("title", detect_section_title(html_path)) if existing else detect_section_title(html_path),
        "footnote": existing.get("footnote", "") if existing else "",
        "items": items,
    }
    upsert_section(digest, section)
    save_digest(date, digest)


def run_render(date: str) -> None:
    render_script = ROOT / "scripts" / "render_daily.py"
    python_sh = ROOT / "scripts" / "python.sh"
    subprocess.run(
        [str(python_sh), str(render_script), date, "--kind", "github"],
        cwd=ROOT,
        check=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Upsert GitHub Trending data into Daily Source JSON.")
    parser.add_argument("html_path", nargs="?", help="Legacy daily HTML path used to extract repo URLs")
    parser.add_argument("--date", help="Daily date in YYYY-MM-DD format")
    parser.add_argument("--from-html", dest="from_html", help="Daily HTML path to extract repo URLs from")
    parser.add_argument("--translations", type=Path, help='JSON file mapping "owner/repo" to Chinese summary')
    parser.add_argument("--ingest-html-only", action="store_true", help="Parse existing cards without calling GitHub API")
    parser.add_argument("--render", action="store_true", help="Run site:render-daily for github after update")
    args = parser.parse_args(argv)

    html_path = Path(args.from_html) if args.from_html else (Path(args.html_path) if args.html_path else None)
    date = args.date
    if html_path and not date:
        date = date_from_html_path(html_path)
    if not date or not html_path:
        parser.error("Provide --date and a daily HTML path")

    if not html_path.exists():
        print(f"HTML path not found: {html_path}", file=sys.stderr)
        return 1

    translations: dict[str, str] = {}
    if args.translations:
        translations = json.loads(args.translations.read_text(encoding="utf-8"))

    repos, layout = extract_repos_from_html(html_path)
    if not repos:
        print("No GitHub repos found to ingest.", file=sys.stderr)
        return 1

    digest = ensure_digest(date, html_path)
    existing_section = get_section(digest, "github")
    html_existing = existing_items_from_html(html_path)
    merged_existing = {item.get("title"): item for item in (existing_section or {}).get("items", []) if item.get("title")}
    merged_existing.update(html_existing)
    existing_list = list(merged_existing.values())

    items = build_github_items(
        repos,
        translations,
        existing_list,
        layout,
        use_api=not args.ingest_html_only,
    )
    if not items:
        print("No GitHub items produced.", file=sys.stderr)
        return 1

    upsert_github_section(date, items, digest, html_path, layout)
    print(f"Updated github section ({layout}) in docs/daily/data/{date}.json ({len(items)} items)")

    if args.render:
        run_render(date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
