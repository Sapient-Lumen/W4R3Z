# Rematch-Proxy Noise Semantics Dominate Cache Keys

> The current start-support cache gate is useful, but it is a zero-noise artifact. Under support-level tremble semantics, the canonical quotient jumps from `63` to `99`, `147`, or `163` families depending on which side can err.

The report in `artifacts/reports/rematch_proxy_noise_semantics_snapshot_20260306.{md,json}` keeps the same current leave/rematch proxy and varies only the support semantics used for reachability.

## Local result

Using the current proxy pool (`extortion_chi3_v1`, `mem1_generous_tft_v1`):

- deterministic no-noise semantics give the familiar `63`-family quotient,
- opponent tremble support alone raises the quotient to `99` families,
- focal tremble support alone raises it to `147` families,
- bilateral tremble support raises it to `163` families.

The entrant-side start-support gate then changes shape:

- in the zero-noise proxy, `C`-only entrants preserve `63` while entrants with initial `D` support reopen the quotient to `87`–`99`,
- under opponent tremble, every entrant signature yields the same `99`-family quotient,
- under focal tremble, a weaker gate remains (`147` for `C`-only entrants, `163` for initial-`D` entrants),
- under bilateral tremble, every entrant signature again yields the same quotient (`163`).

## Why this matters

This is the cleanest local reason so far to stop treating canonicalization as a property of the entrant pool alone.

The current proxy now has three separate facts:

1. canonicalization is pool-specific,
2. initial support is a cheap cache gate only in the deterministic no-noise proxy,
3. once nonzero tremble semantics are admitted, the cache key must include the active noise model and which side can err.

That is exactly the sort of engineering detail that is easy to postpone and then expensive to retrofit.

## Literature fit

The broader repeated-game literature already treats errors as first-class rather than incidental.

- Hilbe et al. emphasize that stable cooperative strategies in repeated dilemmas need to **correct errors**, not just retaliate, and model action implementation errors explicitly as trembling-hand events.
- They also note that occasional errors change which histories matter and can make otherwise ignorable histories relevant again.

For this archive, that literature-level lesson aligns with the new local structural result:

> zero-noise reachability quotients should not be reused across noisy rematch worlds.

## What the inheritor should build next

1. Put tremble semantics into the canonicalization cache key.
2. Distinguish at least three cases in the engine-facing API: no tremble, opponent-only tremble, and bilateral tremble.
3. Recompute canonicalization whenever noise semantics change, even if the entrant pool does not.
4. Keep reporting both raw genotype counts and canonical-family counts, because noise can make a previously compressed search space expand sharply.

## Boundary

This report uses **support semantics**, not calibrated error probabilities.

So it does **not** say that every tiny numerical error rate has the same quantitative effect on payoffs. It says something narrower and still useful for engineering:

- for reachability-based canonicalization,
- any nonzero action tremble that makes both `C` and `D` support-reachable
- is enough to invalidate the current zero-noise cache.
