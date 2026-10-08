# rev0052 life-flip matchup retest

rev0051 found apparently large life-total splits in low-sample target/opponent cells. rev0052 treats those rows as an agenda, not as a conclusion.

The new retest pipeline is:

```text
rev0051 target-pair rows
  ↓
select target/opponent cells with largest |life40 - life20| score split
  ↓
run terminal-clean public DecisionFrame games
  ↓
seat the target as p0 and p1
  ↓
include both starting players and both life totals
  ↓
aggregate from the target player's perspective
  ↓
compare retest delta to previous low-sample delta
```

The selected cells are recorded in:

```text
data/rev0052_life_flip_selected_matchups.csv
```

The per-target/life retest rows are recorded in:

```text
data/rev0052_life_flip_target_life_cells.csv
```

The compact life-split comparison is:

```text
data/rev0052_life_flip_retest.csv
```

No gameplay policy is promoted in this revision. The purpose is claim hygiene: a life split that vanishes under deeper terminal-clean sampling should not become MUC theory.
