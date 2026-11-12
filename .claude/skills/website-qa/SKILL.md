---
name: website-qa
description: Run a full QA audit on a website URL you own or are authorised to test. Covers functional checks, responsive/visual screenshots, accessibility (axe-core, WCAG 2.2), UI/UX basics, performance (Lighthouse), SEO (claude-seo skills) and optional security/API scans, then writes one prioritised report with a release gate. Use when the user asks to QA, test, audit or review a website, or to check a deployment before release.
argument-hint: "<url> [--max-pages N] [--fail-on Critical|High]"
---

# Website QA

Orchestrates several tools, gathers evidence, classifies problems and writes one report. Read-only by default: it never submits forms, logs in, or runs active security scans.

## Rules
- Only test sites the user owns or is authorised to test. If unsure, ask once.
- Active security scans (ZAP) and API fuzzing (Schemathesis) need explicit confirmation and a staging target.
- Report only what the tools measured. Mark anything not tested as "not covered". Do not invent results.
- A preview host may carry `noindex` on purpose. Report it once as a launch item, not as a defect on every page.

## Steps
1. **Setup (once per machine)** from the repo root:
   ```bash
   cd .claude/skills/website-qa/scripts && npm install && npx playwright install chromium
   ```
2. **Browser QA** (functional, responsive, accessibility, UX, links, forms, keyboard, screenshots):
   ```bash
   node .claude/skills/website-qa/scripts/qa_run.mjs <url> --out qa-output/<host> --max-pages 40
   ```
   Discovers pages from `/sitemap.xml` (paths mapped onto the tested host) and a link crawl. Writes `findings.json` and `screenshots/<page>-<desktop|tablet|mobile>.png`.
3. **Performance** (Lighthouse mobile and desktop):
   ```bash
   bash .claude/skills/website-qa/scripts/lighthouse_run.sh <url> qa-output/<host>
   ```
4. **SEO**: use the `seo-audit` skill (or `seo-technical` for technical only) on the same URL. Save its findings as a JSON list in the shape `{area:"seo",severity,title,detail,page}` to `qa-output/<host>/seo-findings.json`.
5. **Optional, with confirmation**: security (`zap-baseline.py` passive scan in Docker), API (`schemathesis run <openapi-url>`). Save results the same way, with `area` set to `security` or `api`.
6. **Look at the screenshots** for the worst pages (mobile and desktop) and add any visual or design problems the automation cannot see, with `area:"visual"` or `"ux"`. Judge hierarchy, spacing, readability and navigation clarity, and say they are a reviewer's opinion.
7. **Report**:
   ```bash
   python3 .claude/skills/website-qa/scripts/report.py qa-output/<host> --extra qa-output/<host>/seo-findings.json --fail-on High
   ```
   Exit code 1 means the release gate failed. Summarise for the user in plain English: gate result, top 5 issues, quick wins, and what was not covered.

## Severity guide
- **Critical**: page fails to load, 5xx, checkout/signup broken.
- **High**: WCAG A/AA failures that block users, broken links/images, failed requests, no mobile layout.
- **Medium**: UX friction, small touch targets, console errors, moderate a11y.
- **Low / Info**: polish and best practice.

## Output
`qa-output/<host>/QA-REPORT.md`, `findings.json`, `lighthouse-*.json`, `screenshots/`. Do not commit `qa-output/` or `node_modules/`.
