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
| Build | `./render.sh` → `dist/`. Data/view split: prose in Markdown, structured content in JSON, view in templates. |
| Toolchain | `bash` + `python3` standard library + `pandoc` (3.9.0.2). No Node/npm, no third-party Python packages. |
| Visual design | Chosen: the yin-yang field board — one dirty composite background and the data on top. No separate page texture and no tape. Compact C05 lanyards hang above every software card; compact N03 robin perches hang above every nature card. The robins are 56 × 72 px placeholders until a transparent PNG arrives. The wooden name/Software/Nature signs were removed. Cards remain unlinked. |
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
2. Visual design session: metaphor, layout, typography, palette, artwork export
   from Canva.
3. YouTube channel and upload of the six video clips.
4. Book PDF readiness; where the PDF lives.
5. Learning-aid hosting strategy.
6. Real CV (email and phone are supplied).
7. Gallery as a first-class card.
8. Voice-over recording and transcripts.

## Notes

- The repository was renamed from `regevran`/`personal_protfolio` to
  `personal_portfolio`.
- `assets/documents/main_page_concept.{jpeg,svg}` is a mood reference, not a
  spec. The SVG is a flattened Canva export (16,844 elements, no semantic
  labels, text outlined, 15 embedded rasters) and is not usable as separable
  production artwork. The cutout and ink background were extracted from it and
  combined into `design/assets/textures/field-background.jpg`.
- The page uses exactly two layers: the single composite background and the
  data on top. The earlier paper-texture layer and taped photo frame were
  removed; the tape metaphor was rejected because it read as a to-do sticker.
  The cutout is baked into the background at 440 px wide, so the owl's eye stays
  on the yin-yang's light eye at (646, 228).
- The ten card anchors were studied in `design/hooks.html`. Selected: **C05
  lanyard** (computer) and **N03 robin perch** (nature). On the board, compact
  versions sit above every card in each family: the lanyard V points down
  (apex at the badge clip) with the straps running up as if from the neck, and
  the perch is a small branch with the robin above the card. The other studies
  remain on the sheet for reference.
- The robin is a **placeholder** on the board (56 × 72 px dashed box per nature
  card; the enlarged study uses 104 × 132 px) until the book's creator supplies
  a transparent PNG. A transparent PNG is sufficient; the image will replace
  the box with `object-fit: contain`. The interim raster robin with the podcast
  microphone is no longer used.
- The wooden Ran Regev, Software, and Nature signs were removed from the hero:
  they read as another anchor and added mass. The topbar wordmark carries the
  name.
- The title bar is sticky at the top: name, email, phone, and a provisional
  About / Work / Nature / Contact navigation. The nav targets are anchors to
  the cards for now; real page routes arrive with the card pages.
- The C05 lanyard straps use the software blue and the N03 perch uses the nature
  green, matching the card family rules. The perch's earlier ochre/green/ink
  three-colour mix was collapsed to the one green. The straps are thinner and
  the V opening a little wider.
- Cards are still not linked to their pages; the board only mounts the chosen
  anchors.
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
  `fetch_repos.py` on every render (unless `--offline`). The value is cached in
  `repos.json` when the network is unavailable.
- Missing dates are non-fatal: `render.sh` prints a warning per entry with the
  file, index, title, and field to edit. Content tests only require the field to
  exist (null allowed).
- Cards carry a provisional `family` (`software`, `nature`, `neutral`) used only
  for colour-coding the structure preview. It is not a visual-design decision.
- The `pelacanus_onocotalus_3.jpeg` filename typo was corrected by the user;
  the current file is `pelecanus_onocrotalus_3.jpeg`.
