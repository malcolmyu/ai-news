#!/usr/bin/env python3
"""Ingest daily HTML sections into Daily Source JSON."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from daily_ingest import ingest_html, parse_builder_vitems
from daily_source import (
    DATA_DIR,
    ROOT,
    date_from_html_path,
    get_section,
    load_digest,
    save_digest,
    section_key,
    upsert_section,
)


PRESERVE_KINDS = ("github",)


def ensure_digest(date: str, html_path: Path) -> dict:
    json_path = DATA_DIR / f"{date}.json"
    if json_path.exists():
        return load_digest(date)
    return ingest_html(html_path)


def reorder_sections(digest: dict) -> None:
    def sort_score(section: dict) -> int:
        kind, *rest = section_key(section)
        layout = rest[0]
        if kind == "analysis" and layout == "highlights":
            return 0
        if kind == "podcasts":
            return 1
        if kind == "news":
            return 2
        if kind == "builders":
            return 3
        if kind == "github":
            return 4
        if kind == "analysis" and layout == "prose":
            return 5
        return 6

    digest["sections"] = sorted(digest.get("sections", []), key=sort_score)


def merge_ingested(date: str, html_path: Path, *, sections: list[str] | None = None) -> dict:
    content = html_path.read_text(encoding="utf-8")
    digest = ensure_digest(date, html_path)
    ingested = ingest_html(html_path)

    digest["title"] = ingested["title"]
    digest["summary"] = ingested["summary"]
    digest["heroLabel"] = ingested.get("heroLabel", "")
    digest["tags"] = ingested.get("tags", [])
    digest["stats"] = ingested.get("stats", [])
    if ingested.get("sources"):
        digest["sources"] = ingested["sources"]

    selected = set(sections) if sections else None
    for section in ingested["sections"]:
        kind = section_key(section)[0]
        layout = section_key(section)[1]
        if kind == "builders":
            continue
        if selected and kind not in selected and f"{kind}:{layout}" not in selected:
            continue
        if kind in PRESERVE_KINDS and get_section(digest, kind):
            continue
        upsert_section(digest, section)

    if selected is None or "builders" in selected or any(k.startswith("builders:") for k in (selected or [])):
        builder = parse_builder_vitems(content)
        upsert_section(digest, builder)

    reorder_sections(digest)
    return digest


def run_render(date: str) -> None:
    render_script = ROOT / "scripts" / "render_daily.py"
    python_sh = ROOT / "scripts" / "python.sh"
    subprocess.run([str(python_sh), str(render_script), date], cwd=ROOT, check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest daily HTML into Daily Source JSON.")
    parser.add_argument("--date", help="Daily date in YYYY-MM-DD format")
    parser.add_argument("--from-html", dest="from_html", help="Daily HTML path")
    parser.add_argument(
        "--section",
        action="append",
        dest="sections",
        help="Only ingest selected section kinds (repeatable)",
    )
    parser.add_argument("--render", action="store_true", help="Render all sections after ingest")
    args = parser.parse_args(argv)

    html_path = Path(args.from_html) if args.from_html else None
    date = args.date or (date_from_html_path(html_path) if html_path else None)
    if not date or not html_path:
        parser.error("Provide --date and --from-html")
    if not html_path.exists():
        print(f"HTML path not found: {html_path}", file=sys.stderr)
        return 1

    digest = merge_ingested(date, html_path, sections=args.sections)
    save_digest(date, digest)
    print(f"Updated docs/daily/data/{date}.json")

    if args.render:
        run_render(date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
