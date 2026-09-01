#!/usr/bin/env python3
"""Check every source_url in the dataset actually resolves.

A citation nobody followed is a guess with a URL attached. State legislature
and revenue sites reorganise constantly, so this runs before each release and
its output belongs in the release notes.

Some state sites refuse HEAD, some refuse non-browser agents, and a few sit
behind bot protection that answers 403 to everything automated. Those are
reported as UNVERIFIABLE rather than DEAD, because a 403 from a WAF says
nothing about whether the page exists.

    python3 scripts/check_sources.py
"""
import json
import pathlib
import ssl
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
doc = json.loads((ROOT / "data" / "jurisdictions.json").read_text())

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

ok, blocked, dead = [], [], []

for j in sorted(doc["jurisdictions"], key=lambda x: x["code"]):
    url = j.get("source_url")
    if not url:
        dead.append((j["code"], "(no source_url)", "missing"))
        continue
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            code = r.status
        (ok if code < 400 else dead).append((j["code"], url, code))
    except urllib.error.HTTPError as e:
        # 403/406/429 are bot filtering, not evidence the page is gone.
        (blocked if e.code in (401, 403, 406, 429) else dead).append((j["code"], url, e.code))
    except Exception as e:
        blocked.append((j["code"], url, type(e).__name__))

print(f"OK {len(ok)}   BLOCKED/UNVERIFIABLE {len(blocked)}   DEAD {len(dead)}\n")
if dead:
    print("DEAD (fix these before release):")
    for c, u, s in dead:
        print(f"  {c}  {s}  {u}")
if blocked:
    print("\nUNVERIFIABLE from automation (check by hand):")
    for c, u, s in blocked:
        print(f"  {c}  {s}  {u}")
