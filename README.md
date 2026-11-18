# Ran Regev — personal portfolio

A static, data-driven portfolio. Content lives in `content/` and `assets/`;
CMake builds the site into `dist/`. The generated output is plain static HTML;
content media (JPEG, MP4, PDF) is referenced from Cloudflare R2, and the rest is
published to GitHub Pages. Open work is tracked in [`TODO.md`](TODO.md).

## Requirements

- `cmake` 3.25+ and `ninja`
- `python3` (3.11+; standard library only)
- `pandoc` (tested with 3.9.0.2)
- Network access only for the explicit GitHub last-push refresh and the R2
  upload/check targets

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
cmake --build --preset upload       # upload dist/ media to Cloudflare R2
cmake --build --preset check-media  # HEAD every R2 URL used by dist/
cmake --build --preset audit-media  # compare the bucket with dist/
cmake --build --preset help      # print the available commands

cmake --install build            # copy dist/ under build/install/
```

Then open `dist/index.html` in a browser. The build prints the absolute path of
the generated index. The default build is **offline** and uses the cached dates
in `content/data/repos.json`; the `refresh` workflow or the `site-refresh-repos`
target updates them from GitHub.

Most pages work from `file://`. YouTube playback does not: YouTube refuses its
player without an HTTP referrer. The book PDF viewer also needs HTTP, because
the PDF is cross-origin from R2 and a `file://` page has no allowed origin. Use
`cmake --build --preset serve` for both; the deployed site plays and turns the
pages inline.

Content media is not copied into `dist/`: the build emits absolute URLs from
`deploy.json` for files under `ringing/`, `rescues/`, `podcast/` and
`documents/`. So `dist/` is both the local preview and the deployable tree;
`cmake --install build --prefix <directory>` copies it. The default tests stay
offline; the media checks are explicit targets because they use the network.

Missing listing dates are reported as warnings before the build; they never
fail it. The affected entries sort last.

## Deployment

**Cloudflare R2 is the source of truth for content media.** Every `.jpeg`,
`.mp4` and `.pdf` under these directories lives in the bucket
`personal-portfolio`:

```text
assets/ringing/     assets/rescues/
assets/podcast/     assets/documents/
```

The public base is configured in `deploy.json`:

```text
https://pub-2c1165061319472a94d3c24d6ccfc009.r2.dev
```

`deploy.json` also holds the bucket name and the S3 endpoint used for uploads.
The build emits absolute R2 URLs for those files and does **not** copy them into
`dist/`. Theme assets — CSS, JS, fonts, icons, `vendor/` and `general/`
`.jpg`/`.png` — stay with the HTML. The PDF download link is rewritten like any
other hosted asset; PDFs are uploaded with
`Content-Disposition: attachment` so a cross-origin link still downloads.

### Book PDF and CORS

The book PDF is R2-only and untracked; `assets/documents/*.pdf` is ignored and
the local file is only a backup. The page's viewer is **pdflip** (BSD,
pdf.js), vendored under `assets/vendor/pdflip/`. It fetches the PDF from R2, so
the bucket needs a CORS policy allowing the site origin
(`https://regevran.github.io`) and the local preview
(`http://localhost:8000`), with `GET` and `HEAD`. The viewer sets
`pdfjs.disableRange = true`, so that simple policy is enough; no `Range` or
`Content-Range` headers are needed. No page images or render step exist. The
counter and Go input use the book's printed numbers (1–87), mapped from the
PDF by `page_offset` and `numbered_pages` in `content/cards/book/card.json`:
printed page 1 is PDF page 7.

### Media workflow

When a photo, video or PDF is added or replaced:

1. Put the file under its hosted directory. The book PDF is untracked; copy it
   to `assets/documents/`, which is ignored by git.
2. Build and test: `cmake --workflow --preset site`.
3. Upload the referenced media: `cmake --build --preset upload`. It uploads only
   files referenced by `dist/`, skips objects whose size already matches, sets
   `Content-Type`, `Cache-Control: public, max-age=604800` and the PDF download
   header, and never deletes.
4. Verify: `cmake --build --preset check-media` HEADs every media URL used by
   the site. Failures are missing objects, wrong content types, or rate limiting.
5. Inventory: `cmake --build --preset audit-media` compares the bucket with
   `dist/` and warns about objects that no page references. Use
   `python3 -m src.check_media audit --strict` to make unused objects fatal.

The `r2.dev` host is rate limited: the checker is deliberately sequential and
retries bursts. For a one-person portfolio this is sufficient; the upload uses
the S3 endpoint, never the public URL.

Because the filenames are stable and versioning is off, uploading the same key
replaces the object. Replacing a file may serve the old copy for up to the cache
lifetime; purge that object in Cloudflare when replacing one. The local
untracked media files are the backup, not R2 versions.

### GitHub Pages

**GitHub Pages** serves the site at
<https://regevran.github.io/personal_portfolio/>. The workflow in
`.github/workflows/pages.yml` runs on every push to `main` (and manually through
`workflow_dispatch`):

1. install Python, CMake, Ninja and Pandoc;
2. `cmake --workflow --preset site` — build and all CTest checks;
3. `python3 -m src.check_media check` — every R2 URL must be reachable;
4. upload `dist/` as the Pages artifact and deploy it.

Pages’ source must be **GitHub Actions**, not a `gh-pages` branch;
`actions/configure-pages` requests enablement on the first run. The workflow
needs no R2 credentials: media is already in the bucket, and the media check
uses the public URLs. The local `audit-media` inventory check stays local
because it needs the R2 API token. The build writes `.nojekyll`, so GitHub
serves the files verbatim.

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
.github/workflows/pages.yml  build, test, media check and Pages deploy
content/
  cards/
    <slug>/
      card.json       page metadata and ordered blocks
      summary.md      visible page lede
      description.md  meta description
      page.md         page prose (any number of prose files)
  data/
    *.json         canonical records (papers, talks, episodes, repos, videos, photos)
    episodes/      per-episode description Markdown
    repos/         per-repository description Markdown
    rescues/       per-rescue story Markdown
    species.json   species names and note pointers for grouped photos
    species/       per-species note Markdown
templates/         base shells, the hub board, card pages and partials
assets/            images, videos, documents, CSS and JS
  css/theme.css    palette, type, topbar and footer
  css/board.css    the hub board
  css/site.css     shared card pages
  css/pages/       optional per-page styles (podcast.css, engineering.css, cpp-standards.css, talks.css, ringing.css, rescues.css)
  icons/           platform, GitHub, C++, badge, nature, document and video marks; lanyard
  fonts/           Patrick Hand (OFL)
tests/             all content, output and media-policy validation
src/               Python build package
  __init__.py
  build.py         the renderer (Python standard library)
  site_schema.py   dataset registry and block-selection semantics
  media.py         R2 policy, URL rewriting and media inventory helpers
  fetch_repos.py   refreshes repo last-push dates from GitHub
  upload_media.py  uploads referenced media to R2
  check_media.py   HEAD check and bucket audit against dist/
deploy.json        public R2 base, hosted paths, bucket and endpoint
CMakeLists.txt     build entry point and validation targets
CMakePresets.json  configure/build/test/workflow presets
build/             CMake build tree (ignored by git)
dist/              generated output (ignored by git)
```

### Editing content

- **Card pages:** `content/cards/<slug>/card.json` holds the hub metadata
  (title, kicker, order, status, family, audio, board placement, optional
  `logo`/`logo_alt`, optional `mark`, optional `holding`) and the ordered
  `blocks` list. The directory name is the slug. `summary.md` supplies the
  visible lede; `description.md` supplies the `<meta name="description">`.
  Both files are required and must not be empty — there is no JSON fallback.
- **Per-page styling:** if `assets/css/pages/<slug>.css` exists, the build
  links it after `site.css` on that page only. Podcast uses
  `assets/css/pages/podcast.css` for its dirty background and floating chapter
  cards; Public GitHub uses `assets/css/pages/engineering.css` for its
  GitHub-logo header and pull-out repository cards; C++ & Standards uses
  `assets/css/pages/cpp-standards.css` for its C++ logo header and paper
  cards; Talks uses `assets/css/pages/talks.css` for its conference-badge
  header, embedded-video talk boxes and click-to-play thumbnails; Ringing uses
  `assets/css/pages/ringing.css` for its robin-perch header, silver ring mark
  and fanned species decks; Rescues uses `assets/css/pages/rescues.css` for
  the full-width stills | text | video rescue rows and vertical stills stack.
  Cards with `holding: true` link the shared
  `assets/css/pages/holding.css` instead; Learning Aid, About and Contact use
  it for their title-and-photo holding pages.
- **Pager:** card pages link to the adjacent cards in `order`. The sequence is
  circular: the first card's Previous points to the last card, and the last
  card's Next points back to the first.
- **Repository cards:** a full description is clamped to a preview with a
  `More…` toggle at the bottom of the card. Opening one expands it to its full
  height, changes the label to `Less…`, and closes any other open repository
  card. The height animates over 240 ms, and `prefers-reduced-motion` turns
  the animation off. The toggle is only shown when the description actually
  overflows; with JavaScript disabled the full text stays visible. The
  behaviour lives in `assets/js/site.js`.
- **Species decks:** a grouped photo block renders each species as a deck one
  photograph wide. The static base sits directly under the photo at the same
  width and carries the shared species note. Hover or keyboard focus fans the
  cards open to one side, like a wing; pressing a fanned card presents it, and
  pressing the presented card returns it to the fan while the deck stays open.
  Leaving hover closes the deck with the selected card moved to the front of
  the stack and the rest behind it in one clean stack. Fan angles come from a
  responsive `--fan-step` and the card index, so the closed and fanned states
  work before JavaScript runs; `site.js` owns the selected/presented state and
  the closed stack order.
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
- **Card summary and description:** `content/cards/<slug>/summary.md` is the
  visible lede under the page title, rendered as Markdown;
  `content/cards/<slug>/description.md` is flattened to plain text for the
  meta description. Both are required.
- **Structured data:** `content/data/*.json` — `papers`, `talks`, `episodes`,
  `repos`, `videos`, `photos`. Every record has a stable `id` and a
  `collections` list.
- **Episode descriptions:** `content/data/episodes/<slug>.md`, referenced by
  `"description_src"` in `episodes.json`.
- **Repository descriptions:** `content/data/repos/<name>.md`, referenced by
  `"description_src"` in `repos.json`. Each file holds the full Markdown body
  for the repository card; the first paragraph doubles as its one-line
  summary. Use `##` and below for subheadings, not `#`.
- **Species notes:** `content/data/species.json` records an `id`,
  `collections`, display `name` and `note_src`; the note itself lives in
  `content/data/species/<id>.md`. Photos reference the species id in a
  `species` field. The note is shared by every photo in the deck.
- **Rescue stories:** `content/data/rescues/<id>.md`, referenced by
  `"description_src"` in `videos.json`. Each rescue video has its own file for
  Ran's field story; a record can also carry `poster` and `photos`, which
  render as the vertical stills stack beside the video.
- **All prose lives in Markdown.** Any text a visitor reads belongs in a
  `.md` file from the start — page prose, card summaries and meta
  descriptions, episode and repository descriptions, species notes and future
  datasets — with JSON carrying only ids, routing fields and structured
  metadata. Do not put prose inline in JSON even when it
  is short; it makes the text easy to find and lets markup grow without a data
  migration.
- **Episode links:** `episodes.json` records carry `links` with `spotify`,
  `apple`, and `pocketcasts` URLs. Episode titles are not links; each card
  renders the three platform logos. A missing direct link falls back to the
  platform show page.
- **Talk videos and slides:** `talks.json` entries may carry `youtube` (a
  video ID or URL) and `slides` (a URL). The card renders a click-to-play
  YouTube thumbnail and icon links; slides live in the same box as the
  recording, and `url` is the fallback origin link.
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
| `{"type": "videos", "select": {"collection": "rescues"}, "layout": "rescue-rows"}` | full-width rescue rows |
| `{"type": "videos", "select": {"collection": "podcast-promos"}}` | video grid |
| `{"type": "photos", "select": {"collection": "ringing"}, "group_by": "species"}` | species decks |
| `{"type": "contact"}` | contact panel and form |

Collection selection ignores records whose `collections` contains `hidden`, so
soft-removing a record means adding `"hidden"`; remove it again to restore the
record. Explicit `ids` selection is not affected by `hidden`.

Photo blocks may add `"group_by": "<field>"` (used with `species` on Ringing)
to render one deck per value. The deck's static base carries the group name,
the photo count, the visit date(s) and the shared note; the photos themselves
have no per-frame caption. Video blocks may add `"layout": "rescue-rows"` to
render each rescue as a full-width stills | text | video row.

All listings render **latest first**: papers by `year`, talks and episodes by
`sort_date`, videos and photos by `date`, repositories by `pushed_at`. A `null`
date sorts to the end and keeps the source order. Explicit `ids` keep the order
given. Use `cmake --build --preset refresh-repos` (or the `refresh` workflow) to
refresh `pushed_at` from GitHub; the default build is offline. The build warns
for any visible entry without a sortable date; fill the `date` field when known
and the warning stops.

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

Rescue videos take their story from `description_src` (Markdown), select their
video frame with `poster`, and list five `photos` for the stills stack. The
poster is a sixth image, not one of those five; if it is absent the first
still is used. The stills render as a pile of cream-bordered prints: the
presented print is full size, the others peek out behind it. Pressing the
presented print advances to the next and wraps; pressing a peeking print
presents it. Every rescue currently has supplied photographs or frames
extracted from its clip.

### Placeholders

The site is intentionally a structural skeleton:

- All prose that is not yet written is lorem ipsum.
- Birding was removed from the hub and deferred to phase 2, if it happens;
  Ringing carries the current ringing photographs.
- The CV link is a placeholder until the real file arrives.
- Cards are colour-coded by family (`software`, `nature`, `neutral`).
- Software cards on the hub are portrait notes hanging from narrow lanyards,
  with a per-page artifact mark and the text grouped at the top, with space
  below. Public GitHub uses the GitHub logo; C++ & Standards uses the official
  C++ logo; Talks uses the conference badge. The repository rail keeps the
  small CMake build tag above the GitHub link. Nature cards remain landscape
  notes with their robin/perch treatment and carry a mark beside the text:
  bird ring (Ringing), podcast logo (Podcast), released bird (Rescues), open
  book (Birds of Israel Index), and bird-name cards (Learning Aid). Neutral
  cards keep the plain grommet.
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
