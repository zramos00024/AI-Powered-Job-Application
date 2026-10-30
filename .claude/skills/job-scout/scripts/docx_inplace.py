#!/usr/bin/env python3
"""Edit text of a candidate's own .docx in place, keeping its layout.

  dump  <in.docx>                      list paragraphs: index, editable?, text
  apply <in.docx> <edits.json> <out.docx>

edits.json maps paragraph index -> new text. A paragraph whose text runs all share
one format takes a string. A paragraph with mixed formats (bold label + plain text)
takes a list with one string per text run. The input file is never modified.

Safety limits, enforced (apply stops and writes nothing if any is broken):
  - text only: no adding or removing paragraphs, so styles, bullets, tables, margins stay put
  - refuses paragraphs holding hyperlinks, fields, images, content controls
  - new text may not be more than --max-growth (default 1.25x) longer than the original
  - after saving, every untouched paragraph must be identical to the original
Not covered: text boxes, headers/footers, tracked changes. Check page count by eye.
"""
import argparse, json, sys
from docx import Document
from docx.oxml.ns import qn

RISKY = ("w:hyperlink", "w:fldSimple", "w:fldChar", "w:drawing", "w:pict", "w:sdt", "w:ins", "w:del")


def iter_paragraphs(doc):
    """Body paragraphs, then table cell paragraphs, in a stable order."""
    for p in doc.paragraphs:
        yield p
    for t in doc.tables:
        for row in t.rows:
            seen = set()
            for cell in row.cells:
                if id(cell._tc) in seen:
                    continue
                seen.add(id(cell._tc))
                yield from cell.paragraphs


def risky(p):
    return any(p._p.findall(".//" + qn(tag)) for tag in RISKY)


def text_runs(p):
    return [r for r in p.runs if r.text]


def uniform(runs):
    fmt = lambda r: str(r._r.rPr.xml) if r._r.rPr is not None else ""
    return len({fmt(r) for r in runs}) <= 1


def editable(p):
    return bool(text_runs(p)) and not risky(p)


def dump(path):
    doc = Document(path)
    return [{"index": i, "editable": editable(p), "runs": len(text_runs(p)),
             "uniform": uniform(text_runs(p)), "text": p.text}
            for i, p in enumerate(iter_paragraphs(doc))]


def apply_edits(src, edits, out, max_growth=1.25):
    doc = Document(src)
    paras = list(iter_paragraphs(doc))
    before = [p.text for p in paras]
    for key, new in edits.items():
        i = int(key)
        if not 0 <= i < len(paras):
            raise ValueError(f"paragraph {i} does not exist")
        p, runs = paras[i], text_runs(paras[i])
        if not editable(p):
            raise ValueError(f"paragraph {i} is not safe to edit (empty, link, field or image)")
        parts = new if isinstance(new, list) else [new]
        if isinstance(new, str) and not uniform(runs):
            raise ValueError(f"paragraph {i} has mixed formatting: give a list of {len(runs)} strings")
        if isinstance(new, list) and len(parts) != len(runs):
            raise ValueError(f"paragraph {i} has {len(runs)} text runs, got {len(parts)} strings")
        old_len = len(before[i])
        if len("".join(parts)) > max(old_len * max_growth, old_len + 20):
            raise ValueError(f"paragraph {i} grows too much ({old_len} -> {len(''.join(parts))} chars)")
        if isinstance(new, str):  # uniform: put all text in the first run, empty the rest
            parts = [new] + [""] * (len(runs) - 1)
        for r, t in zip(runs, parts):
            r.text = t
    doc.save(out)
    after = [p.text for p in iter_paragraphs(Document(out))]
    if len(after) != len(before):
        raise RuntimeError("paragraph count changed")
    for i, (b, a) in enumerate(zip(before, after)):
        if str(i) not in {str(k) for k in edits} and a != b:
            raise RuntimeError(f"untouched paragraph {i} changed")
    return len(edits)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dump"); d.add_argument("docx")
    e = sub.add_parser("apply"); e.add_argument("docx"); e.add_argument("edits"); e.add_argument("out")
    e.add_argument("--max-growth", type=float, default=1.25)
    a = ap.parse_args(argv)
    if a.cmd == "dump":
        print(json.dumps(dump(a.docx), indent=1))
        return 0
    try:
        n = apply_edits(a.docx, json.load(open(a.edits, encoding="utf-8")), a.out, a.max_growth)
    except (ValueError, RuntimeError) as err:
        print("refused:", err, file=sys.stderr)
        return 1
    print(f"edited {n} paragraphs -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
