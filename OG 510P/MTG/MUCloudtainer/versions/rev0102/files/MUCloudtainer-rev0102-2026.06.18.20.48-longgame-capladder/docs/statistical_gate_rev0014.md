# rev0014 statistical gate

rev0014 adds a lightweight statistical layer before heavier learning methods compete.

The problem is not just speed. A simulator can generate many rows, but early rows are noisy, can include max-decision truncations, and can make a weak strategy look strong by luck. The old promotion gate checked provenance, replay, interface, and reward convention. The new statistical gate adds uncertainty labels.

## What the gate computes

Files:

```text
src/muc5/statgate.py
scripts/run_rev0014_statgate_payoff.py
```

Outputs:

```text
data/rev0014_statgate_payoff_games.csv
data/rev0014_statgate_payoff_aggregate.csv
data/rev0014_statgate_standings.csv
data/rev0014_statgate_pairwise.csv
data/rev0014_statgate_replay_traces.jsonl
data/rev0014_statgate_replay_results.json
data/rev0014_statgate_summary.json
```

The standings now include:

```text
mean_score_draw_half
score_lcb_95
score_ucb_95
terminal_win_rate
terminal_win_lcb_95
terminal_win_ucb_95
truncation_rate
claim_ready
```

`score_lcb_95` uses a conservative Hoeffding interval for bounded [0,1] draw-half rewards. `terminal_win_lcb_95` uses a Wilson score interval over terminal wins.

## Why two interval types?

MUC-5 rows have two different notions of success:

```text
terminal win      pure win/loss event
reporting score   win = 1, loss = 0, draw/truncation = 0.5
```

Wilson is appropriate for binomial-style terminal wins. Draw-half reporting score is a bounded scalar, not a pure Bernoulli event, so rev0014 uses a conservative distribution-free Hoeffding interval there.

This is deliberately cautious. A tiny smoke table should almost always say “uncertain” for pairwise claims.

## Current rev0014 smoke result

The rev0014 table ran:

```text
8 strategy bundles
20 and 40 life
both starting-player settings
3 reps per cell
768 total games
8 replay samples
```

The statistical gate passed, but it warned about truncations and no pair/life cell being claim-ready. That is the correct behavior. The gate is saying:

```text
The table is clean enough to inspect.
It is not strong enough for matchup theory.
```

## How to use this later

A future learned constructor/pilot should not be promoted merely because it has the best mean score. It should clear a ladder like:

```text
1. provenance/replay/reward promotion gate
2. statistical gate with enough games
3. no unacceptable truncation/stall behavior
4. replayable sample surprises
5. population analysis, e.g. Alpha-Rank or PSRO
```

## Pushback

Do not turn the confidence interval into a false oracle. A tight interval around a biased simulator result is still biased. The gate only quantifies sampling uncertainty in the rows we generated.
