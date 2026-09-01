#!/usr/bin/env python3
"""Case-law backstop for the states whose statutory status could not be verified.

WHY CASE LAW HELPS HERE. Nine states in this dataset levy nothing and their
legislatures publish no explainer for a tax they stopped collecting, so the
usual source (a DOR filing booklet) does not exist. Courts, however, keep
describing what happened: an opinion that says a state's inheritance tax "was
repealed in" a given year, or that applies the tax to a death in a given year,
is contemporaneous evidence of the mechanism and the date.

Method follows elder/scraper/cl-data-local/probe.py: FTS5 MATCH over op_fts,
database opened immutable, counting distinct clusters. Court is mapped to state
through cluster_court joined to court_meta.

This is a BACKSTOP, not a primary source. A case is evidence of what a court
believed the law to be, which is strong corroboration and weak authority for a
statutory citation. Anything it turns up should be graded VERIFIED-SECONDARY
and used to target a primary pull, never published as the citation itself.

    python3 scripts/caselaw_backstop.py
"""
import json
import pathlib
import sqlite3
import sys
import time

OPS = "/Volumes/Elements/cl-data/us-opinions.db"
META = "/Volumes/Elements/cl-data/us-meta.db"

STATES = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI',
    'Wyoming': 'WY', 'District of Columbia': 'DC',
}

# The nine whose mechanism or year is unverified in jurisdictions.json.
TARGETS = ['AK', 'AL', 'CO', 'ID', 'KS', 'MI', 'OK', 'TX', 'WY']

# Two queries per state. The first finds any death-tax discussion at all, which
# sizes whether the state's courts ever had occasion to describe it. The second
# narrows to language about repeal or expiration, which is where a date lives.
BROAD = '"estate tax" OR "inheritance tax" OR "death tax" OR "succession tax"'
NARROW = ('(("estate tax" OR "inheritance tax" OR "death tax") AND '
          '(repeal* OR expire* OR "no longer" OR sunset OR abolish*))')

# The precise form: a court actually asserting the tax was repealed. FTS5 NEAR()
# accepts only phrases, so this is expanded into OR'd NEAR calls rather than
# written as NEAR(("a" OR "b") "c", n), which is a syntax error.
ASSERTS_REPEAL = (
    'NEAR("inheritance tax" "repealed", 6) OR NEAR("estate tax" "repealed", 6) OR '
    'NEAR("inheritance tax" "abolished", 6) OR NEAR("estate tax" "abolished", 6) OR '
    'NEAR("succession tax" "repealed", 6)')


def court_state_map(mt):
    m = {}
    for cid, full in mt.execute("SELECT id, full_name FROM court_meta"):
        if not full:
            continue
        # Longest name first so "West Virginia" is not swallowed by "Virginia".
        for name in sorted(STATES, key=len, reverse=True):
            if name.lower() in full.lower():
                m[cid] = STATES[name]
                break
    return m


def main():
    for p in (OPS, META):
        if not pathlib.Path(p).exists():
            sys.exit(f"missing {p} — is the Elements drive mounted?")

    op = sqlite3.connect(f"file:{OPS}?immutable=1", uri=True)
    mt = sqlite3.connect(f"file:{META}?immutable=1", uri=True)
    cs = court_state_map(mt)

    by_state = {}
    for court, st in cs.items():
        by_state.setdefault(st, []).append(court)

    print(f"{'state':<6}{'any death-tax':>15}{'repeal language':>18}   top cases")
    results = {}
    for st in TARGETS:
        courts = by_state.get(st, [])
        if not courts:
            print(f"{st:<6}{'no courts mapped':>15}")
            continue
        qmarks = ",".join("?" * len(courts))
        out = {}
        for label, q in (("broad", BROAD), ("narrow", NARROW), ("asserts_repeal", ASSERTS_REPEAL)):
            t = time.time()
            rows = op.execute(
                f"""SELECT DISTINCT o.cluster_id
                    FROM op_fts f
                    JOIN opinions o ON o.id = f.rowid
                    JOIN cluster_court cc ON cc.cluster_id = o.cluster_id
                    WHERE op_fts MATCH ? AND cc.court IN ({qmarks})""",
                (q, *courts),
            ).fetchall()
            out[label] = [r[0] for r in rows]
            out[label + "_secs"] = round(time.time() - t, 1)

        # Rank by RECENCY, not citation count. A repeal is described by the cases
        # that came after it; ranking by citations surfaces old famous opinions
        # that merely mention a death tax in passing.
        top = []
        if out["narrow"]:
            ids = out["narrow"][:900]
            qm = ",".join("?" * len(ids))
            top = mt.execute(
                f"""SELECT case_name, date_filed, citation_count
                    FROM cluster_meta WHERE cluster_id IN ({qm})
                    ORDER BY date_filed DESC LIMIT 3""",
                ids,
            ).fetchall()
        results[st] = {"broad": len(out["broad"]), "narrow": len(out["narrow"]),
                       "asserts_repeal": len(out["asserts_repeal"]),
                       "top": [{"case": c, "date": d, "cites": n} for c, d, n in top]}
        names = "; ".join(f"{c} ({d[:4] if d else '?'})" for c, d, _ in top) or "-"
        print(f"{st:<6}{len(out['broad']):>15}{len(out['narrow']):>18}   {names[:96]}")

    pathlib.Path("data/caselaw_backstop.json").write_text(
        json.dumps({"method": "FTS5 over CourtListener national corpus, 10.8M opinions",
                    "caveat": "Secondary corroboration only. A case shows what a court believed the law to be; cite the statute, not the case.",
                    "finding_2026_09": "Ran against all nine unverified states. Only THREE clusters nationally contain a court asserting a death tax was repealed, and two date from 1917 and 1934. Pick-up taxes collect nothing, so nobody litigates them; the same absence of controversy that leaves these states without a DOR explainer also leaves them without case law. This backstop does not close the nine gaps.",
                    "results": results}, indent=2) + "\n")
    print("\nwrote data/caselaw_backstop.json")


if __name__ == "__main__":
    main()
