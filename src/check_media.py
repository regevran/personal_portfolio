#!/usr/bin/env python3
"""Check the media hosted in Cloudflare R2.

`check` HEADs every media URL referenced by dist/ and verifies its type.
`audit` lists the bucket and reports missing or unused objects. Both are
explicit commands: the default build and CTest stay offline.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.media import DIST, MEDIA, ROOT

EXPECTED_TYPES = {
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".mp4": "video/mp4",
    ".pdf": "application/pdf",
}
KEEP_FILE = ROOT / "content" / "media-keep.txt"


def check_url(url: str) -> str | None:
    """HEAD one object, retrying the burst rate limit of the r2.dev host."""
    for attempt in range(4):
        try:
            request = Request(url, method="HEAD")
            request.add_header("User-Agent", "personal-portfolio-media-check")
            with urlopen(request, timeout=30) as response:
                content_type = response.headers.get_content_type()
                expected = EXPECTED_TYPES.get(Path(url).suffix.lower())
                if expected and content_type != expected:
                    return f"{url}: content-type {content_type}, expected {expected}"
                return None
        except HTTPError as exc:
            if exc.code in (403, 429) and attempt < 3:
                time.sleep(2**attempt)
                continue
            return f"{url}: HTTP {exc.code}"
        except URLError as exc:
            return f"{url}: {exc.reason}"
    return None


def check() -> int:
    urls = MEDIA.urls_in(DIST)
    if not urls:
        print(f"No media URLs found in {DIST.relative_to(ROOT)}/", file=sys.stderr)
        return 1

    failures = []
    for url in urls:
        error = check_url(url)
        if error:
            failures.append(error)
        time.sleep(0.2)

    if failures:
        print("\n".join(failures), file=sys.stderr)
        print(f"{len(failures)} of {len(urls)} media URLs failed", file=sys.stderr)
        return 1

    print(f"Checked {len(urls)} media URLs; all available.")
    return 0


def list_objects(profile: str, region: str) -> dict[str, int]:
    if not MEDIA.bucket or not MEDIA.endpoint:
        raise SystemExit("media: deploy.json needs 'bucket' and 'endpoint' for audit")

    objects: dict[str, int] = {}
    token = None
    while True:
        command = [
            "aws",
            "s3api",
            "list-objects-v2",
            "--bucket",
            MEDIA.bucket,
            "--endpoint-url",
            MEDIA.endpoint,
            "--region",
            region,
            "--output",
            "json",
        ]
        if profile:
            command += ["--profile", profile]
        if token:
            command += ["--continuation-token", token]

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(result.stderr.strip() or "aws s3api failed")

        data = json.loads(result.stdout or "{}")
        for item in data.get("Contents", []):
            objects[item["Key"]] = int(item.get("Size", 0))
        if not data.get("IsTruncated"):
            return objects
        token = data.get("NextContinuationToken")
        if not token:
            raise SystemExit("aws s3api: truncated listing without a token")


def kept_keys() -> set[str]:
    if not KEEP_FILE.is_file():
        return set()
    keys = set()
    for line in KEEP_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            keys.add(line)
    return keys


def audit(profile: str, region: str, strict: bool) -> int:
    objects = list_objects(profile, region)
    referenced = set(MEDIA.keys_in(DIST))
    stored = set(objects)
    kept = kept_keys()

    missing = sorted(referenced - stored)
    unused = sorted(stored - referenced - kept)

    for key in missing:
        print(f"missing: {key} (referenced by dist/)", file=sys.stderr)
    for key in unused:
        print(f"unused:  {key} ({objects[key]} bytes)", file=sys.stderr)

    print(
        f"{len(referenced)} referenced, {len(stored)} stored, "
        f"{len(missing)} missing, {len(unused)} unused."
    )
    if missing or (strict and unused):
        return 1
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Check R2 media")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check", help="HEAD every URL referenced by dist/")

    audit_parser = subparsers.add_parser(
        "audit", help="compare bucket objects with dist/ references"
    )
    audit_parser.add_argument("--profile", default="r2")
    audit_parser.add_argument("--region", default="auto")
    audit_parser.add_argument(
        "--strict", action="store_true", help="treat unused objects as an error"
    )

    args = parser.parse_args()
    if args.command == "check":
        raise SystemExit(check())
    raise SystemExit(audit(args.profile, args.region, args.strict))


if __name__ == "__main__":
    main()
