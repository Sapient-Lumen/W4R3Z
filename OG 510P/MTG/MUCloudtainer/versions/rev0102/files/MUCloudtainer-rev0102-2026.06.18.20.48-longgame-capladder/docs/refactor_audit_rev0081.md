# rev0081 refactor audit

The refactor is deliberately small and risk-facing.

## Changed code

`src/muc5/population_frontier.py` now contains:

```text
population_column_frontier_rows(...)
summarize_population_column_frontier(...)
```

These helpers centralize threat-column diagnostics instead of requiring each revision script to hand-roll a grouping by context, threat axis, and counter policy.

## Failure mode addressed

Before rev0081, the cube could report a single hierarchical floor while leaving unclear whether the low floor came from:

1. one unusually bad threat column,
2. broad weakness across all threat columns,
3. missing cells,
4. inadequate precision, or
5. underpowered opponent-specific slices.

The new helper fails closed on missing counter-policy rows and emits explicit `underpowered_min_games`, `precision_target_not_met`, and `no_credible_counter_answer_for_threat_column` statuses.

## Audit result

The current result is not blocked by missingness or power:

```text
frontier rows:                      36
missing/incomplete rows:            0
underpowered rows:                  0
precision-target rows:              0
no-credible-answer rows:            36
candidate column-answer rows:       0
```

## Evidence hygiene

No new rollout traces or full transition logs were shipped.  rev0081 derives compact diagnostic rows from the existing broad complete-panel summary evidence and keeps adaptive rev0075 evidence excluded from broad promotion diagnostics.
