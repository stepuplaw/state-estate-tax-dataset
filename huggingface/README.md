---
license: cc-by-4.0
language:
  - en
pretty_name: US State Estate and Inheritance Tax, 2026
tags:
  - legal
  - tax
  - estate-tax
  - inheritance-tax
  - united-states
  - reference
  - law
size_categories:
  - n<1K
configs:
  - config_name: jurisdictions
    data_files: jurisdictions.csv
  - config_name: estate_tax_brackets
    data_files: estate_tax_brackets.csv
  - config_name: inheritance_tax_classes
    data_files: inheritance_tax_classes.csv
---

# US state estate and inheritance tax, 2026

All 50 US states and the District of Columbia, with the 2026 estate or
inheritance tax exemption, the full rate schedule, the statutory citation, and
the special rules that break naive calculations.

Compiled and maintained by [Kevin D. Klagge, Esq.](https://stepuplaw.com), a
Florida estate planning and elder law attorney, because no machine-readable
version of this existed and the human-readable versions disagree with each
other.

- Canonical page: <https://stepuplaw.com/data/state-estate-tax>
- Source repository: <https://github.com/stepuplaw/state-estate-tax-dataset>

## Why this exists

The federal exemption is $15,000,000, so most published guidance tells families
they have nothing to worry about. State thresholds start at **$1,000,000 in
Oregon**. A paid-off house plus a retirement account clears that.

## Coverage

Seventeen jurisdictions tax death: twelve states plus DC levy an estate tax,
five states levy an inheritance tax, and Maryland levies both. **The 34 that
levy nothing are included explicitly** with `tax_type: "none"` rather than
omitted, because absence is ambiguous — a reader who looks up Texas and finds
no row cannot tell whether Texas levies nothing or the file is incomplete, and
a program cannot tell either.

## Read these two columns, not one

Use `estate_tax_2026` and `inheritance_tax_2026` rather than filtering on a
single death-tax flag. **Kentucky, New Jersey, Nebraska and Pennsylvania levy
an inheritance tax and no estate tax**, and Maryland levies both. A table keyed
on "estate tax" alone codes the first four as untaxed, which is the single most
common error in published summaries of this subject.

Also read `exemption_kind` before using `exemption_usd`. It is not the same
kind of number in every state. Massachusetts and Rhode Island publish a filing
threshold paired with a statutory credit, so subtracting it gives the wrong
answer. Oregon and New York apply the table to the whole estate once the
threshold is crossed. Pennsylvania has no exemption at all.

## The traps, which are most of the value

- **New York is a cliff.** Above 105% of the exemption ($7,717,500 in 2026) the
  exemption vanishes and the entire estate is taxed from the first dollar.
- **Washington splits 2026 in half.** Deaths before July 1 use a $3,076,000
  exclusion and a schedule topping at 35%; deaths after use $3,000,000 and 20%.
  Both schedules are included.
- **Virginia is not untaxed.** Its chapter is still live and a postponed
  inheritance tax on pre-1980 remainder interests remains collectible.
- **Utah repealed inside the reporting year**, effective 2026-05-06.
- **Most "repealed in 2005" claims are wrong in kind.** Those states levied
  pick-up taxes measured by the federal credit under IRC §2011, which
  terminated for deaths after 2004-12-31 and was repealed outright in 2014.
  Their statutes often remain on the books computing to zero.

## Provenance and verification

Every figure was read from the state's own department of revenue or its
statute, with the citation and source URL stored per record. Effective dates
come from statutes and enrolled acts rather than agency prose, because several
state pages paraphrase "on or after [date]" as "after [date]", which shifts
liability by a day.

The repository includes a verification harness that recomputes every bracket
state across a grid of estate values against an independent implementation,
and that also runs a deliberately corrupted copy to confirm the check can
fail. Current run: 176 cases, 0 mismatches, control fires.

Nine of 51 records carry `status_verified: false` and say so. Those states levy
nothing and every source agrees they levy nothing; what is unverified is the
mechanism and the year, not the current liability.

## Not legal or tax advice

Reference data, not advice, and using it creates no attorney-client
relationship. Real returns involve deductions, lifetime gifts, multi-state
apportionment and elections that change the number. Verify against the statute
before relying on it for a filing.

## Citation

> Klagge, Kevin D. "US state estate and inheritance tax, 2026." StepUpLaw.
> <https://stepuplaw.com/data/state-estate-tax>
