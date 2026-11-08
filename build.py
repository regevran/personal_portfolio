#!/usr/bin/env python3
"""Render the static portfolio into dist/.

The data lives in content/data/*.json, prose in content/cards/*.md, and the
view in templates/. This script only composes them; validation lives in tests/.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
CARDS_DIR = CONTENT / "cards"
DATA_DIR = CONTENT / "data"
TEMPLATES = ROOT / "templates"
ASSETS = ROOT / "assets"
DIST = ROOT / "dist"

STATUS_LABELS = {
    "ready": "",
    "under-construction": "Under construction",
    "coming-soon": "Coming soon",
    "placeholder": "Placeholder",
}

INCLUDE_RE = re.compile(r"<!--\s*include:([\w:-]+)\s*-->")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_json(name: str):
    with (DATA_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


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


def link_item(title: str, url: str | None, meta: str, description: str | None) -> str:
    title_html = f'<a href="{esc(url)}">{esc(title)}</a>' if url else esc(title)
    meta_html = f' <span class="item-meta">{esc(meta)}</span>' if meta else ""
    desc_html = f'<p class="item-desc">{esc(description)}</p>' if description else ""
    return (
        f'<li class="item"><span class="item-title">{title_html}</span>'
        f"{meta_html}{desc_html}</li>"
    )


def render_papers() -> str:
    items = []
    papers = sort_latest(
        load_json("papers.json"),
        lambda paper: date(int(paper["year"]), 1, 1),
    )
    for paper in papers:
        meta = " · ".join(
            str(part) for part in (paper.get("id"), paper.get("role"), paper.get("year")) if part
        )
        items.append(
            link_item(paper["title"], paper.get("link"), meta, paper.get("description"))
        )
    return '<ul class="item-list">' + "".join(items) + "</ul>"


def render_talks() -> str:
    talks = sort_latest(
        load_json("talks.json"),
        lambda talk: iso_date(talk.get("sort_date")),
    )
    items = [
        link_item(talk["title"], talk.get("url"), talk.get("date", ""), talk.get("description"))
        for talk in talks
    ]
    return '<ul class="item-list">' + "".join(items) + "</ul>"


def render_episodes() -> str:
    episodes = sort_latest(
        load_json("episodes.json"),
        lambda episode: iso_date(episode.get("sort_date")),
    )
    items = [
        link_item(
            episode["title"],
            episode.get("url"),
            episode.get("date", ""),
            episode.get("description"),
        )
        for episode in episodes
    ]
    return '<ul class="item-list">' + "".join(items) + "</ul>"


def render_repos() -> str:
    repos = sort_latest(
        load_json("repos.json"),
        lambda repo: iso_moment(repo.get("pushed_at")),
    )
    items = []
    for repo in repos:
        meta = ""
        pushed_at = repo.get("pushed_at")
        if pushed_at:
            meta = f"Last push: {str(pushed_at)[:10]}"
        items.append(
            link_item(repo["name"], repo.get("url"), meta, repo.get("description"))
        )
    return '<ul class="item-list">' + "".join(items) + "</ul>"


def render_videos(root: str, group: str) -> str:
    cards = []
    videos = [
        video for video in load_json("videos.json") if video.get("group") == group
    ]
    videos = sort_latest(videos, lambda video: iso_date(video.get("date")))
    for video in videos:

        youtube = video.get("youtube")
        if youtube:
            source = youtube if str(youtube).startswith("http") else f"https://www.youtube.com/embed/{youtube}"
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
    return '<div class="media-grid">' + "".join(cards) + "</div>"


def render_photos(root: str) -> str:
    cards = []
    photos = sort_latest(
        load_json("photos.json"),
        lambda photo: iso_date(photo.get("date")),
    )
    for photo in photos:
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
    return '<div class="media-grid">' + "".join(cards) + "</div>"


def render_contact(site: dict) -> str:
    template = read_template("partials/contact.html")
    phone = str(site["phone"])
    phone_tel = re.sub(r"[^0-9+]", "", phone)
    return render_template(
        template,
        {
            "NAME": esc(site["name"]),
            "EMAIL": esc(site["email"]),
            "PHONE": esc(phone),
            "PHONE_TEL": esc(phone_tel),
        },
    )


INCLUDES = {
    "papers": lambda root, site: render_papers(),
    "talks": lambda root, site: render_talks(),
    "episodes": lambda root, site: render_episodes(),
    "repos": lambda root, site: render_repos(),
    "photos": lambda root, site: render_photos(root),
    "contact": lambda root, site: render_contact(site),
    "videos:rescues": lambda root, site: render_videos(root, "rescues"),
    "videos:podcast-promos": lambda root, site: render_videos(root, "podcast-promos"),
}


def render_include(name: str, root: str, site: dict) -> str:
    try:
        renderer = INCLUDES[name]
    except KeyError as exc:
        raise SystemExit(f"build.py: unknown include '{name}'") from exc
    return renderer(root, site)


def build() -> None:
    site = load_json("site.json")
    cards = sorted(load_json("cards.json"), key=lambda card: card["order"])

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
    index_template = read_template("index.html")
    card_template = read_template("card.html")
    card_link_template = read_template("partials/card-link.html")

    def write_page(path: Path, title: str, description: str, body: str, root: str) -> None:
        page = render_template(
            base,
            {
                "TITLE": esc(title),
                "DESCRIPTION": esc(description),
                "ROOT": root,
                "SITE_NAME": esc(site["name"]),
                "YEAR": year,
                "BODY": body,
            },
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(page, encoding="utf-8")

    card_links = []
    for card in cards:
        card_links.append(
            render_template(
                card_link_template,
                {
                    "SLUG": esc(card["slug"]),
                    "KICKER": esc(card["kicker"]),
                    "FAMILY": esc(card["family"]),
                    "TITLE": esc(card["title"]),
                    "SUMMARY": esc(card["summary"]),
                    "STATUS": status_badge(card["status"]),
                },
            )
        )

    index_body = render_template(
        index_template,
        {
            "TAGLINE": esc(site["tagline"]),
            "SITE_NAME": esc(site["name"]),
            "INTRO": esc(site["intro"]),
            "CARDS": "".join(card_links),
        },
    )
    write_page(
        DIST / "index.html",
        f'{site["name"]} — Portfolio',
        site["tagline"],
        index_body,
        "",
    )

    for position, card in enumerate(cards):
        root = "../"
        markdown = CARDS_DIR / f'{card["slug"]}.md'
        body_html = markdown_to_html(markdown)
        body_html = INCLUDE_RE.sub(
            lambda match: render_include(match.group(1), root, site),
            body_html,
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
                "KICKER": esc(card["kicker"]),
                "FAMILY": esc(card["family"]),
                "TITLE": esc(card["title"]),
                "SUMMARY": esc(card["summary"]),
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
        )

    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    index_path = (DIST / "index.html").resolve()
    print(f"Built {len(cards) + 1} pages into {DIST.relative_to(ROOT)}/")
    print(f"index: {index_path}")


if __name__ == "__main__":
    build()
