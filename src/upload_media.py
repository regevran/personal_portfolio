#!/usr/bin/env python3
"""Upload the media referenced by dist/ to Cloudflare R2.

Only files the rendered site actually uses are uploaded, so the bucket stays
close to 1:1 with the site. Existing objects with the same size are skipped
unless --force is given. Deletion is never automatic.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from src.check_media import list_objects
from src.media import DIST, MEDIA, ROOT

CACHE_CONTROL = "public, max-age=604800"
CONTENT_TYPES = {
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".mp4": "video/mp4",
    ".pdf": "application/pdf",
}


def upload(key: str, path: Path, profile: str, region: str) -> None:
    content_type = CONTENT_TYPES.get(path.suffix.lower())
    if not content_type:
        raise SystemExit(f"upload: unsupported media type {path.suffix!r}")
    command = [
        "aws",
        "s3",
        "cp",
        str(path),
        f"s3://{MEDIA.bucket}/{key}",
        "--endpoint-url",
        MEDIA.endpoint,
        "--region",
        region,
        "--content-type",
        content_type,
        "--cache-control",
        CACHE_CONTROL,
    ]
    if content_type == "application/pdf":
        # PDFs are downloads, not inline viewers; the header also names the file
        # when the link is cross-origin and the HTML download attribute is ignored.
        command += [
            "--content-disposition",
            f'attachment; filename="{path.name}"',
        ]
    if profile:
        command += ["--profile", profile]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or f"upload failed: {key}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload dist/ media to R2")
    parser.add_argument("--profile", default="r2")
    parser.add_argument("--region", default="auto")
    parser.add_argument("--force", action="store_true", help="upload unchanged files")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    keys = MEDIA.keys_in(DIST)
    if not keys:
        raise SystemExit(f"upload: no media URLs found in {DIST.relative_to(ROOT)}/")

    remote = list_objects(args.profile, args.region)
    uploaded = skipped = 0
    missing: list[str] = []

    for key in keys:
        local = ROOT / key
        if not local.is_file():
            if key in remote:
                print(f"remote only: {key}")
            else:
                missing.append(key)
            continue

        if (
            not args.force
            and key in remote
            and remote[key] == local.stat().st_size
        ):
            skipped += 1
            continue

        if args.dry_run:
            print(f"would upload: {key}")
        else:
            print(f"uploading: {key}")
            upload(key, local, args.profile, args.region)
        uploaded += 1

    if missing:
        for key in missing:
            print(f"missing locally and remotely: {key}", file=sys.stderr)
        raise SystemExit(f"upload: {len(missing)} referenced files are unavailable")

    print(f"Uploaded {uploaded}, skipped {skipped} unchanged, {len(keys)} referenced.")


if __name__ == "__main__":
    main()
