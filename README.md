# Ran Regev — personal portfolio

A static, data-driven portfolio. Content lives in `content/` and `assets/`;
CMake builds the site into `dist/`. The generated output is plain static HTML
with relative URLs, so it can be inspected locally or moved to any static host
later. Open work is tracked in [`TODO.md`](TODO.md).

## Requirements

- `cmake` 3.25+ and `ninja`
- `python3` (3.11+; standard library only)
- `pandoc` (tested with 3.9.0.2)
- Network access only for the explicit GitHub last-push refresh

No Node, npm, or Python packages are required. Set `GITHUB_TOKEN` to raise the
GitHub API rate limit when refreshing repo dates.

## Build

```sh
cmake --preset default          # configure the build/ tree once
cmake --build --preset default  # render dist/ (incremental)
ctest --preset default          # validate content and generated output

cmake --workflow --preset site    # configure, build, validate in one command
cmake --workflow --preset refresh # refresh repo dates, build, validate
cmake --build --preset serve      # build, then serve dist/ on :8000
cmake --build --preset test      # build, then run ctest
cmake --build --preset help      # print the available commands

cmake --install build            # stage a deploy copy under build/install/
```

Then open `dist/index.html` in a browser. The build prints the absolute path of
the generated index. The default build is **offline** and uses the cached dates
in `content/data/repos.json`; the `refresh` workflow or the `site-refresh-repos`
target updates them from GitHub.

`cmake --install build --prefix <directory>` stages the generated site for a
future deploy. The host and upload step are still deferred.

Missing listing dates are reported as warnings before the build; they never
fail it. The affected entries sort last.

## Design preview

`design/index.html` links to the chosen direction and its anchor studies:

- `direction-a.html` — the 16:9 yin-yang poster. One dirty composite background
  (`assets/general/board-background.jpg`) carries a sharp Ran + owl
  cutout with the owl's eye on the yin-yang eye. Eleven title-only cards
  surround it: nature scattered on the left, software on the right, and About
  and Contact as two flat, bottom-aligned cards. Hanging cards use varied
  rotations; the robins are rotated and mirrored and sit on their perches. The yin-yang group sits right of centre to give
  nature more room. Compact C05 lanyards sit above the software cards; compact
  N03 robin perches above the nature cards. The robins use the transparent PNG
  at `assets/general/closing_on_birds_robin.png` (56 × 72 px, `object-fit:
  contain`, bottom-aligned). The board fits the viewport
  when it can and pans horizontally when it cannot; there is no vertical page
  scroll. A fixed title bar carries the name, email, phone, and the
  About / Work / Nature / Contact navigation.
- `hooks.html` — ten anchor studies: five nature anchors (rope & nail, twig
  hook, robin perch, vine loop, wooden peg) and five computer anchors (cable
  loop, binder ring, pegboard hook, monitor arm, lanyard). N03 and C05 are
  marked as the selected pair.

The previews use the book palette, the motif library in `design/assets/motifs/`,
and the single composite background. The approved board is now integrated as
the site hub (`templates/index.html` + `assets/css/board.css`); the card pages
use the same palette and type through `assets/css/theme.css`. The design pages
themselves remain reference-only and are not part of the site build.

Run the tests alone:

```sh
ctest --preset default
```

(`output-validation` requires a built `dist/`.)

## Layout

```text
content/
  cards/
    <slug>/
      card.json    page metadata and ordered blocks
      page.md      page prose (any number of prose files)
  data/
    *.json         canonical records (papers, talks, episodes, repos, videos, photos)
    episodes/      per-episode description Markdown
    repos/         per-repository description Markdown
templates/         base shells, the hub board, card pages and partials
assets/            images, videos, documents, CSS and JS
  css/theme.css    palette, type, topbar and footer
  css/board.css    the hub board
  css/site.css     shared card pages
  css/pages/       optional per-page styles (podcast.css, engineering.css, cpp-standards.css)
  icons/           platform, GitHub, C++ logo and paper marks; lanyard
  fonts/           Patrick Hand (OFL)
tests/             all content and output validation
src/               Python build package
  __init__.py
  build.py         the renderer (Python standard library)
  site_schema.py   dataset registry and block-selection semantics
  fetch_repos.py   refreshes repo last-push dates from GitHub
CMakeLists.txt     build entry point and validation targets
CMakePresets.json  configure/build/test/workflow presets
build/             CMake build tree (ignored by git)
dist/              generated output (ignored by git)
```

### Editing content

- **Card pages:** `content/cards/<slug>/card.json` holds the hub metadata
  (title, kicker, order, status, family, summary, description, audio, board
  placement, optional `logo`/`logo_alt`, optional `mark`) and the ordered
  `blocks` list. The directory name is the slug.
- **Per-page styling:** if `assets/css/pages/<slug>.css` exists, the build
  links it after `site.css` on that page only. Podcast uses
  `assets/css/pages/podcast.css` for its dirty background and floating chapter
  cards; Public GitHub uses `assets/css/pages/engineering.css` for its
  GitHub-logo header and pull-out repository cards; C++ & Standards uses
  `assets/css/pages/cpp-standards.css` for its C++ logo header and paper
  cards.
- **Repository cards:** a full description is clamped to a preview with a
  `More…` toggle at the bottom of the card. Opening one expands it to its full
  height, changes the label to `Less…`, and closes any other open repository
  card. The height animates over 240 ms, and `prefers-reduced-motion` turns
  the animation off. The toggle is only shown when the description actually
  overflows; with JavaScript disabled the full text stays visible. The
  behaviour lives in `assets/js/site.js`.
- **Links:** internal navigation (hub cards, back link, pager) stays in the
  same tab. External links in card data and Markdown open in a new tab with
  `rel="noopener"`; the renderer adds this to http(s) links in Markdown and to
  paper, repository and talk links.
- **Board placement:** the `board` object holds `x`, `y` (or `bottom`), `tilt`,
  `anchor` (`perch`, `lanyard`, `none`) and, for perch cards, `robin` tilt/flip.
  The hub renders directly from it; validation ties the anchor to the family.
- **Card prose:** Markdown files in the same directory, referenced by `prose`
  blocks. A page can use any number of prose fragments. Links and images in
  Markdown are written relative to the site root (`assets/...`); the renderer
  adds the page prefix (`../` on card pages) so the same path works from
  source and from `dist/`. Leave absolute URLs, anchors and `../` paths as
  they are.
- **Structured data:** `content/data/*.json` — `papers`, `talks`, `episodes`,
  `repos`, `videos`, `photos`. Every record has a stable `id` and a
  `collections` list.
- **Episode descriptions:** `content/data/episodes/<slug>.md`, referenced by
  `"description_src"` in `episodes.json`.
- **Repository descriptions:** `content/data/repos/<name>.md`, referenced by
  `"description_src"` in `repos.json`. Each file holds the full Markdown body
  for the repository card; the first paragraph doubles as its one-line
  summary. Use `##` and below for subheadings, not `#`.
- **Episode links:** `episodes.json` records carry `links` with `spotify`,
  `apple`, and `pocketcasts` URLs. Episode titles are not links; each card
  renders the three platform logos. A missing direct link falls back to the
  platform show page.
- **Identity and contact:** `content/data/site.json`; it also holds the footer
  sentence under `footer`.

Blocks render **in array order**. To move a section, reorder the `blocks` array
in `card.json`; no code changes are needed. A block selects records with
`{"collection": "name"}` or, for explicit curation, `{"ids": [...]}`:

| Block | Renders |
|---|---|
| `{"type": "prose", "src": "page.md"}` | one Markdown fragment |
| `{"type": "papers", "select": {"collection": "cpp-standards"}}` | WG21 papers |
| `{"type": "talks", "select": {"collection": "talks"}}` | talks |
| `{"type": "episodes", "select": {"collection": "podcast"}}` | podcast episodes |
| `{"type": "repos", "select": {"collection": "engineering"}}` | repositories |
| `{"type": "videos", "select": {"collection": "rescues"}}` | video grid |
| `{"type": "photos", "select": {"collection": "ringing"}}` | photo gallery |
| `{"type": "contact"}` | contact panel and form |

Collection selection ignores records whose `collections` contains `hidden`, so
soft-removing a record means adding `"hidden"`; remove it again to restore the
record. Explicit `ids` selection is not affected by `hidden`.

All listings render **latest first**: papers by `year`, talks and episodes by
`sort_date`, videos and photos by `date`, repositories by `pushed_at`. A `null`
date sorts to the end and keeps the source order. Explicit `ids` keep the order
given. Use `cmake --build --preset refresh-repos` (or the `refresh` workflow) to
refresh `pushed_at` from GitHub; the default build is offline. Photos and rescue
videos currently have no embedded capture dates; fill their `date` fields when
known and the warnings will stop.

### Videos

Videos are embedded from local files for now. Each video entry in
`content/data/videos.json` may instead carry a `"youtube"` field (a video ID or
embed URL); the renderer then emits a YouTube iframe and ignores `src`. That is
the intended switch once the clips are uploaded. The `collections` field decides
which card blocks include a clip.

Video files are not committed (`*.mp4` is ignored). A missing local video is a
**hard validation error**, not a warning or placeholder: the working copy needs
the files until each entry has a `youtube` value. Once `youtube` is set, the
local-file check is skipped and the iframe is used, so a clean checkout builds
again.

### Placeholders

The site is intentionally a structural skeleton:

- All prose that is not yet written is lorem ipsum.
- The Birding card is a placeholder for future photographs and field stories;
  Ringing carries the current ringing photographs.
- The CV link and the book PDF are placeholders until the real files arrive.
- Cards are colour-coded by family (`software`, `nature`, `neutral`).
- Software cards on the hub are portrait notes hanging from narrow lanyards,
  with a per-page artifact mark and the text grouped at the top, with space
  below. Public GitHub uses the GitHub logo; C++ & Standards uses the official
  C++ logo; Talks still uses the conference-badge QR mark until its artifact
  pass. The repository rail keeps the small CMake build tag above the GitHub
  link. Nature and neutral cards remain landscape notes with their
  robin/perch treatment.
- The hub and card pages share the board's visual language: sand and cream,
  Patrick Hand titles for nature and neutral, formal serif titles for software,
  mono kickers, family-coloured edges, and a fixed topbar and footer. The
  card-page pass is still being reviewed.

### Tests

`tests/validate.py` holds the validation logic. `tests/test_content.py` checks
the source tree (card schema, block selectors, dataset ids/collections,
referenced files) and `tests/test_output.py` checks the built `dist/` (pages
exist, internal links resolve, no unreplaced template tokens). The `site`
workflow builds before running `ctest`, so output validation always sees a
fresh `dist/`.
