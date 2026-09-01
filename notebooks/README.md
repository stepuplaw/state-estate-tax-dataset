# Notebooks

Reproducible computational legal research over the CourtListener bulk corpus.

Each notebook is **generated** by its `build_*.py` script rather than hand-edited,
so the analysis and the prose live in one reviewable file and a rerun after a
corpus refresh produces new numbers instead of stale text beside fresh output.

    python3 notebooks/build_capacity_notebook.py
    python3 -m nbconvert --execute --inplace notebooks/<name>.ipynb

## Published

### [Will contests are disappearing from Florida appellate opinions](florida-testamentary-capacity.ipynb)

Testamentary capacity and undue influence in Florida appellate decisions,
1960 to 2026. The rate at which these doctrines appear has fallen from roughly
40 to 49 per 10,000 decisions in the 1960s through 1980s to between 10 and 20
from the 2000s onward.

The finding only exists because of the denominator. Raw counts show a 1980s
bump and nothing else; normalising against all Florida appellate decisions from
the same courts in the same years turns that into a sustained decline. Federal
courts sitting in Florida are excluded, because their share of the corpus grew
over the period and would otherwise manufacture a decline out of a change in
corpus composition.

Derived outputs, reusable without the corpus:

- `florida-capacity-undue-influence-by-decade.csv`
- `florida-capacity-undue-influence-by-year.csv`

## What these measure, and what they do not

They measure how often courts **discuss** a doctrine, not how often litigants
**win** on it. An FTS match means the phrase appears somewhere in the decision,
so some hits are passing citations rather than holdings. The measure is an upper
bound on doctrinal engagement, and it is comparable across decades only because
the same bias applies to every decade equally.

## Data

CourtListener bulk corpus, snapshot 2026-06-30: 10,797,793 opinions across
10,070,727 clusters, stored locally with an SQLite FTS5 index. Counting is by
cluster rather than opinion, so one decision with a majority plus a dissent
counts once.

Two FTS5 traps worth knowing before writing a new query:

- `NEAR()` accepts only phrases. `NEAR(("a" OR "b") "c", 10)` is a syntax error;
  expand it into OR'd `NEAR()` calls.
- Ranking by citation count surfaces old, famous opinions that mention a term in
  passing. Rank by recency when you want the cases that describe a change.

## Licence

CC BY 4.0, including the derived CSVs. Not legal advice; empirical research
about published opinions creates no attorney-client relationship.
