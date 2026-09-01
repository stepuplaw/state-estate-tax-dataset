# US state estate and inheritance tax, 2026

All 50 states and the District of Columbia, with the 2026 exemption, the full
rate schedule, the statutory citation, and the special rules that break naive
calculations. Twelve states plus the District of Columbia levy an estate tax,
five states levy an inheritance tax, Maryland levies both, and the remaining
34 jurisdictions levy neither.

The 34 that levy nothing are **in the file**, marked `tax_type: "none"`, with
the year they repealed if they formerly taxed. That is deliberate. Absence is
ambiguous: a reader who looks up Texas and finds no row cannot tell whether
Texas levies nothing or whether the file is incomplete, and a program cannot
tell either. It also makes the question people actually ask, which states do
not tax this, answerable directly rather than by inference.

Assembled and maintained by [Kevin D. Klagge, Esq.](https://stepuplaw.com),
a Florida estate planning and elder law attorney, because there was no
machine-readable version of this and the human-readable versions disagree with
each other.

## Why this exists

The federal exemption is $15,000,000, so most published guidance says ordinary
estates have nothing to worry about. State thresholds start at $1,000,000 in
Oregon. A paid-off house plus retirement savings clears that. The gap between
what people are told and what the states actually charge is the reason this
data is worth having in a form a program can read.

## Files

| File | What it is |
|---|---|
| `data/jurisdictions.json` | Source of truth, one record per jurisdiction, all 51 |
| `data/estate_tax_brackets.json` | Source of truth, full rate schedules and inheritance classes |
| `data/jurisdictions.csv` | Generated flat file, one row per jurisdiction |
| `data/estate_tax_brackets.csv` | Generated flat file, one row per bracket |
| `data/inheritance_tax_classes.csv` | Generated flat file, one row per heir class |

The JSON files are authoritative. The CSVs are generated from them by
`scripts/build_csv.py`, because structure the CSV cannot hold (graduated New
Jersey classes, band-style DC, per-state "applies to" semantics) still has to
live somewhere honest.

## Computing a tax

Bracket rows are `[bracket_floor, base_tax, marginal_rate]` and compose as:

    tax = base_tax + marginal_rate * (amount - bracket_floor)

using the highest floor at or below `amount`. What `amount` means differs by
state and is stated per state in `applies_to`. Most states apply the table to
the estate net of the exemption. Oregon and New York apply it to the whole
estate once the threshold is crossed, which is a materially different thing.

## The traps, which are the point

- **New York is a cliff.** Above 105% of the exemption ($7,717,500 in 2026) the
  exemption vanishes entirely and the whole estate is taxed from the first
  dollar. A small overage can cost six figures.
- **Oregon taxes the whole estate**, not just the excess, once you reach
  $1,000,000.
- **Pennsylvania has no exemption at all.** Tax runs from the first dollar,
  and the rate depends on who inherits rather than how much.
- **Maryland levies both taxes** and credits them against each other.
- **Washington changed mid-year.** Deaths on or after 2026-07-01 use a
  $3,000,000 exclusion and rates to 20% under ESB 6347. Deaths in the first
  half of 2026 use $3,076,000 and rates to 35%.
- **Massachusetts and Rhode Island** are not bracket tables. They compute from
  the former federal state death tax credit table less a statutory credit,
  which is what produces their effective exemptions.
- **Illinois** uses an interrelated calculation rather than a table.
- **Iowa now levies nothing.** Its inheritance tax was repealed for deaths on
  or after January 1, 2025 by S.F. 619, and it appears as `none` with that
  repeal year recorded.
- **Florida and Nevada are constitutionally barred** from levying one, so
  their `none` is structural rather than a policy that could flip next
  session.

Massachusetts, Rhode Island and Illinois are described in
`jurisdictions.json` but carry no bracket rows, because inventing rows for
them would be a lie a program would happily believe.

## Four ways published tables get this wrong

These are recorded in `common_miscodings` in the JSON, because avoiding them is
most of the value here.

1. **Inheritance-only states read as untaxed.** Kentucky, New Jersey, Nebraska
   and Pennsylvania each levy an inheritance tax and no estate tax. Kentucky's
   own revenue department says there is no Kentucky estate tax, which is true
   and constantly misread as no death tax. Filter on `inheritance_tax_2026`,
   not on estate tax alone.
2. **Post-2004 reenactors grouped with never-taxed states.** Delaware, Hawaii
   and Illinois all reenacted estate taxes that had expired. Delaware repealed
   again for 2018 deaths; Hawaii and Illinois still tax.
3. **Standalone repeals grouped with sponge states.** Ohio, North Carolina,
   Indiana, Tennessee, Kansas and Oklahoma repealed their own taxes by
   legislation rather than lapsing with the federal credit, so their years are
   real legislative dates rather than an artefact of 2005.
4. **Texas's pick-up tax was statutorily titled an inheritance tax**, which
   invites coding Texas as a former inheritance-tax state. It was measured by
   the federal credit like the other sponge taxes.

## Why so many states show zero

Most states collecting nothing today never repealed anything. They levied a
pick-up (sponge) tax equal to the federal credit for state death taxes under
IRC §2011. That credit was phased down to 75%, 50% and 25% for 2002, 2003 and
2004, then terminated for deaths after 2004-12-31, and was replaced by the
§2058 deduction. Many of those state statutes are still on the books and
simply compute to zero.

Two later changes made the lapse permanent. ATRA §101(a)(1) struck EGTRRA's
Title IX outright, killing the sunset that would have restored the credit. And
IRC §2011 was itself formally repealed in 2014 by Pub. L. 113-295
§221(a)(95)(A)(i), so state sponge statutes now cross-reference a section that
no longer exists. Full citations are in `federal_credit_history`.

## Verification

`scripts/verify_against_calculator.py` recomputes every bracket state across a
grid of estate values and compares against an independent implementation
written from the published schedules. It also runs a deliberately corrupted
copy and requires the harness to catch it, because a check that cannot fail
proves nothing. Current run: 160 cases, 0 mismatches, control fires.

## Provenance

Every figure was read from the state's own department of revenue or statute
on 2026-07-11. Citations and source URLs are per-record in
`jurisdictions.json`. Figures change annually; each year's revision is
released separately.

## Not legal or tax advice

This is reference data, not advice, and using it creates no attorney-client
relationship. Real returns involve deductions, lifetime gifts, multi-state
apportionment and elections that change the number. Verify against the
statute before relying on it for a filing.

## Licence

Data is licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Use it commercially, modify it, build products on it. Attribution keeps the
corrections flowing back, which is how the data stays right.
