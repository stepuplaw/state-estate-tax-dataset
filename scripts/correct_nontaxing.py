#!/usr/bin/env python3
"""Correct the non-taxing records after primary-source review.

WHAT WAS WRONG. The first pass recorded most non-taxing states as having
"repealed" their estate tax in 2005. That mislabels the mechanism. Those
states never repealed anything in 2005. They levied a "pick-up" or "sponge"
tax defined as an amount equal to the federal credit for state death taxes
under IRC §2011, and the FEDERAL credit terminated for deaths after
2004-12-31 (EGTRRA §532; §2011(f)). The state statutes mostly remain on the
books and simply compute to zero. IRC §2011 itself was later formally
repealed by Pub. L. 113-295 §221(a)(95)(A)(i) (2014), and ATRA §101(a)(1)
struck EGTRRA's sunset, so the credit these statutes point at cannot return.

That distinction matters for a legal dataset. "Repealed" and "dormant because
the federal cross-reference it depends on was repealed" are different legal
facts, and a reader planning around a possible revival needs the second.

WHAT THIS DOES. Replaces the repealed_* year fields with an explicit `status`
plus a `status_verified` flag, keeps year claims only where they are
documented, and adds the federal mechanism at the top level so the zeros are
explainable rather than mysterious.

    python3 scripts/correct_nontaxing.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / "data" / "jurisdictions.json"
doc = json.loads(P.read_text())

doc["federal_credit_history"] = {
    "summary": (
        "Most states that levy nothing today never repealed a tax. They levied a "
        "pick-up (sponge) tax equal to the federal credit for state death taxes "
        "under IRC §2011. That credit was phased down (75% in 2002, 50% in 2003, "
        "25% in 2004) and terminated for deaths after 2004-12-31, and was replaced "
        "by the §2058 deduction. Many of those state statutes remain on the books "
        "and compute to zero."
    ),
    "citations": [
        {"cite": "IRC §2011(b)(2), (f) (pre-repeal text)", "url": "https://www.govinfo.gov/content/pkg/USCODE-2010-title26/html/USCODE-2010-title26-subtitleB-chap11-subchapA-partII-sec2011.htm"},
        {"cite": "EGTRRA, Pub. L. 107-16 §§531, 532", "url": "https://www.govinfo.gov/content/pkg/USCODE-2010-title26/html/USCODE-2010-title26-subtitleB-chap11-subchapA-partII-sec2011.htm"},
        {"cite": "IRC §2058 (state death tax deduction, added by EGTRRA §532(b))", "url": "https://www.law.cornell.edu/uscode/text/26/2058"},
        {"cite": "ATRA, Pub. L. 112-240 §101(a)(1) (struck EGTRRA's sunset)", "url": "https://www.govinfo.gov/content/pkg/PLAW-112publ240/html/PLAW-112publ240.htm"},
        {"cite": "Pub. L. 113-295 §221(a)(95)(A)(i) (formally repealed IRC §2011)", "url": "https://www.govinfo.gov/content/pkg/USCODE-2018-title26/html/USCODE-2018-title26-subtitleB-chap11-subchapA-partII-sec2011.htm"},
    ],
}

# status values:
#   sponge_dormant  - pick-up statute keyed to the repealed IRC §2011 credit
#   repealed        - the state's own standalone tax was repealed; year given
#   zeroed_by_statute - statute affirmatively says no tax is levied from a date
STATUS = {
    "GA": ("zeroed_by_statute", 2014, True,
           "O.C.G.A. §48-12-1: on and after July 1, 2014 no estate taxes are levied by the state. The chapter was zeroed prospectively rather than struck.",
           "https://codes.findlaw.com/ga/title-48-revenue-and-taxation/ga-code-sect-48-12-1.html"),
    "FL": ("sponge_dormant", None, True,
           "Fla. Stat. ch. 198 remains in force. §198.02 imposes a pure pick-up tax measured by the federal credit, and §198.41 keeps the chapter effective so long as the federal estate tax exists, so the tax computes to zero rather than having been repealed. Florida DOR states the federal change eliminated the tax for deaths after 2004-12-31. A commonly cited constitutional cap at Fla. Const. Art. VII §5 is NOT independently verified here; the statutory position above is.",
           "https://floridarevenue.com/taxes/taxesfees/Pages/estate_tax.aspx"),
    "CA": ("sponge_dormant", None, True,
           "Cal. Rev. & Tax. Code §13301 bars a state death tax and §13302 carves out a pick-up tax equal to the maximum federal credit, so the tax computes to zero. These are statutes, not constitutional provisions. A 1982 ballot-initiative origin is sometimes asserted and is NOT verified here.",
           "https://codes.findlaw.com/ca/revenue-and-taxation-code/rtc-sect-13302.html"),
    "NV": ("sponge_dormant", None, True,
           "NRS 375A.100 imposes a tax equal to the maximum federal credit for state death taxes, so it computes to zero. A constitutional prohibition is sometimes asserted and is NOT verified here.",
           "https://codes.findlaw.com/nv/title-32-revenue-and-taxation/nv-rev-st-375a-100.html"),
    "DE": ("repealed", 2018, True, "Estate tax repealed for deaths on or after 2018-01-01. Delaware had reenacted a tax after 2009 and then repealed it again.", None),
    "IA": ("repealed", 2025, True, "Inheritance tax phased out and fully repealed for deaths on or after 2025-01-01 (S.F. 619).", None),
    "OH": ("repealed", 2013, True, "Standalone estate tax repealed for deaths on or after 2013-01-01.", None),
    "NC": ("repealed", 2013, True, "Standalone estate tax repealed for deaths on or after 2013-01-01.", None),
    "IN": ("repealed", 2013, True, "Standalone inheritance tax repealed retroactive to deaths after 2012-12-31.", None),
    "TN": ("repealed", 2016, True, "Standalone inheritance tax fully repealed for deaths on or after 2016-01-01.", None),
    "KS": ("repealed", 2010, False, "Standalone estate tax repealed for deaths after 2009. Year not re-verified against the statute.", None),
    "OK": ("repealed", 2010, False, "Standalone estate tax repealed for deaths after 2009. Year not re-verified against the statute.", None),
    "NH": ("repealed", 2003, False, "Legacy and succession tax repealed for deaths after 2002-12-31. Year not re-verified against the statute.", None),
    "LA": ("repealed", 2005, False, "Inheritance tax repealed for deaths after 2004-06-30; the separate estate transfer tax was a pick-up. Not re-verified.", None),
    "VA": ("repealed", 2007, False, "Estate tax repealed for deaths on or after 2007-07-01. Not re-verified; Virginia is also cited as a sponge-only state, so this needs confirmation.", None),
    "WI": ("repealed", 2008, False, "Estate tax sunset for deaths after 2007-12-31. Not re-verified; Wisconsin is also cited as a sponge-only state, so this needs confirmation.", None),
    "SD": ("repealed", 2001, False, "Standalone inheritance tax repealed around 2001, before the federal credit terminated. Year not verified.", None),
    "MT": ("repealed", 2001, False, "Standalone inheritance tax repealed around 2001, before the federal credit terminated. Year not verified.", None),
}

for j in doc["jurisdictions"]:
    if j["tax_type"] != "none":
        j.pop("repealed_estate_tax_year", None)
        j.pop("repealed_inheritance_tax_year", None)
        continue
    code = j["code"]
    j.pop("repealed_estate_tax_year", None)
    j.pop("repealed_inheritance_tax_year", None)
    if code in STATUS:
        status, year, verified, note, url = STATUS[code]
        j["status"] = status
        j["status_year"] = year
        j["status_verified"] = verified
        j["special_rule"] = note
        if url:
            j["source_url"] = url
    else:
        # Everything else: sponge tax that died with the federal credit. The
        # per-state statute has NOT been re-read, so say so rather than imply it.
        j["status"] = "sponge_dormant"
        j["status_year"] = None
        j["status_verified"] = False
        j["special_rule"] = (
            "Levied a pick-up tax measured by the federal credit under IRC §2011, "
            "which terminated for deaths after 2004-12-31. No state death tax applies "
            "today. Whether the state statute was repealed or merely computes to zero "
            "has not been individually verified."
        )

P.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
none = [j for j in doc["jurisdictions"] if j["tax_type"] == "none"]
print(f"corrected {len(none)} non-taxing records")
print("  verified:", sum(1 for j in none if j["status_verified"]))
print("  unverified:", sum(1 for j in none if not j["status_verified"]))
