# rev0050 terminal meta results

Archived smoke panel:

```text
strategies:       8
games:            256
max_decisions:    900
truncations:      0
replay samples:   8 / 8 passed
C++ shadow:       76,375 supported events, 0 skipped, 0 mismatches
C++ trace:        1,872 supported events, 0 skipped, 0 mismatches
```

The terminal-meta gate passed.  The statistical gate passed for strategy-level rows, while pair/life cells remain too small for matchup claims.

Top all-life meta-rank mass in this smoke run was heavily concentrated on `code_jace60`.  That does not prove it is the final champion; it means the next deeper terminal-clean panel should spend more repetitions around the strongest counter-wall / Jace-lock interactions and around life-sensitive strategies.

The claim ledger identified:

```text
robust_candidate_count: 1
life_sensitive_count:  2
large rank-disagreement count: 0
```

The absence of large rank disagreement is good for this small panel: mean-score standings, conservative LCB standings, and meta-rank are not fighting each other badly.
