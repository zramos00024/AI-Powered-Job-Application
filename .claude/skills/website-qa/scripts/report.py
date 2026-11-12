#!/usr/bin/env python3
"""Build QA-REPORT.md from qa_run.mjs + Lighthouse output.
Usage: report.py <out-dir> [--extra findings.json ...] [--fail-on Critical|High]
Extra files hold a JSON list of findings: {area,severity,title,detail?,page?}. Use them for SEO,
security (ZAP), API (Schemathesis) or manual findings. Exit code 1 when the release gate fails."""
import json, re, sys, os, collections

SEV = ["Critical", "High", "Medium", "Low", "Info"]
AREAS = {"functional": "Functional", "visual": "Visual / responsive", "accessibility": "Accessibility", "ux": "UI/UX",
         "performance": "Performance", "seo": "SEO", "security": "Security", "api": "API", "general": "General"}
PLAIN = {  # short plain-English fix hints for frequent findings
    "color-contrast": "Darken text or lighten the background until contrast is at least 4.5:1 (3:1 for large text).",
    "link-in-text-block": "Underline links inside paragraphs, or give them at least 3:1 contrast against surrounding text.",
    "landmark-complementary-is-top-level": "Move the <aside> out of other landmarks such as <main>, or use a different element.",
    "heading-order": "Do not skip heading levels (h2 straight to h4). Restyle with CSS instead.",
    "touch target": "Add padding so links and buttons are at least 24x24 px (44x44 px is more comfortable).",
    "Horizontal scroll": "Find the element wider than the viewport and constrain it (max-width: 100%, overflow-wrap).",
    "broken": "Fix or remove the link or file reference.",
    "console error": "Open DevTools on that page and fix the reported script or resource error.",
}

def args(flag):
    out, a = [], sys.argv
    for i, x in enumerate(a):
        if x == flag and i + 1 < len(a):
            out.append(a[i + 1])
    return out

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d = sys.argv[1]
    data = json.load(open(os.path.join(d, "findings.json")))
    findings = list(data["findings"])
    for f in args("--extra"):
        findings += json.load(open(f))
    fail_on = (args("--fail-on") or ["High"])[0]
    gate_levels = SEV[: SEV.index(fail_on) + 1]

    # group identical findings across pages/viewports
    groups = collections.OrderedDict()
    for f in findings:
        key = (f.get("area", "general"), f["severity"], re.sub(r"\d+", "N", f["title"]))
        g = groups.setdefault(key, {"f": f, "pages": set(), "views": set(), "n": 0})
        g["pages"].add(f.get("page", "(site)")); g["views"].add(f.get("viewport", "")); g["n"] += 1
    rows = sorted(groups.values(), key=lambda g: (SEV.index(g["f"]["severity"]), -len(g["pages"])))

    sev_count = collections.Counter(f["severity"] for f in findings)
    area_sev = collections.defaultdict(collections.Counter)
    for f in findings:
        area_sev[f.get("area", "general")][f["severity"]] += 1

    lh = {}
    for p in ("mobile", "desktop"):
        fp = os.path.join(d, f"lighthouse-{p}.json")
        if os.path.exists(fp):
            j = json.load(open(fp)); c = j["categories"]; a = j["audits"]
            lh[p] = {"scores": {k: round((v["score"] or 0) * 100) for k, v in c.items()},
                     "lcp": a["largest-contentful-paint"]["displayValue"], "cls": a["cumulative-layout-shift"]["displayValue"],
                     "tbt": a["total-blocking-time"]["displayValue"], "fcp": a["first-contentful-paint"]["displayValue"]}
            for k, v in lh[p]["scores"].items():
                if v < 90:
                    rows.append({"f": {"area": "performance" if k == "performance" else k, "severity": "Medium" if v >= 50 else "High",
                                       "title": f"Lighthouse {k} score {v}/100 on {p}"}, "pages": {"/"}, "views": {p}, "n": 1})

    blockers = [g for g in rows if g["f"]["severity"] in gate_levels]
    L = []
    L.append(f"# Website QA report: {data['target']}\n")
    L.append(f"Tested {data['testedAt'][:10]} · {data['pagesTested']} pages · viewports: {', '.join(data['viewports'])}\n")
    verdict = "FAIL: release blocked" if blockers else "PASS"
    L.append(f"## Release gate: **{verdict}**\n")
    L.append(f"Gate rule: any finding rated {' or '.join(gate_levels)} blocks release. {len(blockers)} distinct issue(s) match.\n")
    L.append("| Severity | Findings |\n|---|---|")
    for s in SEV:
        if sev_count[s]:
            L.append(f"| {s} | {sev_count[s]} |")
    L.append("\n## By area\n\n| Area | " + " | ".join(SEV[:4]) + " |\n|---|" + "---|" * 4)
    for a, c in area_sev.items():
        L.append(f"| {AREAS.get(a, a)} | " + " | ".join(str(c[s]) for s in SEV[:4]) + " |")
    if lh:
        L.append("\n## Lighthouse\n\n| | Perf | Access. | Best pract. | SEO | LCP | CLS | TBT |\n|---|---|---|---|---|---|---|---|")
        for p, v in lh.items():
            s = v["scores"]
            L.append(f"| {p} | {s.get('performance')} | {s.get('accessibility')} | {s.get('best-practices')} | {s.get('seo')} | {v['lcp']} | {v['cls']} | {v['tbt']} |")
    L.append("\n## Issues to fix (grouped, worst first)\n")
    for i, g in enumerate(rows, 1):
        f = g["f"]; pages = sorted(g["pages"])
        hint = next((v for k, v in PLAIN.items() if k.lower() in (f["title"] + f.get("detail", "")).lower()), "")
        where = f"{len(pages)} page(s)" if len(pages) > 3 else ", ".join(pages)
        L.append(f"### {i}. [{f['severity']}] {f['title']}")
        L.append(f"- Area: {AREAS.get(f.get('area', 'general'))} · Where: {where} · Viewport: {', '.join(sorted(v for v in g['views'] if v)) or 'n/a'}")
        if f.get("detail"): L.append(f"- Evidence: {f['detail'][:300]}")
        if hint: L.append(f"- Fix: {hint}")
        if f.get("ref"): L.append(f"- Reference: {f['ref']}")
        L.append("")
    L.append("## Evidence\n\nScreenshots at desktop, tablet and mobile widths are in `screenshots/`, named `<page>-<viewport>.png`.\n")
    L.append("## What this report does not cover\n\nAutomated checks only. A person should still review whether the design is intuitive, test real user journeys that need login or payment, and run security (ZAP) and API (Schemathesis) scans against a staging environment you own.\n")
    out = os.path.join(d, "QA-REPORT.md")
    open(out, "w").write("\n".join(L))
    print(f"{verdict}: {len(rows)} grouped issues, {len(blockers)} blocking -> {out}")
    sys.exit(1 if blockers else 0)

main()
