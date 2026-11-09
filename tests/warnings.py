"""Print non-fatal warnings for listing entries without a date.

Run by the CMake build before rendering. Exit status is always 0: missing
dates affect ordering only, not correctness.
"""

from tests.validate import date_warnings


def main() -> int:
    warnings = date_warnings()
    if not warnings:
        print("No missing dates.")
        return 0

    print(f"{len(warnings)} item(s) have no date and will sort last:")
    for warning in warnings:
        print(f"  - {warning}")
    print("Add the missing fields in the files above and re-run the site build.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
