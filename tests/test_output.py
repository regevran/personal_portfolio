import json
import unittest

from tests.validate import DATA_DIR, DIST, validate_output


class OutputValidationTest(unittest.TestCase):
    def test_output(self):
        errors = validate_output()
        self.assertEqual(errors, [], "\n".join(errors))

    def test_hub_uses_board_layout(self):
        hub = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="board"', hub)
        self.assertIn('class="board-item', hub)
        self.assertIn("board-background", (DIST / "assets" / "css" / "board.css").read_text())
        self.assertNotIn('class="card-grid"', hub)

    def test_shared_chrome_and_footer_data(self):
        hub = (DIST / "index.html").read_text(encoding="utf-8")
        card = (DIST / "podcast" / "index.html").read_text(encoding="utf-8")
        expected = "Static, data-driven, rebuilt with cmake."

        for page in (hub, card):
            self.assertIn('class="topbar', page)
            self.assertIn('class="site-footer"', page)
            self.assertIn(expected, page)

        self.assertIn('href="../index.html#nature"', card)

    def test_podcast_page_specific_design(self):
        podcast = (DIST / "podcast" / "index.html").read_text(encoding="utf-8")
        self.assertIn("assets/css/pages/podcast.css", podcast)
        self.assertIn("card-page--podcast", podcast)
        self.assertIn("closing_on_birds_circle.png", podcast)
        podcast_css = (DIST / "assets/css/pages/podcast.css").read_text(
            encoding="utf-8"
        )
        self.assertIn("closing_on_birds_logo.png", podcast_css)
        for platform in ("spotify", "apple", "pocketcasts"):
            self.assertIn(f"episode-link--{platform}", podcast)

        talks = (DIST / "talks" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("pages/podcast.css", talks)
        self.assertNotIn("card-page-logo", talks)

    def test_engineering_page_specific_design(self):
        engineering = (DIST / "engineering" / "index.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("assets/css/pages/engineering.css", engineering)
        self.assertIn("card-page--engineering", engineering)
        self.assertIn("github-qr.svg", engineering)

        engineering_css = (DIST / "assets/css/pages/engineering.css").read_text(
            encoding="utf-8"
        )
        self.assertIn("icons/lanyard.svg", engineering_css)
        self.assertIn("icons/conference-badge.svg", engineering_css)
        self.assertIn("translateY(-6px) scale(1.02)", engineering_css)
        self.assertNotIn("rotate(", engineering_css)
        self.assertNotIn("card-page-header::after", engineering_css)
        self.assertIn("repo-badge", engineering)
        self.assertIn("repo-rail", engineering)

        site_css = (DIST / "assets/css/site.css").read_text(encoding="utf-8")
        board_css = (DIST / "assets/css/board.css").read_text(encoding="utf-8")
        self.assertIn(".card-page--software .card-page-header h1", site_css)
        self.assertIn(".scrap--monitor .card-title", board_css)
        self.assertIn(".board-item--software .scrap", board_css)
        self.assertIn("badge-mark.svg", board_css)

        qr = (DIST / "assets/general/github-qr.svg").read_text(encoding="utf-8")
        self.assertIn("https://github.com/regevran", qr)

        podcast = (DIST / "podcast" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("pages/engineering.css", podcast)

    def test_listings_are_latest_first(self):
        cpp = (DIST / "cpp-standards" / "index.html").read_text(encoding="utf-8")
        self.assertLess(
            cpp.index("Structured Binding Assignment"), cpp.index("Contract concerns")
        )
        self.assertLess(
            cpp.index("Contract concerns"), cpp.index("Reflection on SG21")
        )

        talks = (DIST / "talks" / "index.html").read_text(encoding="utf-8")
        self.assertLess(talks.index("corecpp.org"), talks.index("tzXu5KZGMJk"))
        self.assertLess(talks.index("tzXu5KZGMJk"), talks.index("-1syQN5_5D0"))
        self.assertLess(
            talks.index("-1syQN5_5D0"), talks.index("search_query=Ran+Regev")
        )

        podcast = (DIST / "podcast" / "index.html").read_text(encoding="utf-8")
        self.assertLess(
            podcast.index("Facing Extinction"), podcast.index("Swifts - with")
        )
        self.assertLess(
            podcast.index("Swifts - with"),
            podcast.index("The Birdwatcher"),
        )

    def test_repos_are_latest_push_first(self):
        repos = json.loads((DATA_DIR / "repos.json").read_text(encoding="utf-8"))
        dated = [repo for repo in repos if repo.get("pushed_at")]
        if not dated:
            self.skipTest("no pushed_at values available")

        expected = [
            repo["name"]
            for repo in sorted(
                dated, key=lambda repo: repo["pushed_at"], reverse=True
            )
        ]
        engineering = (DIST / "engineering" / "index.html").read_text(
            encoding="utf-8"
        )
        positions = [engineering.index(name) for name in expected]
        self.assertEqual(positions, sorted(positions))


if __name__ == "__main__":
    unittest.main()
