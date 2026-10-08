# rev0080 size-ladder power audit

rev0079 made the promotion gate hierarchical, which exposed a useful but uncomfortable blocker: the global and life layers were already decisive, while the size layer was blocked by precision and the fine size/life layer was still underpowered.  That meant the cube could say "do not promote," but it could not yet say whether size-specific evidence itself was actually unfavorable or merely too thin.

rev0080 converts that blocker into an executable complete-panel ladder.

## Pre-run allocation

The rev0069 + rev0070 broad-pool source had 432 eligible games and 72 eligible summary rows.  The closed-form familywise Hoeffding calculation said:

- mandatory size rows needed one additional complete-panel rep;
- fine size/life diagnostic rows needed five additional complete-panel reps;
- five reps would clear both the preregistered minimum-game and width targets everywhere.

The rep math is now code, not prose:

```text
complete_panel_games_per_cell_for_axes(()) = 24
complete_panel_games_per_cell_for_axes((starting_life,)) = 12
complete_panel_games_per_cell_for_axes((size_axis,)) = 8
complete_panel_games_per_cell_for_axes((size_axis, starting_life)) = 4
```

## Run

rev0080 ran a seed-disjoint complete outcome panel:

```text
arms:       18
reps:       5
games:      720
truncation: 0
```

It deliberately used the outcome-only runner for the full 720 games and a sampled C++ transition shadow for semantic parity:

```text
C++ shadow specs:    96
C++ records checked: 15000
mismatches:          0
skips:               0
truncations:         0
```

No transition table is shipped; only a 180-row transition sample is kept for compact audit.

## Post-run gate

After pooling rev0069 + rev0070 + rev0080 complete panels, the eligible broad source contains 1152 games and 108 summary rows.

The old power blockers are gone:

```text
post precision-blocked rows: 0
post underpowered rows:     0
post reps still needed:     0
```

The scientific conclusion is not promotion.  It is stronger quarantine:

```text
global:        1 quarantined_low_security_floor
by_life:       2 quarantined_low_security_floor
by_size:       3 quarantined_low_security_floor
by_size_life:  6 quarantined_low_security_floor
```

Every hierarchy row is now complete enough under the current familywise width/min-game rule, and every row still fails the conservative security floor.

## Main files

```text
src/muc5/population_power.py
scripts/run_rev0080_size_ladder_power_audit.py
tests/test_rev0080_size_ladder_power.py
data/rev0080_size_ladder_power_summary.json
data/rev0080_pre_power_ladder.csv
data/rev0080_post_power_ladder.csv
data/rev0080_post_hierarchical_familywise_gate.csv
```
