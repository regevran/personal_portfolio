# Design phase — the yin-yang field board

Date: 2026-11-08
Status: 16:9 poster layout with title-only cards; anchors chosen (C05 lanyard +
N03 robin perch); robin transparent PNG integrated.

## Goal

Settle the visual language of the main page before wiring the card pages. The
cards are shown as a title-only index and deliberately **not linked**; content
lives in the card pages.

## Direction of travel

The first pass was too clean and grid-like. The language is now a **dirty field
notebook collage**: one dirty ink image as the whole page, with the data placed
on top of it. Nothing else: no separate page texture, no taped photo frame, no
strips of tape. The eleven sections are notes on the board, not a grid.

Direction A (the field board) is the only direction. Directions B and C were
dropped and their files deleted.

## Constraints

- Main page only; cards are non-interactive.
- Static HTML/CSS. No runtime network requests.
- English.
- Book palette and book typography as the base.
- One bundled OFL font for handwritten labels: Patrick Hand.
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
- Handwritten names, card titles, sign labels: Patrick Hand (bundled, OFL).
- Fallbacks: `ui-monospace`, Georgia, cursive.

## Source artwork

The Canva SVG is a flattened export and is not usable as separable artwork, but
it contains the exact pieces we need. Extracted from it:

- `design/assets/img/ran-otus.png` — the cutout of Ran and the scops owl, with
  the colour image combined with its alpha mask.
- `design/assets/textures/ink-yinyang.jpg` — the dirty ink yin-yang background.
- `design/assets/textures/board-background.jpg` — **the 1600 × 900 poster
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
(Engineering & Systems, C++ & Standards, Talks) with varied x positions rather
than one column, and the two neutral cards (About, Contact) stay flat and
bottom-aligned under the portrait. Hanging cards rotate up to roughly ±6° and
pivot from their grommet; the rest of the board does not move. The whole
yin-yang group is shifted 120 px right so nature gets more of the wall and
software gets less. The tagline sits above the portrait. Cards are enlarged to
use the free space. The card labels are kicker + title only; descriptions,
statuses, and all other content live in the card pages.

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

## Next step

Integrate the board into `templates/`, `assets/css/site.css`, and the hub
renderer; apply it to the card pages and build the contact
power-line/notebook interaction. Cards stay unlinked until the integration
step. Voice-over comes last.
