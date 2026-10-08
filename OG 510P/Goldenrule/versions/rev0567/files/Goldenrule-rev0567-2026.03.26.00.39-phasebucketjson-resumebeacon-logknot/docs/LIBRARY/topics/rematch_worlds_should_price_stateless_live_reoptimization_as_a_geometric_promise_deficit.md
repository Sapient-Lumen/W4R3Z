# Rematch worlds should price stateless live reoptimization as a geometric promise deficit

The recent passes pinned down three adjacent facts about shared-state exact batching under the current geometric-arrival model:

- a blind-commit timeout promise has an exact minimum viable horizon `K`,
- a miss-by-miss live countdown with the same promise throws away the last `K - 1` ticks as dead reserve,
- and only `K = 1` promises are locally time-consistent under that live reoptimization.

That still leaves one implementor-facing nuisance:

> if the system insists on using the simpler stateless live controller anyway, how much same-horizon value is it actually giving up relative to the blind-commit schedule it was supposed to represent?

The new deficit law answers that exactly.

Let

- `p` be same-state arrival hazard per tick,
- `n` be current batch length,
- `c` be hold cost in bits per script per tick,
- `gain_slope = state_prefix_bits / (n(n+1)) - c / p`,
- `K` be the minimum blind-commit timeout that achieves the target margin,
- `H >= K` be the current remaining deadline horizon.

Then the same-horizon blind-commit value is larger than the stateless live-reoptimized value by exactly

- `gain_slope * (1 - p)^(H - K + 1) * (1 - (1 - p)^(K - 1))`.

So the cost of choosing the simpler controller is not vague policy drift. It is an explicit **geometric haircut** with two factors:

1. a reserve-length term `1 - (1 - p)^(K - 1)` saying how much value lives inside the discarded dead reserve,
2. and a horizon-decay term `(1 - p)^(H - K + 1)` saying how much that discarded tail still matters at the current deadline.

This collapses the implementation choice:

- if `K = 1`, the haircut is identically zero,
- if `K > 1`, the haircut is strictly positive at the boundary `H = K`,
- and then decays geometrically as extra horizon accumulates.

The preserved same-horizon share is exact too:

- `live(H) / blind_commit(H) = (1 - (1 - p)^(H - K + 1)) / (1 - (1 - p)^H)`.

At the boundary checkpoint `H = K`, that becomes

- `p / (1 - (1 - p)^K)`.

So future inheritors should treat stateless live reoptimization as an explicit economic approximation layer.
Do not log it as if it still equals the blind-commit schedule.
Either:

- keep blind commit semantics,
- extend the deadline to offset the haircut,
- or record the controller honestly as **blind-commit value minus the exact geometric deficit**.

Future redesign signal: if the current miss process stops being geometric or if checkpoint decisions become stateful in a richer way than remaining horizon alone, this deficit law should be expected to move.
