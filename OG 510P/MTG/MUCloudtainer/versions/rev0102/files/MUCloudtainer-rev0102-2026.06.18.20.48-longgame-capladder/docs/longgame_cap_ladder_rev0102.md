# rev0102 — long-game cap ladder

## What rev0102 adds

rev0101 showed that the admitted PSRO response still had a weak transfer axis: `ood_counter_jace40`, a no-Overlord counter-control/Jace-control stressor. The focal strategy beat that opponent in mean, but the confidence floor stayed open and one long game remained nonterminal even after a small rescue.

rev0102 turns that caveat into executable evidence.

It adds:

- `src/muc5/longgame.py` for counts-only terminal snapshots, cap-ladder replay, high-cap focal-pair evaluation, and long-game summaries.
- `scripts/run_rev0102_longgame_cap_ladder.py` for the counter/Jace axis audit.
- `tests/test_rev0102_longgame_cap_ladder.py` for snapshot leakage, balanced rows, and deterministic cap-ladder replay.
- `data/rev0102_*` evidence tables and summaries.

## Result

The original rev0101 truncated cell was replayed at these decision caps:

```text
1400, 1600, 2400, 3200, 5000
```

It remained nonterminal at every cap. The diagnostic snapshot labels alternate between near-balanced control caps and library-edge caps; the ordinary payoff convention is unchanged, so those rows continue to score `0.5`.

The counter/Jace axis was also rerun at a higher cap:

```text
games: 192
max_decisions: 3200
mean score: 0.5859375
95% CI: [0.5162701255397072, 0.6556048744602928]
truncations: 1
```

The lower confidence bound is above 0.5, but the axis still does **not** clear the declared confidence floor because the truncation gate remains open.

## Interpretation

The weak axis did not collapse into an opponent win. It now looks more like a small number of Jace/control games that can persist for thousands of decisions under the current deterministic pilots.

That is useful, but it is not a robustness claim. The correct next step is to decide whether MUC-5 should keep treating persistent cap games as half-point draws, implement a formal repetition/draw rule, or change the agent objective so pilots do not create pathological Jace loops.

This revision does **not** promote a strategy and does **not** replace terminal scoring with heuristic adjudication.
