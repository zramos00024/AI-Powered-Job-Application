# SEO Audit: Infotech Consultancy (preview build)

**URL audited:** https://infotech-consultancy-preview.vercel.app/index.html
**Date:** 2026-11-12 · **Method:** claude-seo v2.6.0 scripts (`page_checks.py`) plus custom crawl, Playwright (desktop and mobile) and HTTP checks
**Pages crawled:** 30 of 30 sitemap URLs, plus 4 unlisted draft pages

## Executive summary

**SEO Health Score: 72 / 100** (go-live basis, ignoring the intentional preview `noindex`)
**Business type:** B2B technology consulting and IT services (Australia and India, Salesforce/MuleSoft, Cloud, Data/AI, QE)

The site is technically clean and fast. It has no broken pages, no duplicate titles or descriptions, one H1 per page, WebP images with alt text and a 404 that returns a real 404 status. The main gaps are on-page metadata (titles too long on 18 of 30 pages), thin structured data (Organization only) and a handful of go-live items.

| Category | Weight | Score |
|---|---|---|
| Technical SEO | 22% | 78 |
| Content Quality | 23% | 74 |
| On-Page SEO | 20% | 66 |
| Schema | 10% | 55 |
| Performance | 10% | 92 |
| AI Search Readiness | 10% | 60 |
| Images | 5% | 88 |

### Top 5 issues
1. **Preview `noindex` on all 30 pages (plus the 4 draft pages).** This is intentional per the `robots.txt` comment, but the site is invisible to search until the tags are removed. It is the #1 go-live blocker.
2. **Sitemap and canonicals use `www.infotechconsultancy.io`, but the preview host differs.** Those URLs are not live for me to verify. Confirm the production domain serves identical paths, 301s non-www to www, and that the sitemap is submitted after launch.
3. **Titles too long on 18 of 30 pages.** Case-study titles run 69–124 characters and will be truncated in results. Examples: `/case-studies/optus.html` (124), `/case-studies/optus-docusign-implementation.html` (122), `/delivery-models.html` (96). The homepage is 74.
4. **Four draft case-study pages are linked but not in the sitemap.** `insurance`, `telecom`, `waste-management` and `education` case studies are linked from `/case-studies/index.html` and `/industries.html`, with "(Draft)" in their titles. They are noindex, but they should be finished or unlinked before launch.
5. **Schema is Organization only, and identical on every page.** There is no WebSite, BreadcrumbList, Service or Article/case-study markup.

### Top 5 quick wins
1. Shorten the 18 long titles to 50–60 characters (about 30 minutes of edits).
2. Trim the 5 long meta descriptions (homepage 241, contact 204, about 199, delivery 188, services 177) to 150–160 characters.
3. Remove `loading="lazy"` from the first, above-the-fold image on 13 pages (LCP candidate).
4. Add `/llms.txt` (currently 404).
5. Add BreadcrumbList to all inner pages, and Service schema to the 6 service pages.

## Technical SEO (78)
**Works:** HTTPS with HSTS (`max-age=63072000; includeSubDomains; preload`), HTTP/2, 200s everywhere, custom 404 returning a true 404, valid XML sitemap (30 URLs, all resolve), `robots.txt` present with a sitemap reference, canonicals present and self-consistent on production host, `lang="en-AU"`, viewport meta, favicon and apple-touch-icon present, no mixed content, no external scripts or fonts (fonts are self-hosted and preloaded).
**Findings:**
- **Critical (intentional):** `<meta name="robots" content="noindex">` on every page.
- **High:** canonical points to the production host. This is correct for go-live, but it means the preview is excluded from indexing twice over. Fine as long as the production host is verified.
- **Medium:** missing security headers: no `Content-Security-Policy`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` or clickjacking protection (`X-Frame-Options` or CSP `frame-ancestors`). Set these in `vercel.json`.
- **Medium:** `cache-control: public, max-age=0, must-revalidate` on everything, including the CSS, JS, fonts and images. Give hashed or static assets a long-lived `max-age` plus `immutable`.
- **Low:** `/case-studies/BRP-Quote-Flow-Application.html` has uppercase letters in its URL, and 4 case-study URLs exceed 100 characters. Shorten and lowercase these, with 301s from the old paths.
- **Low:** URLs end in `.html` and the homepage is `/index.html`. Make sure `/` is the canonical form that is linked internally (canonical already uses `/`).
- **Info:** `/.well-known/security.txt` and `/manifest.webmanifest` do not exist (optional).

## On-Page SEO (66)
| Check | Result |
|---|---|
| Unique titles / descriptions | Yes (0 duplicates) |
| Exactly one H1 | 30/30 |
| Title > 60 chars | **18 pages** (max 124) |
| Title too short | 1 (`/events.html`, 29) |
| Description > 160 chars | **5 pages** |
| Heading level skips | 3 pages (`/services/`, `/delivery-models.html`, `/case-studies/`) |
| Generic anchor text | 2 pages (`/services/`, `/delivery.html`) |

Also: `/delivery.html` and `/delivery-models.html` look like overlapping topics. Check for keyword cannibalisation and merge or differentiate them.

## Content Quality (74)
- Homepage 757 words and About 817 words are healthy. Service pages run 300–520 words, which is adequate but light for competitive B2B terms.
- Case studies are 280–450 words each. They would benefit from quantified outcomes, client quotes and named technologies.
- **Thin:** `/events.html` (179 words) and `/contact.html` (180 words). Contact is acceptable, but events should carry real content or be consolidated.
- E-E-A-T: the Organization schema, offices (Parramatta, Hyderabad), founding year (2013) and named client work are good trust signals. Add author or leadership bios, certifications and partner badges (Salesforce, MuleSoft), and dated case-study metadata.

## Schema (55)
- 30/30 pages carry one valid `Organization` JSON-LD block (0 parse errors). The address, contact point, `sameAs` and `areaServed` are good.
- **Missing:** `WebSite` (with publisher link), `BreadcrumbList`, `Service` (service pages), `Article` or `CreativeWork` (case studies), `@id` on Organization so other types can reference it, and more `sameAs` profiles.
- `numberOfEmployees` has only `minValue: 150`. Use a single `value` or add `maxValue`.
- The `logo` and `og:image` point at the production host and could not be verified on it. Confirm they return 200 at go-live.

## Performance (92)
Measured on the live preview in headless Chromium (unthrottled, so treat as indicative, not field data):
| | Desktop | Mobile (390px) |
|---|---|---|
| LCP | 0.64 s | 0.29 s |
| CLS | 0 | 0 |
| DOMContentLoaded | 0.58 s | 0.43 s |
| Requests | 18 | 18 |
| Third-party requests | 0 | 0 |
| Horizontal overflow | none | none |

Strengths: 30 KB CSS, 3 KB deferred JS, self-hosted preloaded fonts, WebP images (60 unique images, 2.1 MB in total across the site, none above 150 KB). INP could not be measured without field data.
Issue: first image is lazy-loaded on 13 pages (can delay LCP on slower devices). Set `fetchpriority="high"` on the hero and `loading="lazy"` only below the fold.
Accessibility note: 15–16 tappable elements are smaller than 24 px on the homepage (WCAG 2.2 target size). Check nav and footer links on mobile.

## AI Search Readiness (60)
- `robots.txt` allows all agents, so AI crawlers are not blocked. Decide on a deliberate policy for GPTBot, ClaudeBot, PerplexityBot, Google-Extended and similar.
- **No `/llms.txt`** (404).
- Clean semantic HTML and Organization data help citation. Short, quotable definition blocks, FAQ sections and clear service summaries on each service page would help further.
- Brand and entity signals: only a LinkedIn `sameAs`. Add Crunchbase, Clutch, Salesforce AppExchange or partner profiles, and Wikidata if eligible.

## Images (88)
60 unique images: 58 WebP, 2 SVG. 0 missing alt text, 0 missing dimensions. 6 empty alts on the homepage (fine if decorative). Filenames and alt text could carry more descriptive, service-specific wording.

## Not covered
- The production domain (www.infotechconsultancy.io) was not audited. It is not live in this environment.
- No Google Search Console, GA4, CrUX field data, backlink or SERP data was available, so Google API, backlinks and competitor checks were skipped.
- Subagents were not used. Checks ran inline with the claude-seo scripts.
