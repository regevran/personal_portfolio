# Portfolio — site structure

## Tree

```text
personal_portfolio/
├── .ai/                      context and decisions for AI sessions
├── content/
│   ├── cards/
│   │   └── <slug>/
│   │       ├── card.json     page metadata and ordered blocks
│   │       └── page.md       page prose (any number of prose files)
│   └── data/
│       ├── site.json         identity, tagline, contact details
│       ├── papers.json       WG21 papers
│       ├── talks.json        public talks
│       ├── episodes.json     podcast catalogue
│       ├── repos.json        selected GitHub repositories
│       ├── videos.json       rescue clips and podcast promos
│       ├── photos.json       ringing photographs
│       └── episodes/         per-episode description Markdown
├── templates/
│   ├── base.html             card page shell
│   ├── base-board.html       hub shell
│   ├── index.html            hub board fragment
│   ├── card.html             card page fragment
│   └── partials/             topbar, footer, board-card, perch, lanyard, contact
├── assets/
│   ├── css/theme.css         palette, type, topbar and footer
│   ├── css/board.css         hub board
│   ├── css/site.css          shared card pages
│   ├── css/pages/            optional per-page styles (podcast.css, engineering.css)
│   ├── js/board.js           horizontal pan and nav shortcuts
│   ├── js/site.js            contact form
│   ├── fonts/                Patrick Hand (OFL)
│   ├── general/              board background, robin PNG, reference assets
│   ├── documents/            CV and book PDF placeholders
│   └── ringing/ rescues/ podcast/ ...
├── tests/                    all validation and date warnings
├── src/
│   ├── __init__.py
│   ├── build.py              renderer
│   ├── site_schema.py        dataset registry and block selection
│   └── fetch_repos.py        refreshes repo last-push dates from GitHub
├── CMakeLists.txt            build entry point and validation targets
├── CMakePresets.json         configure/build/test/workflow presets
├── build/                    CMake build tree (ignored)
├── .gitignore
├── README.md
└── dist/                     generated (ignored)
```

## Cards

| Order | Slug | Title | Family | Status |
|---|---|---|---|---|
| 1 | engineering | Public GitHub | software | ready |
| 2 | cpp-standards | C++ & Standards | software | ready |
| 3 | talks | Talks | software | ready |
| 4 | birding | Birding | nature | placeholder |
| 5 | ringing | Ringing | nature | ready |
| 6 | rescues | Rescues | nature | ready |
| 7 | podcast | Podcast | nature | ready |
| 8 | book | The Book | nature | coming-soon |
| 9 | learn | Learning Aid | nature | under-construction |
| 10 | about | About | neutral | placeholder |
| 11 | contact | Contact | neutral | ready |

Birding and Ringing were one card. Birding is now a placeholder for birding
photographs and field stories; Ringing owns the existing ringing photographs
(`"collections": ["ringing"]`).

Adding a card: create `content/cards/<slug>/card.json` with the metadata,
`board` placement and `blocks`, plus the prose files the prose blocks
reference. The directory name is the slug; the tests and hub pick it up
automatically. No renderer change is needed for a new card.

## Data model

- `site.json`: `name`, `tagline`, `intro`, `email`, `phone`, `github`, `footer`.
  `footer` is the sentence rendered after the copyright line on every page.
- `cards/<slug>/card.json`: `{title, kicker, family, summary, order, status,
  audio, description, board, blocks}`. `status` is one of `ready`,
  `under-construction`, `coming-soon`, `placeholder`; `family` is one of
  `software`, `nature`, `neutral` and drives the card colours and anchors.
  `audio` is `null` or a path under `assets/`; optional `logo` and `logo_alt`
  add a page logo. The slug is the directory name. `board` holds the hub
  placement (see below).
- Every dataset record has a stable `id` and a `collections` list. A collection
  is a selection tag, not an index: several records share one; a record can be
  in several. `hidden` is reserved — a record carrying it is excluded from
  collection selection, and removing it restores the record.
- `papers.json`: `{id, collections, wg21, title, role, year, link,
  description}`.
- `talks.json`: `{id, collections, title, url, description, date, sort_date}`.
  `date` is the display label; `sort_date` is ISO `YYYY-MM-DD` or null.
- `episodes.json`: `{id, collections, title, url, date, sort_date,
  description_src, links}`. `url` is the primary (Spotify) link; `links` holds
  the per-platform URLs `spotify`, `apple`, `pocketcasts`. `description_src`
  points into `content/data/episodes/`; an inline `description` is the fallback
  for other datasets.
- `repos.json`: `{id, collections, name, url, description, pushed_at}`.
  `pushed_at` is refreshed from the GitHub API by `fetch_repos.py` and is an ISO
  timestamp or null.
- `videos.json`: `{id, collections, title, species, src, youtube, date,
  description}`. `youtube` takes precedence when set; `date` is ISO
  `YYYY-MM-DD` or null. Video files are not committed: a missing local `src`
  (with no `youtube`) is a hard validation error.
- `photos.json`: `{id, collections, src, title, caption, date, audio}`. `date`
  is ISO `YYYY-MM-DD` or null.

## Board layout

Every card carries its hub placement in `board`:

- `x` — horizontal position in percent of board width; may be negative
  (Birding deliberately drifts off the left edge).
- `y` — top position in percent of board height for hanging cards.
- `bottom` — distance from the bottom for the flat neutral cards; exactly one
  of `y` or `bottom` is present.
- `tilt` — card rotation in degrees; positive is clockwise.
- `anchor` — `perch` for nature, `lanyard` for software, `none` for neutral.
  Validation enforces the family match.
- `id` — optional DOM id for the top-nav targets (`work`, `nature`, `about`,
  `contact`).
- `robin` — only for `perch`: `{tilt, flip}`. `tilt` is degrees; `flip`
  mirrors the image horizontally.

The values mirror the approved design preview in `design/direction-a.html`.
The hub renderer will read them when the board is integrated.

Blocks are `{type, ...}` objects rendered in order:

- `{"type": "prose", "src": "page.md"}` — Markdown fragment in the card
  directory.
- `{"type": "contact"}` — contact panel from `site.json`.
- `{"type": <dataset>, "select": {"collection": "name"}}` — collection
  selection, excluding hidden records.
- `{"type": <dataset>, "select": {"ids": [...]}}` — explicit records in the
  given order; hidden records are still rendered when named.

Dataset block types: `papers`, `talks`, `episodes`, `repos`, `videos`, `photos`.

## Sorting

Every collection listing renders **latest first**:

- Papers: by `year` (four-digit string).
- Talks and episodes: by `sort_date`.
- Videos and photos: by `date`.
- Repositories: by `pushed_at`.

Entries with a `null` date render after the dated entries and keep their source
order. Explicit `ids` keep the given order. Repos are chronological now; cards
remain a curated order.

`tests/warnings.py` (run by the build, exit status 0) reports every undated
visible entry with its data file, array index, title, and the field to add, plus
records not shown anywhere and blocks selecting an empty collection.

## Build pipeline

CMake is the single build system (matching `../birds`). `CMakeLists.txt` checks
for `python3` 3.11+ and `pandoc`, and `CMakePresets.json` defines the commands.

Targets:

- `site-build` (default `ALL`): render `dist/` with `src/build.py`. A stamp in
  `build/` makes the render incremental; source changes rerun it.
- `site-refresh-repos`: fetch repository `pushed_at` from GitHub. Explicit and
  offline-by-default; failures warn and keep the cached values.
- `site-serve`: build, then serve `dist/` on port 8000.
- `site-test`: build, then `ctest`.
- `usage`: print the command list.

Baseline commands:

```sh
cmake --preset default
cmake --build --preset default
ctest --preset default
cmake --workflow --preset site
cmake --workflow --preset refresh
```

The `site` workflow configures, builds and tests. The `refresh` workflow adds
`site-refresh-repos` before the build so the updated dates are rendered in the
same run. The non-fatal date warnings print during the render. CTest defines
two tests:

1. `content-validation` — `python3 -m unittest -q tests.test_content`.
2. `output-validation` — `python3 -m unittest -q tests.test_output`, ordered
   after the content check; the workflow builds first so `dist/` is fresh.

`cmake --install build` stages `dist/` under the install prefix (the preset
uses `build/install`); the host and upload step for deployment are deferred.

`src/build.py`:

1. Clear and recreate `dist/`.
2. Copy `assets/` (skipping swap files).
3. Read `site.json` and every `content/cards/*/card.json`, sorted by `order`.
4. Build the hub board: each card's `board` metadata produces its position,
   tilt, perch/lanyard rig and robin transform via the `board-card`, `perch`
   and `lanyard` partials. Cards are grouped nature → software → neutral and
   sorted top-down for DOM/tab order; each card links to its page.
5. Render each card's blocks in order: prose via pandoc, contact from site
   data, datasets selected by collection or id and sorted latest-first.
6. Compose `dist/<slug>/index.html` from `card.html` + `base.html`, including
   the shared topbar and footer. If `assets/css/pages/<slug>.css` exists, link
   it after `site.css`; only that page loads it.
7. Compose `dist/index.html` from `index.html` + `base-board.html`, including
   the same topbar and footer.
8. Write `.nojekyll` (harmless now, useful for GitHub Pages later).

## Conventions

- **Relative URLs only.** No leading `/`. Card pages use `../` as their root
  prefix; the hub uses `""`.
- **Fixed chrome.** The topbar and footer are shared partials and stay fixed;
  the main column scrolls between them. The footer sentence comes from
  `site.json`, not from a template.
- **Data and view are separate.** `content/data/` holds domain records and the
  prose that belongs to a record (episode show notes). `content/cards/` holds
  page metadata, page prose and composition. A card points at data; it does not
  copy it.
- **No front matter.** Card metadata is the sidecar `card.json`; Markdown files
  contain prose only.
- **Placeholders are explicit.** Lorem ipsum, a disabled CV link, and no book
  PDF yet. Email and phone are real and live in `site.json`.
- **Validation lives in `tests/`.** The build does not duplicate it; the
  renderer only fails on structural errors it cannot continue past.
