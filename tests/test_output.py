import json
import unittest

from src.build import display_date, iso_date, sort_latest
from src.media import MEDIA
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

    def test_hub_nature_cards_have_their_own_marks(self):
        hub = (DIST / "index.html").read_text(encoding="utf-8")
        for mark in (
            "ringing-station",
            "podcast-logo",
            "rescue",
            "book",
            "learning-aid",
        ):
            self.assertIn(f'data-mark="{mark}"', hub)
        self.assertIn("board-item--nature", hub)
        self.assertIn('id="nature"', hub)
        self.assertNotIn("birding/index.html", hub)
        self.assertNotIn("Birding", hub)
        self.assertFalse((DIST / "birding").exists())

        board_css = (DIST / "assets" / "css" / "board.css").read_text(
            encoding="utf-8"
        )
        for icon in (
            "bird-ring.svg",
            "closing_on_birds_logo.png",
            "rescue.svg",
            "book.svg",
            "learning-aid.svg",
        ):
            self.assertIn(icon, board_css)

        for icon in ("rescue.svg", "book.svg", "learning-aid.svg"):
            self.assertTrue((DIST / "assets" / "icons" / icon).is_file())

    def test_shared_chrome_and_footer_data(self):
        hub = (DIST / "index.html").read_text(encoding="utf-8")
        card = (DIST / "podcast" / "index.html").read_text(encoding="utf-8")
        site = json.loads((DATA_DIR / "site.json").read_text(encoding="utf-8"))
        expected = site["footer"]

        for page in (hub, card):
            self.assertIn('class="topbar', page)
            self.assertIn('class="site-footer"', page)
            self.assertIn(expected, page)

        self.assertIn('href="../index.html#nature"', card)

    def test_card_summary_and_description_markdown(self):
        ringing = (DIST / "ringing" / "index.html").read_text(encoding="utf-8")
        self.assertIn(
            '<meta name="description" content="Bird ringing and field observations.">',
            ringing,
        )
        self.assertIn('<div class="lede"><p>', ringing)

    def test_podcast_page_specific_design(self):
        podcast = (DIST / "podcast" / "index.html").read_text(encoding="utf-8")
        self.assertIn("assets/css/pages/podcast.css", podcast)
        self.assertIn("card-page--podcast", podcast)
        self.assertIn("closing_on_birds_circle.png", podcast)
        podcast_css = (DIST / "assets/css/pages/podcast.css").read_text(
            encoding="utf-8"
        )
        self.assertIn("closing_on_birds_logo.png", podcast_css)
        self.assertNotIn(".card-page--podcast .prose > p", podcast_css)
        self.assertNotIn("background: transparent", podcast_css)
        self.assertIn("float: right", podcast_css)
        self.assertIn("width: clamp(104px, 12vw, 148px)", podcast_css)
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
        self.assertNotIn("icons/lanyard.svg", engineering_css)
        self.assertNotIn("background: transparent", engineering_css)
        self.assertNotIn(".card-page--engineering .prose > p", engineering_css)
        self.assertIn(".card-page--engineering .github-mark", engineering_css)
        self.assertIn("padding-right: calc(var(--artifact)", engineering_css)
        self.assertIn("position: absolute", engineering_css)
        self.assertIn("right: 0", engineering_css)
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
        self.assertNotIn("icons/lanyard.svg", cpp_css)
        self.assertNotIn("background: transparent", cpp_css)
        self.assertNotIn(".card-page--cpp-standards .prose > p", cpp_css)
        self.assertIn("icons/cpp-logo.svg", cpp_css)
        self.assertIn("padding-right: calc(var(--artifact)", cpp_css)
        self.assertIn("position: absolute", cpp_css)
        self.assertIn("right: 0", cpp_css)
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
        self.assertNotIn("icons/lanyard.svg", talks_css)
        self.assertNotIn("background: transparent", talks_css)
        self.assertNotIn(".card-page--talks .prose > p", talks_css)
        self.assertIn("icons/conference-badge-mark.svg", talks_css)
        self.assertIn("padding-right: calc(var(--artifact)", talks_css)
        self.assertIn("position: absolute", talks_css)
        self.assertIn("right: 0", talks_css)
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

    def test_prose_pages_share_the_split_note_intro(self):
        for slug in (
            "engineering",
            "cpp-standards",
            "talks",
            "ringing",
            "rescues",
            "podcast",
        ):
            page = (DIST / slug / "index.html").read_text(encoding="utf-8")
            self.assertIn('class="note-intro"', page)
            self.assertIn('class="note-intro-figure"', page)
            self.assertIn('class="note-intro-copy"', page)
            self.assertIn('class="note-intro-kicker"', page)
            self.assertIn("<mark>", page)

    def test_book_page_is_a_right_to_left_pdf_flipbook(self):
        book = (DIST / "book" / "index.html").read_text(encoding="utf-8")
        hub = (DIST / "index.html").read_text(encoding="utf-8")
        pdf_url = f"{MEDIA.base}/assets/documents/birds-of-israel-index.pdf"

        self.assertIn("<title>Birds of Israel Index — Ran Regev</title>", book)
        self.assertIn("Birds of Israel Index", hub)
        self.assertNotIn("The Book", hub)
        self.assertIn("assets/css/pages/book.css", book)
        self.assertIn("card-page--book", book)
        self.assertIn('class="book-mark"', book)
        self.assertIn('class="book-download"', book)
        self.assertIn(f'href="{pdf_url}"', book)
        self.assertIn(f'data-book-source="{pdf_url}"', book)
        self.assertIn('data-book-page-offset="6"', book)
        self.assertIn('data-book-numbered-pages="87"', book)
        self.assertIn('max="87"', book)
        self.assertIn('download="birds-of-israel-index.pdf"', book)
        self.assertIn("5.0 MB · 98 pages", book)
        self.assertIn("download.svg", book)

        self.assertNotIn("data-book-pages", book)
        self.assertNotIn("page-001.jpeg", book)
        self.assertNotIn('class="book-page"', book)
        self.assertIn('class="book-pdf" data-book-pdf', book)
        self.assertIn("data-book-counter", book)
        self.assertIn("data-book-prev", book)
        self.assertIn("data-book-next", book)
        self.assertIn("data-book-goto", book)
        self.assertIn('data-book-goto novalidate', book)
        self.assertIn("data-book-goto-input", book)
        self.assertIn("assets/vendor/pdflip/pdflip.global.js", book)
        self.assertIn("assets/js/pages/book.js", book)
        self.assertIn("The page-turn preview needs JavaScript", book)
        self.assertIn('class="note-intro"', book)
        self.assertIn('class="note-intro-figure"', book)
        self.assertIn('class="note-intro-copy"', book)
        self.assertIn("565 species<br>in 84 families.", book)
        self.assertIn(
            "I designed and edited this book to be carried into the field.",
            book,
        )
        self.assertIn("<strong>third edition</strong>", book)
        self.assertIn("<em>Hebrew</em>", book)
        self.assertIn("<mark>unpacks the Latin</mark>", book)
        self.assertNotIn("A learning aid, not a field guide.", book)
        self.assertNotIn(
            "It is a learning aid rather than a field guide.", book
        )
        self.assertNotIn("The third edition", book)
        self.assertNotIn("Swipe, drag a page edge", book)
        self.assertNotIn("placeholder", book.lower())

        controls = book[
            book.index('class="book-controls"') : book.index(
                'class="book-counter"'
            )
        ]
        self.assertLess(controls.index("data-book-next"), controls.index("data-book-goto"))
        self.assertLess(controls.index("data-book-goto"), controls.index("data-book-prev"))
        self.assertIn('<span aria-hidden="true">&larr;</span> Next', controls)
        self.assertIn('Previous <span aria-hidden="true">&rarr;</span>', controls)

        book_css = (
            DIST / "assets" / "css" / "pages" / "book.css"
        ).read_text(encoding="utf-8")
        self.assertIn("dirty-background.jpg", book_css)
        self.assertIn(
            '@import url("../../vendor/pdflip/pdflip.css")', book_css
        )
        self.assertIn(".book-pdf", book_css)
        self.assertIn(".book-goto", book_css)
        self.assertIn(".card-page--book .note-intro", book_css)
        self.assertIn(".card-page--book .book-actions", book_css)
        self.assertIn("align-self: end", book_css)
        self.assertIn("display: contents", book_css)
        self.assertIn("padding-right: calc(var(--artifact)", book_css)
        self.assertIn("position: absolute", book_css)
        self.assertIn("right: 0", book_css)
        self.assertIn(".pdflip-toolbar", book_css)
        self.assertIn("justify-content: flex-start", book_css)

        site_css = (DIST / "assets" / "css" / "site.css").read_text(
            encoding="utf-8"
        )
        self.assertIn(".note-intro", site_css)
        self.assertIn(".note-intro mark", site_css)
        self.assertIn("box-decoration-break: clone", site_css)
        self.assertIn("prefers-reduced-motion: reduce", book_css)
        self.assertNotIn("openpageflip", book_css)

        book_js = (
            DIST / "assets" / "js" / "pages" / "book.js"
        ).read_text(encoding="utf-8")
        self.assertIn("new window.Pdflip.Flipbook", book_js)
        self.assertIn('direction: "rtl"', book_js)
        self.assertIn('flipStyle: "cover"', book_js)
        self.assertIn("pageMode: \"auto\"", book_js)
        self.assertIn("disableRange: true", book_js)
        self.assertIn("data-book-page-offset", book_js)
        self.assertIn("data-book-numbered-pages", book_js)
        self.assertIn("target + offset", book_js)
        self.assertIn("book.goTo(physical)", book_js)
        self.assertIn('" of " + numberedPages', book_js)
        self.assertIn("data-book-goto-input", book_js)
        self.assertIn("data-book-prev", book_js)
        self.assertNotIn("OpenPageFlip", book_js)

        for asset in (
            "pdflip.global.js",
            "pdflip.css",
            "LICENSE",
            "pdfjs/pdf.min.mjs",
            "pdfjs/pdf.worker.min.mjs",
            "pdfjs/LICENSE",
        ):
            self.assertTrue(
                (DIST / "assets" / "vendor" / "pdflip" / asset).is_file(),
                asset,
            )
        self.assertTrue((DIST / "assets" / "icons" / "download.svg").is_file())

    def test_learning_aid_is_a_title_and_a_photo(self):
        learn = (DIST / "learn" / "index.html").read_text(encoding="utf-8")

        self.assertIn("<title>Learning Aid — Ran Regev</title>", learn)
        self.assertIn(
            '<meta name="description" content="A companion trainer for learning '
            'the birds of Israel, in development.">',
            learn,
        )
        self.assertIn("assets/css/pages/holding.css", learn)
        self.assertIn("card-page--learn", learn)
        self.assertIn('class="learn-plate"', learn)
        self.assertIn('class="construction-stamp"', learn)
        self.assertIn("Under Construction", learn)
        self.assertIn("assets/general/learning-aid-weaver.jpg", learn)
        self.assertIn('width="1920" height="1280"', learn)
        self.assertIn(
            "A male black-headed weaver hangs upside down beneath a half-built "
            "grass nest.",
            learn,
        )
        self.assertIn('class="visually-hidden"', learn)
        self.assertIn("CC BY-SA 4.0", learn)
        self.assertIn("creativecommons.org/licenses/by-sa/4.0", learn)
        self.assertIn('href="../book/index.html"', learn)
        self.assertNotIn("construction-plate", learn)
        self.assertNotIn("construction-strip", learn)
        self.assertNotIn("One strand at a time", learn)
        self.assertNotIn("The trainer is still being built", learn)
        self.assertNotIn("The book is the list", learn)
        self.assertNotIn("Lorem ipsum", learn)
        self.assertNotIn("placeholder", learn.lower())

        learn_css = (
            DIST / "assets" / "css" / "pages" / "holding.css"
        ).read_text(encoding="utf-8")
        self.assertIn("dirty-background.jpg", learn_css)
        for hidden in (
            ".card-page .back-link",
            ".card-page .eyebrow",
            ".card-page .lede",
            ".card-page .badge",
            ".card-page .learn-mark",
        ):
            self.assertIn(hidden, learn_css)
        self.assertIn("display: none", learn_css)
        self.assertIn(".learn-plate", learn_css)
        self.assertIn(".construction-stamp", learn_css)
        self.assertIn("transform: rotate(-7deg)", learn_css)
        self.assertIn("object-fit: cover", learn_css)
        self.assertIn("height: 100%", learn_css)
        self.assertIn("min-height: 0", learn_css)
        self.assertTrue(
            (DIST / "assets" / "general" / "learning-aid-weaver.jpg").is_file()
        )

    def test_about_and_contact_are_holding_pages(self):
        pages = {}
        for slug, title, description in (
            ("about", "About", "About Ran Regev."),
            ("contact", "Contact", "Contact Ran Regev."),
        ):
            page = (DIST / slug / "index.html").read_text(encoding="utf-8")
            pages[slug] = page
            self.assertIn(f"<title>{title} — Ran Regev</title>", page)
            self.assertIn(
                f'<meta name="description" content="{description}">', page
            )
            self.assertIn("assets/css/pages/holding.css", page)
            self.assertIn(f"card-page--{slug}", page)
            self.assertIn('class="learn-plate"', page)
            self.assertIn('class="construction-stamp"', page)
            self.assertIn("Under Construction", page)
            self.assertIn(
                "assets/general/learning-aid-weaver.jpg", page
            )
            self.assertIn('class="visually-hidden"', page)
            self.assertIn("CC BY-SA 4.0", page)
            self.assertNotIn("Lorem ipsum", page)
            self.assertNotIn("placeholder-note", page)
            self.assertNotIn("construction-strip", page)

        self.assertNotIn("contact-panel", pages["about"])
        self.assertNotIn("contact-panel", pages["contact"])
        self.assertNotIn("<form", pages["contact"])
        self.assertIn('href="../learn/index.html"', pages["about"])
        self.assertIn('href="../contact/index.html"', pages["about"])
        self.assertIn('href="../about/index.html"', pages["contact"])

        holding_css = (
            DIST / "assets" / "css" / "pages" / "holding.css"
        ).read_text(encoding="utf-8")
        for slug in ("learn", "about", "contact"):
            self.assertIn(f'body[data-page="{slug}"]', holding_css)
        self.assertIn(".card-page .back-link", holding_css)
        self.assertIn(".learn-plate", holding_css)
        self.assertIn(".construction-stamp", holding_css)

    def test_page_css_links_are_content_versioned(self):
        for slug in (
            "engineering",
            "cpp-standards",
            "talks",
            "ringing",
            "rescues",
            "book",
            "learn",
            "about",
            "contact",
        ):
            page = (DIST / slug / "index.html").read_text(encoding="utf-8")
            self.assertIn(".css?v=", page, slug)

    def test_shared_css_links_are_content_versioned(self):
        hub = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertIn("assets/css/theme.css?v=", hub)
        self.assertIn("assets/css/board.css?v=", hub)

        for slug in (
            "engineering",
            "cpp-standards",
            "talks",
            "ringing",
            "rescues",
            "podcast",
            "book",
            "learn",
            "about",
            "contact",
        ):
            page = (DIST / slug / "index.html").read_text(encoding="utf-8")
            self.assertIn("assets/css/theme.css?v=", page, slug)
            self.assertIn("assets/css/site.css?v=", page, slug)

    def test_ringing_page_specific_design(self):
        ringing = (DIST / "ringing" / "index.html").read_text(encoding="utf-8")
        self.assertIn("assets/css/pages/ringing.css", ringing)
        self.assertIn("card-page--ringing", ringing)
        self.assertNotIn("hang-rig--perch", ringing)
        self.assertNotIn("robin-img", ringing)
        self.assertNotIn("closing_on_birds_robin.png", ringing)
        self.assertIn('class="ring-band"', ringing)
        self.assertIn("bird-ring.svg", ringing)
        self.assertEqual(ringing.count('class="species-deck"'), 7)
        self.assertIn('data-deck', ringing)
        self.assertIn('data-count="4"', ringing)
        self.assertIn('data-count="2"', ringing)
        self.assertIn('class="deck-cards"', ringing)
        self.assertEqual(ringing.count('<button class="deck-card'), 18)
        self.assertIn('class="deck-base"', ringing)
        self.assertIn('class="deck-note"', ringing)
        self.assertIn('class="deck-species"', ringing)
        self.assertIn('aria-pressed="true"', ringing)
        self.assertIn('style="--i: 0"', ringing)
        self.assertIn("2 photos", ringing)
        self.assertIn("3 photos", ringing)
        self.assertIn('data-count="3"', ringing)
        self.assertIn("4 photos", ringing)
        self.assertIn("White-spectacled Bulbul", ringing)
        self.assertNotIn('class="media-title"', ringing)
        self.assertNotIn("pages/podcast.css", ringing)

        for phrase in (
            "flying into the net",
            "caught early in the morning before sunrise",
            "Just a lovely Hoopoe.",
            "rarer than European stonechats",
            "normally fast to fly once done",
            "mixed colors on its cap",
        ):
            self.assertIn(phrase, ringing)

        ringing_css = (
            DIST / "assets" / "css" / "pages" / "ringing.css"
        ).read_text(encoding="utf-8")
        self.assertIn("dirty-background.jpg", ringing_css)
        self.assertIn(".card-page--ringing", ringing_css)
        self.assertIn(".species-deck", ringing_css)
        self.assertIn(".deck-card", ringing_css)
        self.assertIn(".deck-base", ringing_css)
        self.assertIn(".deck-note", ringing_css)
        self.assertIn(".ring-mark", ringing_css)
        self.assertIn(".ring-band", ringing_css)
        self.assertIn("--fan-step: 10deg", ringing_css)
        self.assertIn("--fan-direction: -1", ringing_css)
        self.assertIn(
            "calc(var(--i) * var(--fan-step) * var(--fan-direction))",
            ringing_css,
        )
        self.assertIn("transform-origin: 50% 100%", ringing_css)
        self.assertIn("rotate(var(--angle))", ringing_css)
        self.assertIn("var(--stack-rank", ringing_css)
        self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr))", ringing_css)
        self.assertIn("aspect-ratio: 4 / 5", ringing_css)
        self.assertIn("flex: 1 1 auto", ringing_css)
        self.assertIn(".deck-card:focus-visible", ringing_css)
        self.assertIn("outline: 2px solid var(--gold)", ringing_css)
        self.assertNotIn(".card-page--ringing .prose > p", ringing_css)
        self.assertIn("prefers-reduced-motion: reduce", ringing_css)

        site_js = (DIST / "assets" / "js" / "site.js").read_text(encoding="utf-8")
        self.assertIn("using-pointer", site_js)
        self.assertIn("[data-deck]", site_js)
        self.assertIn("[data-card]", site_js)
        self.assertIn("is-presented", site_js)
        self.assertIn("is-open", site_js)
        self.assertIn("aria-pressed", site_js)
        self.assertIn("pointerdown", site_js)
        self.assertIn("--stack-rank", site_js)
        self.assertIn("updateStack", site_js)
        self.assertIn(
            "var next = cards[(cards.indexOf(card) + 1) % cards.length]",
            site_js,
        )

        ring = (DIST / "assets" / "icons" / "bird-ring.svg").read_text(
            encoding="utf-8"
        )
        self.assertIn("#D9DDE1", ring)
        self.assertNotIn("#C6A465", ring)
        self.assertIn("ring-opening", ring)

        photos = json.loads(
            (DATA_DIR / "photos.json").read_text(encoding="utf-8")
        )
        species = json.loads(
            (DATA_DIR / "species.json").read_text(encoding="utf-8")
        )
        labels = {record["id"]: record["name"] for record in species}
        ringing_photos = [
            photo
            for photo in photos
            if "ringing" in photo.get("collections", [])
        ]
        ordered = sort_latest(
            ringing_photos, lambda photo: iso_date(photo.get("date"))
        )
        group_order = []
        for photo in ordered:
            if photo["species"] not in group_order:
                group_order.append(photo["species"])
        positions = [
            ringing.index(f'class="deck-species">{labels[species_id]}<')
            for species_id in group_order
        ]
        self.assertEqual(positions, sorted(positions))

        for species_id in group_order:
            group = [
                photo for photo in ordered if photo["species"] == species_id
            ]
            count = "1 photo" if len(group) == 1 else f"{len(group)} photos"
            dates = []
            for photo in group:
                stamp = display_date(photo.get("date"))
                if stamp and stamp not in dates:
                    dates.append(stamp)
            meta = " · ".join([count] + dates)
            self.assertIn(meta, ringing)

    def test_rescues_page_specific_design(self):
        rescues = (DIST / "rescues" / "index.html").read_text(encoding="utf-8")
        self.assertIn("assets/css/pages/rescues.css", rescues)
        self.assertIn("card-page--rescues", rescues)
        self.assertIn('data-video="video-falco-tinnunculus"', rescues)
        self.assertIn('data-video="video-milvus-migrans"', rescues)
        self.assertEqual(rescues.count('class="rescue-row"'), 6)
        self.assertEqual(rescues.count('class="rescue-row-mark"'), 6)
        self.assertEqual(rescues.count('class="rescue-mark"'), 1)
        self.assertEqual(rescues.count('class="rescue-stack"'), 6)
        self.assertEqual(rescues.count('<button class="stack-card'), 30)
        self.assertIn("data-reel-card", rescues)
        self.assertIn('aria-pressed="true"', rescues)
        self.assertIn('style="--depth: 0; z-index: 5"', rescues)
        self.assertNotIn("media-card--with-reel", rescues)
        for poster in (
            "assets/rescues/ardea_alba/ardea_alba_frame_6.jpeg",
            "assets/rescues/ciconia_ciconia/ciconia_ciconia_frame_6.jpeg",
            "assets/rescues/microcarbo_pygmeus/microcarbo_pygmeus_frame_6.jpeg",
            "assets/rescues/pelecanus_onocrotalus/pelecanus_onocrotalus_1.jpeg",
            "assets/rescues/falco_tinnunculus/falco_tinnunculus_frame_1.jpeg",
            "assets/rescues/milvus_migrans/milvus_migrans_frame_6.jpeg",
        ):
            self.assertIn(f'poster="{MEDIA.base}/{poster}"', rescues)
        self.assertIn('class="media-title">Common Kestrel', rescues)
        self.assertIn('class="media-title">Black Kite', rescues)

        videos = json.loads(
            (DATA_DIR / "videos.json").read_text(encoding="utf-8")
        )
        for video in videos:
            if "rescues" not in video.get("collections", []):
                continue
            self.assertEqual(len(video.get("photos", [])), 5)
            self.assertNotIn(video["poster"], video["photos"])

        rescues_css = (
            DIST / "assets" / "css" / "pages" / "rescues.css"
        ).read_text(encoding="utf-8")
        for needle in (
            ".rescue-row",
            ".rescue-stack",
            ".stack-card.is-presented",
            ".stack-card:focus-visible",
            "outline: 2px solid var(--gold)",
            'grid-template-areas: "photos copy media"',
            "repeat(3, minmax(0, 1fr))",
            "--stack-x: 6px",
            "var(--depth",
            "position: absolute",
            "prefers-reduced-motion",
        ):
            self.assertIn(needle, rescues_css)

        site_js = (DIST / "assets" / "js" / "site.js").read_text(encoding="utf-8")
        for needle in (
            "[data-reel]",
            "data-reel-card",
            "is-presented",
            "% cards.length",
        ):
            self.assertIn(needle, site_js)

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

        rescues = (DIST / "rescues" / "index.html").read_text(encoding="utf-8")
        video_records = json.loads(
            (DATA_DIR / "videos.json").read_text(encoding="utf-8")
        )
        rescue_videos = [
            video
            for video in video_records
            if "rescues" in video.get("collections", [])
        ]
        ordered_videos = sort_latest(
            rescue_videos, lambda video: iso_date(video.get("date"))
        )
        positions = [
            rescues.index(f'data-video="{video["id"]}"')
            for video in ordered_videos
        ]
        self.assertEqual(positions, sorted(positions))

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


    def test_card_pagers_wrap_around(self):
        first = (DIST / "engineering" / "index.html").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            'class="pager-prev" href="../contact/index.html"', first
        )
        self.assertIn(
            'class="pager-next" href="../cpp-standards/index.html"', first
        )

        last = (DIST / "contact" / "index.html").read_text(encoding="utf-8")
        self.assertIn(
            'class="pager-prev" href="../about/index.html"', last
        )
        self.assertIn(
            'class="pager-next" href="../engineering/index.html"', last
        )

        home = (DIST / "learn" / "index.html").read_text(encoding="utf-8")
        self.assertIn(
            'class="pager-prev" href="../book/index.html"', home
        )
        self.assertIn(
            'class="pager-next" href="../about/index.html"', home
        )


if __name__ == "__main__":
    unittest.main()
