#!/usr/bin/env python3
"""Prove the dataset reproduces the calculator it was extracted from.

A dataset transcribed by hand from a working tool is worth nothing unless
somebody checks the transcription. This recomputes tax from the JSON for
every bracket state across a grid of estate values, and compares against an
independent implementation of the same published schedules.

It also runs a corrupted control: one rate is deliberately altered and the
harness must report a mismatch. A check that cannot fail is not a check.

    python3 scripts/verify_against_calculator.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
brack = json.loads((ROOT / "data" / "estate_tax_brackets.json").read_text())
juris = {j["code"]: j for j in
         json.loads((ROOT / "data" / "jurisdictions.json").read_text())["jurisdictions"]}

GRID = [0, 500_000, 1_000_000, 1_500_000, 2_000_000, 3_000_000, 4_000_000,
        5_000_000, 6_000_000, 7_500_000, 9_000_000, 10_000_000, 12_000_000,
        15_000_000, 20_000_000, 50_000_000]


def from_rows(amount, rows):
    """base + rate * (amount - floor), using the highest floor at or below amount."""
    if amount <= 0:
        return 0.0
    hit = None
    for floor, base, rate in rows:
        if amount > floor:
            hit = (floor, base, rate)
    if hit is None:
        return 0.0
    floor, base, rate = hit
    return base + rate * (amount - floor)


def from_bands(amount, bands):
    t = 0.0
    for lo, hi, rate in bands:
        if amount > lo:
            top = amount if hi is None else min(amount, hi)
            t += rate * (top - lo)
        else:
            break
    return t


def dataset_tax(code, taxable_estate, tables):
    spec = tables[code]
    if spec.get("band_style"):
        return from_bands(taxable_estate, spec["bands"])
    ex = 3_076_000 if code == "WA_2026H1" else (juris[code]["exemption_usd"] or 0)
    applies = spec["applies_to"]
    amount = taxable_estate if applies.startswith("the whole") else taxable_estate - ex
    tax = from_rows(amount, spec["rows"])
    if code == "OR" and taxable_estate < 1_000_000:
        return 0.0
    if code == "CT":
        tax = min(tax, 15_000_000)
    return max(0.0, tax)


# Independent reimplementation from the published schedules, written from the
# statute descriptions rather than copied from the JSON, so agreement means
# something.
REFERENCE = {
    # Washington's first-half-2026 schedule under SB 5813, exclusion $3,076,000.
    "WA_2026H1": lambda v: from_rows(v - 3_076_000, [[0,0,.10],[1_000_000,100_000,.15],[2_000_000,250_000,.17],[3_000_000,420_000,.19],[4_000_000,610_000,.23],[6_000_000,1_070_000,.26],[7_000_000,1_330_000,.30],[9_000_000,1_930_000,.35]]),
    "WA": lambda v: from_rows(v - 3_000_000, [[0,0,.10],[1_000_000,100_000,.14],[2_000_000,240_000,.15],[3_000_000,390_000,.16],[4_000_000,550_000,.18],[6_000_000,910_000,.19],[7_000_000,1_100_000,.195],[9_000_000,1_490_000,.20]]),
    "OR": lambda v: 0.0 if v < 1_000_000 else from_rows(v, [[1_000_000,0,.10],[1_500_000,50_000,.1025],[2_500_000,152_500,.105],[3_500_000,257_500,.11],[4_500_000,367_500,.115],[5_500_000,482_500,.12],[6_500_000,602_500,.13],[7_500_000,732_500,.14],[8_500_000,872_500,.15],[9_500_000,1_022_500,.16]]),
    "MN": lambda v: from_rows(v - 3_000_000, [[0,0,.13],[7_100_000,923_000,.136],[8_100_000,1_059_000,.144],[9_100_000,1_203_000,.152],[10_100_000,1_355_000,.16]]),
    "NY": lambda v: from_rows(v, [[0,0,.0306],[500_000,15_300,.05],[1_000_000,40_300,.055],[1_500_000,67_800,.065],[2_100_000,106_800,.08],[2_600_000,146_800,.088],[3_100_000,190_800,.096],[3_600_000,238_800,.104],[4_100_000,290_800,.112],[5_100_000,402_800,.12],[6_100_000,522_800,.128],[7_100_000,650_800,.136],[8_100_000,786_800,.144],[9_100_000,930_800,.152],[10_100_000,1_082_800,.16]]),
    "HI": lambda v: from_rows(v - 5_490_000, [[0,0,.10],[1_000_000,100_000,.11],[2_000_000,210_000,.12],[3_000_000,330_000,.13],[4_000_000,460_000,.14],[5_000_000,600_000,.157],[10_000_000,1_385_000,.20]]),
    "ME": lambda v: from_rows(v - 7_160_000, [[0,0,.08],[3_000_000,240_000,.10],[6_000_000,540_000,.12]]),
    "VT": lambda v: max(0.0, .16 * (v - 5_000_000)),
    "CT": lambda v: min(.12 * max(0.0, v - 15_000_000), 15_000_000),
    "MD": lambda v: max(0.0, .16 * (v - 5_000_000)),
    "DC": lambda v: from_bands(v, [[4_988_400,5_000_000,.112],[5_000_000,6_000_000,.12],[6_000_000,7_000_000,.128],[7_000_000,8_000_000,.136],[8_000_000,9_000_000,.144],[9_000_000,10_000_000,.152],[10_000_000,None,.16]]),
}


def run(tables, label):
    bad = []
    for code, ref in REFERENCE.items():
        for v in GRID:
            got = dataset_tax(code, v, tables)
            want = max(0.0, ref(v))
            if abs(got - want) > 0.01:
                bad.append((code, v, got, want))
    print(f"{label}: {len(REFERENCE) * len(GRID)} cases, {len(bad)} mismatch(es)")
    for b in bad[:8]:
        print(f"    {b[0]} @ {b[1]:,}: dataset {b[2]:,.2f} vs reference {b[3]:,.2f}")
    return bad


real = run(brack["brackets"], "dataset vs reference")

# Corrupted control: break one Washington rate and require the harness to notice.
import copy
corrupt = copy.deepcopy(brack["brackets"])
corrupt["WA"]["rows"][0][2] = 0.99
ctrl = run(corrupt, "corrupted control (MUST fail)")

if real:
    print("\nFAIL: dataset does not match the published schedules.")
    sys.exit(1)
if not ctrl:
    print("\nFAIL: corrupted control passed, so this harness proves nothing.")
    sys.exit(1)
print("\nOK: dataset matches, and the harness demonstrably catches an error.")
