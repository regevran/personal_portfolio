#!/usr/bin/env bash
# Build the portfolio into dist/.
#
# Two validation passes bracket the build: the first checks the source data,
# the second checks the generated HTML. Validation lives in tests/. Missing
# listing dates are reported as warnings, not failures.
set -euo pipefail
cd "$(dirname "$0")"

SERVE=0
RUN_TESTS=1
FETCH_REPOS=1

usage() {
  cat <<'EOF'
Usage: ./render.sh [--serve] [--skip-tests] [--offline]

  --serve       serve dist/ at http://localhost:8000 after building
  --skip-tests  skip validation and date warnings (not recommended)
  --offline     do not refresh repository last-push dates from GitHub
  -h, --help    show this message

GITHUB_TOKEN raises the GitHub API rate limit for the repository refresh.
EOF
}

for arg in "$@"; do
  case "$arg" in
    --serve) SERVE=1 ;;
    --skip-tests) RUN_TESTS=0 ;;
    --offline) FETCH_REPOS=0 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "render.sh: unknown option $arg" >&2; exit 2 ;;
  esac
done

command -v python3 >/dev/null || { echo "render.sh: python3 not found" >&2; exit 1; }
command -v pandoc >/dev/null || { echo "render.sh: pandoc not found" >&2; exit 1; }

if [ "$FETCH_REPOS" -eq 1 ]; then
  echo "== refreshing repo dates =="
  python3 fetch_repos.py \
    || echo "warning: repo date refresh failed; using cached dates" >&2
fi

if [ "$RUN_TESTS" -eq 1 ]; then
  echo "== validating content =="
  python3 -m unittest -q tests.test_content

  echo "== date warnings =="
  python3 -m tests.warnings
fi

echo "== building =="
python3 build.py

if [ "$RUN_TESTS" -eq 1 ]; then
  echo "== validating output =="
  python3 -m unittest -q tests.test_output
fi

if [ "$SERVE" -eq 1 ]; then
  echo "Serving dist/ at http://localhost:8000 (Ctrl+C to stop)"
  exec python3 -m http.server -d dist 8000
fi
