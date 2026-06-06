"""Parse daily HTML into Daily Source JSON fields."""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

from daily_source import ROOT


CARD_OPEN = re.compile(r'<(?:section|div)\s+class="card span-4"')
BUILDER_LABELS = ("Builder 动态", "建造者动态")
PODCAST_LABELS = ("深度对话", "深度播客")
MARKER_START = "<!-- DAILY-RENDER:{kind}:START -->"
MARKER_END = "<!-- DAILY-RENDER:{kind}:END -->"


def strip_tag_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def strip_tags(value: str) -> str:
    return strip_tag_text(re.sub(r"<[^>]+>", " ", value))


def section_between(content: str, label: str) -> str | None:
    pattern = re.compile(rf'<div class="label-sm"[^>]*>{re.escape(label)}</div>')
    match = pattern.search(content)
    if not match:
        return None
    anchor = match.group(0)
    start = _card_start_before(content, anchor)
    if start == -1:
        return None
    next_card = CARD_OPEN.search(content, match.start() + 1)
    end = next_card.start() if next_card else len(content)
    return content[start:end]


def _card_start_before(content: str, anchor: str) -> int:
    anchor_idx = content.find(anchor)
    if anchor_idx == -1:
        return -1
    section_start = content.rfind('<section class="card span-4"', 0, anchor_idx)
    div_start = content.rfind('<div class="card span-4"', 0, anchor_idx)
    candidates = [pos for pos in (section_start, div_start) if pos != -1]
    return max(candidates) if candidates else -1


def enrich_media(media: list[dict]) -> list[dict]:
    enriched: list[dict] = []
    for asset in media:
        item = dict(asset)
        if item.get("width") and item.get("height"):
            enriched.append(item)
            continue
        src = item.get("src", "")
        if not src.startswith("assets/"):
            continue
        local = ROOT / "docs" / "daily" / src
        if not local.exists():
            continue
        with Image.open(local) as img:
            item["width"], item["height"] = img.size
        enriched.append(item)
    return enriched


def parse_media(block: str) -> tuple[list[dict], int | None]:
    media: list[dict] = []
    gallery_cols = None
    gallery = re.search(r'<div class="vitem-gallery([^"]*)">(.*?)</div>', block, re.S)
    imgs = gallery.group(2) if gallery else block
    if gallery:
        if "cols-2" in gallery.group(1):
            gallery_cols = 2
        elif "cols-3" in gallery.group(1):
            gallery_cols = 3
    for attrs in re.findall(r"<img\b([^>]+)>", imgs, re.S):
        src = re.search(r'src="([^"]+)"', attrs)
        width = re.search(r'width="(\d+)"', attrs)
        height = re.search(r'height="(\d+)"', attrs)
        alt = re.search(r'alt="([^"]*)"', attrs)
        if not src:
            continue
        item = {"src": src.group(1), "alt": alt.group(1) if alt else ""}
        if width and height:
            item["width"] = int(width.group(1))
            item["height"] = int(height.group(1))
        media.append(item)
    media = enrich_media(media)
    return media, gallery_cols


def parse_links(block: str) -> list[dict]:
    links: list[dict] = []
    for url, label in re.findall(
        r'<a href="([^"]+)"[^>]*class="vitem-link"[^>]*>(.*?)</a>',
        block,
        re.S,
    ):
        links.append({"url": url, "label": strip_tag_text(label)})
    return links


def parse_vitem(block: str) -> dict | None:
    title = re.search(r'vitem-title">([^<]+)<', block)
    desc = re.search(r'vitem-desc">([^<]+)<', block)
    quote = re.search(r'vitem-quote">([^<]+)<', block)
    if not title and not desc:
        return None
    item = {
        "title": strip_tag_text(title.group(1)) if title else "",
        "summary": strip_tag_text(desc.group(1)) if desc else strip_tag_text(title.group(1)),
    }
    if quote:
        item["quote"] = strip_tag_text(quote.group(1))
    media, gallery_cols = parse_media(block)
    if media:
        item["media"] = media
        if gallery_cols:
            item["galleryCols"] = gallery_cols
    links = parse_links(block)
    if links:
        item["links"] = links
        if not item.get("url"):
            item["url"] = links[0]["url"]
    return item


def _hero_bounds(content: str) -> tuple[int, int]:
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


def parse_hero(content: str) -> dict:
    start, end = _hero_bounds(content)
    block = content[start:end]
    label = re.search(r'<div class="label-sm"[^>]*>([^<]+)</div>', block)
    h1 = re.search(r"<h1>(.*?)</h1>", block, re.S)
    subtitle = re.search(r'class="subtitle"[^>]*>(.*?)</div>', block, re.S)
    tags = [strip_tag_text(tag) for tag in re.findall(r'<span class="tag"[^>]*>([^<]+)</span>', block)]
    stats = []
    for num, stat_label in re.findall(
        r'<div class="stat-num">([^<]+)</div>\s*<div class="stat-label">([^<]+)</div>',
        block,
    ):
        stats.append({"num": strip_tag_text(num), "label": strip_tag_text(stat_label)})
    return {
        "title": strip_tag_text(strip_tags(h1.group(1))) if h1 else "",
        "summary": subtitle.group(1).strip() if subtitle else "",
        "heroLabel": strip_tag_text(label.group(1)) if label else "",
        "tags": tags,
        "stats": stats,
    }


def parse_highlights(content: str) -> dict | None:
    block = section_between(content, "今日要点")
    if not block:
        return None
    items: list[dict] = []
    for card in re.findall(r'<div class="feature-card">(.*?)</div>\s*(?:</div>)?', block, re.S):
        paragraph = re.search(r"<p>(.*?)</p>", card, re.S)
        links = parse_links(card)
        if paragraph:
            items.append(
                {
                    "title": "要点",
                    "summary": paragraph.group(1).strip(),
                    **({"links": links} if links else {}),
                }
            )
    if not items:
        grid_match = re.search(r'<div class="grid-2"[^>]*>(.*)', block, re.S)
        if grid_match:
            for card in re.findall(
                r'<div style="background:#fafafa[^"]*"[^>]*>\s*<div[^>]*>(.*?)</div>\s*</div>',
                grid_match.group(1),
                re.S,
            ):
                items.append({"title": "要点", "summary": card.strip()})
    if not items:
        return None
    return {
        "kind": "analysis",
        "layout": "highlights",
        "label": "今日要点",
        "title": "今日要点",
        "items": items,
    }


def parse_podcast_block(block: str, label: str) -> dict:
    title = re.search(r"<h2>(.*?)</h2>", block, re.S)
    intro = re.search(r'<div class="text-body">(.*?)</div>', block, re.S)
    iframe = re.search(r'<iframe[^>]+src="([^"]+)"', block)
    media, _ = parse_media(block)
    items: list[dict] = []
    for vitem in re.split(r'(?=<div class="vitem">)', block):
        if 'class="vitem"' not in vitem:
            continue
        if "vitem-title" not in vitem and "vitem-desc" not in vitem:
            continue
        parsed = parse_vitem(vitem)
        if parsed and parsed.get("title"):
            items.append(parsed)
    links = parse_links(block)
    section = {
        "kind": "podcasts",
        "layout": "embed" if iframe else "vitem",
        "label": label,
        "title": strip_tag_text(title.group(1)) if title else "",
        "intro": strip_tag_text(intro.group(1)) if intro else "",
        "items": items or [{"title": label, "summary": strip_tag_text(intro.group(1)) if intro else label}],
    }
    if iframe:
        section["embedUrl"] = iframe.group(1)
    if media:
        section.setdefault("items", [])
        if section["items"]:
            section["items"][0]["media"] = media
    if links:
        section["footnote"] = links[0]["label"]
        section["items"][-1].setdefault("links", links)
    return section


def parse_podcasts(content: str) -> list[dict]:
    sections: list[dict] = []
    for label in PODCAST_LABELS:
        block = section_between(content, label)
        if block:
            sections.append(parse_podcast_block(block, label))
    return sections


def parse_news(content: str) -> dict | None:
    block = section_between(content, "RSS 精选")
    if not block:
        return None
    title = re.search(r"<h2>(.*?)</h2>", block, re.S)
    footnote = re.search(r'<div class="quote"[^>]*>(.*?)</div>', block, re.S)
    items: list[dict] = []
    for vitem in re.split(r'(?=<div class="vitem">)', block):
        if 'class="vitem"' not in vitem:
            continue
        item_title = re.search(r'vitem-title">([^<]+)<', vitem)
        item_desc = re.search(r'vitem-desc">([^<]+)<', vitem)
        if not item_title:
            continue
        links = parse_links(vitem)
        source = links[0]["label"] if links else ""
        media, gallery_cols = parse_media(vitem)
        item = {
            "title": strip_tag_text(item_title.group(1)),
            "summary": strip_tag_text(item_desc.group(1)) if item_desc else "",
            "source": source,
        }
        if links:
            item["links"] = links
            item["url"] = links[0]["url"]
        if media:
            item["media"] = media
            if gallery_cols:
                item["galleryCols"] = gallery_cols
        items.append(item)
    if not items:
        return None
    return {
        "kind": "news",
        "layout": "rss",
        "label": "RSS 精选",
        "title": strip_tag_text(title.group(1)) if title else "值得关注的文章",
        "footnote": strip_tag_text(strip_tags(footnote.group(1))) if footnote else "",
        "items": items,
    }


def parse_analysis_prose(content: str) -> dict | None:
    match = re.search(r'<(?:section|div)\s+class="card span-4 card-highlight"', content)
    if not match:
        return None
    start = match.start()
    next_card = CARD_OPEN.search(content, start + 1)
    if next_card is None:
        return None
    block = content[start:next_card.start()]
    label = re.search(r'<div class="label-sm"[^>]*>([^<]+)</div>', block)
    label_text = strip_tag_text(label.group(1)) if label else "今日思考"
    intro = block
    if label:
        intro = block[label.end() :].strip()
    if not intro:
        return None
    return {
        "kind": "analysis",
        "layout": "prose",
        "label": label_text,
        "title": label_text,
        "intro": intro,
        "items": [{"title": label_text, "summary": strip_tag_text(strip_tags(intro))[:240]}],
    }


def parse_sources(content: str) -> list[dict]:
    block = section_between(content, "参考来源")
    sources: list[dict] = []
    if block:
        for url, title in re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', block, re.S):
            sources.append({"title": strip_tag_text(title), "url": url})
        if sources:
            return sources
    footer = re.search(r"📚 参考来源</div>(.*?)</div>\s*</div>\s*</div>", content, re.S)
    if footer:
        for url, title in re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', footer.group(1), re.S):
            sources.append({"title": strip_tag_text(title), "url": url})
    return sources


def builder_chunk(content: str) -> tuple[str, str]:
    start = content.find(MARKER_START.format(kind="builders"))
    end = content.find(MARKER_END.format(kind="builders"))
    if start != -1 and end != -1:
        chunk = content[start:end]
        layout = "tweet" if "tweet-card" in chunk else "vitem"
        return chunk, layout
    for label in BUILDER_LABELS:
        block = section_between(content, label)
        if block:
            layout = "tweet" if "tweet-card" in block else "vitem"
            return block, layout
    raise ValueError("Could not locate builders section")


def parse_tweet_metrics(block: str) -> dict | None:
    metrics_block = re.search(r'tweet-metrics">(.*?)</div>', block, re.S)
    if not metrics_block:
        return None
    fav = re.search(r"♥\s*([0-9,]+)", metrics_block.group(1))
    rt = re.search(r"↺\s*([0-9,]+)", metrics_block.group(1))
    rep = re.search(r"💬\s*([0-9,]+)", metrics_block.group(1))
    if not (fav or rt or rep):
        return None
    return {
        "favorites": int(fav.group(1).replace(",", "")) if fav else 0,
        "retweets": int(rt.group(1).replace(",", "")) if rt else 0,
        "replies": int(rep.group(1).replace(",", "")) if rep else 0,
    }


def parse_tweet_card_block(block: str, tweet_id: str) -> dict | None:
    handle = re.search(r'tweet-handle">@([^<]+)<', block)
    name = re.search(r'tweet-name">([^<]+)<', block)
    body = re.search(r'tweet-body">(.*?)</div>', block, re.S)
    translation = re.search(r'tweet-translation">(.*?)</div>', block, re.S)
    avatar = re.search(r'tweet-avatar" src="([^"]+)"', block)
    date_label = re.search(r'tweet-date">([^<]*)<', block)
    media, gallery_cols = parse_media(block)
    metrics = parse_tweet_metrics(block)
    item = {
        "title": strip_tag_text(name.group(1)) if name else handle.group(1) if handle else tweet_id,
        "builder": handle.group(1) if handle else "",
        "summary": strip_tag_text(body.group(1)) if body else "",
        "url": f"https://x.com/{handle.group(1) if handle else 'i'}/status/{tweet_id}",
        "tweetId": tweet_id,
    }
    if translation:
        item["translation"] = strip_tag_text(translation.group(1))
    if avatar and avatar.group(1).strip():
        item["avatar"] = avatar.group(1).strip()
    if date_label and date_label.group(1).strip():
        item["tweetDate"] = strip_tag_text(date_label.group(1))
    if media:
        item["media"] = media
        if gallery_cols:
            item["galleryCols"] = gallery_cols
    if metrics:
        item["metrics"] = metrics
    return item


def parse_builder_vitems(content: str) -> dict:
    chunk, layout = builder_chunk(content)
    title = re.search(r"<h2>(.*?)</h2>", chunk, re.S)
    label = "建造者动态"
    for candidate in BUILDER_LABELS:
        if f">{candidate}<" in chunk:
            label = candidate
            break
    items: list[dict] = []
    if layout == "tweet":
        for block in re.findall(r'(<a[^>]+class="tweet-card".*?</a>)', chunk, re.S):
            tweet_id = re.search(r"/status/(\d+)", block)
            if not tweet_id:
                continue
            parsed = parse_tweet_card_block(block, tweet_id.group(1))
            if parsed:
                items.append(parsed)
    else:
        for vitem in re.split(r'(?=<div class="vitem">)', chunk):
            if 'class="vitem"' not in vitem:
                continue
            parsed = parse_vitem(vitem)
            if parsed:
                items.append(parsed)
    return {
        "kind": "builders",
        "layout": layout,
        "label": label,
        "title": strip_tag_text(title.group(1)) if title else "今日 Builder 动态",
        "items": items,
    }


def ingest_html(html_path: Path) -> dict:
    content = html_path.read_text(encoding="utf-8")
    hero = parse_hero(content)
    sections: list[dict] = []
    highlights = parse_highlights(content)
    if highlights:
        sections.append(highlights)
    sections.extend(parse_podcasts(content))
    news = parse_news(content)
    if news:
        sections.append(news)
    sections.append(parse_builder_vitems(content))
    sources = parse_sources(content)
    analysis = parse_analysis_prose(content)
    if analysis:
        sections.append(analysis)
    return {
        "schemaVersion": 1,
        "date": re.search(r"(\d{4}-\d{2}-\d{2})", html_path.name).group(1),
        **hero,
        "sections": sections,
        **({"sources": sources} if sources else {}),
    }
