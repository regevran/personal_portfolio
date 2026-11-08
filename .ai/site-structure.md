# Portfolio — site structure

## Tree

```text
personal_portfolio/
├── .ai/                      context and decisions for AI sessions
├── content/
│   ├── cards/                one Markdown file per page (prose only)
│   └── data/
│       ├── site.json         identity, tagline, contact details
│       ├── cards.json        the site map: order, titles, summaries, status
│       ├── papers.json       WG21 papers
│       ├── talks.json        public talks
│       ├── episodes.json     podcast catalogue
│       ├── repos.json        selected GitHub repositories
│       ├── videos.json       rescue clips and podcast promos
│       └── photos.json       ringing photographs
├── templates/
│   ├── base.html             document skeleton
│   ├── index.html            hub fragment
│   ├── card.html             card page fragment
│   └── partials/contact.html contact panel
├── assets/                   existing topical layout kept
│   ├── css/site.css
│   ├── js/site.js
│   ├── documents/            CV and book PDF placeholders
│   └── ringing/ rescues/ podcast/ ...
├── tests/                    all validation and date warnings
├── build.py                  renderer
├── fetch_repos.py            refreshes repo last-push dates from GitHub
├── render.sh                 build entry point
├── .gitignore
├── README.md
└── dist/                     generated (ignored)
```

## Cards

| Order | Slug | Title | Family | Status |
|---|---|---|---|---|
| 1 | engineering | Engineering & Systems | software | ready |
| 2 | cpp-standards | C++ & Standards | software | ready |
| 3 | talks | Talks | software | ready |
| 4 | birding | Birding & Ringing | nature | ready |
| 5 | rescues | Rescues | nature | ready |
| 6 | podcast | Podcast | nature | ready |
| 7 | book | The Book | nature | coming-soon |
| 8 | learn | Learning Aid | nature | under-construction |
| 9 | about | About & CV | neutral | placeholder |
| 10 | contact | Contact | neutral | ready |

Adding a card: add an entry to `cards.json`, create `content/cards/<slug>.md`,
and (if needed) an include marker. The tests and the hub pick it up
automatically.

## Data model

- `site.json`: `name`, `tagline`, `intro`, `email`, `phone`, `github`.
- `cards.json`: array of `{slug, title, kicker, family, summary, order, status,
  audio, description}`. `status` is one of `ready`, `under-construction`,
  `coming-soon`, `placeholder`; `family` is one of `software`, `nature`,
  `neutral` and drives the provisional card colours. `audio` is `null` or a
  path under `assets/`.
- `papers.json`: `{id, title, role, year, link, description}`.
- `talks.json`: `{title, url, description, date, sort_date}`. `date` is the
  display label; `sort_date` is ISO `YYYY-MM-DD` or null.
- `episodes.json`: `{title, url, description, date, sort_date}`.
- `repos.json`: `{name, url, description, pushed_at}`. `pushed_at` is refreshed
  from the GitHub API by `fetch_repos.py` and is an ISO timestamp or null.
- `videos.json`: `{group, title, species, src, youtube, date, description}`.
  `group` is `rescues` or `podcast-promos`; `youtube` takes precedence when set;
  `date` is ISO `YYYY-MM-DD` or null. Video files are not committed: a missing
  local `src` (with no `youtube`) is a hard validation error.
- `photos.json`: `{src, title, caption, date, audio}`. `date` is ISO
  `YYYY-MM-DD` or null.

## Sorting

Every listing renders **latest first**:

- Papers: by `year` (four-digit string).
- Talks and episodes: by `sort_date`.
- Videos (within each group) and photos: by `date`.
- Repositories: by `pushed_at`, refreshed at render time.

Entries with a `null` date render after the dated entries and keep their source
order. Repos are chronological now; cards remain a curated order.

`tests/warnings.py` (run by `render.sh`, exit status 0) reports every undated
entry with its data file, array index, title, and the field to add.

## Build pipeline

`render.sh`:

1. Check `pandoc` and `python3`.
2. Refresh repository `pushed_at` from GitHub (unless `--offline`); failures
   warn and keep the cached values.
3. Run `python3 -m unittest -q tests.test_content`.
4. Print date warnings via `python3 -m tests.warnings`.
5. Run `python3 build.py`.
6. Run `python3 -m unittest -q tests.test_output`.
7. Optionally serve `dist/` (`--serve`).

`build.py`:

1. Clear and recreate `dist/`.
2. Copy `assets/` (skipping swap files).
3. Read `site.json`, `cards.json`, and datasets.
4. Render each `content/cards/<slug>.md` with pandoc, replace
   `<!-- include:NAME -->` markers with structured HTML.
5. Compose `dist/<slug>/index.html` from `card.html` + `base.html`.
6. Compose `dist/index.html` from `index.html` + `base.html`.
7. Write `.nojekyll` (harmless now, useful for GitHub Pages later).

## Conventions

- **Relative URLs only.** No leading `/`. Card pages use `../` as their root
  prefix; the hub uses `""`.
- **No front matter.** The manifest (`cards.json`) is the single source of card
  metadata; Markdown files contain prose only.
- **Placeholders are explicit.** Lorem ipsum, a disabled CV link, and no book
  PDF yet. Email and phone are real and live in `site.json`.
- **Validation lives in `tests/`.** The build does not duplicate it; the
  renderer only fails on structural errors it cannot continue past.
