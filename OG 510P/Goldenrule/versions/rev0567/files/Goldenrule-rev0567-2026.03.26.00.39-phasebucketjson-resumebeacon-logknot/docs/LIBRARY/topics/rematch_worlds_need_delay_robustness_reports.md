# Rematch Worlds Need Delay-Robustness Reports

The archive now has enough local evidence to tighten the rematch reporting contract again:

> A rematch-world leaderboard at one nominal delay value is **not** a stable claim unless it is accompanied by either a delay sweep or an explicit crossover-threshold / robustness report.

## What the local proxy now establishes

The derived report in `artifacts/reports/rematch_proxy_delay_crossover_snapshot_20260306.{md,json}` asks a narrow question:

- once occupancy and tempo are already separated, how fragile are raw aggregate rankings to the exact delay value chosen for the benchmark?

The current proxy gives a useful answer.

Using only two delay-0 summary statistics per policy/extortion cell,

- `in_match_avg_payoff`, and
- `avg_match_length`,

we can predict aggregate welfare at delay `d` with the compact approximation

- `overall(d) ≈ in_match_avg_payoff(delay0) * avg_match_length(delay0) / (avg_match_length(delay0) + d)`.

Across all `45` scenario means in the current proxy, this compact predictor has:

- mean absolute error `0.001035`,
- max absolute error `0.005220`.

More importantly, the same summary predicts `89/90` observed pairwise delay-specific orderings correctly.

So the current proxy already supports a stronger interpretation boundary:

- many raw ranking changes can be anticipated from **tempo-sensitive occupancy math**,
- not from a deep change in within-match conduct.

## Why this sharpens the handoff

The archive already learned several distinct facts:

1. rematch delay acts like a tax,
2. most of that tax is an occupancy tax,
3. the size of the tax scales with partnership tempo,
4. raw-vs-normalized leaderboard flips can be occupancy artifacts.

This pass adds the next operational lesson:

- even after all that accounting, a single chosen delay can still make a ranking look more stable than it really is.

In the current proxy, there are explicit pairwise **crossover delays** where one policy overtakes another in raw aggregate welfare purely because the delay tax hits their tempo differently.

Two crossovers already fall inside the tested delay range `[0, 2]`, and several more sit just beyond it.
That means “winner at delay `1`” is not the same claim as “winner robust to the benchmarked rematch friction range.”

## What the literature adds

The outside sources now point in the same direction.

- `RS-GR-016` shows that cooperation depends on the institution governing how relationships dissolve and reform.
- `RS-GR-017` shows that realized match length can materially alter treatment comparisons in indefinitely repeated games.
- `RS-GR-018` argues that sorting / replacement opportunities can matter as much as or more than punishment incentives in repeated relationships.

Together, these support a compact implementor rule:

- do not present one delay setting as if it fully identifies the welfare ranking of rematch-enabled policies.

## Minimal robustness contract for future rematch worlds

At minimum, every rematch-world benchmark artifact should expose one of:

- a short delay sweep over the deployed friction range,
- explicit pairwise crossover thresholds for salient policy comparisons,
- or a per-policy robustness interval stating the delay band over which its ranking claim is intended to hold.

This should be published **in addition to** the paired raw and occupancy-normalized leaderboard views.

## Compact implementor takeaway

The next inheritor should treat single-delay winners as provisional.

> If a ranking changes within a plausible delay band, the archive should describe that result as **delay-fragile** rather than as a universal strategy ordering.
