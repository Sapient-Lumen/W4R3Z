# Rematch worlds should compensate stateless live reoptimization by deadline inflation

The recent passes have shown three equivalent views of the same geometric-arrival control tax:

- a dead reserve of `K - 1` ticks,
- a same-horizon blind-commit haircut under stateless live reoptimization,
- and a time-consistency gap for multi-tick promises.

The next operational question is the constructive one:

> if the system still wants to use stateless live reoptimization, how much extra deadline does it need to get back to the blind-commit value it originally meant to represent?

The answer is pleasantly exact.

## Exact compensation law

Let `K` be the minimum blind-commit timeout required for the target margin promise.
Then for any positive blind-commit horizon `H`, a stateless live-reoptimized controller needs exactly

- `K - 1`

extra ticks to match the blind-commit value at horizon `H`.

Equivalently:

- `live(H + K - 1) = blind_commit(H)`.

This is not an approximation. It is the exact dual of the earlier reserve law.
The same `K - 1` ticks that disappeared as dead reserve are precisely the ticks that must be restored as deadline inflation if the implementation wants value equivalence instead of accepted drift.

## Operational consequence

So implementors now have three interchangeable correction knobs for the simpler stateless controller:

- subtract the exact geometric deficit as an accounting haircut,
- add `K - 1` ticks of deadline inflation,
- or avoid the issue entirely by using blind-commit semantics.

The main convenience is that this correction is **parameter-free once `K` is known**.
No new nonlinear solve is needed online.

## Special case

When `K = 1`, the correction vanishes.
That is why one-tick promises keep reappearing as the unique drift-free and inflation-free class.

## All-state guardrail

The same law applies under the seven-bit universal lower envelope.
So a universal stateless controller can also be repaired exactly by adding the universal reserve length `K - 1` to the deadline whenever it needs to reproduce blind-commit value rather than merely tolerate drift.
