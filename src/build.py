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

from src.site_schema import (
    DATA_DIR,
    load_cards,
    load_dataset,
    load_site,
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


def markdown_to_html(path: Path) -> str:
    result = subprocess.run(
        ["pandoc", "-f", "markdown+smart", "-t", "html5", "--wrap=none", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def iso_date(value):
    """Return a date for sorting, or None when the value is absent/invalid."""
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


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


def description_html(entry: dict) -> str:
    """Render an inline description or a per-record Markdown description."""
    source = entry.get("description_src")
    if source:
        return markdown_to_html(DATA_DIR / source)
    description = entry.get("description")
    return esc(description) if description else ""


def link_item(title: str, url: str | None, meta: str, description: str) -> str:
    title_html = f'<a href="{esc(url)}">{esc(title)}</a>' if url else esc(title)
    meta_html = f' <span class="item-meta">{esc(meta)}</span>' if meta else ""
    desc_html = f'<div class="item-desc">{description}</div>' if description else ""
    return (
        f'<li class="item"><span class="item-title">{title_html}</span>'
        f"{meta_html}{desc_html}</li>"
    )


def render_papers(records: list[dict], root: str) -> str:
    items = []
    for paper in records:
        meta = " · ".join(
            str(part)
            for part in (paper.get("wg21"), paper.get("role"), paper.get("year"))
            if part
        )
        items.append(
            link_item(
                paper["title"], paper.get("link"), meta, description_html(paper)
            )
        )
    return '<ul class="item-list">' + "".join(items) + "</ul>"


def render_talks(records: list[dict], root: str) -> str:
    items = [
        link_item(
            talk["title"],
            talk.get("url"),
            talk.get("date", ""),
            description_html(talk),
        )
        for talk in records
    ]
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
            f'<img src="{esc(root + icon)}" alt="" aria-hidden="true">'
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
        description = description_html(episode)
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


def repo_rail() -> str:
    return (
        '<span class="repo-rail">'
        '<span class="repo-badge" aria-hidden="true"></span>'
        "</span>"
    )


def render_repos(records: list[dict], root: str) -> str:
    items = []
    for repo in records:
        meta = ""
        pushed_at = repo.get("pushed_at")
        if pushed_at:
            meta = f"Last push: {str(pushed_at)[:10]}"
        name_html = (
            f'<a href="{esc(repo["url"])}">{esc(repo["name"])}</a>'
            if repo.get("url")
            else esc(repo["name"])
        )
        meta_html = f'<span class="item-meta">{esc(meta)}</span>' if meta else ""
        description = description_html(repo)
        items.append(
            '<li class="item">'
            '<span class="item-head">'
            f'<span class="item-title">{name_html}</span>'
            f"{meta_html}</span>"
            f'<div class="item-desc">{description}</div>'
            f"{repo_rail()}</li>"
        )
    return '<ul class="item-list">' + "".join(items) + "</ul>"


def render_videos(records: list[dict], root: str) -> str:
    cards = []
    for video in records:
        youtube = video.get("youtube")
        if youtube:
            source = (
                youtube
                if str(youtube).startswith("http")
                else f"https://www.youtube.com/embed/{youtube}"
            )
            media = (
                f'<iframe src="{esc(source)}" title="{esc(video["title"])}" '
                'loading="lazy" allowfullscreen></iframe>'
            )
        else:
            media = (
                f'<video controls preload="metadata" '
                f'src="{esc(root + video["src"])}"></video>'
            )

        species = ""
        if video.get("species"):
            species = f'<span class="media-meta">{esc(video["species"])}</span>'
        description = ""
        if video.get("description"):
            description = f'<p class="item-desc">{esc(video["description"])}</p>'

        cards.append(
            f'<figure class="media-card">{media}<figcaption>'
            f'<span class="media-title">{esc(video["title"])}</span>'
            f"{species}{description}</figcaption></figure>"
        )
    return '<div class="media-grid media-grid--videos">' + "".join(cards) + "</div>"


def render_photos(records: list[dict], root: str) -> str:
    cards = []
    for photo in records:
        media = (
            f'<img src="{esc(root + photo["src"])}" '
            f'alt="{esc(photo["title"])}" loading="lazy">'
        )
        audio = ""
        if photo.get("audio"):
            audio = (
                f'<audio controls preload="none" '
                f'src="{esc(root + photo["audio"])}"></audio>'
            )
        caption = photo.get("caption", "")
        cards.append(
            f'<figure class="media-card">{media}<figcaption>'
            f'<span class="media-title">{esc(photo["title"])}</span>'
            f'<span class="media-meta">{esc(caption)}</span>{audio}'
            "</figcaption></figure>"
        )
    return '<div class="media-grid media-grid--photos">' + "".join(cards) + "</div>"


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
        f'<img class="card-page-logo" src="{esc(root + source)}" '
        f'alt="{esc(alt)}">'
    )


def page_stylesheet(slug: str, root: str) -> str:
    if not (ASSETS / "css" / "pages" / f"{slug}.css").is_file():
        return ""
    relative = f"assets/css/pages/{slug}.css"
    return f'<link rel="stylesheet" href="{esc(root + relative)}">'


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
        "nature": "",
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
        rig = render_template(templates["perch"], {"ROBIN_STYLE": robin_style})
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


def render_dataset(name: str, select: dict, root: str) -> str:
    records = select_records(load_dataset(name), select)
    if "ids" not in select:
        records = sort_latest(records, SORT_KEYS[name])
    return RENDERERS[name](records, root)


def render_block(block: dict, card_dir: Path, site: dict, root: str) -> str:
    block_type = block.get("type")
    if block_type == "prose":
        return markdown_to_html(card_dir / block["src"])
    if block_type == "contact":
        return render_contact(site)
    if block_type in RENDERERS:
        return render_dataset(block_type, block["select"], root)
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
        ignore=shutil.ignore_patterns("*.swp", "*.swo"),
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
                f'<audio controls preload="none" src="{esc(root + card["audio"])}"></audio>'
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

        card_body = render_template(
            card_template,
            {
                "ROOT": root,
                "SLUG": esc(card["slug"]),
                "KICKER": esc(card["kicker"]),
                "FAMILY": esc(card["family"]),
                "TITLE": esc(card["title"]),
                "SUMMARY": esc(card["summary"]),
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
            card.get("description", card["summary"]),
            card_body,
            root,
            card_topbar,
            card_footer,
            card["slug"],
            page_stylesheet(card["slug"], root),
        )

    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    index_path = (DIST / "index.html").resolve()
    print(f"Built {len(cards) + 1} pages into {DIST.relative_to(ROOT)}/")
    print(f"index: {index_path}")


if __name__ == "__main__":
    build()
