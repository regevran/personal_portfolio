# Ran Regev — personal portfolio

A static, data-driven portfolio. Content lives in `content/` and `assets/`;
CMake builds the site into `dist/`. The generated output is plain static HTML
with relative URLs, so it can be inspected locally or moved to any static host
later.

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
  (`design/assets/textures/board-background.jpg`) carries a sharp Ran + owl
  cutout with the owl's eye on the yin-yang eye. Ten title-only cards surround
  it: nature on the left, software on the right, and About and Contact as two
  flat, bottom-aligned cards. The yin-yang group sits right of centre to give
  nature more room. Compact C05 lanyards sit above the software cards; compact
  N03 robin perches above the nature cards. The robins are 56 × 72 px
  placeholders until the transparent PNG arrives. The board fits the viewport
  when it can and pans horizontally when it cannot; there is no vertical page
  scroll. A fixed title bar carries the name, email, phone, and provisional
  About / Work / Nature / Contact navigation.
- `hooks.html` — ten anchor studies: five nature anchors (rope & nail, twig
  hook, robin perch, vine loop, wooden peg) and five computer anchors (cable
  loop, binder ring, pegboard hook, monitor arm, lanyard). N03 and C05 are
  marked as the selected pair.

The previews use the book palette, the motif library in `design/assets/motifs/`,
and the single composite background. They are not part of the site build and
are not linked from the site; they exist to settle the visual language before
integrating it.

Run the tests alone:

```sh
ctest --preset default
```

(`output-validation` requires a built `dist/`.)

## Layout

```text
content/
  cards/        prose for each card/page (Markdown)
  data/         the site map and structured content (JSON)
templates/      page skeletons (base, index, card, partials)
assets/         images, videos, documents, CSS and JS
tests/          all content and output validation
build.py        the renderer (Python standard library)
fetch_repos.py  refreshes repo last-push dates from GitHub
CMakeLists.txt  build entry point and validation targets
CMakePresets.json  configure/build/test/workflow presets
build/          CMake build tree (ignored by git)
dist/           generated output (ignored by git)
```

### Editing content

- **Card list:** `content/data/cards.json` controls the hub order, titles,
  summaries, statuses, colour family, and the optional voice-over field.
- **Card prose:** `content/cards/<slug>.md`. Put `<!-- include:NAME -->` on its
  own line to inject a structured block (see below).
- **Structured data:** `content/data/*.json` — `papers`, `talks`, `episodes`,
  `repos`, `videos`, `photos`.
- **Identity and contact:** `content/data/site.json`.

All listings render **latest first**: papers by `year`, talks and episodes by
`sort_date`, videos and photos by `date`, repositories by `pushed_at`. A `null`
date sorts to the end and keeps the source order. `fetch_repos.py` refreshes
`pushed_at` from the GitHub API on every render (unless `--offline`), so the
repository order reflects your latest pushes. Photos and rescue videos
currently have no embedded capture dates; fill their `date` fields when known
and the warnings will stop.

Available includes:

| Marker | Renders |
|---|---|
| `<!-- include:papers -->` | WG21 papers list |
| `<!-- include:talks -->` | talks list |
| `<!-- include:episodes -->` | podcast episodes |
| `<!-- include:repos -->` | repositories |
| `<!-- include:videos:rescues -->` | rescue videos |
| `<!-- include:videos:podcast-promos -->` | podcast promo clips |
| `<!-- include:photos -->` | ringing photographs |
| `<!-- include:contact -->` | contact panel and form |

### Videos

Videos are embedded from local files for now. Each video entry in
`content/data/videos.json` may instead carry a `"youtube"` field (a video ID or
embed URL); the renderer then emits a YouTube iframe and ignores `src`. That is
the intended switch once the clips are uploaded.

Video files are not committed (`*.mp4` is ignored). A missing local video is a
**hard validation error**, not a warning or placeholder: the working copy needs
the files until each entry has a `youtube` value. Once `youtube` is set, the
local-file check is skipped and the iframe is used, so a clean checkout builds
again.

### Placeholders

The site is intentionally a structural skeleton:

- All prose that is not yet written is lorem ipsum.
- The CV link and the book PDF are placeholders until the real files arrive.
- Cards are colour-coded by family (`software`, `nature`, `neutral`) as a
  structural aid, not a final design decision.
- The visual design (metaphor, typography, palette) is deliberately neutral and
  will be decided in a separate design session.

### Tests

`tests/validate.py` holds the validation logic. `tests/test_content.py` checks
the source tree (card schema, datasets, referenced files, include names) and
`tests/test_output.py` checks the built `dist/` (pages exist, internal links
resolve, no unreplaced template tokens). The `site` workflow builds before
running `ctest`, so output validation always sees a fresh `dist/`.
