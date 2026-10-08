# rev0048 truncation rescue protocol

rev0047’s yield-ranker payoff panel had a useful but uncomfortable result: the panel passed the loose promotion/statistical gates, but 30 of 144 games hit the `max_decisions` ceiling at 380 decisions. Those rows were still marked as draw-half reporting rows, but they were not terminal game outcomes.

rev0048 adds a stricter terminal-gate protocol for this exact failure mode.

## Protocol

1. Keep the same strategy bundles, seeds, starting players, life totals, and public DecisionFrame interface as the rev0047 panel.
2. Rerun the panel with a higher decision ceiling: `900` instead of `380`.
3. Match each final row to its rev0047 baseline row by:

```text
strategy0
strategy1
starting_life
starting_player
seed
```

4. Preserve baseline truncation fields on every final row:

```text
baseline_is_truncation
baseline_decisions
baseline_loss_reason
resolved_from_truncation
truncation_rescue_status
```

5. Use the high-ceiling terminal row as the final score, not the truncated baseline row.
6. Keep draw-half as a reporting convention only. Any remaining truncation remains training-ineligible.

## Result

The archived rev0048 run resolved all rev0047 truncations:

```text
baseline rows:          144
baseline truncations:    30
final rows:             144
final truncations:        0
resolved truncations:    30
```

The result passed the stricter rev0048 gates:

```text
promotion gate max truncation rate:    0.10
observed final truncation rate:        0.00
replay samples:                        8 / 8 passed
C++ full-panel shadow mismatches:      0
C++ replay-trace mismatches:           0
```

## What this does not prove

This is not a strategic MUC claim. It only says the rev0047 panel’s nonterminal rows can be resolved under a larger decision budget without changing the seed/strategy schedule. Pairwise matchup claims still lack enough repetitions.

## Why this matters

A learned or code policy that produces many truncated games can look acceptable under draw-half reporting. rev0048 makes that visible and gives future panels a repeatable rescue path before any result becomes claim-ready.
