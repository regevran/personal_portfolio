# Asset inventory

## Present

| Path | Used by | Notes |
|---|---|---|
| `assets/icons/spotify.svg` | podcast episode cards | Spotify platform logo |
| `assets/icons/applepodcasts.svg` | podcast episode cards | Apple Podcasts platform logo |
| `assets/icons/pocketcasts.svg` | podcast episode cards | Pocket Casts platform logo |
| `assets/icons/lanyard.svg` | hub software notes, Public GitHub, C++ & Standards and Talks headers | narrow C05 lanyard + clip, no string |
| `assets/icons/conference-badge.svg` | Talks page header | full speaker badge: lanyard, clip, name tag, QR and name lines |
| `assets/icons/conference-badge-mark.svg` | hub Talks card and talk-card rail | name-tag crop of the conference badge |
| `assets/icons/cpp-logo.svg` | C++ & Standards header and paper rail, hub C++ & Standards card | official C++ hexagon logo, used unaltered; created by Jeremy Kratz, licensed by The Standard C++ Foundation; source `github.com/isocpp/logos` |
| `assets/icons/paper.svg` | C++ & Standards paper cards | document link icon beside the C++ logo |
| `assets/icons/external.svg` | Talks fallback cards | external-link icon for a talk with no video or slides |
| `assets/icons/youtube.svg` | Talks video cards | YouTube play mark for the watch link |
| `assets/icons/github.svg` | Public GitHub header and hub card, repository-card rail | GitHub mark; the page/hub artifact and the repository link |
| `assets/general/github-qr.svg` | Public GitHub page header | real QR code for `https://github.com/regevran`; beside the GitHub logo, white background and CSS quiet zone |
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
| `design/assets/img/main_page_concept.{jpeg,svg}` | design session only | mood reference, moved out of `assets/` so it is not published. The SVG is a flattened Canva export: 3.1 MB, 16,844 elements, 15 embedded rasters, no semantic labels, text outlined. |

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
| `assets/general/dirty-background.jpg` | podcast and Public GitHub pages | dirty ink yin-yang texture without the cutout, 1280 × 720 |
| `assets/general/closing_on_birds_circle.png` | podcast title | full circular podcast logo, 2025 × 2531 RGBA |
| `assets/general/closing_on_birds_logo.png` | podcast chapter cards | robin on the vintage microphone, 720 × 884 RGBA |
| `design/assets/textures/field-background.jpg` | composite | earlier 1280 × 720 composite for the scrolling board; retained but no longer used by the poster |
| `design/assets/textures/paper-dirty.jpg` | concept SVG | clean wall patch; retained but no longer used (the separate paper layer was removed) |
| `design/assets/img/robin.png` | book cover PDF | interim raster robin; no longer used on the board — waiting for the creator's transparent PNG |
| `design/assets/img/robin-logo.png` | book cover PDF | full robin + microphone + Hebrew podcast mark; reference only |
| `design/assets/img/anchors-preview.svg` | original | three anchor studies used on the design index |
| `design/assets/fonts/PatrickHand-Regular.ttf` | Google Fonts (OFL) | handwritten labels; licence in `OFL.txt` |
| `design/assets/motifs/*.svg` | original | line-art birds, sign, monitor, yin-yang, interlock |

## Hygiene

- The one-shot `links.md` import lists and the vim swap file are gone; `assets/`
  now contains only files that are published.
- Root `tags` is a universal-ctags index; ignored and regenerable.
- The pelican filename typo was fixed by the user.
- No LFS: all binaries are small enough; GitHub Pages does not serve LFS anyway.
