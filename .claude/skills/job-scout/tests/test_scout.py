"""Run: python3 -m unittest discover -s .claude/skills/job-scout/tests -v   (from the repo root)"""
import datetime as dt, json, os, sys, tempfile, unittest
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
SAMPLES = os.path.join(HERE, "..", "..", "..", "..", "profile", "resumes.example")

import pick_resume as pr
import run_window as rw

HEAD_JD = """Head of Customer Support. Own our support strategy and lead the team through
hiring and coaching. You manage escalation management, SLA targets and CSAT."""
MGR_JD = """Support Manager for our service desk. Daily queue management, shift scheduling,
coaching agents, maintaining the knowledge base and weekly KPIs."""
UNRELATED_JD = "Senior Java developer building payment microservices with Kafka and Kubernetes."


class PickResume(unittest.TestCase):
    def setUp(self):
        self.samples = pr.load_samples(SAMPLES)

    def test_header_parsed(self):
        h = pr.parse_header("Role family: X\nTarget titles: A b; C d\nKeywords: k1, k 2\n\n# Name\nKeywords: ignored")
        self.assertEqual(h["role_family"], "X")
        self.assertEqual(h["titles"], ["A b", "C d"])
        self.assertEqual(h["keywords"], ["k1", "k 2"])

    def test_picks_head_of_support(self):
        r = pr.pick(self.samples, "Head of Customer Support", HEAD_JD)
        self.assertEqual(r["match"], "head-of-support.md")

    def test_picks_support_manager(self):
        r = pr.pick(self.samples, "Customer Support Manager", MGR_JD)
        self.assertEqual(r["match"], "support-manager.md")

    def test_no_forced_match(self):
        r = pr.pick(self.samples, "Senior Java Developer", UNRELATED_JD)
        self.assertIsNone(r["match"])
        self.assertIn("no sample is close enough", r["reason"])

    def test_no_samples(self):
        r = pr.pick([], "Support Manager", MGR_JD)
        self.assertIsNone(r["match"])

    def test_keyword_whole_word(self):
        self.assertEqual(pr.keyword_hits("we use SLAs daily", ["SLA"]), ["SLA"])
        self.assertEqual(pr.keyword_hits("islands", ["SLA"]), [])

    def test_deterministic_tie(self):
        a = {"file": "b.md", "role_family": "", "titles": [], "keywords": []}
        b = dict(a, file="a.md")
        self.assertEqual(pr.pick([a, b], "x", "y", min_score=0)["match"], "a.md")

    def test_cli_missing_dir(self):
        self.assertEqual(pr.main(["--resumes-dir", "/nonexistent", "--job-title", "x", "--jd-file", os.devnull]), 0)


class RunWindow(unittest.TestCase):
    PREFS = {"timezone": "Australia/Sydney",
             "run_window": {"days": ["mon", "tue", "wed", "thu", "fri"], "start": "06:00", "end": "17:00", "grace_minutes": 10},
             "alerts": {"alert_mode": "instant_plus_digest", "digest_times": ["12:00", "17:00"]}}

    def at(self, y, mo, d, h, mi, tz="Australia/Sydney"):
        return dt.datetime(y, mo, d, h, mi, tzinfo=ZoneInfo(tz)).astimezone(dt.timezone.utc)

    def test_inside(self):  # Wed 2026-11-04 10:00 Sydney
        self.assertIsNotNone(rw.decide(self.at(2026, 11, 4, 10, 0), self.PREFS, {}))

    def test_before_and_after(self):
        self.assertIsNone(rw.decide(self.at(2026, 11, 4, 5, 59), self.PREFS, {}))
        self.assertIsNone(rw.decide(self.at(2026, 11, 4, 17, 11), self.PREFS, {}))

    def test_edges(self):
        self.assertIsNotNone(rw.decide(self.at(2026, 11, 4, 6, 0), self.PREFS, {}))
        self.assertIsNotNone(rw.decide(self.at(2026, 11, 4, 17, 0), self.PREFS, {}))

    def test_weekend(self):  # Sat 2026-11-07
        self.assertIsNone(rw.decide(self.at(2026, 11, 7, 10, 0), self.PREFS, {}))

    def test_timezone_matters(self):
        # same instant: 10:00 Sydney is 09:00 Brisbane (no DST) in Nov, both inside; 06:30 Brisbane is 07:30 Sydney
        p = dict(self.PREFS, timezone="Australia/Brisbane")
        self.assertIsNone(rw.decide(self.at(2026, 11, 4, 5, 30, "Australia/Brisbane"), p, {}))
        self.assertIsNotNone(rw.decide(self.at(2026, 11, 4, 5, 30, "Australia/Brisbane"), self.PREFS, {}))

    def test_dst_is_followed(self):
        # 2026-06-03 (AEST, UTC+10) vs 2026-11-04 (AEDT, UTC+11): 06:00 local both times, different UTC.
        a, b = self.at(2026, 6, 3, 6, 0), self.at(2026, 11, 4, 6, 0)
        self.assertEqual((a.hour, b.hour), (20, 19))
        self.assertIsNotNone(rw.decide(a, self.PREFS, {}))
        self.assertIsNotNone(rw.decide(b, self.PREFS, {}))
        # a cron fixed in UTC drifts: 19:00 UTC is 05:00 in winter (outside) but 06:00 in summer
        self.assertIsNone(rw.decide(self.at(2026, 6, 3, 5, 0), self.PREFS, {}))

    def test_digest_slots(self):
        d = lambda h, sent=(): rw.decide(self.at(2026, 11, 4, h, 0), self.PREFS,
                                         {"digests_sent": {"2026-11-04": list(sent)}})["digest_due"]
        self.assertIsNone(d(10))
        self.assertEqual(d(12), "12:00")
        self.assertIsNone(d(12, ["12:00"]))
        self.assertEqual(d(14), "12:00")          # missed slot is picked up by the next run
        self.assertEqual(d(17, ["12:00"]), "17:00")

    def test_per_run_has_no_digest(self):
        p = dict(self.PREFS, alerts={"alert_mode": "per_run"})
        self.assertIsNone(rw.decide(self.at(2026, 11, 4, 12, 0), p, {})["digest_due"])

    def test_cli_exit_codes(self):
        import yaml
        with tempfile.TemporaryDirectory() as d:
            pf, sf = os.path.join(d, "p.yaml"), os.path.join(d, "s.json")
            with open(pf, "w") as f: yaml.safe_dump(self.PREFS, f)
            args = lambda t, *x: ["--prefs", pf, "--state", sf, "--now", t, *x]
            self.assertEqual(rw.main(args("2026-11-04T10:00:00+11:00")), 0)
            self.assertEqual(rw.main(args("2026-11-04T20:00:00+11:00")), rw.OUTSIDE)
            self.assertEqual(rw.main(args("2026-11-04T12:00:00+11:00", "--mark-digest-sent", "12:00")), 0)
            with open(sf) as f: self.assertEqual(json.load(f)["digests_sent"], {"2026-11-04": ["12:00"]})


try:
    import docx
    from docx.shared import Pt
    import docx_inplace as di
    HAVE_DOCX = True
except ImportError:
    HAVE_DOCX = False


@unittest.skipUnless(HAVE_DOCX, "python-docx not installed")
class DocxInplace(unittest.TestCase):
    def make(self, d):
        doc = docx.Document()
        doc.add_paragraph("Sample Candidate")
        doc.add_paragraph("Head of Support, Customer Operations")
        p = doc.add_paragraph(); p.add_run("Label: ").bold = True; p.add_run("plain text here")
        doc.add_paragraph("Led a support team across regions.", style="List Bullet")
        doc.add_paragraph("Second bullet about SLA reporting.", style="List Bullet")
        t = doc.add_table(rows=1, cols=1); t.cell(0, 0).text = "In a table cell"
        path = os.path.join(d, "in.docx"); doc.save(path); return path

    def test_edit_keeps_layout(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = self.make(d), os.path.join(d, "out.docx")
            di.apply_edits(src, {"1": "Support Manager, Service Desk",
                                 "2": ["Label: ", "other text"], "3": "Led a team across regions."}, out)
            o = docx.Document(out)
            self.assertEqual(o.paragraphs[1].text, "Support Manager, Service Desk")
            self.assertEqual(o.paragraphs[3].style.name, "List Bullet")
            self.assertTrue(o.paragraphs[2].runs[0].bold)
            self.assertIsNone(o.paragraphs[2].runs[1].bold)
            self.assertEqual(o.paragraphs[4].text, "Second bullet about SLA reporting.")
            self.assertEqual(len(o.paragraphs), 5)
            self.assertEqual(docx.Document(src).paragraphs[1].text, "Head of Support, Customer Operations")

    def test_refusals(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = self.make(d), os.path.join(d, "out.docx")
            with self.assertRaises(ValueError): di.apply_edits(src, {"2": "one string for mixed runs"}, out)
            with self.assertRaises(ValueError): di.apply_edits(src, {"9": "x"}, out)
            with self.assertRaises(ValueError): di.apply_edits(src, {"0": "x" * 200}, out)
            self.assertFalse(os.path.exists(out))

    def test_table_cell_editable(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = self.make(d), os.path.join(d, "out.docx")
            di.apply_edits(src, {"5": "Edited cell"}, out)
            self.assertEqual(docx.Document(out).tables[0].cell(0, 0).text, "Edited cell")

    def test_theme_builds_sample(self):
        import docs_theme
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "r.docx")
            docs_theme.build_resume(docs_theme.THEMES["navy-ice"], os.path.join(SAMPLES, "head-of-support.md"), out)
            texts = [p.text for p in docx.Document(out).paragraphs]
            self.assertIn("Head of Support, Customer Operations", texts)
            self.assertTrue(texts[0].startswith("Sample Candidate"))


if __name__ == "__main__":
    unittest.main()
