# rev0026 — C++ shadow rollout seam

rev0026 adds a live **C++ shadow rollout** path.  It is not a C++ tournament engine yet.

The contract is:

```text
Python public DecisionFrame game loop
  - hidden-information observations
  - public agents choose legal action indices
  - Python applies authoritative transition
  - Python records TransitionMicroRecord + expected SIGv2

one batched C++ transition call
  - C++ applies every recorded one-action transition
  - C++ SIGv2 must equal Python post-action SIGv2
```

This is different from the older recorded-trace checker.  The trace checker starts from JSON replay traces.  The rev0026 shadow rollout prepares transition records during the payoff run itself, so future bulk evaluations can attach C++ parity checks without writing huge public trace logs for every game.

## New API

```python
from src.muc5.cpp_rollout import (
    CppShadowGameSpec,
    strategy_pair_specs,
    prepare_cpp_shadow_rollout,
    finalize_cpp_shadow_rollout,
)

specs = strategy_pair_specs(strategies, simulator_revision="rev0026")
prepared = prepare_cpp_shadow_rollout(specs, revision="rev0026")
summary, transition_rows = finalize_cpp_shadow_rollout(prepared)
```

`prepare_cpp_shadow_rollout` still runs Python semantics.  `finalize_cpp_shadow_rollout` runs one batched C++ process over all supported transition records.

## Smoke result

The rev0026 shadow table used six mixed strategy bundles:

```text
outcome_fjace
outcome_counter_wall
mlp_fjace
pub_threat_overlord
pub_counter_wall
code_jace60
```

It produced:

```text
144 games
42,458 C++-checked transition events
0 skipped C++ events
0 C++ mismatches
0 Python rollout errors
8 / 8 replay samples passed
promotion gate passed
statistical gate passed
```

Three games truncated.  The table still passed the gate because the truncation rate was low, but those rows remain reporting-only for draw-half score.

## Why this matters

The next long-haul engine should be C++ where stable and valuable, but C++ should earn authority by matching Python one seam at a time.  The shadow rollout seam is the first shape that resembles a future tournament path:

```text
bulk games -> batch transition parity -> promoted payoff rows
```

The immediate performance lesson from earlier revisions still holds: C++ should be fed in coarse batches.  A subprocess-per-action engine would be a performance trap.
