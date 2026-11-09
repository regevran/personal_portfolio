"""Print non-fatal warnings for the content model.

Run by the CMake build before rendering. Exit status is always 0: missing
dates affect ordering only, and content warnings identify records or blocks
that currently show nothing.
"""

from tests.validate import content_warnings, date_warnings


def main() -> int:
    dates = date_warnings()
    content = content_warnings()

    if not dates and not content:
        print("No missing dates or content warnings.")
        return 0

    if dates:
        print(f"{len(dates)} item(s) have no date and will sort last:")
        for warning in dates:
            print(f"  - {warning}")

    if content:
        print(f"{len(content)} content warning(s):")
        for warning in content:
            print(f"  - {warning}")

    print("Fix the entries above and re-run the site build.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
