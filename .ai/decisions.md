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
| Visual design | **Deferred to a dedicated session.** Structure must stay metaphor-neutral: no yin-yang, puzzle, palette, or typography commitments in the markup. |
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
- `assets/ringing/main_page_concept.jpeg` is a mood reference, not a spec.
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
