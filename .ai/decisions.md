# Portfolio — agreed decisions

Date: 2026-11-08

## Working agreement

Discuss, summarize, and agree **before** implementing. The structure is built
first; content and visual design follow. The site is static output but
data-driven, because it will be updated from time to time.

## Decisions

| Area | Decision |
|---|---|
| Language | English only. Hebrew is deferred; the cost of retrofitting is accepted. |
| Hosting | **Deferred.** No hosting assumption yet. `dist/` is plain static with relative URLs so it can move to GitHub Pages, a custom domain, or elsewhere later. |
| Build | **CMake** (same single build system as `../birds`) → `dist/`. `CMakeLists.txt` + `CMakePresets.json`; targets, tests and workflow presets. The default build is offline; repo-date refresh is an explicit target/workflow. Data/view split: prose in Markdown, structured content in JSON, view in templates. |
| Content model | `content/data/` holds canonical records, each with a stable `id` and a `collections` list. `content/cards/<slug>/card.json` holds page metadata and ordered `blocks`; page prose is sibling Markdown. Cards select data by collection or explicit ids — no duplicate membership index. `hidden` is a reserved collection for soft removal. |
| Record prose | Episode descriptions live in `content/data/episodes/<slug>.md` and are referenced by `description_src`; the inline `description` remains the fallback for other datasets. |
| Toolchain | `cmake` 3.25+ + Ninja + `python3` standard library + `pandoc` (3.9.0.2). No Node/npm, no third-party Python packages. |
| Visual design | Chosen: a 16:9 yin-yang poster. One dirty composite background with the sharp cutout; eleven title-only cards around it — nature scattered on the left, software on the right, About/Contact bottom. No separate page texture and no tape. Compact C05 lanyards sit above the software cards; compact N03 robin perches above the nature cards. The poster fits the viewport when it can and pans horizontally when it cannot; there is no vertical page scroll. Every card links to its page. |
| Tone | Playful / illustrated, not childish. Employer-facing. |
| Interaction | Cards lift on hover and focus; clicking opens a separate page per card. Keyboard and touch must work; honor `prefers-reduced-motion`. |
| Voice-over | English, added at the very end. Every card reserves an `audio` field and a transcript slot in the template from the start. |
| Videos | Local files embedded during development. Data model supports switching each entry to a YouTube embed later. |
| Contact | Animated notebook/power-line panel planned for the design phase. Direct email (public), public phone, and a form that composes a `mailto:` with the typed message. A true one-click send would require a third-party endpoint or a backend; deferred. |
| Gallery | Deferred. The data model can accept it later, with per-photo text/audio. |
| Book | Card exists as “Coming soon” until the PDF is shareable. |
| Learning aid | Card exists as “Under construction.” GitHub Pages cannot run the Python trainer; hosting/ports deferred. |
| CV | Placeholder until the real CV is ready. |
| Git | No LFS. Ignore `tags`, `*.swp`, `dist/`, Python caches. |

## Deferred items

1. Hosting and domain (and whether the repo becomes `regevran.github.io`).
2. YouTube channel and upload of the six video clips.
3. Book PDF readiness; where the PDF lives.
4. Learning-aid hosting strategy.
5. Real CV (email and phone are supplied).
6. Gallery as a first-class card.
7. Voice-over recording and transcripts.
8. Contact notebook/power-line interaction.

## Notes

- The repository was renamed from `regevran`/`personal_protfolio` to
  `personal_portfolio`.
- `assets/documents/main_page_concept.{jpeg,svg}` is a mood reference, not a
  spec. The SVG is a flattened Canva export (16,844 elements, no semantic
  labels, text outlined, 15 embedded rasters) and is not usable as separable
  production artwork. The cutout and ink background were extracted from it and
  combined into `assets/general/board-background.jpg` (1600 × 900,
  cutout 380 px wide).
- The page is a poster with exactly two layers: the single composite background
  and the data on top. The earlier paper-texture layer and taped photo frame
  were removed; the tape metaphor was rejected because it read as a to-do
  sticker. The cutout is baked into the background at 380 px wide and the whole
  yin-yang group is shifted 120 px right, so the owl's eye stays on the
  yin-yang's light eye at (927.5, 285); the extra left wall gives nature more
  room.
- The eleven cards are title-only (kicker + title); descriptions, statuses and
  content live in the card pages. The poster is not a grid: nature cards are
  scattered on the left in a zigzag, software cards vary their x position on the
  right, and About and Contact stay flat and bottom-aligned. Card rotations run
  to roughly ±6°, with hanging cards pivoting from their grommet. Robins are
  rotated and mirrored per card and sit on the perch branch rather than above
  it.
- The poster scales to the viewport height and fits when the resulting width
  fits; otherwise the board pans horizontally on both desktop and mobile. The
  nav items are zone shortcuts (Nature left, Work right, About/Contact centre).
- The ten card anchors were studied in `design/hooks.html`. Selected: **C05
  lanyard** (computer) and **N03 robin perch** (nature). On the board, compact
  versions sit above every card in each family: the lanyard V points down
  (apex at the badge clip) with the straps running up as if from the neck, and
  the perch is a small branch with the robin above the card. The other studies
  remain on the sheet for reference.
- The robin uses the book's transparent PNG
  (`assets/general/closing_on_birds_robin.png`, 359 × 356 RGBA) on the board:
  56 × 72 px above every nature card and 104 × 132 px in the enlarged N03
  study, with `object-fit: contain` and bottom alignment so the bird sits on the
  perch. The interim raster robin with the podcast microphone is no longer
  used.
- The wooden Ran Regev, Software, and Nature signs were removed: they read as
  another anchor and added mass. The title bar and tagline note carry the name
  and pitch. The tagline uses the kicker's mono uppercase style, is sized to
  its longest line with a small margin, sits left of centre above the yin-yang
  curve with the same 2% spacing from the top that About/Contact have from the
  bottom, and carries a full gold border.
- The title bar is fixed at the top: name, email, phone, and a provisional
  About / Work / Nature / Contact navigation. The nav targets are zone
  shortcuts for now; real page routes arrive with the card pages.
- The C05 lanyard straps use the software blue and the N03 perch uses the nature
  green, matching the card family rules. The perch's earlier ochre/green/ink
  three-colour mix was collapsed to the one green. The straps are thinner and
  the V opening a little wider.
- Every board card links to its page. The card pages now use the board's
  visual language: a cream note on the sand field, Patrick Hand titles, mono
  kickers, family-coloured top edges, ledger-style lists, framed media, and a
  notebook-style contact panel. The contact panel is visual only for now.
- The topbar and footer are shared by the hub and the card pages and stay
  fixed; the content scrolls between them. The footer sentence lives in
  `site.json` (`footer`), so it is data rather than template copy. The palette,
  type, topbar and footer live in `assets/css/theme.css`; `board.css` and
  `site.css` hold only their page-specific rules.
- The book palette is the design base; Patrick Hand (OFL) is bundled for
  handwritten labels.
- The rejected `bird-circuit` motif was removed from the design assets.
- Video files are excluded from git (`*.mp4`). A missing local video is a
  **hard validation error**, never a warning or placeholder. Once an entry has
  a `youtube` value, the local file is no longer required and the build uses
  the iframe. A clean checkout cannot build until the clips are uploaded and
  the data is switched.
- Real email and phone live in `content/data/site.json` (supplied 2026-11-08).
- All listings render latest-first. Undated entries go last and keep their
  source order. Photo and rescue-video capture dates are not embedded in the
  files, so those `date` fields are null until the user supplies them.
- Repositories sort by `pushed_at`, refreshed from the GitHub API by
  `fetch_repos.py` only when the explicit refresh target/workflow runs. The
  value is cached in `repos.json` when the network is unavailable.
- Missing dates are non-fatal: the build prints a warning per entry with the
  file, index, title, and field to edit. Content tests only require the field to
  exist (null allowed).
- The build is CMake-only. `cmake --workflow --preset site` configures, builds
  and tests; `cmake --workflow --preset refresh` refreshes GitHub dates first.
  The default build is offline, like the birds data pipeline. `render.sh` was
  removed. `cmake --install build` stages a deploy copy; the host/upload step
  remains deferred.
- Cards carry a `family` (`software`, `nature`, `neutral`) that drives the
  board's top rule and colour, the anchor (`lanyard`, `perch`, `none`), and the
  card page's top edge.
- The `pelacanus_onocotalus_3.jpeg` filename typo was corrected by the user;
  the current file is `pelecanus_onocrotalus_3.jpeg`.
- The approved hub placement is stored per card in `content/cards/<slug>/card.json`
  under `board` (`x`, `y` or `bottom`, `tilt`, `anchor`, `robin` for the perch,
  and optional nav `id`). Validation ties the anchor to the family. The values
  mirror `design/direction-a.html`.
- The board is the real hub as of 2026-11-09: `templates/base-board.html` +
  `templates/index.html`, `assets/css/board.css`, `assets/js/board.js`, and the
  `board-card`/`perch`/`lanyard` partials. Every board card links to its page.
  Card pages use the shared board language through `theme.css` and `site.css`.
- The **Podcast page** got its own treatment on 2026-11-10: dirty ink
  background (`assets/general/dirty-background.jpg`), no full-page sheet, a
  straight header note with the full circular podcast logo
  (`assets/general/closing_on_birds_circle.png`), and each episode as a
  floating card matching the header width, with the small robin/mic logo and
  long, uncapped text lines. The cards alternate ±4° and overlap by `-1rem`;
  the bottom padding keeps the text and platform links clear. Mobile uses ±3°
  and `-0.5rem`. Hovering or focusing a card straightens it and brings it
  forward; static text rectangles get a soft gold glow. The promo videos are
  straight and sit at the bottom. Episode titles are not links; the small
  robin/mic logo heads a narrow right-hand rail with the Spotify, Apple
  Podcasts and Pocket Casts logo links stacked tightly below it. The title and
  date share the first line; the description follows at full width. The cards
  rotate ±3°, sit `-0.1rem` apart, use `2.2rem` bottom padding, and have an
  `11.5rem` minimum height so the rail always fits; mobile uses 2.5°, `1.2rem`,
  and `9.2rem`. The rail is absolutely positioned at the top-right, its top
  aligned with the title row, with a clear gap before the icons. The mic is a
  CSS background image rather than an `<img>`, because Chromium draws an
  opaque white box around this transparent PNG when it is an image element in
  the rotated card. The links are backed by `episodes.json` `links` data. The
  rules live in
  `assets/css/pages/podcast.css`. Per-page
  stylesheets are auto-discovered from `assets/css/pages/<slug>.css`; pages
  without one get only the shared styles. The rest of the card pages keep the
  shared first-pass design for now.
- The content model was revised on 2026-11-09: `content/data/cards.json` was
  removed; each card is now a directory with `card.json` + prose. Datasets
  gained stable ids and collection tags. The podcast card's promo-video block
  now sits last, at the bottom of the page, by order in the `blocks` array.
- **Birding & Ringing was split** into two cards on 2026-11-09. `birding` is a
  placeholder for photographs and field stories (order 4, status
  `placeholder`, prose only); `ringing` owns the existing ringing photographs
  (order 5, `"collections": ["ringing"]`). The board shows both with the robin
  perch.
