# Asset inventory

## Present

| Path | Used by | Notes |
|---|---|---|
| `assets/github/links.md` | engineering, repos.json | six repositories |
| `assets/iso/wg21/links.md` | cpp-standards, papers.json | three highlighted papers + full list |
| `assets/talks/links.md` | talks, talks.json | six entries |
| `assets/podcast/links.md` | podcast, episodes.json | 19 episodes |
| `assets/podcast/promo_anat_gal_birds_in_the_city.mp4` | podcast | 1080×1920, 27 s |
| `assets/podcast/promo_shay_agmon_ringing.mp4` | podcast | 1080×1920, 65 s |
| `assets/rescues/ardea_alba.mp4` | rescues | 576×1024, 24 s |
| `assets/rescues/ciconia_ciconia.mp4` | rescues | 478×850, 27 s |
| `assets/rescues/microcarbo_pygmeus.mp4` | rescues | 576×1024, 28 s |
| `assets/rescues/pelecanus_onocrotalus/pelecanus_onocrotalus_video.mp4` | rescues | 848×478, 34 s |
| `assets/rescues/pelecanus_onocrotalus/pelecanus_onocrotalus_{1,2,3,4}.jpeg` | rescues (later) | not yet wired into a gallery |
| `assets/ringing/alcedo_atthis_{1,2,3}.jpeg` | ringing, photos.json | Common Kingfisher |
| `assets/ringing/otus_scops_{1,2,3,4}.jpeg` | ringing, photos.json | Eurasian Scops Owl |
| `assets/ringing/saxicola_maurus.jpeg` | ringing, photos.json | Siberian Stonechat |
| `assets/ringing/upupa_epops_{1,2}.jpeg` | ringing, photos.json | Eurasian Hoopoe |
| `assets/documents/main_page_concept.{jpeg,svg}` | design session only | mood reference; not published. The SVG is a flattened Canva export: 3.1 MB, 16,844 elements, 15 embedded rasters, no semantic labels, text outlined. |

## Missing or pending

| Item | Status |
|---|---|
| Robin PNG | **integrated.** `assets/general/closing_on_birds_robin.png` (359 × 356 RGBA) is used at 56 × 72 px above every nature card and 104 × 132 px in the N03 study. |
| Birding photos/stories | placeholder card `birding` has prose only; add the photos block and records when they arrive. |
| CV PDF | pending; card shows a placeholder |
| Bird book PDF | exists in `~/dev/ran/birds/book/out/` (2.3 MB) but not shareable yet |
| Learning-aid build | design phase only in `~/dev/ran/birds/learn` |
| Photo/video capture dates | not present in EXIF or QuickTime metadata; `date` fields are null until supplied |
| YouTube URLs | local files for now |

## Design assets

| Path | Source | Notes |
|---|---|---|
| `design/assets/img/ran-otus.png` | concept SVG | cutout of Ran + scops owl; colour image + alpha mask |
| `design/assets/textures/ink-yinyang.jpg` | concept SVG | dirty ink yin-yang background |
| `assets/general/board-background.jpg` | composite | **the 1600 × 900 poster background**: ink image with the sharp cutout baked in at 380 px; owl eye aligned to the yin-yang eye |
| `design/assets/textures/field-background.jpg` | composite | earlier 1280 × 720 composite for the scrolling board; retained but no longer used by the poster |
| `design/assets/textures/paper-dirty.jpg` | concept SVG | clean wall patch; retained but no longer used (the separate paper layer was removed) |
| `design/assets/img/robin.png` | book cover PDF | interim raster robin; no longer used on the board — waiting for the creator's transparent PNG |
| `design/assets/img/robin-logo.png` | book cover PDF | full robin + microphone + Hebrew podcast mark; reference only |
| `design/assets/img/anchors-preview.svg` | original | three anchor studies used on the design index |
| `design/assets/fonts/PatrickHand-Regular.ttf` | Google Fonts (OFL) | handwritten labels; licence in `OFL.txt` |
| `design/assets/motifs/*.svg` | original | line-art birds, sign, monitor, yin-yang, interlock |

## Hygiene

- `assets/podcast/.links.md.swp` is a vim swap file; ignored by git and skipped
  by the asset copy. Delete it once the vim session is closed.
- Root `tags` is a universal-ctags index; ignored and regenerable.
- The pelican filename typo was fixed by the user.
- No LFS: all binaries are small enough; GitHub Pages does not serve LFS anyway.
