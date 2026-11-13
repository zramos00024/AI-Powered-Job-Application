#!/usr/bin/env python3
"""Builds design-1.html … design-5.html from src/original.html.

The visible copy is never retyped: every design is the original <body> markup with
hooks (ids, data attributes, wrappers) added by the substitutions below. `python3
build.py --check` proves the rendered text of each design matches the original.
"""
import hashlib, html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
SITE = "https://www.infotechconsultancy.io/"

DESIGNS = {
    1: dict(name="Harbour", theme="#f6f4ef", fonts=["jakarta", "inter"], logo="logo"),
    2: dict(name="Control Room", theme="#0a0d12", fonts=["jakarta", "inter", "jbmono"], logo="logo-white"),
    3: dict(name="Broadsheet", theme="#f3eee3", fonts=["fraunces", "inter"], logo="logo"),
    4: dict(name="Stack", theme="#ece7dc", fonts=["bricolage", "inter"], logo="logo"),
    5: dict(name="Two Hubs", theme="#f7f6f1", fonts=["jakarta", "inter"], logo="logo"),
}

TITLE = "Infotech Consultancy | Technology Consulting &amp; Services, Australia &amp; India"
# Trimmed to fit a search snippet (the original ran to 255 characters and was truncated).
DESC = ("Australian-headquartered technology consulting and services company with a dedicated "
        "Offshore Delivery Centre in Hyderabad, India. Established in Sydney in 2013.")

SECTION_IDS = ["top", "clients", "services", "delivery-models", "why-infotech",
               "case-studies", "global-delivery", "industries", "careers", "contact"]


def sub1(s, old, new, count=1):
    assert s.count(old) >= count, f"hook not found: {old[:70]!r}"
    return s.replace(old, new) if count != 1 else s.replace(old, new, 1)


def json_ld(body):
    org = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',
                               (SRC / "original.html").read_text(), re.S).group(1))
    org["@id"] = SITE + "#organization"
    org["image"] = SITE + "assets/img/og-image.jpg"
    services = re.findall(r'<a class="svc-row" href="([^"]+)"><span class="num">\d+</span>'
                          r'<span class="t">(.*?)</span><span class="d">(.*?)</span>', body)
    org["hasOfferCatalog"] = {
        "@type": "OfferCatalog", "name": "Core technology capabilities",
        "itemListElement": [{"@type": "Offer", "itemOffered": {
            "@type": "Service", "name": html.unescape(t), "description": html.unescape(d),
            "url": SITE + href, "provider": {"@id": org["@id"]}}} for href, t, d in services]}
    site = {"@type": "WebSite", "@id": SITE + "#website", "url": SITE,
            "name": "Infotech Consultancy", "inLanguage": "en-AU", "publisher": {"@id": org["@id"]}}
    org.pop("@context")
    return json.dumps({"@context": "https://schema.org", "@graph": [org, site]},
                      ensure_ascii=False, separators=(",", ":"))


def head(n, cfg, body):
    preload = "\n".join(
        f'<link rel="preload" href="assets/fonts/{f}.woff2" as="font" type="font/woff2" crossorigin>'
        for f in cfg["fonts"])
    return f"""<!doctype html>
<html lang="en-AU" class="no-js d{n}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Client preview: remove the robots noindex tag below at go-live -->
<meta name="robots" content="noindex">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{SITE}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Infotech Consultancy">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="{SITE}assets/img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Infotech Consultancy">
<meta property="og:locale" content="en_AU">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{SITE}assets/img/og-image.jpg">
<meta name="theme-color" content="{cfg['theme']}">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<script>document.documentElement.className=document.documentElement.className.replace('no-js','js')</script>
{preload}
<link rel="preload" as="image" type="image/avif" fetchpriority="high" imagesrcset="assets/img/og-default-640.avif 640w, assets/img/og-default-960.avif 960w, assets/img/og-default-1280.avif 1280w" imagesizes="(min-width: 980px) 45vw, 100vw">
<link rel="stylesheet" href="assets/css/d{n}.css?v={cfg['css_v']}">
<script type="application/ld+json">{json_ld(body)}</script>
<script type="speculationrules">{{"prefetch":[{{"where":{{"and":[{{"href_matches":"/*"}},{{"not":{{"selector_matches":"[target=_blank]"}}}}]}},"eagerness":"moderate"}}]}}</script>
</head>
"""


def common(body, cfg):
    # --- section hooks -------------------------------------------------------
    parts = re.split(r"(<section class=\")", body)
    out, i = [parts[0]], 0
    for j in range(1, len(parts), 2):
        out.append(f'<section id="{SECTION_IDS[i]}" data-sec class="s-{SECTION_IDS[i]} ')
        out.append(parts[j + 1])
        i += 1
    assert i == len(SECTION_IDS), i
    body = "".join(out)

    # --- scroll progress + reveal hooks --------------------------------------
    body = sub1(body, '<a class="skip" href="#main">Skip to content</a>',
                '<a class="skip" href="#main">Skip to content</a>\n<div class="progress" aria-hidden="true"></div>')
    body = body.replace(" reveal\"", "\" data-rv")
    for cls in ("eyebrow", "section-head", "svc-row", "muted-label", "dark-note", "model-list", "logo-strip"):
        body = body.replace(f'class="{cls}"', f'class="{cls}" data-rv')
    body = body.replace('class="section-head row-head"', 'class="section-head row-head" data-rv')

    # --- hero: AVIF with WebP fallback, LCP image decoded synchronously -------
    old_img = re.search(r'<img src="assets/img/og-default-1280\.webp"[^>]*>', body).group(0)
    new_img = ('<picture><source type="image/avif" srcset="assets/img/og-default-640.avif 640w, '
               'assets/img/og-default-960.avif 960w, assets/img/og-default-1280.avif 1280w" '
               'sizes="(min-width: 980px) 45vw, 100vw">'
               '<img src="assets/img/og-default-1280.webp" srcset="assets/img/og-default-640.webp 640w, '
               'assets/img/og-default-960.webp 960w, assets/img/og-default-1280.webp 1280w" '
               'sizes="(min-width: 980px) 45vw, 100vw" width="1280" height="853" '
               'alt="Office towers in a central business district" fetchpriority="high"></picture>')
    body = body.replace(old_img, new_img)
    body = sub1(body, '<h1>', '<h1 data-split>')

    # --- srcset fixes: width descriptors must be unique and true ---------------
    body = sub1(body, 'srcset="assets/img/cs-optus-lead-640.webp 640w, assets/img/cs-optus-lead-1280.webp 640w" ', '')
    body = sub1(body, 'src="assets/img/cs-optus-lead-1280.webp"', 'src="assets/img/cs-optus-lead-640.webp"')
    body = body.replace('sizes="(min-width: 900px) 33vw, 100vw"', 'sizes="(min-width: 1000px) 400px, (min-width: 660px) 50vw, 100vw"')

    # --- stats count up (final values stay in the HTML) ------------------------
    body = sub1(body, '<div class="stats">', '<div class="stats" data-rv>')
    for v in ("2013", "150+", "&lt;3%", "2 hubs"):
        body = sub1(body, f"<div><strong>{v}</strong>", f"<div><strong data-count>{v}</strong>")

    body = sub1(body, 'src="assets/img/logo.webp" width="309" height="120" alt="Infotech Consultancy"',
                f'src="assets/img/{cfg["logo"]}.webp" width="309" height="120" alt="Infotech Consultancy" decoding="async"')
    return body


# ---------------------------------------------------------------- per design
def d1(b):
    b = sub1(b, '<div class="hero-media">', '<div class="hero-media" data-tilt>')
    b = sub1(b, '<div class="media-frame" data-rv', '<div class="media-frame" data-rv data-wipe')
    b = b.replace('<article class="case-card"', '<article data-tilt class="case-card"')
    b = sub1(b, '<div class="cta-band" data-rv>', '<div class="cta-band" data-p>')
    return b


def d2(b):
    b = sub1(b, '<p class="dark-note" data-rv>', '<p class="dark-note" data-scrub>')
    b = b.replace('<div class="feature" data-rv>', '<div class="feature" data-rv data-spot>')
    b = b.replace('<a class="ind-tile" data-rv', '<a class="ind-tile" data-rv data-spot')
    b = b.replace('<span class="t">', '<span class="t" data-scramble>')
    # the case studies become a pinned track that travels sideways while the page scrolls
    b = sub1(b, '<div class="section-head row-head" data-rv>', '<div class="pin" data-pin><div class="pin-sticky"><div class="section-head row-head">')
    b = sub1(b, '<div class="grid g3"><article', '<div class="grid g3 pin-track"><article')
    b = sub1(b, '</article></div>\n</div></section>', '</article></div></div></div>\n</div></section>')
    b = b.replace('<article class="case-card" data-rv', '<article data-spot class="case-card"')
    return b


def d3(b):
    b = sub1(b, '<p class="dark-note" data-rv>', '<p class="dark-note" data-scrub>')
    return b


def d4(b):
    b = b.replace('<a class="btn btn-primary"', '<a data-magnetic class="btn btn-primary"')
    return b


def d5(b):
    b = sub1(b, '<main id="main">', '<main id="main"><svg class="route" aria-hidden="true" focusable="false" preserveAspectRatio="none"><path class="route-bg"/><path class="route-fg"/></svg><span class="route-dot" aria-hidden="true"></span>')
    b = sub1(b, '<ul class="svc-list">', '<ul class="svc-list" data-active-list>')
    b = sub1(b, '<ul class="model-list" data-rv>', '<ul class="model-list" data-p>')
    b = sub1(b, '<div class="ind-tiles">', '<div class="ind-tiles" data-p>')
    b = b.replace('<a class="ind-tile" data-rv', '<a class="ind-tile"')
    return b


PER = {1: d1, 2: d2, 3: d3, 4: d4, 5: d5}


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    css = re.sub(r":\s+", ":", css)
    return css.replace(";}", "}").strip()


def visible_text(doc):
    doc = doc[doc.index("<body"):]
    doc = re.sub(r"<(script|style)\b.*?</\1>", "", doc, flags=re.S)
    doc = re.sub(r"<[^>]+>", "\n", doc)
    return [t for t in (re.sub(r"\s+", " ", html.unescape(x)).strip() for x in doc.split("\n")) if t]


def main():
    original = (SRC / "original.html").read_text()
    body0 = original[original.index("<body>"):]
    base_css, core_js = (SRC / "base.css").read_text(), (SRC / "core.js").read_text()
    want = visible_text(original)
    for n, cfg in DESIGNS.items():
        css = minify_css(base_css + (SRC / f"d{n}.css").read_text())
        extra = SRC / f"d{n}.js"
        js = core_js + ("\n" + extra.read_text() if extra.exists() else "")
        # content hashes let the assets be cached for a year (see vercel.json)
        cfg["css_v"], js_v = (hashlib.sha1(x.encode()).hexdigest()[:8] for x in (css, js))
        body = PER[n](common(body0, cfg))
        body = sub1(body, '<script src="assets/js/main.js" defer></script>', f'<script src="assets/js/d{n}.js?v={js_v}" defer onerror="document.documentElement.className=\'no-js\'"></script>')
        page = head(n, cfg, body0) + body
        (ROOT / f"design-{n}.html").write_text(page)
        (ROOT / "assets/css" / f"d{n}.css").write_text(css)
        (ROOT / "assets/js" / f"d{n}.js").write_text(js)
        got = visible_text(page)
        status = "copy identical" if got == want else "COPY DIFFERS"
        print(f"design-{n}.html  {cfg['name']:<13} {len(page):>6} B html  "
              f"{(ROOT / 'assets/css' / f'd{n}.css').stat().st_size:>6} B css  {status}")
        if got != want and "--check" in sys.argv:
            for a, c in zip(want, got):
                if a != c:
                    print("  want:", a, "\n  got: ", c)
                    break
            sys.exit(1)


if __name__ == "__main__":
    main()
