#!/usr/bin/env python3
"""Extend jurisdictions.json to all 51 US jurisdictions.

WHY THE NON-TAXING STATES BELONG IN A DATASET ABOUT TAXING STATES: absence is
ambiguous. A consumer who looks up Texas and finds no row cannot tell whether
Texas levies nothing or whether the file is incomplete, and a program cannot
tell either. An explicit tax_type "none" answers the question. It also makes
the most common real query ("which states don't tax this?") answerable
directly instead of by inference.

Repeal years are carried where a state formerly levied one, because "never
had one" and "repealed in 2013" are different facts and the second is the one
that tells a reader the file is maintained.

    python3 scripts/add_nontaxing.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / "data" / "jurisdictions.json"
doc = json.loads(P.read_text())

# (code, name, repealed_estate, repealed_inheritance, citation, source_url, note)
NONE = [
    ("AL", "Alabama", 2005, None, "Ala. Code §40-15-2", "https://www.revenue.alabama.gov/", "Estate tax was tied to the federal state death tax credit and ended when the credit was repealed."),
    ("AK", "Alaska", 2005, None, "Alaska Stat. §43.31", "https://tax.alaska.gov/", "Pick-up tax only; ended with the federal credit."),
    ("AZ", "Arizona", 2005, None, "A.R.S. §42-4051 (repealed)", "https://azdor.gov/", "Pick-up tax only; ended with the federal credit."),
    ("AR", "Arkansas", 2005, None, "Ark. Code §26-59-106", "https://www.dfa.arkansas.gov/", "Pick-up tax only; ended with the federal credit."),
    ("CA", "California", 2005, None, "Cal. Rev. & Tax. Code §13302", "https://www.cdtfa.ca.gov/", "Pick-up tax only; ended with the federal credit."),
    ("CO", "Colorado", 2005, None, "C.R.S. §39-23.5-103", "https://tax.colorado.gov/", "Pick-up tax only; ended with the federal credit."),
    ("DE", "Delaware", 2018, None, "30 Del. C. ch. 15 (repealed)", "https://revenue.delaware.gov/", "Estate tax repealed for deaths on or after January 1, 2018."),
    ("FL", "Florida", 2005, None, "Fla. Const. Art. VII §5; Fla. Stat. ch. 198", "https://floridarevenue.com/taxes/taxesfees/Pages/estate_tax.aspx", "The Florida Constitution prohibits a state death tax beyond the amount of the former federal credit, so the legislature cannot enact one. No estate or inheritance tax at any estate size."),
    ("GA", "Georgia", 2005, None, "O.C.G.A. §48-12-1", "https://dor.georgia.gov/", "Pick-up tax only; ended with the federal credit."),
    ("ID", "Idaho", 2005, None, "Idaho Code §14-403", "https://tax.idaho.gov/", "Pick-up tax only; ended with the federal credit."),
    ("IN", "Indiana", None, 2013, "Ind. Code §6-4.1 (repealed)", "https://www.in.gov/dor/", "Inheritance tax repealed retroactive to deaths after December 31, 2012."),
    ("IA", "Iowa", None, 2025, "Iowa Code ch. 450; S.F. 619 (2021)", "https://revenue.iowa.gov/", "Inheritance tax phased out and fully repealed for deaths on or after January 1, 2025."),
    ("KS", "Kansas", 2010, None, "K.S.A. §79-15,203", "https://www.ksrevenue.gov/", "Estate tax repealed for deaths after 2009."),
    ("LA", "Louisiana", 2005, 2010, "La. R.S. 47:2401 et seq.", "https://revenue.louisiana.gov/", "Inheritance tax repealed for deaths after June 30, 2004; estate transfer tax ended with the federal credit."),
    ("MI", "Michigan", 2005, None, "MCL §205.201", "https://www.michigan.gov/taxes", "Pick-up tax only; ended with the federal credit."),
    ("MS", "Mississippi", 2005, None, "Miss. Code §27-9-5", "https://www.dor.ms.gov/", "Pick-up tax only; ended with the federal credit."),
    ("MO", "Missouri", 2005, None, "Mo. Rev. Stat. §145.011", "https://dor.mo.gov/", "Pick-up tax only; ended with the federal credit."),
    ("MT", "Montana", 2005, None, "Mont. Code §72-16-904", "https://mtrevenue.gov/", "Pick-up tax only; ended with the federal credit."),
    ("NV", "Nevada", 2005, None, "Nev. Const. Art. 10 §4; NRS ch. 375A", "https://tax.nv.gov/", "The Nevada Constitution prohibits an estate or inheritance tax."),
    ("NH", "New Hampshire", None, 2003, "N.H. RSA ch. 86 (repealed)", "https://www.revenue.nh.gov/", "Legacy and succession tax repealed for deaths after December 31, 2002."),
    ("NM", "New Mexico", 2005, None, "N.M. Stat. §7-7-2", "https://www.tax.newmexico.gov/", "Pick-up tax only; ended with the federal credit."),
    ("NC", "North Carolina", 2013, None, "N.C.G.S. §105-32.1 (repealed)", "https://www.ncdor.gov/", "Estate tax repealed for deaths on or after January 1, 2013."),
    ("ND", "North Dakota", 2005, None, "N.D.C.C. §57-37.1-04", "https://www.tax.nd.gov/", "Pick-up tax only; ended with the federal credit."),
    ("OH", "Ohio", 2013, None, "O.R.C. ch. 5731 (repealed)", "https://tax.ohio.gov/", "Estate tax repealed for deaths on or after January 1, 2013."),
    ("OK", "Oklahoma", 2010, None, "68 O.S. §801 et seq. (repealed)", "https://oklahoma.gov/tax.html", "Estate tax repealed for deaths after December 31, 2009."),
    ("SC", "South Carolina", 2005, None, "S.C. Code §12-16-510", "https://dor.sc.gov/", "Pick-up tax only; ended with the federal credit."),
    ("SD", "South Dakota", 2005, None, "S.D.C.L. ch. 10-40A", "https://dor.sd.gov/", "Inheritance tax repealed 2001; pick-up estate tax ended with the federal credit."),
    ("TN", "Tennessee", None, 2016, "Tenn. Code §67-8-303 (repealed)", "https://www.tn.gov/revenue.html", "Inheritance tax phased out and fully repealed for deaths on or after January 1, 2016."),
    ("TX", "Texas", 2005, None, "Tex. Tax Code ch. 211 (repealed)", "https://comptroller.texas.gov/", "Pick-up tax only; ended with the federal credit."),
    ("UT", "Utah", 2005, None, "Utah Code §59-11-103", "https://tax.utah.gov/", "Pick-up tax only; ended with the federal credit."),
    ("VA", "Virginia", 2007, None, "Va. Code §58.1-901 et seq.", "https://www.tax.virginia.gov/", "Estate tax repealed for deaths on or after July 1, 2007."),
    ("WV", "West Virginia", 2005, None, "W. Va. Code §11-11-3", "https://tax.wv.gov/", "Pick-up tax only; ended with the federal credit."),
    ("WI", "Wisconsin", 2008, None, "Wis. Stat. §72.01", "https://www.revenue.wi.gov/", "Estate tax sunset for deaths after December 31, 2007."),
    ("WY", "Wyoming", 2005, None, "Wyo. Stat. §39-19-103", "https://revenue.wyo.gov/", "Pick-up tax only; ended with the federal credit."),
]

existing = {j["code"] for j in doc["jurisdictions"]}
added = 0
for code, name, rep_e, rep_i, cite, url, note in NONE:
    if code in existing:
        continue
    doc["jurisdictions"].append({
        "code": code, "name": name, "tax_type": "none",
        "exemption_usd": None, "bottom_rate": None, "top_rate": None,
        "citation": cite, "source_url": url,
        "special_rule": note,
        "repealed_estate_tax_year": rep_e,
        "repealed_inheritance_tax_year": rep_i,
    })
    added += 1

# Taxing records gain the same two keys as nulls so every row has one shape.
for j in doc["jurisdictions"]:
    j.setdefault("repealed_estate_tax_year", None)
    j.setdefault("repealed_inheritance_tax_year", None)

order = {"estate": 0, "inheritance": 1, "both": 0, "none": 2}
doc["jurisdictions"].sort(key=lambda j: (order[j["tax_type"]], j["code"]))
doc["coverage"] = (
    "All 50 states and the District of Columbia. Jurisdictions levying no death "
    "tax are included explicitly with tax_type 'none' rather than omitted, so "
    "that absence of a row never has to be interpreted."
)
P.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

n = len(doc["jurisdictions"])
by = {}
for j in doc["jurisdictions"]:
    by[j["tax_type"]] = by.get(j["tax_type"], 0) + 1
print(f"added {added}; total jurisdictions {n}")
print(by)
