#!/usr/bin/env python3
"""Fetch tweet data and upsert the builders section in Daily Source JSON.

Usage:
  python3 scripts/gen_tweet_cards.py --date 2026-06-05 --from-html docs/daily/ai-news-2026-06-05.html
  python3 scripts/gen_tweet_cards.py docs/daily/ai-news-YYYY-MM-DD.html --translations /tmp/tweet-trans.json --render

Legacy HTML patch is removed. The script writes docs/daily/data/YYYY-MM-DD.json and can optionally render tweet cards.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

from daily_ingest import builder_chunk, parse_builder_vitems, parse_tweet_card_block
from daily_source import (
    DATA_DIR,
    ROOT,
    date_from_html_path,
    get_section,
    load_digest,
    save_digest,
    upsert_section,
)


BUILDER_LABELS = ("Builder 动态", "建造者动态")
BUILDER_MARKER_START = "<!-- DAILY-RENDER:builders:START -->"
BUILDER_MARKER_END = "<!-- DAILY-RENDER:builders:END -->"
SYNDICATION_TOKEN = "0"
CARD_OPEN = re.compile(r'<(?:section|div)\s+class="card span-4"')


def fetch_tweet(tweet_id: str) -> dict | None:
    url = f"https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&token={SYNDICATION_TOKEN}"
    try:
        response = requests.get(url, timeout=10)
        return response.json() if response.status_code == 200 else None
    except requests.RequestException:
        return None


def fmt_time(created_at: str) -> str:
    try:
        dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
        diff = datetime.now(timezone.utc) - dt
        if diff.days == 0:
            return dt.strftime("%H:%M")
        if diff.days == 1:
            return "昨天"
        return f"{dt.month}月{dt.day}日"
    except ValueError:
        return ""


def strip_tag_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def enrich_media_dimensions(media: list[dict]) -> list[dict]:
    enriched: list[dict] = []
    for asset in media:
        item = dict(asset)
        if item.get("width") and item.get("height"):
            enriched.append(item)
            continue
        src = item.get("src", "")
        if not src.startswith("assets/"):
            enriched.append(item)
            continue
        local = ROOT / "docs" / "daily" / src
        if not local.exists():
            continue
        with Image.open(local) as img:
            item["width"], item["height"] = img.size
        enriched.append(item)
    return enriched


def extract_tweet_refs(html_path: Path) -> list[dict[str, str]]:
    chunk, _ = builder_chunk(html_path.read_text(encoding="utf-8"))
    refs: list[dict[str, str]] = []
    seen: set[str] = set()
    for url, handle, tweet_id in re.findall(r'href="(https://x\.com/([^/]+)/status/(\d+))"', chunk):
        if tweet_id in seen:
            continue
        seen.add(tweet_id)
        refs.append({"url": url, "builder": handle, "tweetId": tweet_id})
    return refs


def parse_media(block: str) -> tuple[list[dict], int | None]:
    media: list[dict] = []
    gallery_cols = None
    gallery = re.search(r'<div class="vitem-gallery([^"]*)">(.*?)</div>', block, re.S)
    if gallery:
        if "cols-2" in gallery.group(1):
            gallery_cols = 2
        elif "cols-3" in gallery.group(1):
            gallery_cols = 3
        imgs = gallery.group(2)
    else:
        imgs = block
    for attrs in re.findall(r"<img\b([^>]+)>", imgs, re.S):
        src = re.search(r'src="([^"]+)"', attrs)
        width = re.search(r'width="(\d+)"', attrs)
        height = re.search(r'height="(\d+)"', attrs)
        alt = re.search(r'alt="([^"]*)"', attrs)
        if not src:
            continue
        item = {
            "src": src.group(1),
            "alt": alt.group(1) if alt else "",
        }
        if width and height:
            item["width"] = int(width.group(1))
            item["height"] = int(height.group(1))
        media.append(item)
    return media, gallery_cols


def download_avatar(url: str, handle: str, date: str) -> str:
    if not url:
        return ""
    rel = f"assets/{date}/{handle}-avatar.jpg"
    local = ROOT / "docs" / "daily" / rel
    if local.exists():
        return rel
    fetch_url = url.replace("_normal.", "_400x400.") if "_normal." in url else url
    try:
        response = requests.get(fetch_url, timeout=15)
        if response.status_code == 200:
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(response.content)
            return rel
    except requests.RequestException:
        pass
    return url


def parse_existing_tweet_item(block: str, tweet_id: str) -> dict | None:
    return parse_tweet_card_block(block, tweet_id)


def existing_items_by_tweet_id(html_path: Path, digest: dict | None = None) -> dict[str, dict]:
    items: dict[str, dict] = {}
    if digest:
        section = get_section(digest, "builders")
        for item in (section or {}).get("items", []):
            tweet_id = item.get("tweetId")
            if tweet_id:
                items[tweet_id] = item
    chunk, _ = builder_chunk(html_path.read_text(encoding="utf-8"))
    for block in re.findall(r'(<div class="vitem">\s*<a[^>]+class="tweet-card".*?</a>\s*</div>)', chunk, re.S):
        tweet_id = re.search(r"/status/(\d+)", block)
        if not tweet_id:
            continue
        parsed = parse_existing_tweet_item(block, tweet_id.group(1))
        if parsed:
            merged = {**items.get(tweet_id.group(1), {}), **parsed}
            items[tweet_id.group(1)] = merged
    return items


def download_media(tweet: dict, tweet_id: str, handle: str, date: str) -> tuple[list[dict], int | None]:
    asset_dir = ROOT / "docs" / "daily" / "assets" / date
    asset_dir.mkdir(parents=True, exist_ok=True)

    image_urls: list[str] = []
    if tweet.get("photos"):
        image_urls.extend(photo.get("url", "") for photo in tweet["photos"] if photo.get("url"))
    for media in tweet.get("entities", {}).get("media", []):
        if media.get("type") in ("photo", "video", "animated_gif") and media.get("media_url_https"):
            image_urls.append(media["media_url_https"])

    assets: list[dict] = []
    for index, img_url in enumerate(image_urls[:4]):
        if not img_url:
            continue
        rel = f"assets/{date}/{handle}-{tweet_id}-{index}.jpg"
        local = ROOT / "docs" / "daily" / rel
        if not local.exists():
            try:
                response = requests.get(img_url, timeout=15)
                if response.status_code != 200:
                    continue
                img = Image.open(BytesIO(response.content))
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                width, height = img.size
                if width > 1200:
                    height = int(height * 1200 / width)
                    width = 1200
                    img = img.resize((width, height), Image.LANCZOS)
                for quality in (92, 85, 75, 65, 55):
                    img.save(local, "JPEG", quality=quality, optimize=True)
                    if local.stat().st_size <= 500 * 1024:
                        break
            except (requests.RequestException, OSError, ValueError):
                continue
        if local.exists():
            with Image.open(local) as img:
                width, height = img.size
            assets.append(
                {
                    "src": rel,
                    "width": width,
                    "height": height,
                    "alt": "",
                }
            )
    gallery_cols = 2 if len(assets) == 2 else 3 if len(assets) >= 3 else None
    return assets, gallery_cols


def build_tweet_item(
    ref: dict[str, str],
    translations: dict[str, str],
    existing: dict[str, dict],
    date: str,
    *,
    use_api: bool,
) -> dict | None:
    tweet_id = ref["tweetId"]
    fallback = existing.get(tweet_id, {})
    tweet = fetch_tweet(tweet_id) if use_api else None

    if tweet and tweet.get("user"):
        user = tweet["user"]
        handle = user.get("screen_name", ref["builder"])
        media, gallery_cols = download_media(tweet, tweet_id, handle, date)
        avatar_url = user.get("profile_image_url_https", fallback.get("avatar", ""))
        item = {
            "title": user.get("name", handle),
            "builder": handle,
            "summary": tweet.get("text", ""),
            "translation": translations.get(tweet_id) or fallback.get("translation", ""),
            "url": f"https://x.com/{handle}/status/{tweet_id}",
            "tweetId": tweet_id,
            "avatar": download_avatar(avatar_url, handle, date),
            "tweetDate": fmt_time(tweet.get("created_at", "")) or fallback.get("tweetDate", ""),
            "metrics": {
                "favorites": tweet.get("favorite_count", 0),
                "retweets": tweet.get("retweet_count", 0),
                "replies": tweet.get("conversation_count", 0) or tweet.get("reply_count", 0),
            },
        }
        if media:
            item["media"] = media
            if gallery_cols:
                item["galleryCols"] = gallery_cols
        elif fallback.get("media"):
            item["media"] = enrich_media_dimensions(fallback["media"])
            if fallback.get("galleryCols"):
                item["galleryCols"] = fallback["galleryCols"]
        return item

    if tweet_id in existing:
        item = dict(existing[tweet_id])
        if translations.get(tweet_id):
            item["translation"] = translations[tweet_id]
        if item.get("avatar"):
            item["avatar"] = download_avatar(item["avatar"], item.get("builder", ref["builder"]), date)
        return item

    print(f"  FAIL: @{ref['builder']}/{tweet_id} — skipped", file=sys.stderr)
    return None


def normalize_builder_item(item: dict) -> dict:
    normalized = dict(item)
    if normalized.get("media"):
        media = [
            asset
            for asset in enrich_media_dimensions(normalized["media"])
            if asset.get("width") and asset.get("height")
        ]
        if media:
            normalized["media"] = media
        else:
            normalized.pop("media", None)
            normalized.pop("galleryCols", None)
    return normalized


def detect_builder_label(html_path: Path) -> str:
    content = html_path.read_text(encoding="utf-8")
    for label in BUILDER_LABELS:
        if f'<div class="label-sm">{label}</div>' in content:
            return label
    return BUILDER_LABELS[0]


def detect_section_title(html_path: Path) -> str:
    chunk, _ = builder_chunk(html_path.read_text(encoding="utf-8"))
    match = re.search(r"<h2>(.*?)</h2>", chunk, re.S)
    if match:
        return strip_tag_text(match.group(1))
    return "今日 Builder 动态"


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
            title = strip_tag_text(h1.group(1))
        if subtitle:
            summary = strip_tag_text(subtitle.group(1))[:180]
    return {
        "schemaVersion": 1,
        "date": date,
        "title": title,
        "summary": summary,
        "sections": [],
    }


def upsert_builders_section(
    date: str,
    items: list[dict],
    digest: dict,
    html_path: Path,
    *,
    layout: str,
) -> None:
    existing = get_section(digest, "builders")
    section = {
        "kind": "builders",
        "layout": layout,
        "label": existing.get("label", detect_builder_label(html_path)) if existing else detect_builder_label(html_path),
        "title": existing.get("title", detect_section_title(html_path)) if existing else detect_section_title(html_path),
        "items": items,
    }
    upsert_section(digest, section)
    save_digest(date, digest)


def run_render(date: str) -> None:
    render_script = ROOT / "scripts" / "render_daily.py"
    python_sh = ROOT / "scripts" / "python.sh"
    subprocess.run(
        [str(python_sh), str(render_script), date, "--kind", "builders"],
        cwd=ROOT,
        check=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Upsert tweet-based builders section into Daily Source JSON.")
    parser.add_argument("html_path", nargs="?", help="Legacy daily HTML path used to extract tweet URLs")
    parser.add_argument("--date", help="Daily date in YYYY-MM-DD format")
    parser.add_argument("--from-html", dest="from_html", help="Daily HTML path to extract tweet URLs from")
    parser.add_argument("--translations", type=Path, help='JSON file mapping tweet_id -> Chinese translation')
    parser.add_argument("--ingest-html-only", action="store_true", help="Parse existing tweet cards without calling syndication API")
    parser.add_argument("--render", action="store_true", help="Run render_daily for builders after update")
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

    content = html_path.read_text(encoding="utf-8")
    _, layout = builder_chunk(content)
    if layout == "vitem" and args.ingest_html_only:
        digest = ensure_digest(date, html_path)
        section = parse_builder_vitems(content)
        upsert_section(digest, section)
        save_digest(date, digest)
        print(f"Updated builders section in docs/daily/data/{date}.json ({len(section['items'])} vitem items)")
        if args.render:
            run_render(date)
        return 0

    refs = extract_tweet_refs(html_path)
    if not refs:
        print("No tweet URLs found in builders section.", file=sys.stderr)
        return 1

    digest = ensure_digest(date, html_path)
    existing = existing_items_by_tweet_id(html_path, digest)
    for tweet_id, item in existing.items():
        if item.get("translation"):
            translations.setdefault(tweet_id, item["translation"])
    items = [
        normalize_builder_item(item)
        for ref in refs
        if (item := build_tweet_item(ref, translations, existing, date, use_api=not args.ingest_html_only))
    ]
    if not items:
        print("No builder tweet items produced.", file=sys.stderr)
        return 1

    digest = ensure_digest(date, html_path)
    upsert_builders_section(date, items, digest, html_path, layout="tweet")
    print(f"Updated builders section in docs/daily/data/{date}.json ({len(items)} tweet items)")

    if args.render:
        run_render(date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
