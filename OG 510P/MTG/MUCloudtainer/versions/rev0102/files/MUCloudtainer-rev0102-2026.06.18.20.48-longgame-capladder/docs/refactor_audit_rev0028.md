# rev0028 refactor/audit notes

## Refactor

Added:

```text
src/muc5/opening_counterfactual.py
```

and the engine helper:

```text
start_game_from_pregame_state(...)
```

This isolates counterfactual branch construction from normal tournament construction.

## Audit target

The audit now checks:

```text
rev0028 branch rows = 144
rev0028 paired rows = 72
context summary exists
C++ transition rows equal summary transition_events
C++ skipped events = 0
C++ mismatches = 0
truncations = 0
keep/mulligan/tie pair counts sum to 72
required rev0028 docs/scripts/tests/data exist
```

## Main failure modes guarded

```text
opponent opening hand changes across keep/mulligan branches
transition RNG changes across branches for reasons unrelated to branch state
explicit pregame states violate card conservation
counterfactual traffic falls outside C++ transition support
counterfactual rows are mistaken for full tournament claims
```

The last point matters: rev0028 branch rows are diagnostic training/evaluation material.  They are not a normal promoted payoff table.
