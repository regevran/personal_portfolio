# Portfolio — site structure

## Tree

```text
personal_portfolio/
├── .ai/                      context and decisions for AI sessions
├── .github/workflows/pages.yml  build, test, media check, Pages deploy
├── content/
│   ├── cards/
│   │   └── <slug>/
│   │       ├── card.json       page metadata and ordered blocks
│   │       ├── summary.md      visible page lede
│   │       ├── description.md  meta description
│   │       └── page.md         page prose (any number of prose files)
│   └── data/
│       ├── site.json         identity, tagline, contact details
│       ├── papers.json       WG21 papers
│       ├── talks.json        public talks
│       ├── episodes.json     podcast catalogue
│       ├── repos.json        selected GitHub repositories
│       ├── videos.json       rescue clips and podcast promos
│       ├── photos.json       ringing photographs
│       ├── species.json      species names and note pointers
│       ├── episodes/         per-episode description Markdown
│       ├── repos/            per-repository description Markdown
│       ├── rescues/          per-rescue story Markdown
│       └── species/          per-species note Markdown
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
│   ├── css/pages/            optional per-page styles (podcast, engineering, cpp-standards, talks, ringing, rescues, book, learn)
│   ├── js/board.js           horizontal pan and nav shortcuts
│   ├── js/site.js            contact form, repo accordions, talk videos, species decks, rescue stacks
│   ├── js/pages/book.js      pdflip controls, Go to page, and counter
│   ├── vendor/pdflip/        BSD page-turn engine and pdf.js (pruned)
│   ├── fonts/                Patrick Hand (OFL)
│   ├── general/              board background, robin PNG, Learning Aid weaver photo, reference assets
│   ├── documents/            CV and book PDF (R2-hosted; local backup)
│   └── ringing/ rescues/ podcast/ documents/ ...
├── tests/                    all validation and date warnings
├── src/
│   ├── __init__.py
│   ├── build.py              renderer
│   ├── site_schema.py        dataset registry and block selection
│   ├── media.py              R2 policy, URL rewriting and media inventory
│   ├── fetch_repos.py        refreshes repo last-push dates from GitHub
│   ├── upload_media.py       uploads referenced media to R2
│   └── check_media.py        HEAD check and bucket audit against dist/
├── deploy.json               R2 base, hosted paths, bucket and endpoint
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
| 4 | ringing | Ringing | nature | ready |
| 5 | rescues | Rescues | nature | ready |
| 6 | podcast | Podcast | nature | ready |
| 7 | book | Birds of Israel Index | nature | ready |
| 8 | learn | Learning Aid | nature | under-construction |
| 9 | about | About | neutral | placeholder |
| 10 | contact | Contact | neutral | ready |

Ringing and Birding were one card. Ringing owns the existing ringing
photographs (`"collections": ["ringing"]`). Birding was removed from the hub on
2026-11-17 and is deferred to phase 2, if it returns at all.

Adding a card: create `content/cards/<slug>/card.json` with the metadata,
`board` placement and `blocks`, plus the prose files the prose blocks
reference. The directory name is the slug; the tests and hub pick it up
automatically. No renderer change is needed for a new card.

## Data model

- `site.json`: `name`, `tagline`, `intro`, `email`, `phone`, `github`, `footer`.
  `footer` is the sentence rendered after the copyright line on every page.
- `cards/<slug>/card.json`: `{title, kicker, family, order, status, audio,
  board, blocks}`. `status` is one of `ready`, `under-construction`,
  `coming-soon`, `placeholder`; `family` is one of `software`, `nature`,
  `neutral` and drives the card colours and anchors. `audio` is `null` or a
  path under `assets/`; optional `logo` and `logo_alt` add a page logo. The
  slug is the directory name. `board` holds the hub placement (see below).
  `summary.md` supplies the visible lede; `description.md` supplies the meta
  description. Both are required and non-empty, with no JSON fallback.
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
- `repos.json`: `{id, collections, name, url, description_src, pushed_at}`.
  `description_src` points into `content/data/repos/`; an inline `description`
  is still accepted as a fallback (`description_src` is preferred now). The
  Markdown body renders inside the repository card, including headings,
  lists, links and inline code. `pushed_at` is refreshed from the GitHub API by
  `fetch_repos.py` and is an ISO timestamp or null.
- `videos.json`: `{id, collections, title, species, src, youtube, date,
  poster, description, description_src, photos}`. `youtube` takes precedence
  when set; `date` is ISO `YYYY-MM-DD` or null. `description_src` points into
  `content/data/rescues/` for rescue stories (an inline `description` remains
  the fallback for other videos). `poster` is the selected video poster;
  `photos` is an optional list of still-image paths. The first still is the
  fallback poster, and the photos render as the rescue stills stack. Video
  files are not committed: a missing local `src` (with no `youtube`) is a hard
  validation error. A video block may add `"layout": "rescue-rows"` for the
  full-width stills | text | video rows.
- `photos.json`: `{id, collections, species, src, title, date, audio}`.
  `species` is the id of a `species.json` record; `date` is ISO `YYYY-MM-DD`
  or null. There is no per-photo caption.
- `species.json`: `{id, collections, name, note_src}`. `note_src` points into
  `content/data/species/`; the rendered Markdown is the shared note on the
  species deck. Photos grouped by `"species"` join through this id.

## Board layout

Every card carries its hub placement in `board`:

- `x` — horizontal position in percent of board width; may be negative to let
  a card drift off the left edge.
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
- `{"type": "book", "pdf": ..., "note": ...}` — PDF download button and a
  right-to-left pdflip viewer that reads the PDF from R2. `note` is the optional
  file-size/page-count line under the download label. `page_offset` is the
  number of PDF pages before printed page 1 and `numbered_pages` is the highest
  printed number; together they map the printed pages used by the counter and
  the Go input (book: offset 6, pages 1–87). Front matter, blank leaves and the
  covers get text labels instead of page numbers.
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
- `site-upload`: build, then upload the media referenced by `dist/` to R2.
- `site-check-media`: HEAD every R2 URL used by `dist/`.
- `site-audit-media`: list the bucket and compare it with `dist/`; unused
  objects are warnings.
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
three tests:

1. `content-validation` — `python3 -m unittest -q tests.test_content`.
2. `output-validation` — `python3 -m unittest -q tests.test_output`, ordered
   after the content check; the workflow builds first so `dist/` is fresh.
3. `media-config` — `python3 -m unittest -q tests.test_media`, ordered after
   the output check. It verifies the R2 path policy, the copied tree, and the
   absolute URLs the build emits.

`dist/` is the publishable tree: content media is already absolute and not
copied. `cmake --install build` copies it under the install prefix (the preset
uses `build/install`). The network media checks are explicit targets, not part
of CTest.

`src/build.py`:

1. Clear and recreate `dist/`.
2. Copy `assets/` while skipping swap files and the R2-hosted directories
   (`ringing/`, `rescues/`, `podcast/`, `documents/`).
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
8. Write `.nojekyll` (GitHub Pages serves the files verbatim).

## Deployment

Cloudflare R2 is the source of truth for content media. Every `.jpeg`, `.mp4`
and `.pdf` under `assets/ringing/`, `assets/rescues/`, `assets/podcast/` and
`assets/documents/` lives in the bucket `personal-portfolio` and is referenced
through the public base in `deploy.json`
(`https://pub-2c1165061319472a94d3c24d6ccfc009.r2.dev`). The build emits those
URLs directly and leaves those directories out of `dist/`.

Theme assets stay on GitHub Pages: HTML, CSS, JS, fonts, icons, the vendored
pdflip bundle and the `.jpg` / `.png` images in `assets/general/`. Fonts stay
local because that needs no CORS, and the CSS references `general/` and
`icons/` relatively. The book PDF is fetched by pdflip from R2, so the bucket
CORS policy allows `https://regevran.github.io` and `http://localhost:8000`
with `GET`/`HEAD`; range loading is disabled, so no `Range` headers are needed.

`src/upload_media.py` uploads only files referenced by `dist/`, skips objects
whose size already matches, and never deletes. `src/check_media.py check`
HEADs every referenced URL; `audit` lists the bucket and reports objects no
page uses. Both use the S3 endpoint for listing with the `r2` profile; HEAD
requests use the public URL. `r2.dev` is rate limited, so the HEAD check is
sequential and retries 403/429.

Objects carry `Content-Type: image/jpeg|video/mp4|application/pdf` and
`Cache-Control: public, max-age=604800`. Versioning is off: uploading the same
key replaces the object. Local untracked media files are the backup.

GitHub Pages (`https://regevran.github.io/personal_portfolio/`) is deployed by
`.github/workflows/pages.yml` on pushes to `main` and `workflow_dispatch`. It
installs Python/CMake/Ninja/Pandoc, runs `cmake --workflow --preset site`, runs
`check_media check`, uploads `dist/` as the Pages artifact, and deploys it.
Pages' source is **GitHub Actions**; `configure-pages` enables it on the first
run. The workflow needs no R2 credentials; `audit-media` remains a local
inventory command because it uses the S3 API token.

## Conventions

- **Relative URLs for site assets; absolute URLs for R2 media.** No leading
  `/`. Card pages use `../` as their root prefix; the hub uses `""`. Hosted
  media under the four R2 directories is always an absolute `deploy.json` URL.
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
