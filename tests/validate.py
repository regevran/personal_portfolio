"""Validation for the portfolio source tree and built output.

CMake runs the content checks before building and the output checks after.
Keeping the checks here means the build script stays a renderer.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path

from src.site_schema import (
    BLOCK_TYPES,
    CARDS_DIR,
    DATA_DIR,
    DATASETS,
    is_visible,
    load_dataset,
    select_records,
)

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

REQUIRED_SITE = ("name", "tagline", "intro", "email", "phone", "github")
REQUIRED_CARD = (
    "title",
    "kicker",
    "family",
    "summary",
    "order",
    "status",
    "audio",
    "description",
    "blocks",
)
ALLOWED_STATUS = {"ready", "under-construction", "coming-soon", "placeholder"}
ALLOWED_FAMILIES = {"software", "nature", "neutral"}

DATASET_FIELDS = {
    "papers": ("id", "collections", "wg21", "title", "role", "year", "link"),
    "talks": (
        "id",
        "collections",
        "title",
        "url",
        "description",
        "date",
        "sort_date",
    ),
    "episodes": (
        "id",
        "collections",
        "title",
        "url",
        "date",
        "sort_date",
    ),
    "repos": (
        "id",
        "collections",
        "name",
        "url",
        "description",
        "pushed_at",
    ),
    "videos": (
        "id",
        "collections",
        "title",
        "species",
        "src",
        "youtube",
        "date",
        "description",
    ),
    "photos": (
        "id",
        "collections",
        "src",
        "title",
        "caption",
        "date",
        "audio",
    ),
}

# Datasets whose renderer understands a per-record Markdown description.
DESCRIPTION_SRC_TYPES = {"papers", "talks", "episodes", "repos"}


def _load(errors: list[str], name: str):
    path = DATA_DIR / name
    if not path.is_file():
        errors.append(f"{path.relative_to(ROOT)}: missing")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")
        return None


def _card_files(errors: list[str]) -> list[Path]:
    if not CARDS_DIR.is_dir():
        errors.append("content/cards: missing")
        return []
    files = sorted(CARDS_DIR.glob("*/card.json"))
    if not files:
        errors.append("content/cards: no card.json files")
    return files


def _load_card(errors: list[str], path: Path):
    try:
        card = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")
        return None
    if not isinstance(card, dict):
        errors.append(f"{path.relative_to(ROOT)}: expected an object")
        return None
    return card


def _file_exists(errors: list[str], relative: str, label: str) -> None:
    if not (ROOT / relative).is_file():
        errors.append(f"{label}: missing file {relative}")


def _require(errors: list[str], entry, fields, label: str) -> bool:
    if not isinstance(entry, dict):
        errors.append(f"{label}: expected an object")
        return False
    for field in fields:
        if field not in entry:
            errors.append(f"{label}: missing '{field}'")
    return True


def _is_http(value) -> bool:
    return isinstance(value, str) and value.startswith(("http://", "https://"))


def _valid_iso_date(value) -> bool:
    if value is None:
        return True
    try:
        date.fromisoformat(str(value))
        return True
    except (TypeError, ValueError):
        return False


def _valid_iso_moment(value) -> bool:
    if value is None:
        return True
    try:
        datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return True
    except (TypeError, ValueError):
        return False


def validate_site() -> list[str]:
    errors: list[str] = []
    site = _load(errors, "site.json")
    if isinstance(site, dict):
        for key in REQUIRED_SITE:
            if not site.get(key):
                errors.append(f"site.json: missing or empty '{key}'")
    return errors


def _validate_block(
    errors: list[str], block, card_dir: Path, label: str
) -> None:
    if not isinstance(block, dict):
        errors.append(f"{label}: expected an object")
        return

    block_type = block.get("type")
    if block_type not in BLOCK_TYPES:
        errors.append(f"{label}: unknown block type {block_type!r}")
        return

    if block_type == "prose":
        extra = set(block) - {"type", "src"}
        if extra:
            errors.append(f"{label}: unknown fields {sorted(extra)}")
        source = block.get("src")
        if not isinstance(source, str) or not source:
            errors.append(f"{label}: 'src' must be a non-empty string")
            return
        card_root = card_dir.resolve()
        target = (card_dir / source).resolve()
        try:
            target.relative_to(card_root)
        except ValueError:
            errors.append(f"{label}: 'src' escapes the card directory")
            return
        if not target.is_file():
            errors.append(f"{label}: missing {target.relative_to(ROOT)}")
        return

    if block_type == "contact":
        extra = set(block) - {"type"}
        if extra:
            errors.append(f"{label}: unknown fields {sorted(extra)}")
        return

    extra = set(block) - {"type", "select"}
    if extra:
        errors.append(f"{label}: unknown fields {sorted(extra)}")

    try:
        records = load_dataset(block_type)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{label}: cannot load {block_type}: {exc}")
        return

    try:
        select_records(records, block.get("select"))
    except ValueError as exc:
        errors.append(f"{label}: {exc}")


def validate_cards() -> list[str]:
    errors: list[str] = []
    orders: list[int] = []

    for card_file in _card_files(errors):
        card_dir = card_file.parent
        slug = card_dir.name
        label = f"card '{slug}'"
        card = _load_card(errors, card_file)
        if card is None:
            continue
        if not _require(errors, card, REQUIRED_CARD, label):
            continue

        if not isinstance(card.get("order"), int) or isinstance(card.get("order"), bool):
            errors.append(f"{label}: 'order' must be an integer")
        else:
            orders.append(card["order"])

        if card.get("status") not in ALLOWED_STATUS:
            errors.append(f"{label}: unknown status {card.get('status')!r}")

        if card.get("family") not in ALLOWED_FAMILIES:
            errors.append(f"{label}: unknown family {card.get('family')!r}")

        if card.get("audio"):
            _file_exists(errors, card["audio"], label)

        blocks = card.get("blocks")
        if not isinstance(blocks, list) or not blocks:
            errors.append(f"{label}: 'blocks' must be a non-empty list")
            continue
        for index, block in enumerate(blocks):
            _validate_block(errors, block, card_dir, f"{label} blocks[{index}]")

    if len(orders) != len(set(orders)):
        errors.append("content/cards: duplicate 'order' values")

    return errors


def _validate_collections(errors: list[str], entry: dict, label: str) -> None:
    collections = entry.get("collections")
    if not isinstance(collections, list):
        errors.append(f"{label}: 'collections' must be a list")
    elif not all(isinstance(name, str) and name for name in collections):
        errors.append(f"{label}: collection names must be non-empty strings")


def _validate_record_id(
    errors: list[str], entry: dict, label: str, seen: set[str]
) -> None:
    record_id = entry.get("id")
    if not isinstance(record_id, str) or not record_id:
        errors.append(f"{label}: 'id' must be a non-empty string")
    elif record_id in seen:
        errors.append(f"{label}: duplicate id {record_id!r}")
    else:
        seen.add(record_id)


def _validate_description(
    errors: list[str], entry: dict, label: str, dataset: str
) -> None:
    has_inline = entry.get("description") is not None
    has_source = entry.get("description_src") is not None

    if has_source and dataset not in DESCRIPTION_SRC_TYPES:
        errors.append(f"{label}: 'description_src' is not supported here")
        return

    if has_inline and has_source:
        errors.append(f"{label}: use either 'description' or 'description_src', not both")
        return

    if dataset == "episodes" and not has_inline and not has_source:
        errors.append(f"{label}: needs 'description' or 'description_src'")

    if not has_source:
        return

    source = entry["description_src"]
    if not isinstance(source, str) or not source:
        errors.append(f"{label}: 'description_src' must be a non-empty string")
        return
    data_root = DATA_DIR.resolve()
    target = (DATA_DIR / source).resolve()
    try:
        target.relative_to(data_root)
    except ValueError:
        errors.append(f"{label}: 'description_src' escapes content/data")
        return
    if not target.is_file():
        errors.append(f"{label}: missing {target.relative_to(ROOT)}")


def _validate_dataset_entry(
    errors: list[str], dataset: str, entry: dict, label: str
) -> None:
    if dataset == "papers":
        wg21 = entry.get("wg21")
        if not isinstance(wg21, str) or not wg21:
            errors.append(f"{label}: 'wg21' must be a non-empty string")
        year = entry.get("year")
        if not (isinstance(year, str) and len(year) == 4 and year.isdigit()):
            errors.append(f"{label}: 'year' must be a four-digit string")
        link = entry.get("link")
        if link is not None and not _is_http(link):
            errors.append(f"{label}: 'link' must be an http(s) URL or null")

    elif dataset == "talks":
        if not _is_http(entry.get("url")):
            errors.append(f"{label}: 'url' must be an http(s) URL")
        if not _valid_iso_date(entry.get("sort_date")):
            errors.append(f"{label}: 'sort_date' must be YYYY-MM-DD or null")

    elif dataset == "episodes":
        if not _is_http(entry.get("url")):
            errors.append(f"{label}: 'url' must be an http(s) URL")
        if not _valid_iso_date(entry.get("sort_date")):
            errors.append(f"{label}: 'sort_date' must be YYYY-MM-DD or null")

    elif dataset == "repos":
        if not _is_http(entry.get("url")):
            errors.append(f"{label}: 'url' must be an http(s) URL")
        if not _valid_iso_moment(entry.get("pushed_at")):
            errors.append(f"{label}: 'pushed_at' must be an ISO timestamp or null")

    elif dataset == "videos":
        if not _valid_iso_date(entry.get("date")):
            errors.append(f"{label}: 'date' must be YYYY-MM-DD or null")
        youtube = entry.get("youtube")
        if youtube is not None and not isinstance(youtube, str):
            errors.append(f"{label}: 'youtube' must be a string or null")
        elif not youtube:
            source = entry.get("src")
            if not isinstance(source, str) or not source:
                errors.append(f"{label}: needs either 'youtube' or 'src'")
            else:
                _file_exists(errors, source, label)

    elif dataset == "photos":
        source = entry.get("src")
        if not isinstance(source, str) or not source:
            errors.append(f"{label}: 'src' must be a non-empty string")
        else:
            _file_exists(errors, source, label)
        if not _valid_iso_date(entry.get("date")):
            errors.append(f"{label}: 'date' must be YYYY-MM-DD or null")
        if entry.get("audio"):
            _file_exists(errors, entry["audio"], label)


def validate_datasets() -> list[str]:
    errors: list[str] = []

    for dataset in DATASETS:
        records = _load(errors, DATASETS[dataset])
        if records is None:
            continue
        if not isinstance(records, list) or not records:
            errors.append(f"{DATASETS[dataset]}: expected a non-empty list")
            continue

        seen: set[str] = set()
        for index, entry in enumerate(records):
            label = f"{DATASETS[dataset]}[{index}]"
            if not _require(errors, entry, DATASET_FIELDS[dataset], label):
                continue
            _validate_record_id(errors, entry, label, seen)
            _validate_collections(errors, entry, label)
            _validate_description(errors, entry, label, dataset)
            _validate_dataset_entry(errors, dataset, entry, label)

    return errors


def validate_assets() -> list[str]:
    errors: list[str] = []
    for relative in (
        "assets/css/site.css",
        "assets/js/site.js",
        "assets/documents/README.md",
    ):
        _file_exists(errors, relative, "assets")
    return errors


def validate_content() -> list[str]:
    return (
        validate_site()
        + validate_cards()
        + validate_datasets()
        + validate_assets()
    )


def _where(name: str) -> str:
    return str((DATA_DIR / name).relative_to(ROOT))


def _missing_date_warning(name: str, index: int, entry, field: str) -> str:
    title = entry.get("title") or entry.get("name") or "?"
    placeholder = "YYYY-MM-DDTHH:MM:SSZ" if field == "pushed_at" else "YYYY-MM-DD"
    return (
        f'{_where(name)} [{index}] "{title}": missing "{field}" '
        f'(add "{field}": "{placeholder}")'
    )


def date_warnings() -> list[str]:
    """Non-fatal warnings for visible entries without a sortable date."""
    warnings: list[str] = []
    errors: list[str] = []

    datasets = (
        ("talks.json", "sort_date"),
        ("episodes.json", "sort_date"),
        ("videos.json", "date"),
        ("photos.json", "date"),
        ("repos.json", "pushed_at"),
    )
    for name, field in datasets:
        entries = _load(errors, name)
        if not isinstance(entries, list):
            continue
        for index, entry in enumerate(entries):
            if (
                isinstance(entry, dict)
                and is_visible(entry)
                and not entry.get(field)
            ):
                warnings.append(_missing_date_warning(name, index, entry, field))

    return warnings


def content_warnings() -> list[str]:
    """Non-fatal warnings about records and blocks that show nothing."""
    warnings: list[str] = []

    for dataset, filename in DATASETS.items():
        try:
            records = load_dataset(dataset)
        except (OSError, json.JSONDecodeError):
            continue
        for index, entry in enumerate(records):
            if not isinstance(entry, dict):
                continue
            collections = entry.get("collections")
            if not collections:
                title = entry.get("title") or entry.get("name") or "?"
                warnings.append(
                    f'{_where(filename)} [{index}] "{title}": no collections; '
                    "it is not shown anywhere"
                )

    for card_file in sorted(CARDS_DIR.glob("*/card.json")):
        try:
            card = json.loads(card_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        blocks = card.get("blocks")
        if not isinstance(blocks, list):
            continue
        for index, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue
            block_type = block.get("type")
            if block_type not in DATASETS:
                continue
            select = block.get("select")
            if not isinstance(select, dict) or "collection" not in select:
                continue
            collection = select.get("collection")
            try:
                selected = select_records(load_dataset(block_type), select)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if not selected:
                warnings.append(
                    f"{card_file.relative_to(ROOT)}: block[{index}] "
                    f"{block_type!r} selects empty collection {collection!r}"
                )

    return warnings


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.links.append(value)


EXTERNAL_PREFIXES = (
    "http://",
    "https://",
    "mailto:",
    "tel:",
    "#",
    "javascript:",
    "data:",
)


def validate_output() -> list[str]:
    errors: list[str] = []
    if not DIST.is_dir():
        return [
            f"{DIST.relative_to(ROOT)}: missing; "
            "run the site build first (cmake --build --preset default)"
        ]

    cards = []
    for card_file in sorted(CARDS_DIR.glob("*/card.json")):
        try:
            card = json.loads(card_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{card_file.relative_to(ROOT)}: {exc}")
            continue
        cards.append({"slug": card_file.parent.name, "card": card})

    index = DIST / "index.html"
    if not index.is_file():
        errors.append("dist/index.html: missing")

    for card in cards:
        page = DIST / card["slug"] / "index.html"
        if not page.is_file():
            errors.append(f"dist/{card['slug']}/index.html: missing")

    for page in sorted(DIST.rglob("*.html")):
        text = page.read_text(encoding="utf-8")
        relative_page = page.relative_to(ROOT)

        if "{{" in text:
            errors.append(f"{relative_page}: unreplaced template token")

        parser = _Links()
        parser.feed(text)
        for link in parser.links:
            if link.startswith(EXTERNAL_PREFIXES):
                continue
            target = link.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            resolved = (page.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"{relative_page}: broken link {link}")

    if index.is_file():
        index_text = index.read_text(encoding="utf-8")
        for card in cards:
            if f'{card["slug"]}/index.html' not in index_text:
                errors.append(f"dist/index.html: missing link for {card['slug']}")

    return errors
