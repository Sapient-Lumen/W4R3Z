# rev0012 response-oracle seed

rev0012 adds a small first response-oracle seed, not a real learned oracle.

The new file `src/muc5/oracle_seed.py` generates candidate decks by mixing:

```text
local mutations around existing seed decks
random plausible decks
transparent static construction priors
```

Then `scripts/run_rev0012_oracle_seed.py` turns the top candidates into strategy bundles and evaluates them against a small base population using public DecisionFrame agents.

Generated files:

```text
data/rev0012_oracle_seed_candidates.csv
data/rev0012_oracle_seed_games.csv
data/rev0012_oracle_seed_standings.csv
data/rev0012_oracle_seed_summary.json
```

## Why this belongs before PPO

A real neural policy/value system would be harder to debug. The oracle seed is cheap, interpretable, and replay-compatible. It can become the first population-growth mechanism:

```text
population payoff table
  ↓
identify weak/strong opponents
  ↓
generate candidate response decks/pilots
  ↓
public payoff evaluation
  ↓
promotion gate
  ↓
new strategy enters population
```

## Current caveat

The current candidate prior is static and hand-shaped. It is useful as a bootstrapper, not as MUC theory. A high oracle-seed score in rev0012 should be read as: “this candidate is worth testing more,” not “this deck is good.”
