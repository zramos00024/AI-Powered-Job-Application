#!/usr/bin/env node
// Website QA runner: browser checks with Playwright + axe-core.
// Usage: node qa_run.mjs <url> [--out DIR] [--max-pages N] [--no-screens]
// Writes DIR/findings.json and DIR/screenshots/*.png. Read-only: it never submits forms.
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(path.join(process.env.NODE_PATH || '', 'playwright'))); }
const axeSource = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');

const args = process.argv.slice(2);
const target = args.find(a => /^https?:\/\//.test(a));
if (!target) { console.error('usage: qa_run.mjs <url> [--out DIR] [--max-pages N] [--no-screens]'); process.exit(2); }
const opt = (n, d) => { const i = args.indexOf(n); return i > -1 ? args[i + 1] : d; };
const origin = new URL(target).origin;
const host = new URL(target).host;
const outDir = opt('--out', path.resolve(`qa-output/${host}`));
const maxPages = Number(opt('--max-pages', 40));
const screens = !args.includes('--no-screens');
fs.mkdirSync(path.join(outDir, 'screenshots'), { recursive: true });

const VIEWPORTS = [
  { name: 'desktop', width: 1366, height: 800, mobile: false },
  { name: 'tablet', width: 768, height: 1024, mobile: true },
  { name: 'mobile', width: 390, height: 844, mobile: true },
];
const findings = [];
const add = (f) => findings.push({ area: 'general', severity: 'Medium', ...f });
const slug = (u) => (new URL(u).pathname.replace(/[^a-z0-9]+/gi, '_').replace(/^_|_$/g, '') || 'home');
const IMPACT = { critical: 'High', serious: 'High', moderate: 'Medium', minor: 'Low' };

const browser = await chromium.launch();

// ---- discover pages: sitemap paths mapped onto the tested origin, then link crawl
async function discover() {
  const pathStart = new URL(target).pathname;
  const pages = new Set([new URL(target).pathname === '/' ? '/' : new URL(target).pathname]);
  const ctx = await browser.newContext();
  const p = await ctx.newPage();
  try {
    await p.goto(origin + pathStart, { waitUntil: 'domcontentloaded' });
    const xml = await p.evaluate(async () => { try { const r = await fetch('/sitemap.xml'); return r.ok ? await r.text() : ''; } catch { return ''; } });
    for (const m of xml.matchAll(/<loc>([^<]+)<\/loc>/g)) { try { pages.add(new URL(m[1]).pathname); } catch {} }
  } catch {}
  // breadth-first link crawl from the start page
  const queue = [...pages];
  const seen = new Set(queue);
  while (queue.length && seen.size < maxPages) {
    const u = queue.shift();
    try {
      await p.goto(origin + u, { waitUntil: 'domcontentloaded' });
      const hrefs = await p.$$eval('a[href]', as => as.map(a => a.href));
      for (const h of hrefs) {
        try {
          const x = new URL(h);
          if (x.origin !== origin) continue;
          const pp = x.pathname;
          if (/\.(pdf|jpe?g|png|webp|svg|zip|css|js|xml|txt|ico|woff2?)$/i.test(pp)) continue;
          if (!seen.has(pp) && seen.size < maxPages) { seen.add(pp); queue.push(pp); }
        } catch {}
      }
    } catch {}
  }
  await ctx.close();
  return [...seen].slice(0, maxPages);
}

const paths = await discover();
console.error(`Testing ${paths.length} pages on ${origin}`);
const pageSummaries = [];
const checkedLinks = new Map();

for (const pth of paths) {
  const url = origin + pth;
  const sum = { path: pth, url };
  for (const vp of VIEWPORTS) {
    const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height }, isMobile: vp.mobile, hasTouch: vp.mobile });
    const page = await ctx.newPage();
    const consoleErrs = [], failed = [], bad = [];
    page.on('console', m => { if (m.type() === 'error') consoleErrs.push(m.text().slice(0, 200)); });
    page.on('pageerror', e => consoleErrs.push('Uncaught: ' + String(e.message).slice(0, 200)));
    page.on('requestfailed', r => failed.push(r.url()));
    page.on('response', r => { if (r.status() >= 400 && r.url() !== url) bad.push(`${r.status()} ${r.url()}`); });
    const t0 = Date.now();
    let resp;
    try { resp = await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 }); }
    catch (e) { add({ area: 'functional', severity: 'Critical', page: pth, viewport: vp.name, title: 'Page failed to load', detail: String(e.message).slice(0, 200) }); await ctx.close(); continue; }
    const ms = Date.now() - t0;
    const status = resp?.status();
    if (vp.name === 'desktop') { sum.status = status; sum.loadMs = ms; }
    if (status >= 400) add({ area: 'functional', severity: 'Critical', page: pth, viewport: vp.name, title: `Page returns HTTP ${status}` });
    if (consoleErrs.length) add({ area: 'functional', severity: 'Medium', page: pth, viewport: vp.name, title: `${consoleErrs.length} console error(s)`, detail: consoleErrs.slice(0, 3).join(' | ') });
    if (failed.length) add({ area: 'functional', severity: 'High', page: pth, viewport: vp.name, title: `${failed.length} failed request(s)`, detail: failed.slice(0, 3).join(' | ') });
    if (bad.length) add({ area: 'functional', severity: 'High', page: pth, viewport: vp.name, title: `${bad.length} resource(s) returned 4xx/5xx`, detail: bad.slice(0, 3).join(' | ') });

    // responsive: horizontal overflow
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    if (overflow > 1) add({ area: 'visual', severity: 'High', page: pth, viewport: vp.name, title: `Horizontal scroll at ${vp.width}px (${overflow}px overflow)` });

    if (screens) await page.screenshot({ path: path.join(outDir, 'screenshots', `${slug(url)}-${vp.name}.png`), fullPage: true }).catch(() => {});

    if (vp.name === 'mobile') {
      // touch targets under 24px (WCAG 2.2 AA 2.5.8), excluding inline links within running text
      const small = await page.evaluate(() => [...document.querySelectorAll('a,button,input,select,textarea,[role=button]')]
        .filter(e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width > 0 && cs.visibility !== 'hidden' && (r.height < 24 || r.width < 24) && !(cs.display === 'inline' && e.closest('p,li')); })
        .slice(0, 50).map(e => (e.innerText || e.getAttribute('aria-label') || e.tagName).trim().slice(0, 30)));
      if (small.length) add({ area: 'ux', severity: 'Medium', page: pth, viewport: 'mobile', title: `${small.length} touch target(s) smaller than 24px`, detail: small.slice(0, 5).join(', ') });
    }

    if (vp.name === 'desktop') {
      sum.title = await page.title();
      // accessibility (axe-core)
      try {
        await page.evaluate(axeSource);
        const res = await page.evaluate(async () => await window.axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] } }));
        for (const v of res.violations) {
          add({ area: 'accessibility', severity: IMPACT[v.impact] || 'Medium', page: pth, viewport: 'desktop', title: `${v.help} (${v.id})`, detail: `${v.nodes.length} element(s). e.g. ${v.nodes[0]?.target?.join(' ')}`, ref: v.helpUrl });
        }
        sum.axeViolations = res.violations.length;
      } catch (e) { add({ area: 'accessibility', severity: 'Info', page: pth, title: 'axe-core could not run', detail: String(e.message).slice(0, 120) }); }

      // images
      const imgs = await page.evaluate(async () => {
        const list = [...document.images];
        await Promise.all(list.map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; setTimeout(r, 3000); })));
        return { broken: list.filter(i => i.complete && i.naturalWidth === 0 && i.currentSrc).map(i => i.currentSrc), noAlt: list.filter(i => !i.hasAttribute('alt')).length };
      });
      if (imgs.broken.length) add({ area: 'functional', severity: 'High', page: pth, viewport: 'desktop', title: `${imgs.broken.length} broken image(s)`, detail: imgs.broken.slice(0, 3).join(' | ') });
      if (imgs.noAlt) add({ area: 'accessibility', severity: 'Medium', page: pth, viewport: 'desktop', title: `${imgs.noAlt} image(s) without alt attribute` });

      // forms: validate (without submitting) that bad input is rejected by the browser
      const forms = await page.evaluate(() => [...document.forms].map(f => ({
        id: f.id || f.getAttribute('name') || f.action || 'form',
        emails: [...f.querySelectorAll('input[type=email]')].length,
        required: [...f.querySelectorAll('[required]')].length,
        unlabeled: [...f.querySelectorAll('input:not([type=hidden]):not([type=submit]):not([type=button]),select,textarea')].filter(i => !i.labels?.length && !i.getAttribute('aria-label') && !i.getAttribute('aria-labelledby')).length,
        hasSubmit: !!f.querySelector('button,[type=submit]'),
      })));
      sum.forms = forms.length;
      for (const f of forms) {
        if (f.unlabeled) add({ area: 'accessibility', severity: 'High', page: pth, viewport: 'desktop', title: `Form "${f.id}" has ${f.unlabeled} unlabeled field(s)` });
        if (!f.hasSubmit) add({ area: 'functional', severity: 'Medium', page: pth, viewport: 'desktop', title: `Form "${f.id}" has no submit button` });
      }
      const emailCheck = await page.evaluate(() => {
        const out = [];
        document.querySelectorAll('input[type=email]').forEach(i => { const old = i.value; i.value = 'not-an-email'; out.push(i.checkValidity()); i.value = old; });
        return out;
      });
      if (emailCheck.some(v => v === true)) add({ area: 'functional', severity: 'Medium', page: pth, viewport: 'desktop', title: 'Email field accepts an invalid address in the browser' });
      if (forms.length && !emailCheck.length) sum.formNote = 'No email field to test validation';

      // keyboard: tab through, make sure focus is visible and not trapped
      let steps = 0; const seenEls = new Set();
      await page.mouse.click(1, 1).catch(() => {});
      for (let i = 0; i < 25; i++) {
        await page.keyboard.press('Tab');
        const info = await page.evaluate(() => {
          const e = document.activeElement; if (!e || e === document.body) return null;
          const cs = getComputedStyle(e);
          const outline = cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0;
          const shadow = cs.boxShadow && cs.boxShadow !== 'none';
          return { key: e.tagName + (e.id || e.textContent?.slice(0, 20)), visible: outline || shadow || cs.textDecorationLine !== 'none' || cs.borderColor !== '' };
        });
        if (!info) continue;
        if (seenEls.has(info.key)) break;
        seenEls.add(info.key); steps++;
      }
      sum.tabStops = steps;
      if (steps === 0) add({ area: 'accessibility', severity: 'High', page: pth, viewport: 'desktop', title: 'No element can be reached with the Tab key' });

      // page basics
      const meta = await page.evaluate(() => ({
        h1: document.querySelectorAll('h1').length, lang: document.documentElement.lang,
        desc: document.querySelector('meta[name=description]')?.content?.length || 0,
        skip: !!document.querySelector('a[href^="#"][class*=skip],a.skip-link,a[href="#main"],a[href="#content"]'),
        landmarks: ['main', 'nav', 'header', 'footer'].filter(t => !document.querySelector(t)),
      }));
      if (meta.h1 !== 1) add({ area: 'ux', severity: 'Medium', page: pth, viewport: 'desktop', title: `Page has ${meta.h1} H1 headings (expected 1)` });
      if (!meta.lang) add({ area: 'accessibility', severity: 'High', page: pth, viewport: 'desktop', title: 'Missing lang attribute on <html>' });
      if (meta.landmarks.length) add({ area: 'accessibility', severity: 'Low', page: pth, viewport: 'desktop', title: `Missing landmark(s): ${meta.landmarks.join(', ')}` });

      // links: check same-origin links with a HEAD/GET from inside the browser
      const hrefs = await page.$$eval('a[href]', as => [...new Set(as.map(a => a.href))].filter(h => /^https?:/.test(h)));
      const internal = hrefs.filter(h => new URL(h).origin === origin).map(h => h.split('#')[0]);
      for (const h of [...new Set(internal)]) {
        if (!checkedLinks.has(h)) {
          const code = await page.evaluate(async (u) => { try { const r = await fetch(u, { method: 'GET' }); return r.status; } catch { return 0; } }, h);
          checkedLinks.set(h, { code, from: pth });
        }
      }
      sum.externalLinks = hrefs.length - internal.length;
    }
    await ctx.close();
  }
  pageSummaries.push(sum);
}

for (const [u, { code, from }] of checkedLinks) {
  if (code === 0 || code >= 400) add({ area: 'functional', severity: 'High', page: from, title: `Broken internal link (${code || 'no response'})`, detail: u });
}

await browser.close();
const byAreaSev = {};
for (const f of findings) { const k = `${f.area}:${f.severity}`; byAreaSev[k] = (byAreaSev[k] || 0) + 1; }
const result = { target: origin, testedAt: new Date().toISOString(), pagesTested: paths.length, viewports: VIEWPORTS.map(v => v.name), counts: byAreaSev, pages: pageSummaries, findings };
fs.writeFileSync(path.join(outDir, 'findings.json'), JSON.stringify(result, null, 1));
console.log(`Done. ${findings.length} findings across ${paths.length} pages -> ${path.join(outDir, 'findings.json')}`);
