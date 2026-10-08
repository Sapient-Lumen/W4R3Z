# rev0032 refactor/audit notes

## Refactor

`src/muc5/cpp_segment.py` now has a batched panel path:

```python
run_nochoice_segment_cpp_panel_batched(...)
```

It collects all segment records across a panel, calls the C++ segment checker once, then refreshes game-level C++ counts from finalized segment rows.

`CppNoChoiceGameRow` now includes promotion-gate columns:

```text
reward_convention
interface
log_events
turn_number
p0_terminal_only_score
p1_terminal_only_score
```

That lets segment-shadow payoff rows flow through the same promotion gate as ordinary public payoff rows.

`strategy_sets.py` now includes:

```python
mapelite_mulligan_variant_bundles(...)
```

which crosses MAP-Elites construction shells with public/code/learned gameplay and learned mulligan policies.

## Audit

`tests/test_rev0032_segment_shadow.py` checks:

- MAP-Elites mulligan variant bundles load.
- repeated-counterfactual mulligan policies are present.
- batched segment rows expose promotion columns.
- segment rows can pass promotion audit without replay when configured for unit testing.

`scripts/audit_cube.py` now checks the archived rev0032 segment-shadow data, replay samples, promotion/statistical gates, C++ mismatch counts, skipped counts, and required files.
