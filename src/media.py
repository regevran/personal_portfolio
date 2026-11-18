"""Cloudflare R2 media policy shared by the renderer and the media checks.

Content binaries under the configured paths are stored in R2 and referenced by
absolute URL. Everything else stays beside the CSS on GitHub Pages.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
CONFIG = ROOT / "deploy.json"


class MediaConfig:
    def __init__(
        self,
        base: str,
        paths: tuple[str, ...],
        bucket: str = "",
        endpoint: str = "",
    ) -> None:
        self.base = base.rstrip("/")
        self.paths = tuple(path.rstrip("/") + "/" for path in paths)
        self.bucket = bucket
        self.endpoint = endpoint.rstrip("/")

    @classmethod
    def load(cls, path: Path = CONFIG) -> "MediaConfig":
        try:
            config = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise SystemExit(f"media: cannot read {path.name}: {exc}")
        except json.JSONDecodeError as exc:
            raise SystemExit(f"media: invalid {path.name}: {exc}")

        base = config.get("media_base")
        if not isinstance(base, str) or not base.strip():
            raise SystemExit("media: deploy.json needs a non-empty 'media_base'")

        paths = config.get("remote_paths")
        if (
            not isinstance(paths, list)
            or not paths
            or not all(isinstance(item, str) and item for item in paths)
        ):
            raise SystemExit("media: deploy.json needs a non-empty 'remote_paths'")

        bucket = config.get("bucket", "")
        endpoint = config.get("endpoint", "")
        if not isinstance(bucket, str) or not isinstance(endpoint, str):
            raise SystemExit("media: 'bucket' and 'endpoint' must be strings")

        return cls(base, tuple(paths), bucket, endpoint)

    @staticmethod
    def _clean(relative: str) -> str:
        text = str(relative).replace("\\", "/")
        while text.startswith("./"):
            text = text[2:]
        return text.lstrip("/")

    def is_remote(self, relative: str) -> bool:
        text = self._clean(relative)
        return any(text.startswith(prefix) for prefix in self.paths)

    def remote_url(self, relative: str) -> str:
        return f"{self.base}/{self._clean(relative)}"

    def ignore(self, directory: str, names: list[str]) -> set[str]:
        """shutil.copytree callback: skip the directories hosted on R2."""
        current = Path(directory)
        try:
            relative = current.relative_to(ROOT).as_posix()
        except ValueError:
            return set()
        if relative == ".":
            relative = ""
        ignored = set()
        for name in names:
            child = f"{relative}/{name}" if relative else name
            if self.is_remote(child + "/"):
                ignored.add(name)
        return ignored

    def urls_in(self, dist: Path = DIST) -> list[str]:
        """Every configured media URL referenced by the rendered pages."""
        prefix = self.base + "/"
        pattern = re.compile(
            re.escape(prefix) + r"[^\"'\s<>]+"
        )
        urls: set[str] = set()
        for page in sorted(dist.rglob("*.html")):
            urls.update(pattern.findall(page.read_text(encoding="utf-8")))
        return sorted(urls)

    def keys_in(self, dist: Path = DIST) -> list[str]:
        prefix = self.base + "/"
        return [url[len(prefix):] for url in self.urls_in(dist)]


MEDIA = MediaConfig.load()
