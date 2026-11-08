"""Validation for the portfolio source tree and built output.

`render.sh` runs the content checks before building and the output checks
after. Keeping the checks here means the build script stays a renderer.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
CARDS_DIR = CONTENT / "cards"
DATA_DIR = CONTENT / "data"
ASSETS = ROOT / "assets"
DIST = ROOT / "dist"

REQUIRED_SITE = ("name", "tagline", "intro", "email", "phone", "github")
REQUIRED_CARD = (
    "slug",
    "title",
    "kicker",
    "family",
    "summary",
    "order",
    "status",
    "audio",
    "description",
)
ALLOWED_STATUS = {"ready", "under-construction", "coming-soon", "placeholder"}
ALLOWED_FAMILIES = {"software", "nature", "neutral"}
INCLUDE_RE = re.compile(r"<!--\s*include:([\w:-]+)\s*-->")
KNOWN_INCLUDES = {
    "papers",
    "talks",
    "episodes",
    "repos",
    "photos",
    "contact",
    "videos:rescues",
    "videos:podcast-promos",
}
VIDEO_GROUPS = {"rescues", "podcast-promos"}


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


def validate_cards() -> list[str]:
    errors: list[str] = []
    cards = _load(errors, "cards.json")
    if cards is None:
        return errors
    if not isinstance(cards, list) or not cards:
        errors.append("cards.json: expected a non-empty list")
        return errors

    slugs: set[str] = set()
    orders: list[int] = []

    for index, card in enumerate(cards):
        if not _require(errors, card, REQUIRED_CARD, f"cards.json[{index}]"):
            continue

        slug = card["slug"]
        label = f"card '{slug}'"

        if slug in slugs:
            errors.append(f"{label}: duplicate slug")
        slugs.add(slug)

        if not isinstance(card.get("order"), int):
            errors.append(f"{label}: 'order' must be an integer")
        else:
            orders.append(card["order"])

        if card.get("status") not in ALLOWED_STATUS:
            errors.append(f"{label}: unknown status {card.get('status')!r}")

        if card.get("family") not in ALLOWED_FAMILIES:
            errors.append(f"{label}: unknown family {card.get('family')!r}")

        markdown = CARDS_DIR / f"{slug}.md"
        if not markdown.is_file():
            errors.append(f"{label}: missing {markdown.relative_to(ROOT)}")
        else:
            for match in INCLUDE_RE.finditer(markdown.read_text(encoding="utf-8")):
                if match.group(1) not in KNOWN_INCLUDES:
                    errors.append(f"{label}: unknown include 'include:{match.group(1)}'")

        if card.get("audio"):
            _file_exists(errors, card["audio"], label)

    if len(orders) != len(set(orders)):
        errors.append("cards.json: duplicate 'order' values")

    return errors


def validate_datasets() -> list[str]:
    errors: list[str] = []

    papers = _load(errors, "papers.json")
    if papers is not None:
        if not isinstance(papers, list) or not papers:
            errors.append("papers.json: expected a non-empty list")
        else:
            for index, paper in enumerate(papers):
                label = f"papers.json[{index}]"
                if not _require(errors, paper, ("id", "title", "role", "year"), label):
                    continue
                link = paper.get("link")
                if link is not None and not _is_http(link):
                    errors.append(f"{label}: 'link' must be an http(s) URL or null")
                year = paper.get("year")
                if not (isinstance(year, str) and len(year) == 4 and year.isdigit()):
                    errors.append(f"{label}: 'year' must be a four-digit string")

    talks = _load(errors, "talks.json")
    if talks is not None:
        if not isinstance(talks, list) or not talks:
            errors.append("talks.json: expected a non-empty list")
        else:
            for index, talk in enumerate(talks):
                label = f"talks.json[{index}]"
                if not _require(errors, talk, ("title", "url", "description", "date", "sort_date"), label):
                    continue
                if not _is_http(talk.get("url")):
                    errors.append(f"{label}: 'url' must be an http(s) URL")
                if not _valid_iso_date(talk.get("sort_date")):
                    errors.append(f"{label}: 'sort_date' must be YYYY-MM-DD or null")

    episodes = _load(errors, "episodes.json")
    if episodes is not None:
        if not isinstance(episodes, list) or not episodes:
            errors.append("episodes.json: expected a non-empty list")
        else:
            for index, episode in enumerate(episodes):
                label = f"episodes.json[{index}]"
                if not _require(
                    errors, episode, ("title", "url", "description", "date", "sort_date"), label
                ):
                    continue
                if not _is_http(episode.get("url")):
                    errors.append(f"{label}: 'url' must be an http(s) URL")
                if not _valid_iso_date(episode.get("sort_date")):
                    errors.append(f"{label}: 'sort_date' must be YYYY-MM-DD or null")

    repos = _load(errors, "repos.json")
    if repos is not None:
        if not isinstance(repos, list) or not repos:
            errors.append("repos.json: expected a non-empty list")
        else:
            for index, repo in enumerate(repos):
                label = f"repos.json[{index}]"
                if not _require(errors, repo, ("name", "url", "description", "pushed_at"), label):
                    continue
                if not _is_http(repo.get("url")):
                    errors.append(f"{label}: 'url' must be an http(s) URL")
                if not _valid_iso_moment(repo.get("pushed_at")):
                    errors.append(
                        f"{label}: 'pushed_at' must be an ISO timestamp or null"
                    )

    videos = _load(errors, "videos.json")
    if videos is not None:
        if not isinstance(videos, list) or not videos:
            errors.append("videos.json: expected a non-empty list")
        else:
            for index, video in enumerate(videos):
                label = f"videos.json[{index}]"
                if not _require(
                    errors,
                    video,
                    ("group", "title", "src", "youtube", "date", "description"),
                    label,
                ):
                    continue
                if video.get("group") not in VIDEO_GROUPS:
                    errors.append(f"{label}: unknown group {video.get('group')!r}")
                if not _valid_iso_date(video.get("date")):
                    errors.append(f"{label}: 'date' must be YYYY-MM-DD or null")
                youtube = video.get("youtube")
                if youtube:
                    if not isinstance(youtube, str):
                        errors.append(f"{label}: 'youtube' must be a string or null")
                elif video.get("src"):
                    _file_exists(errors, video["src"], label)
                else:
                    errors.append(f"{label}: needs either 'youtube' or 'src'")

    photos = _load(errors, "photos.json")
    if photos is not None:
        if not isinstance(photos, list) or not photos:
            errors.append("photos.json: expected a non-empty list")
        else:
            for index, photo in enumerate(photos):
                label = f"photos.json[{index}]"
                if not _require(errors, photo, ("src", "title", "caption", "date", "audio"), label):
                    continue
                if photo.get("src"):
                    _file_exists(errors, photo["src"], label)
                if not _valid_iso_date(photo.get("date")):
                    errors.append(f"{label}: 'date' must be YYYY-MM-DD or null")
                if photo.get("audio"):
                    _file_exists(errors, photo["audio"], label)

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
    """Non-fatal warnings for entries that cannot be sorted chronologically."""
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
            if isinstance(entry, dict) and not entry.get(field):
                warnings.append(_missing_date_warning(name, index, entry, field))

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
        return [f"{DIST.relative_to(ROOT)}: missing; run ./render.sh first"]

    cards_errors: list[str] = []
    cards = _load(cards_errors, "cards.json")
    if cards is None:
        return cards_errors

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
