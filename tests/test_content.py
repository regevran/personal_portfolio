import unittest

from src.build import iso_date, rewrite_markdown_links, sort_latest
from src.site_schema import select_records
from tests.validate import (
    date_warnings,
    validate_assets,
    validate_cards,
    validate_datasets,
    validate_site,
)


class ContentValidationTest(unittest.TestCase):
    def assert_valid(self, errors):
        self.assertEqual(errors, [], "\n".join(errors))

    def test_site(self):
        self.assert_valid(validate_site())

    def test_cards(self):
        self.assert_valid(validate_cards())

    def test_datasets(self):
        self.assert_valid(validate_datasets())

    def test_assets(self):
        self.assert_valid(validate_assets())


class MarkdownLinkTest(unittest.TestCase):
    def test_relative_links_get_the_page_root(self):
        page = (
            '<p><a href="assets/documents/book.pdf">book</a> '
            '<img src="./assets/icons/github.svg" alt=""></p>'
        )
        rewritten = rewrite_markdown_links(page, "../")
        self.assertIn('href="../assets/documents/book.pdf"', rewritten)
        self.assertIn('src="../assets/icons/github.svg"', rewritten)

    def test_non_relative_links_are_untouched(self):
        page = (
            '<a href="https://example.com/x">https</a>'
            '<a href="mailto:ran@example.com">mail</a>'
            '<a href="#section">anchor</a>'
            '<a href="/root">root</a>'
            '<a href="../sibling">sibling</a>'
        )
        self.assertEqual(rewrite_markdown_links(page, "../"), page)

    def test_no_root_leaves_the_page_unchanged(self):
        page = '<a href="assets/x.pdf">x</a>'
        self.assertEqual(rewrite_markdown_links(page, ""), page)


class SortTest(unittest.TestCase):
    def test_latest_first_and_undated_last(self):
        entries = [
            {"id": "old", "date": "2024-01-01"},
            {"id": "undated", "date": None},
            {"id": "new", "date": "2026-10-20"},
        ]
        ordered = sort_latest(entries, lambda entry: iso_date(entry["date"]))
        self.assertEqual(
            [entry["id"] for entry in ordered], ["new", "old", "undated"]
        )

    def test_ties_keep_source_order(self):
        entries = [
            {"id": "first", "date": "2025-01-01"},
            {"id": "second", "date": "2025-01-01"},
        ]
        ordered = sort_latest(entries, lambda entry: iso_date(entry["date"]))
        self.assertEqual([entry["id"] for entry in ordered], ["first", "second"])


class SelectionTest(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"id": "visible", "collections": ["birding"]},
            {"id": "hidden", "collections": ["birding", "hidden"]},
            {"id": "other", "collections": ["rescues"]},
        ]

    def test_collection_excludes_hidden(self):
        selected = select_records(self.records, {"collection": "birding"})
        self.assertEqual([record["id"] for record in selected], ["visible"])

    def test_ids_keep_explicit_order(self):
        selected = select_records(
            self.records, {"ids": ["other", "visible", "hidden"]}
        )
        self.assertEqual(
            [record["id"] for record in selected],
            ["other", "visible", "hidden"],
        )

    def test_hidden_collection_cannot_be_selected(self):
        with self.assertRaises(ValueError):
            select_records(self.records, {"collection": "hidden"})


class DateWarningTest(unittest.TestCase):
    def test_warnings_point_at_the_data_file_and_field(self):
        for warning in date_warnings():
            self.assertRegex(warning, r"^content/data/\S+ \[\d+\] .+: missing \"\w+\"")


if __name__ == "__main__":
    unittest.main()
