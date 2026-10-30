#!/usr/bin/env python3
"""Run-window gate for job-scout. Prints nothing and exits 10 when outside the window.

Exit 0 = inside the window; stdout is JSON: {"now": ..., "digest_due": "12:00" | null}.
Reads timezone, run_window and alerts from profile/preferences.yaml (PyYAML).
Digest slots already sent today are tracked in profile/state.json.
Uses zoneinfo, so the tzdata package must be installed on minimal systems.
"""
import argparse, datetime as dt, json, os, sys
from zoneinfo import ZoneInfo

OUTSIDE = 10
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def hm(s):
    h, m = s.split(":")
    return dt.time(int(h), int(m))


def in_window(now_local, win):
    """win: {days, start, end, grace_minutes}. End is inclusive, plus a grace for late scheduler starts."""
    if DAYS[now_local.weekday()] not in [d.lower()[:3] for d in win["days"]]:
        return False
    t = now_local.time().replace(second=0, microsecond=0)
    end = (dt.datetime.combine(now_local.date(), hm(win["end"])) +
           dt.timedelta(minutes=win.get("grace_minutes", 10))).time()
    return hm(win["start"]) <= t <= end


def digest_due(now_local, slots, sent_today):
    """Earliest digest slot that has passed today and has not been sent, else None."""
    for s in sorted(slots):
        if s not in sent_today and now_local.time() >= hm(s):
            return s
    return None


def decide(now_utc, prefs, state):
    tz = ZoneInfo(prefs["timezone"])
    now = now_utc.astimezone(tz)
    if not in_window(now, prefs["run_window"]):
        return None
    due = None
    al = prefs.get("alerts", {})
    if al.get("alert_mode") == "instant_plus_digest":
        sent = state.get("digests_sent", {}).get(now.date().isoformat(), [])
        due = digest_due(now, al.get("digest_times", ["12:00", "17:00"]), sent)
    return {"now": now.isoformat(timespec="minutes"), "digest_due": due}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prefs", default="profile/preferences.yaml")
    ap.add_argument("--state", default="profile/state.json")
    ap.add_argument("--now", help="ISO time with offset, for testing (default: current time)")
    ap.add_argument("--mark-digest-sent", metavar="HH:MM", help="record a digest slot as sent today")
    a = ap.parse_args(argv)
    import yaml
    with open(a.prefs, encoding="utf-8") as f:
        prefs = yaml.safe_load(f)
    state = {}
    if os.path.exists(a.state):
        with open(a.state, encoding="utf-8") as f:
            state = json.load(f)
    now_utc = dt.datetime.fromisoformat(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    if a.mark_digest_sent:
        day = now_utc.astimezone(ZoneInfo(prefs["timezone"])).date().isoformat()
        state.setdefault("digests_sent", {}).setdefault(day, []).append(a.mark_digest_sent)
        state["digests_sent"] = {day: state["digests_sent"][day]}  # keep today only
        with open(a.state, "w", encoding="utf-8") as f:
            json.dump(state, f)
        return 0
    res = decide(now_utc, prefs, state)
    if res is None:
        return OUTSIDE
    print(json.dumps(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
