# Rematch Delay Tax Scales With Turnover Tempo

The archive now has enough local evidence to make one more rematch-world boundary explicit:

> In the current leave/rematch proxy, a fixed rematch delay is almost a **tempo-scaled tax** on short-lived partnerships.

## What the local proxy now says clearly

The derived report in `artifacts/reports/rematch_proxy_turnover_tempo_snapshot_20260306.{md,json}` reuses the occupancy-accounting snapshot and asks one narrow question:

- how well does `avg_match_length / (avg_match_length + rematch_delay)` predict `matched_round_share`?

Across all `45` tested scenario means, the answer is: **almost perfectly**.

- max absolute error: `0.000167`
- mean absolute error: `0.000068`

So in the current proxy, the nominal delay knob does not act as one universal penalty.
It acts more like a fixed toll paid at each partnership turnover.

That means short temporary partnerships pay it much more often.

## Concrete local consequence

At `delay=2`:

- the highest-churn tested cell (`DCECC` against extortion share `80`) has `avg_match_length = 8.714702` and loses `0.186826` matched-share points relative to `delay=0`,
- while the `50`-round baselines lose only `0.038301` matched-share points.

That is a `4.878x` larger occupancy penalty under the same nominal delay.

This is the sharpest local reason yet not to collapse “persistence” and “search dead-time” into one friction field.

## What the literature adds

Two outside sources line up with this boundary.

- `RS-GR-015` (Camera & Gioffré, 2025) argues that **temporary partnerships** occupy a real middle ground between fixed partners and one-shot strangers. Relationship persistence therefore changes the cooperation problem itself.
- `RS-GR-016` (Honhon & Hyndman, 2020) studies matching institutions that differ in how relationships are dissolved and finds systematically different cooperation patterns across fixed, flexible, and random matching institutions.

Together with the local proxy result, the implementor lesson is straightforward:

- turnover tempo is not just a byproduct,
- it is part of the scientific world contract.

## Practical handoff for the inheritor

1. Keep `rematch_delay` / search dead-time explicit.
2. Also expose `avg_match_length`, partnership persistence, or an equivalent turnover-rate field.
3. Do not compare two worlds at the same nominal delay unless their turnover tempo is also reported.
4. Treat claims about “delay sensitivity” as incomplete unless the benchmark artifact reveals how often relationships actually turn over.

## Compact implementor takeaway

The archive already knew that rematch delay is a real tax, and then that most of the tax is occupancy.
This pass adds the next refinement:

> the size of that occupancy tax is strongly governed by partnership tempo.

So the next endogenous rematch world should keep **persistence** and **search dead-time** as separate first-class fields.
