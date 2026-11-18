"""Tests for the R2 media policy and the URLs the build emits."""

from __future__ import annotations

import unittest

from src.build import asset_url
from src.media import DIST, MEDIA, ROOT


class MediaConfigTest(unittest.TestCase):
    def test_content_media_is_remote(self):
        for path in (
            "assets/ringing/alcedo_atthis_1.jpeg",
            "assets/rescues/ardea_alba/ardea_alba.mp4",
            "assets/rescues/ardea_alba/ardea_alba_frame_1.jpeg",
            "assets/podcast/promo_shay_agmon_ringing.mp4",
            "assets/documents/birds-of-israel-index.pdf",
        ):
            self.assertTrue(MEDIA.is_remote(path), path)
            self.assertEqual(MEDIA.remote_url(path), f"{MEDIA.base}/{path}")

    def test_theme_media_stays_local(self):
        for path in (
            "assets/general/closing_on_birds_logo.jpeg",
            "assets/general/closing_on_birds_robin.png",
            "assets/icons/bird-ring.svg",
            "assets/css/theme.css",
        ):
            self.assertFalse(MEDIA.is_remote(path), path)

    def test_asset_url_keeps_local_paths_page_relative(self):
        self.assertEqual(
            asset_url("assets/icons/github.svg", "../"),
            "../assets/icons/github.svg",
        )
        self.assertEqual(
            asset_url("assets/ringing/alcedo_atthis_1.jpeg", "../"),
            f"{MEDIA.base}/assets/ringing/alcedo_atthis_1.jpeg",
        )

    def test_copy_ignore_skips_only_the_remote_directories(self):
        ignored = MEDIA.ignore(
            str(ROOT / "assets"),
            ["ringing", "rescues", "podcast", "documents", "general"],
        )
        self.assertEqual(
            ignored, {"ringing", "rescues", "podcast", "documents"}
        )

    def test_dist_references_hosted_media(self):
        urls = MEDIA.urls_in(DIST)
        self.assertTrue(urls)
        self.assertTrue(all(url.startswith(MEDIA.base + "/") for url in urls))
        self.assertTrue(
            any(url.endswith("/birds-of-israel-index.pdf") for url in urls)
        )
        self.assertTrue(any(url.endswith(".mp4") for url in urls))
        self.assertTrue(any(url.endswith(".jpeg") for url in urls))
        self.assertFalse(any("/assets/general/" in url for url in urls))

    def test_dist_has_no_copied_content_media(self):
        self.assertFalse((DIST / "assets" / "ringing").exists())
        self.assertFalse((DIST / "assets" / "rescues").exists())
        self.assertFalse((DIST / "assets" / "podcast").exists())
        self.assertFalse((DIST / "assets" / "documents").exists())


if __name__ == "__main__":
    unittest.main()
