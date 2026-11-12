# Technical SEO Audit: Infotech Consultancy (preview build)

**Host:** https://infotech-consultancy-preview.vercel.app · **Date:** 2026-11-12
**Framework:** claude-seo `seo-technical` (9 categories) · **Pages:** 30 (all sitemap URLs) + 4 unlisted drafts
**Technical score: 80 / 100** (go-live basis; the preview `noindex` is treated as intentional)

> Method note: claude-seo's network scripts (`transport_check.py`, `render_page.py`, `sitemap_discovery.py`, `agentic_check.py`, `preload_check.py`) could not resolve DNS in this sandbox, which only reaches the web through a proxy. I ran the equivalent checks with curl, Playwright and the offline `page_checks.py`. Gaps are listed under "Could not verify".

## Summary by category

| # | Category | Status | Score |
|---|---|---|---|
| 1 | Crawlability | Good, one intentional block | 85 |
| 2 | Indexability | Blocked by preview `noindex` (intentional); canonical handling is good | 80 |
| 3 | Security | HTTPS and HSTS strong, other headers missing | 65 |
| 4 | URL structure | Clean, a few variants | 78 |
| 5 | Mobile and page experience | Good, small tap targets | 82 |
| 6 | Core Web Vitals | Excellent in lab tests | 95 |
| 7 | Structured data | Valid but minimal | 60 |
| 8 | JavaScript rendering | No issues (server-rendered) | 98 |
| 9 | IndexNow | Not implemented | 50 |

## 1. Crawlability
- `robots.txt`: present, valid, `User-agent: *` / `Allow: /`, declares `https://www.infotechconsultancy.io/sitemap.xml`. No resources blocked.
- Sitemap: valid XML, 30 URLs, all 200 on the preview host. It lists the production host, so URLs only resolve here by path. The 4 draft case-study pages (`insurance`, `telecom`, `waste-management`, `education`) are crawlable via links but missing from the sitemap.
- **Crawl depth:** every page is within 2 clicks of the homepage (1 page at depth 0, 21 at depth 1, 8 at depth 2). No orphan pages among the 30.
- HTML weight: largest page 30.7 KB, far below Googlebot's 2 MB fetch limit. JSON-LD sits inside the first bytes.
- AI crawlers: no AI-specific rules. All allowed by default (including GPTBot, ClaudeBot, Google-Extended). Make this a deliberate choice.
- **Medium (intentional):** `<meta name="robots" content="noindex">` on every page, including the 404 template.

## 2. Indexability
- Canonicals: present on all 30 pages, absolute, point to the production host, and match the sitemap exactly. No canonical/noindex conflict in intent.
- Duplicate-URL variants return 200 on the preview host:
  - `/about` (no `.html`) → 200 with the same content as `/about.html`. Canonical covers it, but a 301 to the `.html` URL is cleaner.
  - `/about.html?utm=x` → 200 (canonical strips the query; fine).
  - `/services` → **307** (temporary) to `/services/`. Should be a 301/308.
  - `//about.html` → 308 to `/about.html` (correct).
- `/index`, `/INDEX.HTML` → 404 (correct).
- Titles and descriptions are unique across pages. No hreflang, pagination or AMP (not needed for a single-language site).
- Thin pages: `/events.html` (179 words) and `/contact.html` (180).

## 3. Security
| Header / item | Result |
|---|---|
| HTTPS | Enforced (HTTP/2) |
| Strict-Transport-Security | `max-age=63072000; includeSubDomains; preload`. Meets preload rules |
| Content-Security-Policy | **Missing** |
| X-Content-Type-Options | **Missing** |
| X-Frame-Options / `frame-ancestors` | **Missing** |
| Referrer-Policy | **Missing** |
| Permissions-Policy | **Missing** |
| `access-control-allow-origin: *` | Set on all responses (fine for static public content) |
| Mixed content | None (0 on all 30 pages) |
| Back-button hijacking | None (no `pushState`/`replaceState`/`history.*` in `main.js` or page HTML) |
| Server stack CVE exposure | Static Vercel host, no PHP/WordPress signals. Not exposed |
| Cookies | None set |

**Fix:** add a `headers` block in `vercel.json` for the four missing headers plus Permissions-Policy.

## 4. URL structure
- Descriptive, hyphenated, no query parameters for content. Logical folders: `/services/`, `/case-studies/`.
- **Low:** `.html` extensions throughout and `/index.html` as the homepage. Optional: clean URLs.
- **Low:** 4 URLs over 100 characters (the Veolia, VMware, SY3 and NAC case studies).
- **Low:** `BRP-Quote-Flow-Application.html` has uppercase characters.
- No redirect chains found (max 1 hop).

## 5. Mobile and page experience
- Viewport meta on all pages, `lang="en-AU"`, body text 17 px, no text under 12 px, no horizontal scroll at 390 px.
- No intrusive interstitials or cookie dialogs.
- Content parity: single responsive template, so desktop and mobile carry the same content and markup.
- **Medium:** nav and footer text links are 19 px tall at mobile width (e.g. Salesforce & MuleSoft, About us, Events). WCAG 2.2 AA asks for at least 24 px. Add vertical padding (about 6 px) to footer and nav links.

## 6. Core Web Vitals (lab, headless Chromium, unthrottled)
| | Desktop | Mobile 390 px | Target |
|---|---|---|---|
| LCP | 0.64 s | 0.29 s | ≤ 2.5 s |
| CLS | 0 | 0 | ≤ 0.1 |
| INP | not measured | not measured | ≤ 200 ms |

- 18 requests, 0 third-party, 0 console errors, 0 failed requests.
- Compression works: gzip and brotli served.
- **Medium:** all assets (CSS 30 KB, JS 3.4 KB, fonts, images) carry `cache-control: public, max-age=0, must-revalidate`, so repeat visits revalidate everything. Use long-lived `max-age` with `immutable` for fingerprinted or rarely-changing assets.
- **Medium:** the first image has `loading="lazy"` on 13 pages (LCP candidates).
- INP and real-user LCP need field data (CrUX / Search Console) after launch.

## 7. Structured data
- One `Organization` JSON-LD block per page, 0 parse errors, 30/30 pages.
- Missing: `WebSite`, `BreadcrumbList`, `Service`, `Article`/case-study types; no `@id` on the Organization; `numberOfEmployees` has only `minValue`.

## 8. JavaScript rendering
- Fully server-rendered static HTML. Raw HTML has about 974 words versus 881 rendered on the homepage, so no content depends on JavaScript.
- Title, canonical and meta robots are identical in served and rendered DOM (no JS conflicts).
- Only 3 KB of deferred JS (plus small per-page scripts on events, careers and contact). No SPA framework. Rendering strategy: SSG, which is the recommended approach.
- Error pages: the 404 returns a real 404 status.

## 9. IndexNow
- `/indexnow.txt` (key file) not found; no IndexNow ping set up. Optional, benefits Bing, Yandex and Naver. Add after launch.

## Prioritised fixes
| Priority | Fix | Effort |
|---|---|---|
| Launch | Remove `noindex` from all pages, plus the comment in `robots.txt` | 10 min |
| Launch | Confirm production host: valid TLS, http→https and non-www→www 301s, sitemap and OG image/logo return 200 | 1 h |
| Launch | Finish or unlink the 4 draft case-study pages; add them to the sitemap once ready | content |
| High | Add CSP, X-Content-Type-Options, Referrer-Policy, Permissions-Policy and `frame-ancestors` in `vercel.json` | 1 h |
| High | Long-lived cache headers for static assets | 30 min |
| Medium | Make `/services` use a 301/308 and redirect extensionless URLs like `/about` to their `.html` canonicals | 30 min |
| Medium | Remove `loading="lazy"` from first image on 13 pages | 15 min |
| Medium | Raise nav/footer link tap height to 24 px or more | 30 min |
| Medium | Add `BreadcrumbList`, `WebSite`, `Service` and case-study schema | half day |
| Low | Lowercase and shorten long case-study URLs, with 301s | 1 h |
| Low | Add IndexNow, `llms.txt` and `security.txt` | 1 h |

## Could not verify
- **TLS certificate and http→https redirect:** the sandbox proxy re-signs TLS and blocks plain HTTP, so certificate validity, expiry and the HTTP redirect could not be read. Vercel manages certificates automatically.
- **Production domain** (`www.infotechconsultancy.io`): not reachable from here.
- **Field Core Web Vitals, INP, Search Console indexation, GA4:** need credentials and live traffic.
- claude-seo scripts that need direct DNS (listed at the top) were replaced by equivalent manual checks.
