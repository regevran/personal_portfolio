# Design phase — the yin-yang field board

Date: 2026-11-08
Status: 16:9 poster layout with title-only cards; anchors chosen (C05 lanyard +
N03 robin perch); robin transparent PNG integrated; the board is now the site
hub, with each card linking to its page. Podcast has floating chapter cards;
Public GitHub has a conference badge and straight, pull-out repository cards,
both on the dirty ink background. The other card pages keep the shared
first-pass styling; contact interaction remains.

## Goal

Settle the visual language of the board, then carry it into the card pages. The
board is a title-only index; every card links to its page, where the content
lives.

## Direction of travel

The first pass was too clean and grid-like. The language is now a **dirty field
notebook collage**: one dirty ink image as the whole page, with the data placed
on top of it. Nothing else: no separate page texture, no taped photo frame, no
strips of tape. The eleven sections are notes on the board, not a grid.

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
2. The data on top — a tagline note and eleven title-only cards placed around
   the portrait.

The spatial grammar follows the original jpeg but is deliberately **not a
grid**: **nature is scattered on the left** (Birding, Ringing, Rescues,
Podcast, The Book, Learning Aid) in a zigzag, **software is on the right**
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
above Birding, Ringing, Rescues, Podcast, The Book, and Learning Aid.

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

Podcast gets a page-specific treatment in `assets/css/pages/podcast.css`,
loaded only for that page. It follows the hub more closely than the generic
card page:

- The page background is the dirty ink texture
  (`assets/general/dirty-background.jpg`), fixed on desktop. There is no
  full-page cream sheet.
- The header is one cream note with the full circular logo
  (`assets/general/closing_on_birds_circle.png`) floating in its top-right.
- The intro paragraphs are notes.
- The header and the promo-video cards are straight. The videos sit at the
  bottom of the page, after the episode list.
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
- Static text rectangles (header, intro notes, pager) get a soft gold glow on
  hover; tilted episode cards straighten and lift instead.

### Public GitHub page

Public GitHub (`engineering`) shares the dirty field and cream notes with
Podcast but reads as software. Its rules live in
`assets/css/pages/engineering.css`.

- The background is the same dirty ink texture, fixed on desktop; there is no
  full-page sheet. The title uses the formal serif, not Patrick Hand.
- The header is a portrait cream note with the software-blue top edge and the
  narrow lanyard, now carrying the **build-log artifact**: a dark ink terminal
  panel with the `cmake --build` command and the `Building CXX object
  portfolio` / `Linking CXX executable portfolio` lines, beside the real
  GitHub QR code in a white quiet-zone frame. The kicker, formal-serif title
  and summary sit under the terminal. The QR
  (`assets/general/github-qr.svg`) was generated for
  `https://github.com/regevran` and still scans to the profile.
- Intro paragraphs are straight cream notes with a software-blue left rule.
- Repositories are straight cream cards with a software-blue top edge. The
  repository name sits left and the last-push date is centred on the first
  line; the description follows. An absolutely positioned right-hand rail
  mirrors the robin rail on Podcast cards: the CMake build mark
  (`assets/icons/build-mark.svg`) sits above the GitHub mark
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
- Static text notes (header, intro notes, back link, pager) get a soft blue
  glow. `prefers-reduced-motion` removes the pull-out transform.

### Software badges on the hub

The hub's three software notes use the same portrait container: narrower and
taller than the nature notes, with a narrow C05 lanyard whose clip meets the
blue top edge, no punched-hole circle, and a per-page artifact mark above the
kicker and title. Public GitHub now uses the CMake build mark
(`assets/icons/build-mark.svg`); C++ & Standards and Talks still use the QR
mark (`assets/icons/badge-mark.svg`) until their artifact passes. Nature and
neutral notes keep the landscape note and their robin/perch treatment.

### Software page artifacts

Agreed 2026-11-11. The software pages share one container: the portrait cream
note, narrow lanyard, software-blue edge, formal serif title and mono kicker
hanging on the board. The conference badge is not the generic software mark;
it becomes the **Talks** identity. Each page gets its own artifact at the top:

- **Talks — conference badge.** The speaker badge: lanyard, clip, name-tag or
  QR. Use it on the page header and the hub card. It is the personal, human
  object; Ran wears a badge at conferences.
- **Public GitHub — CMake build log.** A small ink terminal strip with cream
  mono output (`[ 20%] Building CXX object portfolio`). It fits "Systems", is
  recognisable to developers and echoes the site's own CMake build. Replace
  the conference badge in both the page header and the hub card; the
  repository cards carry the build mark above the GitHub link in their rail.
- **C++ & Standards — WG21 document stamp.** A small paper sheet or bordered
  stamp with `WG21`; the full `ISO/IEC JTC1/SC22/WG21` is text, not a logo.
  Use it on the page header and the hub card, with paper-number cards below.
  No ISO or C++ logo: WG21 papers are committee proposals, not ISO
  publications, and the logos are restricted.

Public GitHub is implemented: the page header and hub card use the build-log
mark, and the repository rail keeps only the GitHub link. The hub cards keep
the same portrait note and lanyard; only the top mark changes per page, and
the page headers follow the same artifact. Work order: Public GitHub is done
and awaiting review; then C++ & Standards; then Talks.
The C++ kicker becomes `ISO/IEC JTC1/SC22/WG21` while the title stays
`C++ & Standards`; the string is long for the narrow hub card, so test its
wrapping and adjust the kicker size/tracking or use a deliberate two-line
split.

The generic card page remains the fallback for the other cards. Per-page
stylesheets are auto-discovered from `assets/css/pages/<slug>.css`; a page
without one gets only `theme.css` + `site.css`.

## Next step

Design the remaining card pages individually, starting with whichever card
matters next. Then build the contact power-line/notebook interaction.
Voice-over comes last.
