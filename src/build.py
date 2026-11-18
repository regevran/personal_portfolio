#!/usr/bin/env python3
"""Render the static portfolio into dist/.

Card directories in content/cards/ define the pages and their ordered blocks;
datasets in content/data/ are selected by collection or explicit id. This
script only composes them; validation lives in tests/.
"""

from __future__ import annotations

import html
import re
import shutil
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path

from src.media import MEDIA
from src.site_schema import (
    DATA_DIR,
    load_cards,
    load_dataset,
    load_site,
    load_species,
    select_records,
)

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
ASSETS = ROOT / "assets"
DIST = ROOT / "dist"

STATUS_LABELS = {
    "ready": "",
    "under-construction": "Under construction",
    "coming-soon": "Coming soon",
    "placeholder": "Placeholder",
}

PLATFORM_LABELS = {
    "spotify": "Spotify",
    "apple": "Apple Podcasts",
    "pocketcasts": "Pocket Casts",
}
PLATFORM_ICONS = {
    "spotify": "assets/icons/spotify.svg",
    "apple": "assets/icons/applepodcasts.svg",
    "pocketcasts": "assets/icons/pocketcasts.svg",
}
PLATFORM_ORDER = ("spotify", "apple", "pocketcasts")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def read_template(relative: str) -> str:
    return (TEMPLATES / relative).read_text(encoding="utf-8")


def render_template(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def status_badge(status: str) -> str:
    label = STATUS_LABELS.get(status, "")
    if not label:
        return ""
    return f'<span class="badge badge-{esc(status)}">{esc(label)}</span>'


MARKDOWN_LINK_ATTR = re.compile(r'(?P<attr>\s(?:href|src)=")(?P<url>[^"]*)(?P<quote>")')
ABSOLUTE_URL = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def root_relative_url(url: str, root: str) -> str:
    """Turn a source-root-relative path into a page-relative URL."""
    if not root:
        return url
    if url.startswith(("#", "?", "/")) or url.startswith("../") or ABSOLUTE_URL.match(url):
        return url
    if url.startswith("./"):
        url = url[2:]
    return root + url


def asset_url(relative: str, root: str) -> str:
    """Return an R2 URL for hosted media, otherwise a page-relative URL."""
    if MEDIA.is_remote(relative):
        return MEDIA.remote_url(relative)
    return root_relative_url(relative, root)


def rewrite_markdown_links(page: str, root: str) -> str:
    """Point relative links at their page root, or at R2 for hosted media.

    Content paths are written relative to the site root (`assets/foo.pdf`),
    while card pages live one directory down (`engineering/`), so local links
    add `../` and hosted media becomes an absolute R2 URL.
    """

    def replace(match: re.Match) -> str:
        url = html.unescape(match.group("url"))
        rewritten = asset_url(url, root)
        if rewritten == url:
            return match.group(0)
        return match.group("attr") + esc(rewritten) + match.group("quote")

    return MARKDOWN_LINK_ATTR.sub(replace, page)


ANCHOR_TAG = re.compile(r"<a\b(?P<attrs>[^>]*)>", re.IGNORECASE)
HREF_VALUE = re.compile(r'href="(?P<url>[^"]*)"', re.IGNORECASE)
TARGET_ATTR = re.compile(r'\starget="', re.IGNORECASE)
REL_ATTR = re.compile(r'\srel="', re.IGNORECASE)


def open_external_links_in_new_tabs(page: str) -> str:
    """Open http(s) links in a new tab; leave internal links alone."""

    def replace(match: re.Match) -> str:
        attrs = match.group("attrs")
        href = HREF_VALUE.search(attrs)
        if not href:
            return match.group(0)
        url = html.unescape(href.group("url"))
        if not url.startswith(("http://", "https://")):
            return match.group(0)
        extra = ""
        if not TARGET_ATTR.search(attrs):
            extra += ' target="_blank"'
        if not REL_ATTR.search(attrs):
            extra += ' rel="noopener"'
        if not extra:
            return match.group(0)
        return "<a" + attrs + extra + ">"

    return ANCHOR_TAG.sub(replace, page)


def markdown_to_html(path: Path, root: str = "") -> str:
    result = subprocess.run(
        ["pandoc", "-f", "markdown+smart", "-t", "html5", "--wrap=none", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return open_external_links_in_new_tabs(
        rewrite_markdown_links(result.stdout, root)
    )


def markdown_to_text(path: Path) -> str:
    result = subprocess.run(
        ["pandoc", "-f", "markdown+smart", "-t", "plain", "--wrap=none", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return re.sub(r"\s+", " ", result.stdout).strip()


def card_markdown(card: dict, filename: str) -> Path:
    path = card["dir"] / filename
    if not path.is_file():
        raise SystemExit(f"build.py: missing {path.relative_to(ROOT)}")
    if not path.read_text(encoding="utf-8").strip():
        raise SystemExit(f"build.py: empty {path.relative_to(ROOT)}")
    return path


def iso_date(value):
    """Return a date for sorting, or None when the value is absent/invalid."""
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


MONTHS = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)


def display_date(value):
    """Human date for card metadata, or an empty string."""
    parsed = iso_date(value)
    if not parsed:
        return ""
    return f"{parsed.day} {MONTHS[parsed.month - 1]} {parsed.year}"


def iso_moment(value):
    """Return a naive UTC datetime for sorting an ISO timestamp, or None."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def sort_latest(entries, key):
    """Sort newest first, keeping undated entries at the end and stable."""
    dated = []
    undated = []
    for entry in entries:
        value = key(entry)
        if value is None:
            undated.append(entry)
        else:
            dated.append((value, entry))
    dated.sort(key=lambda pair: pair[0], reverse=True)
    return [entry for _, entry in dated] + undated


def description_html(entry: dict, root: str = "") -> str:
    """Render an inline description or a per-record Markdown description."""
    source = entry.get("description_src")
    if source:
        return markdown_to_html(DATA_DIR / source, root).strip()
    description = entry.get("description")
    return esc(description) if description else ""


CPP_LOGO = "assets/icons/cpp-logo.svg"
PAPER_ICON = "assets/icons/paper.svg"
TALK_BADGE = "assets/icons/conference-badge.svg"
EXTERNAL_ICON = "assets/icons/external.svg"
YOUTUBE_ICON = "assets/icons/youtube.svg"
BOOK_ICON = "assets/icons/book.svg"
DOWNLOAD_ICON = "assets/icons/download.svg"
LEARNING_AID_ICON = "assets/icons/learning-aid.svg"


def paper_rail(paper: dict, root: str) -> str:
    mark = '<span class="paper-mark" aria-hidden="true"></span>'
    url = paper.get("link")
    if not url:
        return f'<span class="paper-rail">{mark}</span>'
    title = paper.get("title", "")
    link = (
        f'<a class="paper-link" href="{esc(url)}" '
        f'aria-label="Open {esc(title)} on wg21.link" '
        f'title="Open {esc(title)} on wg21.link" target="_blank" rel="noopener">'
        f'<img src="{esc(asset_url(PAPER_ICON, root))}" alt="" aria-hidden="true">'
        "</a>"
    )
    return f'<span class="paper-rail">{mark}{link}</span>'


def render_papers(records: list[dict], root: str) -> str:
    items = []
    for paper in records:
        title_html = (
            f'<a href="{esc(paper["link"])}" target="_blank" rel="noopener">'
            f'{esc(paper["title"])}</a>'
            if paper.get("link")
            else esc(paper["title"])
        )
        role_year = " · ".join(
            str(part)
            for part in (paper.get("role"), paper.get("year"))
            if part
        )
        submeta_html = (
            f'<span class="item-submeta">{esc(role_year)}</span>'
            if role_year
            else ""
        )
        description = description_html(paper, root)
        desc_html = f'<div class="item-desc">{description}</div>' if description else ""
        items.append(
            f'<li class="item" data-paper="{esc(paper["id"])}">'
            '<span class="item-head">'
            f'<span class="item-title">{title_html}</span>'
            f'<span class="item-meta">{esc(paper.get("wg21", ""))}</span>'
            "</span>"
            f"{submeta_html}{desc_html}{paper_rail(paper, root)}</li>"
        )
    return '<ul class="item-list">' + "".join(items) + "</ul>"


YOUTUBE_ID = re.compile(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})")


def youtube_id(value: object) -> str:
    text = str(value or "")
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", text):
        return text
    match = YOUTUBE_ID.search(text)
    return match.group(1) if match else ""


def talk_media(talk: dict) -> str:
    video_id = youtube_id(talk.get("youtube"))
    if not video_id:
        return ""
    title = talk.get("title", "")
    watch = f"https://www.youtube.com/watch?v={video_id}"
    embed = f"https://www.youtube.com/embed/{video_id}"
    return (
        '<div class="talk-media">'
        f'<a class="talk-video" href="{esc(watch)}" '
        f'aria-label="Play {esc(title)}" '
        f'data-embed="{esc(embed)}" data-title="{esc(title)}" '
        'target="_blank" rel="noopener">'
        f'<img src="https://i.ytimg.com/vi/{esc(video_id)}/hqdefault.jpg" '
        'alt="" loading="lazy">'
        '<span class="talk-play" aria-hidden="true"></span>'
        "</a></div>"
    )


def talk_links(talk: dict, root: str) -> str:
    title = talk.get("title", "")
    links = []

    video_id = youtube_id(talk.get("youtube"))
    if video_id:
        links.append(
            f'<a class="talk-link talk-link--youtube" '
            f'href="https://www.youtube.com/watch?v={esc(video_id)}" '
            f'aria-label="Watch {esc(title)} on YouTube" '
            f'title="Watch on YouTube" target="_blank" rel="noopener">'
            f'<img src="{esc(asset_url(YOUTUBE_ICON, root))}" alt="" aria-hidden="true">'
            "</a>"
        )

    slides = talk.get("slides")
    if slides:
        links.append(
            f'<a class="talk-link talk-link--slides" href="{esc(slides)}" '
            f'aria-label="Open {esc(title)} slides" title="Slides" '
            'target="_blank" rel="noopener">'
            f'<img src="{esc(asset_url(PAPER_ICON, root))}" alt="" aria-hidden="true">'
            "<span>Slides</span></a>"
        )

    if not links and talk.get("url"):
        links.append(
            f'<a class="talk-link talk-link--origin" '
            f'href="{esc(talk["url"])}" '
            f'aria-label="Open {esc(title)} at its origin" '
            f'title="Open origin" target="_blank" rel="noopener">'
            f'<img src="{esc(asset_url(EXTERNAL_ICON, root))}" alt="" aria-hidden="true">'
            "</a>"
        )

    if not links:
        return ""
    return '<div class="talk-links">' + "".join(links) + "</div>"


def render_talks(records: list[dict], root: str) -> str:
    items = []
    for talk in records:
        title = talk.get("title", "")
        media = talk_media(talk)
        date = talk.get("date", "")
        meta_html = f'<span class="item-meta">{esc(date)}</span>' if date else ""
        description = description_html(talk, root)
        desc_html = f'<div class="item-desc">{description}</div>' if description else ""
        variant = "talk-card--video" if media else "talk-card--text"
        items.append(
            f'<li class="item talk-card {variant}" data-talk="{esc(talk["id"])}">'
            '<div class="talk-copy">'
            '<span class="talk-stamp" aria-hidden="true"></span>'
            f"{meta_html}"
            f'<h2 class="item-title">{esc(title)}</h2>'
            f"{desc_html}</div>"
            f"{media}{talk_links(talk, root)}</li>"
        )
    return '<ul class="item-list">' + "".join(items) + "</ul>"


def episode_links(episode: dict, root: str) -> str:
    links = episode.get("links")
    if not isinstance(links, dict):
        return ""
    anchors = []
    for platform in PLATFORM_ORDER:
        url = links.get(platform)
        if not url:
            continue
        label = PLATFORM_LABELS[platform]
        icon = PLATFORM_ICONS[platform]
        anchors.append(
            f'<a class="episode-link episode-link--{platform}" '
            f'href="{esc(url)}" aria-label="{esc(label)}" '
            f'title="{esc(label)}" target="_blank" rel="noopener">'
            f'<img src="{esc(asset_url(icon, root))}" alt="" aria-hidden="true">'
            "</a>"
        )
    return '<span class="episode-links">' + "".join(anchors) + "</span>"


def episode_rail(episode: dict, root: str) -> str:
    return (
        '<span class="episode-rail">'
        '<span class="episode-mic" aria-hidden="true"></span>'
        f'{episode_links(episode, root)}'
        "</span>"
    )


def render_episodes(records: list[dict], root: str) -> str:
    items = []
    for episode in records:
        description = description_html(episode, root)
        items.append(
            '<li class="item">'
            '<span class="item-head">'
            f'<span class="item-title">{esc(episode["title"])}</span>'
            f'<span class="item-meta">{esc(episode.get("date", ""))}</span>'
            "</span>"
            f'<div class="item-desc">{description}</div>'
            f'{episode_rail(episode, root)}</li>'
        )
    return '<ul class="item-list">' + "".join(items) + "</ul>"


GITHUB_ICON = "assets/icons/github.svg"


def repo_rail(repo: dict, root: str) -> str:
    mark = (
        '<span class="repo-tag" aria-hidden="true">'
        '<span class="repo-tag-line">'
        '<span class="repo-tag-step">[ 20%]</span> Building CXX object'
        "</span>"
        '<span class="repo-tag-line">'
        '<span class="repo-tag-step">[100%]</span> Linking CXX executable'
        "</span>"
        "</span>"
    )
    url = repo.get("url")
    if not url:
        return f'<span class="repo-rail">{mark}</span>'
    name = repo.get("name", "")
    link = (
        f'<a class="repo-link" href="{esc(url)}" '
        f'aria-label="{esc(name)} on GitHub" '
        f'title="{esc(name)} on GitHub" target="_blank" rel="noopener">'
        f'<img src="{esc(asset_url(GITHUB_ICON, root))}" alt="" aria-hidden="true">'
        "</a>"
    )
    return f'<span class="repo-rail">{mark}{link}</span>'


def render_repos(records: list[dict], root: str) -> str:
    items = []
    for repo in records:
        meta = ""
        pushed_at = repo.get("pushed_at")
        if pushed_at:
            meta = f"Last push: {str(pushed_at)[:10]}"
        name_html = (
            f'<a href="{esc(repo["url"])}" target="_blank" rel="noopener">'
            f'{esc(repo["name"])}</a>'
            if repo.get("url")
            else esc(repo["name"])
        )
        meta_html = f'<span class="item-meta">{esc(meta)}</span>' if meta else ""
        description = description_html(repo, root)
        repo_id = esc(repo["id"])
        desc_id = f"repo-desc-{repo_id}"
        items.append(
            f'<li class="item" data-repo="{repo_id}">'
            '<span class="item-head">'
            f'<span class="item-title">{name_html}</span>'
            f"{meta_html}</span>"
            f'<div class="item-desc" id="{desc_id}">{description}</div>'
            '<button class="repo-toggle" type="button" aria-expanded="false" '
            f'aria-controls="{desc_id}">More…</button>'
            f"{repo_rail(repo, root)}</li>"
        )
    return '<ul class="item-list">' + "".join(items) + "</ul>"


def video_poster(video: dict, root: str) -> str:
    source = video.get("poster")
    if not source:
        photos = video.get("photos") or []
        source = photos[0] if photos else ""
    return f' poster="{esc(asset_url(source, root))}"' if source else ""


def video_media(video: dict, root: str) -> str:
    youtube = video.get("youtube")
    if youtube:
        source = (
            youtube
            if str(youtube).startswith("http")
            else f"https://www.youtube.com/embed/{youtube}"
        )
        return (
            f'<iframe src="{esc(source)}" title="{esc(video["title"])}" '
            'loading="lazy" allowfullscreen></iframe>'
        )
    return (
        f'<video controls preload="metadata"{video_poster(video, root)} '
        f'src="{esc(asset_url(video["src"], root))}"></video>'
    )


def rescue_reel(video: dict, root: str) -> str:
    photos = video.get("photos") or []
    if not photos:
        return ""
    total = len(photos)
    cards = []
    for index, source in enumerate(photos):
        active = " is-presented" if index == 0 else ""
        pressed = "true" if index == 0 else "false"
        tabindex = "0" if index == 0 else "-1"
        cards.append(
            f'<button class="stack-card{active}" type="button" data-reel-card '
            f'style="--depth: {index}; z-index: {total - index}" '
            f'tabindex="{tabindex}" aria-pressed="{pressed}" '
            f'aria-label="Photo {index + 1} of {total}: '
            f'{esc(video["title"])}">'
            f'<img src="{esc(asset_url(source, root))}" alt="" loading="lazy">'
            "</button>"
        )
    return f'<div class="rescue-stack" data-reel>{"".join(cards)}</div>'


def render_videos(records: list[dict], root: str) -> str:
    cards = []
    for video in records:
        species = ""
        if video.get("species"):
            species = f'<span class="media-meta">{esc(video["species"])}</span>'
        description = description_html(video, root)
        desc_html = (
            f'<div class="item-desc">{description}</div>' if description else ""
        )
        cards.append(
            f'<figure class="media-card" data-video="{esc(video["id"])}">'
            f'{video_media(video, root)}<figcaption>'
            f'<span class="media-title">{esc(video["title"])}</span>'
            f"{species}{desc_html}</figcaption></figure>"
        )
    return '<div class="media-grid media-grid--videos">' + "".join(cards) + "</div>"


def render_rescue_rows(records: list[dict], root: str) -> str:
    rows = []
    for video in records:
        species = ""
        if video.get("species"):
            species = f'<span class="media-meta">{esc(video["species"])}</span>'
        description = description_html(video, root)
        desc_html = (
            f'<div class="item-desc">{description}</div>' if description else ""
        )
        reel = rescue_reel(video, root)
        extra = "" if reel else " rescue-row--no-photos"
        rows.append(
            f'<article class="rescue-row{extra}" '
            f'data-video="{esc(video["id"])}">'
            '<div class="rescue-copy">'
            '<div class="rescue-head">'
            f'<img class="rescue-row-mark" src="{esc(asset_url(RESCUE_ICON, root))}" '
            'alt="" aria-hidden="true">'
            f'<h2 class="media-title">{esc(video["title"])}</h2>'
            "</div>"
            f"{species}{desc_html}"
            "</div>"
            f'<div class="rescue-photos">{reel}</div>'
            f'<div class="rescue-media">{video_media(video, root)}</div>'
            "</article>"
        )
    return '<div class="rescue-list">' + "".join(rows) + "</div>"


BIRD_RING = "assets/icons/bird-ring.svg"
RESCUE_ICON = "assets/icons/rescue.svg"


def photo_card(photo: dict, root: str) -> str:
    media = (
        f'<img src="{esc(asset_url(photo["src"], root))}" '
        f'alt="{esc(photo["title"])}" loading="lazy">'
    )
    audio = ""
    if photo.get("audio"):
        audio = (
            f'<audio controls preload="none" '
            f'src="{esc(asset_url(photo["audio"], root))}"></audio>'
        )
    caption = photo.get("caption", "")
    parts = [f'<span class="media-title">{esc(photo["title"])}</span>']
    if caption:
        parts.append(f'<span class="media-meta">{esc(caption)}</span>')
    return (
        f'<figure class="media-card">{media}<figcaption>'
        + "".join(parts)
        + audio
        + "</figcaption></figure>"
    )


def species_group(
    species: dict[str, dict] | None, key: str, root: str
) -> tuple[str, str]:
    """Return the display name and rendered note for a grouping key."""
    record = species.get(key) if species else None
    if not record:
        return key, ""
    label = record.get("name") or key
    source = record.get("note_src")
    note = markdown_to_html(DATA_DIR / source, root) if source else ""
    return label, note


def render_photos(
    records: list[dict],
    root: str,
    group_by: str | None = None,
    species: dict[str, dict] | None = None,
) -> str:
    if not group_by:
        cards = [photo_card(photo, root) for photo in records]
        return (
            '<div class="media-grid media-grid--photos">'
            + "".join(cards)
            + "</div>"
        )

    groups: dict[str, list[dict]] = {}
    order: list[str] = []
    for photo in records:
        key = str(photo.get(group_by) or "Other")
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(photo)

    sections = []
    for key in order:
        photos = groups[key]
        total = len(photos)
        count = "1 photo" if total == 1 else f"{total} photos"
        dates: list[str] = []
        for photo in photos:
            stamp = display_date(photo.get("date"))
            if stamp and stamp not in dates:
                dates.append(stamp)
        meta = " · ".join([count] + dates)
        label, note = species_group(species, key, root)
        cards = []
        for index in range(total):
            active = " is-presented" if index == 0 else ""
            pressed = "true" if index == 0 else "false"
            cards.append(
                f'<button class="deck-card{active}" type="button" data-card '
                f'style="--i: {index}" aria-pressed="{pressed}" '
                f'aria-label="Show photo {index + 1} of {total}: '
                f'{esc(photos[index]["title"])}">'
                f'<img src="{esc(asset_url(photos[index]["src"], root))}" alt="" '
                'loading="lazy">'
                "</button>"
            )
        note_html = f'<div class="deck-note">{note}</div>' if note else ""
        sections.append(
            f'<section class="species-deck" data-deck '
            f'data-species="{esc(key)}" data-count="{total}">'
            '<div class="deck-cards">'
            + "".join(cards)
            + "</div>"
            '<div class="deck-base">'
            '<header class="deck-head">'
            f'<img class="ring-mark" src="{esc(asset_url(BIRD_RING, root))}" '
            'alt="" aria-hidden="true">'
            f'<h2 class="deck-species">{esc(label)}</h2>'
            f'<span class="deck-meta">{esc(meta)}</span>'
            "</header>"
            f"{note_html}"
            "</div></section>"
        )
    return '<div class="species-decks">' + "".join(sections) + "</div>"


def phone_tel(phone: object) -> str:
    return re.sub(r"[^0-9+]", "", str(phone))


def render_topbar(site: dict, home: str, nav_root: str) -> str:
    template = read_template("partials/topbar.html")
    return render_template(
        template,
        {
            "SITE_NAME": esc(site["name"]),
            "HOME": esc(home),
            "NAV_ABOUT": esc(f"{nav_root}#about"),
            "NAV_WORK": esc(f"{nav_root}#work"),
            "NAV_NATURE": esc(f"{nav_root}#nature"),
            "NAV_CONTACT": esc(f"{nav_root}#contact"),
            "EMAIL": esc(site["email"]),
            "PHONE": esc(site["phone"]),
            "PHONE_TEL": esc(phone_tel(site["phone"])),
        },
    )


def render_footer(site: dict, year: str) -> str:
    template = read_template("partials/footer.html")
    return render_template(
        template,
        {
            "YEAR": esc(year),
            "SITE_NAME": esc(site["name"]),
            "FOOTER": esc(site["footer"]),
        },
    )


def render_logo(card: dict, root: str) -> str:
    source = card.get("logo")
    if not source:
        return ""
    alt = card.get("logo_alt") or f'{card["title"]} logo'
    return (
        f'<img class="card-page-logo" src="{esc(asset_url(source, root))}" '
        f'alt="{esc(alt)}">'
    )


def render_card_mark(card: dict, root: str) -> str:
    mark = card.get("mark")
    if mark == "github-logo":
        return (
            f'<img class="github-mark" src="{esc(asset_url(GITHUB_ICON, root))}" '
            'alt="" aria-hidden="true">'
        )
    if mark == "cpp-logo":
        return (
            f'<img class="cpp-logo" src="{esc(asset_url(CPP_LOGO, root))}" '
            'alt="" aria-hidden="true">'
        )
    if mark == "conference-badge":
        return (
            f'<img class="conference-mark" src="{esc(asset_url(TALK_BADGE, root))}" '
            'alt="" aria-hidden="true">'
        )
    if mark == "ringing-station":
        return (
            f'<img class="ring-band" src="{esc(asset_url(BIRD_RING, root))}" '
            'alt="" aria-hidden="true">'
        )
    if mark == "rescue":
        return (
            f'<img class="rescue-mark" src="{esc(asset_url(RESCUE_ICON, root))}" '
            'alt="" aria-hidden="true">'
        )
    if mark == "book":
        return (
            f'<img class="book-mark" src="{esc(asset_url(BOOK_ICON, root))}" '
            'alt="" aria-hidden="true">'
        )
    if mark == "learning-aid":
        return (
            f'<img class="learn-mark" '
            f'src="{esc(asset_url(LEARNING_AID_ICON, root))}" '
            'alt="" aria-hidden="true">'
        )
    return ""


def page_stylesheet(slug: str, root: str) -> str:
    if not (ASSETS / "css" / "pages" / f"{slug}.css").is_file():
        return ""
    relative = f"assets/css/pages/{slug}.css"
    return f'<link rel="stylesheet" href="{esc(asset_url(relative, root))}">'


def render_contact(site: dict) -> str:
    template = read_template("partials/contact.html")
    phone = str(site["phone"])
    return render_template(
        template,
        {
            "NAME": esc(site["name"]),
            "EMAIL": esc(site["email"]),
            "PHONE": esc(phone),
            "PHONE_TEL": esc(phone_tel(phone)),
        },
    )


def fmt_num(value) -> str:
    number = float(value)
    return str(int(number)) if number.is_integer() else str(number)


def tagline_lines(tagline: str) -> str:
    parts = [part.strip() for part in tagline.split(".") if part.strip()]
    return "<br>".join(esc(part + ".") for part in parts)


def board_item_style(board: dict) -> str:
    parts = [f"--x: {fmt_num(board['x'])}%"]
    if "y" in board:
        parts.append(f"--y: {fmt_num(board['y'])}%")
    else:
        parts.append(f"--bottom: {fmt_num(board['bottom'])}%")
    parts.append(f"--tilt: {fmt_num(board['tilt'])}deg")
    return "; ".join(parts) + ";"


def render_board_card(card: dict, templates: dict[str, str]) -> str:
    board = card["board"]
    family = card["family"]
    item_class = {
        "nature": " board-item--nature",
        "software": " board-item--software",
        "neutral": " board-item--neutral board-item--bottom",
    }[family]
    item_id = f' id="{esc(board["id"])}"' if board.get("id") else ""
    scrap = {"nature": "sign", "software": "monitor", "neutral": "plain"}[family]

    anchor = board["anchor"]
    if anchor == "perch":
        robin = board["robin"]
        robin_style = f"--robin-tilt: {fmt_num(robin['tilt'])}deg"
        if robin["flip"]:
            robin_style += "; --robin-flip: -1"
        rig = render_template(
            templates["perch"], {"ROBIN_STYLE": robin_style, "ROOT": ""}
        )
    elif anchor == "lanyard":
        rig = templates["lanyard"]
    else:
        rig = ""

    return render_template(
        templates["board_card"],
        {
            "ITEM_CLASS": item_class,
            "ITEM_ID": item_id,
            "ITEM_STYLE": board_item_style(board),
            "RIG": rig,
            "SCRAP": scrap,
            "MARK": esc(card.get("mark", "")),
            "SLUG": esc(card["slug"]),
            "KICKER": esc(card["kicker"]),
            "TITLE": esc(card["title"]),
        },
    )


SORT_KEYS = {
    "papers": lambda paper: date(int(paper["year"]), 1, 1),
    "talks": lambda talk: iso_date(talk.get("sort_date")),
    "episodes": lambda episode: iso_date(episode.get("sort_date")),
    "repos": lambda repo: iso_moment(repo.get("pushed_at")),
    "videos": lambda video: iso_date(video.get("date")),
    "photos": lambda photo: iso_date(photo.get("date")),
}

RENDERERS = {
    "papers": render_papers,
    "talks": render_talks,
    "episodes": render_episodes,
    "repos": render_repos,
    "videos": render_videos,
    "photos": render_photos,
}


def render_dataset(
    name: str,
    select: dict,
    root: str,
    group_by: str | None = None,
    layout: str | None = None,
) -> str:
    records = select_records(load_dataset(name), select)
    if "ids" not in select:
        records = sort_latest(records, SORT_KEYS[name])
    if name == "videos" and layout == "rescue-rows":
        return render_rescue_rows(records, root)
    if name == "photos" and group_by:
        species = (
            {record["id"]: record for record in load_species()}
            if group_by == "species"
            else None
        )
        return render_photos(records, root, group_by, species)
    return RENDERERS[name](records, root)


def render_book(block: dict, root: str) -> str:
    """Render the PDF download and the right-to-left pdflip viewer."""
    pdf = block["pdf"]
    note = block.get("note", "")
    page_offset = block.get("page_offset", 0)
    numbered_pages = block.get("numbered_pages")
    download_name = block.get("download_name") or Path(pdf).name
    pdf_url = asset_url(pdf, root)
    icon = asset_url(DOWNLOAD_ICON, root)
    vendor_js = asset_url("assets/vendor/pdflip/pdflip.global.js", root)
    book_js = asset_url("assets/js/pages/book.js", root)
    meta = (
        f'<span class="book-download-meta">{esc(note)}</span>' if note else ""
    )
    numbering = ""
    max_attr = ""
    if numbered_pages:
        numbering = (
            f' data-book-page-offset="{page_offset}"'
            f' data-book-numbered-pages="{numbered_pages}"'
        )
        max_attr = f' max="{numbered_pages}"'

    return (
        '<div class="book-actions">'
        f'<a class="book-download" href="{esc(pdf_url)}" '
        f'download="{esc(download_name)}" target="_blank" rel="noopener">'
        f'<img src="{esc(icon)}" alt="" aria-hidden="true">'
        '<span class="book-download-copy">'
        "<strong>Download the PDF</strong>"
        f"{meta}"
        "</span></a></div>"
        '<section class="book-viewer" data-book '
        f'data-book-source="{esc(pdf_url)}"{numbering} aria-label="Book preview">'
        '<div class="book-pdf" data-book-pdf></div>'
        '<div class="book-controls">'
        '<button class="book-nav book-nav--next" type="button" data-book-next>'
        '<span aria-hidden="true">&larr;</span> Next</button>'
        '<form class="book-goto" data-book-goto novalidate>'
        '<label class="book-goto-label" for="book-goto">Go to</label>'
        '<input class="book-goto-input" id="book-goto" type="number" '
        f'min="1"{max_attr} step="1" inputmode="numeric" enterkeyhint="go" '
        "data-book-goto-input>"
        '<button class="book-goto-go" type="submit">Go</button>'
        "</form>"
        '<button class="book-nav book-nav--prev" type="button" data-book-prev>'
        'Previous <span aria-hidden="true">&rarr;</span></button>'
        "</div>"
        '<p class="book-counter" data-book-counter aria-live="polite">Cover</p>'
        "<noscript>"
        "<style>.book-controls, .book-counter { display: none; }</style>"
        '<p class="book-fallback">The page-turn preview needs JavaScript. '
        "Use the download button above to read the full book.</p>"
        "</noscript>"
        f'<script src="{esc(vendor_js)}" defer></script>'
        f'<script src="{esc(book_js)}" defer></script>'
        "</section>"
    )


def render_block(block: dict, card_dir: Path, site: dict, root: str) -> str:
    block_type = block.get("type")
    if block_type == "prose":
        return markdown_to_html(card_dir / block["src"], root)
    if block_type == "contact":
        return render_contact(site)
    if block_type == "book":
        return render_book(block, root)
    if block_type in RENDERERS:
        return render_dataset(
            block_type,
            block["select"],
            root,
            block.get("group_by"),
            block.get("layout"),
        )
    raise SystemExit(f"build.py: unknown block type {block_type!r}")


def build() -> None:
    site = load_site()
    cards = load_cards()

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    shutil.copytree(
        ASSETS,
        DIST / "assets",
        ignore=lambda directory, names: MEDIA.ignore(directory, names)
        | {name for name in names if name.endswith((".swp", ".swo"))},
    )

    year = str(date.today().year)
    base = read_template("base.html")
    board_base = read_template("base-board.html")
    index_template = read_template("index.html")
    card_template = read_template("card.html")
    board_templates = {
        "board_card": read_template("partials/board-card.html"),
        "perch": read_template("partials/perch.html"),
        "lanyard": read_template("partials/lanyard.html"),
    }

    def write_page(
        path: Path,
        title: str,
        description: str,
        body: str,
        root: str,
        topbar: str,
        footer: str,
        page_slug: str,
        page_css: str,
    ) -> None:
        page = render_template(
            base,
            {
                "TITLE": esc(title),
                "DESCRIPTION": esc(description),
                "ROOT": root,
                "TOPBAR": topbar,
                "BODY": body,
                "FOOTER": footer,
                "PAGE": esc(page_slug),
                "PAGE_CSS": page_css,
            },
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(page, encoding="utf-8")

    board_order = {"nature": 0, "software": 1, "neutral": 2}
    board_cards = "".join(
        render_board_card(card, board_templates)
        for card in sorted(
            cards,
            key=lambda card: (
                board_order[card["family"]],
                card["board"].get("y", 100),
                card["board"]["x"],
            ),
        )
    )
    index_body = render_template(
        index_template,
        {
            "SITE_NAME": esc(site["name"]),
            "TAGLINE": esc(site["tagline"]),
            "TAGLINE_LINES": tagline_lines(site["tagline"]),
            "BOARD_CARDS": board_cards,
        },
    )
    hub_page = render_template(
        board_base,
        {
            "TITLE": esc(f'{site["name"]} — Portfolio'),
            "DESCRIPTION": esc(site["tagline"]),
            "TOPBAR": render_topbar(site, "index.html", ""),
            "BODY": index_body,
            "FOOTER": render_footer(site, year),
        },
    )
    (DIST / "index.html").write_text(hub_page, encoding="utf-8")

    card_topbar = render_topbar(site, "../index.html", "../index.html")
    card_footer = render_footer(site, year)

    for position, card in enumerate(cards):
        root = "../"
        body_html = "\n".join(
            render_block(block, card["dir"], site, root)
            for block in card["blocks"]
        )

        audio_html = ""
        if card.get("audio"):
            audio_html = (
                '<section class="voice"><h2>Listen</h2>'
                f'<audio controls preload="none" src="{esc(asset_url(card["audio"], root))}"></audio>'
                "</section>"
            )

        transcript_html = ""
        if card.get("transcript"):
            transcript_html = (
                '<section class="transcript"><h2>Transcript</h2>'
                f'<p>{esc(card["transcript"])}</p></section>'
            )

        pager = []
        if position > 0:
            previous = cards[position - 1]
            pager.append(
                f'<a class="pager-prev" href="../{esc(previous["slug"])}/index.html">'
                f'&larr; {esc(previous["title"])}</a>'
            )
        if position + 1 < len(cards):
            following = cards[position + 1]
            pager.append(
                f'<a class="pager-next" href="../{esc(following["slug"])}/index.html">'
                f'{esc(following["title"])} &rarr;</a>'
            )

        summary_html = markdown_to_html(
            card_markdown(card, "summary.md"), root
        )
        description_text = markdown_to_text(
            card_markdown(card, "description.md")
        )

        card_body = render_template(
            card_template,
            {
                "ROOT": root,
                "SLUG": esc(card["slug"]),
                "KICKER": esc(card["kicker"]),
                "FAMILY": esc(card["family"]),
                "TITLE": esc(card["title"]),
                "SUMMARY": summary_html,
                "MARK": render_card_mark(card, root),
                "LOGO": render_logo(card, root),
                "STATUS": status_badge(card["status"]),
                "BODY": body_html,
                "AUDIO": audio_html,
                "TRANSCRIPT": transcript_html,
                "PAGER": "".join(pager),
            },
        )
        write_page(
            DIST / card["slug"] / "index.html",
            f'{card["title"]} — {site["name"]}',
            description_text,
            card_body,
            root,
            card_topbar,
            card_footer,
            card["slug"],
            page_stylesheet(
                "holding" if card.get("holding") else card["slug"], root
            ),
        )

    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    index_path = (DIST / "index.html").resolve()
    print(f"Built {len(cards) + 1} pages into {DIST.relative_to(ROOT)}/")
    print(f"index: {index_path}")


if __name__ == "__main__":
    build()
