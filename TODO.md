# TODO

## Immediate

[x] Public GitHub — complete the artifact pass — [details](.ai/design-brief.md#software-page-artifacts)
[x] C++ & Standards — apply the C++ logo motif — [details](.ai/design-brief.md#software-page-artifacts)
[x] Talks — make the conference badge its identity — [details](.ai/design-brief.md#software-page-artifacts)

## Site

[x] Style the Podcast page in the board's visual language — [details](.ai/design-brief.md#podcast-page)
[x] Style the Public GitHub page in the board's visual language — first pass
[x] Style the Ringing page in the board's visual language — [details](.ai/design-brief.md#ringing-page)
[x] Style the Rescues page in the board's visual language
[x] Style the Birds of Israel Index page in the board's visual language — PDF download, RTL pdflip viewer, Go to page — [details](.ai/design-brief.md#book-page--birds-of-israel-index)
[x] Style the Learning Aid page in the board's visual language — title, licensed weaver photo with tilted Under Construction stamp, Previous/Next, no scrolling
[x] Style the About page in the board's visual language — same title-and-photo holding page as Learning Aid
[x] Style the Contact page in the board's visual language — same title-and-photo holding page as Learning Aid
[ ] Build the contact notebook / power-line interaction — [details](.ai/design-brief.md#next-step)
[x] Choose host and domain, then add a deploy step around `cmake --install` — GitHub Pages + R2 content media, [details](.ai/decisions.md)
[ ] Move "Learning Aid" to software - after all, this is a software development effort more than birding
[x] Keep page.md and unify it with the single page card (Rescues format); summary alone is not enough — Ringing was the only page that split header, prose and cards
[ ] Birding (phase 2, if ever) — build and style the page in the board's visual language

## Content

[x] Apply the split note intro and a language/emphasis pass to the six prose pages — [details](.ai/design-brief.md#prose-pages--split-note-intro)
[x] Add the Common Chiffchaff photos to `content/data/photos.json`
[x] Decide the podcast promo-video block position (first or after episodes)
[x] Fill missing dates (2 talks, 4 rescue videos, 10 photos) — full list in the build warnings, [notes](.ai/asset-inventory.md#missing-or-pending)
[ ] Add the real CV PDF — [details](.ai/asset-inventory.md#missing-or-pending)
[x] Publish the book PDF — [details](.ai/asset-inventory.md#missing-or-pending)
[x] Upload the videos to YouTube and set their `youtube` IDs — [details](.ai/decisions.md#deferred-items)
[ ] Add the gallery as a card — [details](.ai/decisions.md#deferred-items)
[ ] Decide the learning-aid hosting strategy — [details](.ai/asset-inventory.md#missing-or-pending)
[ ] Replace all Lorem Ipsum with real content
[ ] Add more content to each GitHub repository
[ ] Add more content to Rescues cards
[ ] Birding (phase 2, if ever) — add photos and field stories — [details](.ai/asset-inventory.md#missing-or-pending)
[ ] Record voice-over and transcripts — [details](.ai/decisions.md#deferred-items)

## Bugs

[ ] Not all podcast links are correct, it seems that old episodes were not fetched correctly, should be fixed

## Follow-up

[ ] Move the remaining inline prose (paper and talk descriptions) into Markdown files
[x] Verify the live Pages site after the first workflow run — workflow added in `.github/workflows/pages.yml`, URL <https://regevran.github.io/personal_portfolio/>
[ ] Add a "keep/hidden" marker for media intentionally stored in R2 but not referenced by the site, so the audit can distinguish it from stale objects
[x] Delete the stale R2 objects: `assets/book/pages/*` (98 page JPEGs) and `assets/documents/israel_birds_one_file.pdf` (old PDF name).
[ ] Add the robin to every nature page header, and a matching badge to the engineering pages — deferred to the end; Ringing's page robin is removed for now
