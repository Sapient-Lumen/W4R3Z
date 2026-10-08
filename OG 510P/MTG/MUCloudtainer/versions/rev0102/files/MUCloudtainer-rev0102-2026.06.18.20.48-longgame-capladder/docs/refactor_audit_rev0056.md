# rev0056 refactor/audit note

New module:

```text
src/muc5/terminal_life_cell_replicate.py
```

It separates independent life-cell holdout logic from the earlier claim modules:

```text
terminal_matchup_claim.py       all-life concrete matchup dossier
terminal_life_cell_claim.py     life-cell decomposition and cumulative claim rows
terminal_life_cell_replicate.py independent seed-disjoint holdout replication
```

New audit/gate outputs:

```text
rev0056_life_cell_replication_holdout_cells.csv
rev0056_life_cell_replication_comparison.csv
rev0056_life_cell_replication_dimension_stability.csv
rev0056_life_cell_replication_summary.json
```

The replication gate requires terminal-clean rows, zero C++ skipped/mismatched transitions, replay success, enough holdout rows per cell, and explicit holdout labels.
