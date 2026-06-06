#!/usr/bin/env python3
"""Fetch RSS feeds and upsert the news section in Daily Source JSON."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
import xml.etree.ElementTree as ET

import requests

from daily_source import ROOT, date_from_html_path, get_section, load_digest, save_digest, upsert_section


FEEDS_PATH = ROOT / "feeds.json"


def load_feeds() -> list[dict]:
    return json.loads(FEEDS_PATH.read_text(encoding="utf-8"))["feeds"]


def strip_tag_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def fetch_feed(feed: dict) -> list[dict]:
    try:
        response = requests.get(
            feed["url"],
            timeout=15,
            headers={"User-Agent": "ai-news-bot/1.0"},
        )
        if response.status_code != 200:
            return []
        root = ET.fromstring(response.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items = root.findall(".//item") or root.findall(".//atom:entry", ns)
        if not items:
            items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

        articles: list[dict] = []
        for item in items:
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            if link_el is not None:
                link = link_el.get("href") or (link_el.text.strip() if link_el.text else "")
            else:
                link = ""
            desc_raw = desc_el.text.strip() if desc_el is not None and desc_el.text else ""
            desc_clean = strip_tag_text(re.sub(r"<[^>]+>", " ", desc_raw))[:200]
            pub = item.find("pubDate")
            if pub is None:
                pub = item.find(".//{http://www.w3.org/2005/Atom}published")
            if pub is None:
                pub = item.find(".//{http://www.w3.org/2005/Atom}updated")
            pub_date = None
            if pub is not None and pub.text:
                try:
                    pub_date = parsedate_to_datetime(pub.text.strip())
                except Exception:
                    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                        try:
                            pub_date = datetime.strptime(pub.text.strip()[: len(fmt.replace("%", "0"))], fmt).replace(
                                tzinfo=timezone.utc
                            )
                            break
                        except ValueError:
                            continue
            if pub_date and title:
                cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
                if pub_date >= cutoff:
                    articles.append(
                        {
                            "title": title,
                            "summary": desc_clean or title[:200],
                            "url": link,
                            "source": feed["name"],
                            "publishedAt": pub_date.strftime("%m-%d %H:%M"),
                            "links": [{"label": feed["name"], "url": link}] if link else [],
                        }
                    )
        articles.sort(key=lambda article: article["publishedAt"], reverse=True)
        return articles[:2]
    except Exception as exc:
        print(f"  RSS FAIL: {feed['name']} — {exc}", file=sys.stderr)
        return []


def upsert_news_section(date: str, items: list[dict], digest: dict, feeds: list[dict]) -> None:
    existing = get_section(digest, "news")
    sources_str = " · ".join(feed["name"] for feed in feeds)
    section = {
        "kind": "news",
        "layout": "rss",
        "label": "RSS 精选",
        "title": existing.get("title", "值得关注的文章") if existing else "值得关注的文章",
        "footnote": existing.get("footnote", f"RSS 源：{sources_str}") if existing else f"RSS 源：{sources_str}",
        "items": items,
    }
    upsert_section(digest, section)
    save_digest(date, digest)


def run_render(date: str) -> None:
    render_script = ROOT / "scripts" / "render_daily.py"
    python_sh = ROOT / "scripts" / "python.sh"
    subprocess.run(
        [str(python_sh), str(render_script), date, "--kind", "news"],
        cwd=ROOT,
        check=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Upsert RSS news section into Daily Source JSON.")
    parser.add_argument("html_path", nargs="?", help="Legacy daily HTML path (date inference only)")
    parser.add_argument("--date", help="Daily date in YYYY-MM-DD format")
    parser.add_argument("--from-html", dest="from_html", help="Daily HTML path")
    parser.add_argument("--render", action="store_true", help="Render news section after update")
    args = parser.parse_args(argv)

    html_path = Path(args.from_html) if args.from_html else (Path(args.html_path) if args.html_path else None)
    date = args.date or (date_from_html_path(html_path) if html_path else None)
    if not date:
        parser.error("Provide --date or a daily HTML path")

    feeds = load_feeds()
    all_articles: list[dict] = []
    for feed in feeds:
        articles = fetch_feed(feed)
        all_articles.extend(articles)
        print(f"  {feed['name']}: {len(articles)} recent articles")
    all_articles.sort(key=lambda article: article.get("publishedAt", ""), reverse=True)

    json_path = ROOT / "docs" / "daily" / "data" / f"{date}.json"
    if json_path.exists():
        digest = load_digest(date)
    else:
        digest = {"schemaVersion": 1, "date": date, "title": f"{date} AI 日报", "summary": "", "sections": []}

    if not all_articles:
        print("No recent RSS articles found")
        return 0

    upsert_news_section(date, all_articles, digest, feeds)
    print(f"Updated news section in docs/daily/data/{date}.json ({len(all_articles)} items)")

    if args.render:
        run_render(date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
