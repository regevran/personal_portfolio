# Design phase — the yin-yang field board

Date: 2026-11-08
Status: one direction selected; anchors chosen (C05 lanyard + N03 robin perch); robin PNG pending.

## Goal

Settle the visual language of the main page before wiring the card pages. The
cards are shown but deliberately **not linked**. The next decision is which
anchor each card family hangs from.

## Direction of travel

The first pass was too clean and grid-like. The language is now a **dirty field
notebook collage**: one dirty ink image as the whole page, with the data placed
on top of it. Nothing else: no separate page texture, no taped photo frame, no
strips of tape. The ten sections are notes on the board, not a grid.

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
- `design/assets/textures/field-background.jpg` — **the single page
  background**: the ink image, warm-blended, with the sharp cutout baked in.
- `design/assets/textures/paper-dirty.jpg` — retained from the first pass but no
  longer used; the separate paper layer was removed.

The book cover contributed:

- `design/assets/img/robin.png` — the European robin, cropped from the cover's
  podcast mark. It is no longer used on the board because the podcast microphone
  is baked in under the bird's feet; the creator is supplying a transparent PNG
  instead.
- `design/assets/img/robin-logo.png` — the full robin + microphone + Hebrew
  podcast mark; reference only.

**Eye alignment:** in the composite, the cutout is 440 px wide and placed at
(321, 34); the owl's eye lands at (645.67, 227.72), on the yin-yang's light eye
at (646, 228). Because the cutout is baked into the bitmap, the alignment cannot
drift.

The earlier `bird-circuit` vector was rejected and removed.

## Direction A — Field Board

The concept direction, now with exactly two layers:

1. `field-background.jpg` — the dirty ink yin-yang with the sharp Ran + owl
   cutout baked in.
2. The data on top — name sign, tagline and intro notes, Software/Nature signs,
   the book robin, and the ten section notes.

The background is fixed to the viewport on desktop; the notes scroll over it.
The title bar is sticky at the top over that background and carries the name,
email, phone, and a four-item navigation (About, Work, Nature, Contact). The nav
targets are anchors to the corresponding cards for now; real page routes arrive
with the card pages. The cards carry a family-coloured top rule: software
`#3E6B89`, nature `#5F6232`, neutral ochre. The card surfaces stay cream so the
text remains readable over the dark ink.

The anchor colour follows the card: the C05 lanyard straps are software blue,
matching the software card rule; the N03 branch, twine, and leaf are nature
green, matching the nature card rule. The earlier three-colour perch (ochre
branch, olive leaf, ink twine) was collapsed into that single green.

On narrow screens the single background becomes a full-bleed hero panel that
fades into sand; the notes and cards below sit on sand, because a fixed
landscape background cannot be cropped meaningfully on a phone. The hero keeps
the same composite, not a different one.

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
robin perch: a branch, twine, and a small robin slot above the card. The perch
is repeated above Birding & Ringing, Rescues, Podcast, The Book, and Learning
Aid.

The robin is currently a **56 × 72 px placeholder** on the board (a dashed
rectangle); the enlarged N03 study uses 104 × 132 px. The book's creator is
supplying a transparent PNG; that is sufficient. The PNG will replace the
rectangle at either size with `object-fit: contain`. The interim raster robin
with the podcast microphone is no longer used.

The wooden name, Software, and Nature signs were removed from the hero: they
read as yet another anchor and added mass. The topbar wordmark and the tagline
note carry the name and pitch; the hero is the cutout, the notes, and the two
sketch birds.

## Files

- `design/index.html` — chooser: field board + anchor studies.
- `design/direction-a.html` — the one-background board with the selected
  anchors.
- `design/hooks.html` — the ten anchor studies, with N03 and C05 marked selected.
- `design/assets/design.css`.
- `design/assets/img/`, `design/assets/textures/`, `design/assets/fonts/`.

## Next step

Drop in the transparent robin PNG when it arrives. Then integrate the board into
`templates/`, `assets/css/site.css`, and the hub renderer; apply it to the card
pages and build the contact power-line/notebook interaction. Cards stay
unlinked until the integration step. Voice-over comes last.
