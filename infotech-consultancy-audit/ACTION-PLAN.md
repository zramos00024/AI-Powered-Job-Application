# Action Plan: Infotech Consultancy

## Critical (at go-live)
1. Remove `<meta name="robots" content="noindex">` from all pages and the comment in `robots.txt`.
2. Verify production: 301 non-www to www, HTTPS and HSTS, the sitemap at `https://www.infotechconsultancy.io/sitemap.xml`, and that `og-image.jpg` and `logo-square.png` return 200.
3. Submit the sitemap in Google Search Console and Bing Webmaster Tools.

## High
4. Finish and publish the 4 draft case studies (insurance, telecom, waste-management, education) and add them to the sitemap, or remove the links to them from `/case-studies/` and `/industries.html`.
5. Rewrite the 18 titles over 60 characters (worst: `optus.html` 124, `optus-docusign-implementation.html` 122, `blue-cross-blue-shield.html` 113).
6. Add security headers in `vercel.json`: CSP, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy` and `frame-ancestors`.

## Medium
7. Trim 5 meta descriptions to 150–160 characters (home, contact, about, delivery, services).
8. Remove lazy-loading from the first image on 13 pages and add `fetchpriority="high"` to the hero.
9. Add BreadcrumbList to inner pages, and WebSite and Service schema. Give Organization an `@id` and add more `sameAs`.
10. Add `/llms.txt` and an explicit AI-crawler policy in `robots.txt`.
11. Clarify `/delivery.html` vs `/delivery-models.html` (merge, or differentiate and cross-link).
12. Expand `/events.html`, and add outcomes and quotes to the case studies.
13. Set long-lived cache headers on static assets.

## Low
14. Shorten and lowercase long or uppercase case-study URLs (`BRP-Quote-Flow-Application.html`) and 301 the old ones.
15. Fix the 3 heading-level skips and 2 generic anchor texts, and enlarge sub-24 px tap targets.
16. Add `security.txt`.

## Ongoing
- Re-run this audit after go-live on the production domain with GSC and GA4 connected, and set a drift baseline (`seo-drift`).
