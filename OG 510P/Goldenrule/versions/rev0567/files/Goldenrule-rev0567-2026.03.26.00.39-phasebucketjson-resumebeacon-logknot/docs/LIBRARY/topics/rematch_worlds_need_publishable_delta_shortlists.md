# Rematch worlds need publishable delta shortlists, not every persistent micro-island

The persistence pass showed that some rematch delta topologies survive across a real family of extra-budget caps. That was necessary, but it was not yet a publishable shortlist. A future inheritor still needs to know **which** persistent cores are worth elevating into named benchmark constants and which should remain internal diagnostics.

The new derived report in `artifacts/reports/rematch_proxy_delta_publishability_snapshot_20260306.{md,json}` adds that missing filter.

It canonicalizes the persistence ladders to one row per unique family core, then applies three explicit guardrails:

1. the core must survive across at least **four declared caps**,
2. the shared core must clear a declared **minimum width floor**, and
3. the core must avoid the existing `>1000` extra-paired-seed **hazard bands**.

In the current leave/rematch proxy, there are `13` canonical family cores covering at least four caps. But a width floor of `0.0010` collapses that universe to only `3` publishable anchors overall, and only `2` of those remain below `delta=0.01`:

- `TTTMMMMMU` on `0.00538..0.00666`, anchor `0.00602`
- `TTTMMMMUU` on `0.00667..0.00822`, anchor `0.00744`

That is the right scale for a public shortlist: small enough to be stable and interpretable, but derived from explicit guardrails rather than taste.

An important side result is that, once family persistence is already enforced, **width is doing the real filtering** in this proxy. Every width-qualified shortlist candidate already lies comfortably outside the `>1000` extra-seed hazard bands. So future implementors should resist the urge to publish every persistent sliver just because it technically survives across caps. Surviving is not the same as being benchmark-worthy.
