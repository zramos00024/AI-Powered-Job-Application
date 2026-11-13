# Infotech Consultancy home page: five design directions

Source page: https://infotech-consultancy-preview.vercel.app/index.html

Open `index.html` to pick a direction, or go straight to `design-1.html` … `design-5.html`.

| # | Name | Idea |
|---|------|------|
| 1 | Harbour | The current brand, sharpened |
| 2 | Control Room | Dark, technical, pinned sideways case studies |
| 3 | Broadsheet | Editorial serif, ruled columns |
| 4 | Stack | Sections are cards that stack over each other |
| 5 | Two Hubs | A route line drawn down the page by the scroll |

## How it is built

`python3 build.py` regenerates every page from `src/original.html` (the live page, untouched).
The copy is never retyped: each design is the original markup plus hooks, and
`python3 build.py --check` fails if any design's visible text differs from the original.

- `src/base.css`, `src/core.js`: shared header, footer, reveal and scroll engine
- `src/dN.css`, `src/dN.js`: one design each
- `assets/`: built CSS/JS, fonts and images (the output)

## Going live

1. Rename the chosen `design-N.html` to `index.html` and copy it with `assets/css/dN.css`,
   `assets/js/dN.js`, the new `assets/img/og-default-*.avif` / `og-default-960.webp` files and
   any new font in `assets/fonts/` into the site root. Links to other pages are unchanged.
2. Merge `vercel.json` (one-year caching for `/assets/`; the CSS and JS URLs carry a content hash).
3. Remove `<meta name="robots" content="noindex">` when the site should be indexed.

Fonts added: Fraunces, Bricolage Grotesque, JetBrains Mono (all SIL Open Font License), self-hosted.
