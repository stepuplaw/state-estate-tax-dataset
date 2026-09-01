#!/usr/bin/env python3
"""Generate the flat CSV distributions from the JSON sources.

The JSON files are the source of truth because they hold structure the CSVs
cannot (graduated inheritance classes, band-style DC, per-state applies_to
notes). The CSVs exist because most people who want this data open it in a
spreadsheet, and because Google Dataset Search wants a concrete
DataDownload it can point at.

    python3 scripts/build_csv.py
"""
import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

juris = json.loads((DATA / "jurisdictions.json").read_text())
brack = json.loads((DATA / "estate_tax_brackets.json").read_text())

# 1. One row per taxing jurisdiction.
with (DATA / "jurisdictions.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow([
        "code", "name", "tax_type", "exemption_usd", "bottom_rate", "top_rate",
        "citation", "source_url", "special_rule", "tax_year", "retrieved",
    ])
    for j in juris["jurisdictions"]:
        w.writerow([
            j["code"], j["name"], j["tax_type"], j["exemption_usd"],
            j["bottom_rate"], j["top_rate"], j["citation"], j["source_url"],
            j["special_rule"] or "", juris["tax_year"], juris["retrieved"],
        ])

# 2. One row per estate-tax bracket. DC is band-style, so its bands are
#    converted to the same (floor, base, rate) shape by accumulating the
#    tax at each band boundary. That keeps one consistent CSV schema.
with (DATA / "estate_tax_brackets.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["code", "bracket_floor_usd", "base_tax_usd", "marginal_rate", "applies_to"])
    for code, spec in brack["brackets"].items():
        applies = spec["applies_to"]
        if spec.get("band_style"):
            base = 0.0
            for lo, hi, rate in spec["bands"]:
                w.writerow([code, lo, round(base, 2), rate, applies])
                if hi is not None:
                    base += rate * (hi - lo)
        else:
            for floor, base, rate in spec["rows"]:
                w.writerow([code, floor, base, rate, applies])

# 3. One row per inheritance-tax class. Graduated classes are emitted as a
#    readable schedule string rather than exploded, because the tiers are
#    measured on the amount above the exemption and lose meaning alone.
with (DATA / "inheritance_tax_classes.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["code", "heir_class", "exemption_usd", "flat_rate", "graduated_schedule", "note"])
    for code, classes in brack["inheritance_classes"].items():
        for c in classes:
            grad = ""
            if "graduated" in c:
                grad = "; ".join(
                    f"{'remainder' if amt is None else f'next {amt}'} @ {rate}"
                    for amt, rate in c["graduated"]
                )
            elif "rows" in c:
                grad = "; ".join(f"over {fl}: {base}+{rate}" for fl, base, rate in c["rows"])
            w.writerow([
                code, c["class"],
                "" if c.get("exemption_usd") is None else c["exemption_usd"],
                c.get("rate", ""), grad, c.get("note", ""),
            ])

counts = {
    "jurisdictions": len(juris["jurisdictions"]),
    "bracket_states": len(brack["brackets"]),
    "inheritance_states": len(brack["inheritance_classes"]),
}
print("wrote jurisdictions.csv, estate_tax_brackets.csv, inheritance_tax_classes.csv")
print(counts)
