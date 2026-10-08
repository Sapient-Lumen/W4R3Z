# rev0074 risk-seam fuzz profile

rev0074 turns the fuzz harness's weakest signal into an executable guard. Previous fuzz reports counted trigger-stack and loyalty actions, but the fixture did not reliably create those legal actions, so a green fuzz run could still spend almost all of its budget on passes, casts, and mana actions.

## What changed

- `mtgsim_fuzz` accepts `--profile broad|risk-seams`.
- `risk-seams` seeds a compact battlefield fixture with:
  - `Fuzz Warden`, an ETB trigger source,
  - `Fuzz Artist`, a dies-trigger source for later destructive paths,
  - `Fuzz Walker`, a planeswalker with a loyalty ability,
  - hasty token bodies created after the Warden fixture so pending triggers are guaranteed early.
- `mtgsim_fuzz --require-risk-seams` fails a seed unless it exercises both `PutPendingTriggersOnStack` and `ActivateLoyaltyAbility`.
- `tools/run_fuzz.py --profile risk-seams --require-risk-seams` propagates that per-seed guard and also records aggregate risk-seam counters.
- CMake now has `mtgsim_fuzz_risk_seams`, a cheap smoke guard for local/CI coverage.

## Why this is substance, not registry work

The replay and snapshot work from rev0068–rev0073 only matters if validation regularly visits the highest-risk state transitions. This profile makes two previously under-exercised transition families show up inside the normal invariant loop:

1. pending triggers being moved to the stack, including journal/event ordering; and
2. loyalty activation, including counter payment, stack placement, and target selection.

The profile does not replace scenario tests or future coverage-guided fuzzing. It closes the immediate waste where metrics existed but did not force the generator to enter the branches they measured.

## Remaining risk

The broad profile is still intentionally strategy-agnostic and pass-heavy because stack resolution requires priority passes. The next worthwhile step is not more metadata; it is a small targeted action scheduler that can bias toward unresolved stack objects, destructive dies-trigger paths, and branch/replay roundtrips during fuzz.
