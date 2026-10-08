# rev0055 refactor / audit notes

New module:

```text
src/muc5/terminal_life_cell_claim.py
```

It separates life-cell claim work from broader matchup-claim dossiers:

```text
terminal_matchup_claim.py      matchup-level dossier rows
terminal_life_cell_claim.py    target/opponent/life cell agenda, specs, summaries, gates
```

The important audit choice is that rev0055 writes both current-only and cumulative tables:

```text
rev0055_life_cell_current_cells.csv
rev0055_life_cell_cumulative_cells.csv
```

This prevents cumulative evidence from hiding the fresh-run result.

The gate checks:

```text
fresh row count
zero truncations
fresh per-cell game count
cumulative per-cell game count
C++ skipped events = 0
C++ mismatches = 0
```
