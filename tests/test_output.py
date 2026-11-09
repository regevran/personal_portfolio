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
