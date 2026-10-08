# Rematch Worlds Need Occupancy-Normalized Rankings

The archive now has enough local evidence to sharpen the rematch reporting contract one step further:

> Future rematch-world benchmarks should publish **two leaderboards**, not one: a raw aggregate leaderboard and an occupancy-normalized in-match leaderboard.

## What the local proxy now establishes

The derived report in `artifacts/reports/rematch_proxy_rank_decomposition_snapshot_20260306.{md,json}` reuses the occupancy-accounting snapshot and asks one narrow question:

- when rematch delay changes the raw ranking of policies, is that because the policies behave differently **inside** matches, or because they spend different fractions of time stuck searching?

The current proxy gives a sharp answer.

Across all `9` extortion/delay panels:

- the occupancy-normalized rank order (`in_match_avg_payoff`) is identical,
- but `3` of the `6` nonzero-delay panels show raw-vs-normalized rank disagreement,
- for a total of `4` pairwise rank inversions.

So the current proxy already distinguishes two different phenomena:

1. changes in **time spent matched**, and
2. changes in **quality of play while matched**.

Raw aggregate payoffs blend those together.
The occupancy-normalized leaderboard splits them apart.

## Why this belongs in the reporting contract

The archive already learned that most of the current delay penalty is an occupancy tax.
This pass turns that accounting fact into a ranking rule.

In the current proxy, a delay sweep can move the raw leaderboard even when the occupancy-normalized ranking is unchanged.
That means a future rematch-world report can easily overclaim if it publishes only one ranking view.

For example, a policy can look worse in aggregate simply because it churns more and therefore pays the same dead-time tax more often, even if it is still better inside active matches.

## What the literature adds

Three outside results strengthen this rule.

- `RS-GR-013` (Bester & Sákovics, 2024) shows that welfare in a repeated-dilemma matching market depends partly on how many agents are actually in cooperative relationships, not only on in-relationship incentives.
- `RS-GR-015` (Camera & Gioffré, 2025) shows that temporary partnerships form a real middle regime between permanent partners and one-shot strangers.
- `RS-GR-017` (Mengel, Orlandi & Weidenholzer, 2022) shows that realized match length can materially affect cooperation and even treatment comparisons in indefinitely repeated games.

Together, these support a simple implementor rule:

- do not let one raw payoff ranking stand in for all rematch-world conclusions.

## Minimal ranking contract for future rematch worlds

At minimum, every rematch-world benchmark artifact should expose:

- a raw aggregate leaderboard (for overall welfare),
- an occupancy-normalized leaderboard (`in_match_avg_payoff` or equivalent),
- occupancy fields (`matched_round_share`, `dead/searching_round_share`),
- and a persistence / tempo field (`avg_match_length`, hazard, or equivalent).

Then interpret rank changes using the split:

- **raw flips only** → mostly occupancy / tempo effect,
- **normalized flips too** → real change in within-match strategic quality.

## Compact implementor takeaway

The next inheritor should treat paired leaderboards as part of the world contract, not as optional report polish.

> If the raw leaderboard moves but the occupancy-normalized leaderboard does not, the archive should call that an **occupancy artifact** until stronger evidence appears.
