import json
import unittest

from src.build import iso_date, sort_latest
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
        self.assertIn(".card-page--engineering .github-mark", engineering_css)
        self.assertIn('class="github-mark"', engineering)
        self.assertNotIn("build-log", engineering)
        self.assertIn("Building CXX object", engineering)
        self.assertNotIn("repo-badge", engineering)
        self.assertNotIn("repo-mark", engineering)
        self.assertIn('class="repo-tag"', engineering)
        self.assertIn("[ 20%]", engineering)
        self.assertIn("[100%]", engineering)
        self.assertIn("Linking CXX executable", engineering)
        self.assertNotIn("icons/conference-badge.svg", engineering_css)
        self.assertIn("translateY(-6px) scale(1.02)", engineering_css)
        self.assertNotIn("rotate(", engineering_css)
        self.assertNotIn("card-page-header::after", engineering_css)
        self.assertIn("repo-rail", engineering)
        self.assertIn("icons/github.svg", engineering)
        self.assertIn('class="repo-link"', engineering)
        self.assertIn(".card-page--engineering .repo-link", engineering_css)
        self.assertIn("data-repo=", engineering)
        self.assertIn('class="repo-toggle"', engineering)
        self.assertIn(".card-page--engineering .item.has-more .item-desc", engineering_css)
        self.assertIn(".card-page--engineering .item.is-open .item-desc", engineering_css)
        self.assertIn(".card-page--engineering .repo-toggle", engineering_css)
        self.assertIn("transition: max-height 240ms ease", engineering_css)
        self.assertIn("<noscript>", engineering)

        site_js = (DIST / "assets/js/site.js").read_text(encoding="utf-8")
        self.assertIn("measureRepoCard", site_js)
        self.assertIn("repo-toggle", site_js)
        self.assertIn("animateRepo", site_js)
        self.assertIn("repoPreviewHeight", site_js)

        site_css = (DIST / "assets/css/site.css").read_text(encoding="utf-8")
        board_css = (DIST / "assets/css/board.css").read_text(encoding="utf-8")
        self.assertIn(".card-page--software .card-page-header h1", site_css)
        self.assertIn(".scrap--monitor .card-title", board_css)
        self.assertIn(".board-item--software .scrap", board_css)
        self.assertIn("conference-badge-mark.svg", board_css)
        self.assertNotIn("build-mark.svg", board_css)
        self.assertIn("github.svg", board_css)
        self.assertIn('[data-mark="github-logo"]', board_css)

        hub = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-mark="github-logo"', hub)

        qr = (DIST / "assets/general/github-qr.svg").read_text(encoding="utf-8")
        self.assertIn("https://github.com/regevran", qr)

        podcast = (DIST / "podcast" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("pages/engineering.css", podcast)

    def test_cpp_standards_page_specific_design(self):
        cpp = (DIST / "cpp-standards" / "index.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("assets/css/pages/cpp-standards.css", cpp)
        self.assertIn("card-page--cpp-standards", cpp)
        self.assertIn("ISO/IEC JTC1/SC22/WG21", cpp)
        self.assertIn("cpp-logo.svg", cpp)
        self.assertIn('class="cpp-logo"', cpp)
        self.assertIn("paper.svg", cpp)
        self.assertIn("data-paper=", cpp)
        self.assertIn('class="paper-rail"', cpp)
        self.assertIn('class="paper-link"', cpp)
        self.assertNotIn("pages/engineering.css", cpp)

        cpp_css = (DIST / "assets/css/pages/cpp-standards.css").read_text(
            encoding="utf-8"
        )
        self.assertIn("icons/lanyard.svg", cpp_css)
        self.assertIn("icons/cpp-logo.svg", cpp_css)
        self.assertIn("translateY(-6px) scale(1.02)", cpp_css)

        hub = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-mark="cpp-logo"', hub)
        self.assertIn("ISO/IEC JTC1/SC22/WG21", hub)

        board_css = (DIST / "assets/css/board.css").read_text(encoding="utf-8")
        self.assertIn('[data-mark="cpp-logo"]', board_css)
        self.assertIn("cpp-logo.svg", board_css)

    def test_talks_page_specific_design(self):
        talks = (DIST / "talks" / "index.html").read_text(encoding="utf-8")
        self.assertIn("assets/css/pages/talks.css", talks)
        self.assertIn("card-page--talks", talks)
        self.assertIn("conference-badge.svg", talks)
        self.assertIn('class="conference-mark"', talks)
        self.assertIn("data-talk=", talks)
        self.assertIn("talk-card talk-card--", talks)
        self.assertIn('class="talk-media"', talks)
        self.assertIn('class="talk-video"', talks)
        self.assertIn("data-embed=", talks)
        self.assertIn("i.ytimg.com/vi/B788kH9jO-s", talks)
        self.assertIn("youtube.com/embed/B788kH9jO-s", talks)
        self.assertIn("youtube.com/embed/ClezrL78boo", talks)
        self.assertIn('class="talk-links"', talks)
        self.assertIn("talk-link--youtube", talks)
        self.assertIn("talk-link--slides", talks)
        self.assertIn("<span>Slides</span>", talks)
        self.assertIn("youtube.svg", talks)
        self.assertIn("paper.svg", talks)
        self.assertIn("https://regevran.github.io/p3817-presentatin/", talks)
        self.assertIn("slideshare.net/slideshow/object-storage-in-scylladb", talks)
        self.assertNotIn("Object Storage in ScyllaDB - Slides", talks)
        self.assertNotIn("Open origin", talks)
        self.assertIn('class="talk-stamp"', talks)
        self.assertNotIn("pages/engineering.css", talks)

        talks_css = (DIST / "assets" / "css" / "pages" / "talks.css").read_text(
            encoding="utf-8"
        )
        self.assertIn("icons/lanyard.svg", talks_css)
        self.assertIn("icons/conference-badge-mark.svg", talks_css)
        self.assertIn(".talk-video", talks_css)
        self.assertIn(".talk-media iframe", talks_css)
        self.assertIn("aspect-ratio: 16 / 9", talks_css)
        self.assertIn("translateY(-4px)", talks_css)

        site_js = (DIST / "assets" / "js" / "site.js").read_text(encoding="utf-8")
        self.assertIn("data-embed", site_js)
        self.assertIn('createElement("iframe")', site_js)

        hub = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-mark="conference-badge"', hub)

        board_css = (DIST / "assets" / "css" / "board.css").read_text(encoding="utf-8")
        self.assertIn('[data-mark="conference-badge"]', board_css)

    def test_listings_are_latest_first(self):
        cpp = (DIST / "cpp-standards" / "index.html").read_text(encoding="utf-8")
        self.assertLess(
            cpp.index("Structured Binding Assignment"), cpp.index("Contract concerns")
        )
        self.assertLess(
            cpp.index("Contract concerns"), cpp.index("Reflection on SG21")
        )

        talks = (DIST / "talks" / "index.html").read_text(encoding="utf-8")
        talk_records = json.loads(
            (DATA_DIR / "talks.json").read_text(encoding="utf-8")
        )
        ordered_talks = sort_latest(
            talk_records, lambda talk: iso_date(talk.get("sort_date"))
        )
        positions = [
            talks.index(f'data-talk="{talk["id"]}"') for talk in ordered_talks
        ]
        self.assertEqual(positions, sorted(positions))

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
