"""Daily Source JSON load/save helpers shared by render and ingest scripts."""
from __future__ import annotations

import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DAILY_DIR = DOCS / "daily"
DATA_DIR = DAILY_DIR / "data"
SCHEMA_PATH = DOCS / "agents" / "contracts" / "daily-digest.schema.json"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_digest(data: dict) -> None:
    schema = load_schema()
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda err: err.path)
    if errors:
        messages = [f"- {'/'.join(map(str, err.path)) or '$'}: {err.message}" for err in errors[:5]]
        raise ValueError("Daily digest JSON failed schema validation:\n" + "\n".join(messages))


def digest_path(date: str) -> Path:
    return DATA_DIR / f"{date}.json"


def load_digest(date: str, *, validate: bool = True) -> dict:
    path = digest_path(date)
    if not path.exists():
        raise FileNotFoundError(f"Missing daily source JSON: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if validate:
        validate_digest(data)
    return data


def save_digest(date: str, data: dict) -> Path:
    validate_digest(data)
    path = digest_path(date)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


DEFAULT_SECTION_LAYOUT = {
    "builders": "vitem",
    "github": "simple",
    "news": "rss",
    "podcasts": "embed",
    "analysis": "prose",
}


def section_key(section: dict) -> tuple:
    kind = section["kind"]
    layout = section.get("layout") or DEFAULT_SECTION_LAYOUT.get(kind, "vitem")
    if kind == "podcasts":
        return kind, layout, section.get("label", "")
    return kind, layout


def upsert_section(digest: dict, section: dict) -> dict:
    key = section_key(section)
    sections = digest.setdefault("sections", [])
    for index, existing in enumerate(sections):
        if section_key(existing) == key:
            sections[index] = section
            return digest
    sections.append(section)
    return digest


def get_section(digest: dict, kind: str) -> dict | None:
    for section in digest.get("sections", []):
        if section.get("kind") == kind:
            return section
    return None


def date_from_html_path(path: Path) -> str | None:
    match = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
    return match.group(1) if match else None


def load_daily_metadata(html_path: Path) -> dict | None:
    date = date_from_html_path(html_path)
    if not date:
        return None
    path = digest_path(date)
    if not path.exists():
        return None
    try:
        data = load_digest(date, validate=False)
    except (json.JSONDecodeError, ValueError):
        return None
    return {
        "date": data.get("date") or date,
        "title": data.get("title", ""),
        "summary": data.get("summary", ""),
    }
