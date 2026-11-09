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

Adding a card: create `content/cards/<slug>/card.json` with the metadata and
`blocks`, plus the prose files the prose blocks reference. The directory name is
the slug; the tests and hub pick it up automatically. No renderer change is
needed for a new card.

## Data model

- `site.json`: `name`, `tagline`, `intro`, `email`, `phone`, `github`.
- `cards/<slug>/card.json`: `{title, kicker, family, summary, order, status,
  audio, description, blocks}`. `status` is one of `ready`,
  `under-construction`, `coming-soon`, `placeholder`; `family` is one of
  `software`, `nature`, `neutral` and drives the provisional card colours.
  `audio` is `null` or a path under `assets/`. The slug is the directory name.
- Every dataset record has a stable `id` and a `collections` list. A collection
  is a selection tag, not an index: several records share one; a record can be
  in several. `hidden` is reserved — a record carrying it is excluded from
  collection selection, and removing it restores the record.
- `papers.json`: `{id, collections, wg21, title, role, year, link,
  description}`.
- `talks.json`: `{id, collections, title, url, description, date, sort_date}`.
  `date` is the display label; `sort_date` is ISO `YYYY-MM-DD` or null.
- `episodes.json`: `{id, collections, title, url, date, sort_date,
  description_src}`. `description_src` points into `content/data/episodes/`; an
  inline `description` is the fallback for other datasets.
- `repos.json`: `{id, collections, name, url, description, pushed_at}`.
  `pushed_at` is refreshed from the GitHub API by `fetch_repos.py` and is an ISO
  timestamp or null.
- `videos.json`: `{id, collections, title, species, src, youtube, date,
  description}`. `youtube` takes precedence when set; `date` is ISO
  `YYYY-MM-DD` or null. Video files are not committed: a missing local `src`
  (with no `youtube`) is a hard validation error.
- `photos.json`: `{id, collections, src, title, caption, date, audio}`. `date`
  is ISO `YYYY-MM-DD` or null.

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
4. Render each card's blocks in order: prose via pandoc, contact from site
   data, datasets selected by collection or id and sorted latest-first.
5. Compose `dist/<slug>/index.html` from `card.html` + `base.html`.
6. Compose `dist/index.html` from `index.html` + `base.html`.
7. Write `.nojekyll` (harmless now, useful for GitHub Pages later).

## Conventions

- **Relative URLs only.** No leading `/`. Card pages use `../` as their root
  prefix; the hub uses `""`.
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
