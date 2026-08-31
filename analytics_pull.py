#!/usr/bin/env python
"""Pull Garden traffic from the Umami Cloud API and characterise spike days.

The Garden's 404 page redirects every missing URL to /search.html, so search
hits and dead-link arrivals look identical in the dashboard. This script
separates them: it finds the spike days, then breaks each one down by query
string, referrer, browser, OS and country, which is what tells a crawler fleet
apart from an audience.

Needs UMAMI_API_KEY in a .env beside this file (create the key at
cloud.umami.is: profile button > Settings > API keys > Create key). The key is
never printed.

  python analytics_pull.py daily [days]        default 120
  python analytics_pull.py day 2026-08-14      breakdowns for one day
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

WEBSITE_ID = "cc6d6b30-1bf8-497f-b38a-7feae109d761"
BASES = ["https://api.umami.is/v1/eu", "https://api.umami.is/v1"]
TZ = "Europe/London"


def load_key():
    env = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    key = os.environ.get("UMAMI_API_KEY", "")
    if not key and os.path.exists(env):
        for line in open(env, encoding="utf-8"):
            line = line.strip()
            if line.startswith("UMAMI_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        sys.exit("No UMAMI_API_KEY. Put it in .env beside this script.")
    return key


def call(path, params, key, base=None):
    """GET one endpoint, trying each regional base until one answers."""
    bases = [base] if base else BASES
    last = None
    for b in bases:
        url = b + path + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(
            url, headers={"Accept": "application/json", "Authorization": "Bearer " + key}
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode()), b
        except urllib.error.HTTPError as e:
            last = "%s %s on %s" % (e.code, e.reason, b)
            if e.code in (401, 403):
                sys.exit("Umami rejected the key (%s). Regenerate it in Settings > API keys." % last)
        except Exception as e:  # network, timeout
            last = "%s on %s" % (e, b)
    sys.exit("Umami API call failed: %s" % last)


def ms(dt):
    return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)


def daily(days):
    key = load_key()
    end = datetime.utcnow().replace(hour=23, minute=59, second=59)
    start = (end - timedelta(days=days)).replace(hour=0, minute=0, second=0)
    data, base = call(
        "/websites/%s/pageviews" % WEBSITE_ID,
        {"startAt": ms(start), "endAt": ms(end), "unit": "day", "timezone": TZ},
        key,
    )
    views = {r["x"][:10]: r["y"] for r in data.get("pageviews", [])}
    sessions = {r["x"][:10]: r["y"] for r in data.get("sessions", [])}
    counts = sorted(views.values())
    median = counts[len(counts) // 2] if counts else 0
    print("region base: %s   days: %d   median views/day: %d\n" % (base, len(views), median))
    print("%-12s %8s %9s  %s" % ("date", "views", "sessions", ""))
    for d in sorted(views):
        v, s = views[d], sessions.get(d, 0)
        spike = " <-- SPIKE" if median and v >= 3 * median else ""
        print("%-12s %8d %9d  %s%s" % (d, v, s, "#" * min(60, int(v / max(1, median) * 3)), spike))
    spikes = [d for d in sorted(views) if median and views[d] >= 3 * median]
    if spikes:
        print("\nspike days: " + " ".join(spikes))
        print("next: python analytics_pull.py day " + spikes[-1])


def day(date_str):
    key = load_key()
    d0 = datetime.strptime(date_str, "%Y-%m-%d")
    d1 = d0 + timedelta(days=1) - timedelta(seconds=1)
    key_types = [
        ("url", "paths"),
        ("query", "query strings (the ?q= on /search.html)"),
        ("referrer", "referrers"),
        ("browser", "browsers"),
        ("os", "operating systems"),
        ("device", "devices"),
        ("country", "countries"),
        ("host", "hostnames"),
    ]
    for t, label in key_types:
        rows, _ = call(
            "/websites/%s/metrics" % WEBSITE_ID,
            {
                "startAt": ms(d0),
                "endAt": ms(d1),
                "type": t,
                "timezone": TZ,
                "limit": 25,
            },
            key,
        )
        print("\n=== %s: %s ===" % (date_str, label))
        if not rows:
            print("  (nothing returned)")
            continue
        for r in rows:
            print("  %6s  %s" % (r.get("y"), (r.get("x") or "(none)")[:110]))


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "daily":
        daily(int(args[1]) if len(args) > 1 else 120)
    elif args[0] == "day" and len(args) > 1:
        day(args[1])
    else:
        sys.exit(__doc__)
