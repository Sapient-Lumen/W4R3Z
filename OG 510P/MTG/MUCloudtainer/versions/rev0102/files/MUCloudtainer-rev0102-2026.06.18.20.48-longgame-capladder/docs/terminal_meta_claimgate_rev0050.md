# rev0050 terminal meta / claim gate

rev0050 adds a terminal-clean population-analysis layer on top of the yield-ranker family.

The key change is not another gameplay policy.  It is a stricter comparison surface:

```text
terminal-clean payoff rows
  -> aggregate matrix
  -> meta-rank rows for all / 20-life / 40-life scopes
  -> life-split stability rows
  -> rank-disagreement rows
  -> claim ledger
```

The gate refuses to treat nonterminal max-decision rows as population evidence.  Smoke tables can still exist, but the terminal-meta workflow is designed for comparisons where `terminal_clean_game == true` for every row.

## Why meta-rank now?

Mean score standings are useful but can hide population structure.  A strategy can have a good average but lose to the wrong predator; another can be a small but important population response.  The existing Alpha-Rank-inspired `metarank.py` adapter is now wired into a terminal-clean workflow.

rev0050 uses the full eight-strategy `terminal_clean_yield_ranker_bundles(...)` panel rather than the rev0049 six-strategy slice.

## Outputs

```text
data/rev0050_terminal_meta_games.csv
data/rev0050_terminal_meta_aggregate.csv
data/rev0050_terminal_meta_metarank.csv
data/rev0050_terminal_meta_life_stability.csv
data/rev0050_terminal_meta_rank_disagreement.csv
data/rev0050_terminal_meta_claim_ledger.csv
data/rev0050_terminal_meta_summary.json
```

The claim ledger is deliberately conservative.  It labels rows as:

```text
robust_candidate
life_sensitive_candidate
population_candidate
terminal_clean_signal_only
needs_more_games
```

These labels are triage labels, not final MUC theory.
