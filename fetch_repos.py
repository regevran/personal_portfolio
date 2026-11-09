#!/usr/bin/env python3
"""Refresh `pushed_at` for every repository in content/data/repos.json.

The public GitHub API is queried when the refresh target runs so the repo list
reflects the last push seen at that time. Failures are warnings, not errors:
the cached `pushed_at` values stay in place and the build continues.

Set GITHUB_TOKEN to use an authenticated request (higher rate limit).
The default site build is offline; run `cmake --build --preset refresh-repos`
(or `cmake --workflow --preset refresh`) to update the dates.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "content" / "data" / "repos.json"
API = "https://api.github.com/repos/"
TIMEOUT_SECONDS = 10


def repo_slug(url: str) -> str | None:
    prefix = "https://github.com/"
    if not isinstance(url, str) or not url.startswith(prefix):
        return None
    slug = url[len(prefix):].strip().strip("/")
    if slug.endswith(".git"):
        slug = slug[:-4]
    return slug or None


def fetch_pushed_at(slug: str, token: str | None) -> str | None:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ran-regev-portfolio-render",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(API + slug, headers=headers)
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        payload = json.load(response)
    return payload.get("pushed_at")


def main() -> int:
    try:
        repos = json.loads(DATA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"warning: cannot read {DATA.relative_to(ROOT)}: {exc}", file=sys.stderr)
        return 0

    token = os.environ.get("GITHUB_TOKEN")
    fetched = 0
    changed = 0

    for repo in repos:
        slug = repo_slug(repo.get("url", ""))
        if not slug:
            print(
                f"warning: cannot derive a GitHub slug from {repo.get('url')!r}",
                file=sys.stderr,
            )
            continue
        try:
            pushed_at = fetch_pushed_at(slug, token)
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
            print(f"warning: could not fetch {slug}: {exc}", file=sys.stderr)
            continue
        if not pushed_at:
            print(f"warning: {slug}: API returned no pushed_at", file=sys.stderr)
            continue
        fetched += 1
        if pushed_at and repo.get("pushed_at") != pushed_at:
            repo["pushed_at"] = pushed_at
            changed += 1

    if changed:
        DATA.write_text(
            json.dumps(repos, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    print(f"repo dates: {fetched}/{len(repos)} fetched, {changed} changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
