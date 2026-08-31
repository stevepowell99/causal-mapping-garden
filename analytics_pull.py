#!/usr/bin/env python
"""Pull Garden traffic from GoatCounter and characterise the spike days.

The Garden's 404 page redirects every missing URL to /search.html, so a real
search and a dead-link arrival look identical in a dashboard. This script
separates them: it finds the spike days, then breaks one down by browser,
system, location, screen size and referrer, and (where individual pageviews are
switched on) counts GoatCounter's per-hit bot flag.

GoatCounter rather than Umami because Umami Cloud's API needs the Pro plan,
while GoatCounter's is free and is the only one of the two that records whether
a hit was a bot.

Needs GOATCOUNTER_TOKEN in a .env beside this file. Create it at
causal-mapping-garden.goatcounter.com under [your name, top right] > API, with
at least "Read statistics"; the export mode also needs "Export". The token is
never printed.

  python analytics_pull.py daily [days]        default 120
  python analytics_pull.py day 2026-08-14      breakdowns for one day
  python analytics_pull.py export [days]       per-hit CSV, counts the bot flag
"""

import csv
import gzip
import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta

SITE = "https://causal-mapping-garden.goatcounter.com"
API = SITE + "/api/v0"

# isbot constants, from https://github.com/arp242/isbot. 0 and 1 mean "not a
# bot"; everything else is one of its detection reasons.
ISBOT = {
    0: "no bot",
    1: "no bot (unknown UA)",
    2: "no bot (short UA)",
    3: "prefix match",
    4: "known bot UA",
    5: "bot keyword in UA",
    6: "boty range",
    7: "known bot IP range",
    8: "client hint",
    150: "JS: no javascript",
    151: "JS: phantom/headless",
    152: "JS: nightmare",
    153: "JS: selenium",
    154: "JS: webdriver",
}


def token():
    env = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    tok = os.environ.get("GOATCOUNTER_TOKEN", "")
    if not tok and os.path.exists(env):
        for line in open(env, encoding="utf-8"):
            line = line.strip()
            if line.startswith("GOATCOUNTER_TOKEN="):
                tok = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not tok:
        sys.exit(
            "No GOATCOUNTER_TOKEN. Create one at %s (menu top right > API) and put it\n"
            "in .env beside this script as GOATCOUNTER_TOKEN=..." % SITE
        )
    return tok


def call(path, params=None, tok=None, method="GET", body=None, raw=False):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + tok,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            payload = r.read()
            return payload if raw else json.loads(payload.decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        if e.code in (401, 403):
            sys.exit(
                "GoatCounter rejected the token (%s). Check it has the right permissions.\n%s"
                % (e.code, detail)
            )
        raise SystemExit("GoatCounter %s on %s\n%s" % (e.code, path, detail))


def hour(dt):
    return dt.strftime("%Y-%m-%dT%H:00:00Z")


def daily(days):
    tok = token()
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    res = call(
        "/stats/hits",
        {"start": hour(start), "end": hour(end), "group": "day", "limit": 200},
        tok,
    )
    hits = res.get("hits", [])
    if not hits:
        print("No hits returned for the last %d days." % days)
        return
    if res.get("more"):
        print("NOTE: more paths exist beyond the 200 fetched; totals below are of those 200.\n")

    per_day = defaultdict(int)
    search_day = defaultdict(int)
    for h in hits:
        for s in h.get("stats", []):
            per_day[s["day"]] += s.get("daily", 0)
            if h.get("path", "").startswith("/search"):
                search_day[s["day"]] += s.get("daily", 0)

    counts = sorted(per_day.values())
    median = counts[len(counts) // 2] if counts else 0
    print("paths fetched: %d   days: %d   median visitors/day: %d\n" % (len(hits), len(per_day), median))
    print("%-12s %8s %8s  %s" % ("date", "visits", "search", ""))
    spikes = []
    for d in sorted(per_day):
        v = per_day[d]
        bar = "#" * min(60, int(v / max(1, median) * 3))
        flag = ""
        if median and v >= 3 * median:
            flag = "  <-- SPIKE"
            spikes.append(d)
        print("%-12s %8d %8d  %s%s" % (d, v, search_day.get(d, 0), bar, flag))
    if spikes:
        print("\nspike days (>= 3x median): " + " ".join(spikes))
        print("next: python analytics_pull.py day " + spikes[-1])
    else:
        print("\nNo day reached 3x the median, so nothing flagged as a spike.")


def day(date_str):
    tok = token()
    d0 = datetime.strptime(date_str, "%Y-%m-%d")
    d1 = d0 + timedelta(days=1)
    params = {"start": hour(d0), "end": hour(d1), "limit": 20}

    res = call("/stats/hits", dict(params, limit=15), tok)
    print("\n=== %s: top paths ===" % date_str)
    for h in res.get("hits", []):
        print("  %6d  %s" % (h.get("count", 0), h.get("path", "")[:110]))

    for page in ("browsers", "systems", "locations", "sizes", "toprefs", "languages"):
        try:
            res = call("/stats/" + page, params, tok)
        except SystemExit as e:
            print("\n=== %s: %s ===\n  unavailable: %s" % (date_str, page, e))
            continue
        rows = res.get("stats", [])
        print("\n=== %s: %s ===" % (date_str, page))
        if not rows:
            print("  (none recorded)")
        for r in rows:
            print("  %6d  %s" % (r.get("count", 0), (r.get("name") or "(none)")[:100]))


def export(days):
    """Per-hit CSV. Only works if 'Individual pageviews' is on in site settings,
    and only covers hits recorded since it was switched on."""
    tok = token()
    # CSV exports cover the whole history: start_from_day is JSON-only, and
    # start_from_hit_id is a pagination cursor rather than a date. So export
    # everything and cut the rows down to `days` here.
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    job = call("/export", None, tok, method="POST", body={"format": "csv"})
    job_id = job.get("id")
    if not job_id:
        sys.exit("No export id returned: %s" % json.dumps(job)[:300])
    print("export %s queued, waiting..." % job_id)

    for _ in range(60):
        time.sleep(5)
        st = call("/export/%s" % job_id, None, tok)
        if st.get("finished_at"):
            if st.get("error"):
                sys.exit("Export failed: %s" % st["error"])
            print("export finished: %s rows" % st.get("num_rows"))
            break
        print("  ...%s rows so far" % st.get("num_rows", 0))
    else:
        sys.exit("Export did not finish within five minutes.")

    blob = call("/export/%s/download" % job_id, None, tok, raw=True)
    try:
        text = gzip.decompress(blob).decode("utf-8", "replace")
    except OSError:
        text = blob.decode("utf-8", "replace")

    all_rows = list(csv.DictReader(io.StringIO(text)))
    datecol = next((c for c in (all_rows[0].keys() if all_rows else []) if c.lower() == "date"), None)
    rows = [r for r in all_rows if not datecol or (r.get(datecol) or "")[:10] >= since]
    if all_rows:
        print("exported %d hits in total; %d of them on or after %s" % (len(all_rows), len(rows), since))
    if not rows:
        print("The export is empty. 'Individual pageviews' is probably off in site settings,")
        print("so no per-hit data exists yet. Turn it on and the NEXT spike will be diagnosable.")
        return

    header = list(rows[0].keys())
    botcol = next((c for c in header if c.lower() == "bot"), None)
    print("\n%d hits exported, columns: %s" % (len(rows), ", ".join(header)))

    if botcol:
        per_day_bot = defaultdict(Counter)
        for r in rows:
            d = (r.get(datecol) or "")[:10]
            try:
                code = int(r[botcol] or 0)
            except ValueError:
                code = -1
            per_day_bot[d][code] += 1
        print("\n%-12s %8s %8s  %s" % ("date", "hits", "bots", "reasons"))
        for d in sorted(per_day_bot):
            c = per_day_bot[d]
            total = sum(c.values())
            bots = sum(n for code, n in c.items() if code > 2)
            why = ", ".join(
                "%s x%d" % (ISBOT.get(code, "code %s" % code), n)
                for code, n in c.most_common()
                if code > 2
            )
            print("%-12s %8d %8d  %s" % (d, total, bots, why))

    for col in ("Browser", "System", "Location", "Screen size", "Referrer"):
        if col in header:
            print("\n=== %s ===" % col)
            for name, n in Counter(r[col] or "(none)" for r in rows).most_common(12):
                print("  %6d  %s" % (n, name[:100]))


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "daily":
        daily(int(args[1]) if len(args) > 1 else 120)
    elif args[0] == "day" and len(args) > 1:
        day(args[1])
    elif args[0] == "export":
        export(int(args[1]) if len(args) > 1 else 120)
    else:
        sys.exit(__doc__)
