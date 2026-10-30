#!/usr/bin/env python3
"""Pick the closest sample resume for a job by title and keyword overlap.

Each sample is a markdown file in the resumes folder that starts with a header block:

    Role family: Head of Support
    Target titles: Head of Support; Director of Customer Support
    Keywords: escalation management, SLA, team leadership

    # Full Name
    ...

Score is 0-100: up to 60 points for title match (best target title vs job title,
Dice overlap of words) and up to 40 for the share of the sample's keywords found
in the job description. Below --min-score nothing is chosen (match is null).
Standard library only.
"""
import argparse, json, os, re, sys

TITLE_WEIGHT, KEYWORD_WEIGHT = 60, 40
STOP = {"a", "an", "and", "at", "for", "in", "of", "on", "or", "the", "to", "with", "-", "&"}


def norm(text):
    return re.sub(r"[^a-z0-9+#/ ]+", " ", text.lower())


def stem(w):
    return w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w


def tokens(text):
    return {stem(w) for w in norm(text).split() if w not in STOP}


def split_list(value):
    return [p.strip() for p in re.split(r"[;,\n]", value) if p.strip()]


def parse_header(text):
    """Return {role_family, titles, keywords} from the lines above the first '# ' heading."""
    out = {"role_family": "", "titles": [], "keywords": []}
    for line in text.splitlines():
        if line.startswith("# "):
            break
        m = re.match(r"\s*(role family|target titles?|keywords?)\s*:\s*(.*)", line, re.I)
        if not m:
            continue
        key, val = m.group(1).lower(), m.group(2)
        if key == "role family":
            out["role_family"] = val.strip()
        elif key.startswith("target"):
            out["titles"] = split_list(val)
        else:
            out["keywords"] = split_list(val)
    return out


def title_score(job_title, targets):
    """0..1: best Dice overlap between the job title and any target title."""
    jt = tokens(job_title)
    best = 0.0
    for t in targets:
        tt = tokens(t)
        if jt and tt:
            best = max(best, 2 * len(jt & tt) / (len(jt) + len(tt)))
    return best


def keyword_hits(description, keywords):
    """Keywords found in the description (whole word or phrase, case-insensitive)."""
    text = norm(description)
    hits = []
    for k in keywords:
        pat = r"(?<![a-z0-9])" + re.escape(norm(k).strip()) + r"s?(?![a-z0-9])"
        if re.search(pat, text):
            hits.append(k)
    return hits


def score(sample, job_title, description):
    ts = title_score(job_title, sample["titles"])
    hits = keyword_hits(description, sample["keywords"])
    ks = len(hits) / len(sample["keywords"]) if sample["keywords"] else 0.0
    return {
        "file": sample["file"],
        "role_family": sample["role_family"],
        "score": round(TITLE_WEIGHT * ts + KEYWORD_WEIGHT * ks, 1),
        "title_match": round(ts, 2),
        "keyword_hits": hits,
        "keyword_total": len(sample["keywords"]),
    }


def load_samples(folder):
    samples = []
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(folder, name), encoding="utf-8") as f:
            h = parse_header(f.read())
        h["file"] = name
        samples.append(h)
    return samples


def pick(samples, job_title, description, min_score=40.0):
    """Rank samples. 'match' is the best one, or None if it scores under min_score."""
    ranked = sorted((score(s, job_title, description) for s in samples),
                    key=lambda r: (-r["score"], r["file"]))
    best = ranked[0] if ranked else None
    ok = best is not None and best["score"] >= min_score
    if not samples:
        reason = "no sample resumes found"
    elif ok:
        reason = (f"title match {best['title_match']:.0%}, "
                  f"{len(best['keyword_hits'])}/{best['keyword_total']} keywords "
                  f"({', '.join(best['keyword_hits']) or 'none'})")
    else:
        reason = f"best score {best['score']} is under the minimum {min_score}; no sample is close enough"
    return {"match": best["file"] if ok else None, "reason": reason,
            "min_score": min_score, "ranked": ranked}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--resumes-dir", default="profile/resumes")
    ap.add_argument("--job-title", required=True)
    ap.add_argument("--jd-file", help="job description text file (default: read stdin)")
    ap.add_argument("--min-score", type=float, default=40.0)
    a = ap.parse_args(argv)
    if not os.path.isdir(a.resumes_dir):
        print(json.dumps({"match": None, "reason": f"{a.resumes_dir} not found", "ranked": []}))
        return 0
    jd = open(a.jd_file, encoding="utf-8").read() if a.jd_file else sys.stdin.read()
    print(json.dumps(pick(load_samples(a.resumes_dir), a.job_title, jd, a.min_score), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
