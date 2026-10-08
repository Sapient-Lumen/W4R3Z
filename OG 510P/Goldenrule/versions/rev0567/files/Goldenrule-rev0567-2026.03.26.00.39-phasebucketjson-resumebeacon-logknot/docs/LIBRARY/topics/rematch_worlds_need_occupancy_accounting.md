# Rematch Worlds Need Occupancy Accounting

The archive now has enough local evidence to sharpen `SQ-013` into a concrete reporting contract for the future inheritor:

> Any rematch-world welfare report should separate **time spent matched** from **payoff earned while matched**.

## What the local proxy now establishes

The new derived report in `artifacts/reports/rematch_proxy_occupancy_accounting_snapshot_20260306.{md,json}` adds one narrow but high-value decomposition to the current exogenous-pool leave/rematch proxy.

For five salient policies across three extortion shares and three rematch delays, it exposes:

- `matched_round_share`
- `dead_round_share`
- `in_match_avg_payoff`
- `overall_avg_payoff`

and checks the exact per-replicate identity:

- `overall_avg_payoff = matched_round_share * in_match_avg_payoff`

That matters because it turns a vague modeling warning into a precise accounting rule.

## Main local result

In the current proxy:

- all `15` tested policy/extortion cells are monotone in `matched_round_share` as delay rises,
- the mean share of `delay0 -> delay2` payoff loss explained by shrinking `matched_round_share` is `0.985842`,
- the maximum `delay0 -> delay2` drift in `in_match_avg_payoff` is only `0.005788`.

So the current delay sweep is not merely “worse because delay is bad” in some fuzzy sense.
It is much sharper than that:

- delay mostly reduces welfare by shrinking the fraction of time spent in payoff-producing matches,
- not by materially changing the quality of play inside those matches.

## Why this belongs in the engine contract

A future endogenous rematch world will eventually want to say things like:

- this policy improved welfare,
- this world made matching frictions milder,
- this institution increased cooperation.

Without occupancy accounting, those claims are underidentified.
A gain in `overall_avg_payoff` could come from:

1. more time spent matched,
2. better behavior conditional on being matched,
3. both.

Those are substantively different mechanisms.
They should not be collapsed into one aggregate metric.

## What the literature adds

The outside sources now line up with this split.

- `RS-GR-013` (Bester & Sákovics, 2024) studies welfare in a repeated-dilemma matching market where the steady state explicitly distinguishes matched and unmatched agents. The welfare effect of lower frictions depends partly on how many agents are in productive cooperative relationships, not only on incentives inside each relationship.
- `RS-GR-015` (Camera & Gioffré, 2025) studies **temporary partnerships**, filling the spectrum between permanent partners and one-period strangers. That reinforces the need to treat match occupancy/persistence as part of the world contract, not as an invisible implementation detail.

Together with the local proxy decomposition, that yields a clean handoff rule:

- report occupancy,
- report in-match performance,
- do not report only aggregate welfare.

## Minimal reporting contract for future rematch worlds

At minimum, every rematch-world benchmark artifact should expose:

- `overall_avg_payoff`
- `matched_round_share`
- `dead_round_share` (or `searching_round_share`)
- `in_match_avg_payoff`
- match-start / match-end counts or an equivalent occupancy-flow summary

If the world includes endogenous matching, also expose the steady-state matched/searching mass directly.

## Compact implementor takeaway

The archive already learned that rematch delay is a real tax.
This pass says exactly **what kind** of tax it is in the current proxy:

> mostly an occupancy tax on time spent productively matched.

That is worth encoding directly into the next world/report contract so future sessions do not confuse “better matching” with “better conduct inside matches.”
