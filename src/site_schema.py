"""Shared content model: dataset names, card loading, and block selection.

`build.py` and `tests/` both import this module so selection semantics are
defined in one place.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
CARDS_DIR = CONTENT / "cards"
DATA_DIR = CONTENT / "data"

DATASETS = {
    "papers": "papers.json",
    "talks": "talks.json",
    "episodes": "episodes.json",
    "repos": "repos.json",
    "videos": "videos.json",
    "photos": "photos.json",
}
DATASET_TYPES = frozenset(DATASETS)
BLOCK_TYPES = frozenset({"prose", "contact"}) | DATASET_TYPES

# Reserved collection: a record carrying it is excluded from collection
# selection, but remains on disk and can be restored by removing the name.
HIDDEN_COLLECTION = "hidden"


def load_dataset(name: str) -> list[dict]:
    with (DATA_DIR / DATASETS[name]).open(encoding="utf-8") as handle:
        return json.load(handle)


def load_site() -> dict:
    with (DATA_DIR / "site.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def load_cards() -> list[dict]:
    """Return every card, sorted by `order`, with `slug` and `dir` added."""
    cards = []
    for card_file in sorted(CARDS_DIR.glob("*/card.json")):
        card = json.loads(card_file.read_text(encoding="utf-8"))
        cards.append({"slug": card_file.parent.name, "dir": card_file.parent, **card})
    cards.sort(key=lambda card: card["order"])
    return cards


def is_visible(record: dict) -> bool:
    return HIDDEN_COLLECTION not in record.get("collections", [])


def select_records(records: list[dict], select: dict) -> list[dict]:
    """Apply a block's selector.

    `{"collection": "name"}` returns visible members in dataset order.
    `{"ids": [...]}` returns exactly those records in the given order.
    """
    if not isinstance(select, dict):
        raise ValueError("select must be an object")

    keys = set(select)
    if keys == {"collection"}:
        collection = select["collection"]
        if not isinstance(collection, str) or not collection:
            raise ValueError("select.collection must be a non-empty string")
        if collection == HIDDEN_COLLECTION:
            raise ValueError("the hidden collection cannot be selected")
        return [
            record
            for record in records
            if collection in record.get("collections", []) and is_visible(record)
        ]

    if keys == {"ids"}:
        ids = select["ids"]
        if (
            not isinstance(ids, list)
            or not ids
            or not all(isinstance(value, str) and value for value in ids)
        ):
            raise ValueError("select.ids must be a non-empty list of strings")
        by_id = {record.get("id"): record for record in records}
        missing = [record_id for record_id in ids if record_id not in by_id]
        if missing:
            raise ValueError("unknown id(s): " + ", ".join(missing))
        return [by_id[record_id] for record_id in ids]

    raise ValueError("select must contain exactly one of 'collection' or 'ids'")
