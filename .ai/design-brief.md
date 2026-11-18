# Design phase — the yin-yang field board

Date: 2026-11-08
Status: 16:9 poster layout with title-only cards; anchors chosen (C05 lanyard +
N03 robin perch); robin transparent PNG integrated; the board is now the site
hub, with each card linking to its page. Podcast has floating chapter cards;
Public GitHub, C++ & Standards and Talks have artifact-led software treatments;
Ringing has the ringer's field sheet with fanned species decks. The other
card pages keep the shared first-pass styling; contact interaction remains.

## Goal

Settle the visual language of the board, then carry it into the card pages. The
board is a title-only index; every card links to its page, where the content
lives.

## Direction of travel

The first pass was too clean and grid-like. The language is now a **dirty field
notebook collage**: one dirty ink image as the whole page, with the data placed
on top of it. Nothing else: no separate page texture, no taped photo frame, no
strips of tape. The ten sections are notes on the board, not a grid.

Direction A (the field board) is the only direction. Directions B and C were
dropped and their files deleted.

## Constraints

- The board was the first surface; card pages now reuse its palette and type.
- Static HTML/CSS. No runtime network requests.
- English.
- Book palette and book typography as the base.
- One bundled OFL font for handwritten labels: Patrick Hand. Software uses
  the formal serif instead.
- Motion stays light: hover lift and small shifts, with a reduced-motion
  fallback.

## Palette — sampled from the book cover

| Token | Hex | Use |
|---|---|---|
| Sand | `#EFDFC0` | page field |
| Cream | `#FFF9EC` | paper notes |
| Ink | `#2F2714` | text, line art, dark halves |
| Ochre | `#7A4E12` | rules, links, signs |
| Gold | `#ECB652` | the book's cover circle, highlights |
| Wood | `#C98B45` / `#E7C487` | wooden signs |
| Software | `#3E6B89` | muted teal from the cover strip |
| Nature | `#9A9A5B` | muted olive from the cover strip |

## Typography

- Display, kickers, metadata: `Noto Sans Mono`.
- Prose: `Noto Serif`.
- Handwritten names, nature/neutral card titles, sign labels: Patrick Hand
  (bundled, OFL). Software titles use the formal serif (Noto Serif / Georgia).
- Fallbacks: `ui-monospace`, Georgia, cursive.

## Source artwork

The Canva SVG is a flattened export and is not usable as separable artwork, but
it contains the exact pieces we need. Extracted from it:

- `design/assets/img/ran-otus.png` — the cutout of Ran and the scops owl, with
  the colour image combined with its alpha mask.
- `design/assets/textures/ink-yinyang.jpg` — the dirty ink yin-yang background.
- `assets/general/board-background.jpg` — **the 1600 × 900 poster
  background**: the ink image scaled to 16:9 with the sharp cutout baked in at
  380 px wide.
- `design/assets/textures/field-background.jpg` — the earlier 1280 × 720
  composite for the scrolling board; retained, no longer used by the poster.
- `design/assets/textures/paper-dirty.jpg` — retained from the first pass but no
  longer used; the separate paper layer was removed.

The book cover contributed:

- `assets/general/closing_on_birds_robin.png` — the transparent European robin
  used on the board and the N03 study (359 × 356 RGBA); copied to
  `design/assets/img/closing_on_birds_robin.png` so the preview is
  self-contained.
- `design/assets/img/robin.png` — the European robin, cropped from the cover's
  podcast mark. It is no longer used on the board because the podcast microphone
  is baked in under the bird's feet; the creator is supplying a transparent PNG
  instead.
- `design/assets/img/robin-logo.png` — the full robin + microphone + Hebrew
  podcast mark; reference only.

**Eye alignment:** in `board-background.jpg` the cutout is 380 px wide and
placed at (647, 118); the owl's eye lands at (927.5, 285), on the yin-yang's
light eye (the ink image is 1600 × 900, shifted right by 120 px). Because the
cutout is baked into the bitmap, the alignment cannot drift.

The earlier `bird-circuit` vector was rejected and removed.

## Direction A — Field Board

The main page is a **16:9 poster**, not a scrolling document:

1. `board-background.jpg` — the dirty ink yin-yang with the sharp Ran + owl
   cutout baked in at 380 px wide.
2. The data on top — a tagline note and ten title-only cards placed around
   the portrait.

The spatial grammar follows the original jpeg but is deliberately **not a
grid**: **nature is scattered on the left** (Ringing, Rescues, Podcast,
Birds of Israel Index, Learning Aid) in a zigzag, **software is on the right**
(Public GitHub, C++ & Standards, Talks) with varied x positions rather
than one column, and the two neutral cards (About, Contact) stay flat and
bottom-aligned under the portrait. Hanging cards rotate up to roughly ±6° and
pivot from their grommet; the rest of the board does not move. The whole
yin-yang group is shifted 120 px right so nature gets more of the wall and
software gets less. The tagline is a compact note in the kicker's mono
uppercase style, sized to its longest line, placed left of centre above the
yin-yang curve and outlined by a full gold border; its 2% top spacing matches
the bottom row's 2% bottom spacing. Cards are enlarged to use the free space.
The card
labels are kicker + title only; descriptions, statuses, and all other content
live in the card pages. This placement is encoded per card in
`content/cards/<slug>/card.json` under `board`; the hub renderer reads it when
the board is integrated.

The board scales with the viewport height. When the resulting width fits, the
whole poster is visible with no scroll; when it does not fit (narrow laptop,
tablet, phone), the same board pans **horizontally** — never vertically. On
desktop the wheel is mapped to horizontal pan; on touch it is native swipe.
The nav items are zone shortcuts: Nature pans left, Work pans right, About and
Contact pan to the centre.

The title bar is fixed at the top and carries the name, email, phone, and the
About / Work / Nature / Contact navigation. The nav targets are anchors to the
corresponding cards for now; real page routes arrive with the card pages.

The cards carry a family-coloured top rule: software `#3E6B89`, nature
`#5F6232`, neutral ochre. The card surfaces stay cream so the text remains
readable over the dark ink.

The anchor colour follows the card: the C05 lanyard straps are software blue,
matching the software card rule; the N03 branch, twine, and leaf are nature
green, matching the nature card rule. The earlier three-colour perch (ochre
branch, olive leaf, ink twine) was collapsed into that single green.

The wooden Ran Regev, Software, and Nature signs were removed: they read as
another anchor and added mass. The title bar and the tagline carry the name and
pitch.

## Anchors

The tape was rejected: it read as a to-do sticker rather than a record of work.
Instead the cards hang from anchors. Ten studies live in
`design/hooks.html`, in two groups:

- **Nature:** N01 rope & nail, N02 twig hook, N03 robin perch, N04 vine loop,
  N05 wooden peg.
- **Computer:** C01 cable loop, C02 binder ring, C03 pegboard hook, C04 monitor
  arm (VESA plate), C05 lanyard.

**Selected:** N03 robin perch for nature and C05 lanyard for computer.

On the board, the C05 V is compact and points down (apex at the badge clip),
with the straps running up as if from the neck; there is no nail. A small
version sits above every software card. Each nature card carries a compact
robin perch: a branch, twine, and a robin above the card. The perch is repeated
above Ringing, Rescues, Podcast, Birds of Israel Index, and Learning Aid.

The robin uses the book's transparent PNG
(`assets/general/closing_on_birds_robin.png`, 359 × 356 RGBA). It is rendered
at 56 × 72 px on the board and 104 × 132 px in the enlarged N03 study with
`object-fit: contain`; the branch overlaps the bottom of the image and the bird
is nudged onto it. Each board robin gets its own rotation and some are
mirrored, so the perch does not look copied. The interim raster robin with the
podcast microphone is no longer used.

## Files

- `design/index.html` — chooser: field board + anchor studies.
- `design/direction-a.html` — the one-background board with the selected
  anchors.
- `design/hooks.html` — the ten anchor studies, with N03 and C05 marked selected.
- `design/assets/design.css`.
- `design/assets/img/`, `design/assets/textures/`, `design/assets/fonts/`.

## Card pages

The card page is the **opened note** from the board:

- The sand field is the page; one large cream sheet carries the content.
- The topbar and footer are shared with the hub and stay fixed; the sheet
  scrolls between them. The footer sentence lives in `site.json`.
- The header uses the board's kicker/title pairing: mono uppercase kicker,
  Patrick Hand title (formal serif on software pages), serif summary. The
  sheet's top edge carries the family colour (software blue, nature olive,
  neutral ochre); the status badge is a small dashed stamp.
- Prose is serif at a readable measure. Papers, talks, episodes and repos
  render as ledger rows with meta on the left. Videos and photos sit in framed
  prints; photo frames carry a slight rotation. The contact panel is a
  notebook-style pair of notes, with underlined fields.
- Palette, type, topbar and footer are shared in `assets/css/theme.css`.
  `assets/css/site.css` holds the card-page rules only.

The first target was Podcast because it combines a video grid, prose and an
episode list. Public GitHub followed for the repository list and the software
variant. Ringing, C++ & Standards, Contact and About were checked as the other
block types.

### Podcast page

Podcast keeps its page-specific details in `assets/css/pages/podcast.css`,
loaded only for that page, but follows the shared card-page rules:

- The page background is the dirty ink texture
  (`assets/general/dirty-background.jpg`), fixed on desktop. The page is the
  standard cream card sheet, like Ringing and Rescues.
- The header, summary and `page.md` live inside that sheet. The circular logo
  (`assets/general/closing_on_birds_circle.png`) floats small at the header's
  top right, beside the title, small enough not to make the header taller than
  its text.
- `page.md` is ordinary prose inside the sheet; there are no separate intro
  notes.
- The header and the promo-video cards are straight. The videos sit at the
  bottom of the sheet, after the episode list.
- Each episode is a compact cream card matching the header width, with a
  nature-green top edge. The title and date share the first line (date after
  the title); the description follows and uses the full width up to a narrow
  right-hand rail. The cards alternate `rotate(3deg)` / `rotate(-3deg)`, sit
  `-0.1rem` apart, use `2.2rem` bottom padding, and have an `11.5rem` minimum
  height so the rail always fits; mobile uses 2.5°, `1.2rem`, and `9.2rem`.
- Episode titles are not links. The small robin/mic logo heads an absolutely
  positioned right-hand rail whose top aligns with the title row; the Spotify,
  Apple Podcasts, and Pocket Casts logo links stack beneath it with a small
  clear gap. The mic is a CSS background image, not an `<img>`, because
  Chromium draws an opaque box around the transparent PNG in this context.
  Per-episode URLs live in `links` in `episodes.json`; missing direct links
  fall back to the show page.
- Tilted episode cards straighten and lift on hover or focus; static text uses
  the standard card styling.

### Public GitHub page

Public GitHub (`engineering`) shares the dirty field and cream notes with
Podcast but reads as software. Its rules live in
`assets/css/pages/engineering.css`.

- The background is the same dirty ink texture, fixed on desktop. The page is
  the standard cream card sheet with the software-blue top edge. The title
  uses the formal serif, not Patrick Hand.
- The header lives inside that sheet. The official **GitHub logo**
  (`assets/icons/github.svg`) sits at its top left and the real GitHub QR code
  in a white quiet-zone frame at its top right. The kicker, formal-serif title
  and summary sit under them. The old portrait note and lanyard are gone.
  The QR (`assets/general/github-qr.svg`) was generated for
  `https://github.com/regevran` and still scans to the profile.
- `page.md` is ordinary prose inside the sheet; there are no separate intro
  notes.
- Repositories are straight cream cards with a software-blue top edge. The
  repository name sits left and the last-push date is centred on the first
  line; the description follows. An absolutely positioned right-hand rail
  mirrors the robin rail on Podcast cards: a small two-line CMake build tag
  (`[ 20%] Building CXX object` / `[100%] Linking CXX executable`) sits above
  the GitHub mark
  (`assets/icons/github.svg`) in a cream circle, which links to the
  repository in a new tab; the conference badge has moved to Talks. The
  repository name keeps its own link. The body comes from
  `content/data/repos/<name>.md` and is styled for
  long-form Markdown: the first paragraph is the scan line, followed by small
  serif subheadings, lists, blue underlined links and tinted inline code. The
  measure is capped at `72ch` so paragraphs stay readable inside the wide
  card. The card starts as a clamped preview (about four lines, with a soft
  fade) and a small `More…` pill at the bottom left. It expands the card down
  to its full height over 240 ms (the height transition is disabled under
  `prefers-reduced-motion`), turns into `Less…`, and opening another
  repository closes the previous one. Short descriptions get no toggle.
  Instead of
  Podcast's tilt-and-straighten, hovering or focusing a card pulls it out and
  enlarges it slightly (`translateY(-6px) scale(1.02)`) with a blue glow.
  There is no rotation. Mobile stacks the date under the name.
- `prefers-reduced-motion` removes the pull-out transform; static text uses
  the standard card styling.

### C++ & Standards page

C++ & Standards (`cpp-standards`) shares the dirty field, cream notes and
straight pull-out cards with Public GitHub, with the official **C++ logo**
instead of the GitHub logo. Its rules live in
`assets/css/pages/cpp-standards.css`.

- The page is the standard cream sheet with the software-blue top edge. The
  header lives inside it: the unaltered official C++ logo
  (`assets/icons/cpp-logo.svg`) at the top left, then the full designation
  `ISO/IEC JTC1/SC22/WG21`, the formal-serif title `C++ & Standards`, and the
  summary. The logo is the artifact; the full designation supplies the
  standards context. There is no ISO logo. The old portrait note and lanyard
  are gone.
- `page.md` is ordinary prose inside the sheet; there are no separate intro
  notes.
- Papers are straight cream cards with a software-blue top edge. The title
  sits left, the paper number (`P3817R0-R1`, etc.) is centred on the first
  line, and the role/year line sits under the title. The description follows.
  A right-hand rail holds the C++ logo above a document link
  (`assets/icons/paper.svg`), both in the same rhythm as the GitHub page's
  rail. The title and the document icon both link to `wg21.link` in a new
  tab.
- Hovering or focusing a card pulls it out and enlarges it
  (`translateY(-6px) scale(1.02)`) with a blue glow. There is no rotation.
  Mobile stacks the paper number and role/year under the title.
- Paper descriptions can use `description_src` Markdown. The current cards use
  the inline one-liners.

### Talks page

Talks (`talks`) shares the dirty field and cream notes with Public GitHub and
C++ & Standards; its rules live in `assets/css/pages/talks.css`.

- The page is the standard cream sheet with the software-blue top edge. The
  header lives inside it: the full conference badge
  (`assets/icons/conference-badge.svg`) at the top left — badge card, QR, name
  lines and its own lanyard — then the `Stage` kicker, the formal-serif title
  `Talks` and the summary. The old portrait note and note lanyard are gone;
  the badge keeps its own lanyard.
- `page.md` is ordinary prose inside the sheet; there are no separate intro
  notes.
- Talks are straight cream video boxes with a software-blue top edge. Each
  box carries the badge name-tag stamp at the top left, then the uppercase
  date, formal-serif title and description in the copy column, with a 16:9
  video on the right. Under the copy is a small icon row: a YouTube mark for
  the watch link and, when the talk has a deck, a document mark for the
  slides. The ScyllaDB slides live in the same box as the recording; the
  P3817 slides point at `https://regevran.github.io/p3817-presentatin/`. The
  video is a click-to-play thumbnail: clicking it swaps in the YouTube player
  over HTTP(S); from `file://` it opens the watch page because YouTube refuses
  a player without an HTTP referrer. The `youtube` field in `talks.json`
  supplies the video id; `url` stays the origin link (the watch page for
  direct videos, the talk page for the ScyllaDB recording) and is used only
  as a fallback icon when a talk has neither video nor slides. The Core C++
  2026 box has no recording, so its copy spans the full box and the slides
  icon sits under it. Hovering or focusing a card lifts it
  (`translateY(-4px)`) with a blue glow. Mobile stacks the copy, the video and
  then the icon row.
- `prefers-reduced-motion` removes the pull-out transform; static text uses
  the standard card styling.

### Ringing page

Ringing (`ringing`) is the first nature page with its own treatment. It shares
Podcast's dirty field and cream notes and stays in the board's nature half.

- Each row contains two species decks. The two-column grid gives the page the
  same width as the other card pages and aligns `page.md` with the decks; a
  trailing odd deck centers itself under the row.
- The background is the dirty ink texture, fixed on desktop. The page itself is
  the standard cream card sheet, like Rescues, not a loose collection of notes.
- The header lives inside that sheet. The back link stays at the top, then the
  header. A narrow, tall silver leg ring (`assets/icons/bird-ring.svg`), open
  at its seam like a real ringing band, sits at the header's top right as the
  page artifact. The `Field work` kicker, the Patrick Hand title `Ringing` and
  the summary sit below.
- The robin perch is temporarily removed from the page header. The page robins
  will return only when every nature page gets one; engineering pages need a
  matching badge at the same time. This is deferred to the end.
- `page.md` is ordinary prose inside the same sheet, matching the Rescues
  format; there are no separate intro-note cards.
- Each species is a **deck** one grid column wide. A deck in the left column
  fans left; the right column fans right, and the centered last deck fans
  right. The static cream base sits
  directly under the closed photo at the same width and carries the species
  name, photo count, visit date and one shared note — there is no per-photo
  caption. The photograph is the dominant element; the note is a narrow
  column beneath it.
- Decks in the same row share the row's height: the shorter cream base
  stretches until it meets the taller one, so the next row starts on a clean
  line.
- Above the base the photos sit as a closed hand of cards: the selected photo
  is moved to the front of the deck and faces the viewer perfectly upright,
  with the other photos stacked behind it in a clean single-sided stack.
  Selecting another card moves it to the front. The cards tuck behind the
  base's top edge, so the base reads as the lip of a card holder without
  drawing any mechanism.
- Hovering or keyboard focus fans the deck open to one side, like a bird's
  wing opened to one side rather than symmetrically. The cards share a bottom
  pivot and swing away from the page center: a left-column deck fans left, a
  right-column deck fans right, and the centered last deck fans right. The fan
  may extend past the base. Losing hover closes it again, with the selected
  card on top.
  Pressing a fanned card presents it (replacing the previous facing card);
  pressing the presented card advances to the next photo and wraps at the end,
  matching the Rescues stills. A one-photo deck is a one-card deck, and a
  two-photo deck opens into a shallow one-way fan. Touch opens on tap and
  closes on a tap outside.
- Header, back link and pager use the standard card styling inside the sheet.
  `prefers-reduced-motion` keeps the deck states but removes the transitions.
- The photos block groups by `"species"`. Each photo carries a species id;
  `content/data/species.json` holds the name and `note_src`, and the note
  itself lives in `content/data/species/<id>.md`. This is the first page to
  follow the rule that all prose, including group notes, lives in Markdown
  from the start rather than inline JSON.

### Rescues page

Rescues keeps the standard card page and the nature palette; its additions
live in `assets/css/pages/rescues.css`.

- Each rescue is one full-width row, a cream note divided into three equal
  columns: **stills | text | video**, left to right. The text column carries the rescue
  icon, title, species and story; the middle column is a vertical stills
  stack; the video fills the right column.
- The rescue icon (`assets/icons/rescue.svg`) is used in the page header as the
  page artifact and beside every row's title.
- Each rescue story is Markdown in `content/data/rescues/<id>.md`, referenced
  by `"description_src"` in `videos.json`. The files start empty until Ran
  writes the field story; an empty file renders nothing.
- Videos carry a `poster` path in `videos.json`; it is deliberately a sixth
  image, not one of the five presented stills. If `poster` is absent the first
  still is used as a fallback.
- Every rescue has six images: five in the stills stack and one poster. The
  pelican and kestrel use their supplied photographs plus extracted frames;
  the Great Egret, White Stork, Pygmy Cormorant and Black Kite use six frames
  extracted from their clips.
- The stills are a pile of cream-bordered photo prints, not a strip of slices.
  The presented print is full size; the others sit behind it, offset down and
  right so only their cream edges show. There is no hover opening and no
  rotation. Pressing the presented print advances to the next, wrapping at the
  end; pressing a peeking print presents that one. Keys work because the
  prints are real buttons, and `prefers-reduced-motion` removes the transform
  transition.
- On mobile the three columns stack as stills, text, video; the video keeps its
  aspect and the stills stack keeps a fixed height.

### Software badges on the hub

The hub's three software notes use the same portrait container: narrower and
taller than the nature notes, with a narrow C05 lanyard whose clip meets the
blue top edge, no punched-hole circle, and a per-page artifact mark above the
kicker and title. Public GitHub uses the GitHub logo
(`assets/icons/github.svg`); C++ & Standards uses the official C++ logo
(`assets/icons/cpp-logo.svg`) and the full `ISO/IEC JTC1/SC22/WG21` kicker;
Talks uses the conference-badge name tag
(`assets/icons/conference-badge-mark.svg`). Nature notes keep the landscape
note and their robin/perch treatment, and each one now carries its own mark
beside the kicker and title: the bird ring for Ringing, the podcast logo for
Podcast, a released bird for Rescues, an open book for Birds of Israel Index,
and bird-name cards for Learning Aid. Neutral notes stay marked only by the grommet.

### Software page artifacts

Agreed 2026-11-11. The software pages share one container: the portrait cream
note, narrow lanyard, software-blue edge, formal serif title and mono kicker
hanging on the board. The conference badge is not the generic software mark;
it becomes the **Talks** identity. Each page gets its own artifact at the
header's top right, beside the title, matching the nature and neutral pages.
Public GitHub stacks its GitHub logo above the QR in that right rail.

- **Talks — conference badge.** The speaker badge: lanyard, clip, name-tag or
  QR. Use it on the page header and the hub card. It is the personal, human
  object; Ran wears a badge at conferences.
- **Public GitHub — official GitHub logo.** The GitHub mark on the page header
  and the hub card, beside the QR in the header. The CMake reference is
  reduced to a small two-line text tag in each repository card's rail
  (`[ 20%] Building CXX object` / `[100%] Linking CXX executable`), above the
  GitHub link; it is not the page or hub artifact.
- **C++ & Standards — official C++ logo.** The unaltered hexagon logo from
  `github.com/isocpp/logos` (created by Jeremy Kratz, licensed by The
  Standard C++ Foundation), with the full `ISO/IEC JTC1/SC22/WG21` as text.
  The Foundation's terms permit the unaltered logo alongside materials about
  standardized C++ and working drafts, provided it does not imply endorsement
  (it is a trademark, not public domain). Use it on the page header, the
  paper-card rail and the hub card, with paper-number cards below. No ISO
  logo.

Public GitHub is implemented and committed: the page header and hub card use
the GitHub logo, and the repository rail carries the CMake build tag above the
GitHub link. C++ & Standards is implemented. Talks is implemented and awaiting
review: the page header uses the full conference badge, the hub card and the
talk rail use the badge name tag, and the talk cards follow the same straight
pull-out rhythm. The hub cards keep the same portrait note and lanyard; only
the top mark changes per page, and the page headers follow the same artifact.
The C++ kicker becomes `ISO/IEC JTC1/SC22/WG21` while the title stays
`C++ & Standards`; the string is long for the narrow hub card, so test its
wrapping and adjust the kicker size/tracking or use a deliberate two-line
split.

The generic card page remains the fallback for the other cards. Per-page
stylesheets are auto-discovered from `assets/css/pages/<slug>.css`; a page
without one gets only `theme.css` + `site.css`.

### Book page — Birds of Israel Index

The Book card is now **Birds of Israel Index**. It keeps the standard cream
sheet, dirty field and open-book page mark. The page has three parts: the
intro prose, a left-aligned download button with a standard download icon, and
a right-to-left page-turn preview. The preview uses the ready-made **pdflip
0.1.0** engine (BSD-3, pdf.js, vendored) rather than custom page-turn
mechanics, with `direction: "rtl"`, `flipStyle: "cover"`, and
`pageMode: "auto"`. It flips the actual PDF from R2, so there are no page
images and no render step. The book is centred; on narrow screens the spread
becomes one page at a time.

The controls sit under the book: **Next** on the left with a left arrow,
**Previous** on the right with a right arrow, and a **Go to** number input
between them. The `Pages 72–73 of 87` counter is a separate centred line under
the controls; both the counter and the Go input use the book's printed page
numbers (PDF page = printed page + 6). The old instructions ("Swipe, drag a
page edge…") and the "third edition…" sentence were removed. The download
button is aligned left and uses `assets/icons/download.svg`.

The PDF is a real download (`Content-Disposition: attachment`) rather than a
new-tab viewer. The name is `birds-of-israel-index.pdf`; it is R2-only and
untracked. The bucket CORS policy allows the site origin and the local preview
with `GET`/`HEAD`; the viewer disables range loading, so that is enough. If
JavaScript is unavailable, the PDF download remains.

### Holding pages — Learning Aid, About, Contact

These three cards are still in development, so their pages share a deliberately
minimal holding layout: the card title, one large photograph of a male
Black-headed Weaver hanging beneath a half-built grass nest, a tilted **Under
Construction** stamp in the sky, and the Previous/Next pager. There is no prose,
status badge, construction strip or visible caption. The layout fills the
viewport with the photo and does not scroll at normal desktop and mobile sizes.
The CC BY-SA 4.0 attribution remains in a visually hidden figcaption, because
the image requires it.

The cards set `holding: true`, which links the shared
`assets/css/pages/holding.css` instead of a per-slug stylesheet. The real
Learning Aid, About and Contact pages will replace the shared treatment when
their content is ready.

The alternative **Coming Soon** treatment was not used because the
nest-building photograph is clearer and shows the work in progress.

## Next step

The Learning Aid, About and Contact holding pages are in place. Build the
contact power-line/notebook interaction when the real contact content is ready.
Voice-over comes last.
